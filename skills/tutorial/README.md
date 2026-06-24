# tutorial — narrated Playwright walkthroughs

Record **narrated, themeable product tutorials** by driving any web app with Playwright and voicing
every step with a neural TTS voice (**Jenny** by default). One plain-English goal becomes a
drift-free **MP4 + captions** plus a **light/dark, logo-branded `index.html`** that switches between
all your tutorials.

The flow is **human-gated**: approve the *scenario* before recording, approve the *tutorial* before
publishing. It honors **done = proven** — you see the real video, nothing is faked.

```
/tutorial-create "show a new user how to create their first record"
        │
        ▼  draft scenario ──⛔ you approve──▶ Playwright records ──▶ Jenny narrates
        │                                                                   │
   regenerate themeable index ◀──⛔ you approve the video──◀─────────────────┘
```

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
| **ffmpeg + ffprobe** | builds and concatenates the video | Windows: `winget install Gyan.FFmpeg` · macOS: `brew install ffmpeg` · Linux: `apt install ffmpeg` |
| **edge-tts** | the neural narration voice (Jenny) | `pip install edge-tts` then `edge-tts --list-voices` |

All four must be on your `PATH`. The renderer fails fast with a clear message if one is missing.

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
| `/tutorial-create "<goal>"` | Drafts a scenario → **you approve** → records with Playwright → renders the narrated MP4 → **you approve** → publishes + rebuilds the index. |
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
# 1. record the 2-step example against your running app
npx playwright test tests/example.spec.ts

# 2. render the narrated video (Jenny) from the published manifest
node ~/.claude/skills/tutorial/scripts/render-tutorial-video.mjs \
     --manifest public/tutorials/example-tour-steps.json --out public/tutorials

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
| `scripts/render-tutorial-video.mjs` | Manifest → drift-free narrated MP4 + WebVTT (edge-tts + ffmpeg). |
| `scripts/build-index.mjs` | Catalog + config → themeable, switchable `index.html`. |
| `templates/scenario-template.md` | The scenario draft skeleton (steps + narration + acceptance). |
| `templates/theme.css` | Light/dark token sheet shipped beside the index. |
| `templates/playwright.config.example.ts` | Starter Playwright config (1920×1080 video). |
| `templates/test-helpers.ts` | `showIntro`, `showStep`, `publishManifest` for specs. |
| `templates/example.spec.ts` | A minimal, runnable example tutorial spec. |
| `commands/tutorial-*.md` | Slash-command wrappers for the literal `/tutorial-create` etc. tokens. |
| `examples/catalog.example.json` | Sample catalog so `build-index` runs out of the box. |

## How it works (the pipeline)

1. **Scenario** — draft `<scenariosDir>/<slug>.md`; **approve** it (gate 1).
2. **Record** — a Playwright spec drives the UI, captions each step on camera, screenshots into
   `<outputDir>/<slug>-NN.png`, and `publishManifest()` writes `<slug>-steps.json`.
3. **Narrate** — `render-tutorial-video.mjs` synthesizes Jenny audio per step, holds each slide for
   exactly its audio length (+ tail pad → **no drift**), concatenates to `<slug>-jenny.mp4`, writes
   `<slug>-narration.vtt`, and **aborts if the video has no audio stream**.
4. **Approve** — watch it; fix/re-render in a loop (gate 2).
5. **Publish** — upsert the catalog and rebuild the themeable `index.html`.

## Troubleshooting

- **`[edge-tts] failed … not on PATH`** → `pip install edge-tts`; confirm `edge-tts --list-voices` works.
- **`[ffmpeg] failed`** → install ffmpeg so both `ffmpeg` and `ffprobe` are on `PATH`.
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
