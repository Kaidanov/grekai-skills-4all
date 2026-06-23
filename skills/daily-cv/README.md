# daily-cv

A config-driven, self-learning **daily job-search agent**. Each run finds one qualifying role,
verifies the posting is live and accepting applications, and produces a ready-to-apply package —
an ATS-optimised CV and a tailored cover letter (DOCX + PDF) — using **only verified facts from
your profile**. It learns from every run and never repeats a company+role.

## What it does

- Searches broad job sources and a configurable company watchlist.
- Validates each link is alive and actively accepting applications (rules R1-R31).
- Generates application files from **your profile only** — no invented facts.
- Updates a local (or dual local+Google) tracker.
- Records durable lessons so the next run is smarter.

## Why it works this way

- **Profile-driven, not hardcoded.** Everything personal lives in one gitignored file,
  `profile/PROFILE.json` — the single source of truth. The generators read it; nothing about any
  person is baked into the code. That makes the skill reusable by anyone and safe to publish.
- **Anti-fabrication by design.** Every number in a CV/cover letter must trace to
  `profile.key_metrics`. Missing experience is recorded as a gap, never written into existence.
- **Self-learning.** `knowledge/DAILY_CV_LEARNINGS.md` accumulates failure patterns and selection
  rules that are applied before every run.

## The profile + init model

```
profile/PROFILE.template.json   committed   blank template (placeholders)
profile/PROFILE.example.json    committed   fictional Jane Doe — complete shape + zero-setup demo
profile/PROFILE.json            gitignored  YOUR real data (never committed)
```

First-time users run **[INIT.md](INIT.md)** once to build `PROFILE.json` by gathering specifics
from LinkedIn, a Gmail scan (Gmail MCP), exported AI chat history, or a manual questionnaire —
with the assistant **confirming every fact** and never fabricating. See [profile/README.md](profile/README.md).

## Safety / anti-fabrication

- `PROFILE.json`, `*.local.*`, and generated `*.docx`/`*.pdf`/`out/` are gitignored — **no PII is
  ever committed**.
- No secrets or tokens in any committed file; contact details live only in your local profile.
- The assistant uses only profile facts, honours `profile.anti_fabrication_notes`, cites public
  sources for company claims, and marks unsupported requirements as gaps. Full contract:
  *Anti-Fabrication Rules* in [SKILL.md](SKILL.md).

## HOW-TO (quick start)

1. **Init your profile** — copy the template and fill it (or use INIT.md to gather it):
   ```powershell
   Copy-Item .\profile\PROFILE.template.json .\profile\PROFILE.json
   notepad .\profile\PROFILE.json
   ```
2. **Configure sources** — edit `config/SOURCES.md`, `config/JOB_CRITERIA.md`, `config/WATCHLIST.md`.
3. **Run** — point your AI assistant at [SKILL.md](SKILL.md) (or schedule it via
   [SCHEDULED_TASK_PROMPT.md](SCHEDULED_TASK_PROMPT.md)). To generate documents directly:
   ```powershell
   cd .\scripts
   python generate_cv.py  --company Acme --role "VP Engineering" --run-date 20260101 --output-dir ./out
   python generate_pdf.py --company Acme --role "VP Engineering" --run-date 20260101 --output-dir ./out
   python generate_cover_letter.py --company Acme --role "VP Engineering" --run-date 20260101 --output-dir ./out
   ```
4. **Outputs** — `<slug>_CV_<Company>_<date>.{docx,pdf}` and `<slug>_CoverLetter_…`, where `<slug>`
   is `profile.identity.filename_slug`. A loud warning means `PROFILE.json` was missing and the
   fictional example was used.

The full step-by-step (with how the pipeline works end to end) is in **[HOW-TO.md](HOW-TO.md)**.

## How it works (pipeline)

```
INIT.md ──> profile/PROFILE.json ─┐
config/*  ──────────────────────> │
knowledge/DAILY_CV_LEARNINGS.md ─>│  SKILL.md workflow
                                  │   1. search (techmap/LinkedIn/Greenhouse/watchlist)
                                  │   2. validate live + rules R1-R31
                                  │   3. job-intelligence report + partial learnings
                                  │   4. scripts/generate_cv.py + generate_pdf.py
                                  │   5. scripts/generate_cover_letter.py
                                  │   6. interview prep
                                  └─> 7. update tracker  8. append learnings
```

## Files

- `SKILL.md` — the main workflow (read this to run).
- `INIT.md` — one-time per-person onboarding.
- `HOW-TO.md` — detailed step-by-step guide.
- `SCHEDULED_TASK_PROMPT.md` — prompt for a scheduled routine.
- `profile/` — the single source of truth (template, fictional example, your gitignored `PROFILE.json`).
- `config/` — sources, job criteria, watchlist.
- `knowledge/` — learnings log + outreach templates.
- `scripts/` — document generators (`profile_loader.py`, `generate_cv.py`, `generate_pdf.py`, `generate_cover_letter.py`).
- `trackers/` — local tracker template.

Configure the skill through `config/SOURCES.md`, `config/JOB_CRITERIA.md`, and
`config/WATCHLIST.md`, and your `profile/PROFILE.json`, before running.
