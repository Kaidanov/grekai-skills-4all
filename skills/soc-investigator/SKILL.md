---
name: soc-investigator
description: Air-gapped SOC investigation cowork for Microsoft Defender + VirusTotal + Sentinel in locked-down tenants where direct API / MCP / Entra access is forbidden. Use when the user wants to triage IOCs (URLs, domains, file hashes), hunt them in Defender Advanced Hunting split by machine type, unify and enrich the results via VirusTotal, pivot into Sentinel to find affected machines and users, and close incidents — without granting any API access. Claude generates the KQL and the local enrichment, the human runs the queries and exports CSVs in their own authenticated browser, and Claude prepares (never auto-executes) the incident-close step. Triggers on: "run the SOC investigation", "hunt these IOCs", "Defender/Sentinel triage", "check these domains/hashes", "close the risks in Sentinel".
---

# SOC Investigator — Air-Gapped IOC Triage

## FIRST RESPONSE — show these usage options (do this before anything else)

When this skill is invoked, your **first reply** must briefly say what this does in
one line, then present this menu and ask the user to pick a number (or describe their
goal). Do **not** start hunting until they choose.

> **SOC Investigator** — triage suspicious indicators across Microsoft Defender →
> VirusTotal → Sentinel, find which machines/users are affected, and prepare the
> closure. No API access required (you run portal queries in your own browser).
>
> **What do you want to do?**
> 1. **Quick triage** — I have IOCs (domains/URLs/hashes); find affected machines & users → [QUICKSTART](./QUICKSTART.md)
> 2. **Discover new threats** — find brand-new domains/executables to investigate (anomaly hunt) → `references/kql-defender.md`
> 3. **Enrich exports I already have** — I exported Defender CSVs; unify + VirusTotal → `scripts/enrich.py`
> 4. **Threat Sentinel loop** — import IOCs from / push findings back to soc-update.com → `references/integration-threat-sentinel.md`
> 5. **Automate it locally** — run end-to-end with my own API keys, one approval at the end → `references/local-automation.md`
> 6. **Explain / is this safe?** — what it does, what leaves my machine → [GUIDE](./GUIDE.md)

For the full mental model, modes, and FAQ, see **[`GUIDE.md`](./GUIDE.md)**.

---

> **Lazy? Point the user at [`QUICKSTART.md`](./QUICKSTART.md)** — a one-page,
> copy-paste run-through (key → IOCs → Defender export → enrich → Sentinel → close).

**Two modes:**
- **Cowork (default, no API):** Claude generates KQL + steps; the human runs them
  in their own browser and exports CSVs; Claude enriches locally. The five phases below.
- **Local-automated (opt-in):** the human supplies their own API keys and
  `scripts/run_local.py` runs Defender→VirusTotal→Sentinel end-to-end locally,
  stopping for one manual approval before closing. See
  [`references/local-automation.md`](./references/local-automation.md).

A **cowork** playbook for SOC / CISO threat-hunting in a tenant where the CTO
will **not** allow Claude (or any tool) to connect to Defender, Sentinel,
VirusTotal, or Entra via API/MCP. Claude is the *execution brain*; the human is
the *authenticated hands*; the browser and a local Python script do the work.

> **Privacy contract — state this to the user up front.**
> Claude never connects to any security API and never receives your API keys.
> You run every portal query in your own already-signed-in Chrome and export the
> CSVs locally. The VirusTotal key is read from the `VT_API_KEY` environment
> variable on *your* machine. Claude only sees data you choose to paste back.

## When to use

Trigger when the user asks to investigate indicators of compromise across
Microsoft Defender → VirusTotal → Sentinel, e.g. "hunt these domains", "triage
this hash", "find every machine that touched this URL", "close these risks in
Sentinel" — especially when they mention they **can't** or **won't** use APIs.

## The five phases

Walk the user through these in order. Do the thinking and the local scripting;
hand the browser steps to the user with exact, copy-pasteable instructions.

### Phase 1 — Config (the only place specifics live)
Have the user copy `assets/config.example.json` to `config.json` and fill in:
- `iocs` (domains / urls / hashes) — or point `ioc_file` at a list. `ioc_file`
  may be a **Threat Sentinel (soc-update.com) export CSV** with a `BaseDomain` or
  `IOC` column; the skill folds those indicators into the hunt (see
  `references/integration-threat-sentinel.md`).
