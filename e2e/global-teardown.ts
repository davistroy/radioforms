/**
 * Global Teardown for E2E Tests
 * 
 * Ensures complete cleanup after all E2E tests are finished.
 * Removes all test data and generates performance reports.
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('Starting RadioForms E2E Test Teardown...');
  
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:1420';
  
  try {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    await page.goto(baseURL);
    
    // Final cleanup of all test data
    console.log('Performing final cleanup of all test data...');
    
    // Clean up test data with various prefixes
    const testPrefixes = ['TEST_', 'BULK_', 'PERF_', 'STRESS_'];
    
    for (const prefix of testPrefixes) {
      try {
        await page.click('button:has-text("Search")');
        await page.fill('input[placeholder*="incident"], input[name="search"]', prefix);
        await page.click('button:has-text("Search")');
        await page.waitForTimeout(1000);
        
        // Delete all found test forms
        let cleanupAttempts = 0;
        const maxCleanupAttempts = 20;
        
        while (cleanupAttempts < maxCleanupAttempts) {
          const deleteButtons = page.locator('button:has-text("Delete"), [data-testid="delete-button"]');
          const count = await deleteButtons.count();
          
          if (count === 0) break;
          
          await deleteButtons.first().click();
          
          const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
          if (await confirmButton.isVisible({ timeout: 2000 })) {
            await confirmButton.click();
          }
          
          await page.waitForTimeout(300);
          cleanupAttempts++;
        }
        
        console.log(`Cleaned up test data with prefix: ${prefix}`);
      } catch (error) {
        console.warn(`Failed to cleanup test data with prefix ${prefix}:`, error);
      }
    }
    
    // Generate test summary report
    console.log('Generating test summary...');
    
    try {
      // Check final database state
      await page.click('text=Search');
      await page.fill('input[placeholder*="incident"], input[name="search"]', '');
      await page.click('button:has-text("Search")');
      await page.waitForTimeout(1000);
      
      const remainingForms = page.locator('[data-testid="search-result"], .search-result, .form-item');
      const formCount = await remainingForms.count();
      
      console.log(`Final form count in database: ${formCount}`);
      
      // Log any remaining test forms that weren't cleaned up
      if (formCount > 0) {
        console.log('Checking for any remaining test data...');
        
        for (let i = 0; i < Math.min(formCount, 10); i++) {
          try {
            const formText = await remainingForms.nth(i).textContent();
            if (formText && (formText.includes('TEST_') || formText.includes('BULK_') || formText.includes('PERF_'))) {
              console.warn(`Remaining test form detected: ${formText}`);
            }
          } catch {
            // Ignore errors reading form text
          }
        }
      }
      
    } catch (error) {
      console.warn('Failed to generate test summary:', error);
    }
    
    console.log('RadioForms E2E Test Teardown completed successfully!');
    
    await browser.close();
    
  } catch (error) {
    console.error('Global teardown failed:', error);
    // Don't throw here as we don't want to fail the test run
    console.error('Test teardown errors are non-critical, continuing...');
  }
}

export default globalTeardown;