# Current-state mapping — interview + documents → one-page financial snapshot

A sub-skill of exit-strategist. Its job: build a clear, accurate **financial current-state map** of
a household and export it as a clean one-page PDF (any language, RTL-aware) — the foundation every
other use case builds on. It combines two inputs: **documents the user already has** and a
**guided interview** for what the documents don't cover. Use it whenever the user wants "a picture
of where we stand," a snapshot to share with a partner, or before running any exit/retirement plan.

## Privacy — a hard rule

- **Never accept, request, store, or repeat national ID numbers** (ת.ז.), passport numbers, full
  account numbers, or document issue dates. If they appear in an uploaded report, ignore them, do
  not echo them, and gently tell the user they can redact them.
- The user runs official portals themselves (in Israel: **הר הביטוח** for insurance, **הר הכסף**
  for dormant/active accounts, **המסלקה הפנסיונית**/pension portals for balances) and pastes back
  only the **numbers**. The skill cannot and must not log into these on the user's behalf.

## Two input paths (use both)

**Documents (ingest what exists).** Bank/credit-card exports (CSV), insurance reports (הר הביטוח),
pension/long-term-savings reports (הר הכסף / מסלקה), portfolio screenshots. For any transactions
file, run `data-quality.md` BEFORE using a single number. Note that insurance reports usually do
**not** contain pension balances — those come from the pension/savings report.

**Interview (fill the gaps).** Ask, in the user's language, only for what's missing. The structured
set:

- **Household & people:** ages of both partners; net monthly income of each; children and ages;
  aging/ill parents (current eldercare cost if any).
- **Assets:** cash/checking, savings/deposits, FX, investment portfolio (and whether liquid),
  pension/provident/study-fund **current balance** and, critically, the **projected balance at
  retirement** and **projected monthly annuity** (the report shows both — capture both, they differ
  by a lot), inheritance (received? earmarked?).
- **Real estate:** primary residence value; **mortgage balance and monthly payment** (and the
  monthly principal reduction, to estimate payoff date); any additional/inherited property (value,
  rented?, liquid?).
- **Liabilities:** mortgage, loans, high-interest/revolving card debt (distinguish a normal monthly
  card bill from carried interest-bearing balance).
- **Protections & local specifics (Israel):** severance status — **Section 14 (סעיף 14)** means
  severance is owed regardless of how employment ends, which removes the "don't resign" constraint;
  long-term-care (סיעודי) policies and their expiry; health coverage (universal — not employer-tied).
- **Forward view:** desired retirement age; rough target spending in retirement; relocation
  openness; risk tolerance of the portfolios.

Don't block on perfection — missing fields become clearly-labeled assumptions in the output.

## What the snapshot must contain

1. **Net worth** = assets − liabilities, split into **financial** vs **real-estate equity**, and
   **liquid/accessible** vs **locked** (pension/locked wrappers).
2. **Balance sheet** — the asset and liability breakdown, each line sourced.
3. **Cash flow** — household income vs *corrected* expenses (post data-quality audit), true
   monthly surplus/deficit and savings rate.
4. **Immediate savings recommendations (required).** This is mandatory, not optional. From the
   corrected categories, list specific cut opportunities with shekel/month and the inefficiency
   behind each (e.g. habitual high-frequency small purchases), and a monthly + annualized +
   to-retirement total. Protect work/income-producing tools from the cut list.
5. **Job-loss net** — what catches the household if income stops (partner income, severance/
   Section 14, unemployment eligibility, universal health, liquid runway).
6. **Assumptions & caveats** — every assumed or unverified number tagged, plus the data-quality
   findings (missing months, exclusions, re-categorizations).

## Building the PDF

Render HTML→PDF for proper bidi/RTL and clean design (Chromium/Playwright with an embedded Hebrew
font such as Rubik; A4; `print_background`). Aim for **one page** by default — compress spacing and
fold sections before spilling to a second page; if it must break, break on a logical section
boundary, never mid-content. Tag assumed/unverified figures visibly. Output in the user's language
and currency. Keep the disclaimer: *structured analysis, not financial/tax/legal advice — verify
with a licensed professional.* The personal output PDF is the user's private file and must never be
committed to a repo or skills catalog.

## Hand-off

Once the current-state map exists, it feeds directly into the other use cases: income-replacement,
FI/early-retirement (`early-retirement-fi.md`), job-loss resilience, and the macro/relocation and
displacement stress tests.
