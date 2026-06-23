---
name: daily-cv
description: Config-driven daily job-search agent. First-time users run INIT.md to populate profile/PROFILE.json (their single source of truth); thereafter it reads live config, validates that roles are actively accepting applications, generates an ATS-optimised CV + cover letter from verified profile facts only, and updates a local tracker. Learns from each run.
---

# Daily CV — Automated Job Hunt (v2)

Config-driven, self-learning job-search agent. Runs on demand or on a schedule. Produces one ready-to-apply job package (CV + cover letter, DOCX + PDF) per run, learns from every run, updates its own rules, and never repeats a company+role already in the pipeline.

**First time here?** Run **`INIT.md`** to build your `profile/PROFILE.json` (name, contacts,
experience, metrics). That file is the single source of truth and is gitignored — nothing
personal is committed. See `profile/README.md`.

---

## STEP 0 — SELF-LEARNING BOOTSTRAP (ALWAYS FIRST)

Read `skills/daily-cv/knowledge/DAILY_CV_LEARNINGS.md` in full before doing anything else.

Extract and apply:
- **FAILURE PATTERNS** → hard disqualification rules
- **SELECTION RULES R1–R31** → apply in order to every candidate job
- **RUNS LOG** → every company+role ever selected — never repeat

Without reading this file you will repeat past mistakes. This is non-negotiable.

Then read:
- `skills/daily-cv/profile/PROFILE.json` — the **only** authorised source for candidate facts (fallback: `PROFILE.example.json`)
- `skills/daily-cv/config/SOURCES.md` — profile source, tracker, storage paths
- `skills/daily-cv/config/JOB_CRITERIA.md` — role targets, geography, rules
- `skills/daily-cv/config/WATCHLIST.md` — techmap source, LinkedIn queries, Greenhouse slugs, company lists
- `skills/daily-cv/knowledge/Startup_Outreach_Approach.md` — proactive outreach templates

`profile/PROFILE.json` is the only authorised source for candidate facts. Treat it as
read-only during a run.

---

## STEP 1 — JOB SEARCH (techmap-first, then LinkedIn, then ATS APIs)

### Primary Source A — techmap (Daily-Updated Israeli Tech Jobs)

Download and filter these CSV files from GitHub in priority order:

```
https://raw.githubusercontent.com/mluggy/techmap/main/jobs/software.csv
https://raw.githubusercontent.com/mluggy/techmap/main/jobs/product.csv
https://raw.githubusercontent.com/mluggy/techmap/main/jobs/business.csv
https://raw.githubusercontent.com/mluggy/techmap/main/jobs/devops.csv
https://raw.githubusercontent.com/mluggy/techmap/main/jobs/security.csv
```

**Filter logic:**
```python
import urllib.request, csv, io
from datetime import datetime, timedelta

BASE = "https://raw.githubusercontent.com/mluggy/techmap/main/jobs/"
EXEC_FILES = ["software.csv", "product.csv", "business.csv", "devops.csv", "security.csv"]
EXEC_KEYWORDS = ["vp r&d", "vp engineering", "cto", "chief tech", "head of r&d",
                 "head of engineering", "vp product", "director of product",
                 "director r&d", "vp devops", "head of platform", "director of r&d",
                 "head of product", "vp of r&d", "vp of engineering"]
SIZE_FILTER = {"m", "l", "xl"}  # medium, large, extra-large only
CUTOFF = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")

leads = []
for fname in EXEC_FILES:
    url = BASE + fname
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        content = r.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        title_lower = row.get("title", "").lower()
        level = row.get("level", "")
        size = row.get("size", "")
        updated = row.get("updated", "")
        if level == "Executive" and size in SIZE_FILTER and updated >= CUTOFF:
            if any(k in title_lower for k in EXEC_KEYWORDS):
                leads.append(row)
                print(f"LEAD: [{size}] {row['title']} @ {row['company']} "
                      f"({row['city']}) updated:{updated} url:{row['url'][:80]}")

print(f"\nTotal executive leads from techmap: {len(leads)}")
```

