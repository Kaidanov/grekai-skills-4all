import { test, expect } from '@playwright/test';
import { join } from 'node:path';
import { publishManifest, type TutorialStep } from '../../templates/test-helpers';

/**
 * REAL example — a narrated tour of the GrekAI Skills catalog (this repo's own site).
 *
 * Run it:
 *   1. Serve the repo root:   python -m http.server 4178   (or: npx serve . -l 4178)
 *   2. Point Playwright baseURL at http://localhost:4178 and:
 *        npx playwright test grekai-catalog-tour.spec.ts
 *   3. Narrate + build the player (no ffmpeg):
 *        node ../../scripts/synthesize-audio.mjs   --manifest grekai-catalog-tour-steps.json --out .
 *        node ../../scripts/build-tutorial-page.mjs --steps    grekai-catalog-tour-steps.json --out index.html
 *
 * The test captures the 5 screenshots in this folder AND asserts the acceptance criteria below.
 */
const HERE = __dirname;
const SLUG = 'grekai-catalog-tour';

const STEPS: TutorialStep[] = [
  { title: 'The catalog', screenshot: join(HERE, 'step-01-catalog.png'),
    narration: 'This is GrekAI Skills for All, a free and open catalog of agent skills you can drop straight into Claude Code.' },
  { title: 'Filter by category', screenshot: join(HERE, 'step-02-skills.png'),
    narration: 'Filter by category to find what you need. Everything here is a ready to use, self contained skill.' },
  { title: 'The Tutorial skill', screenshot: join(HERE, 'step-03-card.png'),
    narration: 'Here is the Tutorial skill. It records narrated walkthroughs of your own app, exactly like the one you are watching now.' },
  { title: 'Skill details', screenshot: join(HERE, 'step-04-detail.png'),
    narration: 'Open any skill for its own page: what it does, when to use it, and the full README.' },
  { title: 'One-line install', screenshot: join(HERE, 'step-05-install.png'),
    narration: 'Copy the one line install, and the skill lands in your Claude skills folder. Free to use, and open for your contributions.' },
];

test.describe('GrekAI catalog tour @example', () => {
  test('browse the catalog and reach the tutorial install command', async ({ page }) => {
    // AC1 — the catalog loads with at least one skill card
    await page.goto('/');
    await expect(page.locator('#site-title')).toHaveText('GrekAI Skills 4 All');
    const cards = page.locator('.card');
    await expect(cards.first()).toBeVisible();
    expect(await cards.count()).toBeGreaterThan(0);
    await page.screenshot({ path: STEPS[0].screenshot });

    // AC2 — the Tutorial skill is present in the catalog
    const tutorialCard = page.locator('.card', { hasText: 'Tutorial' }).first();
    await expect(tutorialCard).toBeVisible();

    // AC3 — category filtering keeps the list non-empty
    await page.locator('.chip', { hasText: 'Skills' }).first().click();
    await expect(cards.first()).toBeVisible();
    await page.screenshot({ path: STEPS[1].screenshot });

    // step 3 — focus the tutorial card
    await tutorialCard.scrollIntoViewIfNeeded();
    await tutorialCard.screenshot({ path: STEPS[2].screenshot });

    // AC4 — the skill detail page opens for the tutorial skill
    await page.goto('/skill.html?id=tutorial');
    await expect(page.locator('#skill-title')).toContainText('Tutorial');
    await page.screenshot({ path: STEPS[3].screenshot });

    // AC5 — the one-line install command is shown and correct
    const install = page.locator('#install-cmd');
    await expect(install).toContainText('npx degit');
    await expect(install).toContainText('skills/tutorial');
    await page.locator('#install-panel').screenshot({ path: STEPS[4].screenshot });

    // publish the manifest the audio + page generators consume
    publishManifest(join(HERE, `${SLUG}-steps.json`), {
      slug: SLUG,
      title: 'Browse & install from the GrekAI Skills catalog',
      voice: 'en-US-JennyNeural',
      width: 1280,
      height: 800,
      steps: STEPS,
    });
  });
});
