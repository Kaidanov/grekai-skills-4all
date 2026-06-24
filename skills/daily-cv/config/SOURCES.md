# Sources

This file tells the skill where to read verified candidate facts, where to track jobs, and
where to save generated files. Fill in your own values — keep anything private out of any
public copy of this repo.

## Candidate Profile Source

The **single source of truth is `profile/PROFILE.json`** (gitignored). Run `INIT.md` once to
populate it. The generators load it via `scripts/profile_loader.py`.

| Setting | Value |
|---|---|
| Profile file | `profile/PROFILE.json` (your real, gitignored profile) |
| Example fallback | `profile/PROFILE.example.json` (fictional Jane Doe) |
| Candidate display name | from `profile.identity.display_name` |
| Filename slug | from `profile.identity.filename_slug` |
| Read-only external source (optional) | `<YOUR_PROFILE_DOC_URL_OPTIONAL>` |

Rules:

- `profile/PROFILE.json` is the only authorised source for resume facts.
- All numbers must trace back to `profile.key_metrics`.
- Never fabricate metrics, titles, dates, employers, technologies, or credentials.
- If a job asks for experience not present in the profile, record it as a gap.

### Anti-Fabrication Notes (read every run)

Per-person guardrails live in `profile.anti_fabrication_notes`. Keep exact titles, exact date
ranges, and careful framing of investments/clearances there so tailoring never drifts. The
generic, project-wide rules are in `SKILL.md` (Anti-Fabrication Rules).

## Tracker Setup

| Setting | Value |
|---|---|
| Tracker mode | `local` (or `both`) |
| Local tracker path | `<YOUR_LOCAL_TRACKER_PATH>` |
| Tracker template | `trackers/applications.template.csv` |
| Google Sheet URL (optional) | `<YOUR_GOOGLE_SHEET_URL_OPTIONAL>` |
| Google Sheet main tab | `Applications` |
| Duplicate check key | `company + role title` |
| Date format | `YYYY-MM-DD` |

Notes:
- Local tracker is the **primary** R2 source (grep first).
- Google Sheets is the **secondary** R2 source (may exceed MCP limit).
- The agent does NOT update Sheets directly — mirror the markdown/CSV row manually.

## Output Storage

| Setting | Value |
|---|---|
| Storage mode | `local` |
| Local output folder | `<YOUR_OUTPUT_FOLDER>` |
| Learnings log | `knowledge/DAILY_CV_LEARNINGS.md` (committed, scrubbed) + optional local copy |
| Keep local backup | `true` |

### File Naming Convention

Driven by `profile.identity.filename_slug`:

`<slug>_CV_[Company]_[YYYYMMDD].docx`
`<slug>_CV_[Company]_[YYYYMMDD].pdf`
`<slug>_CoverLetter_[Company]_[YYYYMMDD].docx`
`<slug>_CoverLetter_[Company]_[YYYYMMDD].pdf`

## Repository URLs

| Resource | URL |
|---|---|
| GitHub repo | `https://github.com/Kaidanov/grekai-skills` |
| Raw skill base | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/` |
| SKILL.md | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/SKILL.md` |
| Watchlist | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/config/WATCHLIST.md` |
| Job criteria | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/config/JOB_CRITERIA.md` |
| Learnings | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/knowledge/DAILY_CV_LEARNINGS.md` |
| Outreach | `https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/knowledge/Startup_Outreach_Approach.md` |

## Contact Fields

Contact details live in `profile/PROFILE.json` (gitignored). Do not commit phone, email, or
LinkedIn URL to any public repository — keep these in your local profile only.

| Field | Source |
|---|---|
| Email | `profile.contact.email` |
| Phone | `profile.contact.phone` |
| LinkedIn | `profile.contact.linkedin` |

## Status Values

- `found`
- `validated`
- `ready_to_apply`
- `applied`
- `interviewing`
- `offer`
- `rejected`
- `closed`
- `archived`
- `proactive_outreach_pending`
