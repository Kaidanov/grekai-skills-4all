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

![5-phase cowork pipeline](https://raw.githubusercontent.com/Kaidanov/grekai-skills-4all/main/assets/images/soc-investigator-pipeline.svg)

## How it works in 30 seconds

You give it indicators; it gives you *which of your machines and users are
affected* and a closure package — without any tool ever touching your tenant's
APIs.

**Example.** You suspect the domain `evil-newdomain.example` and a hash:

1. Put them in `config.json` → `python3 scripts/gen_queries.py --config config.json`
   produces one Defender KQL per machine group (Servers, Workstations, Linux…).
2. You paste each query into **your** Defender browser session and Export CSV.
3. `python3 scripts/enrich.py --config config.json` unifies the CSVs, checks each
   IOC in VirusTotal with **your** key, and writes:
   ```
   out/report.md            → 2 malicious IOCs, 3 affected machines, 2 users
   out/sentinel_filled.kql  → blast-radius query, entities pre-injected
   out/soc_report.csv       → Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type
   ```
4. You run the Sentinel query, review the prepared close package, and click Close.

Nothing left your machine except the queries you chose to paste.

## The full loop — with Threat Sentinel (soc-update.com)

This skill is the **execution** half of a loop whose **intel** half is
[Threat Sentinel](https://soc-update.com) — your service that polls external
threat feeds and emits candidate IOCs/KQL. They connect through a **CSV bridge**
(no API), so the air-gap holds end to end:

![full loop](https://raw.githubusercontent.com/Kaidanov/grekai-skills-4all/main/assets/images/soc-investigator-loop.svg)

- **Intel in:** point `config.ioc_file` at a Threat Sentinel export — any CSV with
  a `BaseDomain` or `IOC` column (e.g. its `New_query.csv`). The skill folds those
  indicators straight into the hunt.
- **Findings out:** `enrich.py` writes `out/soc_report.csv` in Threat Sentinel's
  exact schema (`Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type`). Upload
  it back through the Threat Sentinel console to record what was found and closed.

See [`references/integration-threat-sentinel.md`](./references/integration-threat-sentinel.md)
for the field mapping and the cowork up/download steps.

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

### Easiest — Download ZIP (no CLI)

Download **[soc-investigator.zip](https://github.com/Kaidanov/grekai-skills-4all/releases/download/skill-downloads/soc-investigator.zip)**
(also via the **Download ZIP** button on the
[skill page](https://grekai-skills-4all.vercel.app/skill?id=soc-investigator)), then:

- **Claude Desktop / claude.ai:** Customize → Skills → **+** → *Upload a skill* → pick the ZIP.
- **Claude Code:** unzip it into your global skills folder and restart:
  ```bash
  unzip soc-investigator.zip -d ~/.claude/skills/      # macOS/Linux
  ```
  ```powershell
  Expand-Archive soc-investigator.zip "$env:USERPROFILE\.claude\skills\"   # Windows PowerShell
  ```
  This yields `~/.claude/skills/soc-investigator/SKILL.md`. Then type `/soc-investigator`.

### Or via the command line

A skill is loaded from a `SKILL.md` inside a `.claude/skills/<name>/` folder.
Pick **personal** (available in every project) or **project** (this repo only).

> ⚠️ **Use an absolute path for a personal/global install.** The destination in
> the command is where the files go. A *relative* path like
> `.claude/skills/...` installs into the folder you're standing in — which is why
> a global `C:\Users\<you>\.claude\skills` can end up empty. For the global
> location, give the absolute path:

**Personal / global — all projects**

```powershell
# Windows PowerShell
npx degit Kaidanov/grekai-skills-4all/skills/soc-investigator "$env:USERPROFILE\.claude\skills\soc-investigator"
```
```bat
:: Windows cmd.exe
npx degit Kaidanov/grekai-skills-4all/skills/soc-investigator "%USERPROFILE%\.claude\skills\soc-investigator"
```
```bash
# macOS / Linux
npx degit Kaidanov/grekai-skills-4all/skills/soc-investigator ~/.claude/skills/soc-investigator
```

**Project — this repo only** (run from the project root):

```bash
npx degit Kaidanov/grekai-skills-4all/skills/soc-investigator .claude/skills/soc-investigator
```

### Make Claude Code see it

1. **Restart Claude Code** if the `.claude/skills/` folder did *not* exist when
   your session started — Claude watches existing skill folders live, but a
   brand-new top-level skills directory is only picked up on restart. (This is
   the #1 reason a fresh install "won't import".)
2. **Verify the path** — `SKILL.md` must sit *directly* in the skill folder:
   ```bash
   # should print the file, not "No such file"
   ls ~/.claude/skills/soc-investigator/SKILL.md          # macOS/Linux
   dir "%USERPROFILE%\.claude\skills\soc-investigator\SKILL.md"   # Windows cmd
   ```
   If it's nested one level deeper (e.g. `…/soc-investigator/soc-investigator/`),
   move the inner contents up so `SKILL.md` is at the top of the folder.
3. **Invoke it** — type `/soc-investigator`, or just ask in plain language
   ("run the SOC investigation", "hunt these IOCs") and Claude loads it
   automatically from the description.

**Still not showing?** Restart Claude Code · confirm the `SKILL.md` path above ·
make sure you launched `claude` from the project that holds the `.claude/` folder
(for a project install) · confirm `SKILL.md` starts with a `---` YAML frontmatter
block. `degit` also needs Node + network and an empty destination (add `--force`
to overwrite).

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
- `references/integration-threat-sentinel.md` — the full loop with soc-update.com
  (CSV field mapping + a ready prompt to finish the Threat Sentinel side).
- `references/playbook.md` — the detailed runbook.
- `assets/config.example.json` / `config.schema.json` — the generic surface.
- `agents/soc-investigator.agent.md` — the bundled cowork-SOC agent.
- Flow diagrams: `assets/images/soc-investigator-pipeline.svg` and
  `…-loop.svg` (in the repo's shared images folder).

---

_Not a replacement for your SOC's judgment. Verdicts are data-grounded
(VirusTotal detections); a human reviews findings and closes incidents._
