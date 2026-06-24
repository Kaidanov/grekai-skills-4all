---
name: tutorial
description: >
  Record narrated, themeable product tutorials by driving any web app with Playwright and
  voicing every step with a neural TTS voice (Jenny by default). Use when the user types
  "/tutorial-create", "/tutorial-update", or "/tutorial-status", or asks to "record a tutorial",
  "make a walkthrough video", "narrated demo", "screen walkthrough with voiceover", "update the
  tutorial", "refresh the tutorials index", or "tutorial status". Runs a human-gated flow:
  draft & APPROVE a scenario, record it with Playwright, render a narrated MP4 + WebVTT captions,
  show the output for APPROVAL and fix issues in a loop, then regenerate a light/dark, logo-branded
  index.html that switches between every tutorial. Project-agnostic — reads ./tutorial.config.json
  for brand, paths and voice.
---

# Tutorial — narrated Playwright walkthroughs

Turn a plain-English goal into a **narrated, themeable tutorial**: Playwright drives the app and
captures a screenshot per step; a neural voice (Jenny) narrates each step; the renderer produces a
**drift-free** MP4 + captions; and a branded `index.html` switches between all tutorials.

The flow is **gated** — never record before the scenario is approved, never publish before the
tutorial is approved. Honor **done = proven**: show real output (a played video / a screenshot), and
never fabricate results.

> Prerequisites (Node 18+, ffmpeg/ffprobe, `edge-tts`, Playwright) and full setup are in `README.md`.
> All paths below are relative to the **skill folder** (`scripts/…`, `templates/…`) and the **project
> root** (`tutorial.config.json`, `public/tutorials/…`). Adjust to wherever the skill is installed.

## 0. One-time project setup (the "initial settings")

On the first `/tutorial-*` run in a repo, ensure a `tutorial.config.json` exists at the project root.
If it is missing, copy `config.example.json`, then fill it in (auto-detect where you can — logo under
`public/`, dev command from `package.json`, base URL from the dev server):

```jsonc
{
  "project": { "name": "My App", "baseUrl": "http://127.0.0.1:5173", "devCommand": "npm run dev" },
  "brand":   { "logo": "/logo.svg", "accent": "#2563eb", "accentDark": "#1e40af", "defaultTheme": "dark" },
  "tts":     { "voice": "en-US-JennyNeural", "tailPadMs": 600 },
  "paths":   { "scenariosDir": "tutorials/scenarios", "specsDir": "tests",
               "outputDir": "public/tutorials", "catalogFile": "public/tutorials/catalog.json" },
  "video":   { "width": 1920, "height": 1080 }
}
```

Confirm the values with the user, then proceed. These settings are read by every mode.

## Modes

The skill dispatches on the first word of its arguments (the bundled `commands/` wrappers map the
literal `/tutorial-create`, `/tutorial-update`, `/tutorial-status` tokens onto these):

| Mode | Trigger | What it does |
|------|---------|--------------|
| **create** | `/tutorial-create "<free-text goal>"` | Draft+approve a scenario → record → render → approve → publish. |
| **update** | `/tutorial-update <slug>` | Re-record an existing tutorial and refresh its video + index card. |
| **status** | `/tutorial-status` | Report which tutorials are recorded vs stale/missing. **No recording.** |

---

## create — the gated pipeline

**1. Draft the scenario.** From the free-text goal, write `<scenariosDir>/<slug>.md` using
`templates/scenario-template.md`: a numbered step table (Action / What to show / Why / spoken
Narration), honesty notes (anything the UI can't do — say so in narration), and acceptance criteria.
Keep narration sentences short and spoken-plain; one cue per step.

**2. ⛔ GATE 1 — approve the scenario.** Show the draft and ask the user to approve or edit. **Do not
record until approved.** Loop on edits.

**3. Generate / extend the Playwright spec** `<specsDir>/<slug>.spec.ts` from the approved steps,
reusing `templates/test-helpers.ts` (`showIntro`, `showStep`, `publishManifest`) and
`templates/example.spec.ts` as the pattern. Each step: drive the UI → on-camera caption → screenshot
into `<outputDir>/<slug>-NN.png`. At the end, `publishManifest()` writes
`<outputDir>/<slug>-steps.json` (the renderer's input).

**4. Record.** Start the app (config `devCommand`/`baseUrl`, or the project's start script), then:
```bash
npx playwright test <specsDir>/<slug>.spec.ts
```
The spec must go green and emit the per-step PNGs + `<slug>-steps.json`.

**5. Render the narration (Jenny).** Drift-free slideshow from the manifest:
```bash
node <skill>/scripts/render-tutorial-video.mjs --manifest <outputDir>/<slug>-steps.json --out <outputDir>
```
Produces `<slug>-jenny.mp4` + `<slug>-narration.vtt`. The script **fails hard if the output has no
audio stream** — never ship a silent or wrong-voice video.

**6. ⛔ GATE 2 — show & approve the tutorial.** Open the MP4 (or capture a Playwright screenshot of it
playing) and present it. Review honestly against the acceptance criteria; fix issues (re-narrate,
re-shoot a step, adjust timing) and re-render in a loop **until the user approves**.

**7. Publish + theme.** Upsert the tutorial into `<catalogFile>` (`{slug,title,description,status,
video,poster,recordedAt}`), then regenerate the switchable, branded index:
```bash
node <skill>/scripts/build-index.mjs --catalog <catalogFile> --config tutorial.config.json --out <outputDir>/index.html
```
The index gets the configured **logo + accent**, a **light/dark toggle** (persisted in `localStorage`),
and a filter box. Report the served URL (e.g. `<baseUrl>/tutorials/index.html`).

## update — refresh an existing tutorial

Re-run the spec for `<slug>`, re-render the narration, update its `recordedAt` in the catalog, and
rebuild the index (step 7). Use when the UI changed or narration needs a tweak.

## status — report, don't record

Read `<catalogFile>` and the specs in `<specsDir>`. Report, per tutorial: recorded vs spec-only,
`recordedAt` vs spec mtime (stale?), and any missing artifacts (no MP4 / no PNGs / no catalog entry).
Output a tight table. Never start a recording in this mode.

## Principles

- **Two approval gates are mandatory** — scenario, then tutorial. They are the whole point.
- **done = proven** — show the rendered video / a screenshot; state what passed and what didn't.
- **Honesty in narration** — if the UI can't do a step, say so on camera; don't hide it.
- **No fabrication** — never claim a render/test passed without the artifact.
- **KISS** — the slideshow renderer (screenshots + voice) is the default; a full screencast-with-voice
  mux is an advanced option (see README), not the baseline.
