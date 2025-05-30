# Revised UI/UX Guidelines for ICS Forms Management Application
*Version 1.1 – April 29, 2025*

## 1. General Visual Style
### 1.1 Aesthetic Principles
- Minimalist, professional appearance with focus on readability and usability.
- Strict adherence to platform-native appearance where appropriate.
- Visual hierarchy emphasizing task-oriented workflows.

### 1.2 Color System Specifications

#### 1.2.1 Light Theme
| Element | Color | Hex Code | RGB | Usage |
|:--------|:------|:---------|:----|:------|
| Background (Primary) | White | #FFFFFF | rgb(255, 255, 255) | Main content areas |
| Background (Secondary) | Light Gray | #F5F5F5 | rgb(245, 245, 245) | Sidebar, headers, grouping containers |
| Text (Primary) | Dark Gray | #212121 | rgb(33, 33, 33) | Main content text |
| Text (Secondary) | Medium Gray | #757575 | rgb(117, 117, 117) | Labels, captions, secondary text |
| Border | Light Gray | #E0E0E0 | rgb(224, 224, 224) | Dividers, borders, separators |
| Accent | Blue | #1976D2 | rgb(25, 118, 210) | Interactive elements, buttons, links |
| Hover State | Light Blue | #E3F2FD | rgb(227, 242, 253) | Hover effect background |
| Focus Outline | Blue | #2196F3 | rgb(33, 150, 243) | Focus indicators for accessibility |

#### 1.2.2 Dark Theme
| Element | Color | Hex Code | RGB | Usage |
|:--------|:------|:---------|:----|:------|
| Background (Primary) | Dark Gray | #212121 | rgb(33, 33, 33) | Main content areas |
| Background (Secondary) | Medium Gray | #303030 | rgb(48, 48, 48) | Sidebar, headers, grouping containers |
| Text (Primary) | Light Gray | #E0E0E0 | rgb(224, 224, 224) | Main content text |
| Text (Secondary) | Medium Light Gray | #BDBDBD | rgb(189, 189, 189) | Labels, captions, secondary text |
| Border | Medium Gray | #424242 | rgb(66, 66, 66) | Dividers, borders, separators |
| Accent | Light Blue | #64B5F6 | rgb(100, 181, 246) | Interactive elements, buttons, links |
| Hover State | Dark Blue | #1A2A38 | rgb(26, 42, 56) | Hover effect background |
| Focus Outline | Light Blue | #64B5F6 | rgb(100, 181, 246) | Focus indicators for accessibility |

#### 1.2.3 High Contrast Theme
| Element | Color | Hex Code | RGB | Usage |
|:--------|:------|:---------|:----|:------|
| Background (Primary) | Black | #000000 | rgb(0, 0, 0) | Main content areas |
| Background (Secondary) | Black | #000000 | rgb(0, 0, 0) | Sidebar, headers, grouping containers |
| Text (Primary) | White | #FFFFFF | rgb(255, 255, 255) | Main content text |
| Text (Secondary) | White | #FFFFFF | rgb(255, 255, 255) | Labels, captions, secondary text |
| Border | White | #FFFFFF | rgb(255, 255, 255) | Dividers, borders, separators |
| Accent | Yellow | #FFFF00 | rgb(255, 255, 0) | Interactive elements, buttons, links |
| Hover State | Yellow | #FFFF00 | rgb(255, 255, 0) | Hover effect background with black text |
| Focus Outline | Yellow | #FFFF00 | rgb(255, 255, 0) | Thick (3px) focus indicators |

#### 1.2.4 Status and Feedback Colors
| Purpose | Light Theme | Dark Theme | High Contrast | Usage |
|:--------|:------------|:-----------|:--------------|:------|
| Success | #4CAF50 | #81C784 | #FFFFFF | Operations completed successfully |
| Error | #F44336 | #E57373 | #FFFF00 | Critical errors, failed operations |
| Warning | #FF9800 | #FFB74D | #FFFF00 | Warnings, cautions, attention required |
| Information | #2196F3 | #64B5F6 | #FFFFFF | Informational messages, hints |
| Required Field | #F44336 | #E57373 | #FFFF00 | Asterisk for required fields |

