/**
 * Performance Tests for Emergency Responder Requirements
 * 
 * Following MANDATORY.md: Simple performance tests for emergency response timing.
 * Verifies the app meets the "2 AM emergency responder" performance requirements.
 */

import { test, expect } from '@playwright/test';

test.describe('Emergency Responder Performance Requirements', () => {
  
  test('Application starts within 3 seconds', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for app to be interactive
    await expect(page.locator('button:has-text("Create New Form")')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    
    // MANDATORY.md requirement: < 3 seconds startup
    expect(loadTime).toBeLessThan(3000);
    console.warn(`App startup time: ${loadTime}ms`);
  });

  test('Form creation completes within 1 second', async ({ page }) => {
    await page.goto('/');
    
    // Pre-fill form data
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', 'Performance Test Incident');
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Performance Test Incident",
      incident_number: "PERF-001"
    }));
    
    // Measure form save time
    const startTime = Date.now();
    
    await page.click('button:has-text("Create Form")');
    
    // Wait for success indication
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    const saveTime = Date.now() - startTime;
    
    // Emergency requirement: form operations < 1 second
    expect(saveTime).toBeLessThan(1000);
    console.warn(`Form save time: ${saveTime}ms`);
  });

  test('Search results appear within 500ms', async ({ page }) => {
    await page.goto('/');
    
    // Go to search
    await page.click('text=Search');
    
    // Measure search time
    const startTime = Date.now();
    
    await page.fill('input[placeholder*="incident name"]', 'Test');
    await page.click('button:has-text("Search")');
    
    // Wait for search results to appear
    await expect(page.locator('text=Search Results')).toBeVisible();
    
    const searchTime = Date.now() - startTime;
    
    // Emergency requirement: search < 500ms
    expect(searchTime).toBeLessThan(500);
    console.warn(`Search time: ${searchTime}ms`);
  });

  test('Form loading is under 200ms', async ({ page }) => {
    await page.goto('/');
    
    // First create a form to test loading
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', 'Load Test Incident');
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Load Test Incident"
    }));
    await page.click('button:has-text("Create Form")');
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    // Navigate to forms list
    await page.click('text=Forms');
    
    // Measure form loading time
    const startTime = Date.now();
    
    const firstForm = page.locator('[data-testid="form-item"], .form-item').first();
    await firstForm.click();
    
    // Wait for form editor to load
    await expect(page.locator('input[name="incident_name"]')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    
    // Performance requirement: form loading < 200ms
    expect(loadTime).toBeLessThan(200);
    console.warn(`Form load time: ${loadTime}ms`);
  });

  test('UI responds to clicks within 100ms', async ({ page }) => {
    await page.goto('/');
    
    // Test button click responsiveness
    const button = page.locator('button:has-text("Create New Form")');
    
    const startTime = Date.now();
    await button.click();
    
    // Wait for form dialog/page to appear
    await expect(page.locator('input[name="incident_name"]')).toBeVisible();
    
    const responseTime = Date.now() - startTime;
    
    // UI responsiveness requirement: < 100ms
    expect(responseTime).toBeLessThan(100);
    console.warn(`UI response time: ${responseTime}ms`);
  });

  test('Application uses minimal memory', async ({ page }) => {
    await page.goto('/');
    
    // Create several forms to test memory usage
    for (let i = 1; i <= 5; i++) {
      await page.click('button:has-text("Create New Form")');
      await page.fill('input[name="incident_name"]', `Memory Test ${i}`);
      await page.selectOption('select[name="form_type"]', 'ICS-201');
      await page.fill('textarea[name="form_data"]', JSON.stringify({
        incident_name: `Memory Test ${i}`,
        data: 'A'.repeat(1000) // Some test data
      }));
      await page.click('button:has-text("Create Form")');
      await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    }
    
    // Check JavaScript heap usage
    const metrics = await page.evaluate(() => {
      if ('memory' in window.performance) {
        return (window.performance as any).memory;
      }
      return null;
    });
    
    if (metrics && metrics.usedJSHeapSize) {
      const memoryMB = metrics.usedJSHeapSize / (1024 * 1024);
      console.warn(`JavaScript heap usage: ${memoryMB.toFixed(2)} MB`);
      
      // Should use reasonable amount of memory (< 100MB for frontend)
      expect(memoryMB).toBeLessThan(100);
    }
  });

  test('Large form data saves efficiently', async ({ page }) => {
    await page.goto('/');
    
    // Create form with large amount of data
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', 'Large Data Test');
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    
    // Create a larger JSON payload (simulating complex incident data)
    const largeData = {
      incident_name: "Large Data Test",
      incident_number: "LARGE-001",
      personnel: Array.from({length: 50}, (_, i) => ({
        name: `Responder ${i + 1}`,
        role: `Role ${i + 1}`,
        unit: `Unit ${Math.floor(i / 10) + 1}`
      })),
      resources: Array.from({length: 20}, (_, i) => ({
        type: `Resource ${i + 1}`,
        quantity: i + 1,
        status: "Available"
      })),
      timeline: Array.from({length: 30}, (_, i) => ({
        time: `14:${30 + i}`,
        event: `Event ${i + 1}`,
        description: `Description for event ${i + 1}`.repeat(5)
      }))
    };
    
    await page.fill('textarea[name="form_data"]', JSON.stringify(largeData));
    
    // Measure save time for large data
    const startTime = Date.now();
    
    await page.click('button:has-text("Create Form")');
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    const saveTime = Date.now() - startTime;
    
    // Should still save large forms efficiently (< 2 seconds)
    expect(saveTime).toBeLessThan(2000);
    console.warn(`Large form save time: ${saveTime}ms`);
  });
});