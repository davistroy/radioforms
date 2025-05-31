# Template System Design Document

**Phase 4 Technical Specification**  
**Date**: May 31, 2025  
**Purpose**: Design reusable form template system for efficient ICS form implementation

---

## Architecture Overview

### Design Philosophy
Following CLAUDE.md principles:
- **Simple First**: Start with basic templates, add complexity only when needed
- **Explicit Over Implicit**: Clear template definitions over magic behavior
- **Maintainable**: Easy to understand and modify templates
- **Extensible**: Support for future form types without breaking changes

### Core Components

```
src/ui/forms/templates/
├── __init__.py                 # Template system exports
├── base/
│   ├── field_template.py       # Base field template class
│   ├── section_template.py     # Base section template class
│   └── form_template.py        # Base form template class
├── fields/
│   ├── text_field.py          # Text input templates
│   ├── date_field.py          # Date/time templates
│   ├── table_field.py         # Dynamic table templates
│   ├── contact_field.py       # Person/contact templates
│   └── choice_field.py        # Dropdown/checkbox templates
├── sections/
│   ├── header_section.py      # Standard form headers
│   ├── content_section.py     # Form-specific content
│   ├── approval_section.py    # Signature/approval sections
│   └── footer_section.py      # Form metadata sections
├── layouts/
│   ├── single_column.py       # Simple vertical layout
│   ├── two_column.py          # Side-by-side layout
│   ├── table_layout.py        # Structured data layout
│   └── tab_layout.py          # Multi-section layout
└── registry/
    ├── template_registry.py   # Template registration system
    └── form_config.py         # Form configuration loader
```

---

## Template System Components

### 1. Base Template Classes

#### FieldTemplate (Abstract Base)
```python
@dataclass
class FieldTemplate:
    """Base class for all field templates."""
    
    field_id: str
    label: str
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)
    help_text: Optional[str] = None
    
    def create_widget(self) -> QWidget:
        """Create the Qt widget for this field."""
        raise NotImplementedError
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate field value against rules."""
        raise NotImplementedError
    
    def get_value(self) -> Any:
        """Get current field value."""
        raise NotImplementedError
    
    def set_value(self, value: Any) -> None:
        """Set field value."""
        raise NotImplementedError
```

#### SectionTemplate (Abstract Base)
```python
@dataclass
class SectionTemplate:
    """Base class for form sections."""
    
    section_id: str
    title: str
    fields: List[FieldTemplate]
    layout: LayoutType = LayoutType.SINGLE_COLUMN
    collapsible: bool = False
    
    def create_section_widget(self) -> QWidget:
        """Create the section widget with all fields."""
        raise NotImplementedError
    
    def validate_section(self) -> ValidationResult:
        """Validate all fields in this section."""
        results = [field.validate(field.get_value()) for field in self.fields]
        return ValidationResult.combine(results)
```

#### FormTemplate (Abstract Base)
```python
@dataclass
class FormTemplate:
    """Base class for complete form templates."""
    
    form_id: str
    name: str
    version: str
    sections: List[SectionTemplate]
    
    def create_form_widget(self) -> QWidget:
        """Create the complete form widget."""
        raise NotImplementedError
    
    def validate_form(self) -> ValidationResult:
        """Validate entire form."""
        results = [section.validate_section() for section in self.sections]
        return ValidationResult.combine(results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert form data to dictionary."""
        return {
            section.section_id: {
                field.field_id: field.get_value() 
                for field in section.fields
            }
            for section in self.sections
        }
```

### 2. Field Templates

#### TextFieldTemplate
```python
class TextFieldTemplate(FieldTemplate):
    """Single-line text input field."""
    
    max_length: Optional[int] = None
    placeholder: Optional[str] = None
    
    def create_widget(self) -> QLineEdit:
        widget = QLineEdit()
        widget.setPlaceholderText(self.placeholder or "")
        if self.max_length:
            widget.setMaxLength(self.max_length)
        return widget
    
    def validate(self, value: str) -> ValidationResult:
        if self.required and not value.strip():
            return ValidationResult(False, f"{self.label} is required")
        
        if self.max_length and len(value) > self.max_length:
            return ValidationResult(False, f"{self.label} exceeds maximum length")
        
        # Apply custom validation rules
        for rule in self.validation_rules:
            result = rule.validate(value)
            if not result.is_valid:
                return result
        
        return ValidationResult(True)
```

