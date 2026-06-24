---
name: gemelnet-advisor
description: Query and analyse Israeli provident (קופת גמל), study (קרן השתלמות) and investment-provident (גמל להשקעה) and pension funds using the official GemelNet open dataset on data.gov.il. Search funds, show a single fund snapshot, compare funds, rank one against its like-for-like peers, scan a statement into a portfolio checkup, and estimate the shekel cost of management fees. Public fund-level data only — framed as data-grounded analysis, not financial advice. Ships a UserPromptSubmit hook that auto-triggers on Hebrew/English fund keywords.
---

# GemelNet Advisor — Israeli Pension Funds

Analyse Israeli long-term-savings funds from the **regulator's own public data**:
the GemelNet open dataset published by the Ministry of Finance (Capital Market,
Insurance & Savings Authority) on **data.gov.il**. The engine pulls live,
fund-level, net-of-fee figures — returns, fees, assets — and turns them into
side-by-side comparisons and peer rankings.

> **Not financial advice.** Everything here is *historical, public, fund-level
> data* presented as analysis. It contains no personal data and no secrets. Tell
> the user this explicitly; do not make buy/sell/switch recommendations or
> promises about future returns.

---

## When to use

Trigger this skill when the user asks about — in Hebrew or English:

- A specific Israeli fund (provident / study / investment-provident / pension).
- "Compare these funds", "which has better returns / lower fees".
- "Is my fund any good?" / "rank my fund against its peers".
- "How much am I paying in fees?" (shekel cost of `דמי ניהול`).
- A pension statement / portfolio checkup.

The bundled **UserPromptSubmit hook** (`hooks/gemelnet-hook.py`) auto-suggests
the skill when it sees keywords like `גמל`, `קרן השתלמות`, `פנסיה`, `תשואה`,
`gemel`, `provident fund`, `study fund`, `pension`.

---

## The engine

`scripts/gemelnet.py` — **Python standard library only**, no `pip install`. It
talks to the data.gov.il CKAN datastore API. Run from the skill folder:

```bash
# List the GemelNet dataset's resource IDs (sanity check — needs network)
python3 scripts/gemelnet.py resources

# Search funds (Hebrew or English free text)
python3 scripts/gemelnet.py funds --q "אלטשולר"
python3 scripts/gemelnet.py funds --q "study" --limit 15

# One fund's latest snapshot
python3 scripts/gemelnet.py fund 9012

# Compare funds side by side
python3 scripts/gemelnet.py compare 9012 512 1234

# Rank a fund against its like-for-like peers (same classification)
python3 scripts/gemelnet.py rank 9012

# Estimate the annual shekel cost of the management fee on a balance
python3 scripts/gemelnet.py revenue 9012 --balance 250000
```

Each command prints a compact table and ends with a "not advice" reminder.
See `references/api.md` for the dataset/field details and `references/analysis.md`
for how to read returns, fees and peer rankings responsibly.

---

## Workflow

1. **Identify the fund(s).** If the user gives a fund number, use it. Otherwise
   run `funds --q "<name>"` (Hebrew accepted) and confirm the right `FUND_ID`
   before going further. Fund numbers are the stable key; names repeat.
2. **Pull the data.** Use `fund`, `compare`, or `rank` as the question demands.
   Always compare **within the same classification** (`FUND_CLASSIFICATION`) —
   a general provident fund and a bond-only study fund are not peers.
3. **Read it responsibly** (see `references/analysis.md`):
   - Prefer **3yr / 5yr average-annual** returns over a single month or YTD.
   - State returns **net of fees**, and surface the management fee (`דמי ניהול`)
     separately — a small fee gap compounds.
   - For "how much do I pay", use `revenue --balance N`; explain it's a flat-balance
     estimate that ignores deposits, deposit fees and compounding.
4. **Statement / portfolio checkup ("scan").** When the user pastes or uploads a
   statement, extract each fund number + balance, then for each holding run
   `fund` (snapshot), `rank` (peer standing) and `revenue` (fee cost). If a PDF
   is provided, try `pdfplumber` / `pypdf` / `pdftotext` to pull the text; if
   none is installed, ask the user to paste the fund numbers and balances. Roll
   the per-fund results into one checkup table.
5. **Frame the answer.** Lead with the data, name the report period, and close
   with the standing disclaimer: *public, historical, fund-level data — analysis,
   not financial advice.*

---

## Guardrails

- **Public data only.** Fund-level figures from GemelNet — never ask for, store,
  or echo back national-ID numbers, account credentials, or other PII.
- **No advice.** No buy/sell/switch calls, no future-return promises, no tax or
  legal guidance. Offer comparisons and context; let the user decide.
- **Be precise about provenance.** Always name the source (GemelNet / data.gov.il)
  and the report period. Past performance ≠ future results.
- **Degrade gracefully.** If the network or a resource is unavailable, say so and
  show the `resources` output rather than guessing numbers.

---

## Files

```
gemelnet-advisor/
├── SKILL.md                  this file — the workflow
├── README.md                 overview + install + usage
├── skill.json                catalog metadata
├── .gitignore                ignores __pycache__, *.pyc, local scans
├── scripts/
│   └── gemelnet.py           the engine (stdlib only)
├── references/
│   ├── api.md                GemelNet dataset + CKAN API + fields
│   └── analysis.md           how to read returns / fees / rankings
└── hooks/
    └── gemelnet-hook.py      UserPromptSubmit auto-trigger
```