### 1.3 Typography
- Font Family: Inter or system-native font stack (Inter, Roboto, Helvetica Neue, -apple-system, BlinkMacSystemFont, sans-serif).
- Font Weight: Regular (400), Medium (500), Bold (700) only.
- Font Sizes:
  - Page Title: 24px (1.5rem)
  - Section Title: 18px (1.125rem)
  - Subsection Title: 16px (1rem)
  - Body Text: 14px (0.875rem)
  - Small Text: 12px (0.75rem)
  - Input Fields: 14px (0.875rem)
  - Buttons: 14px (0.875rem)
- Line Heights:
  - Headings: 1.2 × font size
  - Body Text: 1.5 × font size
  - Form Fields: 1.5 × font size
- Letter Spacing:
  - Headings: -0.01em
  - Body Text: 0
  - Small Text: 0.01em

### 1.4 Icon System
- Use PySide6 (Qt) standard icon set where available
- Supplement with custom SVG icons where needed
- All icons must have:
  - Minimum size of 24×24 pixels
  - Consistent stroke width (1-2px)
  - Centered in 24×24 bounding box
  - Provided in all theme variations
  - Simple, outline-based design

### 1.5 UI Consistency Elements
- Version indicator displayed in status bar and About dialog
- Consistent placement of common actions (top-right for primary actions)
- Persistent keyboard shortcut hints in tooltips
- Status indicators for offline/online in footer
- Consistent padding and margins throughout interface

## 2. Layout and Information Architecture
### 2.1 Overall Structure
- Sidebar (Persistent, collapsible)
- Top Bar (Search, Save, Export, Import)
- Main Content Area (Lists, Forms, or Dashboard)
- Tabbed Interface for working with multiple forms simultaneously
- Optional Footer (App version, Offline indicator)

### 2.2 Key Modules
- Forms
- Saved Forms
- Dashboard (showing form completion status across an incident)
- Settings
- Help (including interactive help)

## 3. Navigation and Flow
- Sidebar-driven navigation.
- Top Bar for context-sensitive actions.
- Modals for confirmations only.
- Instant transitions, no page reloads.
- Keyboard shortcuts for all common operations with visual reference.
- "Recently Edited" quick access panel.
- Form completion checklist for tracking required documentation.

## 4. Forms and Data Entry
- Vertical stacking of fields.
- Labels above fields.
- Mandatory fields marked with *.
- Logical sectioning.
- Clear visual indication of attached files.
- Background saving to prevent data loss.
- Undo/redo functionality using command pattern.
- Form templates with pre-filled common fields based on context.

## 5. Data Management
### 5.1 Tables
- 50 rows per page max.
- Pagination at bottom.
- Columns: Label headers, single-column sorting.
- Bulk actions supported.
- Lazy loading for large datasets.
- Batch operations for working with multiple forms simultaneously.

### 5.2 Search, Filter, Sort
- Always-visible search bar.
- Basic filtering options.
- Single-column sorting.
- Enhanced search capabilities across all form fields.
- Configurable form ordering system based on incident type.

## 6. User Settings Panel
- Theme selection (Light/Dark/High Contrast modes).
- Save location selection.
- User name and call sign input.
- Customizable keyboard shortcuts.
- Database configuration options.
- Backup strategy settings.

## 7. Exporting and Importing Forms
- JSON, PDF, and ICS-DES export formats.
- Batch export/import operations.
- Differential file format for efficient radio transmission.
- "Package" export format that includes all attachments.
- Merge capabilities for reconciling forms from different sources.
- Cross-form data extraction for reporting purposes.
- Export format suitable for integration with other systems.

## 8. Help and Support
- Local-only Help content (Markdown or light HTML).
- Include overview, how-to, troubleshooting, keyboard shortcuts.
- Interactive help within the application.
- Video tutorials for common operations.
- Troubleshooting guides for common issues.
- Guided workflow option for new users.

## 9. Notifications and User Feedback
- Toast notifications.
- Inline error messages.
- Confirmation dialogs for potentially destructive actions.
- Error severity classification system (critical, error, warning, info).
- Specific error codes for common issues that can be referenced in documentation.
- Standardized error logging format.

## 10. Offline Functionality
- Full functionality offline.
- Offline status indicated.
- Local storage for caching.
- Background synchronization for future cloud features.

## 11. Accessibility Guidelines

### 11.1 Core Accessibility Requirements

The application must be accessible to users with various abilities, meeting or exceeding WCAG 2.1 AA compliance standards.

