import { test, type Page } from '@playwright/test';
import { join } from 'node:path';
import { showIntro, showStep, publishManifest, type TutorialStep } from './test-helpers';

/**
 * Example tutorial spec — the shape `/tutorial-create` generates. Replace the URL and
 * STEPS with your app's real flow. Each step: drive the UI → caption on camera → screenshot.
 * At the end we publish the manifest the renderer turns into a narrated MP4.
 *
 * Run:   npx playwright test tests/example.spec.ts
 * Then:  node skills/tutorial/scripts/render-tutorial-video.mjs \
 *           --manifest public/tutorials/example-tour-steps.json --out public/tutorials
 */
const SLUG = 'example-tour';
const OUT = join(process.cwd(), 'public', 'tutorials');

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

test('example tutorial — narrated tour', async ({ page }) => {
  await page.goto('/');
  await showIntro(page, 'Example Tutorial', 'A two-step narrated tour');

  let i = 0;
  for (const step of STEPS) {
    i += 1;
    await step.drive(page);
    await showStep(page, i, step.title);
    await page.screenshot({ path: step.screenshot });
  }

  publishManifest(join(OUT, `${SLUG}-steps.json`), {
    slug: SLUG,
    title: 'Example Tutorial',
    voice: 'en-US-JennyNeural',
    steps: STEPS.map(({ title, narration, screenshot }) => ({ title, narration, screenshot })),
  });
});
