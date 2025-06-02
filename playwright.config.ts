/**
 * Playwright Configuration for RadioForms E2E Tests
 * 
 * Following MANDATORY.md: Simple configuration for emergency responder workflow testing.
 * Tests run against the actual Tauri application to verify real-world usage.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    // Test against the development server
    baseURL: 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Test on Firefox for compatibility
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    // Test tablet size for emergency vehicle use
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
    },
  ],

  // Start the Tauri dev server before running tests
  webServer: {
    command: 'npm run tauri dev',
    port: 1420,
    timeout: 120 * 1000, // 2 minutes for Tauri to start
    reuseExistingServer: !process.env.CI,
  },
});