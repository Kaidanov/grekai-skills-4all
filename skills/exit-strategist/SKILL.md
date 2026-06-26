---
name: exit-strategist
description: >-
  Build an honest, localized, family-adjusted plan to reduce dependence on a salary,
  grow income outside a job, and (if the user wants) leave their 9-5 — WITHOUT the
  hustle-culture fantasy. Use whenever the user wants an "exit plan", wants to "replace
  my salary", "quit my 9-5", "escape the rat race", "reach financial independence",
  "build a second income to leave my job", asks "how long until I can quit", "is my exit
  date realistic", or pastes one of the viral "I handed Claude my salary / 7 prompts to
  escape your job" threads and wants to actually run it. Also triggers on: "freedom
  number", "salary replacement plan", "12 month escape plan", "what if AI takes my job",
  "am I about to be automated", "retire early", "FIRE plan", "coast FI", "should we relocate
  to afford this", and Hebrew: "תוכנית יציאה", "להחליף את המשכורת", "לעזוב את העבודה",
  "פרישה מוקדמת", "כמה זמן עד שאוכל להתפטר". Use it EVEN when the user only gives partial
  numbers, and use it instead of just answering the raw viral prompt verbatim — the whole point
  is to add realism, a full household balance sheet, partner income, care obligations (kids and
  aging parents), local tax/pension/safety-net context, relocation options, and stress tests for
  both AI job loss and macro shocks (war, reserve duty, currency) that the original prompts ignore.
  Handles three models: income-replacement, capital / early-retirement (FI, Coast-FI, Barista-FI),
  and blends.
---

# Exit Strategist

Turns the popular "escape your 9-5" prompts into a plan a careful adult can actually act
on. It runs the same seven questions the viral threads use, but wraps each one in four
things those threads leave out: **honest base rates**, **the user's country and tax/safety-net
reality**, **their family situation**, and **a stress test for involuntary job loss (incl.
AI displacement)**. Output is a scenario-banded plan, not a single optimistic number.

## Use-case map (this skill is generic — route to the right path)

This skill is not only about quitting a job. It covers the whole "money independence" surface.
Identify which the user wants (often several) and pull the matching references:

| # | Use case | Trigger | Core references |
|---|----------|---------|-----------------|
| 1 | **Salary-exit / quit the 9-5** | "replace my salary", "escape my job", pasted viral prompts | base-rates, blind-spots, ai-displacement |
| 2 | **FI / early retirement** | "retire early", "FIRE", "Coast-FI", "never need a salary" | early-retirement-fi |
| 3 | **Involuntary job-loss resilience** | "I'm about to be laid off", "what if AI takes my job" | ai-displacement, blind-spots, country-profiles |
| 4 | **Current-state mapping → PDF** (sub-skill) | "map where we stand", "snapshot for my partner", interview + uploaded reports | current-state-mapping, data-quality |
| 5 | **Spending optimization / where to cut** | "where can we save", uploaded transaction export | **data-quality (first)**, current-state-mapping |
| 6 | **Macro / relocation resilience** | war, reserve duty, currency, "should we relocate" | macro-and-relocation, country-profiles |

