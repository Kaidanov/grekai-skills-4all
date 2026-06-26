# Data-quality audit — never trust an export until it passes these checks

Financial exports from Israeli (and most) aggregators are routinely **wrong in ways that
silently destroy the analysis**. Categories are mislabeled, transfers and income masquerade as
expenses, months are missing, and a single junk transaction can double a category. If you compute
averages or "where to cut" on raw export data you will give confidently wrong advice. Run this
audit FIRST, on any uploaded transactions, and state what you found before any number reaches the
user. This is a hard gate, not an optional step.

## The five failure modes (all observed in real exports)

1. **Mislabeled categories.** Auto-tagging guesses from a partial merchant string and is often
   nonsense. Real example: a recurring ₪6,350 and a one-off ₪12,700 both tagged "coffee"; a
   ₪10,000 transfer tagged "internet"; an inter-account transfer tagged "rent". Treat the source
   category as a *hint*, never as truth.
2. **Junk-bucket categories.** Catch-all buckets like "שונות / misc" and broad ones like
   "household & shopping" absorb everything unrecognized and balloon to meaningless totals
   (e.g. "household ₪11,287/mo" when real food is a fraction of that). Never quote a super-category
   as a spending figure — decompose it.
3. **Transfers & income counted as expenses.** Money moved between the user's own accounts,
   salary inflows, loan repayments, and reimbursements appear as outflows. Tells: descriptions with
   "הע."/"העברה"/transfer, identical recurring round amounts, same amount appearing as +X and −X
   across two of the user's accounts, amounts near a known salary. These are **not spending** —
   exclude them.
4. **Missing months.** A multi-year export may have data for a category only in some months. If you
   divide a category's total by 12 but it only has 6 active months, every figure is **halved**.
   Always check date coverage *per category* and divide by active months, not calendar months.
5. **Duplicates.** Exact duplicate rows, and the same purchase logged on two card accounts
   (e.g. a max sub-card and cal). Dedup on (date, agent, amount, account) then on
   (date, agent, amount) before summing.

## The audit procedure

1. **Span & coverage.** Print the date range. For each category, count how many distinct months
   actually contain transactions. Normalize to monthly using *active* months only, and say so.
2. **Dedup.** Remove exact-duplicate rows, then same-purchase cross-account copies. Report the
   shekel amount removed.
3. **Outlier scan.** List the largest single transactions (e.g. > a few × the category median).
   These are where mislabeled transfers/income hide. Inspect them by description before trusting
   the category.
4. **Transfer/income filter.** Exclude inter-account transfers, salary, loan repayments, and
   reimbursements from the *expense* view. When unsure, ask the user about a specific recurring
   amount rather than guessing ("the recurring ₪6,350 tagged coffee — salary? transfer? loan?").
5. **Rebuild categories by merchant when needed.** If source categories fail the checks above,
   re-categorize from the merchant name (שופרסל/רמי לוי→groceries; ארומה/cafe→coffee;
   GitHub/Anthropic/Lovable→work tools; Netflix/Disney/PlayStation→home entertainment).
6. **Reconcile against a second source.** Cross-check the rebuilt totals against the app's own
   dashboard and against known fixed bills (mortgage, rent, utilities). If they diverge a lot, the
   export is incomplete — say so and lower confidence.

## Separating work tools from household spending

When categorizing software/subscriptions, split **work/income-producing tools** (e.g. GitHub,
AI/dev subscriptions, professional networking, cloud) from **home entertainment** (streaming,
gaming, consumer subscriptions). Never recommend cutting income-producing tools as if they were
discretionary — flag them separately and protect them.

## How to present spending after the audit

- Give the user **categories they actually understand** (food, eating-out, transport, kids,
  home, entertainment, work-tools), not the source's broken buckets.
- State confidence and caveats: which months were missing, what was excluded as transfers, what was
  re-categorized, where the export looks incomplete.
- Only THEN compute "where to cut" — and size the cut to the *corrected* number, not the raw one.

If the export can't be made trustworthy, say so plainly and fall back to the interview
(`current-state-mapping.md`) and the user's own reliable figures. Wrong precision is worse than
honest ranges.
