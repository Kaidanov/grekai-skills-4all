# Scheduled Routine Setup — daily-cv-agent (v2)

## Instructions

Open a scheduling-capable AI assistant session and paste the message below.
Schedule: every weekday morning in your timezone. First-time users must complete `INIT.md`
(build `profile/PROFILE.json`) before scheduling.

---

## Message to paste:

```
Run the daily job search using live config from GitHub.

## Step 0 — Self-Learning Bootstrap (ALWAYS FIRST)

Read these files in order before doing anything else:

1. Learnings log (read FIRST — contains all R1-R29 rules and runs log):
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/knowledge/DAILY_CV_LEARNINGS.md

2. Sources config:
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/config/SOURCES.md

3. Job criteria:
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/config/JOB_CRITERIA.md

4. Watchlist:
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/config/WATCHLIST.md

5. Full skill spec:
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/SKILL.md

6. Candidate profile (read-only — ONLY source for candidate facts):
   skills/daily-cv/profile/PROFILE.json   (fallback: PROFILE.example.json)

7. Outreach templates:
   https://raw.githubusercontent.com/Kaidanov/grekai-skills/main/skills/daily-cv/knowledge/Startup_Outreach_Approach.md

8. Local job tracker (R2 primary — check for duplicates):
   <YOUR_LOCAL_TRACKER_PATH>

9. Local learnings log (R29 — write entries here, not only to GitHub):
   <YOUR_LOCAL_LEARNINGS_PATH>

## Step 1 — Apply ALL Accumulated Rules
Apply every rule from DAILY_CV_LEARNINGS.md. One fail = discard and try next candidate.
Check the RUNS LOG — never repeat a company+role already listed.

## Step 2 — Find Best Job (techmap-first)

Priority order:
1. Download all 5 techmap CSVs (software, product, business, devops, security).
   Base URL: https://raw.githubusercontent.com/mluggy/techmap/main/jobs/
   Filter: level=Executive, size in {m,l,xl}, updated within 14 days, title matches exec keywords.
2. LinkedIn search for "VP R&D" / "VP Engineering" / "CTO" / "Head of R&D" Israel — last 30 days.
3. Greenhouse API scan of Israel company slugs.
4. HIGH priority watchlist company career pages.
5. MEDIUM priority sources.
6. Proactive outreach if nothing qualifies.

Before selecting any job, verify ALL of R1, R2, R3, R4, R5, R6, R14, R25.

## Step 3 — Job Intelligence Report + Write Partial Learnings Entry (Step 3.5)

After a job passes all checks:
1. Produce the Job Intelligence Report (see SKILL.md format).
2. Write partial entry to local DAILY_CV_LEARNINGS.md NOW (before CV generation) using Python append.

## Step 4 — Generate CV

File naming: <slug>_CV_[Company]_[YYYYMMDD].docx  (slug from profile.identity.filename_slug)
Output folder: <YOUR_OUTPUT_FOLDER>

- Use the bundled generators (generate_cv.py / generate_pdf.py) — they load the profile (R19).
- 1-page target. Validate with pdfinfo after PDF conversion (R15).
- Apply bullet count limits: 4/3/3/2 pattern (R13).
- No emojis, no em-dashes, no banned words, no fabricated metrics (R12).
- Name: profile.identity.display_name — grep for the wrong word order = 0 (R9).
- All facts from profile/PROFILE.json only (R10).
- ATS keyword check >= 85% on required keywords (R11, R21, R28).

## Step 5 — Generate Cover Letter

File naming: <slug>_CoverLetter_[Company]_[YYYYMMDD].docx
- 1 page. Personalized salutation if recruiter name found in tracker (R18).
- No emojis, no banned words, no fabricated claims.
- Convert to PDF and validate page count.

## Step 6 — Interview Prep

Add to local <your local interview-prep tracker>:
- Company context briefing
- Round-by-round Q&A with STAR answers from verified experience only
- Skills gap table

## Step 7 — Update Local Job Tracker

Append new row to pipeline table in <your local interview-prep tracker>.
Update Last updated: date.

## Step 8 — Complete Learnings Entry

Append ATS score, file sizes, new lesson to the Step 3.5 entry.
If new failure pattern → add to FAILURE PATTERNS and increment rules.

## Final Output (order is mandatory — R16)

1. Apply here: [Company — Role Title](URL)    <- FIRST, always
2. ATS score summary
3. File paths (all 4 files)
4. Pre-flight summary
5. One-sentence learning

## Anti-Fabrication
Only profile/PROFILE.json is the source for candidate facts.
All numbers must trace to profile.key_metrics.
Never invent facts. Mark gaps as gaps.
```

---

## After setup

To update watchlist, job criteria, rules, or sources — edit the files under `skills/daily-cv/config/` and push. Changes take effect on the next run when the skill reads the raw GitHub URLs.

To add a new learned rule — append to `skills/daily-cv/knowledge/DAILY_CV_LEARNINGS.md` and push.

No routine recreation is needed unless the schedule itself changes.
