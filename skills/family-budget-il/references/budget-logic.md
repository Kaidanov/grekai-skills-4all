# Budget logic (reused from the FinanceOS project)

These are the calculation rules that make a family budget *correct* rather than
just a sum of rows. The dashboard formulas and the logging flow must respect
them.

## 1. Operating budget vs. total cash flow

Not every shekel that moves is "spending". Moving money to a pension, buying
stocks, or transferring between your own accounts are **asset transfers**, not
consumption. If you count them as expenses, the budget looks alarming and the
savings rate looks wrong.

So the dashboard shows **two figures**:

1. **תקציב שוטף / Operating budget** — income and expenses only, *excluding*
   anything flagged `ExcludeFromBudget = TRUE`. **This is the default view.**
2. **תזרים כולל / Total cash flow** — everything, including investments and
   transfers. Useful for "did money actually leave the account?".

Rule: a transaction counts toward the operating budget **only if**
`ExcludeFromBudget = FALSE`.

## 2. The ExcludeFromBudget flag

Set `ExcludeFromBudget = TRUE` automatically for:
- Anything in **Savings & Investments** (pension, השתלמות, גמל, stocks, crypto,
  savings transfers).
- Anything in **Transfers** (Bit, Paybox, bank transfer, ATM withdrawal —
  these are money relocating, not being consumed; the actual spend shows up when
  the cash/Bit is used).
- Credit-card **bank settlement** lines (see §3).

Everything else (`income` and real `expense`) is `FALSE`.

The investment summary still reports invested / returns / net flow separately —
just keep it out of the operating budget.

## 3. Credit-card reconciliation (avoid double-counting)

The trap: a family logs both
- the **monthly bank deduction** ("חיוב כרטיס אשראי — Cal — 7,430"), and
- the **individual line items** on that card (groceries, fuel, restaurants…).

If both count as expense, every shekel is counted twice. Fix:
- Treat the **line items** as the real spend (they carry the right categories).
- Treat the **monthly bank deduction** as a settlement: category
  `הלוואות וחובות / כרטיס אשראי`, and `ExcludeFromBudget = TRUE`.
- When the family only logs the lump-sum deduction (not line items), keep it as a
  normal expense so spending isn't undercounted — but then don't also log the
  line items.

In logging, watch for this and ask one clarifying question if it's ambiguous:
"do you also log this card's individual purchases, or just the monthly bill?"

## 4. Salary-aligned budget cycle

Israeli salaries usually land a few days before month-end. A 1st-to-1st cycle
splits the salary from the rent/bills it's meant to cover. Default to a
**salary-aligned cycle**:

- Preferred: **salary-day to salary-day** (e.g. the 10th of each month to the
  9th of the next), using the salary arrival day from setup.
- Common alternative: **15th-to-15th**.
- Fallback: calendar month (1st-to-1st) if the family prefers it.

Store the cycle start day in the Setup tab; the dashboard derives the current
cycle window from it and filters Transactions by date accordingly.

## 5. Core dashboard figures (per current cycle)

- **Total income** = SUM of `Amount` where `Type = income` and date in cycle.
- **Operating spend** = SUM where `Type = expense` and `ExcludeFromBudget=FALSE`
  and date in cycle.
- **Net operating** = income − operating spend.
- **Savings rate** = (income − operating spend) / income. Show as %; if income is
  0, show "—" (guard against #DIV/0!).
- **Invested this cycle** = SUM where `Type = investment` and date in cycle.
- **Per-group actual** = SUMIFS over `Group`, respecting type and exclude flag.
- **Per-group variance** = budget target − actual. Negative = over budget;
  highlight.

## 6. Net worth

Net worth lives on its own tab, not in the cycle math:
- **Assets** = bank balances + investment account balances (pension, השתלמות,
  גמל, brokerage, savings) + other assets.
- **Liabilities** = mortgage balance + loans + current card balances.
- **Net worth** = assets − liabilities.
These are point-in-time balances the family updates occasionally; they aren't
derived from the transaction ledger.

## 7. Formula hygiene (Google-Sheets-safe)

- Use `SUMIFS` / `SUMPRODUCT`, `IFERROR`, `IF`. All survive the Excel→Google
  Sheets import.
- Guard every division with `IFERROR(...,"—")` or an `IF(denominator=0,...)`.
- Reference the Transactions columns by whole-column ranges so new rows are
  picked up automatically (e.g. `Transactions!$H:$H`).
- Keep date filtering with a helper cycle-start / cycle-end cell pair so one edit
  reframes the whole dashboard.
