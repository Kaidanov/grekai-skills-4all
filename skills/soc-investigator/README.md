# SOC Investigator — Air-Gapped IOC Triage

**Defender → VirusTotal → Sentinel, without giving Claude any API access.**

A cowork playbook for SOC / CISO threat-hunting in locked-down tenants where the
CTO forbids direct API / MCP / Entra connections. Claude is the execution
brain; **you** are the authenticated hands in your own browser; a local,
stdlib-only Python engine does the data work. Your API keys and raw tenant data
never leave your machine.

> **Will it be an agent?** Yes — it ships as a skill **and** a bundled agent
> definition (`agents/soc-investigator.agent.md`). But because APIs are off the
> table, it's honestly a *cowork agent*: it drives the workflow and processes
> data locally while you run the portal queries and confirm the destructive step.

## Why this exists

The usual answer to "automate SOC triage" is a fleet of API integrations
(Graph Security, Log Analytics, VirusTotal API) behind a managed identity. If
your CTO won't grant that, those designs are dead on arrival. This skill is the
deliberately lean alternative: **exact queries + local enrichment + guided
browser steps**, nothing to authorize.

## The flow

```
Phase 0  Discovery (browser)   find new domains / new exes  ─┐ seed
Phase 1  Config (edit JSON)    your IOCs + machine groups  ◄─┘
Phase 2  Generate (script)     one Defender KQL per machine group
Phase 3  Hunt (browser)        run + Export CSV per group
Phase 4  Enrich (script)       unify + VirusTotal + Sentinel prep
Phase 5  Pivot & close (browser, you confirm)  affected machines/users → close
```

## Install

```bash
npx degit Kaidanov/grekai-skills-4all/skills/soc-investigator .claude/skills/soc-investigator
```

## Quick start

```bash
cp assets/config.example.json config.json      # then edit: IOCs, machine_groups, thresholds
python3 scripts/gen_queries.py --config config.json --out out/queries
# → run each out/queries/defender_*.kql in Defender, Export CSV to ./exports/defender/
export VT_API_KEY=...                           # optional; VT skipped cleanly if unset
python3 scripts/enrich.py --config config.json
# → review out/report.md, paste out/sentinel_filled.kql into Sentinel, close incidents
```

Or just ask Claude: **"run the SOC investigation"** and it walks you through each
phase.

## Configure your specifics — `assets/config.example.json`

Everything tenant-specific lives in one JSON file (no secrets — the VirusTotal
key comes from `VT_API_KEY`):

| Field | What it controls |
|---|---|
| `iocs.{domains,urls,hashes}` | The indicators to hunt (or point `ioc_file` at a list). |
| `machine_groups[]` | One query + one CSV per entry. The generic form of the fixed "7 files" — each has a KQL `filter` like `DeviceType == "Server"`. |
| `time_window_days` | Look-back → `ago(Nd)`. |
| `virustotal.malicious_threshold` | Engines flagging an IOC before it's `malicious`. |
| `portals.{defender_url,sentinel_url}` | Where the browser steps point. |
| `closing.{classification,comment_template}` | The prepared incident-close package. |

## What the scripts produce

`scripts/enrich.py` writes to `out/`:
- `report.md` — IOC verdicts + affected machines/users + next steps.
- `suspects.csv` / `suspects.json` — CSV-injection-safe suspect rows.
- `sentinel_entities.txt` — suspect device + user lists.
- `sentinel_filled.kql` — Sentinel blast-radius query, entities pre-injected.

## Safety invariants

- Claude never connects to Defender / Sentinel / VirusTotal / Entra.
- The VirusTotal key only ever lives in your `VT_API_KEY` env var.
- `config.json`, `exports/`, `out/`, `*.csv` are git-ignored — tenant data stays local.
- Closing incidents is **prepared** by the tooling and **executed by a human** —
  never automated, never reported as done until you confirm.

## Files

- `SKILL.md` — the activation playbook Claude follows.
- `scripts/gen_queries.py` — config → per-machine-group Defender KQL.
- `scripts/enrich.py` — unify CSVs + VirusTotal + Sentinel prep (stdlib only).
- `references/kql-defender.md` — discovery + targeted hunt query catalog.
- `references/kql-sentinel.md` — blast-radius, incident-mapping, close queries.
- `references/playbook.md` — the detailed runbook.
- `assets/config.example.json` / `config.schema.json` — the generic surface.
- `agents/soc-investigator.agent.md` — the bundled cowork-SOC agent.

---

_Not a replacement for your SOC's judgment. Verdicts are data-grounded
(VirusTotal detections); a human reviews findings and closes incidents._
