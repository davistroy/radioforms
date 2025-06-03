# RadioForms E2E Test Suite

## Overview

This directory contains comprehensive end-to-end tests for the RadioForms application, covering the top 20 functional scenarios identified from the product requirements. All tests include proper data cleanup to prevent test data pollution.

## Test Structure

### Core Test Files

1. **`comprehensive-functional.spec.ts`** - Core functionality tests (15 scenarios)
   - Form creation for all ICS types
   - Form editing with validation
   - Multi-criteria search functionality
   - Export in multiple formats (PDF, JSON, ICS-DES)
   - Form duplication and templates
   - Real-time validation
   - Auto-save functionality
   - Advanced search with filters
   - Form status management
   - Performance requirements
   - Error handling and recovery
   - Keyboard navigation
   - Data persistence across sessions
   - Large dataset performance
   - Cross-browser compatibility

2. **`form-templates-bulk.spec.ts`** - Advanced operations (5 scenarios)
   - Form templates creation and usage
   - Bulk operations on multiple forms
   - Import/export backup functionality
   - Form history and audit trail
   - Stress testing with large datasets

3. **`emergency-workflows.spec.ts`** - Emergency responder workflows (existing)
4. **`performance.spec.ts`** - Performance requirements (existing)

### Support Files

- **`test-config.ts`** - Shared utilities for test data management
- **`global-setup.ts`** - Global test environment initialization
- **`global-teardown.ts`** - Complete cleanup after all tests
- **`README.md`** - This documentation file

## Key Features

### ✅ Data Cleanup Strategy

Every test includes automatic cleanup:
- Unique test IDs generated for each test run
- Automatic search and deletion of test data after each test
- Global teardown removes any remaining test data
- Sequential test execution prevents data conflicts

### ✅ Performance Monitoring

Tests verify application meets emergency response requirements:
- App startup < 3 seconds
- Form operations < 1 second
- Search results < 500ms
- UI responsiveness < 100ms

### ✅ Error Recovery

Tests verify graceful error handling:
- Invalid form data validation
- Network/system error recovery
- User input validation
- Consistent error messaging

### ✅ Accessibility

Tests include keyboard navigation and accessibility:
- Tab navigation through forms
- Keyboard shortcuts
- Screen reader compatibility
- WCAG compliance verification

## Installation & Setup

### Prerequisites

1. **Node.js** (Latest LTS version)
2. **RadioForms application** running in development mode
3. **Playwright browsers** installed

### Installation Steps

```bash
# Install Playwright (if not already installed)
npm install --save-dev @playwright/test

# Install Playwright browsers
npx playwright install

# Verify installation
npx playwright --version
```

## Running Tests

### All Tests
```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (visual test runner)
npm run test:e2e:ui
```

### Specific Test Suites
```bash
# Run comprehensive functional tests
npx playwright test comprehensive-functional

# Run bulk operations tests
npx playwright test form-templates-bulk

# Run emergency workflows only
npx playwright test emergency-workflows

# Run performance tests only
npx playwright test performance
```

### Development Mode
```bash
# Run tests in headed mode (visible browser)
npx playwright test --headed

# Run tests with debug mode
npx playwright test --debug

# Run specific test file
npx playwright test comprehensive-functional.spec.ts
```

## Test Configuration

### Playwright Configuration

The `playwright.config.ts` is configured for:
- **Sequential execution** (single worker) to prevent data conflicts
- **Comprehensive reporting** (HTML + list reporters)
- **Automatic cleanup** (global setup/teardown)
- **Cross-browser testing** (Chromium, Firefox, iPad)
- **Performance monitoring** (traces, screenshots, videos)

### Test Timeouts

- **Test timeout**: 60 seconds per test
- **Assertion timeout**: 10 seconds
- **Action timeout**: 15 seconds
- **Navigation timeout**: 30 seconds

## Test Data Management

### TestDataManager Class

Each test uses a `TestDataManager` instance that:
- Generates unique test IDs
- Tracks all created test data
- Automatically cleans up after each test
- Prevents test data pollution

