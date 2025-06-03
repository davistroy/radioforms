/**
 * Test Configuration and Utilities
 * 
 * Shared utilities for test data management and cleanup across all E2E tests.
 * Ensures consistent test isolation and prevents test data pollution.
 */

import { Page } from '@playwright/test';

export interface TestForm {
  name: string;
  type?: string;
  data?: Record<string, any>;
  status?: string;
  date?: string;
}

export class TestDataCleanup {
  private static testIds: Set<string> = new Set();
  private static page: Page;

  static initialize(page: Page): void {
    this.page = page;
  }

  static generateTestId(prefix = 'TEST'): string {
    const testId = `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.testIds.add(testId);
    return testId;
  }

  static async cleanupAllTestData(): Promise<void> {
    if (!this.page) return;

    try {
      await this.page.goto('/');
      await this.page.waitForLoadState('networkidle');
      
      for (const testId of this.testIds) {
        await this.cleanupTestId(testId);
      }
      
      this.testIds.clear();
    } catch (error) {
      console.warn('Failed to cleanup test data:', error);
    }
  }

  private static async cleanupTestId(testId: string): Promise<void> {
    try {
      // Search for forms with test ID
      await this.page.click('text=Search');
      await this.page.fill('input[placeholder*="incident"], input[name="search"]', testId);
      await this.page.click('button:has-text("Search")');
      await this.page.waitForTimeout(500);

      // Delete all found forms
      let attempts = 0;
      const maxAttempts = 10;
      
      while (attempts < maxAttempts) {
        const deleteButtons = this.page.locator('button:has-text("Delete"), [data-testid="delete-button"]');
        const count = await deleteButtons.count();
        
        if (count === 0) break;
        
        await deleteButtons.first().click();
        
        // Handle confirmation dialog
        const confirmButton = this.page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
        if (await confirmButton.isVisible({ timeout: 1000 })) {
          await confirmButton.click();
        }
        
        await this.page.waitForTimeout(300);
        attempts++;
      }
    } catch (error) {
      console.warn(`Failed to cleanup test data for ${testId}:`, error);
    }
  }

  static async createTestForm(testId: string, formData: TestForm): Promise<void> {
    if (!this.page) throw new Error('Page not initialized');

    await this.page.click('button:has-text("Create New Form"), button:has-text("New Form")');
    await this.page.fill('input[name="incident_name"], input[placeholder*="incident"]', formData.name);
    
    // Select form type if specified and dropdown exists
    if (formData.type) {
      const formTypeSelect = this.page.locator('select[name="form_type"], select[name="type"]');
      if (await formTypeSelect.isVisible({ timeout: 1000 })) {
        await formTypeSelect.selectOption(formData.type);
      }
    }
    
    // Fill form data if provided
    if (formData.data) {
      const dataField = this.page.locator('textarea[name="form_data"], textarea[name="data"]');
      if (await dataField.isVisible({ timeout: 1000 })) {
        await dataField.fill(JSON.stringify(formData.data));
      }
    }
    
    // Save the form
    await this.page.click('button:has-text("Create Form"), button:has-text("Save"), button:has-text("Submit")');
    await this.page.waitForSelector('.success, .notification, text=/saved|created/i', { timeout: 5000 });
  }

  static async searchForTestForms(testId: string): Promise<number> {
    if (!this.page) return 0;

    await this.page.click('text=Search');
    await this.page.fill('input[placeholder*="incident"], input[name="search"]', testId);
    await this.page.click('button:has-text("Search")');
    await this.page.waitForTimeout(500);

    const results = this.page.locator('[data-testid="search-result"], .search-result, .form-item');
    return await results.count();
  }
}

export class PerformanceMonitor {
  private static measurements: Record<string, number[]> = {};

  static startMeasurement(_name: string): number {
    return Date.now();
  }

  static endMeasurement(name: string, startTime: number): number {
    const duration = Date.now() - startTime;
    
    if (!this.measurements[name]) {
      this.measurements[name] = [];
    }
    
    this.measurements[name].push(duration);
    return duration;
  }

  static getAverageDuration(name: string): number {
    const measurements = this.measurements[name];
    if (!measurements || measurements.length === 0) return 0;
    
    return measurements.reduce((sum, duration) => sum + duration, 0) / measurements.length;
  }

  static getStats(): Record<string, { avg: number; min: number; max: number; count: number }> {
    const stats: Record<string, { avg: number; min: number; max: number; count: number }> = {};
    
    for (const [name, measurements] of Object.entries(this.measurements)) {
      if (measurements.length > 0) {
        stats[name] = {
          avg: this.getAverageDuration(name),
          min: Math.min(...measurements),
          max: Math.max(...measurements),
          count: measurements.length
        };
      }
    }
    
    return stats;
  }

  static logStats(): void {
    const stats = this.getStats();
    console.log('Performance Statistics:');
    console.table(stats);
  }

  static reset(): void {
    this.measurements = {};
  }
}

export class FormValidator {
  static async validateFormExists(page: Page, formName: string): Promise<boolean> {
    try {
      await page.click('text=Search');
      await page.fill('input[placeholder*="incident"], input[name="search"]', formName);
      await page.click('button:has-text("Search")');
      await page.waitForTimeout(500);
      
      const result = page.locator(`text=${formName}`);
      return await result.isVisible();
    } catch {
      return false;
    }
  }

  static async validateFormData(page: Page, formName: string, expectedData: Record<string, any>): Promise<boolean> {
    try {
      // Navigate to the form
      await page.click('text=Search');
      await page.fill('input[placeholder*="incident"], input[name="search"]', formName);
      await page.click('button:has-text("Search")');
      await page.click(`text=${formName}`);
      
      // Check if data field contains expected data
      const dataField = page.locator('textarea[name="form_data"], textarea[name="data"]');
      if (await dataField.isVisible({ timeout: 1000 })) {
        const actualData = await dataField.inputValue();
        try {
          const parsedData = JSON.parse(actualData);
          
          // Check if all expected keys/values exist
          for (const [key, value] of Object.entries(expectedData)) {
            if (parsedData[key] !== value) {
              return false;
            }
          }
          
          return true;
        } catch {
          return false;
        }
      }
      
      return false;
    } catch {
      return false;
    }
  }
}

export const TEST_TIMEOUTS = {
  short: 1000,
  medium: 3000,
  long: 5000,
  veryLong: 10000
} as const;

export const PERFORMANCE_THRESHOLDS = {
  appStartup: 3000,
  formCreation: 2000,
  formLoading: 200,
  searchOperation: 1000,
  uiResponse: 100
} as const;