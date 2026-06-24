# GrekAI Skills 4 All

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
| **[No-Repo Collaborative Deck](./skills/no-repo-collab-deck/)** | Serverless, AI-driven presentation collaboration — no server, no repo. Stateful HTML reads/writes a `state.json` sidecar synced over a shared cloud folder; an MCP agent rewrites the deck from approved changes. | [README](./skills/no-repo-collab-deck/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=no-repo-collab-deck) · [demo](./decks/elon-musk/) |
| **[Session Handoff](./skills/handoff/)** | Package the current session so the **next** one resumes with zero re-research — a dated handoff doc, a copy-paste resume prompt, and a session-log metrics row. | [README](./skills/handoff/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=handoff) |
| **[Setup Memory — Memory-in-Repo](./skills/setup-memory/)** | Move Claude's per-project memory **into** the repo (`memories/repo/`) and auto-load it via a filesystem junction — committed, team-shared, token-efficient. | [SKILL.md](./skills/setup-memory/SKILL.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=setup-memory) |
| **[Dev Rules &amp; 13-Agent Roster](./skills/dev-rules-and-agents/)** | A portable bundle of engineering rules plus a reusable 13-agent specialist roster and routing standard — drop it into any codebase to bootstrap `CLAUDE.md` / `AGENTS.md` / `.cursor` rules and subagents. | [README](./skills/dev-rules-and-agents/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=dev-rules-and-agents) |
| **[Daily CV — Automated Job Hunt](./skills/daily-cv/)** | Config-driven, self-learning job-search agent: validates that roles are live, then generates an ATS-optimised CV + cover letter (DOCX + PDF) from verified facts only — never repeating a company+role. | [README](./skills/daily-cv/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=daily-cv) |
| **[My Claude Toolkit](./skills/my-claude-toolkit/)** | A portable, hand-authored Claude Code setup: helper command-scripts, hooks, a token/cost usage monitor + dashboard, a sparse-worktree engine, and a sanitized MCP-server inventory. | [README](./skills/my-claude-toolkit/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=my-claude-toolkit) |
| **[TLDR — End-of-Turn Status Report](./skills/tldr/)** | `/tldr` emits a tight status memo for the batch just finished — tokens (est total + exact per-subagent), time, a components-used table, done / to-do / issues / options, and a fresh-session call. Never fabricates numbers. | [README](./skills/tldr/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=tldr) |
| **[Token Audit — Cut Context Cost](./skills/token-audit/)** | `/token-audit` inventories your MCP servers, hooks, CLAUDE.md chain, skills, agents and memory, ranks the biggest per-session token sinks, and hands back Top-3 quick wins + a full reduction plan. Read-only by default. | [README](./skills/token-audit/README.md) · [page](https://grekai-skills-4all.vercel.app/skill?id=token-audit) |

> The full writeup for each skill — including the No-Repo deck's architecture and UI mocks —
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

## License

© Kaidanov. All rights reserved unless noted otherwise.
