# RadioForms Refactoring Implementation Plan

This document outlines a detailed, phased approach to implement the architectural improvements recommended in the architecture analysis. The plan is designed to minimize disruption to ongoing development while systematically addressing the identified issues.

## Implementation Phases Overview

| Phase | Timeline | Focus Area | Key Deliverables |
|-------|----------|------------|------------------|
| 1 | Weeks 1-2 | Setup & Database Layer | SQLAlchemy integration, initial schema migration |
| 2 | Weeks 3-4 | Core Model Refactoring | New form model implementation, adapter layer |
| 3 | Weeks 5-6 | Controller Consolidation | Application controller implementation |
| 4 | Weeks 7-8 | UI Component Redesign | New form editors and viewers |
| 5 | Weeks 9-10 | Testing & Validation | Comprehensive testing, documentation |

## Phase 1: Setup & Database Layer (Weeks 1-2)

### Week 1: Setup and Planning

#### Day 1-2: Project Setup
- [ ] Create a new branch `refactor/sqlalchemy-integration`
- [ ] Set up SQLAlchemy and Alembic in the project
  ```bash
  pip install sqlalchemy alembic
  alembic init migrations
  ```
- [ ] Configure Alembic to work with the project structure
- [ ] Create a test database for development

#### Day 3-4: Schema Analysis and Mapping
- [ ] Analyze existing database schema
- [ ] Map current schema to SQLAlchemy models
- [ ] Define relationships between models
- [ ] Set up initial migration script

#### Day 5: Testing Setup
- [ ] Set up pytest fixtures for database testing
- [ ] Create test cases for basic database operations
- [ ] Implement CI integration for the refactoring branch

### Week 2: Database Implementation

#### Day 1-2: Core Models Implementation
- [ ] Implement SQLAlchemy models for core entities:
  - [ ] Form
  - [ ] Incident
  - [ ] User
  - [ ] Attachment
  - [ ] FormVersion

```python
# Example implementation of core models
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    forms = relationship("Form", back_populates="incident")

class Form(Base):
    __tablename__ = 'forms'
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey('incidents.id'))
    form_type = Column(String(20), nullable=False)
    title = Column(String(150))
    state = Column(String(20), default='draft')
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    creator_id = Column(Integer, ForeignKey('users.id'))
    
    incident = relationship("Incident", back_populates="forms")
    versions = relationship("FormVersion", back_populates="form")
    attachments = relationship("Attachment", back_populates="form")

# Additional models follow similar pattern
```

#### Day 3-4: Repository Implementation
- [ ] Implement repository pattern for database access
- [ ] Create repositories for each core entity
- [ ] Implement migration from old DAO pattern to new repository pattern

```python
# Example repository implementation
class FormRepository:
    def __init__(self, session):
        self.session = session
        
    def get_by_id(self, form_id):
        return self.session.query(Form).filter(Form.id == form_id).first()
        
    def get_all_for_incident(self, incident_id):
        return self.session.query(Form).filter(Form.incident_id == incident_id).all()
        
    def create(self, form_data):
        form = Form(**form_data)
        self.session.add(form)
        self.session.commit()
        return form
        
    def update(self, form_id, form_data):
        form = self.get_by_id(form_id)
        if not form:
            return None
            
        for key, value in form_data.items():
            setattr(form, key, value)
            
        self.session.commit()
        return form
        
    def delete(self, form_id):
        form = self.get_by_id(form_id)
        if not form:
            return False
            
        self.session.delete(form)
        self.session.commit()
        return True
        
    def find_with_content(self, form_id, version=None):
        form = self.get_by_id(form_id)
        if not form:
            return None
            
        if version:
            content = (self.session.query(FormVersion)
                       .filter(FormVersion.form_id == form_id)
                       .filter(FormVersion.version_number == version)
                       .first())
        else:
            content = (self.session.query(FormVersion)
                       .filter(FormVersion.form_id == form_id)
                       .order_by(FormVersion.version_number.desc())
                       .first())
                       
        if not content:
            return form, {}
            
        return form, json.loads(content.content)
```

