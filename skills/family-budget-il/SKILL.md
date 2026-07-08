---
name: family-budget-il
description: >-
  Set up and run a shared family budget planner as a Google-Sheets-ready
  workbook, with natural-language expense logging through chat. Defaults to
  Israel (Hebrew/RTL, shekels, Israeli categories, HMOs, 15th-to-15th salary
  cycle, provident/pension funds, benefit clubs) but works for any country. Use
  whenever the user wants to build a family/household budget, create a shared
  budget spreadsheet, plan monthly spending by category, log expenses/salary/
  bills in plain language ("spent 250 at Shufersal", "arnona 1200", "salary came
  in"), see where the family stands vs. budget, track net worth and investments
  alongside spending, or get discount/benefit-club recommendations. Trigger on
  "תקציב משפחתי", "מתכנן תקציב", "ניהול הוצאות משפחה", "family budget",
  "household budget", "budget planner", "track our spending", "shared budget
  sheet", even without the word "skill". Prefer this over a plain spreadsheet
  whenever the budget is for a household and ongoing logging is implied.
license: Proprietary
---

# Family Budget Planner (Israel-first)

Build a **shared, Google-Sheets-ready budget workbook** for a household, then let
the family keep it current by **typing expenses in plain Hebrew or English** —
no bank connections, no app to install, no data uploads required.

The design goal is *lightweight*: one workbook the family shares via Google
Sheets, plus chat-based logging. Do **not** turn this into a system that forces
the family to connect every bank, card, and broker.

## How it works (the two-phase model)

1. **Setup (once)** — interview the family, then generate one `.xlsx` workbook.
   They upload it to Google Drive → *Open with Google Sheets* → *Share* with the
   family. That sheet is now their live, shared budget.
2. **Logging (ongoing, through chat)** — the family tells Claude what happened
   ("שילמתי 250 בשופרסל", "נכנסה משכורת 18,000", "קנס חניה 100"). Claude returns
   clean, categorized rows ready to paste into the **תנועות / Transactions** tab.
   The dashboard recalculates itself. If the Google Drive/Sheets connector is
   available, append the rows directly instead of asking them to paste.

---

## Phase 1 — Setup interview

Run the wizard the first time, or whenever the user says "set up", "new budget",
"start a family budget". Ask in the user's language (Hebrew if they wrote in
Hebrew). Keep it to a few grouped questions — do not interrogate one field at a
time. Use the `ask_user_input` tool for the multiple-choice ones (country,
budget cycle, currency) so it is one tap on mobile.

Collect:

1. **Family members** — names and (optionally) who earns / who has a card.
2. **Country & currency** — default Israel / ₪ (ILS). If another country, adjust
   currency symbol, swap Israeli-specific categories (HMOs, ארנונה, ביטוח לאומי)
   for local equivalents, and skip the Israeli clubs section.
3. **Income sources** — salary(ies), freelance, rental, allowances, benefits.
   Capture the **salary arrival day** (e.g. the 10th) — it drives the cycle.
4. **Budget cycle** — Israel default is **15th-to-15th** (salary-aligned), since
   Israeli salaries land a few days before month-end and a 1st-to-1st cycle
   splits the salary from its expenses. Offer: salary-day cycle / 15th-to-15th /
   calendar month (1st-to-1st).
5. **Fixed monthly expenses** — rent/mortgage, ארנונה, ועד בית, utilities,
   internet, phone, insurances, subscriptions, loan repayments, tuition/חוגים.
6. **Accounts** — bank accounts and credit cards (just labels + last 4 digits;
   no numbers, no credentials).
7. **Monthly budget targets** — per category group. If they don't know, seed
   sensible defaults from their fixed expenses and ask them to adjust later.
8. **Savings & investments** — קרן השתלמות, קרן פנסיה, קופת גמל, מניות/ETF,
   savings — for the net-worth tab. These are **asset transfers, not spending**
   (see budget-logic).
9. **Goals** — what is the family saving for? (trip, emergency fund, apartment,
   debt payoff…). For each: a name, target amount, target date, and how much is
   already saved. These seed the **יעדים / Goals** tab, which computes the
   required ₪/month and flags when goals together exceed the monthly surplus.
10. **Benefit / discount clubs** (Israel) — ask which they belong to (חבר, מועדון
   הסתדרות / ועד עובדים, מועדוני אשראי, תן ביס/Cibus/Pluxee, supermarket clubs,
   etc.). Used later for recommendations. See `references/israeli-clubs.md`.

Write the answers to a config JSON, then build the workbook:

```bash
python scripts/build_workbook.py --config /home/claude/budget_config.json \
  --out /mnt/user-data/outputs/family_budget.xlsx
python scripts/recalc.py /mnt/user-data/outputs/family_budget.xlsx   # if present
```

The config schema and a worked example are in `assets/config.example.json`.
Read `references/categories.md` for the full category tree the workbook seeds,
and `references/budget-logic.md` for how the dashboard formulas must behave.

After building, present the file and give the family **three short steps**:
upload to Google Drive → Open with Google Sheets → Share with the family.

---

## Phase 2 — Natural-language logging

