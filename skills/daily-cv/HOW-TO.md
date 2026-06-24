# daily-cv — HOW-TO

A detailed, step-by-step guide. For the overview see [README.md](README.md); for the full
agent workflow see [SKILL.md](SKILL.md).

## Prerequisites

- Python 3.10+ with `python-docx` and `reportlab`:
  ```powershell
  pip install python-docx reportlab
  ```
- (Optional) `pdfinfo`/`pdftotext` (Poppler) and `pdfplumber` for page-count + ATS checks.
- (Optional) The **Gmail MCP** connector if you want the email-scan path during INIT.

## Step 1 — Initialise your profile (once)

The profile is your single source of truth. Build `profile/PROFILE.json` either manually or by
gathering your specifics — see [INIT.md](INIT.md) for the full onboarding flow (LinkedIn export
or "Save to PDF", Gmail scan, AI chat-history parsing, or a manual questionnaire).

```powershell
# from skills/daily-cv/
Copy-Item .\profile\PROFILE.template.json .\profile\PROFILE.json
notepad .\profile\PROFILE.json
```

Fill every section: `identity`, `contact`, `summary`, `competencies`, `experience[]`,
`education[]`, `volunteering[]`, and especially `key_metrics` — the only numbers the generators
may use. The assistant must **confirm each extracted fact with you** and never invent data.

`PROFILE.json` is gitignored, so it never leaves your machine.

## Step 2 — Configure the search

Edit the three config files to your targets (they ship with sensible defaults):

- `config/SOURCES.md` — where the profile, tracker, and outputs live.
- `config/JOB_CRITERIA.md` — target titles, geography, work-mode, seniority, disqualifiers.
- `config/WATCHLIST.md` — job sources, ATS boards, company watchlist.

Keep anything private out of these files — they are committed. Personal facts belong only in
`PROFILE.json`.

## Step 3 — Run

### Option A — full agent workflow

Point your AI assistant at [SKILL.md](SKILL.md). It will:

1. Bootstrap from `knowledge/DAILY_CV_LEARNINGS.md` (rules + runs log).
2. Search techmap CSVs, then LinkedIn, then Greenhouse, then the watchlist.
3. Validate the best candidate against rules R1-R31 (live, not a duplicate, recent, in scope).
4. Emit a job-intelligence report and write a partial learnings entry.
5. Generate the CV + cover letter via the scripts below.
6. Add interview prep, update the tracker, and append the learnings entry.

### Option B — generate documents directly

```powershell
cd .\scripts
# CV (DOCX) and CV (PDF) — keep --summary/--competencies in sync between them
python generate_cv.py  --company "Acme" --role "VP Engineering" --run-date 20260101 `
       --summary "JD-tuned 2-sentence summary" --output-dir ./out
python generate_pdf.py --company "Acme" --role "VP Engineering" --run-date 20260101 `
       --summary "JD-tuned 2-sentence summary" --output-dir ./out
# Cover letter — pass the model-written body paragraphs (or a body file)
python generate_cover_letter.py --company "Acme" --role "VP Engineering" --run-date 20260101 `
       --body "Hook paragraph..." --body "Match paragraph..." --body "Close paragraph..." `
       --output-dir ./out
```

Useful flags (all generators): `--profile <path>` (override which profile to load),
`--salutation`, `--letter-date`, `--output-dir`. Per-run target defaults can also live in
`profile.target_defaults`.

## Step 4 — Outputs

Files are named from `profile.identity.filename_slug`:

```
<slug>_CV_<Company>_<YYYYMMDD>.docx
<slug>_CV_<Company>_<YYYYMMDD>.pdf
<slug>_CoverLetter_<Company>_<YYYYMMDD>.docx
```

If you see a loud `WARNING: profile/PROFILE.json not found … Jane Doe` banner, the generators
fell back to the fictional example — create your `PROFILE.json` and re-run.

## Step 5 — Validate (recommended)

```powershell
# 1-page check (R15)
pdfinfo .\out\<slug>_CV_Acme_20260101.pdf | Select-String Pages
# ATS keyword check (R11/R28) — normalize whitespace, then match JD keywords
```

Banned-content checks (R12): no emojis, em-dashes, smart quotes, first-person pronouns, Tier-1
buzzwords, or numbers absent from `profile.key_metrics`.

## How the pipeline fits together

```
profile/PROFILE.json ─┐
config/*.md ──────────┼─> SKILL.md (search → validate → report → generate → track → learn)
DAILY_CV_LEARNINGS.md ┘            │
                                   └─> scripts/profile_loader.py
                                         ├─ generate_cv.py   (python-docx)
                                         ├─ generate_pdf.py  (reportlab, ATS-clean text)
                                         └─ generate_cover_letter.py
```

The loader resolves the profile as: `--profile`/`DAILY_CV_PROFILE` → `PROFILE.json` →
`PROFILE.example.json` (with a warning). Everything personal stays in `PROFILE.json`; the rest
of the repo is publishable.

## Troubleshooting

- **"Jane Doe" appears in output** → `PROFILE.json` is missing; copy the template and fill it.
- **`ModuleNotFoundError: docx`/`reportlab`** → `pip install python-docx reportlab`.
- **2-page PDF** → trim a summary sentence, reduce bullets, or tighten margins (R15).
- **ATS keyword miss** → match the JD's exact word form (R21); add it only if it's a real,
  profile-backed fact (anti-fabrication).