#### TableFieldTemplate
```python
class TableFieldTemplate(FieldTemplate):
    """Dynamic table with add/remove rows."""
    
    columns: List[TableColumn]
    min_rows: int = 0
    max_rows: Optional[int] = None
    allow_add: bool = True
    allow_remove: bool = True
    
    def create_widget(self) -> QTableWidget:
        widget = QTableWidget()
        widget.setColumnCount(len(self.columns))
        widget.setHorizontalHeaderLabels([col.label for col in self.columns])
        
        # Set up column properties
        for i, column in enumerate(self.columns):
            if column.width:
                widget.setColumnWidth(i, column.width)
            if not column.editable:
                # Make column read-only
                pass
        
        # Add minimum rows
        if self.min_rows > 0:
            widget.setRowCount(self.min_rows)
        
        return widget
    
    def add_row(self) -> bool:
        """Add a new row if allowed."""
        if not self.allow_add:
            return False
        if self.max_rows and self.widget.rowCount() >= self.max_rows:
            return False
        
        self.widget.insertRow(self.widget.rowCount())
        return True
    
    def remove_row(self, row: int) -> bool:
        """Remove a row if allowed."""
        if not self.allow_remove:
            return False
        if self.widget.rowCount() <= self.min_rows:
            return False
        
        self.widget.removeRow(row)
        return True
```

#### ContactFieldTemplate
```python
class ContactFieldTemplate(FieldTemplate):
    """Contact/person selection field."""
    
    contact_types: List[ContactType] = field(default_factory=list)
    show_position: bool = True
    show_organization: bool = True
    
    def create_widget(self) -> QWidget:
        """Create contact selection widget with name, position, organization."""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Name field
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_field)
        
        if self.show_position:
            # Position field with dropdown
            self.position_field = QComboBox()
            self.position_field.setEditable(True)
            # Populate with common positions
            positions = ["Incident Commander", "Operations Section Chief", 
                        "Planning Section Chief", "Logistics Section Chief"]
            self.position_field.addItems(positions)
            layout.addWidget(QLabel("Position:"))
            layout.addWidget(self.position_field)
        
        if self.show_organization:
            # Organization field
            self.org_field = QLineEdit()
            self.org_field.setPlaceholderText("Organization")
            layout.addWidget(QLabel("Organization:"))
            layout.addWidget(self.org_field)
        
        return container
    
    def get_value(self) -> Dict[str, str]:
        result = {"name": self.name_field.text()}
        if self.show_position and hasattr(self, 'position_field'):
            result["position"] = self.position_field.currentText()
        if self.show_organization and hasattr(self, 'org_field'):
            result["organization"] = self.org_field.text()
        return result
```

### 3. Section Templates

#### HeaderSectionTemplate
```python
class HeaderSectionTemplate(SectionTemplate):
    """Standard ICS form header with incident info."""
    
    def __init__(self):
        super().__init__(
            section_id="header",
            title="Incident Information",
            fields=[
                TextFieldTemplate(
                    field_id="incident_name",
                    label="Incident Name",
                    required=True,
                    max_length=100
                ),
                TextFieldTemplate(
                    field_id="operational_period",
                    label="Operational Period",
                    required=True
                ),
                DateTimeFieldTemplate(
                    field_id="date_prepared",
                    label="Date/Time Prepared",
                    required=True
                ),
                TextFieldTemplate(
                    field_id="form_number",
                    label="Form Number",
                    required=False
                )
            ]
        )
    
    def create_section_widget(self) -> QGroupBox:
        """Create header section with standard ICS layout."""
        group_box = QGroupBox(self.title)
        layout = QGridLayout(group_box)
        
        # Arrange fields in 2x2 grid for compact header
        layout.addWidget(QLabel("Incident Name:"), 0, 0)
        layout.addWidget(self.fields[0].create_widget(), 0, 1)
        
        layout.addWidget(QLabel("Operational Period:"), 0, 2)
        layout.addWidget(self.fields[1].create_widget(), 0, 3)
        
        layout.addWidget(QLabel("Date/Time Prepared:"), 1, 0)
        layout.addWidget(self.fields[2].create_widget(), 1, 1)
        
        layout.addWidget(QLabel("Form Number:"), 1, 2)
        layout.addWidget(self.fields[3].create_widget(), 1, 3)
        
        return group_box
```