**Key notes on techmap data:**
- `updated` field = date the listing was last verified active (discard if > 14 days old per R3)
- `url` field links directly to the ATS job posting
- `size`: xs=<10, s=10-50, m=50-200, l=200-1000, xl=1000+ — use m/l/xl only
- `level == "Executive"` is the reliable filter for VP/Director/CTO titles
- Company name = None → fetch the URL to get company name from ATS page

### Primary Source B — LinkedIn Jobs (for CTO/VP R&D not on techmap)

Per R24/R26: CTO and VP R&D roles at well-backed companies often appear on LinkedIn but not standard ATS boards.

Search queries (in order):
1. `"VP R&D" Israel Tel Aviv` — filter: last 30 days
2. `"VP Engineering" Israel Tel Aviv` — filter: last 30 days
3. `"CTO" Israel "Tel Aviv"` — filter: last 30 days
4. `"Head of R&D" Israel` — filter: last 30 days

Use WebSearch with `site:linkedin.com/jobs` and extract job IDs from results.

### Secondary Sources (if techmap + LinkedIn yield nothing qualifying)

**Greenhouse API scan:**
```python
import urllib.request, json

GREENHOUSE_SLUGS = [
    "monday", "fiverr", "riskified", "jfrog", "yotpo", "tipalti",
    "gong", "bigid", "aquasecurity", "forter", "similarweb", "armis",
    "axonius", "catonetworks", "wiz", "snyk", "checkmarx", "cybereason",
    "guardicore", "illumio", "orca", "lacework", "sysdig", "torq",
    "coralogix", "logz", "datagen", "lightricks", "via", "moovit",
    "ironvest", "payoneer", "papaya", "rapyd", "melio", "tipalti",
    "lemonade", "hippo", "next-insurance", "kape", "expressvpn",
    "ironnet", "sentinelone", "cyberark", "varonis", "radware"
]
EXEC_TITLE_KEYWORDS = ["vp r&d", "vp engineering", "cto", "head of r&d",
                       "director r&d", "vp product", "director of product"]

for slug in GREENHOUSE_SLUGS:
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            jobs = json.loads(r.read()).get("jobs", [])
        for j in jobs:
            title = j.get("title", "").lower()
            location = str(j.get("location", {}).get("name", "")).lower()
            if (any(k in title for k in EXEC_TITLE_KEYWORDS) and
                    ("israel" in location or "tel aviv" in location)):
                print(f"GH HIT: {slug} | {j['title']} | {location} | ID:{j['id']}")
    except Exception:
        pass
```

**Direct career pages (R23):** For companies whose Greenhouse/Lever slug is 404, check: `careers.[company].com`, `jobs.[company].com`, `makers.[company].com`

**Other secondary sources:**
- Built In Israel: `https://builtin.com/jobs/mena/israel` — filter by Director/VP level
- Wellfound / AngelList: `https://wellfound.com/role/l/vp-of-engineering/israel`
- VC portfolio boards: TechAviv, Viola Ventures, Sequoia Israel, Bessemer Israel, Lightspeed Israel

---

## STEP 2 — PRE-FLIGHT VALIDATION

Apply rules in order. First candidate to pass ALL = today's job. One fail = discard, next.

| Rule | Check | Method |
|---|---|---|
| R1 | Job actively accepting applications | Fetch URL; grep for "no longer accepting", "closed", "filled", "not accepting". Redirect to search page = closed. |
| R2 | Not already in pipeline | grep -i "[company]" local tracker first; Sheets secondary. If match → FAIL. |
| R3 | Posted ≤ 30 days ago | Check listing date. For techmap: `updated` within 14 days. For custom boards: og:updated_time metadata. |
| R4 | Israel or remote/EMEA | Check location field. |
| R5 | People management / exec title | VP/CTO/Director/Head-of with direct reports or R&D org ownership. |
| R6 | ≥ 3 of the candidate's 5 priorities | People mgmt, WLB, new tech, significance, GAMPA-tier. |
| R14 | Estimated ATS ≥ 65% | Quick keyword scan of JD vs profile before committing to full CV build. |
| R25 | Company size qualifier | Series B+ ≥ $100M raised, OR publicly traded, OR GAMPA-tier. |

