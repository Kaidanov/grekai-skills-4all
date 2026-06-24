# Job Criteria (v2)

> Edit this file to your own targets. The examples below use a senior tech-exec search; change
> the titles, geography, and priorities to fit you. Candidate facts come from
> `profile/PROFILE.json` — this file is only the *search* criteria.

---

## Mission Statement

The candidate wants to (edit to taste):
- Lead people (VP R&D / CTO / Head of R&D — top tech executive, NOT reporting to a CTO)
- Work-life balance (explicitly stated by employer preferred)
- Build or shape new tech (AI, GenAI, LLM, platform, cloud-native)
- Do significant work — top employers, meaningful impact, mission-driven orgs
- Interview ASAP

---

## Target Role Titles (Priority Order)

1. CTO / VP R&D / VP Engineering / Head of R&D — top tech executive at the site
2. Director R&D Program Management — only if org-spanning, not a single team
3. VP of Product / Director of Product — ONLY if no qualifying R&D/CTO roles found

**Hard disqualification:** Any role that reports to a CTO (the candidate IS the CTO-equivalent).

---

## Company Qualifier (R25)

A company must meet at least ONE of these criteria:

- Series B+ with ≥ $100M raised, OR
- Publicly traded, OR
- GAMPA-tier company

**GAMPA-tier** = Google, Apple, Microsoft, Amazon, Meta, Palo Alto Networks, Check Point, CrowdStrike, Akamai, Wiz, NVIDIA, Mobileye.

techmap size filter: `m` (50-200), `l` (200-1000), `xl` (1000+) — never `xs` or `s`.

---

## Geography

| Setting | Value |
|---|---|
| Primary country | Israel |
| Cities | Tel Aviv, Herzliya, Ramat Gan, Petah Tikva, Haifa, Raanana, Beer Sheva, Jerusalem, Bnei Brak |
| Remote | EMEA remote acceptable |
| Relocation | No |

---

## Work Mode Preferences

| Mode | Preference |
|---|---|
| Hybrid (2-3 days office) | Preferred |
| On-site (Israel) | Acceptable |
| Remote (EMEA) | Acceptable |
| Remote (US/Asia only) | Reject |

WLB signal: explicit WLB statement by employer is a positive signal in R6 scoring.

---

## Candidate's 5 Priorities (R6 — need ≥ 3 to qualify)

1. **People management** — leading engineering/R&D teams with direct reports
2. **Work-life balance** — employer explicitly mentions WLB, flexibility, or sustainable pace
3. **New technology** — AI, GenAI, LLM, platform engineering, cloud-native, ML, data
4. **Significance** — top employer, meaningful mission, societal impact, GAMPA-tier, or nationally known brand
5. **GAMPA-tier** — company is in the GAMPA list above

A job must match **at least 3 of 5** priorities to pass R6.

---

## Must-Have Rules (ALL must pass — one fail = discard)

| # | Rule | How Checked |
|---|---|---|
| R1 | Job actively accepting applications | Fetch URL; grep for "no longer accepting", "closed", "filled", "not accepting". Redirect to search page = closed. |
| R2 | Not already in pipeline | grep -i "[company]" local tracker first; Sheets secondary. If match → FAIL. |
| R3 | Posted ≤ 30 days ago | Check listing date. For techmap: `updated` within 14 days. For custom boards: check og:updated_time metadata. |
| R4 | Israel or remote/EMEA | Check location field. |
| R5 | People management / exec title | VP/CTO/Director/Head-of with direct reports or R&D org ownership. |
| R6 | ≥ 3 of the candidate's 5 priorities | Score each priority; need 3+ hits. |
| R14 | Estimated ATS ≥ 65% | Quick keyword scan of JD vs profile before committing to full CV build. |
| R25 | Company size qualifier | Series B+ ≥ $100M raised, OR publicly traded, OR GAMPA-tier. |

---

## Platform-Specific Open-Status Checks

| Platform | Method |
|---|---|
| Greenhouse | `boards-api.greenhouse.io/v1/boards/{slug}/jobs` — job present = open (R8) |
| Workable | Check `apply.workable.com/{slug}` — active page with job content = open |
| Comeet | Fetch URL directly — redirect to company board with no job = closed (R26) |
| SmartRecruiters | Google-search the exact job URL — if indexed = open (R27) |
| Custom boards | Check og:updated_time in page source — if > 30 days = fail R3 (R25) |
| LinkedIn | Check "No longer accepting applications" banner |

---

## Priority Order (when multiple qualifying jobs found)

1. GAMPA-tier with new executive role posted ≤ 7 days ago
2. Series B+ ≥ $100M + CTO/VP R&D + WLB signal + AI/GenAI tech
3. Publicly traded Israeli tech company + VP Engineering/Head of R&D
4. Strong techmap Executive hit at large (l/xl) company
5. Director R&D Program Management if org-spanning

---

## Seniority Floor

- Minimum: Director-level with direct reports (≥ 5 engineers) or org-spanning scope
- Preferred: VP or C-level equivalent
- Hard reject: Individual contributor, team lead without exec scope, PM below Director

---

## Nice-to-Have Signals

- Explicit WLB / work-life balance statement from employer
- AI/GenAI/LLM/platform focus in JD
- Recently announced product launch or funding round
- Recruiter name findable (enables personalized cover letter)
- Direct ATS apply link (not Easy Apply)
- Company in WATCHLIST.md HIGH priority

---

## Disqualification Rules (auto-reject)

| Condition | Reason |
|---|---|
| Role reports to a CTO | candidate IS the CTO-equivalent |
| Role is below Director or lacks direct reports | Seniority floor |
| Company < Series B or < $100M raised AND not public AND not GAMPA | R25 fail |
| Location outside Israel and not EMEA remote | R4 fail |
| Job closed / filled / redirected | R1 fail |
| Already in tracker | R2 fail |
| Posted > 30 days (techmap: updated > 14 days) | R3 fail |
| < 3 of 5 priorities match | R6 fail |
| Estimated ATS < 65% | R14 fail |
| Required resume claim not in approved profile source | Anti-fabrication |

---

## Application Preferences

- Prefer direct ATS apply forms (Greenhouse, Comeet, Workable, Lever, Ashby) over LinkedIn Easy Apply.
- If Easy Apply is the only path, flag low selectivity and higher applicant volume in the Job Intel report (R7).
- Personalize cover letter salutation with verified recruiter name (R18) — if not found, use "Dear Hiring Team, [Company],"
- Never use unverified personal names or internal contacts.

---

## Compensation Expectations

| Setting | Value |
|---|---|
| Currency | `<YOUR_CURRENCY>` |
| Target cash range | Market rate for the target seniority/region |
| Notes | Never include your current salary in any document. |

---

## KEY METRICS REFERENCE (Anti-Fabrication Ground Truth)

**Your real metrics live in `profile.key_metrics`** (in `profile/PROFILE.json`). That list is
the ground truth: every number used in a CV or cover letter MUST come from it. Do not maintain
a second copy of real numbers here.

Illustrative shape only (fictional — see `profile/PROFILE.example.json`):

| Metric | Value | Role/Context |
|---|---|---|
| Customers acquired | 9,000 | Example Company |
| Team managed (max) | 12 people, 6 team leads | Example Company |
| Years experience | 18+ | Full career |
