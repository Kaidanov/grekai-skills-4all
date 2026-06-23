---
name: my-claude-toolkit
description: >-
  The user's portable, self-authored Claude Code setup — reusable skills,
  hooks, helper command-scripts, a sanitized MCP-server inventory, and a
  usage-monitor. Use when setting up Claude Code on a NEW machine, restoring the
  user's personal toolkit, re-adding their hooks/skills to settings.json, or
  reviewing which skills/subagents/commands they use most. Not a marketplace
  plugin: everything here was hand-written by the user and is safe to copy.
---

# My Claude Toolkit

A single bundle of the **user-authored** Claude Code artifacts found on their
PC, packaged so the same setup can be reinstalled on another machine without
re-deriving it. Vendor/marketplace plugins (`vercel:*`, `telegram:*`,
`israeli-*`, `ralph-loop`, `skill-creator`, etc.) are intentionally **excluded**
— those reinstall from their marketplaces.

## What's inside

| Folder | Contents |
| --- | --- |
| `skills/` | User-written skills not already top-level in this repo (`subset-worktree`). |
| `commands/scripts/` | Reusable PowerShell helper scripts (`commit-and-pr`, `verify`). |
| `hooks/` | Hook scripts + `hooks.md` (event/matcher/command to paste into `settings.json`). |
| `mcp/mcp.md` | Sanitized MCP-server inventory (names, purpose, required env vars — placeholders only). |
| `monitor/` | Usage monitor: a SessionEnd/Stop hook + aggregator + one-off history analyzer, `monitor/README.md` to install. |
| `USAGE.md` | Most-used ranking (skills / slash commands / subagents / MCP) derived from local transcripts. |
| `README.md` | Overview + provenance (where each item came from). |

Already-imported elsewhere in this repo (referenced, **not** duplicated):
- `handoff` skill → top-level `skills/handoff/`.
- The 13-agent example dev roster → `skills/dev-rules-and-agents/agents/`.

## Reinstall on a new machine

1. **Skills** — copy each folder under `skills/` to `~/.claude/skills/<name>/`
   (or into a project's `.claude/skills/`). `subset-worktree`'s engine script
   is invoked as `~/.claude/skills/subset-worktree/New-SubsetWorktree.ps1`.
2. **Command scripts** — drop `commands/scripts/*.ps1` into a project's
   `.claude/scripts/` and run them with
   `powershell -ExecutionPolicy Bypass -File .\.claude\scripts\<name>.ps1`.
3. **Hooks** — copy `hooks/*.ps1` to the target location, then add the matching
   hook block from `hooks/hooks.md` to `~/.claude/settings.json` (global) or a
   project `.claude/settings.json`.
4. **Usage monitor** — copy `monitor/*.ps1` to `~/.claude/scripts/`, then add
   the `Stop` (and optional `SessionEnd`) hook from `monitor/README.md`.
5. **MCP** — recreate servers from `mcp/mcp.md`. Set every `${env:NAME}` as a
   Windows User environment variable first; never hardcode a secret.

## Provenance & safety

Every item lists its typical source path in `README.md`. All secrets (auth JWTs,
DB passwords, bot tokens, connection strings) are stripped and replaced with
`${env:NAME}` / `<REDACTED>` placeholders. The **real, filled config stays
local** — this folder is a public, sanitized template. See `mcp/mcp.md` and
`hooks/hooks.md` for the redaction notes.
