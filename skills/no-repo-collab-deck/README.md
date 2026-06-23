# No-Repo Collaborative Deck

Serverless, AI-driven presentation collaboration — no server, no repo. See the
[root README](../../README.md#featured-skill--the-no-repo-architecture) for the full
architecture writeup and diagrams.

## How it works

- **Stateful HTML** uses the File System Access API to read/write a sidecar `state.json`.
- **A shared cloud folder** (OneDrive / Google Drive / Dropbox) syncs that file across the team.
- **A Figma-style overlay** captures comment pins, AI prompt drafts, and approvals.
- **An MCP agent** reads the approved `state.json` and rewrites the deck HTML.

## Demo

A deck demo is published under [`decks/elon-musk/`](../../decks/elon-musk/).

## Local state

Per-session sidecar state belongs in `state.local.json`, which is git-ignored — never
commit a teammate's live session state.
