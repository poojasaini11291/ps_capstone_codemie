// @ts-check
const { defineConfig } = require('@playwright/test');

/**
 * KeyCraft QA harness for KAN-22 (clipboard auto-clear).
 *
 * NOTE ON FRAMEWORK SCOPE:
 * KeyCraft is a pure Tkinter desktop app. Playwright browser automation
 * cannot interact with native Tkinter windows. GUI scenarios (A-C from
 * KAN-22 acceptance criteria) are therefore marked test.fixme() with an
 * ENVIRONMENT/FRAMEWORK MISMATCH explanation.
 *
 * What CAN be tested here:
 *   - CLI flag existence and behaviour via Python subprocess (AC3)
 *   - Core clipboard module logic via Python subprocess
 *   - Full Python unittest regression suite via subprocess (Scenario D)
 */
module.exports = defineConfig({
  testDir: './tests',
  timeout: 90000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  // No browser projects — all tests use Node.js child_process (no page fixture).
  projects: [
    { name: 'node-subprocess' }
  ],
});
