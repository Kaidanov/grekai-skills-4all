import type { Page } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

/** One step of a tutorial: what to say + where its screenshot lands. */
export interface TutorialStep {
  title: string;
  /** Spoken narration — short, plain sentences. One cue per step. */
  narration: string;
  /** Absolute path the screenshot is written to (also referenced by the manifest). */
  screenshot: string;
}

/** Full-screen intro card, shown for `ms`. Use once at the start. */
export async function showIntro(page: Page, title: string, subtitle = '', ms = 3000): Promise<void> {
  await overlay(page,
    `<div style="font:700 56px system-ui;color:#fff;text-align:center;padding:0 8vw">${title}` +
    `<div style="font:400 26px system-ui;color:#cbd5e1;margin-top:14px">${subtitle}</div></div>`, ms, true);
}

/** Bottom subtitle banner, shown for `ms`. Use to caption each step on camera. */
export async function showStep(page: Page, n: number, text: string, ms = 2600): Promise<void> {
  await overlay(page,
    `<div style="position:fixed;left:0;right:0;bottom:0;padding:18px 28px;` +
    `background:linear-gradient(transparent,rgba(0,0,0,.82));color:#fff;font:500 24px system-ui">` +
    `<b style="color:#6aa3ff">Step ${n}</b> &nbsp; ${text}</div>`, ms, false);
}

// NOTE: `inner` is HTML on purpose (styled captions) and is ALWAYS developer-authored — the step
// titles/narration you write in your spec. It runs only against your own dev server during a local
// recording, never in production. If you ever interpolate untrusted/external data into a caption,
// escape it first (or set textContent instead of innerHTML).
async function overlay(page: Page, inner: string, ms: number, dim: boolean): Promise<void> {
  await page.evaluate(({ inner, dim }) => {
    const d = document.createElement('div');
    d.id = '__tut_overlay';
    d.style.cssText =
      'position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;' +
      (dim ? 'background:rgba(8,10,14,.72)' : 'pointer-events:none');
    d.innerHTML = inner;
    document.body.appendChild(d);
  }, { inner, dim });
  await page.waitForTimeout(ms);
  await page.evaluate(() => document.getElementById('__tut_overlay')?.remove());
}

/** Write the step manifest that scripts/render-tutorial-video.mjs consumes. */
export function publishManifest(
  outFile: string,
  data: { slug: string; title: string; voice?: string; width?: number; height?: number; tailPadMs?: number; steps: TutorialStep[] },
): void {
  mkdirSync(dirname(outFile), { recursive: true });
  const steps = data.steps.map((s) => ({ image: s.screenshot, narration: s.narration, title: s.title }));
  writeFileSync(outFile, JSON.stringify({ ...data, steps }, null, 2));
}
