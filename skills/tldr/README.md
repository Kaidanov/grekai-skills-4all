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
- The **report itself** needs no external tools, no network, no config — it only reads what's already
  in the session.
- Works best when your subagents return a `usage` block (tokens + duration) — those are the only
  numbers reported as exact.
- **For the daily trail log only:** PowerShell (Windows ships it; macOS/Linux can use `pwsh`). The
  bundled `scripts/Append-TldrTrail.ps1` appends each report to `~/.claude/tldr-trail/<date>.md`. If
  you don't want the trail, just skip that step — the in-chat report works on its own.

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

- **Original ask** — your initiating request for this batch, quoted back, so a `/tldr` late in a long
  session reminds you what you actually asked for.
- **Work statistics** — total tokens `(est)`, exact per-subagent token + duration breakdown, the
  **rounds** (user turns) and ~time/round, the **tools activated** this batch, and a small
  **components-used** table (what each subagent / tool / skill / hook did).
- **Reasoning (summary)** — 1–2 lines on the approach taken and why.
- **Q&A (self + user)** — the key questions this batch and how each resolved (decisions made
  autonomously vs. answered by you).
- **Done** — what shipped (with commit hashes where relevant).
- **To do** — what's left, in priority order.
- **Issues** — blockers / problems found.
- **Options** — concrete next choices.
- **New session?** — an explicit YES/NO recommendation (long transcripts are the biggest token sink).

## Daily trail log (every window → one file per day)

Reports accumulate into a **shared daily log** so *all* your Claude windows build one scannable TLDR
trail per day at `~/.claude/tldr-trail/<YYYY-MM-DD>.md`. Two layers feed it:

**1. Automatic per-turn heartbeat (no `/tldr` needed).** Wire `scripts/Log-TurnHeartbeat.ps1` as a
`Stop` hook in `~/.claude/settings.json` and *every* turn appends a compact one-liner
(`time · proj@branch · session · +Δmin · ask → gist`) — capturing **your prompt** plus a gist of the
reply, so the trail reconstructs what you asked each turn. The gap between heartbeats is the real
per-round wall-clock. The hook never throws and caps its stdin read at 3s, so it can't stall turn-end.

```jsonc
// ~/.claude/settings.json
"hooks": {
  "Stop": [
    { "hooks": [ { "type": "command",
      "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:\\Users\\<you>\\.claude\\skills\\tldr\\scripts\\Log-TurnHeartbeat.ps1\"" } ] }
  ]
}
```

> Ready-to-paste copy: [`examples/settings.stop-hook.json`](./examples/settings.stop-hook.json). After editing `settings.json`, reload the window (or restart the session) so the hook loads.

**2. Full report on `/tldr`.** When you run a full report, also append the whole thing:

```powershell
& "$HOME\.claude\skills\tldr\scripts\Append-TldrTrail.ps1" -Path "<tempfile>" -Project "<repo>@<branch>" -Session "<short id>"
```

- **Choose where it lives.** `-Scope global` (default) → `~/.claude/tldr-trail/`; `-Scope project` →
  `<repo-root>/.claude/tldr-trail/` (travels with the repo); `-TrailDir "<path>"` → explicit override.
- **Concurrency-safe.** An atomic lock means two windows finishing at once queue instead of
  clobbering the file; it waits up to 2s, steals a stale lock after 30s, and deletes the temp file.
- **Real time.** Each entry stamps the wall-clock elapsed since the previous one — the trustworthy
  time source (in-chat per-round time stays an estimate).
- **UTF-8, append-only, clickable.** Safe for em-dashes, Hebrew, emoji; the script prints the trail
  path so the assistant can link it (`file://` for the global log, a relative path when in-project).

## Notes

- **Honors a project-specific format.** If your repo defines its own report format in memory or docs,
  the skill follows it; otherwise it uses the universal default above.
- Pairs with the [`token-audit`](../token-audit/) skill: `/tldr` reports *actual spend this turn*;
  `/token-audit` trims the *always-on context baseline* (MCPs, hooks, skills, CLAUDE.md).
- Generic by design — no project, org, or user names — so it's safe to publish and reuse anywhere.
