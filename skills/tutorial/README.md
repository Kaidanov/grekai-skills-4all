# tutorial — narrated Playwright walkthroughs

Record **narrated, themeable product tutorials** by driving any web app with Playwright and voicing
every step with a neural TTS voice (**Jenny** by default). One plain-English goal becomes a
drift-free, narrated output — a **real motion video** of the app moving (MP4), a screenshot slideshow,
or a no-ffmpeg HTML player, each with **captions** — plus a **light/dark, logo-branded `index.html`**
that switches between all your tutorials.

The flow is **human-gated**: approve the *scenario* before recording, approve the *tutorial* before
publishing. It honors **done = proven** — you see the real video, nothing is faked.

```
/tutorial-create "show a new user how to create their first record"
        │
        ▼  draft scenario ──⛔ you approve──▶ Playwright records ──▶ Jenny narrates
        │                                                                   │
   regenerate themeable index ◀──⛔ you approve the video──◀─────────────────┘
```

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/Kaidanov/grekai-skills-4all?style=social)](https://github.com/Kaidanov/grekai-skills-4all)
[![Made by Set4u](https://img.shields.io/badge/made%20by-Set4u-2563eb)](https://set4u.biz)

▶️ **See it in action** — the [GrekAI catalog tour](./examples/grekai-catalog-tour/): real screenshots + real
Jenny audio in a no-ffmpeg HTML player. It's a tutorial *of this catalog*, made *by this skill*.

## Install

Add it to your **global** Claude skills folder (available in every repo):

```bash
npx degit Kaidanov/grekai-skills-4all/skills/tutorial ~/.claude/skills/tutorial
```

- **Project-scoped instead?** Target `.claude/skills/tutorial` to commit it with one repo.
- **Want the literal `/tutorial-create` etc. commands?** Copy the wrappers into your commands folder:
  ```bash
  npx degit Kaidanov/grekai-skills-4all/skills/tutorial/commands ~/.claude/commands
  ```
  (Or invoke the skill directly: `/tutorial create …`, `/tutorial update …`, `/tutorial status`.)

## Prerequisites

| Tool | Why | Install / check |
|------|-----|-----------------|
| **Node 18+** | runs the renderer + index generator (`.mjs`) | `node -v` |
| **Playwright** | drives the app and captures screenshots | `npm i -D @playwright/test && npx playwright install chromium` |
| **edge-tts** | the neural narration voice (Jenny) | `pip install edge-tts` then `edge-tts --list-voices` |
| **ffmpeg** | the **real motion MP4** + the slideshow MP4 (a full build) | Windows: `winget install Gyan.FFmpeg` · macOS: `brew install ffmpeg` · Linux: `apt install ffmpeg` |

**Three outputs — pick by what's installed:**

| Output | What you get | Needs |
|--------|--------------|-------|
| **Real motion MP4** (`render-motion-video.mjs`) | the **app actually moving** with narration over it | Node + Playwright + edge-tts + **ffmpeg** |
| **HTML player** (`build-tutorial-page.mjs`) | screenshots + voice, themeable, self-contained | Node + Playwright + edge-tts (**no ffmpeg**) |
| **Slideshow MP4** (`render-tutorial-video.mjs`) | static screenshots held under narration | Node + Playwright + edge-tts + **ffmpeg** |

> ⚠️ **Use a full ffmpeg, not Playwright's bundled one.** Playwright ships a *webm-only* ffmpeg (just
> enough to save its own recordings) — it can't encode H.264/AAC, so it won't render the MP4s. Install a
> real ffmpeg, or point the renderers at one you already have (e.g. `node_modules/ffmpeg-static`):

```bash
FFMPEG_BIN=/path/to/ffmpeg FFPROBE_BIN=/path/to/ffprobe \
  node scripts/render-motion-video.mjs --manifest <out>/<slug>-steps.json --audio <out>/<slug>-audio.json --out <out>
```

`ffprobe` is **optional** — the motion renderer reads durations from `<slug>-audio.json` and parses the
recording's length from ffmpeg itself; pass `--video-dur <sec>` to override. Use `--dry-run` to preview the
exact ffmpeg plan (per-step timings + freeze pads) without rendering. Scripts fail fast with a clear
message if a genuinely-required tool is unavailable, and never ship a silent video.

## Setup (one-time, per project)

1. Copy `config.example.json` to your **project root** as `tutorial.config.json` and fill it in:

   ```jsonc
   {
     "project": { "name": "My App", "baseUrl": "http://127.0.0.1:5173", "devCommand": "npm run dev" },
     "brand":   { "logo": "/logo.svg", "accent": "#2563eb", "accentDark": "#60a5fa", "defaultTheme": "dark" },
     "tts":     { "voice": "en-US-JennyNeural", "tailPadMs": 600 },
     "paths":   { "scenariosDir": "tutorials/scenarios", "specsDir": "tests",
                  "outputDir": "public/tutorials", "catalogFile": "public/tutorials/catalog.json" },
     "video":   { "width": 1920, "height": 1080 }
   }
   ```

2. If your repo has no Playwright config yet, copy `templates/playwright.config.example.ts` to
   `playwright.config.ts` and adjust the dev-server command/port.

The assistant does this with you on the first `/tutorial-*` run.

## Use it

| Command | What happens |
|---------|--------------|
| `/tutorial-init` | Asks a few setup questions, writes `tutorial.config.json`, scaffolds folders. Run this first. |
| `/tutorial-create "<goal>"` | Drafts a scenario → **you approve** → records with Playwright → renders narration (HTML player or MP4) → **you approve** → publishes + rebuilds the index. |
| `/tutorial-update <slug>` | Re-records an existing tutorial and refreshes its video + index card. |
| `/tutorial-status` | Prints which tutorials are recorded vs stale/missing. No recording. |

## Theming

The generated `index.html` is fully themeable from `tutorial.config.json`:

- **Light / dark** — a header toggle, persisted in `localStorage`; default from `brand.defaultTheme`.
  Tokens live in `templates/theme.css` (copied next to the index).
- **Company logo** — `brand.logo` renders in the header.
- **Accent color** — `brand.accent` (light) / `brand.accentDark` (dark) are injected as `--accent`.

Swap the logo + two colors and the whole site rebrands. No build step.

## Try it in 60 seconds (the bundled example)

```bash
# 1. record the 2-step example against your running app (captures a session video too)
npx playwright test tests/example.spec.ts

# 2. render the REAL motion video (Jenny narration over the recorded app)
node ~/.claude/skills/tutorial/scripts/synthesize-audio.mjs \
     --manifest public/tutorials/example-tour-steps.json --out public/tutorials
node ~/.claude/skills/tutorial/scripts/render-motion-video.mjs \
     --manifest public/tutorials/example-tour-steps.json \
     --audio public/tutorials/example-tour-audio.json --out public/tutorials
#   (no ffmpeg? swap step 2 for build-tutorial-page.mjs to get the HTML player instead)

# 3. build the themeable switcher index from the sample catalog
node ~/.claude/skills/tutorial/scripts/build-index.mjs \
     --catalog skills/tutorial/examples/catalog.example.json \
     --config tutorial.config.json --out public/tutorials/index.html
```

Open `public/tutorials/index.html` — toggle light/dark, watch the narrated tour.

## Contents

| Path | Purpose |
|------|---------|
| `SKILL.md` | The full skill instructions (the gated create/update/status pipeline). |
| `README.md` | This guide. |
| `config.example.json` | Per-project settings template → copy to `tutorial.config.json`. |
| `scripts/synthesize-audio.mjs` | Manifest → per-step Jenny mp3 + WebVTT + `-audio.json` (**no ffmpeg**). |
| `scripts/render-motion-video.mjs` | Recorded session video + manifest → **real motion MP4** with narration (drift-free; freezes a frame when a step's voice runs long). edge-tts + **ffmpeg**. |
| `scripts/build-tutorial-page.mjs` | Steps + audio → a self-contained HTML **audio-slideshow player** (no ffmpeg). |
| `scripts/render-tutorial-video.mjs` | Manifest → drift-free **slideshow** MP4 + WebVTT from screenshots (edge-tts + **ffmpeg**). |
| `scripts/build-index.mjs` | Catalog + config → themeable, switchable `index.html`. |
| `examples/grekai-catalog-tour/` | A real, runnable example — screenshots + audio + the player. |
| `templates/scenario-template.md` | The scenario draft skeleton (steps + narration + acceptance). |
| `templates/theme.css` | Light/dark token sheet shipped beside the index. |
| `templates/playwright.config.example.ts` | Starter Playwright config (1920×1080 video). |
| `templates/test-helpers.ts` | `showIntro`, `showStep`, `Timeline`, `saveVideo`, `publishManifest` for specs. |
| `templates/example.spec.ts` | A minimal, runnable example tutorial spec. |
| `commands/tutorial-*.md` | Slash-command wrappers for the literal `/tutorial-create` etc. tokens. |
| `examples/catalog.example.json` | Sample catalog so `build-index` runs out of the box. |

## How it works (the pipeline)

1. **Scenario** — draft `<scenariosDir>/<slug>.md`; **approve** it (gate 1).
2. **Record** — a Playwright spec drives the UI in a `recordVideo` context, captions each step on
   camera, screenshots into `<outputDir>/<slug>-NN.png`, marks each step's start time (`Timeline`),
   then `saveVideo()` writes `<slug>.webm` and `publishManifest()` writes `<slug>-steps.json` (with the
   video path + per-step `atMs`).
3. **Narrate & render** — pick a format:
   - **Real motion MP4 (ffmpeg):** `synthesize-audio.mjs` makes per-step Jenny mp3s, then
     `render-motion-video.mjs` cuts the recorded session video per step and muxes the narration —
     freezing a step's last frame only if its voice runs longer than its clip, so it **never drifts**
     and **aborts if the video has no audio stream**. → `<slug>-motion.mp4`.
   - **HTML player (no ffmpeg):** `build-tutorial-page.mjs` emits a self-contained screenshots+voice player.
   - **Slideshow MP4 (ffmpeg):** `render-tutorial-video.mjs` holds each screenshot under its narration.
4. **Approve** — watch it; fix/re-render in a loop (gate 2).
5. **Publish** — upsert the catalog and rebuild the themeable `index.html`.

## Troubleshooting

- **`[edge-tts] failed … not on PATH`** → `pip install edge-tts`; confirm `edge-tts --list-voices` works.
- **`[ffmpeg] failed`** → install a **full** ffmpeg on `PATH` (or set `FFMPEG_BIN`). Playwright's
  bundled ffmpeg is webm-only and **cannot** render the MP4s — use a real build.
- **motion MP4 looks like a slideshow / no movement** → the manifest had no `video` (the spec didn't
  record a session), so only screenshots existed. Ensure the spec uses a `recordVideo` context and
  `saveVideo()` (see `templates/example.spec.ts`), then re-run with `render-motion-video.mjs`.
- **"rendered video has NO audio stream"** → the TTS step produced no audio; check the voice name
  (`tts.voice`) and that narration text isn't empty.
- **Screenshots are blank/cut off** → raise the viewport in your Playwright config and `await` the UI
  before `page.screenshot()`.
- **Index has no logo / wrong color** → check `brand.logo` is a path your site serves and `brand.accent`
  is a valid CSS color; re-run `build-index.mjs`.

## Why

Hand-made walkthrough videos rot the moment the UI changes, and re-recording + re-narrating them is
tedious. This skill makes tutorials **reproducible**: the scenario is text you approve, the recording
is a Playwright spec you can re-run, and the narration + branded index regenerate on command — so
refreshing a tutorial is one `/tutorial-update`, not an afternoon.

## License & credits

[MIT](../../LICENSE) — free to use, modify, and ship; keep the copyright notice. Created by
**Tzvi Gregory Kaidanov** — **[Set4u](https://set4u.biz)**. Contributions welcome
([CONTRIBUTING](../../CONTRIBUTING.md)); if it helps you, please ⭐ the
[repo](https://github.com/Kaidanov/grekai-skills-4all).
