---
name: setup-memory
description: Set up version-controlled, per-project Claude memory that lives IN the repo (memories/repo/) and is auto-loaded via a filesystem junction at ~/.claude/projects/<slug>/memory. Use when starting Claude on a new project, when the user asks to "set up memory", "memory in repo", "share memory with the team", "make memory reusable across projects", or to migrate an existing ~/.claude project-memory folder into the repo. Generic + publishable — no secrets, no per-user content.
---

# Setup Memory — memory-in-repo

Claude's per-project memory normally lives **outside** the repo at `~/.claude/projects/<slug>/memory/`, so it is never versioned or shared. This skill moves it **into** the repo at `memories/repo/` and links it back with a directory **junction**, so the curated project knowledge is:

- **Committed + team-shared** — clone the repo, run the setup, and Claude instantly has the project's context.
- **Token-efficient** — Claude reads a tight, hand-maintained `MEMORY.md` index instead of re-discovering the codebase every session. That is the whole point: pay once to write a memory, save tokens on every future session.
- **Just files** — adding/updating memory is a normal file edit in the repo (the junction makes it live immediately).

Each project keeps its **own** memory (per-project; nothing is shared between projects except this generic skill).

## Run

```powershell
& "$HOME\.claude\skills\setup-memory\scripts\Setup-Memory.ps1" -ProjectPath <repo-root>
# -ProjectPath defaults to the current directory. Add -WhatIf to preview, -Force to re-seed templates.
```

Idempotent and **no admin required** (a directory junction, not a symlink). The script:

1. Computes the project **slug** from the path the same way the harness does: lowercase the drive letter, then turn `:` `\` `/` `.` `_` and spaces into `-` (e.g. `C:\Projects\Foo.Bar_v2` → `c--Projects-Foo-Bar-v2`).
2. Creates `<repo>/memories/repo/` and a `MEMORY.md` index skeleton (**Feedback / Reference / Project / User**) if missing.
3. If `~/.claude/projects/<slug>/memory` already exists as a **real folder**, migrates its files into `memories/repo/` first (never overwrites a newer file), then removes the empty folder.
4. Replaces it with a junction: `~/.claude/projects/<slug>/memory` → `<repo>/memories/repo`.
5. Seeds `_TEMPLATE.memory.md` (frontmatter template) + a `README.md` if missing. Prints slug, paths, and migrated-file count.

## Memory file convention (what goes in `memories/repo/`)

- One fact per file, named `<type>_<kebab-slug>.md` where **type ∈ feedback | project | reference | user**.
- Frontmatter:
  ```markdown
  ---
  name: <type>_<kebab-slug>
  description: <one line — used for recall relevance>
  metadata:
    node_type: memory
    type: feedback | project | reference | user
  ---
  <the fact. For feedback/project, add **Why:** and **How to apply:** lines. Cross-link with [[other_name]].>
  ```
- `MEMORY.md` is the index loaded every session: one bullet per file under its section, `- [file](file.md) — hook`. Never put memory content in `MEMORY.md`.
- **type meanings:** `user` = who the user is / preferences · `feedback` = how Claude should work here (with the why) · `project` = ongoing work/goals/constraints not derivable from code or git · `reference` = pointers to external resources (URLs, dashboards, tickets).

## Notes

- Commit `memories/` to share with the team. Keep it **public-safe** — no secrets, tokens, or credentials.
- Re-run any time; safe and idempotent. Use `-WhatIf` to see what it would change.
- Generic by design (no hardcoded user, org, or project names) so it can be published and reused anywhere.
