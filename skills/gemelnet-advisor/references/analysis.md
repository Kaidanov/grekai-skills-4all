# Reading GemelNet data responsibly

This skill turns public fund data into analysis. To keep that analysis honest —
and to stay on the right side of the *not-advice* line — apply the following when
you present numbers.

> **Standing disclaimer.** Everything below is *historical, public, fund-level*
> data. Past performance does not predict future results. Present comparisons and
> context; do not make buy/sell/switch recommendations or promise returns.

## 1. Use the right return horizon

- **Single-month (`MONTHLY_YIELD`)** — noisy; one month tells you almost nothing.
- **Year-to-date (`YEAR_TO_DATE_YIELD`)** — partial year, sensitive to start date.
- **3yr / 5yr average annual** — the figures to lead with. They smooth market
  cycles and are the fairest basis for comparison.

When the user asks "which fund is better", anchor on the 3yr/5yr average-annual
return **within the same classification**, and name the report period.

## 2. Always surface the fee

GemelNet returns are **net of management fees**, but the fee (`דמי ניהול`,
`AVG_ANNUAL_MANAGEMENT_FEE`) still matters because:

- It is the most negotiable lever the saver actually controls.
- Small gaps compound. ~1%/yr extra fee on a 250,000 ₪ balance is ~2,500 ₪ in
  year one and far more over decades.

Report the fee **alongside** return, never instead of it. Use
`revenue --balance N` to put the fee in shekels — and say it's a flat-balance
estimate that ignores deposits, deposit fees and compounding.

## 3. Compare like-for-like only

A fund's classification (`FUND_CLASSIFICATION`) sets its risk/asset profile. A
general-equity provident fund and a short-term-bond study fund are **not peers** —
the higher-return one is simply taking more risk. The `rank` command enforces
this by filtering to the target fund's own classification. Never rank across
classes.

## 4. Risk, not just return

Where the dataset provides them:

- **Standard deviation** — higher = more volatile. A slightly higher return with
  much higher volatility is not obviously "better".
- **Sharpe ratio** — return per unit of risk; useful for tie-breaking peers.

Mention risk whenever you highlight a high return, so the user sees the trade-off.

## 5. Statement / portfolio checkup ("scan")

When the user shares a statement:

1. Extract each **fund number + balance**. From a PDF, try `pdfplumber` / `pypdf`
   / `pdftotext`; if none is installed, ask the user to paste the numbers.
2. For each holding run `fund` (snapshot), `rank` (peer standing), and
   `revenue --balance <that holding>` (fee cost).
3. Roll it into one table: fund | class | 3yr return | peer rank | fee % | ₪/yr.
4. Summarise *observations* ("fund X sits in the bottom quartile of its class and
   charges an above-median fee"), not *instructions*. The decision is the user's.

## 6. Language to use — and avoid

**Use:** "Based on GemelNet data for <period>…", "ranks #k of N in its class",
"the published fee is…", "historically returned…".

**Avoid:** "you should switch", "this is the best fund", "you'll earn", "I
recommend". Those cross from analysis into advice.
