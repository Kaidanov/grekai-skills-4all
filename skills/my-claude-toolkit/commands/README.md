# commands

This toolkit ships **no** custom slash-command markdown files (those would live
under `~/.claude/commands/`); built-in commands (e.g. `/model`, see
`../USAGE.md`) cover day-to-day slash usage. What lives here instead are
reusable **command-style PowerShell scripts** for project automation, kept so
they can be dropped into any repo's `.claude/scripts/`.

| Script | Typical source | What it does |
| --- | --- | --- |
| `scripts/commit-and-pr.ps1` | a project's `.claude/scripts/` | Create a timestamped `release-<ts>` branch, `git add`/commit, tag `rollback-<ts>`, push, then `gh pr create --fill --base main`. A one-shot "ship it" command. |
| `scripts/verify.ps1` | same | Gate: `pnpm lint` → `pnpm typecheck` → `pnpm test` → boot the dev server and probe `http://localhost:3000`. Exits non-zero on any failure. |

## Use

```powershell
powershell -ExecutionPolicy Bypass -File .\.claude\scripts\verify.ps1
powershell -ExecutionPolicy Bypass -File .\.claude\scripts\commit-and-pr.ps1
```

> `verify.ps1` assumes a `pnpm` project on port 3000; `commit-and-pr.ps1`
> assumes `gh` is authenticated and `main` is the base. Adjust per project. To
> turn either into a real slash command, wrap it in a `commands/<name>.md` that
> calls the script.
