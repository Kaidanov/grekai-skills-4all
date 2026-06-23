# monitor — usage tracking

Two layers, both user-runnable and re-installable:

1. **Cost layer** (imported, already in use) — token/cost per session + a
   cross-tool HTML dashboard.
2. **Invocation layer** (added here, KISS) — a CSV counter for Skill /
   SlashCommand / Agent fires + a ranker. This is the "usage-monitor" the
   toolkit ships so the most-used ranking stays current on any machine.

## Files

| File | Role |
| --- | --- |
| `usage-report.ps1` | **Stop hook.** Reads the session transcript, sums tokens, prices them (Opus/Sonnet/Haiku tiers), and emits a one-line `{systemMessage}` footer with cost + context-window % free. |
| `usage-dashboard.ps1` | **Aggregator.** Builds a self-contained HTML dashboard (`~/.claude/usage-dashboard.html`): cross-tool totals from `ccusage`, per-project + per-session drill-down from `~/.claude/projects/`. Run with `-Open`. |
| `usage-counter.ps1` | **PostToolUse hook.** Appends one row per Skill/SlashCommand/Agent invocation to `~/.claude/usage-log.csv`. |
| `usage-rank.ps1` | **Aggregator.** Prints a ranked top-list per category from that CSV. |
| `analyze-history.ps1` | **One-off analyzer.** Scans existing transcripts to produce the historical ranking in `../USAGE.md` (use it to bootstrap before the counter has data). |

## Install the invocation monitor (the simple, recommended one)

Copy `usage-counter.ps1` to `~/.claude/scripts/`, then add this to
`~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Skill|Agent|Task|SlashCommand",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\scripts\\usage-counter.ps1\""
          }
        ]
      }
    ]
  }
}
```

> The `matcher` is a regex on the tool name — only Skill / Agent / Task /
> SlashCommand fire the hook, so the CSV stays signal-dense. If your harness
> doesn't expand `%USERPROFILE%` in hook commands, use the absolute path.

Then rank anytime:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.claude\scripts\usage-rank.ps1" -Top 10
```

## Install the cost footer (optional, already in the user's global config)

Copy `usage-report.ps1` to `~/.claude/scripts/` and add:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\scripts\\usage-report.ps1\""
          }
        ]
      }
    ]
  }
}
```

Dashboard (on demand):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.claude\scripts\usage-dashboard.ps1" -Open
```

`usage-dashboard.ps1` needs `ccusage` on PATH for the cross-tool totals; the
per-project section works without it. Chart.js is vendored locally on first run
(no CDN, no keys).
