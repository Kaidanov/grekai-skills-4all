#!/usr/bin/env python3
"""
enrich.py — unify exported Defender CSVs, enrich IOCs via VirusTotal, and prepare
the Sentinel pivot + incident-close package.

Standard library only. The VirusTotal API key is read from the VT_API_KEY
environment variable and never written anywhere. Your raw tenant CSVs stay on
disk; Claude only sees what you choose to paste back.

Pipeline:
  1. Read every CSV in --exports (default ./exports/defender), unify the rows.
  2. Extract + de-dup the IOCs (urls / domains / ips / hashes) seen in those rows.
  3. Look each IOC up in VirusTotal v3 (skipped cleanly if VT_API_KEY is unset).
  4. Apply the verdict rule from config -> mark suspect rows.
  5. Write out/: suspects.csv, suspects.json, report.md, sentinel_entities.txt,
     and sentinel_filled.kql (the blast-radius query with your suspect entities
     injected, ready to paste into Sentinel).

Usage:
    export VT_API_KEY=...        # optional; without it VT is skipped
    python3 enrich.py --config config.json
    python3 enrich.py --config config.json --exports ./exports/defender --out ./out
"""
import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

VT_BASE = "https://www.virustotal.com/api/v3"

# Candidate column names (lower-cased) for the fields we care about.
COLS = {
    "device":  ["devicename", "computer", "computername", "device"],
    "user":    ["accountname", "username", "userprincipalname", "account", "initiatingprocessaccountname"],
    "ioc":     ["ioc", "remoteurl", "url"],
    "ip":      ["remoteip", "ip", "ipaddress", "destinationip"],
    "sha256":  ["sha256"],
    "sha1":    ["sha1"],
    "md5":     ["md5"],
    "time":    ["timestamp", "timegenerated", "time"],
    "group":   ["machinegroup", "group"],
}


def pick(row_lower, names):
    for n in names:
        if n in row_lower and row_lower[n] not in (None, ""):
            return row_lower[n]
    return ""


def classify(token):
    t = token.strip()
    if not t:
        return None
    if all(c in "0123456789abcdefABCDEF" for c in t) and len(t) in (32, 40, 64):
        return "hash"
    if "://" in t or "/" in t:
        return "url"
    # ip vs domain
    parts = t.split(".")
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return "ip"
    return "domain"


def read_exports(exports_dir):
    rows = []
    if not os.path.isdir(exports_dir):
        return rows
    for name in sorted(os.listdir(exports_dir)):
        if not name.lower().endswith(".csv"):
            continue
        path = os.path.join(exports_dir, name)
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                low = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
                rows.append({
                    "source_file": name,
                    "time": pick(low, COLS["time"]),
                    "device": pick(low, COLS["device"]),
                    "user": pick(low, COLS["user"]),
                    "group": pick(low, COLS["group"]),
                    "ioc": pick(low, COLS["ioc"]),
                    "ip": pick(low, COLS["ip"]),
                    "sha256": pick(low, COLS["sha256"]),
                    "sha1": pick(low, COLS["sha1"]),
                    "md5": pick(low, COLS["md5"]),
                })
    return rows


def collect_iocs(rows):
    """Return {ioc_value: type} for every distinct indicator across the rows."""
    found = {}
    for r in rows:
        for val in (r["ioc"], r["ip"], r["sha256"], r["sha1"], r["md5"]):
            val = (val or "").strip()
            if not val:
                continue
            kind = classify(val)
            if kind:
                found.setdefault(val, kind)
    return found