#### Day 5: Data Migration
- [ ] Create data migration scripts to move from old schema to new schema
- [ ] Test migration on sample data
- [ ] Validate data integrity after migration

## Phase 2: Core Model Refactoring (Weeks 3-4)

### Week 3: Form Model Implementation

#### Day 1-2: Base Model Framework
- [ ] Create Python dataclass-based form models
- [ ] Implement serialization/deserialization
- [ ] Implement validation logic

```python
# Example of dataclass-based form model
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid

class FormState(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    ARCHIVED = "archived"

@dataclass
class BaseForm:
    form_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    state: FormState = FormState.DRAFT
    title: str = ""
    
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = {}
        
        if not self.title:
            errors["title"] = "Title is required"
            
        return errors
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        
        # Handle special types
        data["state"] = self.state.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseForm':
        """Create from dictionary"""
        # Handle special types
        if "state" in data:
            data["state"] = FormState(data["state"])
            
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)
```

#### Day 3-5: Specific Form Implementations
- [ ] Implement ICS-213 form model
- [ ] Implement ICS-214 form model
- [ ] Create test cases for each form model
- [ ] Implement form factory for creating different form types

### Week 4: Integration Layer

#### Day 1-2: Adapter Implementation
- [ ] Create adapter layer to connect new models with existing UI
- [ ] Implement backward compatibility for existing code
- [ ] Write comprehensive tests for the adapter layer

```python
# Example adapter to bridge old and new implementations
class FormAdapter:
    """Adapter to make new form models work with existing code"""
    
    @staticmethod
    def adapt_to_new_model(old_form) -> BaseForm:
        """Convert old form to new model"""
        if old_form.get_form_type() == "ICS-213":
            new_form = ICS213Form(
                form_id=old_form.form_id,
                title=getattr(old_form, "subject", ""),
                to=getattr(old_form, "to", ""),
                from_field=getattr(old_form, "from_field", ""),
                message=getattr(old_form, "message", ""),
                # ... other fields ...
            )
        elif old_form.get_form_type() == "ICS-214":
            # Similar conversion for ICS-214
            pass
        else:
            raise ValueError(f"Unsupported form type: {old_form.get_form_type()}")
            
        return new_form
        
    @staticmethod
    def adapt_to_old_model(new_form):
        """Convert new form to old model format for backward compatibility"""
        # Implementation depends on old model structure
        pass
```

#### Day 3-5: Repository Integration
- [ ] Connect form models with repositories
- [ ] Implement persistence operations for new models
- [ ] Create integration tests for the full data flow

## Phase 3: Controller Consolidation (Weeks 5-6)

### Week 5: Application Controller Framework

#### Day 1-2: Controller Design
- [ ] Design the unified ApplicationController interface
- [ ] Define interaction patterns with UI and models
- [ ] Create a detailed controller class diagram

#### Day 3-5: Core Controller Implementation
- [ ] Implement ApplicationController basic functionality
- [ ] Create form management methods
- [ ] Implement incident management methods
- [ ] Write unit tests for controller operations

