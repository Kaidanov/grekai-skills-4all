# HOWTO — car-finder-il (English)

A step-by-step from zero to "my phone buzzes when a good car shows up."

## 0. Try it offline first (30 seconds)

No tokens needed — proves the scoring is what you want before you wire anything:

```bash
python3 scripts/carfinder.py search examples/criteria.example.json --source mock --lang en
```

Read the reason line under each car. If those reasons match how *you* judge a
car, the rest is just plumbing.

## 1. Write your criteria

Copy the example and edit:

```bash
cp examples/criteria.example.json my_criteria.json
```

```jsonc
{
  "id": "family-suv",          // dedupe key — keep it stable per search
  "label": "Family SUV < 90k", // shown in the phone push
  "lang": "he",                // push language
  "make": ["Kia", "Hyundai"],  // empty = any
  "year_min": 2019,
  "price_max": 90000,
  "km_max": 120000,
  "hand_max": 2,               // יד ≤ 2
  "owner_type": ["private"],   // drop ex-company / lease
  "min_score": 60,             // ping threshold
  "weights": { "price_value": 0.4, "hand": 0.15, "owner": 0.15,
               "km": 0.15, "photos": 0.05, "fresh": 0.1 }
}
```

`make`/`model` matching is fuzzy and never drops a car for *missing* data — only
for data that actively fails a rule.

## 2. Connect real Yad2 data (Apify)

1. Sign up at [apify.com](https://apify.com) and copy your API token.
2. In [apify.com/store](https://apify.com/store), search **yad2**, open a
   vehicles actor, and copy its id (looks like `user/actor-name`).
3. Export and run:

```bash
export APIFY_TOKEN=apify_api_xxx
export APIFY_ACTOR_ID=user/yad2-vehicles
python3 scripts/carfinder.py search my_criteria.json --lang en
```

If your actor wants a different input shape, add an `apify_input` block to the
criteria — it's passed through verbatim.

Cost note: Apify bills per run/result. A twice-daily scan of one search is cents.

## 3. Turn on phone alerts (the `run` path)

`run` = fetch → score → compare to what it already showed you → push only the
new ones. You need a memory and a channel.

**Memory (Supabase):**

```bash
python3 scripts/carfinder.py init-db        # prints the SQL
# paste it into the Supabase SQL editor, OR:
python3 scripts/carfinder.py init-db | psql "$DATABASE_URL"
export SUPABASE_URL=https://<ref>.supabase.co
export SUPABASE_KEY=<service_role key>
```

No Supabase? `run` still works — it falls back to `~/.car-finder-il/seen.json`
so dedupe survives across runs on one machine.

**Channel (pick one):**

```bash
export WAAI_WEBHOOK_URL=https://your-wa-ai/hook     # WhatsApp via your own agent
# or
export TELEGRAM_BOT_TOKEN=123:abc
export TELEGRAM_CHAT_ID=456
# or (zero setup)
export NTFY_TOPIC=my-car-hunt-7f3a
```

Test:

```bash
python3 scripts/carfinder.py run my_criteria.json
```

First run pushes everything matching; later runs push only new cars and price
drops.

## 4. Put it on a schedule

`.github/workflows/car-finder.yml` already runs `run` twice a day. To use it:

1. Push this skill to your repo.
2. Repo → **Settings → Secrets and variables → Actions** → add `APIFY_TOKEN`,
   `APIFY_ACTOR_ID`, `SUPABASE_URL`, `SUPABASE_KEY`, and your channel secret.
3. Edit the `cron:` lines and the `criteria:` matrix (one line per search).
4. Use the **Run workflow** button to trigger a test run.

## Troubleshooting

- **`APIFY_TOKEN not set`** → you're on the real source with no token. Add it, or
  use `--source mock`.
- **Empty results on real data** → your actor's output keys differ; check one raw
  item and, if needed, map via `apify_input`. The normaliser already tries many
  common key names.
- **No push** → no channel env is set, so it printed to stdout (by design).
- **Re-pinged about the same car** → different machine / no shared Supabase, so
  the local seen-file didn't carry over. Point both at the same `SUPABASE_*`.

## Reminder

This is a finder. It will never post, bump, message a seller, or buy. That's the
sell side and needs a logged-in browser — a separate tool on purpose.