def vt_get(path, api_key):
    req = urllib.request.Request(VT_BASE + path, headers={"x-apikey": api_key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def vt_lookup(value, kind, api_key):
    """Return dict(malicious, total, reputation, found) or None on hard error."""
    if kind == "domain":
        path = "/domains/{0}".format(value)
    elif kind == "ip":
        path = "/ip_addresses/{0}".format(value)
    elif kind == "hash":
        path = "/files/{0}".format(value)
    elif kind == "url":
        uid = base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").strip("=")
        path = "/urls/{0}".format(uid)
    else:
        return {"malicious": 0, "total": 0, "reputation": 0, "found": False}

    try:
        data = vt_get(path, api_key)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"malicious": 0, "total": 0, "reputation": 0, "found": False}
        if e.code == 401:
            raise RuntimeError("VirusTotal rejected VT_API_KEY (401).")
        if e.code == 429:
            return {"_rate_limited": True}
        return {"malicious": 0, "total": 0, "reputation": 0, "found": False, "error": e.code}
    except urllib.error.URLError as e:
        return {"malicious": 0, "total": 0, "reputation": 0, "found": False, "error": str(e.reason)}

    attrs = data.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {}) or {}
    total = sum(v for v in stats.values() if isinstance(v, int))
    return {
        "malicious": int(stats.get("malicious", 0)),
        "total": total,
        "reputation": int(attrs.get("reputation", 0)),
        "found": True,
    }


def enrich_iocs(iocs, vt_cfg, api_key):
    """Look up every IOC; return {value: result}. Degrades to skipped if no key."""
    results = {}
    if not api_key:
        for v, k in iocs.items():
            results[v] = {"type": k, "skipped": True}
        return results

    delay = float(vt_cfg.get("rate_limit_seconds", 15))
    items = list(iocs.items())
    for idx, (value, kind) in enumerate(items):
        res = vt_lookup(value, kind, api_key)
        if res.get("_rate_limited"):
            time.sleep(max(delay, 30))
            res = vt_lookup(value, kind, api_key)
            if res.get("_rate_limited"):
                res = {"malicious": 0, "total": 0, "reputation": 0, "found": False, "error": "rate_limited"}
        res["type"] = kind
        results[value] = res
        flagged = res.get("malicious", 0)
        print("  VT [{0}/{1}] {2} ({3}): {4} malicious".format(
            idx + 1, len(items), value, kind, flagged), file=sys.stderr)
        if idx < len(items) - 1:
            time.sleep(delay)
    return results


def verdict_for(res, vt_cfg):
    if res is None or res.get("skipped"):
        return "unchecked"
    mal = res.get("malicious", 0)
    rep = res.get("reputation", 0)
    if mal >= int(vt_cfg.get("malicious_threshold", 5)):
        return "malicious"
    if mal >= int(vt_cfg.get("suspicious_min", 1)) and rep < 0:
        return "suspicious"
    return "benign"


def confidence(res):
    """0-100 explainable score; detections dominate."""
    if res is None or res.get("skipped"):
        return 0
    score = min(res.get("malicious", 0), 20) * 4          # 0-80
    if res.get("reputation", 0) < 0:
        score += 10
    if res.get("malicious", 0) > 0 and res.get("total", 0) > 0:
        score += 10
    return max(0, min(100, score))


def csv_safe(value):
    """Neutralize CSV/formula injection."""
    s = "" if value is None else str(value)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def ioc_of_row(row):
    for val in (row["ioc"], row["sha256"], row["sha1"], row["md5"], row["ip"]):
        if (val or "").strip():
            return val.strip()
    return ""


def kql_list(values):
    escaped = [v.replace("\\", "\\\\").replace('"', '\\"') for v in values]
    return "dynamic([{0}])".format(", ".join('"{0}"'.format(v) for v in escaped))