- `machine_groups` — one query (and one exported CSV) per entry. This is the
  generic version of the original "7 files": declare however many groups you
  want, each with a KQL `filter` like `DeviceType == "Server"`.
- `time_window_days`, `virustotal.malicious_threshold`, `portals.*`, `closing.*`.

Validate it: the structure must satisfy `assets/config.schema.json`.

### Phase 2 — Generate the hunting queries (local, no network)
```bash
python3 scripts/gen_queries.py --config config.json --out out/queries
```
This writes one `defender_<group>.kql` per machine group, with the IOCs injected
as KQL `dynamic([...])` lists and the group `filter` applied. It prints a cowork
checklist. Show the user the generated queries.

### Phase 3 — Hunt in Defender (browser, the human drives)
For **each** generated `.kql`, instruct the user to:
1. Open `security.microsoft.com` → Hunting → **Advanced hunting**.
2. Paste the query, **Run**.
3. **Export → CSV**, saving into `./exports/defender/` (keep the group name).
Remind them they are doing this in their own authenticated session — Claude is
not connecting.

### Phase 4 — Unify + enrich (local, no portal)
```bash
export VT_API_KEY=...   # the user's key, on their machine; optional
python3 scripts/enrich.py --config config.json
```
This unifies every CSV, de-dups the IOCs, looks each up in **VirusTotal v3**
(domains/ips/files/urls; skipped cleanly if `VT_API_KEY` is unset), applies the
verdict rule, and writes to `out/`:
- `suspects.csv` / `suspects.json` — CSV-injection-safe suspect rows.
- `report.md` — human-readable summary with IOC verdicts + affected entities.
- `sentinel_entities.txt` — suspect device + user lists.
- `sentinel_filled.kql` — the Sentinel blast-radius query with the suspect
  entities already injected, ready to paste.
- `soc_report.csv` — findings in **Threat Sentinel's** schema
  (`Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type`); the user uploads
  this back into the soc-update.com console to close the loop.

Summarize `out/report.md` for the user.

### Phase 5 — Pivot & close in Sentinel (browser + human confirmation)
1. Have the user paste `out/sentinel_filled.kql` into **Sentinel → Logs** and
   Run, to confirm the blast radius (every machine + user that touched a
   confirmed IOC). They export this too if useful.
2. Claude **prepares** the closure package from `config.closing`: the list of
   incidents/entities, the classification (e.g. `TruePositive` /
   `SuspiciousActivity`), and the justification comment.
3. The **user** opens the incidents in Sentinel and clicks Close.
   **Never instruct automated/bulk closing and never claim to have closed
   anything — closing is the human's confirmed action.**

## Notes on correctness
- Verdict rule: `malicious` when VT engines flagging ≥ `malicious_threshold`;
  `suspicious` when ≥ `suspicious_min` **and** reputation < 0. Reputation alone
  is a weak signal (often 0 even for real malware) — detections dominate.
- All scripts are **Python standard library only** — no `pip install`.
- See `references/playbook.md`, `references/kql-defender.md`, and
  `references/kql-sentinel.md` for the detailed runbook and query catalog.
- `references/integration-threat-sentinel.md` describes the full loop with
  **Threat Sentinel (soc-update.com)**: intel in via IOC CSV, findings out via
  `soc_report.csv` — a CSV bridge, no API.

## Files
- `GUIDE.md` — CISO guide (what it is, modes, what you can do, safety, FAQ).
- `QUICKSTART.md` — the one-page lazy-CISO run-through.
- `scripts/gen_queries.py` — config → per-group Defender KQL.
- `scripts/enrich.py` — unify CSVs + VirusTotal + Sentinel prep (exposes `run()`).
- `scripts/run_local.py` — opt-in local full-automation (manual approval at the end).
- `assets/config.example.json` / `config.schema.json` — the generic surface.
- `assets/.env.example` — local-automation credentials template.
- `references/local-automation.md` — the local-automated mode spec.
- `agents/soc-investigator.agent.md` — bundled cowork-SOC agent definition.
