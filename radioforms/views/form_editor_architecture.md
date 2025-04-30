# Form Editor Component Architecture

## Overview

This document outlines the architecture for the form editor components in RadioForms. These components provide the user interface for creating, editing, and managing ICS forms, building on the enhanced form models and DAO layer.

## Design Goals

1. **Separation of Concerns**: Clear separation between UI, business logic, and data
2. **Reusability**: Maximize reuse of components across different form types
3. **Extensibility**: Easy addition of new form types
4. **Consistency**: Uniform user experience across all form types
5. **Validation Feedback**: Clear visual indication of validation errors
6. **State Visualization**: Visual representation of form states and transitions

## Component Hierarchy

```
FormEditorContainer
├── FormHeader
│   ├── FormTitle
│   ├── FormStateIndicator
│   └── FormActions
├── FormBody (specific to form type)
│   ├── FormSection
│   │   └── FormField (various types)
│   └── FormCollectionSection (for collections like activity logs)
│       └── CollectionItem
└── FormFooter
    ├── ValidationSummary
    ├── FormStateTransitionControls
    └── FormMetadata
```

## Component Descriptions

### FormEditorContainer

The top-level component that orchestrates the form editing experience. It:

- Manages the overall form state
- Handles form loading and saving via the Form Model Registry
- Coordinates between subcomponents
- Manages form validation workflow

```python
class FormEditorContainer(QWidget):
    """Container widget for form editors."""
    
    def __init__(self, form_registry, form=None, form_id=None, form_type=None, parent=None):
        """
        Initialize a form editor container.
        
        Args:
            form_registry: The FormModelRegistry instance
            form: An existing form instance to edit (optional)
            form_id: ID of an existing form to load and edit (optional)
            form_type: Type of form to create if form and form_id are None
            parent: Parent widget
        """
        # ...implementation...
```

### FormHeader

Displays form identification information and global actions. Contains:

- Form title with form type and ID
- Form state indicator showing the current state
- Global actions like save, print, export

### FormBody

Form-specific component containing the actual form fields. This is implemented separately for each form type. It:

- Arranges form fields according to the official form layout
- Manages form-specific validation
- Handles data binding between UI fields and the form model

### FormSection

A logical grouping of form fields, used to organize the form into sections (e.g., "Message Details", "Routing Information").

### FormField

Base class for various types of form fields, with specific implementations for:

- TextField: Single-line text input
- TextAreaField: Multi-line text input
- DateTimeField: Date and time input
- ChoiceField: Selection from a list of options
- SignatureField: Signature capture area

Each field provides:
- Two-way data binding with the form model
- Validation and error display
- Appropriate input UI based on field type

### FormCollectionSection

Special section for handling collections like activity log entries or personnel lists. It:

- Displays a table or list of items
- Provides controls for adding, editing, and removing items
- Handles bulk operations on collections

### CollectionItem

A row or item in a collection, with inline editing capabilities.

### FormFooter

Contains validation summary, state transition controls, and metadata:

- ValidationSummary: Shows all validation errors in one place
- FormStateTransitionControls: Buttons for state transitions (approve, finalize, etc.)
- FormMetadata: Displays creation date, last modified date, version number, etc.

## Data Flow

1. **Loading a Form**:
   - FormEditorContainer loads form from registry
   - Form data is distributed to subcomponents
   - UI fields are populated with form data

2. **Editing a Form**:
   - UI components capture user input
   - Changes are reflected in form model via two-way binding
   - Validation is triggered on field changes

3. **Saving a Form**:
   - FormEditorContainer collects data from all subcomponents
   - Validation is performed on the complete form
   - Form is saved to registry, which persists via DAO

4. **State Transitions**:
   - User initiates state transition via controls
   - Required information is collected (e.g., signature)
   - Form model handles state transition logic
   - UI is updated to reflect new state

## Styling

- Use Qt stylesheets for consistent appearance
- Follow official ICS form layouts as closely as possible
- Use color coding for form states:
  - Draft: Blue
  - Approved/Finalized: Green
  - Transmitted: Orange
  - Received/Replied: Purple
  - Archived: Gray

## Form State Visualization

- State indicator uses color and icon to show current state
- State history is displayed in a timeline view
- Available state transitions are shown as enabled buttons
- Unavailable transitions are disabled with tooltips explaining why

## Validation Visualization

- Invalid fields are highlighted with red border
- Error messages appear below the field
- ValidationSummary shows all errors in one place
- Fields with validation errors have appropriate icons

## Implementation Approach

1. **Base Components First**:
   - Implement FormEditorContainer and base classes
   - Create form field components with validation

2. **Form-Specific Implementations**:
   - Implement ICS-213 form editor
   - Implement ICS-214 form editor with activity log management

3. **Advanced Features**:
   - Add state transition visualization
   - Implement version history viewer
   - Add attachment management UI

## Integration with Existing Components

- **Form Tab Widget**: Each form will be displayed in a tab
- **Main Window**: Form editors will be the main content area
- **DAO Layer**: Used for persistence via Form Model Registry
- **Enhanced Form Models**: Provide the data model and business logic

## Special Considerations

### Accessibility

- Ensure all inputs are keyboard accessible
- Use appropriate labels for screen readers
- Provide high contrast mode option
- Ensure error messages are accessible

### Performance

- Lazy-load heavy components
- Only validate affected fields on change
- Defer validation of complex rules
- Use efficient rendering for collection displays

### Form Collections

For ICS-214 activity log entries and similar collections:
- Use QTableView with custom model for efficient display
- Provide sorting and filtering
- Support drag-and-drop reordering
- Allow bulk operations (add, update, delete multiple items)

## Next Steps

1. Implement the base FormEditorContainer and essential UI components
2. Create the form-specific editor for ICS-213
3. Develop the more complex ICS-214 editor with activity log management
4. Add state transition controls and validation visualization
5. Integrate with the main application UI
