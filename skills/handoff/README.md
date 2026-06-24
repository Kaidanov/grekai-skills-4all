# handoff

Package the current working session into a **handoff** so the **next** session
resumes with zero re-research. It produces a dated handoff doc, a standalone
copy-paste resume prompt, and a metrics row — and syncs the shared coordination
file when a concurrent session is active.

## Why

Long or context-bound sessions lose state when they end. Re-deriving "where were
we, what's next, what's the safe approach, what proves it works" wastes tokens
and time. This skill captures all of that **once**, in linkable artifacts, so the
next session (or a teammate) continues cold.

## When to use

Invoke at final-context steps — when budget/context is nearly exhausted, or when
the user says: *"handoff"*, *"prepare next session"*, *"hand off"*, *"wrap up the
session"*, *"switch to next session"*, *"create a resume prompt"*. Works in any
repo; it's project-agnostic.

## Contents

| File | Purpose |
| --- | --- |
| `SKILL.md` | The full skill instructions (gather → write-doc → resume-prompt → log → commit). Project-agnostic. |
| `README.md` | This overview: what/why/when + how it works. |

## What it produces (per run, under the project's `docs/handoffs/` folder)

1. `<YYYY-MM-DD>-<scope>-handoff.md` — the handoff doc, including a **Session
   metrics** block.
2. `<YYYY-MM-DD>-<scope>-resume-prompt.md` — a standalone, copy-paste resume
   prompt so you can stop now and continue later.
3. `session-log.csv` — one **appended** row per session (created with a header if
   missing) for tracking progress/cost over time.

## How it works (the pipeline)

1. **Gather** (read-only, fast) — current branch + recent commits, working-tree
   status, active trackers/plan/coordination docs, the todo list, the last known
   build/test result, memory files touched this session, and exact per-subagent
   token/duration metrics from each subagent's returned `usage` block.
2. **Write the handoff doc** — TL;DR state, Done (with commit hashes), In
   progress/locked, Next (prioritized, with a safe approach + proof gate),
   Rejected/deferred, Key facts/gotchas (linked `file:line`), How to verify
   (commands + green baseline), Coordination, Rules, and a Session-metrics block.
3. **Append `session-log.csv`** — a single metrics row (pure append, never a
   rewrite, since a concurrent session may have added rows).
4. **Write the resume-prompt** — one fenced, self-contained block the user pastes
   into the next session; it points at the handoff/coordination/tracker/memory
   paths, states the immediate next task + safe approach + proof gate, and
   restates the project's hard rules.
5. **Commit + report** — commit the three artifacts and show the user the paths +
   the resume prompt.

### Principles it honors

- **done = proven.** It records what was actually verified, not what was merely
  written. Numbers are never fabricated — totals the harness doesn't expose are
  recorded as `n/a (estimate)`.
- **Link, don't duplicate.** It links to existing docs and `file:line` rather
  than pasting large code.
- **Concurrent-safe.** Appends to the shared coordination file and commits small
  and often.

See `SKILL.md` for the exact step-by-step instructions and field formats.
