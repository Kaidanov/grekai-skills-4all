# Hooks

User-authored Claude Code hooks found on this PC, sanitized for reuse. Each
entry gives the **event**, **matcher**, and the exact `command` to paste into a
`settings.json` `"hooks"` block. Paths assume the script sits where noted; adjust
to your machine.

## 1. `intake-issue-image.ps1` — UserPromptSubmit

**Purpose:** when you paste a screenshot into the prompt, save it to
`client/docs/issue-images/` with auto-numbering (`I1.png`, `I2.png`, …) and echo
back a markdown reference so Claude can cite it. Also runs as a manual clipboard
saver when invoked directly.

**Source:** a project-level `.claude\scripts\intake-issue-image.ps1`. Place it
under a project's `.claude\scripts\`.

**Install** — project `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \".claude\\scripts\\intake-issue-image.ps1\""
          }
        ]
      }
    ]
  }
}
```

> The image-dir path (`client/docs/issue-images/`) is hard-coded relative to the
> repo root inside the script — change `Get-IssueImagesDir` for a different layout.

## 2. `usage-report.ps1` — Stop

Token/cost + context-window footer per session. Documented with its install
snippet in `../monitor/README.md` (it lives under `monitor/`).

## 3. `usage-counter.ps1` — PostToolUse / SessionEnd (the usage monitor)

Lightweight CSV logger for Skill / SlashCommand / Agent invocations. Install
snippet in `../monitor/README.md`.

## Redaction notes

- A global `~/.claude/settings.json` `permissions.allow` array can contain **real
  secrets** (auth JWTs, DB passwords embedded in allow-listed commands, project
  refs). **Never** copy those into a shared/public repo — import only the
  reusable hook *structure* above and recreate permissions locally.
- `settings.local.json` files (which may hold `set PASSWORD=...` style entries)
  must **not** be imported into a public repo.
