<div align="center">

<img src="./logo.svg" width="92" alt="GrekAI Skills 4 All" />

# GrekAI Skills 4 All

**A free, open catalog of agent skills, hooks &amp; connectors — drop them into Claude Code, Cursor, Codex &amp; friends.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/Kaidanov/grekai-skills-4all?style=social)](https://github.com/Kaidanov/grekai-skills-4all/stargazers)
[![Live site](https://img.shields.io/badge/live-vercel-black)](https://grekai-skills-4all.vercel.app/)
[![Made by Set4u](https://img.shields.io/badge/made%20by-Set4u-2563eb)](https://set4u.biz)
[![Sponsor](https://img.shields.io/badge/%F0%9F%92%96-Sponsor-ff5e9c)](https://set4u.biz)

### 💖 [Support this project — keep it free &amp; open source](https://set4u.biz)

</div>

> **Free & open (MIT)** — use anything here, attribution appreciated. **PRs welcome.** Built by [Set4u](https://set4u.biz).
> ▶️ Watch a [narrated demo of this very catalog](https://grekai-skills-4all.vercel.app/skills/tutorial/examples/grekai-catalog-tour/) — made by the **tutorial** skill. If it's useful, please ⭐.

A **static catalog** of agent skills (and, soon, hooks &amp; connectors), deployable to
Vercel with zero backend. The site root is a manifest-driven dashboard: add a folder
and one entry in [`skills.json`](./skills.json) and a new card appears — no build step.
Each card opens its own page with the skill's README, an install command, and how-to-use
instructions.

> **Live:** <https://grekai-skills-4all.vercel.app/> — `/` is the catalog, each item
> opens `/skill?id=<id>`. `Skills` is live today; `Hooks` and `Connectors` are scaffolded
> as categories for later.

---

## Skills catalog

Every skill lives in its own folder under [`skills/`](./skills/) with its own README. The
table below maps what's in the catalog today — follow each skill's link for the full
explanation, install command, and usage.

| Skill | What it does | Docs |
|---|---|---|
| **[Tutorial — Narrated Playwright Walkthroughs](./skills/tutorial/)** | Record narrated, themeable product tutorials: Playwright drives the app and screenshots each step, `edge-tts` (Jenny) narrates, and you get either a **no-ffmpeg HTML player** or an MP4, plus a light/dark, logo-branded `index.html` switching between all tutorials. Human-gated; ships `/tutorial-init/create/update/status`. | [README](./skills/tutorial/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=tutorial) · [▶ demo](https://grekai-skills-4all.vercel.app/skills/tutorial/examples/grekai-catalog-tour/) |
| **[Share Presentation — Collaborate Over Shared Org Folders](./skills/share-presentation/)** | Presentation collaboration **inside your organization** — no server, no repo. Stateful HTML reads/writes a `state.json` sidecar synced over a shared org folder (OneDrive / SharePoint / Google Drive / Dropbox); an MCP agent rewrites the deck from approved changes. | [README](./skills/share-presentation/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=share-presentation) · [demo](./decks/elon-musk/) |
| **[Session Handoff](./skills/handoff/)** | Package the current session so the **next** one resumes with zero re-research — a dated handoff doc, a copy-paste resume prompt, and a session-log metrics row. | [README](./skills/handoff/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=handoff) |
| **[Setup Memory — Memory-in-Repo](./skills/setup-memory/)** | Move Claude's per-project memory **into** the repo (`memories/repo/`) and auto-load it via a filesystem junction — committed, team-shared, token-efficient. | [README](./skills/setup-memory/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=setup-memory) |
| **[Dev Rules &amp; 13-Agent Roster](./skills/dev-rules-and-agents/)** | A portable bundle of engineering rules plus a reusable 13-agent specialist roster and routing standard — drop it into any codebase to bootstrap `CLAUDE.md` / `AGENTS.md` / `.cursor` rules and subagents. | [README](./skills/dev-rules-and-agents/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=dev-rules-and-agents) |
| **[Daily CV — Automated Job Hunt](./skills/daily-cv/)** | Config-driven, self-learning job-search agent: validates that roles are live, then generates an ATS-optimised CV + cover letter (DOCX + PDF) from verified facts only — never repeating a company+role. | [README](./skills/daily-cv/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=daily-cv) |
| **[My Claude Toolkit](./skills/my-claude-toolkit/)** | A portable, hand-authored Claude Code setup: helper command-scripts, hooks, a token/cost usage monitor + dashboard, a sparse-worktree engine, and a sanitized MCP-server inventory. | [README](./skills/my-claude-toolkit/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=my-claude-toolkit) |
| **[TLDR — End-of-Turn Status Report](./skills/tldr/)** | `/tldr` emits a tight status memo for the batch just finished — tokens (est total + exact per-subagent), time, a components-used table, done / to-do / issues / options, and a fresh-session call. Never fabricates numbers. | [README](./skills/tldr/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=tldr) |
| **[Token Audit — Cut Context Cost](./skills/token-audit/)** | `/token-audit` inventories your MCP servers, hooks, CLAUDE.md chain, skills, agents and memory, ranks the biggest per-session token sinks, and hands back Top-3 quick wins + a full reduction plan. Read-only by default. | [README](./skills/token-audit/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=token-audit) |
| **[Family Budget Planner (Israel-first)](./skills/family-budget-il/)** | Build a shared, Google-Sheets-ready family budget workbook, then keep it current by typing expenses in plain Hebrew or English — no bank links, no app. Setup wizard builds one `.xlsx` of live SUMIFS formulas; chat logging returns categorized rows to paste. Israel defaults (₪, HMOs, ארנונה, 15th-to-15th cycle, benefit clubs) but works anywhere. | [README](./skills/family-budget-il/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=family-budget-il) |
| **[Exit Strategist — Money-Independence & Early Retirement](./skills/exit-strategist/)** | Honest planning across the whole money-independence surface — salary-exit, FI/early retirement (Coast/Barista-FI), job-loss resilience, current-state mapping → one-page PDF, spending cuts, macro/relocation. Strips hustle-culture hype; runs a hard-gate **data-quality audit** on real exports before any number is used; localizes tax/pension/Section 14; stress-tests AI & macro shocks. Bilingual (EN/HE), any language. Not financial advice. | [README](./skills/exit-strategist/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=exit-strategist) |
| **[Car Finder IL — Smart Used-Car Alerts (Yad2)](./skills/car-finder-il/)** | Find a good second-hand car in Israel and get a phone ping **only when something genuinely worth it appears**. Reads Yad2 via an Apify actor (reads-only, no login), **scores each car against its own peer cohort** (price vs comparables, hand/יד, owner, km/yr, photos), dedupes in Supabase, and pushes only new matches / real price drops to WhatsApp · Telegram · ntfy. Stdlib-only Python; bilingual (EN/HE). | [README](./skills/car-finder-il/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=car-finder-il) |

> The full writeup for each skill — including the Share Presentation skill's architecture and UI mocks —
> now lives in that skill's own folder, not here.

---

## Project layout

```
.
├── index.html          # manifest-driven dashboard (the catalog UI)
├── skill.html          # per-skill detail page (README + install + usage)
├── skills.json         # the catalog manifest — register items here
├── vercel.json         # Vercel static config (clean URLs)
├── assets/
│   ├── style.css
│   └── images/         # shared diagram/UI images
├── skills/
│   ├── README.md       # how to add a skill
│   ├── _template/      # copy this to start a new skill
│   └── <skill>/        # one folder per skill (its own README + assets)
└── decks/              # collaborative deck demos (e.g. elon-musk)
```

## Run / deploy

**Local preview** — it's static, so any static server works:

```bash
npx serve .
# or: python3 -m http.server 8000
```

**Vercel** — import `Kaidanov/grekai-skills-4all` in the Vercel dashboard
(Add New → Project → Import). No framework preset needed; `vercel.json` handles it.
Every push redeploys automatically.

## Add a skill

See [`skills/README.md`](./skills/README.md). In short: copy `skills/_template/`,
fill in `skill.json`, add an entry to `items` in [`skills.json`](./skills.json) (with a
short `usage` string), and write a `README.md` in the new skill folder — it renders
automatically on the skill's page.

---

## License & credits

Licensed under the **[MIT License](./LICENSE)** — free to use, modify, and distribute; just keep the
copyright notice. A link back to [set4u.biz](https://set4u.biz) or this repo is appreciated.

Created and maintained by **Tzvi Gregory Kaidanov** — **[Set4u](https://set4u.biz)**.
Contributions are welcome — see **[CONTRIBUTING](./CONTRIBUTING.md)**. If this catalog helps you,
a ⭐ on the [repo](https://github.com/Kaidanov/grekai-skills-4all) means a lot and helps others find it.