**Platform-specific open-status methods:**
- Greenhouse: `boards-api.greenhouse.io/v1/boards/{slug}/jobs` — job present = open (R8)
- Workable: Check `apply.workable.com/{slug}` — active page with job content = open
- Comeet: Fetch URL directly — redirect to company board with no job = closed (R26)
- SmartRecruiters: Google-search the exact job URL — if indexed = open (R27)
- Custom boards: Check og:updated_time in page source — if > 30 days = fail R3 (R25)
- LinkedIn: Check "No longer accepting applications" banner

---

## STEP 3 — JOB INTELLIGENCE REPORT

After a job passes all pre-flight rules, produce this report:

```
╔══════════════════════════════════════════════════════════════╗
║  JOB INTELLIGENCE REPORT                                     ║
╠══════════════════════════════════════════════════════════════╣
║  Role:           [Title] at [Company]                        ║
║  Source:         techmap / LinkedIn / Greenhouse / etc.      ║
║  Platform:       [ATS name]                                  ║
║  Apply URL:      [direct link]                               ║
║  Posted:         [X days ago / updated YYYY-MM-DD]           ║
║  Status:         VERIFIED OPEN (method + date)               ║
╠══════════════════════════════════════════════════════════════╣
║  COMPANY INTELLIGENCE                                        ║
║  Funding:        [$XM raised / publicly traded / GAMPA]      ║
║  Employees:      [size]                                      ║
║  Tech stack:     [what they build]                           ║
╠══════════════════════════════════════════════════════════════╣
║  APPLICANT DATA                                              ║
║  Applicants:     [count or "unknown - JS-rendered"]          ║
║  Easy Apply:     Yes/No                                      ║
║  Repost:         Yes/No/Unknown                              ║
╠══════════════════════════════════════════════════════════════╣
║  PRE-FLIGHT CHECKS                                           ║
║  R1 Open status:    PASS / FAIL                              ║
║  R2 Not in tracker: PASS / FAIL                              ║
║  R3 <= 30 days:     PASS / FAIL                              ║
║  R4 Israel/Remote:  PASS / FAIL                              ║
║  R5 People mgmt:    PASS / FAIL                              ║
║  R6 3+ priorities:  PASS / FAIL                              ║
║  R14 ATS >= 65%:    PASS / FAIL                              ║
║  R25 Company size:  PASS / FAIL                              ║
╠══════════════════════════════════════════════════════════════╣
║  STRATEGIC READ                                              ║
║  [2-3 sentence honest assessment of fit and risk]            ║
╠══════════════════════════════════════════════════════════════╣
║  REFERRAL PLAY                                               ║
║  [Who to contact on LinkedIn + suggested message text]       ║
╚══════════════════════════════════════════════════════════════╝
```

---

## STEP 3.5 — WRITE LEARNINGS ENTRY NOW (before building documents)

Per R29: Write the partial self-learning entry to the local DAILY_CV_LEARNINGS.md NOW, before any document generation. Use Python `open(path, 'a')` to append.

Write this block immediately:

```markdown
### Run YYYY-MM-DD (Run N) — [Company]

- Job selected: [Title] at [Company]
- URL: [apply URL]
- Source: techmap / LinkedIn / Greenhouse / etc.
- Pre-flight checks: ALL PASSED (R1: [method]; R2: not in tracker; R3: [X days];
  R4: [city]; R5: [why]; R6: [priorities matched]; R14: est. [X%]; R25: [qualifier])
- Jobs discarded before selection:
  - [Company]: [reason — which rule failed]
- ATS score: TBD — to be filled after CV generation
- Status: IN PROGRESS
```

After delivery, append to the same block:

