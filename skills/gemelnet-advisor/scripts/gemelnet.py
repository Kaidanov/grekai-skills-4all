#!/usr/bin/env python3
"""GemelNet Advisor — query & analyse Israeli pension / provident / study funds.

Public, fund-level data only, pulled live from the official GemelNet open
dataset on data.gov.il (CKAN datastore API). Standard library only — no pip
install required for the core. The optional ``scan --pdf`` mode will use
``pdfplumber`` / ``pypdf`` / ``pdftotext`` if one happens to be installed and
degrades gracefully otherwise.

This is data-grounded analysis, NOT financial advice. Numbers are historical,
net-of-fee fund returns as published by the regulator (Ministry of Finance,
Capital Market, Insurance & Savings Authority).

Commands
--------
  resources                 List the GemelNet dataset's resource IDs.
  funds   [--q TEXT]        Search funds by name / managing company.
  fund     FUND_ID          Show the latest snapshot for one fund.
  compare  ID ID [ID ...]   Compare funds side by side.
  rank     FUND_ID          Rank a fund against its like-for-like peers.
  revenue  FUND_ID --balance N   Estimate annual shekel cost (mgmt fee) on a balance.

Examples
--------
  python3 gemelnet.py resources
  python3 gemelnet.py funds --q "אלטשולר"
  python3 gemelnet.py funds --q "study"
  python3 gemelnet.py fund 9012
  python3 gemelnet.py compare 9012 512 1234
  python3 gemelnet.py rank 9012
  python3 gemelnet.py revenue 9012 --balance 250000
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request

CKAN = "https://data.gov.il/api/3/action"
# The GemelNet package slug on data.gov.il. Resources under it hold the
# monthly fund-level return / fee tables (one per year-range).
PACKAGE_ID = "gemelnet"
USER_AGENT = "gemelnet-advisor/1.0 (+https://github.com/Kaidanov/grekai-skills-4all)"
TIMEOUT = 30

# Candidate field names. The GemelNet schema publishes English column names;
# we keep a small synonym map so the engine keeps working if a column is
# renamed or localised. The first key found in a record wins.
FIELDS = {
    "id":        ["FUND_ID", "fund_id", "ID"],
    "name":      ["FUND_NAME", "fund_name", "NAME"],
    "company":   ["MANAGING_CORPORATION", "MANAGING_COMPANY", "managing_corporation"],
    "kind":      ["FUND_CLASSIFICATION", "SUB_TYPE", "fund_classification", "TARGET_POPULATION"],
    "period":    ["REPORT_PERIOD", "MONTH", "report_period"],
    "assets":    ["TOTAL_ASSETS", "total_assets"],
    "month_yld": ["MONTHLY_YIELD", "monthly_yield"],
    "ytd_yld":   ["YEAR_TO_DATE_YIELD", "year_to_date_yield"],
    "yld_3yr":   ["AVG_ANNUAL_YIELD_TRAILING_3YRS", "avg_annual_yield_trailing_3yrs"],
    "yld_5yr":   ["AVG_ANNUAL_YIELD_TRAILING_5YRS", "avg_annual_yield_trailing_5yrs"],
    "mgmt_fee":  ["AVG_ANNUAL_MANAGEMENT_FEE", "MANAGEMENT_FEE", "avg_annual_management_fee"],
    "deposit_fee": ["AVG_DEPOSIT_FEE", "DEPOSITS_FEE", "avg_deposit_fee"],
    "sharpe":    ["SHARPE_RATIO", "sharpe_ratio"],
    "stdev":     ["STANDARD_DEVIATION", "standard_deviation"],
}


# --------------------------------------------------------------------------- #
# Low-level CKAN access (stdlib only)
# --------------------------------------------------------------------------- #
def _get(action: str, params: dict) -> dict:
    url = f"{CKAN}/{action}?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload.get("success"):
        raise RuntimeError(f"CKAN error for {action}: {payload.get('error')}")
    return payload["result"]


def list_resources() -> list[dict]:
    """Return the resource descriptors under the GemelNet package."""
    result = _get("package_show", {"id": PACKAGE_ID})
    return result.get("resources", [])


def _datastore_resource_id() -> str:
    """Pick the most relevant datastore-active resource (largest table)."""
    candidates = [r for r in list_resources() if r.get("datastore_active")]
    if not candidates:
        raise RuntimeError(
            "No datastore-active resource found under package "
            f"'{PACKAGE_ID}'. Run the 'resources' command to inspect."
        )
    # Prefer the current main data table ("...לשנים 2024-היום") over older
    # year-range tables and over the change-log resource ("פירוט שינויים").
    def score(r: dict) -> int:
        blob = f"{r.get('name','')} {r.get('description','')}".lower()
        s = 0
        s += 3 if "נתוני" in blob else 0          # the main data tables
        s += 3 if "היום" in blob else 0           # "...to today" = current table
        s -= 5 if ("שינויים" in blob or "פירוט" in blob) else 0  # change-log, skip
        s += sum(k in blob for k in ("2026", "2025", "2024"))
        return s
    candidates.sort(key=score, reverse=True)
    return candidates[0]["id"]


def datastore_search(resource_id: str, q=None, filters=None, limit=100) -> dict:
    params = {"resource_id": resource_id, "limit": limit}
    if q:
        params["q"] = q
    if filters:
        params["filters"] = json.dumps(filters, ensure_ascii=False)
    return _get("datastore_search", params)


# --------------------------------------------------------------------------- #
# Field helpers
# --------------------------------------------------------------------------- #
def pick(record: dict, key: str):
    for name in FIELDS[key]:
        if name in record and record[name] not in (None, ""):
            return record[name]
    return None


def as_float(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return None


def latest(records: list[dict]) -> list[dict]:
    """Keep only the most recent report period per fund id."""
    best: dict[str, dict] = {}
    for r in records:
        fid = str(pick(r, "id"))
        period = str(pick(r, "period") or "")
        if fid not in best or period > str(pick(best[fid], "period") or ""):
            best[fid] = r
    return list(best.values())


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_resources(_args) -> int:
    resources = list_resources()
    if not resources:
        print(f"No resources found under package '{PACKAGE_ID}'.")
        return 1
    print(f"GemelNet dataset resources (package '{PACKAGE_ID}'):\n")
    for r in resources:
        flag = "datastore" if r.get("datastore_active") else "file     "
        print(f"  [{flag}] {r['id']}  {r.get('name','')}")
    return 0


def _summary_row(r: dict) -> str:
    return (
        f"{str(pick(r,'id')):>7}  "
        f"{(pick(r,'name') or '')[:34]:<34}  "
        f"{(pick(r,'company') or '')[:18]:<18}  "
        f"YTD {fmt_pct(pick(r,'ytd_yld')):>7}  "
        f"3yr {fmt_pct(pick(r,'yld_3yr')):>7}  "
        f"fee {fmt_pct(pick(r,'mgmt_fee')):>6}"
    )


def fmt_pct(value) -> str:
    f = as_float(value)
    return f"{f:.2f}%" if f is not None else "  n/a"


def cmd_funds(args) -> int:
    rid = _datastore_resource_id()
    # Each fund has many monthly rows; over-fetch so latest() yields enough
    # distinct funds to fill the requested display limit.
    result = datastore_search(rid, q=args.q, limit=max(args.limit * 60, 400))
    rows = latest(result.get("records", []))
    if not rows:
        print("No funds matched.")
        return 1
    rows.sort(key=lambda r: as_float(pick(r, "yld_3yr")) or -999, reverse=True)
    print(f"  {'ID':>7}  {'Fund':<34}  {'Company':<18}  {'YTD':>11}  {'3yr':>11}  {'Fee':>10}")
    for r in rows[: args.limit]:
        print("  " + _summary_row(r))
    print(f"\n{len(rows)} fund(s). Historical, net-of-fee public data — not advice.")
    return 0


def _fetch_fund(rid: str, fund_id: str) -> dict | None:
    for key in FIELDS["id"]:
        try:
            result = datastore_search(rid, filters={key: fund_id}, limit=400)
        except (urllib.error.HTTPError, RuntimeError):
            continue  # column doesn't exist on this resource → try next synonym
        records = result.get("records", [])
        if records:
            return latest(records)[0]
    return None


def cmd_fund(args) -> int:
    rid = _datastore_resource_id()
    r = _fetch_fund(rid, args.fund_id)
    if not r:
        print(f"Fund {args.fund_id} not found.")
        return 1
    print(f"Fund {pick(r,'id')} — {pick(r,'name')}")
    print(f"  Managing company : {pick(r,'company')}")
    print(f"  Classification   : {pick(r,'kind')}")
    print(f"  Report period    : {pick(r,'period')}")
    print(f"  Total assets     : {pick(r,'assets')}")
    print(f"  Monthly yield    : {fmt_pct(pick(r,'month_yld'))}")
    print(f"  Year-to-date     : {fmt_pct(pick(r,'ytd_yld'))}")
    print(f"  3yr avg annual   : {fmt_pct(pick(r,'yld_3yr'))}")
    print(f"  5yr avg annual   : {fmt_pct(pick(r,'yld_5yr'))}")
    print(f"  Mgmt fee (annual): {fmt_pct(pick(r,'mgmt_fee'))}")
    print(f"  Deposit fee      : {fmt_pct(pick(r,'deposit_fee'))}")
    print(f"  Sharpe ratio     : {pick(r,'sharpe') or 'n/a'}")
    print("\nHistorical public fund-level data — data-grounded analysis, not advice.")
    return 0


def cmd_compare(args) -> int:
    rid = _datastore_resource_id()
    rows = [r for fid in args.fund_ids if (r := _fetch_fund(rid, fid))]
    if not rows:
        print("None of the requested funds were found.")
        return 1
    print(f"  {'ID':>7}  {'Fund':<34}  {'Company':<18}  {'YTD':>11}  {'3yr':>11}  {'Fee':>10}")
    for r in rows:
        print("  " + _summary_row(r))
    best = max(rows, key=lambda r: as_float(pick(r, "yld_3yr")) or -999)
    cheap = min(rows, key=lambda r: as_float(pick(r, "mgmt_fee")) or 999)
    print(f"\n  Highest 3yr return : {pick(best,'id')} ({fmt_pct(pick(best,'yld_3yr'))})")
    print(f"  Lowest mgmt fee    : {pick(cheap,'id')} ({fmt_pct(pick(cheap,'mgmt_fee'))})")
    print("\nLike-for-like comparison only matters within the same fund class. Not advice.")
    return 0


def cmd_rank(args) -> int:
    rid = _datastore_resource_id()
    target = _fetch_fund(rid, args.fund_id)
    if not target:
        print(f"Fund {args.fund_id} not found.")
        return 1
    kind = pick(target, "kind")
    # Pull a broad page and keep same-classification peers.
    result = datastore_search(rid, q=kind, limit=args.limit)
    peers = [r for r in latest(result.get("records", []))
             if pick(r, "kind") == kind and as_float(pick(r, "yld_3yr")) is not None]
    if target["_id"] not in {p.get("_id") for p in peers}:
        peers.append(target)
    peers.sort(key=lambda r: as_float(pick(r, "yld_3yr")) or -999, reverse=True)
    n = len(peers)
    pos = next((i for i, r in enumerate(peers, 1)
                if str(pick(r, "id")) == str(args.fund_id)), None)
    print(f"Fund {pick(target,'id')} — {pick(target,'name')}")
    print(f"  Class           : {kind}")
    print(f"  3yr avg annual  : {fmt_pct(pick(target,'yld_3yr'))}")
    print(f"  Mgmt fee        : {fmt_pct(pick(target,'mgmt_fee'))}")
    if pos:
        pct = round((n - pos) / max(n - 1, 1) * 100)  # higher = better
        print(f"  Rank by 3yr ret : #{pos} of {n} like-for-like peers "
              f"({pct}th percentile, higher is better)")
    print("\nPeers = same GemelNet classification. Historical data, not advice.")
    return 0


def cmd_revenue(args) -> int:
    rid = _datastore_resource_id()
    r = _fetch_fund(rid, args.fund_id)
    if not r:
        print(f"Fund {args.fund_id} not found.")
        return 1
    fee = as_float(pick(r, "mgmt_fee"))
    if fee is None:
        print("This fund has no published management-fee figure.")
        return 1
    annual_cost = args.balance * fee / 100.0
    print(f"Fund {pick(r,'id')} — {pick(r,'name')}")
    print(f"  Annual mgmt fee  : {fee:.2f}%")
    print(f"  On balance       : {args.balance:,.0f} ₪")
    print(f"  Estimated cost   : {annual_cost:,.0f} ₪ / year (~{annual_cost/12:,.0f} ₪ / month)")
    print("\nEstimate from the published fee on a flat balance; ignores deposits, "
          "deposit fees and compounding. Not advice.")
    return 0


# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GemelNet Advisor — Israeli pension fund analysis.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("resources", help="List GemelNet dataset resource IDs").set_defaults(func=cmd_resources)

    fp = sub.add_parser("funds", help="Search funds by name / company")
    fp.add_argument("--q", help="Free-text query (Hebrew or English)")
    fp.add_argument("--limit", type=int, default=25)
    fp.set_defaults(func=cmd_funds)

    one = sub.add_parser("fund", help="Latest snapshot for one fund")
    one.add_argument("fund_id")
    one.set_defaults(func=cmd_fund)

    cp = sub.add_parser("compare", help="Compare two or more funds")
    cp.add_argument("fund_ids", nargs="+")
    cp.set_defaults(func=cmd_compare)

    rk = sub.add_parser("rank", help="Rank a fund against like-for-like peers")
    rk.add_argument("fund_id")
    rk.add_argument("--limit", type=int, default=500)
    rk.set_defaults(func=cmd_rank)

    rv = sub.add_parser("revenue", help="Estimate annual shekel fee cost on a balance")
    rv.add_argument("fund_id")
    rv.add_argument("--balance", type=float, required=True)
    rv.set_defaults(func=cmd_revenue)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except urllib.error.URLError as e:
        print(f"Network error reaching data.gov.il: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
