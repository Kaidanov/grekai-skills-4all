---
name: stock-mapper
description: >-
  Turn a market-moving catalyst into a sourced map of the public stocks that fit
  it, OR take the user's current portfolio and return full research, multi-
  timeframe trend charts, and a decision analysis. Catalysts: a speech, executive
  order, policy, earnings/M&A headline, product launch, viral clip
  (Instagram/TikTok/X), macro shift, or a named theme (AI power, GLP-1, rare
  earths). Use whenever the user shares a link, screenshot, quote, ticker,
  holdings list, or topic and asks which stock fits, who benefits, what to buy,
  "analyze my portfolio", or "should I hold". Trigger on bare links or pasted
  holdings too. Produces a TLDR table (cap, dividend, risk/upside) bucketed
  pure-play/large-cap/picks-and-shovels, 1D-5Y trend charts, sourced research, a
  short- vs long-term decision framework, red flags, and a deployable single-file
  HTML dashboard. Can interview first (risk, horizon, depth). Presents analysis
  and the case each way — NOT licensed financial advice or personalized buy/sell
  directives.
---

# Catalyst → Stock Mapper & Portfolio Research

Two jobs, one engine:

- **Mode A — Catalyst → map.** A catalyst comes in; you map it to the public
  companies most exposed, with trends, research, and a short/long-term read.
- **Mode B — Portfolio → research.** The user pastes their holdings; you analyze
  exposure, overlap, concentration, and per-holding research, and lay out the
  decision factors — without telling them what to buy or sell.

The output is always a **decision aid, not a recommendation** — name the players,
show the trend, give the case each way, and let the user decide.

## Non-negotiable frame (finance)

Three rules override everything else:

1. **Not financial advice.** Present the factual landscape and the case for and
   against. Never issue a personalized buy/sell/allocation directive or position
   sizing. In portfolio mode you give a *framework* and "what an investor in this
   position commonly weighs", never "sell 40% of your NVDA". Close every output
   with a one-line reminder: a decision aid, not advice; do your own due
   diligence; you're not a licensed advisor.
2. **Search before you state — every time.** Prices, caps, dividends, yields,
   period returns, who got funded, even "which companies are in this space" drift
   fast and may post-date training. Never fill these from memory. Never fabricate
   a price series for a chart — if you can't get real data, show the period
   % changes you sourced and say the live chart needs the dashboard + a data key.
3. **Cite the moving facts and list sources.** Dollar figures, caps, returns,
   funding, ratings, and named beneficiaries get citations. Always end with a
   plain Sources list so the user can verify.

**Personal-data limit:** use only the holdings/weights the user volunteers. Never
ask for net worth, income, or account size, and never make output depend on them.

## Workflow

### Step 0 — Optional interview (only if the user wants it)

Default is to just produce the output. Run a short interview when the user signals
they want it dialed-in ("best for me", "I'm cautious/aggressive", "should I
hold", "go deep"), or offer it as a one-line follow-up otherwise.

Three tappable questions, max, one screen (use the tappable-options tool where
supported; else ask inline). Ask once, then proceed.

1. **Frame?** Just the map · Cautious lean · Aggressive lean · Income focus
2. **Horizon?** Short (days–weeks) · Long (multi-year) · Both
3. **Depth?** TLDR · + fundamentals deep-dive · + dashboard

The interview tunes *emphasis, framing, depth* only — never a suitability
assessment, never personal finances. The disclaimer stays regardless.

### Step 1 — Establish the input

- **Mode A:** pin the catalyst to one sentence — *"The catalyst is X, the
  investable angle is Y."* If a link won't open (Instagram/TikTok/X reels almost
  never do), say so in one line and ask what it's about; once they tell you,
  proceed. If they named a theme, go straight to research.
- **Mode B:** parse the pasted holdings (tickers, optional weights/shares).
  Weights or ratios are enough — don't require dollars. Echo back what you read.

### Step 2 — Research (current state)

Search to ground everything. Find: what was announced/said, **when**, by whom;
hard numbers (funding, contracts, stakes); **named beneficiaries** (highest-
confidence fits); analyst ratings / price targets; and whether the news is fresh
or already priced in. Scale searches to complexity; search each name separately.

### Step 3 — Map

- **Mode A:** bucket the names — **pure-plays** (whole business is the theme;
  highest beta, usually smallest/speculative) · **large-cap exposure** (theme is
  upside, not survival) · **picks-and-shovels** (suppliers/infrastructure that win
  either way) · **can't-buy-it** (private/pre-IPO — name them so the user isn't
  hunting a ghost ticker). Named/funded beneficiaries go to the top of their
  bucket.
- **Mode B:** map each holding to the theme and to its sector. Compute **theme
  exposure** (share of the portfolio riding this catalyst), **overlap** (correlated
  names / single-factor risk, e.g. everything is AI-compute), and **concentration**
  (any one name too large). Note **gaps** the theme has that the portfolio lacks
  (hedges, picks-and-shovels) — as "options to consider", not directives.

### Step 4 — Per-name data + multi-timeframe trends

For each name (Mode A list, or Mode B holding) pull and report:

- **Ticker / cap / dividend** (yes-no + rough yield; flag pre-profit dilution).
- **Trend across 1D · 1W · 1M · YTD · 1Y · 3Y · 5Y** — see Trend charts below.
- **One-line risk/upside profile** — bull case + the catch.

Never state a price/cap/return you didn't just read; mark estimates "~" or omit.

### Step 5 — Sources, research & the short/long-term split

- **Research per name (paraphrased, never long quotes):** rating tone, price-
  target direction, the bull case and the bear case in your own words.
