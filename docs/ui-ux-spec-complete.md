# Enterprise UI/UX Design Specification v2.0

_A Production-Ready, Accessible, Scalable Design System for Business Applications_

**Version:** 2.0  
**Last Updated:** May 2025  
**Status:** Production Ready

---

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Design Principles](#design-principles)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Layout & Spacing](#layout--spacing)
6. [Component Library](#component-library)
   - [Buttons](#buttons)
   - [Forms](#forms)
   - [Tables](#tables)
   - [Modals](#modals)
   - [Navigation](#navigation)
   - [Cards & Lists](#cards--lists)
   - [Alerts & Notifications](#alerts--notifications)
7. [Common UI Patterns](#common-ui-patterns)
8. [Error Handling](#error-handling)
9. [Accessibility Guidelines](#accessibility-guidelines)
10. [Performance Standards](#performance-standards)
11. [Security Patterns](#security-patterns)
12. [Responsive Design](#responsive-design)
13. [Dark Mode & Theming](#dark-mode--theming)
14. [Testing Checklist](#testing-checklist)
15. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
16. [Quick Reference](#quick-reference)

---

## Quick Start Guide

### Essential Setup (Copy This First!)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="enterprise-ui.css">
</head>
<body>
  <!-- Your app content -->
</body>
</html>
```

### Base CSS Variables (Required)

```css
:root {
  /* Colors */
  --color-primary: #71639e;
  --color-primary-hover: #5d5184;
  --color-secondary: #714B67;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-warning: #ffac00;
  --color-info: #17a2b8;
  
  /* Spacing (8px base) */
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  
  /* Typography */
  --font-system: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: SFMono-Regular, Menlo, Monaco, monospace;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  
  /* Focus */
  --focus-ring: 0 0 0 2px rgba(113, 99, 158, 0.5);
}
```

[↑ Back to top](#table-of-contents)

---

## Design Principles

### 1. Accessibility First
Every component must work for every user, regardless of their abilities.

### 2. Performance Matters
Components must render quickly and efficiently.

### 3. Mobile First
Design for mobile, enhance for desktop.

### 4. Consistency Wins
Use the same patterns everywhere.

### 5. Clear Over Clever
Obvious UI is good UI.

[↑ Back to top](#table-of-contents)

---

## Color System

### Primary Colors

```css
/* Primary Palette - All WCAG AA Compliant */
--color-primary: #71639e;      /* Use with white text */
--color-primary-hover: #5d5184;
--color-primary-active: #4a3f6b;

--color-secondary: #714B67;    /* Use with white text */
--color-secondary-hover: #5c3d54;
--color-secondary-active: #493041;
```

### Semantic Colors

```css
/* Status Colors */
--color-success: #28a745;      /* ✅ Positive actions/states */
--color-info: #17a2b8;         /* ℹ️ Informational */
--color-warning: #ffac00;      /* ⚠️ Caution needed */
--color-danger: #dc3545;       /* ❌ Errors/destructive */
```

### Grayscale

```css
/* Neutral Colors */
--gray-50: #f8f9fa;   /* Backgrounds */
--gray-100: #e9ecef;  /* Borders */
--gray-200: #dee2e6;  /* Disabled backgrounds */
--gray-300: #ced4da;  /* Disabled borders */
--gray-400: #adb5bd;  /* Placeholder text */
--gray-500: #8b92a9;  /* Muted text */
--gray-600: #6c757d;  /* Secondary text */
--gray-700: #495057;  /* Body text */
--gray-800: #343a40;  /* Headings */
--gray-900: #212529;  /* Primary text */
```

### Color Usage Guidelines

| Element | Color | Contrast Ratio | Usage |
|---------|-------|----------------|-------|
| Primary Button | `--color-primary` | 4.5:1 | Main actions |
| Body Text | `--gray-700` | 7:1 | Readable content |
| Disabled State | `--gray-400` | 3:1 | Inactive elements |
| Error Text | `--color-danger` | 4.5:1 | Error messages |
| Focus Ring | `--color-primary` + 50% opacity | N/A | Keyboard focus |

> ⚠️ **Common Mistake**: Using color alone to convey meaning
> 
> **Do this instead**: Always pair color with icons, text, or patterns
> ```html
> <!-- ❌ Bad -->
> <div class="status-red"></div>
> 
> <!-- ✅ Good -->
> <div class="status-error">
>   <svg class="icon-error" aria-hidden="true">...</svg>
>   <span>Error: Invalid input</span>
> </div>
> ```

[↑ Back to top](#table-of-contents)

---

## Typography

### Font Stack

```css
/* System Font Stack (Performance Optimized) */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", 
               "Segoe UI Emoji", "Segoe UI Symbol";
}

/* Monospace for Code */
code, pre {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 
               "Liberation Mono", "Courier New", monospace;
}
```

### Type Scale

```css
/* Headings */
.h1 { font-size: 2.5rem; line-height: 1.2; font-weight: 600; } /* 40px */
.h2 { font-size: 2rem; line-height: 1.2; font-weight: 600; }   /* 32px */
.h3 { font-size: 1.75rem; line-height: 1.3; font-weight: 600; }/* 28px */
.h4 { font-size: 1.5rem; line-height: 1.3; font-weight: 500; } /* 24px */
.h5 { font-size: 1.25rem; line-height: 1.4; font-weight: 500; }/* 20px */
.h6 { font-size: 1rem; line-height: 1.4; font-weight: 500; }   /* 16px */

/* Body Text */
.text-base { font-size: 1rem; line-height: 1.5; }     /* 16px - Touch friendly */
.text-sm { font-size: 0.875rem; line-height: 1.5; }   /* 14px - Desktop default */
.text-xs { font-size: 0.75rem; line-height: 1.5; }    /* 12px - Captions only */
```

### Typography Utilities

```css
/* Text Alignment */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* Text Transform */
.text-uppercase { text-transform: uppercase; letter-spacing: 0.05em; }
.text-capitalize { text-transform: capitalize; }

/* Text Utilities */
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-muted { 
  color: var(--gray-600); 
  opacity: 0.76;
}

/* Font Weight */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
```

[↑ Back to top](#table-of-contents)

---

## Layout & Spacing

### Spacing Scale (8px Base Unit)

```css
/* Spacing Variables */
--space-0: 0;
--space-1: 8px;   /* Tight */
--space-2: 16px;  /* Default */
--space-3: 24px;  /* Comfortable */
--space-4: 32px;  /* Section */
--space-5: 40px;  /* Large Section */
--space-6: 48px;  /* Extra Large */
--space-8: 64px;  /* Page Section */
```

### Spacing Classes

```css
/* Margin (m) and Padding (p) utilities */
/* Pattern: .{property}-{side}-{size} */

/* All sides */
.m-0 { margin: 0; }
.m-1 { margin: var(--space-1); }
.m-2 { margin: var(--space-2); }
/* ... up to m-8 */

.p-0 { padding: 0; }
.p-1 { padding: var(--space-1); }
.p-2 { padding: var(--space-2); }
/* ... up to p-8 */

/* Specific sides */
.mt-2 { margin-top: var(--space-2); }
.mr-2 { margin-right: var(--space-2); }
.mb-2 { margin-bottom: var(--space-2); }
.ml-2 { margin-left: var(--space-2); }

/* X and Y axis */
.mx-2 { margin-left: var(--space-2); margin-right: var(--space-2); }
.my-2 { margin-top: var(--space-2); margin-bottom: var(--space-2); }
```

### Grid System

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-2);
}

.grid {
  display: grid;
  gap: var(--space-2);
}

/* 12-column grid */
.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
.grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }

/* Responsive grid */
@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  /* etc */
}
```

### Common Layout Patterns

#### Dashboard Layout
```
+------------------+----------------------+
|     Header       |                      |
+------------------+                      |
|                  |                      |
|    Sidebar       |     Main Content     |
|    (240px)       |      (fluid)         |
|                  |                      |
+------------------+----------------------+
```

```html
<div class="dashboard">
  <header class="dashboard-header">
    <!-- Logo, user menu, etc -->
  </header>
  <aside class="dashboard-sidebar">
    <!-- Navigation -->
  </aside>
  <main class="dashboard-main">
    <!-- Page content -->
  </main>
</div>
```

```css
.dashboard {
  display: grid;
  grid-template-areas: 
    "header header"
    "sidebar main";
  grid-template-columns: 240px 1fr;
  grid-template-rows: 64px 1fr;
  height: 100vh;
}

.dashboard-header { grid-area: header; }
.dashboard-sidebar { grid-area: sidebar; }
.dashboard-main { grid-area: main; overflow-y: auto; }

/* Mobile: Stack vertically */
@media (max-width: 767px) {
  .dashboard {
    grid-template-areas: 
      "header"
      "main";
    grid-template-columns: 1fr;
    grid-template-rows: 64px 1fr;
  }
  
  .dashboard-sidebar { display: none; }
}
```

[↑ Back to top](#table-of-contents)

---

## Component Library

### Buttons

#### Basic Button Structure

```html
<!-- Primary Button -->
<button type="button" class="btn btn--primary">
  <span class="btn__text">Save Changes</span>
</button>

<!-- With Icon -->
<button type="button" class="btn btn--primary">
  <svg class="btn__icon" aria-hidden="true">...</svg>
  <span class="btn__text">Save Changes</span>
</button>

<!-- Loading State -->
<button type="button" class="btn btn--primary" aria-busy="true" disabled>
  <span class="btn__spinner"></span>
  <span class="btn__text">Saving...</span>
</button>
```

#### Button CSS

```css
/* Base Button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-height: 44px; /* Touch target */
  
  /* Prevent text selection */
  user-select: none;
  -webkit-user-select: none;
}

/* Focus State - NEVER REMOVE THIS */
.btn:focus {
  outline: none;
  box-shadow: var(--focus-ring);
}

/* Primary Button */
.btn--primary {
  background-color: var(--color-primary);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.btn--primary:active:not(:disabled) {
  background-color: var(--color-primary-active);
}

/* Secondary Button */
.btn--secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--color-primary);
  color: white;
}

/* Danger Button */
.btn--danger {
  background-color: var(--color-danger);
  color: white;
}

/* Disabled State */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading Spinner */
.btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Icon Spacing */
.btn__icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

/* Button Sizes */
.btn--sm {
  padding: 8px 16px;
  font-size: 0.875rem;
  min-height: 36px;
}

.btn--lg {
  padding: 16px 32px;
  font-size: 1.125rem;
  min-height: 52px;
}

/* Full Width */
.btn--full {
  width: 100%;
}
```

#### Button Usage Guidelines

| Button Type | Use Case | Example |
|------------|----------|---------|
| Primary | Main action on page | "Save", "Submit", "Continue" |
| Secondary | Alternative actions | "Cancel", "Back", "Reset" |
| Danger | Destructive actions | "Delete", "Remove", "Destroy" |
| Ghost | Tertiary actions | "Learn More", "View Details" |

> ⚠️ **Common Mistake**: Multiple primary buttons on one screen
> 
> **Rule**: Only ONE primary button per view/section
> ```html
> <!-- ❌ Bad -->
> <button class="btn btn--primary">Save</button>
> <button class="btn btn--primary">Save and Continue</button>
> 
> <!-- ✅ Good -->
> <button class="btn btn--secondary">Save Draft</button>
> <button class="btn btn--primary">Save and Continue</button>
> ```

### Forms

#### Form Structure

```html
<form class="form" novalidate>
  <!-- Text Input Group -->
  <div class="form-group">
    <label for="email" class="form-label">
      Email Address
      <span class="required" aria-label="required">*</span>
    </label>
    <input 
      type="email" 
      id="email" 
      name="email"
      class="form-control" 
      aria-describedby="email-hint email-error"
      aria-invalid="false"
      aria-required="true"
      required
    >
    <small id="email-hint" class="form-hint">
      We'll never share your email
    </small>
    <span id="email-error" class="form-error" role="alert"></span>
  </div>

  <!-- Select Dropdown -->
  <div class="form-group">
    <label for="country" class="form-label">Country</label>
    <select id="country" name="country" class="form-control">
      <option value="">Select a country</option>
      <option value="us">United States</option>
      <option value="uk">United Kingdom</option>
    </select>
  </div>

  <!-- Checkbox -->
  <div class="form-group">
    <label class="checkbox">
      <input type="checkbox" name="terms" required>
      <span class="checkbox__label">
        I agree to the <a href="/terms">terms and conditions</a>
      </span>
    </label>
  </div>

  <!-- Radio Group -->
  <fieldset class="form-group">
    <legend class="form-label">Preferred Contact Method</legend>
    <label class="radio">
      <input type="radio" name="contact" value="email" checked>
      <span class="radio__label">Email</span>
    </label>
    <label class="radio">
      <input type="radio" name="contact" value="phone">
      <span class="radio__label">Phone</span>
    </label>
  </fieldset>

  <!-- Form Actions -->
  <div class="form-actions">
    <button type="button" class="btn btn--secondary">Cancel</button>
    <button type="submit" class="btn btn--primary">Submit</button>
  </div>
</form>
```

#### Form CSS

```css
/* Form Layout */
.form-group {
  margin-bottom: var(--space-3);
}

.form-label {
  display: block;
  margin-bottom: var(--space-1);
  font-weight: 500;
  color: var(--gray-800);
}

/* Required Indicator */
.required {
  color: var(--color-danger);
  margin-left: 4px;
}

/* Form Controls */
.form-control {
  display: block;
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--gray-900);
  background-color: white;
  border: 1px solid var(--gray-300);
  border-radius: 4px;
  transition: border-color 0.15s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--focus-ring);
}

/* Placeholder Styling */
.form-control::placeholder {
  color: var(--gray-500);
  opacity: 1; /* Firefox fix */
}

/* Invalid State */
.form-control[aria-invalid="true"] {
  border-color: var(--color-danger);
}

.form-control[aria-invalid="true"]:focus {
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.25);
}

/* Disabled State */
.form-control:disabled {
  background-color: var(--gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Form Hints and Errors */
.form-hint {
  display: block;
  margin-top: var(--space-1);
  font-size: 0.875rem;
  color: var(--gray-600);
}

.form-error {
  display: block;
  margin-top: var(--space-1);
  font-size: 0.875rem;
  color: var(--color-danger);
}

.form-error:empty {
  display: none;
}

/* Checkbox and Radio */
.checkbox,
.radio {
  display: flex;
  align-items: flex-start;
  margin-bottom: var(--space-2);
  cursor: pointer;
}

.checkbox input[type="checkbox"],
.radio input[type="radio"] {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-right: var(--space-1);
  margin-top: 2px;
  cursor: pointer;
}

.checkbox__label,
.radio__label {
  flex: 1;
  user-select: none;
}

/* Custom Checkbox Style (Optional Enhancement) */
.checkbox input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  border: 2px solid var(--gray-400);
  border-radius: 4px;
  position: relative;
}

.checkbox input[type="checkbox"]:checked {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.checkbox input[type="checkbox"]:checked::after {
  content: "✓";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--gray-200);
}
```

#### Form Validation

```javascript
// Client-side validation example
class FormValidator {
  constructor(form) {
    this.form = form;
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    
    // Real-time validation
    this.form.querySelectorAll('input, select, textarea').forEach(field => {
      field.addEventListener('blur', () => this.validateField(field));
    });
  }

  validateField(field) {
    const errorElement = this.form.querySelector(`#${field.id}-error`);
    let isValid = true;
    let errorMessage = '';

    // Required field
    if (field.hasAttribute('required') && !field.value.trim()) {
      isValid = false;
      errorMessage = `${this.getFieldLabel(field)} is required`;
    }
    
    // Email validation
    else if (field.type === 'email' && field.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(field.value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }

    // Update UI
    field.setAttribute('aria-invalid', !isValid);
    if (errorElement) {
      errorElement.textContent = errorMessage;
    }

    return isValid;
  }

  getFieldLabel(field) {
    const label = this.form.querySelector(`label[for="${field.id}"]`);
    return label ? label.textContent.replace('*', '').trim() : field.name;
  }

  handleSubmit(e) {
    e.preventDefault();
    
    let isFormValid = true;
    const fields = this.form.querySelectorAll('input, select, textarea');
    
    fields.forEach(field => {
      if (!this.validateField(field)) {
        isFormValid = false;
      }
    });

    if (isFormValid) {
      // Submit form
      console.log('Form is valid, submitting...');
    } else {
      // Focus first error field
      const firstError = this.form.querySelector('[aria-invalid="true"]');
      if (firstError) {
        firstError.focus();
      }
    }
  }
}

// Initialize
document.querySelectorAll('form').forEach(form => {
  new FormValidator(form);
});
```

### Tables

#### Data Table Structure

```html
<div class="table-container" role="region" aria-label="User Management">
  <!-- Table Actions Bar -->
  <div class="table-actions">
    <div class="table-actions__left">
      <button class="btn btn--primary">
        <svg class="btn__icon" aria-hidden="true">...</svg>
        Add User
      </button>
    </div>
    <div class="table-actions__right">
      <input 
        type="search" 
        class="form-control" 
        placeholder="Search users..." 
        aria-label="Search users"
      >
    </div>
  </div>

  <!-- Responsive Table Wrapper -->
  <div class="table-wrapper">
    <table class="table" aria-label="Users">
      <thead>
        <tr>
          <th scope="col">
            <input type="checkbox" aria-label="Select all users">
          </th>
          <th scope="col">
            <button class="table__sort" aria-label="Sort by name">
              Name
              <svg class="table__sort-icon" aria-hidden="true">...</svg>
            </button>
          </th>
          <th scope="col">Email</th>
          <th scope="col">Role</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <input type="checkbox" aria-label="Select John Doe">
          </td>
          <td>John Doe</td>
          <td>john@example.com</td>
          <td>Admin</td>
          <td>
            <span class="badge badge--success">Active</span>
          </td>
          <td>
            <div class="table__actions">
              <button class="btn btn--ghost btn--sm" aria-label="Edit John Doe">
                Edit
              </button>
              <button class="btn btn--ghost btn--sm" aria-label="Delete John Doe">
                Delete
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  <div class="pagination">
    <div class="pagination__info">
      Showing 1-10 of 50 results
    </div>
    <div class="pagination__controls">
      <button class="pagination__btn" disabled aria-label="Previous page">
        Previous
      </button>
      <button class="pagination__btn pagination__btn--active" aria-current="page">
        1
      </button>
      <button class="pagination__btn">2</button>
      <button class="pagination__btn">3</button>
      <button class="pagination__btn" aria-label="Next page">
        Next
      </button>
    </div>
  </div>
</div>
```

#### Table CSS

```css
/* Table Container */
.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

/* Table Actions Bar */
.table-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  border-bottom: 1px solid var(--gray-200);
}

/* Table Wrapper (for horizontal scroll) */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Table Styles */
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: var(--space-2);
  text-align: left;
  white-space: nowrap;
}

.table th {
  font-weight: 600;
  color: var(--gray-700);
  background-color: var(--gray-50);
  border-bottom: 2px solid var(--gray-200);
}

.table td {
  border-bottom: 1px solid var(--gray-100);
}

.table tbody tr:hover {
  background-color: var(--gray-50);
}

/* Sort Button */
.table__sort {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font: inherit;
  color: inherit;
  cursor: pointer;
  padding: 0;
}

.table__sort:hover {
  color: var(--color-primary);
}

.table__sort-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.2s;
}

.table__sort[aria-pressed="true"] .table__sort-icon {
  transform: rotate(180deg);
}

/* Table Actions */
.table__actions {
  display: flex;
  gap: var(--space-1);
}

/* Badge */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge--success {
  background-color: rgba(40, 167, 69, 0.1);
  color: var(--color-success);
}

.badge--warning {
  background-color: rgba(255, 172, 0, 0.1);
  color: var(--color-warning);
}

.badge--danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: var(--color-danger);
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  border-top: 1px solid var(--gray-200);
}

.pagination__controls {
  display: flex;
  gap: var(--space-1);
}

.pagination__btn {
  padding: 8px 12px;
  border: 1px solid var(--gray-300);
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination__btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.pagination__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination__btn--active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .table {
    font-size: 0.875rem;
  }
  
  .table th,
  .table td {
    padding: var(--space-1);
  }
  
  /* Hide less important columns on mobile */
  .table th:nth-child(4),
  .table td:nth-child(4) {
    display: none;
  }
}
```

### Modals

#### Modal Structure

```html
<!-- Modal Backdrop -->
<div class="modal-backdrop" id="modal-backdrop" aria-hidden="true">
  <!-- Modal Container -->
  <div 
    class="modal" 
    role="dialog" 
    aria-modal="true" 
    aria-labelledby="modal-title"
    aria-describedby="modal-description"
  >
    <!-- Modal Header -->
    <div class="modal__header">
      <h2 id="modal-title" class="modal__title">Confirm Action</h2>
      <button 
        type="button" 
        class="modal__close" 
        aria-label="Close modal"
      >
        <svg aria-hidden="true">...</svg>
      </button>
    </div>

    <!-- Modal Body -->
    <div class="modal__body" id="modal-description">
      <p>Are you sure you want to delete this item? This action cannot be undone.</p>
    </div>

    <!-- Modal Footer -->
    <div class="modal__footer">
      <button type="button" class="btn btn--secondary" data-modal-close>
        Cancel
      </button>
      <button type="button" class="btn btn--danger">
        Delete
      </button>
    </div>
  </div>
</div>
```

#### Modal CSS

```css
/* Modal Backdrop */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, visibility 0.3s;
}

.modal-backdrop.is-open {
  opacity: 1;
  visibility: visible;
}

/* Modal Container */
.modal {
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  transform: scale(0.9);
  transition: transform 0.3s;
}

.modal-backdrop.is-open .modal {
  transform: scale(1);
}

/* Modal Header */
.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  border-bottom: 1px solid var(--gray-200);
}

.modal__title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal__close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.modal__close:hover {
  background-color: var(--gray-100);
}

/* Modal Body */
.modal__body {
  padding: var(--space-3);
  overflow-y: auto;
  flex: 1;
}

/* Modal Footer */
.modal__footer {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
  padding: var(--space-3);
  border-top: 1px solid var(--gray-200);
}

/* Mobile Full Screen */
@media (max-width: 767px) {
  .modal {
    width: 100%;
    height: 100%;
    max-width: none;
    max-height: none;
    border-radius: 0;
  }
}
```

#### Modal JavaScript

```javascript
class Modal {
  constructor(modalId) {
    this.backdrop = document.getElementById(modalId);
    this.modal = this.backdrop.querySelector('.modal');
    this.focusableElements = this.modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    this.firstFocusable = this.focusableElements[0];
    this.lastFocusable = this.focusableElements[this.focusableElements.length - 1];
    
    this.bindEvents();
  }

  bindEvents() {
    // Close button
    this.modal.querySelector('.modal__close').addEventListener('click', () => this.close());
    
    // Cancel buttons
    this.modal.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => this.close());
    });
    
    // Backdrop click
    this.backdrop.addEventListener('click', (e) => {
      if (e.target === this.backdrop) {
        this.close();
      }
    });
    
    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
    
    // Tab trap
    this.modal.addEventListener('keydown', (e) => this.trapFocus(e));
  }

  open() {
    // Store last focused element
    this.lastFocused = document.activeElement;
    
    // Open modal
    this.backdrop.classList.add('is-open');
    this.backdrop.setAttribute('aria-hidden', 'false');
    
    // Focus first focusable element
    this.firstFocusable.focus();
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  close() {
    // Close modal
    this.backdrop.classList.remove('is-open');
    this.backdrop.setAttribute('aria-hidden', 'true');
    
    // Restore focus
    if (this.lastFocused) {
      this.lastFocused.focus();
    }
    
    // Restore body scroll
    document.body.style.overflow = '';
  }

  isOpen() {
    return this.backdrop.classList.contains('is-open');
  }

  trapFocus(e) {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusable) {
        e.preventDefault();
        this.lastFocusable.focus();
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusable) {
        e.preventDefault();
        this.firstFocusable.focus();
      }
    }
  }
}

// Usage
const deleteModal = new Modal('delete-modal');
document.getElementById('delete-btn').addEventListener('click', () => {
  deleteModal.open();
});
```

[↑ Back to top](#table-of-contents)

---

## Common UI Patterns

### Loading States

```html
<!-- Inline Loading -->
<div class="loading loading--inline">
  <span class="loading__spinner"></span>
  <span class="loading__text">Loading...</span>
</div>

<!-- Full Page Loading -->
<div class="loading loading--overlay">
  <div class="loading__content">
    <span class="loading__spinner loading__spinner--lg"></span>
    <span class="loading__text">Loading application...</span>
  </div>
</div>

<!-- Skeleton Loading -->
<div class="skeleton">
  <div class="skeleton__header"></div>
  <div class="skeleton__text"></div>
  <div class="skeleton__text skeleton__text--short"></div>
</div>
```

```css
/* Loading States */
.loading {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.loading__spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--gray-300);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading__spinner--lg {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading--overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* Skeleton Loading */
.skeleton {
  padding: var(--space-3);
}

.skeleton__header,
.skeleton__text {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton__header {
  height: 32px;
  width: 200px;
  margin-bottom: var(--space-2);
}

.skeleton__text {
  height: 16px;
  width: 100%;
  margin-bottom: var(--space-1);
}

.skeleton__text--short {
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

### Empty States

```html
<div class="empty-state">
  <svg class="empty-state__icon" aria-hidden="true">
    <!-- Empty folder icon or similar -->
  </svg>
  <h3 class="empty-state__title">No results found</h3>
  <p class="empty-state__text">
    Try adjusting your search or filter to find what you're looking for.
  </p>
  <button class="btn btn--primary">Clear filters</button>
</div>
```

```css
.empty-state {
  text-align: center;
  padding: var(--space-6) var(--space-3);
}

.empty-state__icon {
  width: 80px;
  height: 80px;
  color: var(--gray-400);
  margin-bottom: var(--space-3);
}

.empty-state__title {
  font-size: 1.25rem;
  color: var(--gray-800);
  margin-bottom: var(--space-2);
}

.empty-state__text {
  color: var(--gray-600);
  margin-bottom: var(--space-3);
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
```

### Toast Notifications

```html
<div class="toast-container" aria-live="polite" aria-atomic="true">
  <!-- Success Toast -->
  <div class="toast toast--success" role="alert">
    <svg class="toast__icon" aria-hidden="true">...</svg>
    <div class="toast__content">
      <strong class="toast__title">Success!</strong>
      <p class="toast__message">Your changes have been saved.</p>
    </div>
    <button class="toast__close" aria-label="Close notification">
      <svg aria-hidden="true">...</svg>
    </button>
  </div>
</div>
```

```css
.toast-container {
  position: fixed;
  top: var(--space-3);
  right: var(--space-3);
  z-index: 1050;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-2);
  margin-bottom: var(--space-2);
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  transform: translateX(400px);
  transition: transform 0.3s;
}

.toast.is-visible {
  transform: translateX(0);
}

.toast__icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.toast--success {
  border-left: 4px solid var(--color-success);
}

.toast--success .toast__icon {
  color: var(--color-success);
}

.toast--error {
  border-left: 4px solid var(--color-danger);
}

.toast--error .toast__icon {
  color: var(--color-danger);
}

.toast__content {
  flex: 1;
}

.toast__title {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
}

.toast__message {
  margin: 0;
  font-size: 0.875rem;
  color: var(--gray-600);
}

.toast__close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.toast__close:hover {
  opacity: 1;
}
```

[↑ Back to top](#table-of-contents)

---

## Error Handling

### Error Message Templates

| Error Type | Message Template | Example | Icon |
|------------|------------------|---------|------|
| Required Field | "[Field] is required" | "Email is required" | ⚠️ |
| Invalid Format | "Please enter a valid [field]" | "Please enter a valid email" | ❌ |
| Network Error | "Unable to [action]. Please try again." | "Unable to save. Please try again." | 🔄 |
| Permission | "You don't have permission to [action]" | "You don't have permission to delete" | 🔒 |
| Not Found | "[Item] not found" | "User not found" | 🔍 |
| Server Error | "Something went wrong. Please try again later." | - | ⚡ |

### Error Display Patterns

#### Inline Field Errors
```html
<div class="form-group">
  <label for="email">Email</label>
  <input 
    type="email" 
    id="email" 
    class="form-control" 
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <span id="email-error" class="form-error" role="alert">
    Please enter a valid email address
  </span>
</div>
```

#### Summary Error Box
```html
<div class="alert alert--error" role="alert">
  <h3 class="alert__title">Please fix the following errors:</h3>
  <ul class="alert__list">
    <li><a href="#email">Email is required</a></li>
    <li><a href="#password">Password must be at least 8 characters</a></li>
  </ul>
</div>
```

#### Global Error State
```html
<div class="error-page">
  <div class="error-page__content">
    <h1 class="error-page__code">500</h1>
    <h2 class="error-page__title">Something went wrong</h2>
    <p class="error-page__message">
      We're having trouble loading this page. Please try again later.
    </p>
    <div class="error-page__actions">
      <button class="btn btn--primary" onclick="window.location.reload()">
        Try Again
      </button>
      <a href="/" class="btn btn--secondary">Go Home</a>
    </div>
  </div>
</div>
```

### Error Recovery Patterns

```javascript
// Retry Logic with Exponential Backoff
class APIClient {
  async fetchWithRetry(url, options = {}, maxRetries = 3) {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx)
        if (error.message.startsWith('HTTP 4')) {
          throw error;
        }
        
        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, i), 10000);
        await new Promise(resolve => setTimeout(resolve, delay));
        
        // Show retry notification
        this.showRetryNotification(i + 1, maxRetries);
      }
    }
    
    throw lastError;
  }
  
  showRetryNotification(attempt, maxAttempts) {
    const toast = new Toast({
      type: 'info',
      title: 'Connection Issue',
      message: `Retrying... (${attempt}/${maxAttempts})`,
      duration: 2000
    });
    toast.show();
  }
}
```

[↑ Back to top](#table-of-contents)

---

## Accessibility Guidelines

### ARIA Attributes Reference

```html
<!-- Labeling -->
aria-label="Clear description"
aria-labelledby="id-of-labeling-element"
aria-describedby="id-of-description"

<!-- States -->
aria-pressed="true|false"      <!-- Toggle buttons -->
aria-expanded="true|false"     <!-- Accordions, dropdowns -->
aria-selected="true|false"     <!-- Tabs, list items -->
aria-checked="true|false|mixed" <!-- Checkboxes -->
aria-disabled="true|false"     <!-- Disabled state -->
aria-hidden="true|false"       <!-- Hide from screen readers -->
aria-busy="true|false"         <!-- Loading states -->
aria-invalid="true|false"      <!-- Form validation -->

<!-- Live Regions -->
aria-live="polite|assertive"   <!-- Dynamic content -->
aria-atomic="true|false"       <!-- Read entire region -->

<!-- Relationships -->
aria-controls="id"             <!-- Controls another element -->
aria-owns="id"                 <!-- Parent-child relationship -->

<!-- Navigation -->
aria-current="page|step|location|date|time|true"
```

### Keyboard Navigation Patterns

| Component | Keys | Action |
|-----------|------|--------|
| Button | `Enter`, `Space` | Activate |
| Checkbox | `Space` | Toggle |
| Radio | `Arrow keys` | Navigate group |
| Select | `Arrow keys`, `Enter` | Open/navigate/select |
| Modal | `Escape` | Close |
| Menu | `Arrow keys`, `Enter`, `Escape` | Navigate/select/close |
| Tabs | `Arrow keys`, `Home`, `End` | Navigate tabs |

### Screen Reader Announcements

```javascript
// Announce dynamic content changes
class Announcer {
  constructor() {
    this.liveRegion = this.createLiveRegion();
  }
  
  createLiveRegion() {
    const region = document.createElement('div');
    region.setAttribute('aria-live', 'polite');
    region.setAttribute('aria-atomic', 'true');
    region.className = 'sr-only';
    document.body.appendChild(region);
    return region;
  }
  
  announce(message, priority = 'polite') {
    this.liveRegion.setAttribute('aria-live', priority);
    this.liveRegion.textContent = message;
    
    // Clear after announcement
    setTimeout(() => {
      this.liveRegion.textContent = '';
    }, 1000);
  }
}

// Usage
const announcer = new Announcer();
announcer.announce('Form submitted successfully');
announcer.announce('Error: Please fix the highlighted fields', 'assertive');
```

### Focus Management

```css
/* Never remove focus indicators */
:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Visible focus for keyboard users only */
.focus-visible:focus {
  outline: 2px solid var(--color-primary);
}

.focus-visible:focus:not(:focus-visible) {
  outline: none;
}

/* Skip Links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

[↑ Back to top](#table-of-contents)

---

## Performance Standards

### Component Performance Budgets

| Component | Max JS | Max CSS | Initial Render | User Interaction |
|-----------|--------|---------|----------------|------------------|
| Button | 0 KB | 2 KB | < 16ms | < 50ms |
| Form Input | 2 KB | 3 KB | < 16ms | < 50ms |
| Modal | 5 KB | 3 KB | < 100ms | < 50ms |
| Dropdown | 8 KB | 3 KB | < 100ms | < 100ms |
| Data Table | 15 KB | 5 KB | < 200ms | < 100ms |
| Date Picker | 25 KB | 5 KB | < 300ms | < 150ms |
| Chart | 50 KB | 2 KB | < 500ms | < 150ms |

### Optimization Techniques

```css
/* Use CSS containment for complex components */
.data-table {
  contain: layout style;
}

/* Hardware acceleration for animations */
.modal {
  will-change: transform, opacity;
}

/* Reduce reflows with CSS Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
```

```javascript
// Debounce expensive operations
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Virtual scrolling for large lists
class VirtualList {
  constructor(container, items, rowHeight) {
    this.container = container;
    this.items = items;
    this.rowHeight = rowHeight;
    this.visibleItems = Math.ceil(container.clientHeight / rowHeight);
    this.render();
  }
  
  render() {
    const scrollTop = this.container.scrollTop;
    const startIndex = Math.floor(scrollTop / this.rowHeight);
    const endIndex = startIndex + this.visibleItems;
    
    // Only render visible items
    const visibleItems = this.items.slice(startIndex, endIndex);
    // ... render logic
  }
}
```

### Image Optimization

```html
<!-- Responsive images -->
<picture>
  <source 
    media="(max-width: 768px)" 
    srcset="image-mobile.webp" 
    type="image/webp"
  >
  <source 
    media="(max-width: 768px)" 
    srcset="image-mobile.jpg" 
    type="image/jpeg"
  >
  <source 
    srcset="image-desktop.webp" 
    type="image/webp"
  >
  <img 
    src="image-desktop.jpg" 
    alt="Description" 
    loading="lazy"
    width="800" 
    height="600"
  >
</picture>

<!-- Lazy loading -->
<img 
  src="placeholder.jpg" 
  data-src="actual-image.jpg" 
  alt="Description" 
  loading="lazy"
  class="lazyload"
>
```

[↑ Back to top](#table-of-contents)

---

## Security Patterns

### Secure Form Handling

```javascript
// XSS Prevention
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// CSRF Token
class SecureForm {
  constructor(form) {
    this.form = form;
    this.addCSRFToken();
  }
  
  addCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrf_token';
    input.value = token;
    this.form.appendChild(input);
  }
}
```

### Password Input Patterns

```html
<div class="form-group">
  <label for="password">Password</label>
  <div class="password-input">
    <input 
      type="password" 
      id="password" 
      class="form-control" 
      aria-describedby="password-requirements"
      pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
      required
    >
    <button 
      type="button" 
      class="password-toggle" 
      aria-label="Show password"
      aria-pressed="false"
    >
      <svg class="icon-eye" aria-hidden="true">...</svg>
    </button>
  </div>
  <div id="password-requirements" class="password-requirements">
    <p class="text-sm text-muted">Password must contain:</p>
    <ul class="requirements-list">
      <li data-requirement="length">At least 8 characters</li>
      <li data-requirement="lowercase">One lowercase letter</li>
      <li data-requirement="uppercase">One uppercase letter</li>
      <li data-requirement="number">One number</li>
    </ul>
  </div>
</div>
```

```javascript
// Password strength indicator
class PasswordStrength {
  constructor(input) {
    this.input = input;
    this.requirements = {
      length: /.{8,}/,
      lowercase: /[a-z]/,
      uppercase: /[A-Z]/,
      number: /\d/,
      special: /[!@#$%^&*]/
    };
    
    this.input.addEventListener('input', () => this.check());
  }
  
  check() {
    const password = this.input.value;
    let strength = 0;
    
    Object.entries(this.requirements).forEach(([key, regex]) => {
      const requirement = document.querySelector(`[data-requirement="${key}"]`);
      if (regex.test(password)) {
        strength++;
        requirement?.classList.add('is-met');
      } else {
        requirement?.classList.remove('is-met');
      }
    });
    
    this.updateStrengthIndicator(strength);
  }
  
  updateStrengthIndicator(strength) {
    const indicator = document.querySelector('.strength-indicator');
    const levels = ['weak', 'fair', 'good', 'strong', 'very-strong'];
    indicator.className = `strength-indicator strength-indicator--${levels[strength]}`;
  }
}
```

### Sensitive Data Display

```css
/* Masked data */
.data-masked {
  position: relative;
}

.data-masked::after {
  content: "••••••••";
  position: absolute;
  left: 0;
  top: 0;
  background: white;
}

.data-masked.is-revealed::after {
  display: none;
}

/* Redacted content */
.redacted {
  background-color: var(--gray-900);
  color: var(--gray-900);
  user-select: none;
}
```

[↑ Back to top](#table-of-contents)

---

## Responsive Design

### Breakpoint System

```scss
// Breakpoint variables
$breakpoints: (
  xs: 0,
  sm: 576px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1400px
);

// Media query mixins
@mixin media-up($breakpoint) {
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

@mixin media-down($breakpoint) {
  @media (max-width: map-get($breakpoints, $breakpoint) - 1px) {
    @content;
  }
}

@mixin media-between($lower, $upper) {
  @media (min-width: map-get($breakpoints, $lower)) and (max-width: map-get($breakpoints, $upper) - 1px) {
    @content;
  }
}
```

### Responsive Utilities

```css
/* Display utilities */
.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

/* Responsive display */
@media (min-width: 576px) {
  .sm\:d-none { display: none; }
  .sm\:d-block { display: block; }
  .sm\:d-flex { display: flex; }
}

@media (min-width: 768px) {
  .md\:d-none { display: none; }
  .md\:d-block { display: block; }
  .md\:d-flex { display: flex; }
}

/* Text alignment */
@media (min-width: 768px) {
  .md\:text-left { text-align: left; }
  .md\:text-center { text-align: center; }
  .md\:text-right { text-align: right; }
}

/* Hiding elements */
.visible-xs { display: none; }
.visible-sm { display: none; }
.visible-md { display: none; }
.visible-lg { display: none; }

@media (max-width: 575px) { .visible-xs { display: block; } }
@media (min-width: 576px) and (max-width: 767px) { .visible-sm { display: block; } }
@media (min-width: 768px) and (max-width: 991px) { .visible-md { display: block; } }
@media (min-width: 992px) { .visible-lg { display: block; } }
```

### Mobile-First Component Patterns

```css
/* Card component - mobile first */
.card {
  background: white;
  border-radius: 8px;
  padding: var(--space-2);
  box-shadow: var(--shadow-sm);
}

@media (min-width: 768px) {
  .card {
    padding: var(--space-3);
  }
}

/* Navigation - mobile first */
.nav {
  position: fixed;
  top: 0;
  left: -100%;
  width: 80%;
  height: 100vh;
  background: white;
  transition: left 0.3s;
  z-index: 1000;
}

.nav.is-open {
  left: 0;
}

@media (min-width: 768px) {
  .nav {
    position: static;
    width: auto;
    height: auto;
  }
}
```

### Touch-Friendly Design

```css
/* Minimum touch target size */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Increase spacing on mobile */
@media (max-width: 767px) {
  .btn {
    min-height: 48px;
    font-size: 1rem;
  }
  
  .form-control {
    min-height: 48px;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* Disable hover effects on touch devices */
@media (hover: none) {
  .btn:hover {
    background-color: inherit;
  }
}
```

[↑ Back to top](#table-of-contents)

---

## Dark Mode & Theming

### CSS Custom Properties for Theming

```css
/* Light mode (default) */
:root {
  /* Colors */
  --color-bg: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-text: #212529;
  --color-text-muted: #6c757d;
  --color-border: #dee2e6;
  
  /* Component specific */
  --card-bg: var(--color-bg);
  --input-bg: var(--color-bg);
  --input-border: var(--color-border);
}

/* Dark mode */
[data-theme="dark"] {
  /* Colors */
  --color-bg: #1a1a1a;
  --color-bg-secondary: #2d2d2d;
  --color-text: #e9ecef;
  --color-text-muted: #adb5bd;
  --color-border: #343a40;
  
  /* Component specific */
  --card-bg: #2d2d2d;
  --input-bg: #2d2d2d;
  --input-border: #495057;
}

/* System preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    /* Dark mode colors */
    --color-bg: #1a1a1a;
    --color-bg-secondary: #2d2d2d;
    --color-text: #e9ecef;
    --color-text-muted: #adb5bd;
    --color-border: #343a40;
  }
}
```

### Theme Toggle Implementation

```html
<button 
  class="theme-toggle" 
  aria-label="Toggle dark mode"
  aria-pressed="false"
>
  <svg class="theme-toggle__icon theme-toggle__icon--light">
    <!-- Sun icon -->
  </svg>
  <svg class="theme-toggle__icon theme-toggle__icon--dark">
    <!-- Moon icon -->
  </svg>
</button>
```

```javascript
class ThemeToggle {
  constructor() {
    this.toggle = document.querySelector('.theme-toggle');
    this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Initialize theme
    this.initTheme();
    
    // Bind events
    this.toggle?.addEventListener('click', () => this.toggleTheme());
    this.prefersDark.addEventListener('change', (e) => this.handleSystemChange(e));
  }
  
  initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = this.prefersDark.matches ? 'dark' : 'light';
    const theme = savedTheme || systemTheme;
    
    this.setTheme(theme);
  }
  
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.toggle?.setAttribute('aria-pressed', theme === 'dark');
    localStorage.setItem('theme', theme);
  }
  
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  }
  
  handleSystemChange(e) {
    if (!localStorage.getItem('theme')) {
      this.setTheme(e.matches ? 'dark' : 'light');
    }
  }
}

// Initialize
new ThemeToggle();
```

### Theme-Aware Components

```css
/* Card with theme support */
.card {
  background-color: var(--card-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

/* Form controls with theme support */
.form-control {
  background-color: var(--input-bg);
  color: var(--color-text);
  border-color: var(--input-border);
}

.form-control::placeholder {
  color: var(--color-text-muted);
}

/* Adjust shadows for dark mode */
[data-theme="dark"] {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.5);
}
```

[↑ Back to top](#table-of-contents)

---

## Testing Checklist

### Component Testing Checklist

Before marking any component as complete, verify each item:

#### ✅ Visual Design
- [ ] Matches design specifications exactly
- [ ] All states implemented (default, hover, focus, active, disabled)
- [ ] Consistent spacing using the 8px grid
- [ ] Proper typography hierarchy
- [ ] Brand colors applied correctly

#### ✅ Accessibility
- [ ] **Keyboard Navigation**
  - [ ] Tab through all interactive elements
  - [ ] Visible focus indicators (never remove!)
  - [ ] Escape key closes overlays
  - [ ] Enter/Space activate buttons
- [ ] **Screen Reader**
  - [ ] Meaningful labels on all inputs
  - [ ] Proper heading hierarchy
  - [ ] ARIA labels where needed
  - [ ] Error messages announced
- [ ] **Color Contrast**
  - [ ] Text: 4.5:1 minimum
  - [ ] Large text: 3:1 minimum
  - [ ] Focus indicators: 3:1 minimum

#### ✅ Responsive Behavior
- [ ] Mobile (320px - 767px)
  - [ ] Touch targets ≥ 44px
  - [ ] No horizontal scroll
  - [ ] Readable without zoom
- [ ] Tablet (768px - 991px)
  - [ ] Layout adjusts gracefully
- [ ] Desktop (992px+)
  - [ ] Optimal use of space

#### ✅ Performance
- [ ] Initial render < 200ms
- [ ] Interactions < 100ms response
- [ ] No layout shifts during load
- [ ] Images optimized and lazy loaded

#### ✅ Cross-Browser
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS 14+)
- [ ] Chrome Mobile (Android 10+)

### Automated Testing

```javascript
// Example accessibility test with Jest and Testing Library
describe('Button Component', () => {
  it('is keyboard accessible', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button');
    
    // Focus the button
    button.focus();
    expect(document.activeElement).toBe(button);
    
    // Activate with Space
    fireEvent.keyDown(button, { key: ' ' });
    expect(onClick).toHaveBeenCalled();
  });
  
  it('has proper ARIA attributes', () => {
    render(<Button loading>Save</Button>);
    const button = screen.getByRole('button');
    
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).toBeDisabled();
  });
});
```

### Manual Testing Scripts

```markdown
#### Form Validation Test
1. Tab to first input field
2. Leave it empty and tab away
3. ✓ Error message appears
4. ✓ Field has red border
5. ✓ Screen reader announces error
6. Enter valid data
7. ✓ Error clears immediately
8. Submit form with errors
9. ✓ Focus moves to first error
10. ✓ Error summary appears at top

#### Modal Accessibility Test
1. Open modal with keyboard (Enter on trigger)
2. ✓ Focus moves to modal
3. ✓ Focus is trapped inside
4. Tab through all elements
5. ✓ Tab loops at end
6. Press Escape
7. ✓ Modal closes
8. ✓ Focus returns to trigger
```

[↑ Back to top](#table-of-contents)

---

## Common Mistakes to Avoid

### ❌ Never Do This

#### 1. **Removing Focus Indicators**
```css
/* ❌ NEVER DO THIS */
*:focus {
  outline: none;
}

/* ✅ Do this instead */
*:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

#### 2. **Using Placeholder as Label**
```html
<!-- ❌ Bad -->
<input placeholder="Email">

<!-- ✅ Good -->
<label for="email">Email</label>
<input id="email" type="email" placeholder="user@example.com">
```

#### 3. **Click Handlers on Non-Interactive Elements**
```html
<!-- ❌ Bad -->
<div onclick="doSomething()">Click me</div>

<!-- ✅ Good -->
<button type="button" onclick="doSomething()">Click me</button>
```

#### 4. **Forgetting Loading States**
```javascript
// ❌ Bad
async function saveData() {
  await api.save(data);
}

// ✅ Good
async function saveData() {
  setLoading(true);
  try {
    await api.save(data);
    showSuccess('Saved successfully');
  } catch (error) {
    showError('Failed to save');
  } finally {
    setLoading(false);
  }
}
```

#### 5. **Inconsistent Spacing**
```css
/* ❌ Bad - random values */
.card {
  padding: 13px;
  margin-bottom: 17px;
}

/* ✅ Good - using scale */
.card {
  padding: var(--space-2);
  margin-bottom: var(--space-3);
}
```

### 💡 Best Practices Quick Reference

1. **Always provide text alternatives**
   - Images need alt text
   - Icons need labels or titles
   - Videos need captions

2. **Test with keyboard only**
   - Unplug your mouse
   - Navigate entire flow
   - Everything must be reachable

3. **Announce dynamic changes**
   - Loading states
   - Success messages
   - Error states
   - Content updates

4. **Support all viewport sizes**
   - Test at 320px width
   - Ensure no horizontal scroll
   - Check touch target sizes

5. **Handle errors gracefully**
   - Show clear error messages
   - Provide recovery options
   - Maintain user data

[↑ Back to top](#table-of-contents)

---

## Quick Reference

### Essential CSS Classes

```css
/* Layout */
.container          /* Max-width wrapper */
.grid               /* Grid container */
.grid-cols-{1-12}   /* Grid columns */

/* Spacing */
.m-{0-8}           /* Margin all sides */
.p-{0-8}           /* Padding all sides */
.mt-{0-8}          /* Margin top */
.mb-{0-8}          /* Margin bottom */

/* Typography */
.h{1-6}            /* Heading styles */
.text-sm           /* Small text */
.text-muted        /* Muted color */
.font-bold         /* Bold weight */

/* Components */
.btn               /* Button base */
.btn--primary      /* Primary button */
.form-control      /* Form input */
.card              /* Card container */

/* States */
.is-loading        /* Loading state */
.is-disabled       /* Disabled state */
.is-error          /* Error state */
```

### Essential HTML Attributes

```html
<!-- Every interactive element needs -->
role="..."              <!-- Semantic role -->
aria-label="..."        <!-- Accessible name -->
aria-describedby="..."  <!-- Additional description -->
aria-live="..."         <!-- Dynamic regions -->

<!-- Form inputs need -->
id="..."                <!-- Unique ID -->
name="..."              <!-- Form field name -->
required                <!-- Required field -->
aria-invalid="..."      <!-- Validation state -->
aria-required="true"    <!-- Required for SR -->

<!-- Buttons need -->
type="button|submit"    <!-- Explicit type -->
aria-pressed="..."      <!-- Toggle state -->
aria-busy="..."         <!-- Loading state -->
disabled                <!-- Disabled state -->
```

### JavaScript Utilities

```javascript
// Debounce function
const debounce = (func, wait) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
};

// Trap focus
const trapFocus = (element) => {
  const focusable = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstFocusable = focusable[0];
  const lastFocusable = focusable[focusable.length - 1];
  
  element.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      } else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  });
};

// Announce to screen readers
const announce = (message) => {
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.className = 'sr-only';
  liveRegion.textContent = message;
  document.body.appendChild(liveRegion);
  setTimeout(() => liveRegion.remove(), 1000);
};
```

### Accessibility Checklist Card

```markdown
Before shipping any feature:

✓ Keyboard accessible
✓ Screen reader tested
✓ Color contrast checked
✓ Focus indicators visible
✓ Error messages clear
✓ Loading states shown
✓ Mobile touch friendly
✓ Works without JavaScript
✓ Tested with real users
```

---

_End of Enterprise UI/UX Design Specification v2.0_

**Remember:** Great UI is invisible when it works, and obvious when it doesn't. Build for everyone, test everything, and never stop improving.

[↑ Back to top](#table-of-contents)