# Daily CV — Learning Log (v2)
# Self-Learning Job Search Agent

This file is append-only. The `daily-cv` skill reads it before EVERY run (Step 0) and appends durable lessons after EVERY run (Step 8). Keep it free of personal data — it is committed. Personal facts belong only in the gitignored `profile/PROFILE.json`.

**CRITICAL:** Reading this file before searching is non-negotiable. Without it, rules are violated and companies are re-submitted.

---

## How To Use This File

Before selecting any job:

1. Read all solved failure patterns.
2. Apply every rule in the Selection Rules table to every candidate job.
3. Check the Runs Log — every company+role ever selected — never repeat.

After the run:
1. Append a new `### Run YYYY-MM-DD (Run N)` block.
2. If a new failure pattern emerged, add it to Solved Failure Patterns AND add a new Rn rule.

---

## Solved Failure Patterns

### Failure: Closed Job Selected

**What happened:** A job was selected after the apply flow had closed.

**Root cause:** The workflow trusted a search result without validating the live job page and apply action.

**Rule added (R1):** Before selecting any job, fetch the canonical job URL and confirm it is actively accepting applications. Reject pages that show closed, expired, filled, no longer accepting, or that redirect to a generic search page.

### Failure: Duplicate Job Selected

**What happened:** A job already tracked by the user was selected again.

**Root cause:** The workflow did not read the configured tracker before selection.

**Rule added (R2):** Read the local tracker first (grep), Sheets secondary. Use `company + role title` as the duplicate key.

### Failure: Unsupported Resume Claim Added

**What happened:** A generated resume implied experience not present in the approved candidate profile.

**Root cause:** The workflow optimized keywords without enforcing source-of-truth boundaries.

**Rule added (R10):** Use only `profile/PROFILE.json` for candidate facts. Missing experience is a gap, not a writing opportunity.

### Failure: Wrong Name Order in Generated Document

**What happened:** A generated document used the wrong name word order.

**Root cause:** Model reordered the name to a different convention.

**Rule added (R9):** Name must always match `profile.identity.display_name` exactly. After generation, grep for the wrong word order — if found, fail and regenerate.

### Failure: 2-Page CV Generated

**What happened:** PDF output was 2 pages, not 1.

**Root cause:** Default margins and spacing filled the second page.

**Rule added (R15):** After PDF conversion, validate page count via `pdfinfo`. If 2+ pages, reduce in order: margins → spacing → summary → font size. Target: exactly 1 page.

### Failure: Stale Comeet URL Selected

**What happened:** A Comeet URL from Google index was selected, but the job was closed. Comeet redirected to company board with no job content.

**Root cause:** Google index shows stale Comeet URLs long after closure.

**Rule added (R26):** For Comeet URLs, always fetch directly. If the URL redirects to a company board with no job content, the job is closed — fail R1.

### Failure: SmartRecruiters JD Not Fetchable

**What happened:** SmartRecruiters job pages are JS-rendered, so WebFetch returns empty content.

**Root cause:** SmartRecruiters uses heavy client-side rendering.

**Rule added (R27):** For SmartRecruiters, verify R1 via Google index presence (if the exact URL appears in Google results with a snippet, the job is likely open). Reconstruct JD from: Google snippet + LinkedIn mirror + Glassdoor + company tech page.

### Failure: ATS Keyword Missed Due to Whitespace in PDF

**What happened:** Keyword was present in the DOCX but not matched in ATS scan of the PDF because PDF extraction introduced extra whitespace.

**Root cause:** pdfplumber extracts text with line-break whitespace that breaks multi-word keyword matching.

**Rule added (R28):** Always normalize whitespace before ATS matching: `re.sub(r'\s+', ' ', text.lower())`.

### Failure: DOCX Encoding Error with JS Heredoc

**What happened:** JS heredoc-generated DOCX file had encoding errors in special characters (smart quotes, em-dashes).

**Root cause:** Bash heredoc encoding is fragile for multi-byte characters.

**Rule added (R19):** Use python-docx (Python) for DOCX generation — it avoids heredoc encoding issues entirely.

### Failure: Verb/Noun Form Keyword Miss

**What happened:** CV used "mentorship" but JD required "mentoring" — ATS flagged as a miss.

**Root cause:** ATS parsers do not always stem keywords.

**Rule added (R21):** Check both noun and verb forms of every keyword. Match the exact form used in the JD.

### Failure: Wrong Greenhouse Slug Used

**What happened:** Searched `expressvpn` slug on Greenhouse but the parent company `kape` holds the actual board.

**Root cause:** Some brands use their parent company's Greenhouse account.

**Rule added (R20):** Always check both brand slug and parent slug on Greenhouse.

### Failure: Learnings Entry Written After CV — Lost if Process Interrupted

**What happened:** Learning entry was only written at the end of the run. If CV generation failed, no record was kept of jobs evaluated.

**Root cause:** Learnings written too late in the workflow.

