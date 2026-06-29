# Local automation mode (opt-in)

The default skill flow is **air-gapped cowork** — no API access; you run the portal
queries (QUICKSTART.md). This document defines the **opt-in local-automated mode**:
you supply your own API keys once and `scripts/run_local.py` runs the whole flow on
your machine, stopping for **one manual approval** before anything is closed.

Keys live only on your machine (a git-ignored `.env`); Claude never sees them.

## When to use it
Use cowork mode if the CTO won't grant an Entra app. Use local mode if you (the
CISO) can register an app and want your daily triage to run unattended up to the
approval gate.

## Credentials (`.env`, git-ignored)
Copy `assets/.env.example` → `.env`:

| Var | Required | Unlocks |
|---|---|---|
| `VT_API_KEY` | yes | VirusTotal verdicts |
| `AZ_TENANT_ID`, `AZ_CLIENT_ID`, `AZ_CLIENT_SECRET` | optional | Defender + Sentinel automation |
| `LA_WORKSPACE_ID` | optional | Sentinel blast-radius query |
| `AZ_SUBSCRIPTION_ID`, `AZ_RESOURCE_GROUP`, `LA_WORKSPACE_NAME` | optional | incident close via ARM |

Entra app registration needs app permissions **`ThreatHunting.Read.All`** (Microsoft
Graph, for Defender Advanced Hunting) and **Log Analytics Reader** on the workspace
(for Sentinel). Auth is OAuth2 **client-credentials**.

## What `run_local.py` does
```bash
python3 scripts/run_local.py --config config.json          # safe: API stages run only if creds exist
python3 scripts/run_local.py --config config.json --close  # also close (needs ARM creds)
```

1. **Build** Defender KQL from `config.json` (reuses `gen_queries`).
2. **Defender** — with Entra creds, calls Graph Security `runHuntingQuery`
   (`POST https://graph.microsoft.com/v1.0/security/runHuntingQuery`) per machine
   group and writes the results as CSVs into `exports/defender/`. No creds → prints
   the manual export step and continues.
3. **Enrich** — runs the local VirusTotal pipeline (`enrich.run()`), producing
   `out/report.md`, `out/soc_report.csv`, `out/sentinel_filled.kql`.
4. **Sentinel** — with creds + `LA_WORKSPACE_ID`, runs `sentinel_filled.kql` via the
   Log Analytics Query API (`POST https://api.loganalytics.io/v1/workspaces/{id}/query`)
   and saves `out/sentinel_results.csv`. No creds → paste it in the portal.
5. **Approval gate** — prints the report + the close package and waits for you to
   type `yes`. Nothing destructive happens before that. On approval, by default it
   tells you to close in the UI; with `--close` + ARM creds it performs the
   incident close (`PATCH` the Sentinel incident to `Status=Closed` with your
   classification/comment).

## Safety invariants
- Every API stage is **guarded** by credential presence; the script is always safe
  to run and degrades to the manual QUICKSTART steps.
- **Closing is never automatic** — it requires both the typed `yes` and `--close`
  (plus ARM creds). Default behaviour only prepares the package.
- Keys never leave your machine; `.env`, `config.json`, `exports/`, `out/` are
  git-ignored.

## Roadmap
- Enumerate matching Sentinel incidents by entity and present them in the approval
  gate for selective close.
- Optional scheduled run (cron / Task Scheduler) that stops at the gate and notifies.
