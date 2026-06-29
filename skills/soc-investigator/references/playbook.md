# SOC Investigator — detailed cowork runbook

The operating model: **Claude thinks and scripts; you click and export.** No API,
no MCP, no Entra connection from Claude. Your keys and raw tenant data never
leave your machine.

```
 Phase 0  Discovery (browser)      new domains / new exes  ──┐
 Phase 1  Config (you edit JSON)   IOCs + machine groups   ◄─┘ seed
 Phase 2  Generate (local script)  N Defender KQL files
 Phase 3  Hunt (browser)           run + export N CSVs
 Phase 4  Enrich (local script)    unify + VirusTotal + Sentinel prep
 Phase 5  Pivot & close (browser)  affected machines/users → close (you confirm)
```

## Phase 0 — Discovery (optional but recommended)
If you don't already have a known IOC list, start by *finding* anomalies. Run the
discovery queries in `kql-defender.md` (D1: new base domains seen yesterday but
not in 90d; D2: new executables created yesterday, unseen before). Eyeball the
output and lift suspicious `BaseDomain` / `SHA256` values into your config.

## Phase 1 — Config
```bash
cp assets/config.example.json config.json   # config.json is git-ignored
```
Fill in:
- `iocs.domains / urls / hashes` (or `ioc_file`).
- `machine_groups` — one CSV per entry; the generic form of the "7 files".
- `time_window_days`, `virustotal.malicious_threshold`, `portals`, `closing`.

Your config must satisfy `assets/config.schema.json`.

## Phase 2 — Generate
```bash
python3 scripts/gen_queries.py --config config.json --out out/queries
```
Produces `out/queries/defender_<group>.kql` plus a checklist. Stdlib-only, no
network.

## Phase 3 — Hunt in Defender (you, in your browser)
For each `.kql`: `security.microsoft.com` → Hunting → Advanced hunting → paste →
Run → **Export → CSV** → save into `./exports/defender/`.

## Phase 4 — Enrich
```bash
export VT_API_KEY=...        # your key, your machine; optional (VT skipped if unset)
python3 scripts/enrich.py --config config.json
```
Outputs in `out/`: `suspects.csv`, `suspects.json`, `report.md`,
`sentinel_entities.txt`, `sentinel_filled.kql`.

Verdict rule: `malicious` when VT detections ≥ `malicious_threshold`;
`suspicious` when ≥ `suspicious_min` **and** reputation < 0. Detections dominate;
reputation alone is unreliable.

## Phase 5 — Pivot & close in Sentinel (you confirm)
1. Paste `out/sentinel_filled.kql` into Sentinel → Logs to confirm the machines
   and users affected (see `kql-sentinel.md` S1).
2. Use S2 to map those entities to open incidents.
3. Review the prepared classification + comment, then **you** close each incident
   in the Sentinel UI (S3). Closing is never automated.

## Privacy & safety invariants
- Claude never connects to Defender / Sentinel / VirusTotal / Entra.
- The VirusTotal key is only ever in your `VT_API_KEY` env var.
- `config.json`, `exports/`, `out/`, and `*.csv` are git-ignored — never commit
  tenant data.
- Destructive console actions (closing incidents) are prepared by the tooling and
  executed only by a human.