```python
# Example ApplicationController implementation
class ApplicationController:
    """Main application controller that handles all app functionality"""
    
    def __init__(self, db_url=None):
        """Initialize controller with database connection"""
        self.engine = create_engine(db_url or 'sqlite:///radioforms.db')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize repositories
        self.form_repository = FormRepository(self.session)
        self.incident_repository = IncidentRepository(self.session)
        self.user_repository = UserRepository(self.session)
        self.attachment_repository = AttachmentRepository(self.session)
        
        # Form factory for creating forms
        self.form_factory = FormFactory()
        
        # UI state
        self.main_window = None
        
    def start_application(self):
        """Initialize and start the application UI"""
        self.main_window = MainWindow(self)
        self.main_window.show()
        
    # Form operations
    def create_form(self, form_type, initial_data=None):
        """Create a new form"""
        # Create form through factory
        form = self.form_factory.create_form(form_type)
        
        # Set initial data if provided
        if initial_data:
            for key, value in initial_data.items():
                if hasattr(form, key):
                    setattr(form, key, value)
                    
        # Save to database through repository
        db_form = self.form_repository.create({
            "form_type": form.form_type,
            "title": form.title,
            "state": form.state.value,
            # ... other fields ...
        })
        
        # Update form ID from database
        form.form_id = str(db_form.id)
        
        return form
        
    def load_form(self, form_id):
        """Load a form by ID"""
        form_data, content = self.form_repository.find_with_content(form_id)
        if not form_data:
            return None
            
        # Create form of appropriate type
        form = self.form_factory.create_form(form_data.form_type)
        
        # Populate with data
        form.form_id = str(form_data.id)
        form.title = form_data.title
        form.state = FormState(form_data.state)
        form.created_at = form_data.created_at
        form.updated_at = form_data.updated_at
        
        # Set form-specific content
        for key, value in content.items():
            if hasattr(form, key):
                setattr(form, key, value)
                
        return form
    
    # Additional methods for incidents, users, etc.
```

### Week 6: Advanced Controller Functionality

#### Day 1-2: Specialized Operations
- [ ] Implement form state transition logic
- [ ] Implement attachment handling
- [ ] Implement export functionality

#### Day 3-4: Event System
- [ ] Implement event system for model changes
- [ ] Connect controller to UI update mechanisms
- [ ] Create tests for event propagation

#### Day 5: Legacy Integration
- [ ] Create bridge between new controller and old controllers
- [ ] Implement graceful degradation for unsupported operations
- [ ] Test backward compatibility

## Phase 4: UI Component Redesign (Weeks 7-8)

### Week 7: Form Component Framework

#### Day 1-2: Base Components
- [ ] Create FormEditorBase class
- [ ] Implement basic UI structure
- [ ] Define common patterns for all form editors

```python
# Example form editor base class
class FormEditorBase(QWidget):
    """Base class for all form editors"""
    
    formChanged = Signal()  # Signal emitted when form data changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._form = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up common UI elements"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Header
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        
        # Form type label
        self.form_type_label = QLabel()
        self.form_type_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.header_layout.addWidget(self.form_type_label)
        
        # Spacer
        self.header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel()
        self.header_layout.addWidget(self.status_label)
        
        # Add header to main layout
        self.main_layout.addWidget(self.header_widget)
        
        # Content area - to be implemented by subclasses
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.main_layout.addWidget(self.content_widget)
        
        # Buttons area
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        
        # Add stretch to push buttons to the right
        self.buttons_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.buttons_layout.addWidget(self.save_button)
        
        # Add buttons to main layout
        self.main_layout.addWidget(self.buttons_widget)
        
    def set_form(self, form):
        """Set the form to edit"""
        self._form = form
        
        # Update header
        if form:
            self.form_type_label.setText(form.form_type)
            self.status_label.setText(f"Status: {form.state.name}")
            
        # Update content
        self._update_ui_from_form()
        
    def get_form(self):
        """Get the current form"""
        return self._form
        
    def _update_ui_from_form(self):
        """Update UI from form data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _update_ui_from_form")
        
    def _update_form_from_ui(self):
        """Update form data from UI - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _update_form_from_ui")
        
    def _on_save_clicked(self):
        """Handle save button click"""
        # Update form from UI
        self._update_form_from_ui()
        
        # Emit signal
        self.formChanged.emit()
```

#### Day 3-5: Specific Form Editors
- [ ] Implement ICS-213 form editor
- [ ] Implement ICS-214 form editor
- [ ] Create common validation and error display

### Week 8: UI Integration

#### Day 1-2: Tab Management
- [ ] Implement tab management system
- [ ] Create form opening and closing logic
- [ ] Implement dirty state tracking and save prompts

