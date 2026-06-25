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

## Log to the global daily trail (every window → one daily file)
After composing the report, append it to the shared daily log so **all** Claude windows on this machine accumulate one scannable TLDR trail per day:

1. Write the full report markdown to a temp file (use the session scratchpad).
2. Run (PowerShell):

   ```powershell
   & "$HOME\.claude\skills\tldr\scripts\Append-TldrTrail.ps1" -Path "<tempfile>" -Project "<repo>@<branch|cwd>" -Session "<short id, e.g. latest commit hash>"
   ```

The script appends to `~/.claude/tldr-trail/<YYYY-MM-DD>.md` under a **cross-process lock** — it waits up to 2s if another window is mid-write, steals a stale lock after 30s, and deletes the temp file when done. It also stamps the **real wall-clock elapsed since the previous entry** (the trustworthy time source). Do this on every TLDR; note the trail path in chat once per session.

## Notes
- Keep it to a short table + bullets. No subagents this batch? Say so rather than padding.
- The daily trail is the source of truth for **real** time-between-TLDRs; in-chat per-round time stays an estimate.
- **Honors a project-specific format.** If the current project defines its own TLDR/report format in its memory or docs (e.g. a `feedback_*` memory), follow that — this skill is the universal default and the on-demand trigger.
- Pairs with the `token-audit` skill: `/tldr` reports *actual spend this turn*; `/token-audit` targets the *always-on context baseline* (MCPs, hooks, skills, CLAUDE.md).