```markdown
- ATS score: [X%] ([Y/Z keywords])
- Status: CV + CL delivered
  - <slug>_CV_[Company]_[YYYYMMDD].docx ([bytes], 1 page confirmed)
  - <slug>_CV_[Company]_[YYYYMMDD].pdf ([bytes], 1 page confirmed)
  - <slug>_CoverLetter_[Company]_[YYYYMMDD].docx ([bytes])
  - <slug>_CoverLetter_[Company]_[YYYYMMDD].pdf ([bytes])
- New lesson: [one sentence, or "None"]
- Rule added/updated: [Rn — description] or "None"
```

---

## STEP 4 — FETCH JD AND BUILD CV

### 4a — Fetch the Job Description

Try these methods in order until you have the full JD text:

1. Direct URL fetch (works for Greenhouse, Workable, most ATS)
2. Greenhouse API: `boards-api.greenhouse.io/v1/boards/{slug}/jobs/{id}?content=true`
3. Google cache: `cache:[url]`
4. Google search snippet + LinkedIn mirror + Glassdoor (for SmartRecruiters/JS-rendered per R27)
5. Reconstruct from: job title + company tech page + parallel open roles from same company

Never claim the JD is unavailable until all 5 methods are exhausted.

### 4b — Check Recruiter Name (R18)

Before writing the cover letter:
- grep -i "[company]" local tracker — check for recruiter name
- Attempt Google Sheets read (secondary) — recruiter name in rightmost filled column
- If recruiter name found → use "Dear [FirstName]," in cover letter salutation
- If not found → use "Dear Hiring Team, [Company],"

### 4c — Generate CV (python-docx — R19)

Use the bundled generators — they load `profile/PROFILE.json` and never hardcode any
person's facts:

```bash
cd skills/daily-cv/scripts
python generate_cv.py  --company "[Company]" --role "[Role]" --run-date [YYYYMMDD] \
       --summary "[JD-tuned 2-sentence summary]" --output-dir "[output folder]"
python generate_pdf.py --company "[Company]" --role "[Role]" --run-date [YYYYMMDD] \
       --summary "[same summary]" --output-dir "[output folder]"
```

The name, contacts, experience, education, and volunteering all come from the profile.
Tune only the per-run `--summary` / `--competencies` to the JD's keywords. Never generate
DOCX by hand.

**Document sections (in order):**
1. Name block — `profile.identity.display_name` (large, bold, centered)
2. Contact line — phone | email | linkedin | location | optional clearance (centered)
3. Summary — 2 sentences max, role-title keyword in sentence 1, 3 JD keywords woven in
4. Core Competencies — single paragraph of 8-12 keywords, pipe-separated
5. Experience — reverse-chronological, ~4 roles max visible
6. Education — 2 lines max
7. Volunteering — 1 line

**Bullet count limits (R13 — anti-AI-fingerprint):**
- Current role: max 4 bullets
- Roles 2-3: max 3 bullets each
- Older roles: max 2 bullets
- Vary bullet length: at least one short (<12 words) and one long (>18 words) per role

**Banned content (blocking checks):**
- Zero emojis in any document (R12)
- Zero em-dashes (—) → use plain hyphen (-)
- Zero curly/smart quotes → use straight quotes
- Zero Tier 1 banned words: "spearheaded", "leveraged", "synergy", "passionate", "results-driven", "dynamic", "innovative", "seasoned", "guru", "ninja", "wizard", "rock star", "thought leader", "visionary", "transformational", "game-changer"
- Zero first-person pronouns (I, me, my, we, our)
- Zero fabricated metrics — all numbers from `profile.key_metrics` only

**Anti-fabrication rules (always apply):**
- Honour the per-person guardrails in `profile.anti_fabrication_notes` (exact titles, exact
  date ranges, careful framing of investments/clearances/parallel roles).
- Use the exact `display_name` and word order from the profile — verify the wrong order
  appears 0 times in generated files (R9).
- Every number must trace to `profile.key_metrics`. Missing experience is a gap, not a
  writing opportunity.

### 4d — PDF Generation and Validation

Prefer `generate_pdf.py` (reportlab) from Step 4c — it emits a clean, ATS-readable text
layer directly (R30). Only if you must convert an existing DOCX, LibreOffice headless is a
last-resort fallback (unreliable in containers):

