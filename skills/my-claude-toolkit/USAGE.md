# USAGE — most-used ranking (method + sample shape)

Which Claude Code building blocks you actually invoke most, derived from your
own local session transcripts. This file documents the **method** and shows a
**representative sample shape** — the numbers below are illustrative; re-run the
analyzer to get your own.

## Method & sample

- **Source:** `%USERPROFILE%\.claude\projects\**\*.jsonl` — your local Claude
  Code session transcripts.
- **Sample size (example run):** ~140 transcript files, ~80 MB, across ~10
  project folders; ~16k tool-use / command lines parsed.
- **Date range:** whatever window your transcripts span (e.g. ~19 days).
- **Tool:** `monitor/analyze-history.ps1` (re-runnable). It counts `Skill`
  tool_use (`input.skill`), `Agent` tool_use (`input.subagent_type`, the
  subagent dispatch primitive — the older `Task` name is also handled),
  `<command-name>/…</command-name>` user entries for slash commands, and
  `mcp__*` tool_use for MCP calls.
- **Caveat:** in this harness most slash-command and skill *triggers* are not
  logged as discrete tool_use blocks (they expand inline), so those counts are a
  floor, not the full picture. Subagent (`Agent`) and MCP counts are reliable.

## Top subagents (`subagent_type`) — most reliable signal

Representative shape (your roster names will differ):

| Rank | Subagent | Count |
| --- | --- | --- |
| 1 | `Explore` (built-in read-only) | 36 |
| 2 | `<your-refactor-test-agent>` | 9 |
| 3 | `general-purpose` | 7 |
| 4 | `<your-guardian-agent>` | 6 |
| 5 | `<your-architect-agent>` | 2 |

Total subagent dispatches in the sample: **~61**. Read-only exploration
(`Explore`) plus a project's refactor/test guardians typically dominate —
consistent with a custom agent roster being the workhorse.

## Top skills (`Skill` tool_use)

| Rank | Skill | Count |
| --- | --- | --- |
| 1= | `subset-worktree` | 1 |
| 1= | `handoff` | 1 |
| 1= | `update-config` | 1 |
| 1= | `<other-skill>` | 1 |

Only a handful of skill invocations are logged as tool_use blocks in a typical
window (others expand inline and aren't separately recorded). User-authored
skills like `subset-worktree` and `handoff` tend to surface here.

## Top slash commands (`<command-name>`)

| Rank | Command | Count |
| --- | --- | --- |
| 1 | `/model` | 9 |

`/model` (switching model tiers) is often the only slash command that surfaces
as a discrete logged entry.

## Top MCP tools (`mcp__*`)

| Rank | Tool | Count |
| --- | --- | --- |
| 1 | `<some mcp__* call>` | 1 |

MCP traffic is usually light in the local transcripts even when many servers are
*configured* (see `mcp/mcp.md`) — much DB/CLI work goes through allow-listed
shell calls instead, which don't show up as `mcp__*` tool_use.

## Takeaway

The leverage is in **subagents** (led by `Explore` and a project's refactor/test
agents) far more than in slash commands or MCP. The `monitor/` counter going
forward captures skill/command/agent fires explicitly (not just what the
transcript happens to log) for a cleaner ranking on any machine.