SENTINEL_TEMPLATE = """// ===========================================================================
// Sentinel blast-radius — auto-filled by soc-investigator/enrich.py
// Suspect entities derived from confirmed-malicious/suspicious IOCs.
// Run in Microsoft Sentinel -> Logs. Lists every machine + user that touched them.
// ===========================================================================
let LookBack = {days}d;
let SuspectIocs = {iocs};
let SuspectDevices = {devices};
let SuspectUsers = {users};
let Net =
    DeviceNetworkEvents
    | where Timestamp > ago(LookBack)
    | where RemoteUrl has_any (SuspectIocs) or RemoteIP in (SuspectIocs)
    | project Timestamp, Device = DeviceName, User = InitiatingProcessAccountName,
              Ioc = coalesce(RemoteUrl, RemoteIP);
let Alerts =
    SecurityAlert
    | where TimeGenerated > ago(LookBack)
    | where Entities has_any (SuspectDevices) or Entities has_any (SuspectUsers)
    | project Timestamp = TimeGenerated, Device = CompromisedEntity,
              User = "", Ioc = AlertName;
union Net, Alerts
| where Device in (SuspectDevices) or User in (SuspectUsers)
     or Ioc has_any (SuspectIocs)
| summarize Hits = count(), FirstSeen = min(Timestamp), LastSeen = max(Timestamp),
            Iocs = make_set(Ioc, 20) by Device, User
| sort by Hits desc
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Unify Defender CSVs + VirusTotal enrichment + Sentinel prep.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--exports", default="exports/defender")
    ap.add_argument("--out", default="out")
    args = ap.parse_args(argv)

    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    vt_cfg = cfg.get("virustotal", {}) or {}
    days = int(cfg.get("time_window_days", 7))

    rows = read_exports(args.exports)
    if not rows:
        print("No CSVs found in {0}. Export your Defender hunting results there first."
              .format(args.exports), file=sys.stderr)
        return 1
    print("Unified {0} row(s) from {1}.".format(len(rows), args.exports))

    iocs = collect_iocs(rows)
    print("Found {0} distinct IOC(s) across the exports.".format(len(iocs)))

    api_key = os.environ.get("VT_API_KEY", "").strip()
    if not api_key:
        print("VT_API_KEY not set -> VirusTotal enrichment SKIPPED (rows still unified).",
              file=sys.stderr)
    enriched = enrich_iocs(iocs, vt_cfg, api_key)

    # Decorate rows with verdict/confidence from their IOC.
    suspect_rows = []
    for r in rows:
        ind = ioc_of_row(r)
        res = enriched.get(ind)
        v = verdict_for(res, vt_cfg)
        r["verdict"] = v
        r["vt_malicious"] = (res or {}).get("malicious", "")
        r["vt_total"] = (res or {}).get("total", "")
        r["vt_reputation"] = (res or {}).get("reputation", "")
        r["confidence"] = confidence(res)
        if v in ("malicious", "suspicious"):
            suspect_rows.append(r)

    os.makedirs(args.out, exist_ok=True)

    # suspects.csv (injection-safe)
    fields = ["time", "device", "user", "group", "ioc_value", "verdict",
              "vt_malicious", "vt_total", "vt_reputation", "confidence",
              "sha256", "ip", "source_file"]
    with open(os.path.join(args.out, "suspects.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(fields)
        for r in suspect_rows:
            w.writerow([
                csv_safe(r["time"]), csv_safe(r["device"]), csv_safe(r["user"]),
                csv_safe(r["group"]), csv_safe(ioc_of_row(r)), csv_safe(r["verdict"]),
                csv_safe(r["vt_malicious"]), csv_safe(r["vt_total"]), csv_safe(r["vt_reputation"]),
                csv_safe(r["confidence"]), csv_safe(r["sha256"]), csv_safe(r["ip"]),
                csv_safe(r["source_file"]),
            ])

    devices = sorted({r["device"] for r in suspect_rows if r["device"]})
    users = sorted({r["user"] for r in suspect_rows if r["user"]})
    confirmed_iocs = sorted({ioc_of_row(r) for r in suspect_rows if ioc_of_row(r)})

    # suspects.json
    with open(os.path.join(args.out, "suspects.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "summary": {
                "rows_total": len(rows),
                "suspect_rows": len(suspect_rows),
                "distinct_iocs": len(iocs),
                "suspect_devices": devices,
                "suspect_users": users,
                "confirmed_iocs": confirmed_iocs,
                "vt_checked": bool(api_key),
            },
            "iocs": {k: enriched.get(k) for k in iocs},
            "rows": suspect_rows,
        }, fh, indent=2)

    # sentinel_entities.txt
    with open(os.path.join(args.out, "sentinel_entities.txt"), "w", encoding="utf-8") as fh:
        fh.write("# Suspect devices\n")
        fh.write("\n".join(devices) + "\n\n")
        fh.write("# Suspect users\n")
        fh.write("\n".join(users) + "\n\n")
        fh.write("# Confirmed IOCs\n")
        fh.write("\n".join(confirmed_iocs) + "\n")

    # sentinel_filled.kql
    with open(os.path.join(args.out, "sentinel_filled.kql"), "w", encoding="utf-8") as fh:
        fh.write(SENTINEL_TEMPLATE.format(
            days=days,
            iocs=kql_list(confirmed_iocs),
            devices=kql_list(devices),
            users=kql_list(users),
        ))

    # report.md
    write_report(os.path.join(args.out, "report.md"), cfg, rows, suspect_rows,
                 enriched, iocs, devices, users, bool(api_key))

    print()
    print("Wrote to {0}/:".format(args.out))
    print("  - suspects.csv / suspects.json   ({0} suspect row(s))".format(len(suspect_rows)))
    print("  - sentinel_filled.kql            (paste into Sentinel -> Logs)")
    print("  - sentinel_entities.txt          ({0} device(s), {1} user(s))".format(len(devices), len(users)))
    print("  - report.md                      (human-readable summary)")
    if not api_key:
        print("\nNOTE: set VT_API_KEY and re-run to populate verdicts.")
    return 0


def write_report(path, cfg, rows, suspect_rows, enriched, iocs, devices, users, vt_checked):
    mal = [v for v, r in enriched.items() if r and r.get("malicious", 0) >= int(cfg["virustotal"].get("malicious_threshold", 5))]
    lines = []
    lines.append("# SOC Investigation Report\n")
    lines.append("## Summary\n")
    lines.append("- Rows unified: **{0}**".format(len(rows)))
    lines.append("- Distinct IOCs: **{0}**".format(len(iocs)))
    lines.append("- VirusTotal: **{0}**".format("checked" if vt_checked else "SKIPPED (no VT_API_KEY)"))
    lines.append("- Confirmed-malicious IOCs: **{0}**".format(len(mal)))
    lines.append("- Suspect rows: **{0}**".format(len(suspect_rows)))
    lines.append("- Affected devices: **{0}** | users: **{1}**\n".format(len(devices), len(users)))

    lines.append("## IOC verdicts\n")
    lines.append("| IOC | Type | VT malicious | VT total | Reputation | Verdict |")
    lines.append("|---|---|---|---|---|---|")
    for v, r in sorted(iocs.items()):
        res = enriched.get(v) or {}
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            v, r, res.get("malicious", "-"), res.get("total", "-"),
            res.get("reputation", "-"), verdict_for(res, cfg["virustotal"])))
    lines.append("")

    lines.append("## Affected devices & users\n")
    lines.append("**Devices:** " + (", ".join(devices) if devices else "_none_"))
    lines.append("\n**Users:** " + (", ".join(users) if users else "_none_") + "\n")

    lines.append("## Next steps (human-confirmed)\n")
    lines.append("1. Paste `out/sentinel_filled.kql` into Sentinel -> Logs to confirm blast radius.")
    lines.append("2. Open the matching incidents in Sentinel.")
    closing = cfg.get("closing", {}) or {}
    lines.append("3. Classify as **{0}** / {1} and close, using this comment:".format(
        closing.get("classification", "TruePositive"),
        closing.get("classification_reason", "SuspiciousActivity")))
    lines.append("   > " + closing.get("comment_template", "Validated via Defender + VirusTotal + Sentinel."))
    lines.append("\n_Claude prepares this list; you click Close in Sentinel._\n")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
