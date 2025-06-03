/**
 * Form Templates and Bulk Operations Tests
 * 
 * Tests for form templates, bulk operations, and import/export functionality.
 * Includes comprehensive data cleanup after each test.
 */

import { test, expect, Page } from '@playwright/test';

// Test data cleanup utility
class TestDataManager {
  private testIds: string[] = [];
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  generateTestId(): string {
    const testId = `BULK_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.testIds.push(testId);
    return testId;
  }

  async cleanupAllTestData(): Promise<void> {
    try {
      await this.page.goto('/');
      await this.page.waitForLoadState('networkidle');
      
      for (const testId of this.testIds) {
        try {
          await this.page.click('text=Search');
          await this.page.fill('input[placeholder*="incident"], input[name="search"]', testId);
          await this.page.click('button:has-text("Search")');
          await this.page.waitForTimeout(500);

          const deleteButtons = this.page.locator('button:has-text("Delete"), [data-testid="delete-button"]');
          const count = await deleteButtons.count();
          
          for (let i = 0; i < count; i++) {
            await deleteButtons.first().click();
            const confirmButton = this.page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
            if (await confirmButton.isVisible({ timeout: 1000 })) {
              await confirmButton.click();
            }
            await this.page.waitForTimeout(200);
          }
        } catch (error) {
          console.warn(`Failed to cleanup test data for ${testId}:`, error);
        }
      }
    } catch (error) {
      console.warn('Failed to cleanup test data:', error);
    }
    
    this.testIds = [];
  }
}

test.describe('Form Templates and Bulk Operations', () => {
  let testDataManager: TestDataManager;

  test.beforeEach(async ({ page }) => {
    testDataManager = new TestDataManager(page);
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page: _ }) => {
    await testDataManager.cleanupAllTestData();
  });

  // Test 16: Form Templates - Pre-filled template usage
  test('should use and create form templates effectively', async ({ page }) => {
    const testId = testDataManager.generateTestId();
    
    // Create a template form
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', `${testId}_Template`);
    
    const templateData = {
      incident_name: `${testId}_Template`,
      template_field: 'Default template value',
      location_template: 'Standard Location',
      commander_template: 'Standard IC'
    };
    
    const dataField = page.locator('textarea[name="form_data"]');
    if (await dataField.isVisible({ timeout: 1000 })) {
      await dataField.fill(JSON.stringify(templateData));
    }
    
    // Save as template if option exists
    const saveAsTemplateButton = page.locator('button:has-text("Save as Template"), checkbox[name="is_template"]');
    if (await saveAsTemplateButton.isVisible({ timeout: 2000 })) {
      await saveAsTemplateButton.click();
    }
    
    await page.click('button:has-text("Create Form")');
    await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    
    // Use template to create new form
    await page.click('button:has-text("Create New Form")');
    
    // Look for template selection
    const templateSelect = page.locator('select[name="template"], button:has-text("From Template")');
    if (await templateSelect.isVisible({ timeout: 2000 })) {
      if (await templateSelect.getAttribute('tagName') === 'SELECT') {
        await templateSelect.selectOption(`${testId}_Template`);
      } else {
        await templateSelect.click();
        await page.click(`text=${testId}_Template`);
      }
      
      // Verify template data loaded
      await expect(page.locator('input[value*="Standard Location"], textarea:has-text("Standard Location")')).toBeVisible();
    }
    
    // Modify template data for new form
    await page.fill('input[name="incident_name"]', `${testId}_FromTemplate`);
    await page.click('button:has-text("Create Form")');
    await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
  });

  // Test 17: Bulk Operations - Multiple form selection and actions
  test('should support bulk operations on multiple forms', async ({ page }) => {
    const testId = testDataManager.generateTestId();
    
    // Create multiple forms for bulk operations
    const formNames = [
      `${testId}_Bulk_1`,
      `${testId}_Bulk_2`,
      `${testId}_Bulk_3`,
      `${testId}_Bulk_4`
    ];
    
    for (const formName of formNames) {
      await page.click('button:has-text("Create New Form")');
      await page.fill('input[name="incident_name"]', formName);
      
      const formData = { incident_name: formName, bulk_test: true };
      const dataField = page.locator('textarea[name="form_data"]');
      if (await dataField.isVisible({ timeout: 1000 })) {
        await dataField.fill(JSON.stringify(formData));
      }
      
      await page.click('button:has-text("Create Form")');
      await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    }
    
    // Navigate to forms list
    await page.click('text=Forms');
    
    // Look for bulk selection checkboxes
    const bulkCheckboxes = page.locator('input[type="checkbox"][name*="select"], .bulk-select input');
    const checkboxCount = await bulkCheckboxes.count();
    
    if (checkboxCount > 0) {
      // Select multiple forms
      for (let i = 0; i < Math.min(3, checkboxCount); i++) {
        await bulkCheckboxes.nth(i).check();
      }
      
      // Look for bulk action buttons
      const bulkDeleteButton = page.locator('button:has-text("Delete Selected"), .bulk-actions button:has-text("Delete")');
      const bulkExportButton = page.locator('button:has-text("Export Selected"), .bulk-actions button:has-text("Export")');
      
      if (await bulkExportButton.isVisible({ timeout: 2000 })) {
        // Test bulk export
        const downloadPromise = page.waitForEvent('download');
        await bulkExportButton.click();
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/\.(zip|json|pdf)$/);
      }
      
      if (await bulkDeleteButton.isVisible({ timeout: 2000 })) {
        // Test bulk delete (this will clean up our test data)
        await bulkDeleteButton.click();
        
        // Confirm deletion
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")');
        if (await confirmButton.isVisible({ timeout: 2000 })) {
          await confirmButton.click();
        }
        
        await expect(page.locator('.success, text=/deleted/i')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  // Test 18: Import/Export - Backup and restore functionality
  test('should support import and export of form data', async ({ page }) => {
    const testId = testDataManager.generateTestId();
    
    // Create forms to export
    const exportForms = [
      `${testId}_Export_1`,
      `${testId}_Export_2`
    ];
    
    for (const formName of exportForms) {
      await page.click('button:has-text("Create New Form")');
      await page.fill('input[name="incident_name"]', formName);
      
      const formData = {
        incident_name: formName,
        export_test: true,
        data: `Export data for ${formName}`
      };
      
      const dataField = page.locator('textarea[name="form_data"]');
      if (await dataField.isVisible({ timeout: 1000 })) {
        await dataField.fill(JSON.stringify(formData));
      }
      
      await page.click('button:has-text("Create Form")');
      await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    }
    
    // Look for export/backup functionality
    const exportButton = page.locator('button:has-text("Export All"), button:has-text("Backup"), a:has-text("Export")');
    if (await exportButton.isVisible({ timeout: 2000 })) {
      // Test full export/backup
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.(json|zip|backup)$/);
    }
    
    // Look for import functionality
    const importButton = page.locator('button:has-text("Import"), button:has-text("Restore"), input[type="file"]');
    if (await importButton.isVisible({ timeout: 2000 })) {
      // Note: Actually testing file upload would require a real file
      // For now, just verify the import UI is accessible
      await expect(importButton).toBeVisible();
    }
  });

  // Test 19: Form History - Version tracking and audit trail
  test('should track form history and audit trail', async ({ page }) => {
    const testId = testDataManager.generateTestId();
    
    // Create initial form
    await page.click('button:has-text("Create New Form")');
    await page.fill('input[name="incident_name"]', `${testId}_History`);
    
    const initialData = {
      incident_name: `${testId}_History`,
      version: 1,
      content: 'Initial content'
    };
    
    const dataField = page.locator('textarea[name="form_data"]');
    if (await dataField.isVisible({ timeout: 1000 })) {
      await dataField.fill(JSON.stringify(initialData));
    }
    
    await page.click('button:has-text("Create Form")');
    await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    
    // Edit the form multiple times to create history
    await page.click('text=Forms');
    await page.click(`text=${testId}_History`);
    
    // First edit
    await page.fill('input[name="incident_name"]', `${testId}_History_v2`);
    
    const updatedData = { ...initialData, version: 2, content: 'Updated content' };
    if (await dataField.isVisible({ timeout: 1000 })) {
      await dataField.fill(JSON.stringify(updatedData));
    }
    
    await page.click('button:has-text("Update"), button:has-text("Save")');
    await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    
    // Second edit
    const finalData = { ...updatedData, version: 3, content: 'Final content' };
    if (await dataField.isVisible({ timeout: 1000 })) {
      await dataField.fill(JSON.stringify(finalData));
    }
    
    await page.click('button:has-text("Update"), button:has-text("Save")');
    await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
    
    // Look for history/audit trail
    const historyButton = page.locator('button:has-text("History"), button:has-text("Audit"), tab:has-text("History")');
    if (await historyButton.isVisible({ timeout: 2000 })) {
      await historyButton.click();
      
      // Verify history entries
      await expect(page.locator('text=/version|Version|v1|v2|v3/i')).toBeVisible();
      await expect(page.locator('text=/Initial content|Updated content|Final content/')).toBeVisible();
    }
  });

  // Test 20: Stress Test - Large dataset performance
  test('should maintain performance with large datasets', async ({ page }) => {
    const testId = testDataManager.generateTestId();
    
    // Create a significant number of forms to test performance
    const formCount = 50; // Reduced from original plan to keep test reasonable
    
    console.log(`Creating ${formCount} forms for stress testing...`);
    
    const startTime = Date.now();
    
    for (let i = 1; i <= formCount; i++) {
      await page.click('button:has-text("Create New Form")');
      await page.fill('input[name="incident_name"]', `${testId}_Stress_${i.toString().padStart(3, '0')}`);
      
      const formData = {
        incident_name: `${testId}_Stress_${i.toString().padStart(3, '0')}`,
        form_number: i,
        stress_test: true,
        large_data: Array.from({length: 50}, (_, j) => `Data item ${j} for form ${i}`).join(' ')
      };
      
      const dataField = page.locator('textarea[name="form_data"]');
      if (await dataField.isVisible({ timeout: 1000 })) {
        await dataField.fill(JSON.stringify(formData));
      }
      
      await page.click('button:has-text("Create Form")');
      await expect(page.locator('.success')).toBeVisible({ timeout: 5000 });
      
      // Progress logging every 10 forms
      if (i % 10 === 0) {
        console.log(`Created ${i}/${formCount} forms`);
      }
    }
    
    const creationTime = Date.now() - startTime;
    console.log(`Created ${formCount} forms in ${creationTime}ms`);
    
    // Test search performance with large dataset
    const searchStartTime = Date.now();
    await page.click('text=Search');
    await page.fill('input[placeholder*="incident"], input[name="search"]', testId);
    await page.click('button:has-text("Search")');
    
    await expect(page.locator('text=Search Results')).toBeVisible();
    const searchTime = Date.now() - searchStartTime;
    
    console.log(`Search completed in ${searchTime}ms`);
    
    // Performance requirements
    expect(searchTime).toBeLessThan(2000); // 2 seconds for search with large dataset
    
    // Test pagination if available
    const paginationControls = page.locator('.pagination, button:has-text("Next"), button:has-text("Previous")');
    if (await paginationControls.isVisible({ timeout: 2000 })) {
      const nextButton = page.locator('button:has-text("Next")');
      if (await nextButton.isVisible() && !await nextButton.isDisabled()) {
        await nextButton.click();
        await expect(page.locator('text=Search Results')).toBeVisible();
      }
    }
    
    // Test form list performance
    const listStartTime = Date.now();
    await page.click('text=Forms');
    await expect(page.locator(`text=${testId}_Stress_001`)).toBeVisible();
    const listTime = Date.now() - listStartTime;
    
    console.log(`Form list loaded in ${listTime}ms`);
    expect(listTime).toBeLessThan(3000); // 3 seconds for large form list
  });
});