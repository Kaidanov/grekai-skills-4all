# daily-cv profile — your single source of truth

This folder holds the **profile**: the one place that stores who you are, where you
worked, and which numbers are true. The CV / cover-letter / PDF generators read from
here. Nothing personal is committed to Git.

## Files

| File | Committed? | Purpose |
|---|---|---|
| `PROFILE.template.json` | yes | Blank template with placeholders + inline `_comment_*` hints. Copy it to start. |
| `PROFILE.example.json` | yes | A fully-filled **fictional** example (Jane Doe) so you can see the complete shape and run the generators with zero setup. Contains no real person. |
| `PROFILE.json` | **no — gitignored** | **Your** real, filled profile. The generators prefer this file. Create it locally; it is never committed. |
| `.gitignore` | yes | Ignores `PROFILE.json`, `*.local.*`, and generated `out/`, `*.docx`, `*.pdf`. |

## How the generators choose a profile

The shared loader (`../scripts/profile_loader.py`) resolves the profile in this order:

1. A path given via the `--profile` CLI flag or the `DAILY_CV_PROFILE` environment variable.
2. `profile/PROFILE.json` (your real, gitignored file).
3. `profile/PROFILE.example.json` — used **only as a fallback**, and it prints a loud
   warning so you never ship a "Jane Doe" CV by accident.

## Getting started

```powershell
# from skills/daily-cv/
Copy-Item .\profile\PROFILE.template.json .\profile\PROFILE.json
notepad .\profile\PROFILE.json   # fill in YOUR values
```

To populate `PROFILE.json` quickly (LinkedIn, Gmail, AI-chat history, or a manual
questionnaire), follow **[../INIT.md](../INIT.md)**. The assistant must confirm every
extracted fact with you and never fabricate — see the Anti-Fabrication Rules in
`../SKILL.md`.

## Why a profile, not hardcoded constants

The generators used to hardcode one person's name, contacts, and full history. That made
the skill unpublishable and impossible to reuse. Centralising everything here means:

- **Reusable** — anyone fills `PROFILE.json` and the whole skill works for them.
- **Safe** — `PROFILE.json` is gitignored, so no PII can be committed.
- **Single source of truth** — `key_metrics` is the anti-fabrication ground truth: every
  number in a CV or cover letter must trace back to it.
