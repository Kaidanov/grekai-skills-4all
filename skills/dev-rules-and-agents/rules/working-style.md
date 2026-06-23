# Working Style (session hygiene & proof)

How a session should run, regardless of project. These rules are generalized from repeated
feedback — they encode "done = proven", token economy, and clean handoffs.

## Done = proven, not written
- Never report a task done without an evidence artifact — test output, an HTTP/CLI response, or a
  screenshot of the running app. "Compiles" / "code written" is **not** "works". State what was verified.
- Run the app or the narrowest real proof immediately after the first substantive edit.

## Token economy
- Delegate broad search/exploration to subagents — they return conclusions, not file dumps.
- Don't preload skills/MCPs. Reuse cached context; avoid re-reading files already seen.
- Start from the nearest concrete anchor (file, spec, failing command) and make the smallest grounded edit first.
- Prefer exact searches over repeated exploratory ones; prefer targeted file reads over broad repo tours.
- Use one primary agent unless the task proves it needs another (see `../agents/`).

## Handoffs
- Hand off **only when work is unfinished.** Leave a dated note (Next / Open-questions-&-gotchas /
  Ownership) so the next session resumes without re-research; read it before starting.
- If the work is complete, **don't** create a handoff doc — record what shipped in the commit message and close.

## Commits
- Commit per logical unit, small + frequent; the message states what changed **and the proof**.
- Never include `Co-Authored-By` lines unless explicitly asked.
- Branch before committing if you're on the default branch. Commit/push only when asked.

## UI specifics (when applicable)
- Modal dialogs must never have dead whitespace. Use flex layout rules (`flex-1` for growing panels,
  `shrink-0` for fixed) — never fixed `clamp()` heights on panels that should grow.

## Don't over-engineer
- Break god-files, remove dead code, never add code without a real need.
- When you extract a util/hook from a god-file, replace the original in the **same** session — don't leave both.

## Completion report (TLDR)
On each completion give a short TLDR: tokens (total estimate + per-subagent), time, components used
(which agents/tools/skills/hooks did what), what's done, what's left, issues, and options.
