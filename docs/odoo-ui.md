# Odoo-Inspired UI/UX Design Specification
*A Comprehensive Design System for Business Applications*

## Table of Contents
1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Component Library](#component-library)
6. [Navigation Patterns](#navigation-patterns)
7. [Forms & Inputs](#forms--inputs)
8. [Data Display](#data-display)
9. [Interaction States](#interaction-states)
10. [Responsive Design](#responsive-design)
11. [Implementation Guidelines](#implementation-guidelines)

---

## Design Philosophy

### Core Principles
- **Functional Clarity**: Every element serves a clear purpose
- **Responsive Adaptability**: Seamless experience across all devices
- **Modular Architecture**: Reusable components with consistent behavior
- **Accessibility First**: Inclusive design for all users
- **Business Focus**: Professional appearance suitable for enterprise applications

### Visual Approach
- Clean, minimalist interface with purposeful use of whitespace
- Subtle shadows and borders for depth without distraction
- Consistent iconography using FontAwesome
- Progressive disclosure to manage complexity

---

## Color System

### Primary Palette
```scss
// Brand Colors
$odoo-primary: #71639e;          // Main brand color (Community)
$odoo-enterprise: #714B67;       // Enterprise variant
$odoo-secondary: #71639e;        // Secondary actions

// Contextual Colors
$success: #28a745;               // Success states, confirmations
$info: #17a2b8;                  // Information, neutral alerts
$warning: #ffac00;               // Warnings, cautions
$danger: #dc3545;                // Errors, destructive actions
```

### Grayscale System
```scss
$white: #FFFFFF;
$gray-50: #f8f9fa;              // Background tints
$gray-100: #e9ecef;             // Light borders
$gray-200: #dee2e6;             // Subtle dividers
$gray-300: #ced4da;             // Disabled elements
$gray-400: #adb5bd;             // Placeholder text
$gray-500: #6c757d;             // Secondary text
$gray-600: #495057;             // Body text
$gray-700: #343a40;             // Headers
$gray-800: #212529;             // High contrast text
$black: #000000;
```

### Usage Guidelines
- **Primary**: Use sparingly for main CTAs and brand elements
- **Contextual**: Apply consistently for system feedback
- **Grayscale**: Primary palette for most interface elements
- **Opacity Levels**: 0, 0.25, 0.5, 0.75, 1.0 for layering
- **Disabled Opacity**: 0.5 for disabled elements
- **Muted Opacity**: 0.76 for secondary content

---

## Typography

### Font Stack
```scss
// Primary Font Family
$font-family-sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                         "Helvetica Neue", Arial, sans-serif;

// Display Font (Headings)
$font-family-headings: "SF Pro Display", -apple-system, BlinkMacSystemFont, 
                       "Segoe UI", sans-serif;

// Monospace (Code)
$font-family-monospace: SFMono-Regular, Menlo, Monaco, Consolas, 
                        "Liberation Mono", "Courier New", monospace;
```

### Type Scale
```scss
$font-size-root: 1rem;           // 16px base
$font-size-base: 14px;           // Body text
$font-size-touch: 16px;          // Touch interfaces
$font-size-sm: 13px;             // Small text
$font-size-xs: 12px;             // Micro text

// Headings
$h1-font-size: 2.5rem;           // 40px
$h2-font-size: 2rem;             // 32px
$h3-font-size: 1.75rem;          // 28px
$h4-font-size: 1.5rem;           // 24px
$h5-font-size: 1.25rem;          // 20px
$h6-font-size: 1rem;             // 16px
```

### Font Weights
```scss
$font-weight-normal: 400;        // Body text
$font-weight-medium: 500;        // Emphasized text
$font-weight-bold: 700;          // Headings, strong emphasis
```

### Text Utilities
- `.o_text_overflow`: Truncate text with ellipsis
- `.o_force_ltr`: Force left-to-right text direction
- Use consistent line-height: 1.5 for body text, 1.2 for headings

---

## Spacing & Layout

### Spacing Scale
```scss
$spacer: 16px;                   // Base spacing unit
$spacers: (
  0: 0,
  1: $spacer * 0.25,             // 4px
  2: $spacer * 0.5,              // 8px
  3: $spacer,                    // 16px
  4: $spacer * 1.5,              // 24px
  5: $spacer * 2,                // 32px
  6: $spacer * 2.5,              // 40px
  7: $spacer * 3,                // 48px
  8: $spacer * 4,                // 64px
);
```

### Layout Patterns
- **Horizontal Padding**: 16px standard, 20px for dropdowns
- **Vertical Padding**: 3px for dropdowns, 16px for content areas
- **Content Margins**: Use spacer multiples consistently
- **Component Spacing**: Minimum 8px between related elements

### Border Radius
```scss
$border-radius: 4px;             // Standard radius
$border-radius-sm: 3px;          // Small elements
$border-radius-lg: 6px;          // Large elements
$border-radius-pill: 50rem;      // Fully rounded
```

---

## Component Library

### Buttons

#### Primary Button
```scss
.btn-primary {
  background-color: $odoo-primary;
  border-color: $odoo-primary;
  color: $white;
  padding: 8px 16px;
  border-radius: $border-radius;
  font-weight: $font-weight-medium;
  transition: all 0.15s ease-in-out;
  
  &:hover {
    background-color: darken($odoo-primary, 7.5%);
    border-color: darken($odoo-primary, 10%);
  }
  
  &:focus {
    box-shadow: 0 0 0 0.2rem rgba($odoo-primary, 0.5);
  }
  
  &.o_btn_loading {
    position: relative;
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      top: 50%;
      left: 50%;
      margin-left: -8px;
      margin-top: -8px;
      border: 2px solid transparent;
      border-top-color: $white;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
}
```

#### Secondary Button
```scss
.btn-secondary {
  background-color: transparent;
  border-color: $gray-300;
  color: $gray-600;
  
  &:hover {
    background-color: $gray-50;
    border-color: $gray-400;
  }
}
```

### Dropdowns

#### Structure
```xml
<div class="dropdown">
  <button class="btn dropdown-toggle" type="button">
    <span>Dropdown Button</span>
    <i class="fa fa-caret-down ms-1"></i>
  </button>
  <div class="dropdown-menu">
    <a class="dropdown-item" href="#">Action</a>
    <div class="dropdown-divider"></div>
    <a class="dropdown-item" href="#">Another action</a>
  </div>
</div>
```

#### Styling
```scss
.dropdown-toggle {
  &::after {
    display: none; // Remove default caret
  }
  
  .fa-caret-down {
    transition: transform 0.15s ease-in-out;
  }
  
  &[aria-expanded="true"] .fa-caret-down {
    transform: rotate(180deg);
  }
}

.dropdown-menu {
  font-size: $font-size-sm;
  margin-top: 2px;
  padding: 8px 0;
  
  .dropdown-item {
    padding: 6px 16px;
    
    &:hover,
    &:focus {
      background-color: $gray-50;
    }
  }
}
```

### Form Controls

#### Input Fields
```scss
.form-control {
  border: 1px solid $gray-300;
  border-radius: $border-radius;
  padding: 8px 12px;
  font-size: $font-size-base;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  
  &:focus {
    border-color: $odoo-primary;
    box-shadow: 0 0 0 0.2rem rgba($odoo-primary, 0.25);
    outline: 0;
  }
  
  &::placeholder {
    color: $gray-400;
    opacity: 1;
  }
  
  &:disabled {
    background-color: $gray-100;
    opacity: $disabled-opacity;
  }
}
```

#### Checkbox Component
```scss
.o-checkbox {
  width: fit-content;
  
  input[type="checkbox"] {
    width: 16px;
    height: 16px;
    border: 1px solid $gray-300;
    border-radius: 3px;
    
    &:checked {
      background-color: $odoo-primary;
      border-color: $odoo-primary;
    }
  }
}
```

### Modal Dialogs

#### Structure
```xml
<div class="modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Modal Title</h5>
        <button type="button" class="btn-close"></button>
      </div>
      <div class="modal-body">
        <!-- Content -->
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary">Cancel</button>
        <button type="button" class="btn btn-primary">Save</button>
      </div>
    </div>
  </div>
</div>
```

#### Styling
```scss
.modal-dialog {
  margin: 1.75rem auto;
  max-width: 500px;
  
  @media (max-width: 768px) {
    margin: 0;
    max-width: 100%;
    height: 100vh;
  }
}

.modal-content {
  border: none;
  border-radius: $border-radius-lg;
  box-shadow: 0 10px 30px rgba($black, 0.19);
}

.modal-header {
  border-bottom: 1px solid $gray-200;
  padding: 16px 24px;
  
  .modal-title {
    font-weight: $font-weight-medium;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.modal-footer {
  border-top: 1px solid $gray-200;
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  
  @media (max-width: 576px) {
    flex-direction: column-reverse;
    
    .btn {
      width: 100%;
    }
  }
}
```

---

## Navigation Patterns

### Top Navigation Bar

#### Structure
```xml
<nav class="o_navbar">
  <div class="o_navbar_apps_menu">
    <button class="dropdown-toggle">
      <i class="fa fa-th"></i>
    </button>
  </div>
  
  <div class="o_navbar_brand">
    <img src="logo.png" alt="Brand" />
    <span class="o_navbar_brand_name">App Name</span>
  </div>
  
  <div class="o_navbar_sections">
    <div class="dropdown">
      <button class="dropdown-toggle">Section Name</button>
      <!-- Dropdown menu -->
    </div>
  </div>
  
  <div class="o_navbar_systray">
    <!-- System tray items -->
  </div>
</nav>
```

#### Mobile Navigation
```scss
@media (max-width: 768px) {
  .o_navbar {
    .o_navbar_sections {
      display: none;
    }
    
    .o_mobile_menu_toggle {
      display: flex;
    }
  }
  
  .o_navbar_mobile_sidebar {
    position: fixed;
    top: 0;
    left: -300px;
    width: 300px;
    height: 100vh;
    background: $white;
    transition: transform 0.3s ease-in-out;
    z-index: 9999;
    
    &.show {
      transform: translateX(300px);
    }
  }
}
```

### Sidebar Navigation
- Fixed-width sidebar (280px) for desktop
- Collapsible sections with accordion behavior
- Icon + text for primary navigation items
- Nested menu support with indentation

---

## Data Display

### Tables
```scss
.table {
  width: 100%;
  margin-bottom: 0;
  color: $gray-700;
  
  th {
    font-weight: $font-weight-medium;
    border-bottom: 2px solid $gray-200;
    padding: 12px 8px;
    
    &.sortable {
      cursor: pointer;
      
      &:hover {
        background-color: $gray-50;
      }
    }
  }
  
  td {
    padding: 12px 8px;
    border-bottom: 1px solid $gray-100;
    vertical-align: middle;
  }
  
  tbody tr:hover {
    background-color: $gray-50;
  }
}
```

### Cards
```scss
.card {
  background: $white;
  border: 1px solid $gray-200;
  border-radius: $border-radius;
  box-shadow: 0 2px 4px rgba($black, 0.1);
  
  .card-header {
    background: $gray-50;
    border-bottom: 1px solid $gray-200;
    padding: 16px 20px;
    font-weight: $font-weight-medium;
  }
  
  .card-body {
    padding: 20px;
  }
}
```

### Lists
```scss
.list-group {
  .list-group-item {
    border: 1px solid $gray-200;
    padding: 12px 16px;
    
    &:first-child {
      border-top-left-radius: $border-radius;
      border-top-right-radius: $border-radius;
    }
    
    &:last-child {
      border-bottom-left-radius: $border-radius;
      border-bottom-right-radius: $border-radius;
    }
    
    &.active {
      background-color: $odoo-primary;
      border-color: $odoo-primary;
      color: $white;
    }
  }
}
```

---

## Interaction States

### Hover States
- Subtle background color changes ($gray-50)
- 0.15s transition for smooth feedback
- Slight opacity changes for icons (0.7 to 1.0)

### Focus States
- Blue outline using primary color at 25% opacity
- 2px outline offset for accessibility
- Remove default browser outline styles

### Active States
- Darker background colors
- Pressed appearance with subtle shadow inset
- Immediate visual feedback (no transition delay)

### Disabled States
```scss
.disabled,
:disabled {
  opacity: $disabled-opacity;
  pointer-events: none;
  cursor: not-allowed;
}
```

### Loading States
```scss
.o_btn_loading {
  position: relative;
  color: transparent !important;
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 16px;
    height: 16px;
    margin: -8px 0 0 -8px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## Responsive Design

### Breakpoints
```scss
$grid-breakpoints: (
  xs: 0,
  sm: 576px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1400px
);
```

### Mobile-First Approach
- Start with mobile layout as base
- Progressive enhancement for larger screens
- Touch-friendly interaction targets (minimum 44px)
- Simplified navigation for small screens

### Adaptive Components
- Collapsing navigation on mobile
- Stacked button layouts on narrow screens
- Responsive table with horizontal scroll
- Modal fullscreen on mobile devices

---

## Implementation Guidelines

### CSS Architecture
1. **Use SCSS with variables** for maintainable styling
2. **Modular component files** for organization
3. **BEM methodology** for class naming
4. **Utility classes** for common patterns

### Component Development
1. **Start with semantic HTML** structure
2. **Apply progressive enhancement** with CSS and JavaScript
3. **Use consistent spacing** from the spacing scale
4. **Implement proper focus management** for accessibility

### Performance Considerations
1. **Minimize CSS file size** through optimization
2. **Use efficient selectors** avoiding deep nesting
3. **Leverage CSS custom properties** for theming
4. **Implement smooth transitions** sparingly

### Accessibility Requirements
1. **Proper color contrast** ratios (WCAG AA compliance)
2. **Keyboard navigation** support for all interactive elements
3. **Screen reader compatibility** with semantic markup
4. **Focus indicators** clearly visible and consistent

### Quality Assurance
1. **Cross-browser testing** (Chrome, Firefox, Safari, Edge)
2. **Device testing** across mobile, tablet, and desktop
3. **Accessibility auditing** with automated tools
4. **Performance monitoring** for smooth interactions

---

## Utility Classes

### Visibility
```scss
.o_hidden { display: none !important; }
.o_invisible { visibility: hidden; }
```

### Text Utilities
```scss
.o_text_overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### Spacing Utilities
```scss
// Margin utilities
.m-0 { margin: 0 !important; }
.m-1 { margin: $spacer * 0.25 !important; }
// ... (continue for all spacer values)

// Padding utilities
.p-0 { padding: 0 !important; }
.p-1 { padding: $spacer * 0.25 !important; }
// ... (continue for all spacer values)
```

### Animation
```scss
.o_catch_attention {
  animation: bounce 0.6s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
```

---

This specification provides a comprehensive foundation for building business applications with consistent, professional UI/UX that matches Odoo's design language. Junior engineers should reference this document for all interface development to ensure consistency and maintainability across the application suite.