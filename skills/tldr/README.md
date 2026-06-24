# TLDR — end-of-turn status report

A one-command status memo for the **batch of work just finished**. Type `/tldr` and the
assistant emits a tight, scannable report: how many tokens and how long it spent, which
components (subagents / tools / skills / hooks) did the work, what shipped, what's left,
any blockers, the choices you can make next, and whether to start a fresh session.

It exists so you can **decide the next step without re-reading the transcript** and keep an
eye on token + time spend — the two things that actually cost you.

The golden rule is **never fabricate numbers**: per-subagent tokens and durations are reported
*exactly* (read from each subagent's `usage` block), while totals and wall-clock are clearly
marked `(est)`, and anything the harness can't measure (per-tool / per-skill token counts) is
marked `n/a`.

## Prerequisites

- An agent host that supports skills — Claude Code (CLI or IDE extension) or a compatible runner.
- **No external tools, no network, no config.** It only reads what's already in the session.
- Works best when your subagents return a `usage` block (tokens + duration) — those are the only
  numbers reported as exact.

## Install

You want status reports everywhere, so install it **globally**:

```bash
npx degit Kaidanov/grekai-skills-4all/skills/tldr ~/.claude/skills/tldr
```

Or per-project, to share it with a repo's team:

```bash
npx degit Kaidanov/grekai-skills-4all/skills/tldr .claude/skills/tldr
```

> **After installing, reload.** A skill added mid-session does **not** hot-reload into the
> slash-command picker. In VS Code: `Ctrl+Shift+P → "Developer: Reload Window"` (or restart the
> session). Then `/tldr` appears.

## Use it

Type `/tldr` — or just ask for a "status", "wrap-up", or "TLDR". You get:

- **Work statistics** — total tokens `(est)`, exact per-subagent token + duration breakdown, and a
  small **components-used** table (what each subagent / tool / skill / hook did).
- **Done** — what shipped (with commit hashes where relevant).
- **To do** — what's left, in priority order.
- **Issues** — blockers / problems found.
- **Options** — concrete next choices.
- **New session?** — an explicit YES/NO recommendation (long transcripts are the biggest token sink).

## Notes

- **Honors a project-specific format.** If your repo defines its own report format in memory or docs,
  the skill follows it; otherwise it uses the universal default above.
- Pairs with the [`token-audit`](../token-audit/) skill: `/tldr` reports *actual spend this turn*;
  `/token-audit` trims the *always-on context baseline* (MCPs, hooks, skills, CLAUDE.md).
- Generic by design — no project, org, or user names — so it's safe to publish and reuse anywhere.
