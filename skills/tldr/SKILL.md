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
- **Time** — `~<N> min (est)`; sub-step durations exact only where a subagent reported `duration_ms`.
- **Components used** — small table:

| Component | Type | What for | Tokens | Duration |
|-----------|------|----------|--------|----------|
| <subagent name> | subagent | <purpose> | <exact from usage> | <exact ms> |
| <tool names> | tools | <what for> | n/a (total only) | n/a |
| <skill/hook> | skill/hook | <what fired, why> | n/a | n/a |

**Done** — what shipped, with commit hashes where relevant.
**To do** — remaining work, priority order.
**Issues** — problems / blockers found.
**Options** — concrete choices the user can pick next.
**New session?** — explicit YES/NO. Recommend **YES** when the transcript is long/old (transcript size is the biggest token sink), the remaining task is cleanly scoped, and its context is already captured durably (e.g. project memory/docs). Say so plainly and name what the new session should pick up.

## Notes
- Keep it to a short table + bullets. No subagents this batch? Say so rather than padding.
- **Honors a project-specific format.** If the current project defines its own TLDR/report format in its memory or docs (e.g. a `feedback_*` memory), follow that — this skill is the universal default and the on-demand trigger.
- Pairs with the `token-audit` skill: `/tldr` reports *actual spend this turn*; `/token-audit` targets the *always-on context baseline* (MCPs, hooks, skills, CLAUDE.md).