**Rule added (R29):** Write the partial learnings entry at Step 3.5 — before CV generation — using `open(path, 'a')`. Append ATS score and file sizes after delivery.

### Failure: CTO/VP R&D Role Not Found on ATS Boards

**What happened:** Top executive roles for VP R&D / CTO were not appearing on Greenhouse or Comeet scans.

**Root cause:** These roles are often posted only on LinkedIn or company career pages, not ATS boards.

**Rule added (R24):** Lead job search with techmap + LinkedIn for CTO/VP R&D roles. ATS board scan is a secondary fallback.

### Failure: Fabricated Company Funding Claims

**What happened:** CV or cover letter claimed a company had "raised $150M" without verification.

**Root cause:** Model inferred funding from company size without checking.

**Rule added (R25 qualifier check):** Only claim funding stage when it can be verified from public sources (Crunchbase, TechCrunch, company press release). If unverified, do not state the amount — use "well-funded" or "publicly traded" as appropriate.

### Failure: Old Posting Selected via Custom Company Career Page

**What happened:** A job on a company's custom career page had no visible posting date. og:updated_time metadata showed it was 45 days old — failed R3.

**Root cause:** Custom career pages often don't show a visible posting date.

**Rule added (R25 — custom boards):** For custom career pages without a visible date, check `og:updated_time` in the HTML source. If > 30 days from today, fail R3 and discard.

### Failure: PDF Toolchain Fails or Garbles Text in Headless/Container Environments

**What happened:** Multiple runs hit PDF-generation failures: LibreOffice headless (`soffice --convert-to`) failed silently (exit 0, no output) or crashed (SIGABRT / "source file could not be loaded"); fpdf2 with `set_xy()` positional layout produced scrambled text that `pdfplumber` could not reassemble, causing real ATS keywords to read as MISS.

**Root cause:** Headless LibreOffice is unreliable in cloud/CI containers; fpdf2 positional cells emit non-sequential character streams in the PDF content layer.

**Rule added (R30):** For PDF generation prefer, in order, **weasyprint** (HTML-to-PDF) or **reportlab** (flowables) — both emit clean, sequentially-encoded text layers that `pdfplumber`/`pdftotext` extract correctly. Do NOT rely on LibreOffice headless or fpdf2 positional layout. (Last-resort fallback seen in the field: Playwright/Chromium headless HTML-to-PDF.) Note: CSS `letter-spacing` on headings makes `pdftotext` emit spaced letters (e.g. `p r o f e s s i o n a l`) — strip these before pronoun/keyword regex checks.

### Failure: Comeet Job Pages Return 403 to All Bots

**What happened:** Comeet job URLs return HTTP 403 for every automated fetch (with or without UTM params), so R1 (open-status) could not be confirmed by direct fetch. Time was wasted retrying.

**Root cause:** Comeet has blanket bot protection — 403 is bot-blocking, not closure.