```bash
# Last-resort DOCX -> PDF (prefer generate_pdf.py instead)
soffice --headless --convert-to pdf \
  <slug>_CV_[Company]_[YYYYMMDD].docx \
  --outdir "[your output folder]"

# Validate page count (R15)
pdfinfo <slug>_CV_[Company]_[YYYYMMDD].pdf | grep Pages

# If 2+ pages, reduce in this order (R15):
# 1. Shrink margins (try top/bottom 0.25")
# 2. Reduce section/role spacing (spaceAfter=0)
# 3. Trim summary by one sentence
# 4. Reduce nameBlock font from 44pt to 40pt
```

Page count check is MANDATORY before delivery. CV must be exactly 1 page.

### 4e — ATS Keyword Verification (R11, R21, R28)

```python
import pdfplumber, re

def ats_score(pdf_path, keywords):
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = " ".join(p.extract_text() or "" for p in pdf.pages)
    # R28 — normalize whitespace before matching
    normalized = re.sub(r'\s+', ' ', raw_text.lower())
    hits, misses = [], []
    for kw in keywords:
        if kw.lower() in normalized:
            hits.append(kw)
        else:
            misses.append(kw)
    pct = round(len(hits) / len(keywords) * 100)
    return hits, misses, pct

hits, misses, score = ats_score("<slug>_CV_[Company]_[YYYYMMDD].pdf", required_keywords)
print(f"ATS Score: {score}% ({len(hits)}/{len(required_keywords)})")
print(f"Misses: {misses}")
```

After getting misses:
- Check noun/verb form (R21): "mentoring" vs "mentorship" — patch to exact JD form
- Add missing keyword to summary or competencies if not fabrication
- Re-run ATS check on the regenerated PDF (not the source text)
- Target: >= 85% for required keywords

**Full ATS report format (R11):**
For every keyword in the JD: HIT or MISS, which CV section it appears in.
For every miss: state whether added, and why not if skipped (anti-fabrication).

### 4f — Final Validation Checklist

```
[ ] Page count: exactly 1
[ ] Name: matches `profile.identity.display_name` exactly — grep confirms the wrong word order = 0 hits
[ ] No emojis in document content
[ ] No em-dashes in document
[ ] No curly/smart quotes
[ ] No Tier 1 banned words
[ ] No first-person pronouns
[ ] No fabricated metrics
[ ] Bullet counts: 4/3/3/2 pattern
[ ] ATS score: >= 85%
[ ] PDF page count confirmed via pdfinfo
[ ] Cover letter: 1 page, personalized salutation
```

---

## STEP 5 — GENERATE COVER LETTER

**Structure:**
1. Header: same as CV (name, contact)
2. Salutation: "Dear [RecruiterFirstName]," OR "Dear Hiring Team, [Company],"
3. Para 1 (hook): Why this company, why now. Reference one specific company fact.
4. Para 2 (match): 2-3 most relevant achievements from profile, mapped to JD requirements.
5. Para 3 (close): Availability, enthusiasm, call to action.
6. Sign-off: "Warm regards, / <profile.identity.display_name>"

**Constraints:** 1 page, no emojis, no banned words, no fabricated claims.

Convert to PDF and validate page count (same process as CV).

---

## STEP 6 — INTERVIEW PREP

Add a section to your local interview-prep tracker (path from `SOURCES.md`):

**Sections to include:**
- Company context briefing (5-7 bullet facts about the company + strategic moment)
- Interview format (rounds, what each tests — from Glassdoor/Blind/company blog)
- Round-by-round scripted answers (3 questions per round, STAR format where applicable)
  - Answers draw exclusively from the candidate's verified experience (the profile)
  - Use real metrics from `profile.key_metrics` only
- STAR stories mapped to JD requirements
- Skills gap table: skill vs. the candidate's level vs. gap vs. specific free course/resource

---

## STEP 7 — UPDATE JOB TRACKER

Append a new row to the pipeline table in your local tracker (path from `SOURCES.md`):

