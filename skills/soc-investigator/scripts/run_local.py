#!/usr/bin/env python3
"""
run_local.py — opt-in LOCAL full-automation for the soc-investigator skill.

For a CISO who wants his daily triage to run end-to-end on his own machine with
his own API keys, stopping for ONE manual approval before anything is closed.

This is the automated counterpart to the air-gapped cowork flow (QUICKSTART.md).
It is fully OPTIONAL: every API stage is guarded by the presence of credentials,
and with no credentials it just tells you the manual step and continues — so the
script is always safe to run.

Credentials come from a local .env (git-ignored) or the environment — NEVER from
Claude. See assets/.env.example. Stdlib only.

Stages:
  1. Build Defender hunting KQL from config.json.
  2. Defender: if Entra creds present, run each query via Graph Security
     runHuntingQuery and write CSVs to exports/defender/. Else: manual export.
  3. Enrich locally via VirusTotal (reuses enrich.run()).
  4. Sentinel: if creds present, run out/sentinel_filled.kql via the Log Analytics
     Query API and save results. Else: manual.
  5. APPROVAL GATE — print the report + close package, require you to type "yes".
     Closing incidents is only attempted with --close AND full creds; otherwise
     the package is printed for you to action in the Sentinel UI.

Usage:
    python3 scripts/run_local.py --config config.json            # safe dry/manual-aware run
    python3 scripts/run_local.py --config config.json --close    # also close (needs ARM creds)
"""
import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import enrich          # noqa: E402  (reused pipeline)
import gen_queries     # noqa: E402  (reused IOC loader + query builder)

TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_HUNT = "https://graph.microsoft.com/v1.0/security/runHuntingQuery"
LA_QUERY = "https://api.loganalytics.io/v1/workspaces/{wid}/query"


# ---------- tiny .env + env helpers ----------
def load_dotenv(path):
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def env(name):
    return os.environ.get(name, "").strip()


def has_azure():
    return all(env(k) for k in ("AZ_TENANT_ID", "AZ_CLIENT_ID", "AZ_CLIENT_SECRET"))


# ---------- minimal HTTP (stdlib) ----------
def _post(url, data=None, headers=None, form=False):
    body = None
    headers = dict(headers or {})
    if form:
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_token(scope):
    return _post(
        TOKEN_URL.format(tenant=env("AZ_TENANT_ID")),
        data={
            "grant_type": "client_credentials",
            "client_id": env("AZ_CLIENT_ID"),
            "client_secret": env("AZ_CLIENT_SECRET"),
            "scope": scope,
        },
        form=True,
    )["access_token"]


# ---------- Defender (Graph Security) ----------
def defender_hunt(kql, token):
    """runHuntingQuery → list[dict] rows."""
    res = _post(GRAPH_HUNT, data={"Query": kql},
                headers={"Authorization": "Bearer " + token})
    return res.get("results", []) or []


def write_rows_csv(path, rows):
    cols = []
    for r in rows:
        for k in r.keys():
            if k not in cols:
                cols.append(k)
    if not cols:
        cols = ["DeviceName"]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