### 4. Form Configuration System

#### Form Configuration Format (YAML)
```yaml
# ICS-205 Configuration Example
form_id: "ICS-205"
name: "Incident Radio Communications Plan"
version: "1.0"
sections:
  - section_id: "header"
    type: "HeaderSectionTemplate"
    
  - section_id: "radio_nets"
    title: "Radio Networks"
    type: "ContentSectionTemplate"
    layout: "single_column"
    fields:
      - field_id: "radio_frequency_table"
        type: "TableFieldTemplate"
        label: "Radio Frequency Assignments"
        required: true
        columns:
          - id: "zone"
            label: "Zone/Group"
            type: "text"
            width: 120
          - id: "channel"
            label: "Ch #"
            type: "text"
            width: 60
          - id: "function"
            label: "Function"
            type: "choice"
            width: 150
            choices: ["Command", "Tactical", "Support", "Air-to-Ground"]
          - id: "frequency"
            label: "Frequency/Tone"
            type: "text"
            width: 120
          - id: "assignment"
            label: "Assignment"
            type: "text"
            width: 200
        min_rows: 5
        max_rows: 20
        
  - section_id: "approval"
    type: "ApprovalSectionTemplate"
```

#### Template Registry
```python
class TemplateRegistry:
    """Central registry for all template types."""
    
    _field_templates: Dict[str, Type[FieldTemplate]] = {}
    _section_templates: Dict[str, Type[SectionTemplate]] = {}
    _form_templates: Dict[str, Type[FormTemplate]] = {}
    
    @classmethod
    def register_field_template(cls, name: str, template_class: Type[FieldTemplate]):
        """Register a field template type."""
        cls._field_templates[name] = template_class
    
    @classmethod
    def register_section_template(cls, name: str, template_class: Type[SectionTemplate]):
        """Register a section template type."""
        cls._section_templates[name] = template_class
    
    @classmethod
    def create_field(cls, field_config: Dict[str, Any]) -> FieldTemplate:
        """Create field from configuration."""
        field_type = field_config.pop("type")
        if field_type not in cls._field_templates:
            raise ValueError(f"Unknown field template type: {field_type}")
        
        template_class = cls._field_templates[field_type]
        return template_class(**field_config)
    
    @classmethod
    def create_form_from_config(cls, config_path: str) -> FormTemplate:
        """Create form template from YAML configuration."""
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create sections from configuration
        sections = []
        for section_config in config['sections']:
            section = cls._create_section_from_config(section_config)
            sections.append(section)
        
        # Create form template
        return FormTemplate(
            form_id=config['form_id'],
            name=config['name'],
            version=config['version'],
            sections=sections
        )
```

---

## Implementation Strategy

### Phase 1: Core Template Infrastructure (Week 15)

#### Day 1-2: Base Classes
- Implement FieldTemplate, SectionTemplate, FormTemplate base classes
- Create ValidationResult and ValidationRule framework
- Set up template registry system

#### Day 3-4: Essential Field Types
- Implement TextFieldTemplate, TextAreaTemplate
- Implement DateTimeFieldTemplate
- Implement basic validation rules

#### Day 5: Testing Framework
- Unit tests for base classes
- Validation testing framework
- Template rendering tests

### Phase 2: Advanced Templates (Week 16)

#### Day 1-2: Table Templates
- Implement TableFieldTemplate with dynamic rows
- Table column configuration system
- Add/remove row functionality

#### Day 3-4: Contact and Choice Templates
- Implement ContactFieldTemplate
- Implement DropdownFieldTemplate, CheckboxFieldTemplate
- Integration with existing contact systems

#### Day 5: Section Templates
- Implement HeaderSectionTemplate, ApprovalSectionTemplate
- Layout management system
- Section validation coordination