```markdown
| [N] | [YYYY-MM-DD] | **[Company]** | [Role Title] | To Apply |
| [stars] | [Apply URL] | [ATS%] | [2-line summary] |
```

Update the `Last updated:` date at the top of the tracker file.

Also append the full intelligence report + ATS report + interview prep below the table.

**Note on Google Sheets:** The Sheets tracker is for human reference. The agent does NOT update Sheets directly — user mirrors the markdown row to Sheets manually.

---

## STEP 8 — COMPLETE LEARNINGS ENTRY (per R29)

Append the completion block to the `### Run YYYY-MM-DD` entry written in Step 3.5.

If a new failure pattern emerged, ALSO add:
- A new entry to FAILURE PATTERNS section
- A new row to SELECTION RULES table (increment Rn)
- Append to the Runs Log table

---

## OUTPUT SUMMARY FORMAT

End every run with this block in chat:

```
## Daily CV Run — [Date]

Apply here: [Company — Role Title](URL)

Files:
- <slug>_CV_[Company]_[YYYYMMDD].docx
- <slug>_CV_[Company]_[YYYYMMDD].pdf
- <slug>_CoverLetter_[Company]_[YYYYMMDD].docx
- <slug>_CoverLetter_[Company]_[YYYYMMDD].pdf
- All saved to: [your output folder from SOURCES.md]

Pre-flight: All [N] checks passed
ATS Score:  [X%]
Source:     techmap / LinkedIn / [platform]
Learning:   [One sentence — what was learned or confirmed today]
```

---

## Anti-Fabrication Rules

- `profile/PROFILE.json` is the only source for candidate facts.
- Never add unsupported metrics, titles, dates, employers, technologies, credentials, or achievements.
- Never alter a job requirement into a candidate achievement.
- Mark unsupported requirements as gaps.
- Cite public company/job sources in the intelligence report.
- Discard jobs that cannot be verified as active and fileable.
- Confirm every number against `profile.key_metrics`.
- Honour each per-person guardrail in `profile.anti_fabrication_notes`.
- During INIT (see `INIT.md`), confirm every extracted fact with the user before writing it — never fabricate from LinkedIn/email/AI-chat sources.

---

## ANTI-FABRICATION NOTES (per-person)

Per-person guardrails live in **`profile.anti_fabrication_notes`** — exact titles, exact date
ranges, careful framing of investments/clearances, and the exact name word order. Keep them
there, not here, so the skill stays person-agnostic. Example shape (fictional):

| Fact | Correct Value |
|---|---|
| Exact title at <Company> | `<exact title>` (not the inflated variant) |
| Investment framing | `sourced $X investment commitment` — never "raised $X" |
| Clearance | state historical vs. active accurately, or omit |
| Name order | exact `display_name` — verify the wrong order appears 0 times |

---

## ACCUMULATED SELECTION RULES (R1-R29 here; R30-R31 in DAILY_CV_LEARNINGS.md)

Apply every rule to every candidate job before selection. One fail = discard. The learnings
log (`knowledge/DAILY_CV_LEARNINGS.md`) is canonical and may contain newer rules.

