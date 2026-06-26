# stock-mapper 📈

Turn a **market-moving catalyst** into a sourced map of the public stocks that fit
it — or paste your **holdings** and get full per-name research, multi-timeframe
trend charts, and a decision analysis.

> **Not financial advice.** This is a *decision aid* — it names the players, shows
> the trend, and lays out the case each way, then lets you decide. No personalized
> buy/sell/allocation directives. Do your own due diligence; it's not a licensed
> advisor. The skill repeats this in its own output.

## Two modes, one engine

| Mode | You give it | You get back |
|---|---|---|
| **A — Catalyst → map** | a link, screenshot, quote, ticker, or theme ("AI power", "GLP-1", "rare earths") | the public companies most exposed, bucketed + researched |
| **B — Portfolio → research** | your holdings ("NVDA 30%, PLTR 20%, …") | exposure, overlap, concentration, gaps + per-holding research |

Triggers on bare links or pasted holdings too — *"who benefits from this?"*,
*"what should I buy?"*, *"analyze my portfolio"*, *"should I hold?"*.

## What a run produces

- **TLDR table** — Stock · Ticker · Market cap · Dividend · Risk/upside, **bucketed**
  into *pure-play* (whole business is the theme; highest beta) · *large-cap exposure*
  (theme is upside, not survival) · *picks-and-shovels* (suppliers that win either
  way) · *can't-buy-it* (private/pre-IPO — named so you're not hunting a ghost ticker).
- **Trend across 1D · 1W · 1M · YTD · 1Y · 3Y · 5Y** — every series labelled
  "% change over the period", catalyst date marked where it matters.
- **Short- vs long-term split** — catalyst freshness / momentum / upcoming events
  vs fundamentals / moat / theme durability / dilution.
- **Red flags + a plain Sources list** — so you can verify every moving number.
- **Optional single-file HTML dashboard** (`assets/research-dashboard.html`) with
  the run's data embedded.

## The non-negotiable frame

1. **Not advice.** Map + case-each-way, never a verdict or position sizing.
2. **Search before it states — every time.** Prices, caps, dividends, returns,
   "who's in this space" all drift fast; nothing is filled from memory and no
   price curve is ever fabricated.
3. **Cite the moving facts.** Dollar figures, caps, returns, funding, ratings and
   named beneficiaries get citations; every output ends with a Sources list.

**Personal-data limit:** it uses only the holdings/weights you volunteer — never
net worth, income, or account size.

## The dashboard (`assets/research-dashboard.html`)

A self-contained HTML file — no server, no build — that runs locally, from a synced
folder, or on Vercel. Ticker chips, a 1D–5Y timeframe toggle, a Chart.js trend line,
per-stock research panels, short/long tabs, a portfolio paste box, sources, and a
prominent not-advice banner. Live series load when a free Twelve Data key is present
(stored in `localStorage`); with no key it falls back to the embedded period-return
data so the file is useful immediately. It never ships a fake series.

## Install

```bash
npx degit Kaidanov/grekai-skills-4all/skills/stock-mapper .claude/skills/stock-mapper
```

Then just ask — share a catalyst or paste holdings. An optional 3-question interview
(frame / horizon / depth) tunes emphasis only; the disclaimer stays regardless.
