---
name: car-finder-il
description: >-
  Find a good second-hand car in Israel (Yad2) and get pinged on your phone only
  when something genuinely worth it shows up. Reads listings via an Apify actor
  (no login, no browser, reads-only), scores each car against its OWN peer cohort
  (price vs comparable listings, hand / יד, owner type, km-per-year, photos), and
  on a schedule pushes ONLY new matches and real price drops to WhatsApp (wa-ai),
  Telegram or ntfy. Use whenever the user wants to: search used cars, "find me a
  car", set buying criteria, watch the market, get alerts smarter than Yad2's, or
  compare a specific car's price to similar ones. Triggers on: רכב יד שנייה, חיפוש
  רכב, קניית רכב, יד2 רכב, התראות רכב, "find me a used car", "watch for cars",
  "is this car a good price". Reads-only — it finds and ranks, it does not post,
  bump, or buy.
---

# Car Finder IL (חיפוש רכב יד שנייה)

Turns the noise of Yad2 into a short, ranked shortlist and a phone ping. It does
the one thing Yad2's own alerts don't: it only tells you about a car when the car
is actually *good* — priced under its peers, low hand, private owner, sane km.

## What this CAN and CANNOT do

**CAN (public, reads-only):** read live Yad2 vehicle listings — price, make,
model, year, km, hand (יד), owner type, photo count, link — through a maintained
Apify actor that absorbs Yad2's anti-bot. Score them against their own cohort.
Remember what it already showed you. Push new hits to your phone on a schedule.

**CANNOT:** publish, bump (הקפצה), edit, message sellers, or buy. There is **no
posting API** on any Israeli car board; this skill stays firmly on the read side
on purpose. It's a finder, not a bot, so it can't get your account flagged.

**Baseline it has to beat:** Yad2's saved-search alerts are free but fire on
every crude filter match. The whole point here is the *scoring* — pinging you
only when a listing beats the median of comparable cars, not on everything.

## No מחירון API — so we benchmark honestly

לוי יצחק has no public API, so the skill doesn't fake one. Instead each car is
scored against **its own cohort** — same make+model, year within ±1, pulled in
the same fetch. "12% under comparable listings" is self-contained and true.
If you have a personal target price per model, put it in your criteria and the
hard filters enforce it.

## The engine

All logic is stdlib-only Python under `scripts/` — no install. Run with bash;
add `--json` to `search` for machine-readable output.

```bash
# one-shot ranked search (no DB, no push) — start here with mock data:
python3 scripts/carfinder.py search examples/criteria.example.json --source mock --lang he

# real data once APIFY_TOKEN + APIFY_ACTOR_ID are set:
python3 scripts/carfinder.py search my_criteria.json --lang he

# the scheduled job: push ONLY new matches / price drops to your phone:
python3 scripts/carfinder.py run my_criteria.json

# print the seen_listings table SQL:
python3 scripts/carfinder.py init-db
```

| File | Does |
|------|------|
| `scripts/carfinder.py` | CLI, EN/HE rendering, orchestration |
| `scripts/source.py` | fetch listings (Apify adapter + mock), normalise |
| `scripts/score.py` | hard filters + cohort-relative weighted score |
| `scripts/store.py` | Supabase dedupe (PostgREST); local-file fallback offline |
| `scripts/notify.py` | push to wa-ai / Telegram / ntfy / stdout |

## Criteria file

A small JSON the user edits — see `examples/criteria.example.json`. Hard filters
(`price_max`, `year_min`, `km_max`, `hand_max`, `owner_type`, `make`) gate what's
even considered; `weights` tune the score; `min_score` sets the ping threshold;
`label` and `lang` shape the message. Keep one file per search; the `id` field
is the dedupe key.

## How to drive this as the assistant

1. If the user describes what they want ("family SUV, private owner, under 90k"),
   write them a criteria JSON — don't make them learn the schema.
2. Run `search --source mock` first to show the shape, then `search` on real data
   once their Apify keys are in. Always surface the **reasons**, not just a score.
3. Only suggest the cron + Supabase + phone-push (the `run` path) once they like
   the shortlist. It's optional; `search` alone is fully useful.
4. Stay honest: this finds and ranks. For posting/selling, that's a different,
   browser-driven problem — don't imply this can buy or message anyone.
