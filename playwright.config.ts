/**
 * Playwright Configuration for RadioForms E2E Tests
 * 
 * Following MANDATORY.md: Simple configuration for emergency responder workflow testing.
 * Tests run against the actual Tauri application to verify real-world usage.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Ensure tests run sequentially to prevent data conflicts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker to ensure test data isolation
  reporter: [['html'], ['list']],
  timeout: 60000, // 60 seconds per test
  expect: {
    timeout: 10000, // 10 seconds for assertions
  },
  // globalSetup: './e2e/global-setup.ts',
  // globalTeardown: './e2e/global-teardown.ts',
  
  use: {
    // Test against the development server
    baseURL: 'http://localhost:1420',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000, // 15 seconds for actions
    navigationTimeout: 30000, // 30 seconds for navigation
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
    timeout: 300 * 1000, // 5 minutes for first-time Rust compilation
    reuseExistingServer: !process.env.CI,
  },
});