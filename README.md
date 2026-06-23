# GrekAI Skills 4 All

A **static catalog** of agent skills (and, soon, hooks &amp; connectors), deployable to
Vercel with zero backend. The site root is a manifest-driven dashboard: add a folder
and one entry in [`skills.json`](./skills.json) and a new card appears — no build step.

> **Live structure:** `/` is the catalog → each item links to its demo and docs.
> `Skills` is live today; `Hooks` and `Connectors` are scaffolded as categories for later.

---

## Project layout

```
.
├── index.html          # manifest-driven dashboard (the catalog UI)
├── skills.json         # the catalog manifest — register items here
├── vercel.json         # Vercel static config (clean URLs)
├── assets/
│   ├── style.css
│   └── images/         # README/diagram images live here
├── skills/
│   ├── README.md       # how to add a skill
│   └── _template/      # copy this to start a new skill
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
fill in `skill.json`, then add an entry to `items` in `skills.json`.

---

## Featured skill — The No-Repo Architecture

A serverless, AI-driven way to collaborate on presentations (and other documents)
with **no server and no repository**. Persistence rides on a shared cloud sync folder;
a stateful HTML file reads and writes a `state.json` sidecar; an MCP agent rewrites the
source from approved changes.

![The No-Repo Architecture — Serverless AI Collaboration](./assets/images/architecture-pillars.svg)

### The four architectural pillars

1. **Stateful HTML via File System Access API** — modern browser APIs grant JavaScript
   permission to read and write a local sidecar `state.json` directly on the user's machine.
2. **Persistence via shared sync drives** — standard cloud folders (OneDrive, Google Drive,
   Dropbox) handle all file distribution and syncing. No server.
3. **The Figma-style UI overlay** — the generated HTML ships self-contained JS for comment
   pins, AI prompt drafts, assigning approvers, and approvals.
4. **The Agentic Orchestrator (MCP)** — Claude connects directly to the local directory via a
   File System MCP server to read and edit files.

![The 4 Pillars of No-Repo Architecture](./assets/images/architecture-4-pillars.svg)

### The collaborative workflow

1. **Generation** — the AI agent creates the initial presentation HTML, UI overlay, and state logic.
2. **Distribution** — the `.html` file and an empty `state.json` are saved into the shared cloud folder.
3. **Human collaboration** — colleagues open the local file; comment pins and prompt drafts update
   `state.json`, which instantly syncs across the team's machines.
4. **Agentic execution** — the agent reviews the approved `state.json` via MCP and rewrites the HTML
   to finalize the design.

> **Two layers, kept separate:** the hosted URL (Vercel/Pages) is just the *player*.
> Real-time collaboration runs off the shared cloud folder (e.g. `ClaudePresentationColab`)
> that each person connects to. Hosting and the shared folder are independent.

### The collaborative deck in action

The generated deck includes a Figma-style overlay: comment pins, an inline review panel,
AI assistant, change approvals, and export to PPTX/PDF.

| Comment on the image area | Comment on the title |
|---|---|
| ![Comment pin on the image area](./assets/images/collab-comment-image-area.svg) | ![Comment pin on the title](./assets/images/collab-comment-title.svg) |

![Full collaborative deck view](./assets/images/collab-deck-full.svg)

![Comment dialog, zoomed](./assets/images/collab-comment-title-zoom.svg)

> **About these images:** the diagrams and UI mocks above are committed **SVG
> recreations** so the README renders everywhere with no binary assets. To use the
> real product screenshots instead, drop PNGs into [`assets/images/`](./assets/images/)
> and switch the extension from `.svg` to `.png` in the links above — the filenames
> already match.

---

## License

© Kaidanov. All rights reserved unless noted otherwise.
