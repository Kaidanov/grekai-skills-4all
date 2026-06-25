# Example: GrekAI catalog tour 🎬

A **real, runnable** tutorial produced by this skill — a narrated tour of the GrekAI Skills
catalog (the site this repo deploys). Open **[`index.html`](./index.html)** to watch it: real
screenshots, real **Jenny** (edge-tts) narration, captions, a light/dark toggle, and player
controls — **no ffmpeg required**.

## What's here

| File | What it is |
|------|------------|
| `index.html` | The playable HTML audio-slideshow (open this). |
| `scenario.md` | The approved scenario + acceptance criteria. |
| `grekai-catalog-tour.spec.ts` | The Playwright spec — captures the screenshots and asserts AC1–AC5. |
| `grekai-catalog-tour-steps.json` | Step manifest (image + narration per step). |
| `grekai-catalog-tour-audio.json` | Per-step audio files + measured durations. |
| `grekai-catalog-tour-narration.vtt` | Combined WebVTT captions. |
| `audio/step-0N.mp3` | The narration audio sources (en-US-JennyNeural). |
| `step-0N-*.png` | The step screenshots. |

## Reproduce it

```bash
# from the repo root
python -m http.server 4178            # serve the catalog

# from this folder (with Playwright + edge-tts installed)
npx playwright test grekai-catalog-tour.spec.ts            # capture screenshots + assert AC1–AC5
node ../../scripts/synthesize-audio.mjs   --manifest grekai-catalog-tour-steps.json --out .   # Jenny mp3s + VTT
node ../../scripts/build-tutorial-page.mjs --steps    grekai-catalog-tour-steps.json --out index.html  # the player
```

`synthesize-audio.mjs` needs only **edge-tts** (`pip install edge-tts`). `build-tutorial-page.mjs`
needs nothing but Node. The MP4 path (`render-tutorial-video.mjs`) additionally needs **ffmpeg**.
