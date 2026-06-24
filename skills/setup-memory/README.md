# Setup Memory — memory-in-repo

Claude's per-project memory normally lives **outside** the repo at
`~/.claude/projects/<slug>/memory/`, so it is never versioned or shared. This skill moves
it **into** the repo at `memories/repo/` and links it back with a directory **junction**, so
the curated project knowledge is:

- **Committed + team-shared** — clone the repo, run the setup, and Claude instantly has the
  project's context.
- **Token-efficient** — Claude reads a tight, hand-maintained `MEMORY.md` index instead of
  re-discovering the codebase every session. Pay once to write a memory, save tokens on every
  future session.
- **Just files** — adding/updating memory is a normal file edit in the repo; the junction makes
  it live immediately.

## Install

This skill is a script you run, so install it **globally** into your Claude skills folder — it
is reused across every project:

```bash
npx degit Kaidanov/grekai-skills-4all/skills/setup-memory ~/.claude/skills/setup-memory
```

> The `Run` command below invokes `~/.claude/skills/setup-memory/scripts/Setup-Memory.ps1`, so
> a global install is required here. (No `npx`? The
> [skill page](https://grekai-skills-4all.vercel.app/skill?id=setup-memory) shows a
> `git sparse-checkout` alternative.)

## Use it

Run the script from your repo root — once per project you want memory in:

```powershell
& "$HOME\.claude\skills\setup-memory\scripts\Setup-Memory.ps1" -ProjectPath .
# -ProjectPath defaults to the current directory. Add -WhatIf to preview, -Force to re-seed templates.
```

Idempotent and **no admin required** (a directory junction, not a symlink). The script:

1. Computes the project **slug** from the path the same way the harness does: lowercase the drive
   letter, then turn `:` `\` `/` `.` `_` and spaces into `-` (e.g. `C:\Projects\Foo.Bar_v2` →
   `c--Projects-Foo-Bar-v2`).
2. Creates `<repo>/memories/repo/` and a `MEMORY.md` index skeleton (**Feedback / Reference /
   Project / User**) if missing.
3. If `~/.claude/projects/<slug>/memory` already exists as a **real folder**, migrates its files
   into `memories/repo/` first (never overwrites a newer file), then removes the empty folder.
4. Replaces it with a junction: `~/.claude/projects/<slug>/memory` → `<repo>/memories/repo`.
5. Seeds `_TEMPLATE.memory.md` + a `README.md` if missing. Prints slug, paths, and migrated-file
   count.

## Why the memory links **per-project**, not to one global folder

Two things live in two different places here — don't conflate them:

- **The skill** (`setup-memory`) is installed **globally** at `~/.claude/skills/` because it's a
  generic tool you reuse everywhere.
- **The memory it links** is **per-project**: the junction repoints *this project's* memory path
  (`~/.claude/projects/<slug>/memory`) at *this repo's* `memories/repo/`. Each repo carries its own.

We deliberately do **not** point every project at a single shared global memory folder. Per-project
linkage wins on every axis that matters:

- **Recall quality & token cost.** Claude loads the project's `MEMORY.md` every session. If one
  global store mixed facts from all your repos, recall would surface irrelevant context and you'd
  pay tokens to load the wrong project's notes every time. Per-project keeps the index tight and
  on-topic.
- **Travels with the code.** The memory describes *this* codebase — its decisions, gotchas,
  constraints. Keeping it in the repo means it moves with clones, branches, and PRs. Clone on a new
  machine, run the script, and the memory is already there — nothing to copy out of `~/.claude`.
- **Versioned & reviewable.** Memory edits ride the same git history as the code: you can see when
  and why a fact changed, branch it, and review it in a PR. A global folder under `~/.claude` is
  unversioned and lives on exactly one machine.
- **Team-shared at the right boundary.** Committing `memories/` shares context with exactly the
  people who clone that repo — no more, no less. A machine-wide store can't be shared per-project.
- **Isolation & safety.** A project's notes stay inside that project's boundary instead of leaking
  into a global store that every other project (and agent) on the machine can read.

The link is a **junction, not a copy**, so there's a single source of truth (the repo) and edits are
live immediately — and because it's a junction rather than a symlink, **no admin rights are needed**.

## Memory file convention (what goes in `memories/repo/`)

- One fact per file, named `<type>_<kebab-slug>.md` where **type ∈ feedback | project | reference |
  user**.
- `MEMORY.md` is the index loaded every session: one bullet per file under its section,
  `- [file](file.md) — hook`. Never put memory content in `MEMORY.md`.
- **type meanings:** `user` = who the user is / preferences · `feedback` = how Claude should work
  here (with the why) · `project` = ongoing work/goals/constraints not derivable from code or git ·
  `reference` = pointers to external resources.

The full frontmatter format and field rules are in [`SKILL.md`](./SKILL.md).

## Notes

- Commit `memories/` to share with the team. Keep it **public-safe** — no secrets, tokens, or
  credentials.
- Re-run any time; safe and idempotent. Use `-WhatIf` to see what it would change.
- Generic by design (no hardcoded user, org, or project names) so it can be published and reused
  anywhere.
