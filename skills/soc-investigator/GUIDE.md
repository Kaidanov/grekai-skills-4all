# SOC Investigator — CISO Guide

A plain-English guide to what this is, how to use it properly, and what you can do
with it. If you just want the steps, use [QUICKSTART.md](./QUICKSTART.md).

## What it is (in one breath)
You hand it suspicious **indicators** (domains, URLs, file hashes). It tells you
**which of your machines and users touched them**, how dangerous they are
(VirusTotal), and hands you a ready package to **close the incidents** — across
Microsoft **Defender** and **Sentinel**, without you writing a single KQL query.

## The mental model
```
   IOCs you care about
          │
   ┌──────▼───────┐   you paste & export in YOUR browser
   │  Defender    │   (or it's automated locally with your keys)
   │  hunting     │──► exports/defender/*.csv
   └──────┬───────┘
          │  enrich.py (local, your VirusTotal key)
   ┌──────▼───────┐
   │ VirusTotal   │──► out/report.md + out/sentinel_filled.kql + out/soc_report.csv
   └──────┬───────┘
          │  paste the ready-made query
   ┌──────▼───────┐
   │  Sentinel    │──► affected machines + users
   └──────┬───────┘
          │  YOU approve
   ┌──────▼───────┐
   │ Close risks  │   (prepared for you; you click Close)
   └──────────────┘
```

## The golden rule (why your CISO/CTO can say yes)
**Nothing connects to your tenant's APIs by default, and nothing destructive happens
without your explicit approval.** Claude never sees your keys or raw data — you run
the portal queries in your own signed-in browser and only paste back what you choose.
Your VirusTotal key lives in an environment variable on your machine.

## Two ways to run it
| Mode | Who touches the portals | Setup | Use when |
|---|---|---|---|
| **Cowork** (default) | You (browser), Claude guides | none — just a VirusTotal key | The CTO won't grant API access |
| **Local-automated** (opt-in) | `run_local.py` with your keys | an Entra app + `.env` | You can register an app and want it hands-off |

Both end the same way: **you approve before anything closes.**

## What you can do with it (the menu)
1. **Quick triage** — you have IOCs → get affected machines/users + a close package. → [QUICKSTART](./QUICKSTART.md)
2. **Discover new threats** — find brand-new domains/executables (seen yesterday, never before) to investigate. → `references/kql-defender.md`
3. **Enrich exports you already have** — drop Defender CSVs in `exports/defender/`, get verdicts. → `scripts/enrich.py`
4. **Threat Sentinel loop** — pull candidate IOCs from your soc-update.com app and push findings back. → `references/integration-threat-sentinel.md`
5. **Automate locally** — one command runs Defender→VirusTotal→Sentinel; stops for your `yes`. → `references/local-automation.md`

## What you get each run (`out/`)
- **`report.md`** — the human summary: malicious IOCs, affected machines & users, next steps.
- **`sentinel_filled.kql`** — the ready-to-paste Sentinel query (entities already filled in).
- **`soc_report.csv`** — `Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type` (upload to Threat Sentinel).
- `suspects.csv` / `suspects.json` — the raw suspect rows.

## How verdicts are decided
VirusTotal **engine detections** drive the call: `malicious` when detections ≥ your
`malicious_threshold` (default 5); `suspicious` when ≥1 detection **and** negative
reputation. Reputation alone is ignored (it's often 0 even for real malware). You set
the thresholds in `config.json`.

## Working habits (so it stays effortless)
- Keep one folder (`~/.claude/skills/soc-investigator/`). `config.json` remembers your
  IOCs, machine groups and thresholds — next run is just steps 2–6.
- Re-run discovery (option 2) when you want fresh leads; paste the interesting ones
  into `config.json`.
- Never commit `config.json`, `exports/`, `out/`, `.env` — they're git-ignored for you.

## FAQ
- **Does Claude see my data or keys?** No. Keys stay in your env/`.env`; you paste only
  what you choose. Cowork mode makes no API calls at all.
- **Will it close incidents on its own?** Never. It *prepares* the close; you click
  Close (or, in local mode, you type `yes` and pass `--close`).
- **Do I need to know KQL?** No — the queries are generated for you.
- **No Python?** Cowork still works; the scripts just save you the manual unify/enrich.
- **What if the CTO blocks the Entra app?** Stay in cowork mode — everything works,
  you just export CSVs by hand.
