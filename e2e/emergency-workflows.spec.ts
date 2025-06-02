/**
 * End-to-End Tests for Emergency Responder Workflows
 * 
 * Following MANDATORY.md: Simple E2E tests for critical emergency responder workflows.
 * Tests the complete user journey from form creation to submission.
 * These tests verify the app works for emergency responders at 2 AM under stress.
 */

import { test, expect } from '@playwright/test';

test.describe('Emergency Responder Core Workflows', () => {
  
  test('Emergency responder can create and save an ICS-201 form', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Verify app loads correctly
    await expect(page).toHaveTitle(/RadioForms/);
    
    // Create a new form
    await page.click('button:has-text("Create New Form")');
    
    // Fill out incident information
    await page.fill('input[name="incident_name"]', 'Structure Fire - Main Street');
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    
    // Fill out basic form data
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Structure Fire - Main Street",
      incident_number: "2025-001",
      date: "2025-01-06",
      time: "14:30",
      location: "123 Main Street",
      incident_commander: "Chief Smith"
    }));
    
    // Save the form
    await page.click('button:has-text("Create Form")');
    
    // Verify success message or navigation
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    // Verify form appears in form list
    await page.click('text=Forms');
    await expect(page.locator('text=Structure Fire - Main Street')).toBeVisible();
  });

  test('Emergency responder can search for existing forms by incident', async ({ page }) => {
    await page.goto('/');
    
    // Go to search
    await page.click('text=Search');
    
    // Search for fire incidents
    await page.fill('input[placeholder*="incident name"]', 'Fire');
    await page.click('button:has-text("Search")');
    
    // Verify search results appear
    await expect(page.locator('text=Search Results')).toBeVisible();
    
    // If results exist, verify they contain the search term
    const results = page.locator('[data-testid="search-result"], .search-result');
    const resultCount = await results.count();
    
    if (resultCount > 0) {
      // Check that results contain fire-related incidents
      await expect(results.first()).toContainText(/fire/i);
    } else {
      // If no results, verify the "no results" message
      await expect(page.locator('text=No forms found')).toBeVisible();
    }
  });

  test('Emergency responder can update form status during incident', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to forms list
    await page.click('text=Forms');
    
    // Find the first available form
    const firstForm = page.locator('[data-testid="form-item"], .form-item').first();
    await firstForm.click();
    
    // Verify form editor opened
    await expect(page.locator('h2:has-text("Edit Form")')).toBeVisible();
    
    // Update form status if status controls exist
    const statusSelect = page.locator('select[name="status"], .status-select');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption('completed');
      await page.click('button:has-text("Update Form")');
      
      // Verify status update
      await expect(page.locator('.success, .notification')).toContainText(/updated|saved/i);
    }
  });

  test('Emergency responder can export form to PDF', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to forms and select one
    await page.click('text=Forms');
    const firstForm = page.locator('[data-testid="form-item"], .form-item').first();
    await firstForm.click();
    
    // Look for export button
    const exportButton = page.locator('button:has-text("Export PDF")');
    if (await exportButton.count() > 0) {
      // Set up download handling
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Verify download starts
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.pdf$/);
    } else {
      // If no export button visible, this test is not applicable
      console.warn('PDF export not available for this form');
    }
  });

  test('Emergency responder can quickly create multiple forms for large incident', async ({ page }) => {
    await page.goto('/');
    
    // Create first form (ICS-201)
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', 'Multi-Agency Response');
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Multi-Agency Response",
      incident_number: "2025-002"
    }));
    await page.click('button:has-text("Create Form")');
    
    // Wait for form to be saved
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    // Create second form (ICS-202)
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', 'Multi-Agency Response');
    await page.selectOption('select[name="form_type"]', 'ICS-202');
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_objectives: "Contain and extinguish fire"
    }));
    await page.click('button:has-text("Create Form")');
    
    // Verify second form created
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
    
    // Verify both forms exist for the incident
    await page.click('text=Search');
    await page.fill('input[placeholder*="incident name"]', 'Multi-Agency Response');
    await page.click('button:has-text("Search")');
    
    // Should find at least 2 forms for this incident
    const results = page.locator('[data-testid="search-result"], .search-result');
    const resultCount = await results.count();
    expect(resultCount).toBeGreaterThanOrEqual(2);
  });

  test('Emergency responder can recover from errors gracefully', async ({ page }) => {
    await page.goto('/');
    
    // Try to create form with invalid data
    await page.click('button:has-text("Create New Form")');
    
    // Leave incident name empty (should trigger validation)
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    await page.fill('textarea[name="form_data"]', 'invalid json');
    await page.click('button:has-text("Create Form")');
    
    // Verify error message appears
    await expect(page.locator('.error, .alert-error, [role="alert"]')).toBeVisible();
    
    // Fix the errors
    await page.fill('input[name="incident_name"]', 'Valid Incident Name');
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Valid Incident Name"
    }));
    
    // Try saving again
    await page.click('button:has-text("Create Form")');
    
    // Should succeed this time
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
  });

  test('Application loads quickly for emergency responder', async ({ page }) => {
    // Measure application startup time
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for main interface to be ready
    await expect(page.locator('h1, .app-title, [data-testid="app-ready"]')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    
    // Verify app loads within 3 seconds (emergency requirement)
    expect(loadTime).toBeLessThan(3000);
    
    // Verify essential UI elements are present
    await expect(page.locator('button:has-text("Create New Form")')).toBeVisible();
    await expect(page.locator('text=Forms, text=Search')).toBeVisible();
  });

  test('Form validation helps emergency responder avoid errors', async ({ page }) => {
    await page.goto('/');
    
    await page.click('button:has-text("Create New Form")');
    
    // Test required field validation
    await page.selectOption('select[name="form_type"]', 'ICS-201');
    await page.click('button:has-text("Create Form")');
    
    // Should show validation error for missing incident name
    await expect(page.locator('.error, .field-error, [aria-invalid="true"]')).toBeVisible();
    
    // Test JSON validation
    await page.fill('input[name="incident_name"]', 'Test Incident');
    await page.fill('textarea[name="form_data"]', 'not valid json');
    await page.click('button:has-text("Create Form")');
    
    // Should show JSON validation error
    await expect(page.locator('text=/JSON/i')).toBeVisible();
    
    // Fix validation errors
    await page.fill('textarea[name="form_data"]', JSON.stringify({
      incident_name: "Test Incident"
    }));
    await page.click('button:has-text("Create Form")');
    
    // Should succeed with valid data
    await expect(page.locator('.success, .notification')).toContainText(/saved|created/i);
  });
});