#### 11.1.1 Keyboard Navigation
- **Complete Keyboard Access**: All functionality must be operable through keyboard without requiring specific timing for key presses
- **Focus Indicators**: Highly visible focus states for all interactive elements (3px blue border in Light/Dark modes, 3px yellow border in High Contrast mode)
- **Focus Order**: Logical tab order following visual layout (top to bottom, left to right)
- **Keyboard Shortcuts**:
  - All common actions must have keyboard shortcuts
  - Shortcuts must be displayed in tooltips
  - Shortcuts must not conflict with browser or screen reader shortcuts
  - Custom shortcuts must be configurable in settings

#### 11.1.2 Screen Reader Support
- **Semantic HTML**: Use proper HTML elements for their intended purpose
- **ARIA Attributes**: Implement ARIA labels, roles, and properties where native semantics are insufficient
- **Descriptive Labels**: All form controls must have clear, descriptive labels
- **Form Instructions**: Error messages and validation must be programmatically associated with inputs
- **Dynamic Content Updates**: Use aria-live regions for important updates
- **Custom Controls**: Complex custom controls must implement appropriate ARIA patterns

### 11.2 Visual Accessibility

#### 11.2.1 Color and Contrast
- **Contrast Ratios**:
  - 4.5:1 minimum for normal text
  - 3:1 minimum for large text (18pt or 14pt bold)
  - 3:1 minimum for UI components and graphical objects
- **Color Independence**: Information must never be conveyed by color alone
- **Text Resizing**: Support text resizing up to 200% without loss of content or functionality
- **High Contrast Theme**: Dedicated high contrast theme with clearly defined focus states

#### 11.2.2 Content Structure
- **Headings**: Proper heading hierarchy (H1-H6) with no skipped levels
- **Landmarks**: Use ARIA landmarks to identify page regions
- **Form Groups**: Group related form elements using fieldset and legend
- **Lists**: Use appropriate list elements for lists
- **Tables**: Use proper table markup with headers for data tables

### 11.3 Cognitive Accessibility
- **Clear Instructions**: Provide clear, concise instructions for complex operations
- **Consistent Layout**: Maintain consistent navigation and control placement
- **Error Prevention**: Provide warnings before destructive actions
- **Error Correction**: Clear error messages with resolution guidance
- **Autofill Support**: Support browser autofill functionality
- **Predictable Operation**: Components that look the same should behave the same

### 11.4 Accessibility Testing
- **Automated Testing**: Incorporate accessibility testing in CI/CD pipeline
- **Screen Reader Testing**: Test with at least two major screen readers (NVDA, JAWS, or VoiceOver)
- **Keyboard Testing**: Verify all functionality is accessible via keyboard alone
- **Contrast Checking**: Use tools to verify color contrast compliance
- **Regular Audits**: Conduct periodic full accessibility audits

## 12. Performance Optimization
- Lazy loading for form sections to improve initial load times.
- Lightweight for 1280x720 screens.
- Quick export/import performance (<5 seconds).
- Background saving to prevent data loss without impacting user experience.
- Efficient data caching strategy for repeated form access.

## 13. Data Visualization
- Visual data visualizations for form data to aid in situation awareness.
- Dashboard view showing form completion status across an incident.
- Progress indicators for multi-step processes.
- Clear visual indication of attached files.

## 14. Component Standards Summary
| Component | Description |
|:----------|:------------|
| Sidebar | Persistent navigation panel, collapsible |
| Topbar | Search bar, main action buttons |
| Tabs | For working with multiple forms simultaneously |
| Forms | Vertical layout, grouped sections |
| Data Tables | Sortable, paginated, hover effect |
| Dashboard | Visual overview of incident status |
| Toasts | Quick notifications |
| Modals | Confirmation dialogs |
| Settings Page | Theme, user settings, local path |
| Help Center | Interactive offline help system |
| Form Checklist | To track required documentation |
| Quick Access Panel | Showing recently edited forms |

## 15. Summary of Critical UX Constraints
| Attribute | Decision |
|:----------|:---------|
| Platform | Windows, macOS, Linux |
| Min Resolution | 1280x720 |
| Data Size | Max 2,000 records |
| Customization | Limited customization through settings |
| Branding | No branding applied |
| User Roles | Single user type (future support for roles) |
| Themes | Light, Dark, and High Contrast modes |
| Offline Operation | Fully supported |
| Exports | JSON, PDF, ICS-DES, Package Format |
| Help System | Interactive local/offline help system |

## 16. Future UI Considerations
- Cloud synchronization UI indicators
- Multi-user interface elements
- Mobile interface design guidelines
- Plugin management interface
- Advanced reporting and visualization tools