- **Split the decision factors:**
  - **Short-term (days–weeks):** catalyst freshness, momentum / key technical
    levels, upcoming events (earnings, contracts, policy dates), insider flow.
  - **Long-term (1–5y):** fundamentals (growth, margins, cash, valuation), moat,
    theme durability, dilution.
- **Sources list:** outlets/titles used, so the user can verify.

### Step 6 — Assemble + (optional) dashboard

Use the templates below. Lead with the table/analysis, then trends, then the
short/long split, then red flags, sources, and the one-line disclaimer. If the
user asked for depth/dashboard, also generate `assets/research-dashboard.html`
populated with the run's data (see Deployable dashboard).

## Trend charts

Cover **1D, 1W, 1M, YTD, 1Y, 3Y, 5Y**. Always label each as "% change over the
period" and, when relevant, mark the catalyst date on the series.

How to render:

- **Quick / inline:** use the chart tool to draw the period series or a
  period-return bar per name.
- **Full deliverable:** generate the HTML dashboard; it pulls live series client-
  side and toggles timeframes.
- **Data:** daily frames (1M, YTD, 1Y, 3Y, 5Y) come from a keyless/free source;
  intraday (1D, 1W) needs an intraday feed or API key. If a frame can't be
  fetched, show the sourced period % change instead and label it — never invent a
  curve. Put the real period-return numbers you found into the embedded data so
  the dashboard renders even before any live key is set.

## Output templates

**Mode A — catalyst map:**

```
[One sentence: catalyst + investable angle.]

[TLDR table: Stock | Ticker | Market cap | Dividend | Risk/upside — bucketed.]

Trend (% change): [per name across 1D/1W/1M/YTD/1Y/3Y/5Y — table or charts.]

Short-term vs long-term:
- Short (days–weeks): [catalyst timing, momentum, upcoming events.]
- Long (1–5y): [fundamentals, durability, dilution.]

Takeaways: [2–4 one-liners — dividends/safety, the real exposure + danger,
the tightest fit.]

Red flags: [the ones that apply, with cited specifics.]

Sources: [list.]

[One line: decision aid, not advice — DYOR, not a licensed advisor.]
```

**Mode B — portfolio analysis:**

```
[One line: what you read — N holdings, theme exposure %.]

Snapshot: theme exposure ·· overlap / single-factor risk ·· concentration flags.

Per holding: [ticker — bucket/sector — trend — short & long factors — case
for / case against.]

Gaps & options to consider: [what the theme has that the portfolio lacks —
framed as considerations, never directives.]

Sources: [list.]

[One line: decision aid, not advice — DYOR, not a licensed advisor.]
```

## Deployable dashboard (`assets/research-dashboard.html`)

A single self-contained HTML file — no server, no build — that runs locally, from
a synced folder, or on Vercel. Regenerate it per run with the data embedded.

- **Features:** ticker chips · timeframe toggle (1D/1W/1M/YTD/1Y/3Y/5Y) · Chart.js
  trend line · per-stock research panel · short-term/long-term tabs · portfolio
  paste box that maps holdings to the analysis · sources list · a prominent
  not-advice banner. Mobile-first; RTL-capable.
- **Data layer:** live series via a pluggable free provider (Twelve Data key,
  stored in localStorage); on no-key/failure it falls back to the embedded
  period-return data so the file is useful immediately. Never ships a fake series.
- **You fill** `window.RESEARCH_DATA` (one object per name: bucket, cap, dividend,
  profile, periodReturns, shortTerm[], longTerm[], research[], sources[]). Prices
  load live when a key is present.

Keep it lean (around the 500-line cap). Don't use localStorage for anything but
the optional API key.

## Red-flag library (use the ones that apply)

Already priced in / buy-the-rumor (say when it happened) · speech ≠ law ≠ revenue
· extreme valuation (cite the multiple) · dilution (pre-profit names) · insider
selling (cite the figure) · volatility / 50%+ drawdowns · no single winner yet
(structure beats a single pick) · concentration or conflict-of-interest.

## Common framing analysts use (offer, don't prescribe)

A balanced way to play a speculative theme — *as what analysts commonly suggest*,
attributed, never your advice: a large-cap core plus small, equally-weighted
satellite positions in the pure-plays, each sized so a 50% drop in one won't hurt,
treated as a multi-year option. Weight to the interview answers if you ran it;
never cross into "buy this."

## Quality bar / common mistakes

- **Don't recommend.** Map + case-each-way, not a verdict. Portfolio mode =
  framework + considerations, never directives or sizing.
- **Don't invent tickers, caps, or price curves.** Wrong/made-up data is worse
  than omitting it. Verify; label freshness.
- **Lead with named beneficiaries** — the tightest fits.
- **Surface private names** so the user isn't hunting a ticker that doesn't exist.
- **Mobile-first formatting.** Table + one-liners, not an essay.
- **Don't over-interview.** One short set, max; never ask about personal finances.

## Examples

**Mode A (catalyst):** clip won't fetch → user says "American quantum computing" →
research finds an executive order + a funding round naming firms → pure-plays IonQ
(IONQ)/D-Wave (QBTS)/Rigetti (RGTI), large-cap IBM/Alphabet, picks-and-shovels
GlobalFoundries (GFS), can't-buy Infleqtion/PsiQuantum → table + 1D–5Y trends +
short/long split + red flags (priced in, P/S extremes, insider selling) + sources.

**Mode B (portfolio):** user pastes "NVDA 30%, PLTR 20%, DELL 20%, INTC 15%,
LLY 15%" → snapshot: ~85% AI / policy-linked single-factor risk, NVDA concentration →
per-holding trends + short/long factors + case each way → gaps: no hedge, no
picks-and-shovels → considerations, not directives → sources → not advice.
