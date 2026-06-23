---
name: subset-worktree
description: >-
  Create a git worktree that materializes ONLY selected folders of a large
  solution/monorepo via cone-mode sparse-checkout, instead of checking out the
  whole tree. Use when the user wants "a worktree with only the changed folders",
  "just the WebAPI/tests folder in its own directory", "extract part of the repo
  to C:\\...", "sparse worktree", or to pull one release line's sub-area into a
  separate folder (e.g. MyApp_1.2.3_webapi). Also verifies the version
  stamp ("is this really on 1.2.3?") of the materialized projects.
---

# Subset worktree (sparse, single sub-area)

A **worktree** checks out a branch into a second folder that shares the one repo
(`.git`). A **cone sparse-checkout** then materializes only the folders you name
(plus root files) — so a 2 GB solution becomes an 11 MB WebAPI-only folder while
staying fully git-aware (history, commit, push all work normally). Sparse hides
files from disk; it never deletes them from the branch or commits.

## Fast path — run the engine script

The deterministic engine is `New-SubsetWorktree.ps1` (next to this file). Prefer
it over issuing the git commands by hand — it auto-detects folders, is
idempotent, and prints a fit/version report. Do **not** spin up an LLM subagent
for the run; the script is the optimization.

```powershell
& "$HOME\.claude\skills\subset-worktree\New-SubsetWorktree.ps1" `
    -RepoPath  C:\Projects\MyApp `
    -Branch    feature/1234-api-docs `
    -DestPath  C:\Projects\MyApp_1.2.3_webapi `
    -Folders   WebApi,WebApiDocs,UnitTests,IntegrationTests `
    -ExpectVersion 1.2.3
```

Omit `-Folders` to **auto-detect** the changed top-level dirs vs `-BaseBranch`
(default `origin/dev`). Use `-Force` to drop and recreate an existing dest.

## Manual equivalent (if the script is unavailable)

```powershell
git -C <repo> worktree add --no-checkout <dest> <branch>
git -C <dest> sparse-checkout init --cone
git -C <dest> sparse-checkout set <folderA> <folderB> ...
git -C <dest> checkout
```

## Discovering scope cheaply (low token)

To find which folders a branch actually changed, use plain git (not file reads):

```powershell
$base = git -C <repo> merge-base <branch> origin/dev
git -C <repo> diff --name-only $base <branch> |
    ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique
```

Only delegate to the read-only **Explore** subagent when the folder layout is
unknown and needs interpreting — for a known diff, the git one-liner is cheaper.

## Verifying "is it really on version X?"

The script greps `AssemblyVersion(...)` / `<Version>` under the materialized
folders and warns if none match `-ExpectVersion`. To confirm the branch is
actually *based on* a release line (not just labelled):

```powershell
# Are the release commits contained in the branch?
git -C <repo> merge-base --is-ancestor origin/releases/4.12.1.36 <branch>
#   exit 0 = branch is built on top of that release; non-zero = it is NOT.
git -C <repo> show <branch>:<proj>/Properties/AssemblyInfo.cs | Select-String AssemblyVersion
```

A folder *named* `..._4.12.1.36_...` does not imply the code is on that release —
always check the merge-base and the stamp.

## Cleanup

```powershell
git -C <repo> worktree remove <dest>      # add --force if it has local edits
git -C <repo> worktree prune
```

## Why no hook for this

This is an explicit, on-demand action with no recurring trigger event, so a
settings.json hook (which fires automatically on session/tool events) is the
wrong primitive and only adds overhead. This skill + script is the minimal-token
entry point. A hook would only make sense to *enforce* something automatically
(e.g. block writing outside the sparse cone) — not to create the worktree.