**Rule added (R31):** For Comeet-listed jobs, treat the **techmap `updated` timestamp** as the R1 validator: updated within 14 days = PASS R1. Do not attempt direct Comeet page fetch. (A 403 is a bot block, not a closed job — distinct from R26's redirect-to-board = closed.)

---

## Selection Rules (R1–R31)

Apply every rule to every candidate job. One fail = discard, next candidate.

| # | Rule | How to Check |
|---|---|---|
| R1 | Job actively accepting applications | Fetch URL; grep for "no longer accepting", "closed", "filled", "not accepting". Redirect to search page = closed. |
| R2 | Not already in pipeline | grep -i "[company]" local tracker first; Sheets secondary. If match → FAIL. |
| R3 | Posted ≤ 30 days ago | Check listing date. For techmap: `updated` within 14 days. For custom boards: og:updated_time metadata. |
| R4 | Israel or remote/EMEA | Check location field. |
| R5 | People management / exec title | VP/CTO/Director/Head-of with direct reports or R&D org ownership. |
| R6 | ≥ 3 of the candidate's 5 priorities | People mgmt, WLB, new tech, significance, GAMPA-tier. |
| R7 | Flag Easy Apply | Note in report — OK to proceed, flag low selectivity. |
| R8 | Greenhouse open-status via API | `boards-api.greenhouse.io/v1/boards/{slug}/jobs` — job present = open. |
| R9 | Name = `profile.identity.display_name` | Exact word order always. grep for the wrong order = 0 hits in generated files. |
| R10 | Profile from `PROFILE.json` only | Never use memory or a stray backup as the profile source. |
| R11 | Full ATS keyword breakdown mandatory | Every keyword: hit/miss/section/action taken. |
| R12 | No emojis in documents | Blocking check — search DOCX/PDF content for emoji codepoints. |
| R13 | Bullet count limits | 4 bullets (current role), 3/3 (roles 2-3), 2 (older). Vary short (<12 words) and long (>18 words). |
| R14 | Estimated ATS ≥ 65% before committing | Quick keyword scan before full CV build. |
| R15 | PDF page count = 1 via pdfinfo | Reduce: margins → spacing → summary → font size. Mandatory before delivery. |
| R16 | Apply link is always first output | Before ATS reports, before files, before everything. |
| R17 | Local markdown = primary R2 source | Google Sheets is secondary (may exceed MCP limit). |
| R18 | Recruiter name personalization | "Dear [FirstName]," if name found in tracker. Otherwise "Dear Hiring Team, [Company]," |
| R19 | Python for DOCX generation | Use python-docx — avoids multi-byte heredoc encoding errors. |
| R20 | Check brand slug AND parent slug | For Greenhouse: try both (e.g., expressvpn and kape). |
| R21 | Match exact keyword form from JD | "mentoring" ≠ "mentorship" for ATS parsers — use the JD's exact form. |
| R22 | Corrections propagate everywhere | DOCX + PDF + learnings log — all four files updated when a fix is made. |
| R23 | Custom board URL patterns | Try `careers.[co].com`, `jobs.[co].com`, `makers.[co].com` when ATS slug 404s. |
| R24 | CTO/VP R&D not on standard ATS | Lead with techmap + LinkedIn; ATS scan is secondary. |
| R25 | Company size qualifier | Series B+ ≥ $100M raised, OR publicly traded, OR GAMPA-tier. Also: check og:updated_time for custom boards. |
| R26 | Comeet URLs are stale in Google index | Fetch directly — if redirects to company board with no job = closed. |
| R27 | SmartRecruiters = JS-rendered | Google index presence = R1 pass. Reconstruct JD from 4 sources. |
| R28 | Normalize PDF whitespace for ATS | `re.sub(r'\s+', ' ', text.lower())` before keyword matching. |
| R29 | Write learnings at Step 3.5 | Before CV build. Append ATS/sizes after delivery. |
| R30 | Use weasyprint/reportlab for PDF | Avoid LibreOffice headless (silent fail/SIGABRT) and fpdf2 set_xy (garbled pdfplumber extraction). Strip CSS letter-spacing artifacts before ATS text checks. |
| R31 | Comeet 403 = bot block, not closed | Use techmap `updated` timestamp as R1 validator (≤14 days = open). Do not direct-fetch Comeet. |

---

## GAMPA-Tier Quick Reference

Google, Apple, Microsoft, Amazon, Meta, Palo Alto Networks, Check Point, CrowdStrike, Akamai, Wiz, NVIDIA, Mobileye.

These companies pass R25 automatically. Always check for open exec roles even when their Greenhouse/LinkedIn listings don't surface in broad searches.

---

## Banned Content (blocking — fail generation if found)

- Emojis (any) in document text (R12)
- Em-dashes (—) → use plain hyphen (-)
- Curly/smart quotes → use straight quotes
- Tier 1 banned words: "spearheaded", "leveraged", "synergy", "passionate", "results-driven", "dynamic", "innovative", "seasoned", "guru", "ninja", "wizard", "rock star", "thought leader", "visionary", "transformational", "game-changer"
- First-person pronouns: I, me, my, we, our
- Fabricated metrics (any number not in `profile.key_metrics`)

---

## Runs Log

Every company+role ever selected. Never repeat. This log is committed — keep it to
company/role/date/status (no private notes). It starts empty; each run appends a row.

<!-- Append new entries below after each run in this format:
| YYYY-MM-DD | Company | Role Title | Status |
-->

| Date | Company | Role Title | Status |
|---|---|---|---|
| _(empty — populated as you run)_ | | | |

---

## Run Log Entries

Full run blocks are appended below. Template (fictional example shown):

```markdown
### Run YYYY-MM-DD (Run N) — [Company]

- Job selected: [Title] at [Company]
- URL: [apply URL]
- Source: techmap / LinkedIn / Greenhouse / etc.
- Pre-flight checks: ALL PASSED (R1: [method]; R2: not in tracker; R3: [X days];
  R4: [city]; R5: [why]; R6: [priorities matched]; R14: est. [X%]; R25: [qualifier])
- Jobs discarded before selection:
  - [Company]: [reason — which rule failed]
- ATS score: [X%] ([Y/Z keywords])
- Status: CV + CL delivered
  - <slug>_CV_[Company]_[YYYYMMDD].docx ([bytes], 1 page confirmed)
  - <slug>_CV_[Company]_[YYYYMMDD].pdf ([bytes], 1 page confirmed)
  - <slug>_CoverLetter_[Company]_[YYYYMMDD].docx ([bytes])
  - <slug>_CoverLetter_[Company]_[YYYYMMDD].pdf ([bytes])
- New lesson: [one sentence, or "None"]
- Rule added/updated: [Rn — description] or "None"
```

_No runs recorded yet. Durable lessons learned in the field (e.g. Comeet 403 handling) are
captured as Solved Failure Patterns and rules above, not as run history here._
