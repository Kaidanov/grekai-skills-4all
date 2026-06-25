---
name: tldr
description: Produce an end-of-turn TLDR status report for the current batch of work — tokens used (total estimate + exact per-subagent), time, components used, done, to-do, issues, options, and a fresh-session recommendation. Use when the user types /tldr, asks for a "status", "TLDR", "wrap-up", "summary of what you did", or a work-statistics report.
---

# /tldr — End-of-turn status report

Emit a tight, scannable status memo for the work done **this turn / this batch**, so the user can decide the next step without re-reading the transcript and can track token + time spend. This is the chat-level summary; detailed write-ups belong in `.md` files, not here. Never omit the work-statistics block.

## Hard rules (measurability — never fabricate)
- **Per-subagent tokens + duration are EXACT** — read them from each subagent's returned `usage` block (already in context; do not re-run anything). If a workflow/audit returned a `usage` block (agent_count, subagent_tokens, duration_ms), use those numbers.
- **Total tokens and wall-clock are NOT exposed to the model** — report them as estimates and label `(est)`.
- **Per-tool / per-skill / per-hook token counts are NOT itemizable** — mark them `n/a`. Never invent them.
- Gather as you go from what's already in context — near-zero cost, not a separate analysis pass.

## Report format

**TLDR — <one-line of what this batch was>**

**Work statistics**
- **Tokens** — `~<N>k total (est)`; per-subagent breakdown below (exact).
- **Time** — `~<N> min (est)` total; sub-step durations exact only where a subagent reported `duration_ms`. Real wall-clock between TLDRs is stamped in the daily trail (see below).
- **Rounds** — `<N> rounds (user turns) this batch · ~<t> min/round (est)`. Count the user turns in the batch; per-round wall-clock is an estimate (not exposed to the model) — the trail timestamps are the real source.
- **Tools activated** — comma-separated list of every tool / skill / subagent type used this batch (e.g. `Bash, Edit, Read, Workflow, gh`).
- **Components used** — small table:

| Component | Type | What for | Tokens | Duration |
|-----------|------|----------|--------|----------|
| <subagent name> | subagent | <purpose> | <exact from usage> | <exact ms> |
| <tool names> | tools | <what for> | n/a (total only) | n/a |
| <skill/hook> | skill/hook | <what fired, why> | n/a | n/a |

**Reasoning (summary)** — 1–2 lines on the approach/path taken (what you decided and why), not a replay of every step.
**Q&A (self + user)** — the key questions this batch and how each resolved, one per line: `Q: … → A: … [self|user]`. Include decisions you made autonomously (`self`) and anything the user answered (`user`). Write `None` if trivial.

**Done** — what shipped, with commit hashes where relevant.
**To do** — remaining work, priority order.
**Issues** — problems / blockers found.
**Options** — concrete choices the user can pick next.
**New session?** — explicit YES/NO. Recommend **YES** when the transcript is long/old (transcript size is the biggest token sink), the remaining task is cleanly scoped, and its context is already captured durably (e.g. project memory/docs). Say so plainly and name what the new session should pick up.

## Log to the daily trail (every window → one daily file)
Two layers feed the same daily log so you get a full picture:

- **Automatic (every turn):** a `Stop` hook (`scripts/Log-TurnHeartbeat.ps1`, wired in `~/.claude/settings.json`) appends a compact one-line **heartbeat** — `time · proj@branch · session · +Δmin · gist` — on *every* turn, with no `/tldr` needed. The gap between heartbeats is the real per-round wall-clock.
- **Manual (rich report):** when you emit a full `/tldr`, also append the whole report so it's preserved in the trail.

After composing a `/tldr` report:
1. Write the full report markdown to a temp file (session scratchpad).
2. Run (PowerShell):

   ```powershell
   & "$HOME\.claude\skills\tldr\scripts\Append-TldrTrail.ps1" -Path "<tempfile>" -Project "<repo>@<branch>" -Session "<short id>"
   ```

**Where it saves (`-Scope`):**
- `-Scope global` (default) → `~/.claude/tldr-trail/<YYYY-MM-DD>.md` (all windows aggregate here).
- `-Scope project` → `<repo-root>/.claude/tldr-trail/<YYYY-MM-DD>.md` (travels with the repo). Use when the user wants the trail in the project.
- `-TrailDir "<path>"` → explicit override.

The script appends under a **cross-process lock** (waits ≤2s if another window is writing, steals a stale lock after 30s), is UTF-8/unicode-safe, stamps **real wall-clock since the previous entry**, deletes the temp file, and **prints the trail file path** (use it for the link below).

**Always give a clickable link to the trail in chat** so it opens even though it lives outside the project:
- Global / outside the workspace → `file://` URI: `[~/.claude/tldr-trail/<date>.md](file:///C:/Users/<you>/.claude/tldr-trail/<date>.md)`
- In-project (`-Scope project`) → relative path: `[.claude/tldr-trail/<date>.md](.claude/tldr-trail/<date>.md)`

## Notes
- Keep it to a short table + bullets. No subagents this batch? Say so rather than padding.
- The daily trail (heartbeats + reports) is the source of truth for **real** time-between-turns; in-chat per-round time stays an estimate.
- **Honors a project-specific format.** If the current project defines its own TLDR/report format in its memory or docs (e.g. a `feedback_*` memory), follow that — this skill is the universal default and the on-demand trigger.
- Pairs with the `token-audit` skill: `/tldr` reports *actual spend this turn*; `/token-audit` targets the *always-on context baseline* (MCPs, hooks, skills, CLAUDE.md).
