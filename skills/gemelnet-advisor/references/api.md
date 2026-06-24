# GemelNet dataset & API reference

The engine reads the **GemelNet** open dataset published on
[data.gov.il](https://data.gov.il) by Israel's Ministry of Finance — the Capital
Market, Insurance & Savings Authority (רשות שוק ההון, ביטוח וחיסכון). GemelNet
(גמל-נט) is the regulator's public reporting system for long-term savings funds:
provident funds (קופות גמל), study funds (קרנות השתלמות), investment-provident
(גמל להשקעה) and pension funds.

## Access — CKAN datastore API

data.gov.il runs on **CKAN**. The engine uses two actions, both over plain HTTPS
(no key required for public reads):

| Action | Purpose |
|---|---|
| `package_show?id=gemel-net` | List the dataset's resources (tables/files). |
| `datastore_search?resource_id=…` | Query rows from a datastore-active resource. |

Base URL: `https://data.gov.il/api/3/action`

`datastore_search` parameters the engine uses:

- `resource_id` — the table to query (discovered from `package_show`).
- `q` — free-text search (works with Hebrew, URL-encoded).
- `filters` — JSON object for exact-match columns, e.g. `{"FUND_ID": "9012"}`.
- `limit` — max rows.

The engine never hardcodes a resource ID. `resources` lists them; the other
commands pick the most relevant **datastore-active** resource automatically
(preferring a returns/yield table) so the skill keeps working if IDs change.

```bash
# See exactly what the dataset exposes today
python3 scripts/gemelnet.py resources
```

## Fields

GemelNet publishes English column names. The engine keeps a small synonym map
(`FIELDS` in `scripts/gemelnet.py`) so a renamed column does not break it. The
columns it reads:

| Concept | Primary column | Notes |
|---|---|---|
| Fund number | `FUND_ID` | Stable key. Names repeat; always confirm by number. |
| Fund name | `FUND_NAME` | Hebrew. |
| Managing company | `MANAGING_CORPORATION` | e.g. אלטשולר שחם, מיטב, הראל. |
| Classification | `FUND_CLASSIFICATION` | Use this to define "like-for-like" peers. |
| Report period | `REPORT_PERIOD` | Month of the snapshot — always state it. |
| Total assets | `TOTAL_ASSETS` | Fund size. |
| Monthly yield | `MONTHLY_YIELD` | Net of fees, single month — noisy. |
| Year-to-date | `YEAR_TO_DATE_YIELD` | Net of fees. |
| 3yr avg annual | `AVG_ANNUAL_YIELD_TRAILING_3YRS` | Preferred for comparison. |
| 5yr avg annual | `AVG_ANNUAL_YIELD_TRAILING_5YRS` | Preferred for comparison. |
| Management fee | `AVG_ANNUAL_MANAGEMENT_FEE` | Annual %, on accumulation (`דמי ניהול`). |
| Deposit fee | `AVG_DEPOSIT_FEE` | On contributions, where reported. |
| Sharpe ratio | `SHARPE_RATIO` | Risk-adjusted return, where reported. |
| Std deviation | `STANDARD_DEVIATION` | Volatility, where reported. |

All return figures are **net of management fees** as published by the regulator.

## Gotchas

- **Confirm by number, not name.** Several funds share similar Hebrew names; the
  `FUND_ID` is the only stable key.
- **State the report period.** Snapshots are monthly; always tell the user which
  month the numbers are from.
- **Peers = same classification.** Comparing across `FUND_CLASSIFICATION` is
  apples-to-oranges; the `rank` command filters to the target's own class.
- **Network required.** The engine calls data.gov.il live. On failure it surfaces
  the error rather than inventing numbers.
