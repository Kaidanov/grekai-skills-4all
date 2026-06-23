# Project memory (memory-in-repo)

This folder **is** Claude's per-project memory. It lives in the repo so it is version-controlled
and shared with the team. A directory junction links it to `~/.claude/projects/<slug>/memory`, so
Claude loads it automatically every session. Set up / re-link with the `setup-memory` skill.

Why bother: Claude reads the curated `MEMORY.md` index instead of re-discovering the codebase each
session — you pay once to write a memory and save tokens on every future session. Each project keeps
its **own** memory here.

## Files

- `MEMORY.md` — the index loaded each session. One bullet per memory under its section
  (**Feedback / Reference / Project / User**), `- [file](file.md) — hook`. No memory content here.
- `<type>_<kebab-slug>.md` — one fact per file. `type ∈ feedback | project | reference | user`.
- `_TEMPLATE.memory.md` — copy this to start a new memory.

## Frontmatter

```markdown
---
name: <type>_<kebab-slug>
description: <one line — recall relevance>
metadata:
  node_type: memory
  type: feedback | project | reference | user
---
```

## type meanings

| type | holds |
|---|---|
| `user` | who the user is — role, expertise, durable preferences |
| `feedback` | how Claude should work here, **with the why** (corrections + confirmed approaches) |
| `project` | ongoing work, goals, constraints **not** derivable from code or git history |
| `reference` | pointers to external resources — URLs, dashboards, tickets |

## Rules

- One idea per file. Update the existing file rather than duplicating; delete memories that turn out wrong.
- Don't store what the repo already records (code structure, past fixes, git history, CLAUDE.md).
- Cross-link related memories with `[[other_name]]`.
- **Keep it public-safe — no secrets, tokens, or credentials.** Commit `memories/` to share with the team.