# ---------- Sentinel (Log Analytics query) ----------
def la_run(workspace_id, kql, token):
    res = _post(LA_QUERY.format(wid=workspace_id), data={"query": kql},
                headers={"Authorization": "Bearer " + token})
    tables = res.get("tables", []) or []
    if not tables:
        return [], []
    t = tables[0]
    cols = [c["name"] for c in t.get("columns", [])]
    return cols, t.get("rows", [])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Local full-automation for soc-investigator (manual approval at the end).")
    ap.add_argument("--config", required=True)
    ap.add_argument("--exports", default="exports/defender")
    ap.add_argument("--out", default="out")
    ap.add_argument("--env", default=".env", help="path to local .env (git-ignored)")
    ap.add_argument("--close", action="store_true", help="attempt Sentinel incident close (needs ARM creds)")
    args = ap.parse_args(argv)

    load_dotenv(args.env)
    base = os.path.dirname(os.path.abspath(args.config))
    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    os.makedirs(args.exports, exist_ok=True)
    os.makedirs(args.out, exist_ok=True)

    days = int(cfg.get("time_window_days", 7))
    groups = cfg.get("machine_groups") or []
    iocs = gen_queries.load_iocs(cfg, base)

    # ---- Stage 1+2: Defender ----
    if has_azure():
        print("[Defender] Entra creds found — running hunting queries via Graph Security…")
        token = get_token("https://graph.microsoft.com/.default")
        for g in groups:
            kql = gen_queries.build_query(g, iocs, days)
            try:
                rows = defender_hunt(kql, token)
            except urllib.error.HTTPError as e:
                print("  ! {0}: HTTP {1} — skipping".format(g["name"], e.code), file=sys.stderr)
                continue
            out_csv = os.path.join(args.exports, "defender_{0}.csv".format(g["name"]))
            write_rows_csv(out_csv, rows)
            print("  ✓ {0}: {1} row(s) → {2}".format(g["name"], len(rows), out_csv))
    else:
        print("[Defender] No Entra creds (AZ_*). MANUAL step:")
        print("  1) python3 scripts/gen_queries.py --config " + args.config)
        print("  2) run each out/queries/defender_*.kql in Defender, Export CSV → " + args.exports)
        print("  (then re-run this script, or just continue if the CSVs are already there)\n")

    # ---- Stage 3: enrich (VirusTotal) ----
    summary = enrich.run(cfg, args.exports, args.out)
    if summary is None:
        print("\nNo Defender CSVs to enrich yet. Add them to {0} and re-run.".format(args.exports))
        return 1

    # ---- Stage 4: Sentinel pivot ----
    kql_path = summary["sentinel_kql"]
    if has_azure() and env("LA_WORKSPACE_ID"):
        print("\n[Sentinel] Running blast-radius query via Log Analytics…")
        kql = open(kql_path, "r", encoding="utf-8").read()
        try:
            token = get_token("https://api.loganalytics.io/.default")
            cols, rows = la_run(env("LA_WORKSPACE_ID"), kql, token)
            sres = os.path.join(args.out, "sentinel_results.csv")
            with open(sres, "w", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(cols)
                w.writerows(rows)
            print("  ✓ {0} row(s) → {1}".format(len(rows), sres))
        except urllib.error.HTTPError as e:
            print("  ! Log Analytics HTTP {0}; paste {1} into Sentinel manually.".format(e.code, kql_path))
    else:
        print("\n[Sentinel] No creds — paste {0} into Sentinel → Logs to get machines + users.".format(kql_path))

    # ---- Stage 5: APPROVAL GATE ----
    print("\n================ REVIEW ================")
    print(open(summary["report_md"], "r", encoding="utf-8").read())
    print("=======================================")
    print("Affected devices: {0} | users: {1}".format(len(summary["devices"]), len(summary["users"])))
    print("Close package: classification '{0}' / '{1}'".format(
        (cfg.get("closing") or {}).get("classification", "TruePositive"),
        (cfg.get("closing") or {}).get("classification_reason", "SuspiciousActivity")))

    try:
        ans = input("\nApprove and proceed to CLOSE these risks? type 'yes': ").strip().lower()
    except EOFError:
        ans = ""
    if ans != "yes":
        print("Not approved — nothing closed. Review out/report.md and re-run when ready.")
        return 0

    if args.close and has_azure() and env("AZ_SUBSCRIPTION_ID") and env("AZ_RESOURCE_GROUP") and env("LA_WORKSPACE_NAME"):
        print("[Close] ARM creds present — see references/local-automation.md for the incident "
              "PATCH call. (Closing is intentionally conservative; wire incident IDs per your tenant.)")
    else:
        print("[Close] Approved. Close the incidents in the Sentinel UI using the package above "
              "(or supply ARM creds + --close to automate). out/soc_report.csv is ready to upload "
              "to Threat Sentinel (soc-update.com).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