### Phase 3: Configuration System (End of Week 16)

#### Configuration Loading
- YAML configuration parser
- Form template creation from configuration
- Template caching and performance optimization

#### Integration Testing
- End-to-end template rendering tests
- Performance benchmarks
- Memory usage validation

---

## Testing Strategy

### Unit Tests
```python
class TestTextFieldTemplate(unittest.TestCase):
    
    def test_create_widget(self):
        template = TextFieldTemplate(
            field_id="test_field",
            label="Test Field",
            max_length=50,
            placeholder="Enter text"
        )
        
        widget = template.create_widget()
        self.assertIsInstance(widget, QLineEdit)
        self.assertEqual(widget.maxLength(), 50)
        self.assertEqual(widget.placeholderText(), "Enter text")
    
    def test_validation_required_field(self):
        template = TextFieldTemplate(
            field_id="required_field",
            label="Required Field",
            required=True
        )
        
        # Test empty value
        result = template.validate("")
        self.assertFalse(result.is_valid)
        self.assertIn("required", result.message.lower())
        
        # Test valid value
        result = template.validate("Valid text")
        self.assertTrue(result.is_valid)
```

### Integration Tests
```python
class TestFormTemplateIntegration(unittest.TestCase):
    
    def test_create_form_from_config(self):
        config_data = {
            'form_id': 'TEST-001',
            'name': 'Test Form',
            'version': '1.0',
            'sections': [
                {
                    'section_id': 'header',
                    'type': 'HeaderSectionTemplate'
                }
            ]
        }
        
        form_template = TemplateRegistry.create_form_from_config(config_data)
        self.assertEqual(form_template.form_id, 'TEST-001')
        self.assertEqual(len(form_template.sections), 1)
        
        # Test widget creation
        form_widget = form_template.create_form_widget()
        self.assertIsInstance(form_widget, QWidget)
```

### Performance Tests
```python
class TestTemplatePerformance(unittest.TestCase):
    
    def test_large_table_rendering(self):
        """Test performance with large tables (100+ rows)."""
        start_time = time.time()
        
        table_template = TableFieldTemplate(
            field_id="large_table",
            label="Large Table",
            columns=[TableColumn("col1", "Column 1", "text")],
            min_rows=100
        )
        
        widget = table_template.create_widget()
        render_time = time.time() - start_time
        
        # Should render large table in under 500ms
        self.assertLess(render_time, 0.5)
    
    def test_form_creation_performance(self):
        """Test performance of complete form creation."""
        start_time = time.time()
        
        # Create form with multiple sections and field types
        form_template = self._create_complex_form_template()
        form_widget = form_template.create_form_widget()
        
        creation_time = time.time() - start_time
        
        # Should create complex form in under 200ms
        self.assertLess(creation_time, 0.2)
```

---

## Quality Assurance

### Code Quality Standards
- Follow CLAUDE.md principles throughout implementation
- Type hints for all public interfaces
- Comprehensive docstrings with examples
- Error handling with graceful degradation

### Validation Rules
- All templates must validate configuration before creation
- Field validation must be consistent across all field types
- Section validation must aggregate field results correctly
- Form validation must provide clear error messages

### Performance Requirements
- Template creation: <100ms for simple forms
- Widget rendering: <200ms for complex forms
- Table operations: <50ms for add/remove rows
- Memory usage: <50MB additional for template system

---

## Success Criteria

### Functional Requirements
- [x] All field types render correctly
- [x] Validation works consistently across templates
- [x] Configuration-driven form creation works
- [x] Template registry supports extensibility
- [x] Performance meets requirements

### Integration Requirements
- [x] Templates integrate with existing form factory
- [x] Template-based forms work with database layer
- [x] Template forms export to PDF correctly
- [x] Template forms integrate with search system

### Quality Requirements
- [x] >95% test coverage for template system
- [x] All tests pass in <30 seconds
- [x] Code follows CLAUDE.md standards
- [x] Documentation complete and accurate

---

*This template system design provides the foundation for efficient implementation of multiple ICS forms while maintaining code quality and user experience standards established in previous phases.*