### Example Usage

```typescript
const testDataManager = new TestDataManager(page);
const testId = testDataManager.generateTestId();

// Create test form
await testDataManager.createTestForm(testId, {
  name: `${testId}_TestForm`,
  type: 'ICS-201',
  data: { incident_name: 'Test Incident' }
});

// Automatic cleanup happens in afterEach
```

## Performance Benchmarks

Tests verify the following performance requirements:

| Operation | Requirement | Test Verification |
|-----------|-------------|------------------|
| App Startup | < 3 seconds | ✅ Measured and enforced |
| Form Creation | < 2 seconds | ✅ Measured and enforced |
| Form Loading | < 200ms | ✅ Measured and enforced |
| Search Operations | < 500ms | ✅ Measured and enforced |
| UI Responsiveness | < 100ms | ✅ Measured and enforced |

## Browser Compatibility

Tests run on:
- **Chromium** (Desktop Chrome simulation)
- **Firefox** (Desktop Firefox simulation)
- **iPad Pro** (Tablet compatibility for emergency vehicles)

## Troubleshooting

### Common Issues

1. **Tests failing due to application not ready**
   - Ensure `npm run tauri dev` is running
   - Wait for application to be fully loaded on localhost:1420

2. **Test data conflicts**
   - Tests run sequentially to prevent conflicts
   - Each test generates unique IDs
   - Global cleanup removes all test data

3. **Performance test failures**
   - Check system resources during test execution
   - Verify development server performance
   - Review performance thresholds in test-config.ts

4. **Browser installation issues**
   - Run `npx playwright install` to install browsers
   - Check internet connection for browser downloads
   - Verify disk space for browser installations

### Debug Mode

```bash
# Run single test with full debugging
npx playwright test --debug comprehensive-functional.spec.ts

# Generate trace files for failed tests
npx playwright test --trace=on
```

## Contributing

When adding new tests:

1. **Use TestDataManager** for all test data
2. **Include cleanup** in afterEach hooks
3. **Generate unique test IDs** to prevent conflicts
4. **Follow naming conventions** (TEST_, BULK_, PERF_ prefixes)
5. **Add performance assertions** where appropriate
6. **Include error handling** verification
7. **Test cross-browser compatibility**

## Test Coverage Summary

✅ **20/20 Core Scenarios Covered**

| Scenario | File | Status |
|----------|------|--------|
| 1. Form Creation | comprehensive-functional.spec.ts | ✅ |
| 2. Form Editing | comprehensive-functional.spec.ts | ✅ |
| 3. Form Search | comprehensive-functional.spec.ts | ✅ |
| 4. Form Export | comprehensive-functional.spec.ts | ✅ |
| 5. Form Duplication | comprehensive-functional.spec.ts | ✅ |
| 6. Form Validation | comprehensive-functional.spec.ts | ✅ |
| 7. Auto-save | comprehensive-functional.spec.ts | ✅ |
| 8. Advanced Search | comprehensive-functional.spec.ts | ✅ |
| 9. Status Management | comprehensive-functional.spec.ts | ✅ |
| 10. Performance | comprehensive-functional.spec.ts | ✅ |
| 11. Error Handling | comprehensive-functional.spec.ts | ✅ |
| 12. Keyboard Navigation | comprehensive-functional.spec.ts | ✅ |
| 13. Data Persistence | comprehensive-functional.spec.ts | ✅ |
| 14. Large Dataset | comprehensive-functional.spec.ts | ✅ |
| 15. Cross-Browser | comprehensive-functional.spec.ts | ✅ |
| 16. Form Templates | form-templates-bulk.spec.ts | ✅ |
| 17. Bulk Operations | form-templates-bulk.spec.ts | ✅ |
| 18. Import/Export | form-templates-bulk.spec.ts | ✅ |
| 19. Form History | form-templates-bulk.spec.ts | ✅ |
| 20. Stress Testing | form-templates-bulk.spec.ts | ✅ |

All tests include comprehensive data cleanup and follow enterprise testing standards.