The **current-state map (#4)** is the foundation — most other use cases run better once it exists.
Whenever the request involves an **uploaded financial export** (bank/card/insurance/pension), the
**data-quality audit (`references/data-quality.md`) is a hard gate** — run it before trusting any
number (see "Audit the data first" below).

## The honesty contract (read first)

The genre this comes from sells a fantasy: "I handed an AI my salary and it told me I was
6 months from never needing one again." For the large majority of people that is false,
and repeating it does real harm — people quit too early, drain savings, and land worse off.

So this skill commits to four rules. Apply them in every response:

1. **No fabricated certainty.** Never promise a timeline or income figure the inputs don't
   support. Give ranges (conservative / base / stretch), and say which assumptions move them.
2. **Base rates beat vibes.** Most side incomes start small and slow, many never replace a
   salary, and the ones featured online are survivors. Anchor every projection to
   `references/base-rates.md`, not to what would sound motivating.
3. **Downside before upside.** Protect the floor (emergency runway, insurance, not burning
   the boat) *before* optimizing the climb. A plan that ignores what happens if it fails is
   not a plan.
4. **This is not financial, tax, or legal advice.** It's a structured way to think, using
   the user's own numbers. For anything binding — resignation, tax registration, pension,
   investing — tell them to confirm with a licensed professional in their country.

If following these rules makes the answer less exciting than the thread promised, that is
the correct outcome. Say so plainly and kindly.

## Audit the data first (whenever an export is involved)

If the user uploads any financial export — bank, credit-card, insurance, or pension — do **not**
compute averages or "where to cut" from the raw file. Read `references/data-quality.md` and run its
audit first. Real exports routinely: mislabel categories (a ₪12,700 transfer tagged "coffee"),
hide income/transfers as expenses, span multiple years with **missing months** (so dividing by 12
halves every figure), bloat junk buckets ("misc", "household & shopping"), and carry duplicates.
State what you found, rebuild categories the user actually understands, separate
income-producing work tools from discretionary spend, reconcile against a second source, and only
then quote numbers — sized to the corrected figures, with confidence and caveats. Wrong precision
is worse than an honest range.

## What you need from the user (intake)

Model the **household**, not the individual — a salary exit is a household decision. Collect what
you can; don't block on perfection. Missing fields become explicit assumptions you flag. Ask in
the user's own language. The essentials:

**The destination (ask this first, it shapes everything)**
- **What they actually want.** Not just "out of my job" — *toward what*? More time with kids, a
  craft/business they love, travel, less stress, a different field, full early retirement. The
  positive vision sets what "enough" means and which model (below) fits. A plan to escape with no
  destination is the one people abandon.
- **Why now** (burnout, ceiling, layoff fear, war/instability, autonomy, a sick parent). If the
  driver is burnout or a bad manager, the fix may be a transfer/sabbatical, not entrepreneurship.
- **Desired exit date and target retirement age** (if any) — and whether they want to *replace
  income* or *retire early on capital*, or both.

**The household income & people**
- **Their net + gross monthly income**, and the **partner's net income and job security** —
  treat partner income as a core variable: whose income is the floor, and whether one partner
  stays employed (for stability, health, pension) as the anchor while the other builds/exits.
- **Dependents and care load.** Number and ages of children (costs rise, esp. education); and
  **aging or ill parents** — likely future eldercare cost and time (the "sandwich" squeeze).
  Don't bank on inheritance. Who else relies on this salary.

**Full current financials (balance sheet, not just cash flow)**
- **Assets:** liquid savings/emergency fund, investments, home equity, pension/retirement
  balances, business value. Separate *accessible* cash from locked wealth.
- **Liabilities:** mortgage (balance, rate, years left), loans, high-interest debt.
- **Cash flow:** household essential expenses (housing, food, utilities, debt minimums, care)
  vs. discretionary; current side income (and whether it's proven recurring or one-off).
- **Net worth** = assets − liabilities. Needed for any early-retirement / FI calculation.

**Capacity, status & risk**
- **Skills + realistic *sustainable* weekly hours** after job + family without burnout. Be
  skeptical of "20 hrs/week" from someone with a full-time job and kids.
- **Status & contract gates.** Visa/work-authorization (tied to the employer?); non-compete, IP
  and moonlighting clauses. Can void a plan — see hard gates below.
- **Pension conditions.** What employer contributions stop on exit; self-employed pension
  obligations; study-fund (e.g. קרן השתלמות) continuity; early-withdrawal penalties; what
  relocation/emigration does to the pension. Feeds the localize step and the retirement-hole cost.
- **Relocation openness.** Would they move — domestically (cheaper area), internationally
  (cost/safety/tax/opportunity), or go remote-first to decouple income from location? Relocation
  is often a bigger lever than any side hustle.
- **Macro/country exposure.** Country stability, war/security, mobilization or reserve duty
  (e.g. מילואים pulling the earner away for weeks), currency risk. Feeds the macro stress test.
- **Debt & near-term borrowing**, **partner buy-in** (a gate, not a nicety), and **age / years
  to retirement** (sets how recoverable a failed exit is).

If the user pasted the viral prompts with `[brackets]` unfilled, your first job is to turn
those brackets into this intake — fill them with real numbers before running anything.

## Check the hard gates first

Before any math, read `references/blind-spots.md` and clear its **hard gates** — the factors
that can void an entire plan no matter how good the numbers look: visa/work-authorization tied
to the employer, non-compete / IP-assignment / moonlighting clauses, and the resignation-vs-
dismissal asymmetry that can forfeit unemployment and severance. If a hard gate is open (e.g.
a tied visa, or a side path that breaches the contract), say so plainly, route the plan around
it, and tell the user to confirm with the relevant professional (immigration or employment
lawyer) before acting. The rest of `blind-spots.md` (borrow-before-you-leave, kill high-interest
debt first, the retirement hole, re-employability, partner buy-in, cost-of-living arbitrage, and
the non-binary "third option") feeds the engine steps below — pull from it as each becomes relevant.

## Pick the right model (there are three, not one)

The viral prompts assume everyone wants the same thing — build side income to replace a salary.
They don't. Match the model to the destination from intake:

- **Income-replacement** — grow income *outside* the job until it covers the floor, then (maybe)
  leave. Best when they want autonomy/a business or to quit sooner than capital allows. This is
  the engine's default seven-step path below.
- **Capital / early retirement (FI)** — accumulate investments until a safe withdrawal covers
  expenses, so they never *need* earned income again. Different math entirely (savings rate +
  returns + withdrawal rate + years, not a side-hustle ramp). When the user wants to "retire
  early" / "never need a salary," read `references/early-retirement-fi.md` and run that model —
  including the lighter hybrids: **Coast-FI** (stop saving, let existing investments grow to cover
  a normal retirement age) and **Barista-FI** (a small/part-time income bridges the gap so the
  portfolio can be smaller).
- **Blend** — the common real answer: a stable (often partner's) salary as the anchor, modest
  side income, *and* steady investing toward FI. Sequence the irreversible moves; don't do them
  all at once.

State which model you're running and why. If they asked for "replace my salary in 6 months" but
their real wish is early retirement, say so — the honest path may be slower capital accumulation,
not a frantic hustle.

## Late-life & legacy layers (the long horizon)

A serious retirement plan is more than one withdrawal number — these layers sit on top and are
easy to under-count. Surface them explicitly and use a **multi-pot model** so they don't all compete
for the same asset:

- **Pension: current balance vs projected.** Pension reports show *current* savings AND a much
  larger *projected balance at normal retirement age* plus a *projected monthly annuity* — they
  differ enormously because the projection assumes years of further contributions. Use the right one
  for the question: early retirement stops contributions, so you must **bridge the years between
  early-retirement age and when the annuity begins** from liquid assets, not from the projected
  figure.
- **Eldercare / nursing (from ~80).** Long-term care can cost far more than normal living
  (illustratively ~₪25k/person/month in Israel today), for years, and is poorly covered by health
  insurance and shrinking סיעודי policies. Don't fold it into the steady withdrawal — fund it from a
  dedicated reserve, typically **home equity** (sale or reverse mortgage). This implies the primary
  residence may be the care fund, not a guaranteed inheritance.
- **Private medical & dental.** Recurring, real, and largely uncovered (implants, electives) —
  budget a standing reserve, don't assume zero.
- **Child support timing.** Help with cars, education, and especially a first home often lands in
  the very years before early retirement, competing with accumulation. Map it on a timeline and
  decide which assets fund it (often an inherited/second property) so it doesn't quietly delay the
  exit.

**The multi-pot framing:** liquid portfolio funds living (+ the bridge to the annuity); one property
funds late-life care; a second/inherited property or surplus funds children. The honest strategic
question is usually *how much of the real estate is for us vs the children* — name it; there's no
single right answer.

## Section 14 and local severance (Israel)

Where the user has **Section 14 (סעיף 14)**, accrued severance is theirs regardless of how
employment ends — this removes the usual "don't resign, you'll forfeit severance" constraint and
changes the exit sequencing. Absent Section 14, the resignation-vs-dismissal asymmetry in
`blind-spots.md` applies. Confirm specifics with a רו"ח / employment lawyer.

## Localize before you calculate

Read `references/country-profiles.md` and apply the user's country. It covers, per country,
the things the original prompts get silently wrong by assuming the US:

- **Currency & realistic cost-of-living** for the math.
- **Tax on side income** and the threshold where casual income becomes a registered business
  (e.g. Israel עוסק פטור/מורשה; US Schedule C / 1099; UK self-assessment; etc.).
- **Social safety net** — what actually catches you if the job ends: unemployment benefit
  duration & eligibility, statutory severance, notice periods, and whether health coverage
  is tied to employment (huge in the US, far less in Israel/EU). This directly changes how
  big an emergency fund needs to be.
- **Pension / retirement conditions** of leaving employment: which employer contributions stop,
  study-fund continuity (e.g. קרן השתלמות), self-employed pension obligations, early-withdrawal
  penalties and tax, and what relocation/emigration does to the pension. This sets the true
  long-term cost of leaving, not just the monthly gap.
- **Macro & country shocks and relocation.** For unstable regions, model involuntary disruption —
  war, mobilization/reserve duty (e.g. מילואים), currency swings, capital controls — and weigh
  relocation (domestic / international / remote-first) as a strategic lever. Read
  `references/macro-and-relocation.md` and apply it alongside the country profile.

Worked example inside the file is Israel; a generic template lets you handle any country,
and you can web-search to fill gaps for a country not pre-profiled. Always state the local
assumptions you used.

## The engine — seven steps, upgraded

Run these in order for the **income-replacement** model. (For the **capital / early-retirement**
model, run `references/early-retirement-fi.md` instead of steps 3–7, then still do steps 8–9.)
Each keeps the recognizable name from the thread, then does more. Reference base rates from
`references/base-rates.md` throughout, and both stress tests — AI (`references/ai-displacement.md`)
and macro/country (`references/macro-and-relocation.md`) — at step 8.

### 1. The Reality Check (true financial position)
Lay out the real position from their income, fixed costs, and current side income —
**after local tax**, not gross. Compute: monthly surplus/deficit, months of runway their
savings actually buy at essential-spend, and savings rate. Then name the 2–3 biggest *real*
levers (not "12 opportunities") and the single highest-leverage change for this month.
Family adjustment: runway is measured against *household essential* spend, and against the
chance the partner's income also wobbles.

### 2. The Expense Identifier (free up cash — honestly)
From their spending, flag genuinely habitual/low-value outflows and total the realistic
monthly amount freed. Be honest that cutting lattes rarely funds freedom; the big rocks are
housing, transport, debt cost, and lifestyle creep. Redirect freed cash with a rule:
**first to emergency runway until it hits the localized target, then to income-building.**
Never advise cutting into health, insurance, or essentials for kids.

### 3. The Freedom Number (what "enough" actually is)
Compute the monthly *outside-job* income needed to cover **household essentials** (the floor)
and, separately, **full current lifestyle** (the goal). Give both — people conflate them.
Subtract any **stable partner income** that will keep flowing: the user often needs to replace
only *their* share, not the whole household budget — this can change the target dramatically and
is the single biggest reason a partnered exit is more feasible than a solo one. Express it after
tax and after the cost of running the side income, and add a line for **future care costs**
(kids' education, aging parents) so the number isn't quietly too low. Then give the *single
fastest realistic* route to the floor using their skills — flagged with the base-rate
time-to-first-revenue, not a fantasy ramp.

### 4. The Income Multiplier (three realistic paths)
Three realistic ways to grow income outside the job, matched to their actual skills and
sustainable hours. For each: the honest time-to-first-money, the time-to-meaningful-money,
the main failure mode, and the exact first step this week. Prefer paths with fast feedback
and low fixed cost over ones needing a big audience or upfront capital. Weight toward skills
that are **AI-complementary, not AI-exposed** (see step 8).

### 5. The Exit-Date Test (is the date real?)
Take their desired date, savings, and side income, and answer honestly whether it's realistic.
If yes: monthly milestones. If no: the *earliest defensible* date and exactly what has to
change to hit it. Hard rule: do not validate an exit date that leaves the household below a
safe localized runway with dependents. Recommend the lower-risk sequencing (go part-time /
negotiate / keep the job as the funding engine) before "quit by Friday."

### 6. The Salary-Replacement Plan (de-hyped)
The thread asks to "replace my salary in 6 months." State plainly: full replacement in 6
months is rare and usually means a pre-existing audience, capital, or an unusually
in-demand skill. Build the month-by-month plan to *partial* replacement with honest targets
(e.g. cover X% of essentials by month 6), and show what the genuine 6-month full-replacement
case would require so they can judge if it's them. Targets are bands, not points.

### 7. The 12-Month Plan (cut dependence, keep optionality)
A simple month-by-month plan that lowers salary dependence, grows one proven income stream
(don't sprawl across five), and positions — not forces — an exit. Every month has: one
primary action, a measurable target, and a **go/no-go gate** (only scale time/money into
something once it shows real revenue). Build in reversibility: nothing in the plan should be
irreversible until the income is proven.

### 8. The Disruption Stress Test (the part the threads skip)
Stress-test against the income you might *not* keep — from two directions.

**AI / automation** (`references/ai-displacement.md`):
- **Score the day-job's exposure.** How automatable is the role on current trends, and over
  what horizon? Treat the salary as *possibly time-limited*, not guaranteed for the full
  runway. If exposure is high, the exit plan stops being optional and becomes resilience.
- **Score the side-income paths.** Down-weight paths whose value an AI tool is rapidly
  commoditizing (generic copywriting, basic translation, template design, simple data entry);
  up-weight paths combining judgment, trust, physical presence, accountability, distribution,
  or a human relationship. Re-rank step 4's options accordingly.

**Macro / country** (`references/macro-and-relocation.md`):
- For unstable regions, model **war, mobilization/reserve duty, currency collapse, capital
  controls, sector shocks.** Reserve duty alone can remove the earner — from both the job and
  the side hustle — for weeks. Build a buffer for it and prefer income that survives the earner
  being away. Weigh **relocation** (domestic / international / remote-first) where it cuts cost
  or risk more than any hustle would.

Then run the contingency: "If the job income drops by 50%, or ends in N months, or the earner is
mobilized for two months, does the plan survive?" If not, fix the floor first.

### 9. Consolidate
Produce the final plan (format below) combining all steps, in the user's language and currency.
State which **model** (income-replacement / capital-FI / blend) you ran. Make visible — not
buried — the **household** framing (partner income, care obligations), the **pension/retirement**
cost of leaving, the **relocation** option if relevant, and both **disruption contingencies**
(AI and macro). Tie the plan back to the **destination** the user named: this should move them
toward what they actually want, not just away from a job.

## Output format

ALWAYS structure the final plan like this (translate headings into the user's language):

```
# Your Exit Plan — [honest one-line read of the situation]

## What you're aiming for
[The destination in their words + which model this plan runs:
 income-replacement / capital-FI / blend.]

## Gates & flags
[Any hard gates (visa, contract clauses, resignation-vs-dismissal) and what they force.
 If none, say so. If one is open, it leads the whole plan.]

## Where you actually stand
[Balance sheet: net worth (assets − liabilities), accessible cash, after-tax household
 surplus/deficit, true runway in months, savings rate. State local assumptions used.]

## Your number(s)
- Floor (household essentials, minus stable partner income): [amount] /mo after tax
- Goal (full lifestyle):                                     [amount] /mo after tax
- [If FI model:] FI target capital + Coast/Barista variants and years to each.
[Inflation-adjusted; include future care costs (kids, parents) and the retirement cost of leaving.]

## The realistic timeline
Conservative / Base / Stretch — with the assumption that flips each band.
[Plain statement of whether their desired date / retirement age is realistic.]

## The smartest path (incl. the non-binary options)
[Don't default to "quit." Put the real options on the table — internal move, part-time,
 sabbatical, negotiate, switch employer, job-as-funding-engine, one partner stays employed
 as the anchor, relocation (domestic / abroad / remote-first), cost-of-living arbitrage —
 and recommend the lowest-risk one that gets them toward the destination above.]

## The plan, month by month
[Each month: primary action · measurable target (as a band) · go/no-go gate.]
Built to be reversible until income is proven; keeps the re-employment off-ramp open.
Sequence irreversible moves (quit / relocate / launch) — don't stack them.

## If things go wrong (disruption contingencies)
[AI/automation exposure of the day job. Macro/country: what the household does if income
 drops 50%, the job ends in N months, or the earner is mobilized/on reserve duty for weeks.
 The floor-first fix.]

## Do this in the next 7 days
[3–5 concrete first steps.]

## Honest caveats
[What could make this slower/harder; what's outside the model; "not financial/tax/legal
 advice — confirm resignation, tax registration, pension, visa, and contract terms with the
 right licensed professional in [country]."]
```

## Tone

Direct, warm, numerate. You are the friend who is good with money and refuses to let them do
something dumb — not the influencer selling the dream. When the realistic answer is "this is
a 2–3 year project, not 6 months, and here's how to do it without wrecking your family's
safety," say exactly that.