| # | Rule | Method |
|---|---|---|
| R1 | Job actively accepting applications | Fetch URL; grep for "no longer accepting", "closed", "filled", "not accepting". Redirect to search page = closed. |
| R2 | Not already in pipeline | grep -i "[company]" local tracker first; Sheets secondary. If match → FAIL. |
| R3 | Posted <= 30 days ago | Check listing date. For techmap: `updated` within 14 days. For custom boards: og:updated_time metadata. |
| R4 | Israel or remote/EMEA | Check location field. |
| R5 | People management / exec title | VP/CTO/Director/Head-of with direct reports or R&D org ownership. |
| R6 | >= 3 of the candidate's 5 priorities | People mgmt, WLB, new tech, significance, GAMPA-tier. |
| R7 | Flag Easy Apply | Note in report — OK to proceed, flag low selectivity. |
| R8 | Greenhouse open-status via API | `boards-api.greenhouse.io/v1/boards/{slug}/jobs` — job present = open. |
| R9 | Name = `profile.identity.display_name` | Exact word order always. grep for the wrong order = 0 hits in generated files. |
| R10 | Profile from `PROFILE.json` only | Never use memory or a stray backup as the profile source. |
| R11 | Full ATS keyword breakdown mandatory | Every keyword: hit/miss/section/action taken. |
| R12 | No emojis in documents | Blocking check — search DOCX/PDF content for emoji codepoints. |
| R13 | Bullet count limits | 4 bullets (current role), 3/3 (roles 2-3), 2 (older). Vary short (<12 words) and long (>18 words). |
| R14 | Estimated ATS >= 65% before committing | Quick keyword scan before full CV build. |
| R15 | PDF page count = 1 via pdfinfo | Reduce: margins -> spacing -> summary -> font size. Mandatory before delivery. |
| R16 | Apply link is always first output | Before ATS reports, before files, before everything. |
| R17 | Local markdown = primary R2 source | Google Sheets is secondary (may exceed MCP limit). |
| R18 | Recruiter name personalization | "Dear [FirstName]," if name found in tracker. Otherwise "Dear Hiring Team, [Company]," |
| R19 | Python for DOCX generation | Use python-docx — avoids multi-byte heredoc encoding errors. |
| R20 | Check brand slug AND parent slug | For Greenhouse: try both (e.g., expressvpn and kape). |
| R21 | Match exact keyword form from JD | "mentoring" != "mentorship" for ATS parsers — use the JD's exact form. |
| R22 | Corrections propagate everywhere | DOCX + PDF + learnings log — all four files updated when a fix is made. |
| R23 | Custom board URL patterns | Try `careers.[co].com`, `jobs.[co].com`, `makers.[co].com` when ATS slug 404s. |
| R24 | CTO/VP R&D not on standard ATS | Lead with techmap + LinkedIn; ATS board scan is secondary. |
| R25 | Company size qualifier | Series B+ >= $100M raised, OR publicly traded, OR GAMPA-tier. Also: check og:updated_time for custom boards. |
| R26 | Comeet URLs are stale in Google index | Fetch directly — if redirects to company board with no job = closed. |
| R27 | SmartRecruiters = JS-rendered | Google index presence = R1 pass. Reconstruct JD from 4 sources. |
| R28 | Normalize PDF whitespace for ATS | `re.sub(r'\s+', ' ', text.lower())` before keyword matching. |
| R29 | Write learnings at Step 3.5 | Before CV build. Append ATS/sizes after delivery. |

---

## KEY METRICS REFERENCE (anti-fabrication ground truth)

**Your real metrics live in `profile.key_metrics`.** Every number used in a CV or cover letter
MUST come from that list. Do not keep a second copy of real numbers in this file.

---

## TECHMAP QUICK REFERENCE

| File | Best For | Filter |
|---|---|---|
| `software.csv` | VP R&D, VP Engineering, Head of R&D | `level=Executive`, `size in {m,l,xl}` |
| `product.csv` | VP Product, Director of Product | `level=Executive`, `size in {m,l,xl}` |
| `business.csv` | Head of Data, Director BI/AI | `level=Executive`, `size in {m,l,xl}` |
| `devops.csv` | Head of Platform, VP DevOps | `level=Executive`, `size in {m,l,xl}` |
| `security.csv` | Head of Security R&D, CISO (if R&D scope) | `level=Executive`, `size in {m,l,xl}` |

Raw URL pattern: `https://raw.githubusercontent.com/mluggy/techmap/main/jobs/{file}.csv`

Updated: Daily (check `updated` field — discard if > 14 days old)

Source coverage: Comeet, Greenhouse, Workable, LinkedIn, direct career pages — all Israeli tech.

Company name = None: Fetch the `url` field to extract company name from the ATS page.

---

_Skill version: 2.0 | Last updated: 2026-05-13 | Rules: R1-R29 | Sources: techmap + LinkedIn + Greenhouse API + Workable + Comeet + custom boards_
