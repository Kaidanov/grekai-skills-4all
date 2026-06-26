---
name: tutorial
description: >
  Record narrated, themeable product tutorials by driving any web app with Playwright and
  voicing every step with a neural TTS voice (Jenny by default). Use when the user types
  "/tutorial-create", "/tutorial-update", or "/tutorial-status", or asks to "record a tutorial",
  "make a walkthrough video", "narrated demo", "real video with voiceover", "screen recording with
  narration", "update the tutorial", "refresh the tutorials index", or "tutorial status". Outputs a
  REAL motion video of the app moving with narration (MP4), or a screenshot slideshow, or a
  no-ffmpeg HTML player — all with WebVTT captions. Runs a human-gated flow: draft & APPROVE a
  scenario, record it with Playwright, render, show the output for APPROVAL and fix issues in a
  loop, then regenerate a light/dark, logo-branded index.html that switches between every tutorial.
  Project-agnostic — reads ./tutorial.config.json for brand, paths and voice.
---

# Tutorial — narrated Playwright walkthroughs

Turn a plain-English goal into a **narrated, themeable tutorial**. Playwright drives the app while
**recording the live session to video** and capturing a screenshot per step; a neural voice (Jenny)
narrates each step; then you render one of three **drift-free** outputs — a **real motion video** of
the app in motion, a screenshot slideshow MP4, or a no-ffmpeg HTML player — each with captions, and a
branded `index.html` switches between all tutorials.

The flow is **gated** — never record before the scenario is approved, never publish before the
tutorial is approved. Honor **done = proven**: show real output (a played video / a screenshot), and
never fabricate results.

> Prerequisites (Node 18+, `edge-tts`, Playwright; **ffmpeg** for the motion/slideshow MP4 — a full
> build, not Playwright's webm-only bundled one) and full setup are in `README.md`.
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
| **init** | `/tutorial-init` | Ask setup questions, then write `tutorial.config.json` + scaffold folders. Optionally flow into create. |
| **create** | `/tutorial-create "<free-text goal>"` | Draft+approve a scenario → record → render → approve → publish. |
| **update** | `/tutorial-update <slug>` | Re-record an existing tutorial and refresh its video + index card. |
| **status** | `/tutorial-status` | Report which tutorials are recorded vs stale/missing. **No recording.** |

> 📺 **Working example to copy:** [`examples/grekai-catalog-tour/`](./examples/grekai-catalog-tour/) — a real
> narrated tour (real screenshots + real Jenny audio + a no-ffmpeg HTML player). Open its `index.html`.

---

## init — interactive setup (ask first)

When invoked via `/tutorial-init`, **ask the user before doing anything** (AskUserQuestion, one batch):
app name + base URL + dev command · brand (logo, accent, default theme) · narration voice + output folder
· an optional first-tutorial goal. Then copy `config.example.json` → `tutorial.config.json`, fill it from
the answers, create the `scenariosDir`/`outputDir`, and confirm. If a first-tutorial goal was given, flow
straight into **create** (draft the scenario for approval). Never record before a scenario is approved.

## create — the gated pipeline

**1. Draft the scenario.** From the free-text goal, write `<scenariosDir>/<slug>.md` using
`templates/scenario-template.md`: a numbered step table (Action / What to show / Why / spoken
Narration), honesty notes (anything the UI can't do — say so in narration), and acceptance criteria.
Keep narration sentences short and spoken-plain; one cue per step.

**2. ⛔ GATE 1 — approve the scenario.** Show the draft and ask the user to approve or edit. **Do not
record until approved.** Loop on edits.

**3. Generate / extend the Playwright spec** `<specsDir>/<slug>.spec.ts` from the approved steps,
reusing `templates/test-helpers.ts` (`showIntro`, `showStep`, `Timeline`, `saveVideo`,
`publishManifest`) and `templates/example.spec.ts` as the pattern. Create a context with
`recordVideo` (the config template already sets `video: { mode: 'on' }`), and for each step: drive the
UI → on-camera caption → screenshot into `<outputDir>/<slug>-NN.png` → `timeline.mark()` to record when
the step starts. At the end, `saveVideo()` writes `<outputDir>/<slug>.webm` and `publishManifest()`
writes `<outputDir>/<slug>-steps.json` (with the `video` path + per-step `atMs` for the motion renderer).

**4. Record.** Start the app (config `devCommand`/`baseUrl`, or the project's start script), then:
```bash
npx playwright test <specsDir>/<slug>.spec.ts
```
The spec must go green and emit `<slug>.webm` + the per-step PNGs + `<slug>-steps.json`.

**5. Render.** Three formats — **a real motion video is the headline output**; pick by what's installed:

- **A · Real motion MP4 (the app actually moving + Jenny narration)** — needs `edge-tts` + `ffmpeg`.
  Synthesize the narration first (gives per-step durations), then mux it over the recorded session video:
  ```bash
  node <skill>/scripts/synthesize-audio.mjs    --manifest <outputDir>/<slug>-steps.json --out <outputDir>
  node <skill>/scripts/render-motion-video.mjs --manifest <outputDir>/<slug>-steps.json \
       --audio <outputDir>/<slug>-audio.json   --out <outputDir>
  ```
  Produces `<slug>-motion.mp4` + `<slug>-narration.vtt`. **Drift-free:** each step shows real motion for
  its window, and if a step's narration is longer than its clip the last frame is frozen to fit — so the
  voice is always fully audible and never desyncs. Add `--dry-run --video-dur <sec>` to preview the plan
  without rendering. **Fails hard if the output has no audio stream.** No system ffmpeg? Point at any
  binary with `FFMPEG_BIN=…` (NOTE: Playwright's *bundled* ffmpeg is webm-only — use a full ffmpeg, e.g.
  `node_modules/ffmpeg-static/ffmpeg`).
- **B · HTML player (no ffmpeg)** — needs only `edge-tts`:
  ```bash
  node <skill>/scripts/synthesize-audio.mjs    --manifest <outputDir>/<slug>-steps.json --out <outputDir>
  node <skill>/scripts/build-tutorial-page.mjs --steps    <outputDir>/<slug>-steps.json --out <outputDir>/<slug>.html
  ```
  A self-contained, themeable `<slug>.html` that plays the screenshots in sync with the audio
  (captions + light/dark toggle). Good when ffmpeg isn't available.
- **C · Slideshow MP4 (screenshots → video)** — needs `edge-tts` + `ffmpeg`:
  ```bash
  node <skill>/scripts/render-tutorial-video.mjs --manifest <outputDir>/<slug>-steps.json --out <outputDir>
  ```
  Produces `<slug>-jenny.mp4` — static screenshots held under narration. Use when there's no recorded
  session video (e.g. a re-render from screenshots only).

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
- **Real video is the headline** — when ffmpeg is available, render the motion MP4 (the app actually
  moving + narration). The no-ffmpeg HTML player and the screenshot slideshow are the graceful
  fallbacks when ffmpeg or the recorded session video isn't available — never silently downgrade
  without saying so.

---

Part of [GrekAI Skills 4 All](https://github.com/Kaidanov/grekai-skills-4all) · MIT-licensed, free to use.
Created by **Tzvi Gregory Kaidanov** — [Set4u](https://set4u.biz). ⭐ the repo if it helps you.
