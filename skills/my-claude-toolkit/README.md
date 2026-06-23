# my-claude-toolkit

The user's own, hand-authored Claude Code setup, imported from this PC for reuse
on other machines. Marketplace/vendor plugins are **excluded** (they reinstall
from their own marketplaces); only user-written artifacts live here.

See `SKILL.md` for the reinstall steps. This file is the **inventory +
provenance** record.

## Contents & provenance

Source paths below are shown generically — they point at where each item
**type** lives on a typical machine, not at any one person's folders.

| Item | Type | Typical source | Notes |
| --- | --- | --- | --- |
| `skills/subset-worktree/` | Skill | `~/.claude/skills/subset-worktree/` | Sparse cone-checkout worktree engine (`SKILL.md` + `New-SubsetWorktree.ps1`). The global copy is the canonical one. |
| `hooks/intake-issue-image.ps1` | Hook | a project's `.claude/scripts/` | `UserPromptSubmit` hook: saves pasted screenshots to `client/docs/issue-images/` and echoes markdown refs. Has a manual clipboard mode too. |
| `commands/scripts/commit-and-pr.ps1` | Command-script | a project's `.claude/scripts/` | Branch + commit + tag + push + `gh pr create`. |
| `commands/scripts/verify.ps1` | Command-script | a project's `.claude/scripts/` | lint → typecheck → test → dev-server boot probe (pnpm). |
| `monitor/usage-report.ps1` | Hook (Stop) | `~/.claude/scripts/` | Per-session token/cost + context-window footer; emits `{systemMessage}`. |
| `monitor/usage-dashboard.ps1` | Aggregator | `~/.claude/scripts/` | Cross-tool HTML cost dashboard (ccusage + per-project transcript scan). |
| `monitor/usage-counter.ps1` | Hook (new) | authored here | Lightweight CSV logger for Skill/SlashCommand/Agent invocations. |
| `monitor/usage-rank.ps1` | Aggregator (new) | authored here | Prints a ranked top-list from the counter CSV. |
| `monitor/analyze-history.ps1` | Analyzer (new) | authored here | One-off scan of `~/.claude/projects/**/*.jsonl` → the `USAGE.md` ranking. |
| `mcp/mcp.md` | MCP inventory | a canonical `.ai/mcp.json` + Claude Desktop config | Sanitized server list (env-var placeholders). |
| `USAGE.md` | Report | derived | Most-used skills / commands / subagents / MCP, with method + date range. |

## Referenced, not copied (already in this repo)

| Item | Where it lives | Typical source |
| --- | --- | --- |
| `handoff` skill | top-level `skills/handoff/` | `~/.claude/skills/handoff/` |
| 13-agent example dev roster (architect-overwatch, backend-dev, frontend-dev, devops-engineer, qa-test-engineer, security-specialist, ui-ux-designer, project-orchestrator, refactor-test-guardian, playwright-guardian, mapper-refactor-test, mapper-competitor-ux-research, tutorial-test-recording) | `skills/dev-rules-and-agents/agents/` | a project's `.ai/agents/` |

## Excluded (vendor / marketplace — not user-authored)

`vercel:*`, `telegram:*`, `israeli-bank-connector`, `israeli-grocery-price-intelligence`,
`ralph-loop`, `skill-creator`, `frontend-design`, `claude-md-management`,
`claude-code-setup`, `code-review`, `context7`, `csharp-lsp` — these are enabled
plugins under `~/.claude/plugins/` and reinstall from their marketplaces.

## Redactions

No secret values are committed here. Stripped / placeholdered: auth JWTs, SQL
Server passwords + remote host IPs, real database/project names, and any
per-project allow-list command secrets from `settings.json` /
`settings.local.json`. Details in `mcp/mcp.md` and `hooks/hooks.md`.

> The **real, filled config stays local.** Everything in this folder is a
> public, sanitized template — your machine's actual paths, database names, host
> IPs, and env-var *values* are private and must not be committed.