#### Day 3-4: Main Window Integration
- [ ] Connect new UI components to main window
- [ ] Implement form selection dialogs
- [ ] Create incident management UI

#### Day 5: Polishing
- [ ] Implement styling improvements
- [ ] Fix layout issues
- [ ] Ensure consistent look and feel

## Phase 5: Testing & Validation (Weeks 9-10)

### Week 9: Comprehensive Testing

#### Day 1-2: Unit Testing
- [ ] Complete unit tests for all new components
- [ ] Ensure test coverage for critical paths
- [ ] Fix issues identified during testing

#### Day 3-4: Integration Testing
- [ ] Create end-to-end tests for common workflows
- [ ] Test cross-component interactions
- [ ] Verify database operations

#### Day 5: Performance Testing
- [ ] Benchmark core operations
- [ ] Identify and fix performance issues
- [ ] Test with large datasets

### Week 10: Finalization

#### Day 1-2: Documentation
- [ ] Update code documentation
- [ ] Create architectural documentation
- [ ] Write user guide for developers

#### Day 3-4: Final Validation
- [ ] Conduct peer code reviews
- [ ] Run full test suite
- [ ] Address any remaining issues

#### Day 5: Deployment Preparation
- [ ] Prepare migration guide for users
- [ ] Create release notes
- [ ] Finalize branch for merging to main

## Risk Management

### Identified Risks and Mitigation Strategies

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| Data loss during migration | Medium | High | Create comprehensive backups; implement rollback capability; validate data integrity after each migration step |
| Compatibility issues with existing code | High | Medium | Implement adapter pattern; maintain backward compatibility; extensive testing of integration points |
| Performance regression | Medium | Medium | Benchmark key operations; performance testing with realistic data volumes; optimize critical paths |
| Incomplete test coverage | Medium | High | Define test coverage targets; code review focusing on testability; prioritize testing of core functionality |
| Schedule slippage | Medium | Medium | Build in buffer time; prioritize critical path items; consider phased rollout |

### Contingency Plans

1. **Rollback Strategy**: Maintain the ability to revert to the previous implementation at each phase.
2. **Parallel Systems**: Run old and new implementations side by side during transition.
3. **Feature Freezes**: Implement temporary feature freezes during critical migration periods.
4. **User Communication**: Keep users informed about changes and potential disruptions.

## Team Organization

### Roles and Responsibilities

| Role | Responsibilities | Skills Required |
|------|-----------------|----------------|
| Technical Lead | Overall architecture design; code review; key decisions | Strong architecture skills; experience with refactoring; Python expertise |
| Database Engineer | Schema design; migration scripts; ORM implementation | SQLAlchemy experience; database design; migration expertise |
| UI Developer | Form component implementation; UI integration | PySide6/Qt experience; UI design; user experience focus |
| QA Engineer | Test design; automation; validation | Testing methodologies; Python testing frameworks; attention to detail |
| Documentation Specialist | Code documentation; architecture docs; user guides | Technical writing; documentation tools; clear communication |

### Communication Plan

- Daily stand-up meetings to track progress and identify blockers
- Weekly review of completed work and planning for the next week
- Regular technical discussions for design decisions
- Documentation updates as features are completed

## Success Criteria

The refactoring will be considered successful when:

1. All existing functionality works correctly with the new architecture
2. Code metrics show improvement in:
   - Cyclomatic complexity
   - Class and method size
   - Coupling measures
   - Test coverage
3. Performance metrics meet or exceed the current implementation
4. New features can be implemented more efficiently using the new architecture
5. Developer feedback indicates improved maintainability and understandability

## Conclusion

This implementation plan provides a structured approach to refactoring the RadioForms application to address the architectural issues identified in the analysis. By following this phased approach, the team can systematically improve the codebase while minimizing disruption to users and ongoing development.

The plan emphasizes risk management, thorough testing, and maintaining backward compatibility to ensure a smooth transition. Upon completion, the application will have a more maintainable architecture that better aligns with the actual complexity needs of the domain.
