# RadioForms Project: AI Assistant Guide

## Project Overview

**RadioForms** is a standalone, offline-first desktop application for creating, managing, exporting, and archiving FEMA Incident Command System (ICS) forms. Built using Python and PySide6, it provides administrative staff and radio operators with a modern, user-friendly interface for managing ICS forms while supporting offline operation and multiple export formats including a specialized radio transmission format (ICS-DES).

### Key Project Characteristics
- **Technology Stack**: Python 3.10+, PySide6 (Qt for Python), SQLite
- **Deployment**: Single-file executable for Windows, macOS, and Linux
- **Operation Mode**: Offline-only (no cloud/network dependencies)
- **Target Users**: Administrative staff and radio operators in emergency management
- **Form Coverage**: 20+ ICS forms (201-225 series) with MVP focus on ICS-213 and ICS-214

## Architecture & Technical Foundation

### Core Technology Principles
1. **Offline-First Architecture**: No internet connection required
2. **Single-File Application**: Portable executable with SQLite database
3. **Cross-Platform Compatibility**: Windows, macOS, Linux support
4. **Event-Driven Design**: PySide6 signal-slot architecture
5. **Plugin Architecture**: Extensible form system for future additions

### Database Strategy
- **Storage**: SQLite with Write-Ahead Logging (WAL) mode
- **Location**: Default in application directory, user-configurable
- **Version Control**: Semantic versioning for app, date-based for forms
- **Backup**: Automatic backup on application close with rotation policies

### Performance Requirements
- **Startup**: Cold start < 3 seconds, warm start < 1.5 seconds
- **UI Responsiveness**: Form loading < 300ms, field updates < 50ms
- **Scalability**: Support up to 2,000 forms with pagination
- **Memory**: Base footprint < 150MB, max usage < 500MB

## Project Structure & File Organization

```
radioforms/
├── docs/                           # Project documentation
│   ├── prd.md                     # Product Requirements Document
│   ├── tdd.md                     # Technical Design Document (read via TDD read limit)
│   ├── UI-UX.md                   # UI/UX Guidelines with theme specifications
│   └── ics-des.md                 # Radio transmission encoding specification
├── forms/                         # ICS forms analysis and specifications
│   ├── ICS-Forms-Analysis-Summary.md  # Executive summary of all forms
│   ├── forms_analysis.md              # Original analysis requirements
│   └── ICS-[XXX]-Analysis.md          # Individual form specifications
├── rules/                         # Development coding standards
│   ├── python-rules.md           # Python best practices and patterns
│   ├── pyside6-rules.md          # PySide6 GUI development guidelines
│   └── generic-rules.md          # General coding principles and anti-patterns
└── src/                          # Source code (to be created)
    ├── main.py                   # Application entry point
    ├── app/                      # Application core
    ├── ui/                       # User interface components
    ├── models/                   # Data models and business logic
    ├── controllers/              # Form controllers and business logic
    ├── database/                 # Database layer and migrations
    ├── utils/                    # Utility functions and helpers
    └── resources/                # Assets, icons, stylesheets
```

## Form System Architecture

### Supported ICS Forms (20+ forms analyzed)
**MVP Priority Forms:**
- ICS-213: General Message (radio communication)
- ICS-214: Activity Log (personnel activity tracking)

**Full Implementation Forms:**
- Planning: ICS-201, ICS-202, ICS-203, ICS-204, ICS-205, ICS-205A, ICS-206, ICS-207
- Operations: ICS-208, ICS-209, ICS-210, ICS-211, ICS-215, ICS-215A
- Support: ICS-218, ICS-220, ICS-221, ICS-225

### Form Data Patterns
1. **Common Fields**: Incident name, operational period, preparer, date/time
2. **Hierarchical Structure**: Header (identification) → Content (form-specific) → Footer (approval)
3. **Relationship Dependencies**: Forms reference each other (ICS-202 → ICS-215 → ICS-204)
4. **Repeatable Sections**: Dynamic tables for resources, assignments, activities

### Export Formats
1. **JSON**: Complete form data with metadata and version history
2. **PDF**: Print-ready format matching FEMA layouts
3. **ICS-DES**: Ultra-compact radio transmission format with numeric field codes
4. **Package Format**: JSON with all attachments for archiving

## Development Guidelines & Coding Standards

### Python Development (python-rules.md)
- **Core Philosophy**: Explicit > implicit, Simple > complex
- **Required**: Virtual environments, type hints, dataclasses
- **Testing**: pytest with >80% coverage, fast execution (<30 seconds)
- **Code Quality**: Black formatting, ruff linting, mypy type checking
- **Anti-Patterns**: No mutable defaults, bare except clauses, or global state

### PySide6 GUI Development (pyside6-rules.md)
- **Core Principle**: Never block the main UI thread
- **Architecture**: Model-View separation, signal-slot communication
- **Threading**: QThread for background operations, signals for UI updates
- **Resource Management**: Proper widget parenting, context managers
- **Styling**: QSS stylesheets with light/dark/high-contrast themes

### General Coding Principles (generic-rules.md)
- **Simplicity First**: If it's not working simply, it won't work complexly
- **Incremental Development**: One feature completely before the next
- **Dependency Management**: Prefer built-in solutions, avoid bleeding edge
- **Testing Strategy**: Simple, fast tests that actually run

## User Interface Design System

### Theme System (UI-UX.md)
**Light Theme:**
- Primary Background: #FFFFFF
- Text: #212121 (primary), #757575 (secondary)
- Accent: #1976D2 (blue)

