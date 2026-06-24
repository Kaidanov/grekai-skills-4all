import { defineConfig, devices } from '@playwright/test';

// Starter Playwright config for the `tutorial` skill. Copy to your project root as
// playwright.config.ts (or merge into an existing one). Records 1920×1080 video + screenshots.
const host = process.env.PLAYWRIGHT_HOST ?? '127.0.0.1';
const port = process.env.PLAYWRIGHT_PORT ?? '5173';
const baseURL = `http://${host}:${port}`;

export default defineConfig({
  testDir: './tests',
  testMatch: ['**/*.spec.ts'],
  fullyParallel: false,
  timeout: 900_000, // tutorial recordings can run several minutes
  use: {
    baseURL,
    viewport: { width: 1920, height: 1080 },
    screenshot: 'on',
    trace: 'on',
    video: { mode: 'on', size: { width: 1920, height: 1080 } },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `npm run dev -- --host ${host} --port ${port}`,
    url: baseURL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
