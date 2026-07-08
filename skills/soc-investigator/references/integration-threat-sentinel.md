# Integration — Threat Sentinel (soc-update.com)

The `soc-investigator` skill is the **execution** half of a loop. The **intel**
half is **Threat Sentinel** (https://soc-update.com, repo `Kaidanov/soc-update`):
it polls ~10 external threat feeds every 24h and emits candidate IOCs, daily
briefings, and Sentinel KQL. This skill takes those indicators, hunts them inside
your tenant, enriches them, finds the affected machines/users, and prepares
closure — then hands a report back.

The two systems connect through a **CSV bridge** — no API, so the air-gap holds.

```
 Threat Sentinel ──IOCs CSV (BaseDomain / IOC)──▶ soc-investigator
   (external intel)                                (internal hunt + enrich)
        ▲                                                    │
        └──── soc_report.csv ◀───────────────────────────────┘
              Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type
```

## Direction 1 — Intel IN (Threat Sentinel → skill)

1. In Threat Sentinel, export the indicators (e.g. the daily `New_query.csv`, or
   any report CSV that has a `BaseDomain` or `IOC` column).
2. Save it locally and point your config at it:
   ```json
   { "ioc_file": "./exports/threat-sentinel/New_query.csv" }
   ```
3. `gen_queries.py` reads these columns case-insensitively and classifies each
   value into domains / urls / hashes: **`BaseDomain`, `IOC`, `Domain`, `URL`,
   `Hash`, `SHA256`, `MD5`, `SHA1`**. They're merged with any inline `config.iocs`.

## Direction 2 — Findings OUT (skill → Threat Sentinel)

`enrich.py` always writes `out/soc_report.csv` in Threat Sentinel's exact schema,
one row per distinct IOC, sorted by Score. Upload it through the Threat Sentinel
console to record what was actually found and closed.

### Field mapping

| Column | Source in the skill |
|---|---|
| `Status` | `config.soc_report.default_status` (default `Open`) |
| `IOC` | the indicator value |
| `Verdict` | `malicious` / `suspicious` / `benign` / `unchecked` (VT detections vs threshold) |
| `Score` | confidence 0–100 (detections dominate) |
| `Country` | VirusTotal `country` (domains/IPs; blank for files) |
| `Tags` | VirusTotal `tags` + `config.soc_report.extra_tags`, `;`-joined |
| `Created` | VirusTotal `creation_date` (domains) / `first_submission_date` (files), ISO date |
| `Link` | VirusTotal GUI permalink (`/gui/domain` · `/ip-address` · `/file` · `/url`) |
| `Type` | `domain` / `url` / `ip` / `file` |

Tune the constant bits in `config.json`:
```json
"soc_report": { "default_status": "Open", "extra_tags": ["tenant:IL"] }
```

## What stays manual

Closing incidents happens in the Sentinel UI (human-confirmed). Uploading
`soc_report.csv` into Threat Sentinel is also a human step through its console —
the skill never calls the Threat Sentinel API.

---

## Prompt to finish the Threat Sentinel side (use in a separate session)

The skill side of the bridge is done. To make Threat Sentinel **accept** the
skill's `soc_report.csv` and **emit** a clean IOC CSV, run a session in the
`Kaidanov/soc-update` repo (or against its Lovable project) with this prompt:

> **Context:** This is "Threat Sentinel" (soc-update.com), a Lovable app that
> aggregates external threat feeds into daily SOC briefings. It needs to
> interoperate, via CSV files only (no shared API, air-gapped), with a separate
> "soc-investigator" cowork skill that hunts IOCs inside a Microsoft Defender /
> Sentinel tenant.
>
> **Add two CSV interop features:**
>
> 1. **Export IOCs** — a button/endpoint that downloads the current candidate
>    indicators as a CSV with at least an `IOC` column (and, where known,
>    `Type` ∈ {domain,url,ip,file}). This is what the skill ingests as its hunt
>    list. Keep the existing `New_query.csv` shape (`BaseDomain,RequestsYesterday,
>    RequestsBefore`) working too.
>
> 2. **Import findings** — a CSV upload that ingests rows in exactly this schema
>    and upserts them into the report/dashboard table, keyed on `IOC`:
>    `Status,IOC,Verdict,Score,Country,Tags,Created,Link,Type`
>    - `Score` is 0–100; `Verdict` ∈ {malicious,suspicious,benign,unchecked};
>      `Tags` is `;`-separated; `Link` is a VirusTotal GUI URL; `Created` is an
>      ISO date.
>    - Treat the file as untrusted: strip leading `= + - @` from cells to prevent
>      CSV/formula injection, validate the header, and cap row count.
>    - Show an import summary (added / updated / skipped) and never auto-execute
>      anything destructive on import.
>
> **Constraints:** keep it CSV-only (no direct API to the skill), preserve the
> existing dashboard columns, and add a short README note describing the bridge
> with the soc-investigator skill.

Once that's deployed, the loop runs hands-free except for the human upload/download
and the human-confirmed incident close.
