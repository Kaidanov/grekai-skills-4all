import { test, type Page } from '@playwright/test';
import { join } from 'node:path';
import { showIntro, showStep, publishManifest, saveVideo, Timeline, type TutorialStep } from './test-helpers';

/**
 * Example tutorial spec — the shape `/tutorial-create` generates. Replace the URL and
 * STEPS with your app's real flow. Each step: drive the UI → caption on camera → screenshot,
 * while a Timeline records WHEN each step starts and the whole session is recorded to video.
 *
 * It records a real session video AND per-step screenshots, then publishes ONE manifest that
 * drives either renderer:
 *   Real motion video (the app moving + narration):
 *     node skills/tutorial/scripts/synthesize-audio.mjs   --manifest public/tutorials/example-tour-steps.json --out public/tutorials
 *     node skills/tutorial/scripts/render-motion-video.mjs --manifest public/tutorials/example-tour-steps.json \
 *          --audio public/tutorials/example-tour-audio.json --out public/tutorials   # -> example-tour-motion.mp4
 *   Screenshot slideshow (no recording needed):
 *     node skills/tutorial/scripts/render-tutorial-video.mjs --manifest public/tutorials/example-tour-steps.json --out public/tutorials
 *   HTML player (no ffmpeg):
 *     node skills/tutorial/scripts/build-tutorial-page.mjs --steps public/tutorials/example-tour-steps.json --out public/tutorials/example-tour.html
 *
 * Run:   npx playwright test tests/example.spec.ts
 */
const SLUG = 'example-tour';
const OUT = join(process.cwd(), 'public', 'tutorials');
const W = 1920, H = 1080;

const STEPS: (TutorialStep & { drive: (page: Page) => Promise<void> })[] = [
  {
    title: 'Open the app',
    narration: 'We start on the home page of the application.',
    screenshot: join(OUT, `${SLUG}-01.png`),
    drive: async (page) => { await page.goto('/'); },
  },
  {
    title: 'Find the heading',
    narration: 'Here is the main heading that greets every visitor.',
    screenshot: join(OUT, `${SLUG}-02.png`),
    drive: async (page) => { await page.locator('h1, h2').first().scrollIntoViewIfNeeded().catch(() => {}); },
  },
];

// A manual recorded context gives us a deterministically-named .webm we can save on close.
test('example tutorial — narrated tour', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    recordVideo: { dir: OUT, size: { width: W, height: H } },
  });
  const page = await context.newPage();
  const timeline = new Timeline();

  await page.goto('/');
  await showIntro(page, 'Example Tutorial', 'A two-step narrated tour');
  timeline.start();                         // t0 = first real frame (after the intro)

  let i = 0;
  for (const step of STEPS) {
    i += 1;
    step.atMs = timeline.mark();            // record when this step begins
    await step.drive(page);
    await showStep(page, i, step.title);
    await page.screenshot({ path: step.screenshot });
  }

  await context.close();                    // finalize the recording
  await saveVideo(page, join(OUT, `${SLUG}.webm`));

  publishManifest(join(OUT, `${SLUG}-steps.json`), {
    slug: SLUG,
    title: 'Example Tutorial',
    voice: 'en-US-JennyNeural',
    width: W, height: H,
    video: `${SLUG}.webm`,                  // enables the MOTION renderer
    steps: STEPS.map(({ title, narration, screenshot, atMs }) => ({ title, narration, screenshot, atMs })),
  });
});
