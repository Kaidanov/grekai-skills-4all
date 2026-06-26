#!/usr/bin/env python3
"""
carfinder.py — second-hand car finder for Israel (Yad2), reads-only.

Commands:
  search  one-shot. Fetch -> score -> print ranked matches. No DB, no push.
  run     the scheduled job. Fetch -> score -> diff vs Supabase -> push ONLY
          new matches & price drops to your phone -> remember them.
  init-db print the SQL to create the seen_listings table.

  python3 scripts/carfinder.py search examples/criteria.example.json --source mock
  python3 scripts/carfinder.py search criteria.json --lang he
  python3 scripts/carfinder.py run criteria.json
  python3 scripts/carfinder.py init-db

Add --json to search for machine-readable output. Stdlib only.

What this CAN see: public Yad2 listings (price, model, year, km, hand, owner,
photos, link) via an Apify read actor — no login, no browser, reads only.
What it CANNOT do: post, bump, or edit anything. This is a finder, not a bot.
Baseline to beat: Yad2's own saved-search alerts are free but fire on every
crude match; this only pings when a car actually beats its peer cohort.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source as src      # noqa: E402
import score as scoring   # noqa: E402
import store as storage   # noqa: E402
import notify as notifier # noqa: E402

REASONS = {
    "under_peers":   ("{0}% under comparable listings", "{0}% מתחת למודעות דומות"),
    "over_peers":    ("{0}% above comparable listings", "{0}% מעל מודעות דומות"),
    "first_hand":    ("first hand", "יד ראשונה"),
    "private_owner": ("private owner", "בעלות פרטית"),
    "company_owner": ("ex-company/lease", "רכב חברה/ליסינג"),
    "low_km":        ("low km (~{0}/yr)", "ק\"מ נמוך (~{0} לשנה)"),
    "high_km":       ("high km (~{0}/yr)", "ק\"מ גבוה (~{0} לשנה)"),
    "few_photos":    ("only {0} photos", "רק {0} תמונות"),
}


def load_criteria(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data.setdefault("id", Path(path).stem)
    return data


def render_reason(code, value, lang):
    en, he = REASONS.get(code, (code, code))
    tmpl = he if lang == "he" else en
    return tmpl.format(value) if value is not None else tmpl


def fmt_price(p):
    return "₪{:,}".format(p) if p else "—"


def line(r, lang):
    l = r["listing"]
    head = "%s %s · %s · %s" % (
        l.get("make") or "", l.get("model") or "",
        l.get("year") or "?", fmt_price(l.get("price")))
    reasons = ", ".join(render_reason(c, v, lang) for c, v in r["reasons"][:3])
    drop = ""
    if r.get("dropped_from"):
        word = "ירד מ-" if lang == "he" else "dropped from"
        drop = "  ⬇ %s %s" % (word, fmt_price(r["dropped_from"]))
    return "  [%3d] %s\n        %s%s\n        %s" % (
        r["score"], head.strip(), reasons, drop, l.get("url") or "")


# --------------------------------------------------------------------------- #
def cmd_search(args):
    crit = load_criteria(args.criteria)
    listings = src.fetch_listings(crit, source=args.source)
    results = scoring.apply(listings, crit)
    top = results[: args.limit]
    if args.json:
        print(json.dumps(top, ensure_ascii=False, indent=2))
        return
    if not top:
        print("No matches cleared your filters / min_score." if args.lang != "he"
              else "אין התאמות שעברו את הסינון / ציון מינימום.")
        return
    header = ("Top %d of %d matches (scanned %d listings):" if args.lang != "he"
              else "%d ההתאמות הטובות מתוך %d (נסרקו %d מודעות):")
    print(header % (len(top), len(results), len(listings)))
    for r in top:
        print(line(r, args.lang))


def cmd_run(args):
    crit = load_criteria(args.criteria)
    listings = src.fetch_listings(crit, source=args.source)
    results = scoring.apply(listings, crit)
    db = storage.Store()
    seen = db.seen(crit["id"])
    fresh, dropped = db.split_new(results, seen)
    db.remember(crit["id"], results)
    hits = fresh + dropped
    if not hits:
        print("run: nothing new for '%s' (%d scored, all seen)." %
              (crit["id"], len(results)))
        return
    lang = crit.get("lang", args.lang)
    label = crit.get("label", crit["id"])
    title = ("🚗 %d new for «%s»" if lang != "he" else "🚗 %d חדשים ל-«%s»") % (
        len(hits), label)
    msg = title + "\n\n" + "\n\n".join(line(r, lang) for r in hits[: args.limit])
    channel = notifier.send(msg)
    print("run: pushed %d hit(s) via %s (%d new, %d price-drop)." %
          (len(hits), channel, len(fresh), len(dropped)))


def cmd_init_db(args):
    sql = (Path(__file__).resolve().parent.parent / "db" /
           "seen_listings.sql").read_text(encoding="utf-8")
    print(sql)


# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(prog="carfinder")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="one-shot ranked search")
    s.add_argument("criteria")
    s.add_argument("--source", choices=["apify", "mock"], default="apify")
    s.add_argument("--lang", choices=["en", "he"], default="en")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    r = sub.add_parser("run", help="scheduled: push only new matches")
    r.add_argument("criteria")
    r.add_argument("--source", choices=["apify", "mock"], default="apify")
    r.add_argument("--lang", choices=["en", "he"], default="en")
    r.add_argument("--limit", type=int, default=8)
    r.set_defaults(func=cmd_run)

    d = sub.add_parser("init-db", help="print seen_listings SQL")
    d.set_defaults(func=cmd_init_db)

    args = p.parse_args()
    try:
        args.func(args)
    except (RuntimeError, ValueError) as e:
        print("error: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