This is the everyday path. The family sends messages like:

- "שילמתי 250 בשופרסל ועוד 40 בארומה"
- "arnona 1,247 came out today"
- "salary 18,500 net, and Maya's freelance 3,200"
- "parking fine 100, and 600 to the dentist"
- "העברתי 2,000 לקרן השתלמות"

For each message:

1. **Parse** every line item — amount, currency, merchant/description, and date
   (default to today if unstated). Follow `references/nl-parsing.md`.
2. **Classify** each into the taxonomy: pick *type* (income / expense / transfer
   / investment) and *category group + category*. Use merchant→category mapping
   from `references/nl-parsing.md`; when unsure, mark category as
   `לא מסווג / Uncategorized` rather than guessing wildly.
3. **Set the budget flag** — `exclude_from_budget = TRUE` for investments,
   savings, and internal transfers (asset moves, not consumption). See
   budget-logic.
4. **Avoid double-counting credit cards** — if they log both a card's monthly
   bank deduction *and* its line items, keep the line items and mark the bank
   deduction as a reconciliation/transfer. See budget-logic.
5. **Output rows** in the exact Transactions column order, as a clean block the
   user can paste. Echo a one-line confirmation of what was logged and the
   running cycle balance if known. Then **stop** — don't over-explain.

**Transactions column order (must match the workbook):**
`Date | Member | Account | Type | Group | Category | Description | Amount | ExcludeFromBudget | Notes`

If the Google Drive/Sheets connector is connected, offer to append the rows to
their sheet directly instead of pasting. Confirm the sheet name first.

---

## Phase 3 — Goals, "where do we stand?", and recommendations

When the user asks how they're doing ("איפה אנחנו עומדים?", "how's the budget?",
"can we afford X?"):

- Summarize the **current cycle**: total income, operating spend, savings rate,
  and the 3–4 categories most over/under budget. Lead with the number, keep it
  to a screenful. Offer a chart only if they want detail.
- Distinguish **תקציב שוטף (operating budget)** from **תזרים כולל (total cash
  flow)** — default to operating. See budget-logic.

**Goals** live on the **יעדים / Goals** tab. When the user sets or asks about a
goal ("we want ₪30k for a trip by July", "are we on track for the down payment?"):

- Make sure the goal row exists (name, target, target date, saved). The tab
  auto-computes months left, still-needed, and **required ₪/month**.
- Read the **Gap** cell (monthly surplus − total required/month). If negative,
  say plainly that the goals together outpace the surplus and offer the levers:
  push a date out, trim a category, or raise income. Tie it to the savings rate.

**Recommendations** live on the **המלצות / Recommendations** tab. The top of that
tab auto-computes insights (biggest category, most over budget, subscriptions
total, savings rate). The **action board** below is yours to fill:

- Read `references/israeli-clubs.md`. Map the family's declared clubs and their
  biggest categories to concrete actions, and **write rows into the action
  board**: Area, Action, Est. ₪/month saving, Status. **Web-search the specific
  clubs they named** for current benefits before quoting any number — perks
  change often, so never state a current discount from memory.
- The tab totals the potential saving and shows the **improved savings rate** if
  they action the "לביצוע" items — use that as the motivating headline.
- Be concrete and non-pushy. Note you're not a financial advisor for anything
  involving investing or pensions; hand pension/fund questions to the
  `gemelnet-advisor` skill if available.

---

## Reference files

Read these as needed — don't load them all up front.

- `references/categories.md` — the full bilingual Israeli category taxonomy (18
  groups, ~70 categories) that the workbook seeds. Read before building or when
  categorizing an unusual item.
- `references/budget-logic.md` — the calculation rules reused from the user's
  FinanceOS project: operating-vs-total cash flow, the `ExcludeFromBudget` flag,
  credit-card reconciliation, salary-aligned cycles, savings rate, net worth.
  Read before building the dashboard or when a logging edge case is unclear.
- `references/nl-parsing.md` — how to turn Hebrew/English plain-language messages
  into transaction rows, including Israeli merchant→category mappings and
  currency/amount parsing. Read whenever logging transactions.
- `references/israeli-clubs.md` — major Israeli benefit/discount programs and how
  to turn club membership into spending recommendations. Read for Phase 3.

## Scripts

- `scripts/build_workbook.py` — generates the Google-Sheets-ready `.xlsx` from a
  config JSON. All dashboard cells are live formulas (SUMIFS over Transactions),
  so the sheet stays correct as rows are added. Dropdowns use data validation so
  they survive the import to Google Sheets.
- `scripts/recalc.py` — (copied from the xlsx skill) recalculates formulas and
  reports any formula errors. Run after building; fix until zero errors.

## Guardrails

- Never ask for or store account numbers, card numbers, passwords, or
  credentials. Labels and last-4 only.
- Keep every workbook formula error-free (no #REF!, #DIV/0!, #VALUE!).
- Don't fabricate current club discounts or fund yields — search first.
- For anything touching pensions/provident funds or investing decisions, hand off
  to the `gemelnet-advisor` skill if available, and note you're not a financial
  advisor.
