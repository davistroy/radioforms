/**
 * Basic UI Test - Check what the actual UI looks like
 */

import { test, expect } from '@playwright/test';

test.describe('Basic UI Check', () => {
  test('should load the application and show main elements', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot to see what we're working with
    await page.screenshot({ path: 'debug-ui.png', fullPage: true });
    
    // Check for main title
    await expect(page.locator('h1')).toBeVisible();
    
    // Print the page title
    const title = await page.locator('h1').textContent();
    console.log('Page title:', title);
    
    // Check for navigation buttons
    const navButtons = page.locator('nav button, header button');
    const navCount = await navButtons.count();
    console.log('Navigation buttons found:', navCount);
    
    for (let i = 0; i < navCount; i++) {
      const buttonText = await navButtons.nth(i).textContent();
      console.log(`Button ${i + 1}:`, buttonText);
    }
    
    // Check for any forms on the page
    const forms = page.locator('form');
    const formCount = await forms.count();
    console.log('Forms found:', formCount);
    
    // Check for any buttons
    const allButtons = page.locator('button');
    const buttonCount = await allButtons.count();
    console.log('Total buttons found:', buttonCount);
    
    // List all button text for first 10 buttons
    for (let i = 0; i < Math.min(buttonCount, 10); i++) {
      const buttonText = await allButtons.nth(i).textContent();
      console.log(`All Button ${i + 1}:`, buttonText);
    }
  });
});