**Dark Theme:**
- Primary Background: #212121
- Text: #E0E0E0 (primary), #BDBDBD (secondary)
- Accent: #64B5F6 (light blue)

**High Contrast Theme:**
- Background: #000000, Text: #FFFFFF
- Accent: #FFFF00 (yellow)
- Focus: 3px yellow borders

### Layout Principles
- **Structure**: Sidebar navigation + main content area + optional footer
- **Forms**: Vertical field stacking, labels above fields, logical sectioning
- **Tables**: 50 rows max per page, single-column sorting, bulk actions
- **Accessibility**: WCAG 2.1 AA compliance, full keyboard navigation

## Core Features & Implementation Priorities

### Phase 1: MVP Foundation
1. **Application Setup**
   - PySide6 main window with basic layout
   - SQLite database initialization with WAL mode
   - User configuration (name, call sign, incident name)
   - Settings persistence and window state restoration

2. **Form Management Core**
   - ICS-213 and ICS-214 form implementation
   - Basic CRUD operations with version tracking
   - Automatic saving with background persistence
   - Form search and filtering capabilities

3. **Export System**
   - JSON export for data portability
   - ICS-DES encoding for radio transmission
   - PDF generation with ReportLab

### Phase 2: Enhanced Features
1. **Complete Form Set**
   - All 20+ ICS forms with proper validation
   - Form interdependency handling
   - Template system with pre-filled common fields

2. **Advanced UI Features**
   - Tabbed interface for multiple forms
   - Dashboard with form completion status
   - Recently used forms quick access
   - Keyboard shortcuts for all operations

3. **Data Management**
   - Import/export functionality
   - Database switching for multiple incidents
   - Backup and archive operations

### Phase 3: Advanced Capabilities
1. **Plugin Architecture**
   - Custom form type support
   - Configurable form ordering by incident type
   - Third-party integration hooks

2. **Enhanced User Experience**
   - Interactive help system
   - Visual data representations
   - Form completion checklists
   - Accessibility enhancements

## Radio Transmission Integration (ICS-DES)

### ICS-DES Format Specification
- **Purpose**: Ultra-compact encoding for low-bandwidth radio transmission
- **Structure**: Numeric field codes with enumeration tables
- **Format**: `FID{c1~v1|c2~v2|...}` where FID is form number, fields pipe-separated
- **Optimization**: Form-specific field requirements matrix reduces transmission size

### Key Features
- Character escaping for special characters
- Enumeration tables for status codes and positions
- Field requirement matrix for transmission optimization
- Automatic clipboard integration for radio operators

## Testing & Quality Assurance

### Testing Strategy
- **Unit Tests**: Core business logic with property-based testing
- **Integration Tests**: Database operations and form workflows
- **UI Tests**: pytest-qt for widget testing and user journeys
- **Performance Tests**: Benchmark validation against requirements
- **Visual Regression**: Automated UI appearance validation

### Quality Gates
- All tests passing in CI/CD pipeline
- Type checking with mypy
- Code formatting with Black
- Linting with ruff
- Security scanning with pip-audit
- Documentation completeness check

## Deployment & Distribution

### Build Requirements
- Python 3.10+ with PySide6
- PyInstaller for executable creation
- Platform-specific packaging (Windows .exe, macOS .app, Linux AppImage)
- Resource compilation with pyside6-rcc

### Distribution Strategy
- Single-file executables for each platform
- No installation required (portable applications)
- Automatic database creation on first run
- Settings migration between versions

## Security & Data Protection

### Security Model
- Local-only data storage (no network transmission)
- Optional data encryption at rest for sensitive information
- Audit logging for all data modifications
- Secure deletion options for sensitive forms
- Digital signature support for form validation

### Privacy Considerations
- No telemetry or data collection
- User data remains on local machine
- Export operations under user control
- Attachment handling with explicit user consent

## Future Considerations

### Planned Enhancements
- Cloud synchronization capability (disabled by default)
- Multi-user access with role-based permissions
- Mobile companion application
- Advanced reporting and analytics
- Integration with GIS/mapping systems

### Technical Debt Prevention
- Regular dependency updates and security audits
- Code review process for all changes
- Performance monitoring and optimization
- Documentation maintenance and accuracy
- User feedback integration loops

## Development Commands & Tools

### Common Development Tasks
```bash
# Environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements-dev.txt

# Code quality
black src/
ruff check src/
mypy src/

# Testing
pytest tests/ -v --cov=src

# Resource compilation
pyside6-rcc resources.qrc -o resources_rc.py

# Build executable
pyinstaller --onefile --windowed main.py
```

### Project Health Indicators
- All tests pass in <30 seconds
- No linting or type checking errors
- Documentation is current and complete
- Dependencies are up-to-date and minimal
- User feedback is positive and actionable

## Key Documentation References

1. **Product Requirements**: `/docs/prd.md` - Complete functional requirements
2. **Technical Design**: `/docs/tdd.md` - Implementation specifications
3. **UI Guidelines**: `/docs/UI-UX.md` - Design system and accessibility
4. **Radio Protocol**: `/docs/ics-des.md` - Transmission format specification
5. **Form Analysis**: `/forms/ICS-Forms-Analysis-Summary.md` - Business rules
6. **Python Rules**: `/rules/python-rules.md` - Coding standards
7. **PySide6 Rules**: `/rules/pyside6-rules.md` - GUI development practices
8. **General Rules**: `/rules/generic-rules.md` - Development philosophy

---

*This guide provides Claude with comprehensive context for effective development assistance on the RadioForms project. Always prioritize simplicity, user needs, and maintainable code over complex technical solutions.*