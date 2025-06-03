/**
 * Global Setup for E2E Tests
 * 
 * Ensures clean test environment before running comprehensive E2E tests.
 * Handles application initialization and cleanup of any existing test data.
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('Starting RadioForms E2E Test Setup...');
  
  // Get the base URL from config
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:1420';
  
  try {
    // Launch browser to verify application is running
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    console.log('Waiting for RadioForms application to be ready...');
    
    // Wait for application to be accessible
    let retries = 0;
    const maxRetries = 30; // 30 attempts = ~60 seconds
    
    while (retries < maxRetries) {
      try {
        await page.goto(baseURL, { timeout: 10000 });
        
        // Check if application loaded successfully or is in error state
        const errorHeading = await page.locator('h1:has-text("Error")').isVisible({ timeout: 5000 });
        
        if (errorHeading) {
          console.warn('Application is in error state - backend not ready yet');
          throw new Error('Backend not ready - likely still compiling');
        }
        
        // Wait for the main application interface to load
        await page.waitForSelector('h1:has-text("RadioForms")', { timeout: 10000 });
        
        console.log('RadioForms application is ready!');
        break;
      } catch (error) {
        retries++;
        console.log(`Attempt ${retries}/${maxRetries}: Waiting for application...`);
        
        if (retries >= maxRetries) {
          throw new Error(`RadioForms application failed to start after ${maxRetries} attempts. Error: ${error}`);
        }
        
        await page.waitForTimeout(2000); // Wait 2 seconds before retry
      }
    }
    
    // Clean up any existing test data from previous runs
    console.log('Cleaning up any existing test data...');
    
    try {
      // Search for any existing test data
      await page.click('button:has-text("Search")', { timeout: 5000 });
      await page.fill('input[placeholder*="incident"], input[name="search"]', 'TEST_');
      await page.click('button:has-text("Search")');
      
      // Wait a moment for search results
      await page.waitForTimeout(1000);
      
      // Clean up any found test data
      const deleteButtons = page.locator('button:has-text("Delete"), [data-testid="delete-button"]');
      const count = await deleteButtons.count();
      
      if (count > 0) {
        console.log(`Found ${count} existing test forms to clean up...`);
        
        for (let i = 0; i < count; i++) {
          try {
            await deleteButtons.first().click();
            
            // Handle confirmation dialog
            const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
            if (await confirmButton.isVisible({ timeout: 2000 })) {
              await confirmButton.click();
            }
            
            await page.waitForTimeout(500);
          } catch (error) {
            console.warn(`Failed to delete test form ${i + 1}:`, error);
          }
        }
        
        console.log('Test data cleanup completed.');
      } else {
        console.log('No existing test data found.');
      }
    } catch (error) {
      console.warn('Failed to clean existing test data:', error);
    }
    
    // Verify application is in a clean state
    await page.goto(baseURL);
    await page.waitForSelector('h1:has-text("RadioForms")', { timeout: 10000 });
    
    console.log('RadioForms E2E Test Setup completed successfully!');
    
    await browser.close();
    
  } catch (error) {
    console.error('Global setup failed:', error);
    throw error;
  }
}

export default globalSetup;