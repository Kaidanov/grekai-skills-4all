---
name: handoff
description: >
  Package the current working session into a handoff so the NEXT session resumes
  with ZERO re-research. Use at final context steps, when budget/context is nearly
  exhausted, or when the user says "handoff", "prepare next session", "hand off",
  "wrap up the session", "switch to next session", "create a resume prompt". Works
  in any repo. Produces a dated handoff doc, a standalone resume-prompt md, and
  appends a session-log.csv metrics row; syncs the shared coordination file if a
  concurrent session is active.
---

# Session Handoff

Goal: capture everything the next session needs to continue THIS work cold, with **zero
re-research**, plus a metrics row so progress/cost is trackable over time. Link to existing
docs — don't duplicate. Honor done=proven: state what was actually verified.

Artifacts (under the project's docs/handoffs folder):
1. `<YYYY-MM-DD>-<scope>-handoff.md` — handoff doc (incl. a Session metrics block).
2. `<YYYY-MM-DD>-<scope>-resume-prompt.md` — standalone copy-paste resume prompt (so you can stop now and continue later).
3. `session-log.csv` — append one row (create with header if missing).

## 1. Gather (read-only, fast — don't re-run heavy builds unless state is unknown)
- `git rev-parse --abbrev-ref HEAD` + `git log --oneline -25` — THIS session's commits.
- `git status --short` — uncommitted/concurrent state.
- Active trackers/plan/coordination docs + the current todo list.
- Last known build/test result from the conversation (state it).
- **Memory saved this session** — list memory files created/updated.
- **Metrics** — exact per-subagent tokens+duration from each subagent's returned `usage` block (and any workflow `usage`:
  agent_count / subagent_tokens / duration_ms). The harness does NOT expose per-session total tokens or wall-clock to
  the model — record those as `n/a (estimate)`; NEVER fabricate numbers.

## 2. Write the handoff doc
Sections: **TL;DR state · Done (commit hashes) · In progress/locked · Next (prioritized + safe approach + proof gate) ·
Rejected/deferred (reasons) · Key facts/gotchas (link file:line) · How to verify (commands + green baseline) ·
Coordination · Rules**. Plus a **Session metrics** block: completed / left / commits / subagent_tokens (exact) /
total tokens + time (`n/a estimate`) / memory saved.

## 3. Append the session-log.csv row
File: `<docs>/handoffs/session-log.csv`. Header (create if missing):
`date,session,branch,completed,left,commits,subagent_tokens_exact,total_tokens_est,duration,memory_saved,handoff_doc,resume_prompt,notes`
**APPEND** (`>>`), never rewrite — a concurrent session may have added rows. Quote any field containing commas.

## 4. Write the standalone resume-prompt md
A single fenced block the user pastes into the next session. It MUST: point to the handoff + coordination + tracker +
memory + session-log paths (read first); state the immediate next task + safe approach + proof gate; restate the
project's hard rules (behavior-preserving refactors, verify-before-merge, typing/lint rules, file-size limits,
commit-per-item, typecheck+test+build gate, coordinate via the shared file); be self-contained.

## 5. Commit + report
Commit the handoff doc, resume-prompt md, and session-log.csv. Show the user the paths + the resume prompt.
Keep it scannable; link file:line, don't paste large code.

## TLDR cadence (between handoffs)
A full handoff is for session end. Between handoffs, keep the user oriented:
- **Every completion** — a tight TLDR memo: work-statistics (per-subagent tokens+duration exact; total tokens/time as estimates, `n/a` where not measurable) · done · to do (prioritized) · issues · options.
- **At least every 5–10 min of continuous work** — a one-line pulse: done / todo / time-or-budget left.
- **New-session recommendation** — in each TLDR, say plainly whether to start a fresh session now. Recommend YES when the transcript is long/old (token cost scales with transcript size — long sessions are the biggest sink), the remaining task is cleanly scoped, and the needed context is already in `memories/repo/` (or a handoff doc). Name what the new session should pick up.

## Notes
- Concurrent session: append to the shared coordination file (pure append, don't overwrite); commit small + often.
- Compiler/typecheck caches lie after file moves/renames — the **build** is the real gate.
