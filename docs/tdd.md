# Technical Design Document
# ICS Forms Management Application

**Version:** 1.1  
**Date:** April 29, 2025  
**Status:** Draft

## 1. Introduction

### 1.1 Purpose
This Technical Design Document (TDD) provides the detailed technical design for implementing the ICS Forms Management Application as specified in the revised Product Requirements Document (PRD). It outlines the architecture, design patterns, data structures, and implementation details necessary for development, incorporating the recommended improvements for database design, architecture, UI/UX, performance, and security.

### 1.2 Scope
This document covers the technical design of all aspects of the application, including:
* Enhanced application architecture using event-driven patterns
* User interface design and implementation with tabbed interface
* Database design with migration support and version tracking
* Form template and plugin system
* Enhanced import/export functionality
* Comprehensive error handling and logging
* Testing approach with additional verification methods
* Performance optimizations including lazy loading
* Security enhancements including data encryption

### 1.3 References
* Revised Product Requirements Document (PRD) v1.1
* Revised DB_Design_Guidelines.md v1.1
* Revised UI_UX_Guidelines.md v1.1
* ICS-DES.md
* ICS Form Analysis documents
* Technical Recommendations Document

### 1.4 Technology Stack
* **Programming Language:** Python 3.10+
* **UI Framework:** PySide6 (Qt for Python)
* **Database:** SQLite 3 with WAL mode
* **PDF Generation:** ReportLab
* **Testing:** pytest, pytest-qt, property-based testing
* **Encryption:** Python cryptography library
* **Compression:** zlib/gzip for database compression

## 2. System Architecture

### 2.1 Architectural Overview

The ICS Forms Management Application follows an enhanced layered architecture with event-driven communication patterns:

1. **Presentation Layer (UI):** Implements the user interface using PySide6, with tabbed interface and keyboard shortcuts
2. **Application Layer:** Contains the core business logic, application services, and command pattern for undo/redo
3. **Domain Layer:** Defines the core domain models and business rules
4. **Data Access Layer:** Handles database operations with migration support and file I/O
5. **Plugin System:** Allows extending form types and functionality
6. **Services Layer:** Provides cross-cutting concerns like logging, error handling, and security

![Architecture Diagram](architecture_diagram.png)

### 2.2 Component Diagram

```
+----------------------------------+
|          Presentation Layer      |
| +------------+ +---------------+ |
| | Form Views | | List/Settings | |
| +------------+ +---------------+ |
| +-------------+ +--------------+ |
| | Tabbed      | | Dashboard    | |
| | Interface   | | View         | |
| +-------------+ +--------------+ |
+----------------------------------+
|          Application Layer       |
| +----------+ +------------------+|
| |  Form    | | Import/Export    ||
| |Controller| | Services         ||
| +----------+ +------------------+|
| +----------+ +------------------+|
| | Template | | Validation       ||
| | Service  | | Service          ||
| +----------+ +------------------+|
| +----------+ +------------------+|
| | Command  | | Event            ||
| | Processor| | Bus              ||
| +----------+ +------------------+|
+----------------------------------+
|          Plugin System           |
| +------------+ +---------------+ |
| | Plugin     | | Plugin        | |
| | Manager    | | Interfaces    | |
| +------------+ +---------------+ |
+----------------------------------+
|          Domain Layer            |
| +------------+ +---------------+ |
| | Form       | | Template      | |
| | Models     | | Models        | |
| +------------+ +---------------+ |
| +------------+ +---------------+ |
| | Command    | | Event         | |
| | Models     | | Models        | |
| +------------+ +---------------+ |
+----------------------------------+
|          Data Access Layer       |
| +------------+ +---------------+ |
| | Database   | | File System   | |
| | Repository | | Service       | |
| +------------+ +---------------+ |
| +------------+ +---------------+ |
| | Migration  | | Backup        | |
| | Service    | | Service       | |
| +------------+ +---------------+ |
+----------------------------------+
|          Services Layer          |
| +------------+ +---------------+ |
| | Logging    | | Error         | |
| | Service    | | Handler       | |
| +------------+ +---------------+ |
| +------------+ +---------------+ |
| | Security   | | Performance   | |
| | Service    | | Optimizer     | |
| +------------+ +---------------+ |
+----------------------------------+
```

### 2.3 Design Patterns

The application will implement the following design patterns:

1. **Model-View-Controller (MVC):** Separates the application into three interconnected components to separate internal representations of information from how information is presented to and accepted from the user.

2. **Command Pattern:** Implements undo/redo functionality by encapsulating all information needed to perform an action or trigger an event.

3. **Event-driven Architecture:** Uses an event bus to improve component decoupling and enable plugin system extensibility.

4. **Repository Pattern:** Mediates between the domain and data mapping layers, acting like an in-memory collection of domain objects.

5. **Factory Pattern:** Used for creating form instances based on templates.

6. **Observer Pattern:** Implemented through Qt's signal-slot mechanism and custom event bus to handle events and updates across the application.

7. **Strategy Pattern:** Used for implementing different validation strategies, export formats, and rendering approaches.

8. **Singleton Pattern:** Used for services that should have only one instance, such as the database connection manager and logger.

9. **Decorator Pattern:** Used for enhancing objects with additional functionality, especially for form fields and validation.

10. **Plugin Pattern:** Allows for extending the application with new form types and functionality.

### 2.4 Directory Structure

```
ics_forms_app/
├── assets/                   # Static assets (icons, images)
├── forms/                    # Form template definitions (JSON)
│   ├── ics213.json
│   ├── ics214.json
│   └── ...
├── plugins/                  # Plugin system
│   ├── core/                 # Core plugin functionality
│   │   ├── __init__.py
│   │   ├── plugin_manager.py
│   │   └── plugin_interface.py
│   └── available/            # Available plugins
│       ├── custom_form_plugin/
│       └── report_generator/
├── src/                      # Source code
│   ├── main.py               # Application entry point
│   ├── config.py             # Configuration and constants
│   ├── ui/                   # UI components
│   │   ├── main_window.py
│   │   ├── tabbed_interface.py
│   │   ├── form_view.py
│   │   ├── form_list.py
│   │   ├── dashboard_view.py
│   │   ├── settings_dialog.py
│   │   └── widgets/          # Custom widgets
│   │       ├── repeatable_section.py
│   │       ├── form_field.py
│   │       ├── attachment_viewer.py
│   │       └── keyboard_shortcuts.py
│   ├── models/               # Domain models
│   │   ├── form.py
│   │   ├── template.py
│   │   ├── attachment.py
│   │   ├── command.py
│   │   └── event.py
│   ├── controllers/          # Application controllers
│   │   ├── form_controller.py
│   │   ├── template_controller.py
│   │   ├── settings_controller.py
│   │   └── command_processor.py
│   ├── services/             # Application services
│   │   ├── db_service.py
│   │   ├── migration_service.py
│   │   ├── backup_service.py
│   │   ├── template_service.py
│   │   ├── validation_service.py
│   │   ├── export_service.py
│   │   ├── import_service.py
│   │   ├── ics_des_service.py
│   │   ├── file_service.py
│   │   ├── event_bus.py
│   │   └── security_service.py
│   ├── repository/           # Data access layer
│   │   ├── form_repository.py
│   │   ├── version_repository.py
│   │   ├── attachment_repository.py
│   │   ├── audit_repository.py
│   │   └── incident_repository.py
│   └── utils/                # Utility functions
│       ├── logger.py
│       ├── error_handler.py
│       ├── db_utils.py
│       ├── file_utils.py
│       ├── encryption_utils.py
│       └── compression_utils.py
├── tests/                    # Test code
│   ├── unit/
│   │   ├── models/
│   │   ├── controllers/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/
│   │   ├── db_integration_tests.py
│   │   ├── ui_integration_tests.py
│   │   └── service_integration_tests.py
│   ├── ui/
│   │   ├── form_view_tests.py
│   │   ├── tabbed_interface_tests.py
│   │   └── visual_regression_tests.py
│   ├── property/             # Property-based tests
│   │   └── validation_property_tests.py
│   ├── performance/          # Performance tests
│   │   ├── benchmark_tests.py
│   │   └── large_data_tests.py
│   └── chaos/                # Chaos engineering tests
│       └── error_recovery_tests.py
└── docs/                     # Documentation
    ├── user/
    │   ├── manual.md
    │   ├── tutorials/
    │   └── troubleshooting.md
    ├── developer/
    │   ├── api.md
    │   ├── plugin_development.md
    │   └── architecture.md
    └── samples/
        └── sample_data.json
```

This comprehensive directory structure better reflects the enhanced architecture with event-driven design, plugin system, and additional services for security, backups, and migrations. The tests directory has been expanded to include property-based testing, performance testing, and chaos engineering tests.

## 3. Detailed Design: User Interface

### 3.1 UI Framework

The application will use PySide6 (Qt for Python) as the UI framework, which provides:
- Cross-platform compatibility (Windows, macOS, Linux)
- A rich set of UI components
- Layout management for responsive design
- Signal-slot mechanism for event handling
- Styling capabilities
- Accessibility features

### 3.2 Main Window

The main window will follow the updated structure outlined in the revised UI/UX Guidelines:

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create and add the sidebar
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Create and add the content area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        
        # Connect signals
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        
        # Initialize pages
        self.form_list_page = FormListPage()
        self.dashboard_page = DashboardView()
        self.settings_page = SettingsPage()
        self.help_page = HelpPage()
        
        # Add pages to stack
        self.content_stack.addWidget(self.form_list_page)
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.help_page)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Version indicator
        self.version_label = QLabel(f"Version: {config.APP_VERSION}")
        self.status_bar.addPermanentWidget(self.version_label)
        
        # Menu bar
        self.setup_menu_bar()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Register with event bus
        self.event_bus = EventBus()
        self.event_bus.register("form_modified", self.on_form_modified)
        self.event_bus.register("error_occurred", self.on_error_occurred)
    
    def setup_menu_bar(self):
        # Menu bar implementation with all actions
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_form_action = QAction("&New Form...", self)
        new_form_action.setShortcut(QKeySequence("Ctrl+N"))
        new_form_action.triggered.connect(self.on_new_form)
        file_menu.addAction(new_form_action)
        
        # Add other menus and actions
        # ...
    
    def setup_shortcuts(self):
        # Set up global keyboard shortcuts
        shortcuts = [
            (QKeySequence("Ctrl+Tab"), self.next_tab),
            (QKeySequence("Ctrl+Shift+Tab"), self.previous_tab),
            (QKeySequence("Ctrl+S"), self.save_current_form),
            (QKeySequence("Ctrl+P"), self.print_current_form),
            (QKeySequence("Ctrl+E"), self.export_current_form),
            (QKeySequence("Ctrl+Z"), self.undo),
            (QKeySequence("Ctrl+Y"), self.redo),
            (QKeySequence("F1"), self.show_help)
        ]
        
        for key_sequence, slot in shortcuts:
            shortcut = QShortcut(key_sequence, self)
            shortcut.activated.connect(slot)
```

### 3.3 Tabbed Interface

A new tabbed interface will be implemented to allow working with multiple forms simultaneously:

```python
class TabbedInterface(QWidget):
    form_saved = Signal(int)  # Emits form_id when form is saved
    form_closed = Signal(int)  # Emits form_id when tab is closed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        
        # Connect signals
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_current_tab_changed)
        
        # Add tab widget to layout
        self.layout.addWidget(self.tab_widget)
        
        # Track open forms
        self.open_forms = {}  # form_id -> tab_index
        
        # Register with event bus
        self.event_bus = EventBus()
        self.event_bus.register("form_modified", self.on_form_modified)
    
    def open_form(self, form_id, form_type=None):
        """Open a form in a new tab or switch to it if already open"""
        if form_id in self.open_forms:
            # Form already open, switch to tab
            self.tab_widget.setCurrentIndex(self.open_forms[form_id])
            return
        
        # Create form view
        form_view = FormView(form_id=form_id, form_type=form_type)
        form_view.form_saved.connect(self.on_form_saved)
        
        # Add new tab
        form_name = form_view.form_name if hasattr(form_view, 'form_name') else "New Form"
        tab_index = self.tab_widget.addTab(form_view, form_name)
        
        # Track open form
        self.open_forms[form_id] = tab_index
        
        # Switch to new tab
        self.tab_widget.setCurrentIndex(tab_index)
    
    def close_tab(self, index):
        """Close the tab at the given index"""
        # Get form view from tab
        form_view = self.tab_widget.widget(index)
        
        # Check if form has unsaved changes
        if hasattr(form_view, 'has_unsaved_changes') and form_view.has_unsaved_changes:
            # Confirm close
            confirm = QMessageBox.question(
                self,
                "Unsaved Changes",
                "This form has unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if confirm == QMessageBox.Save:
                # Save form before closing
                form_view.save_form()
            elif confirm == QMessageBox.Cancel:
                # Cancel close
                return
        
        # Get form_id
        form_id = None
        for fid, tab_idx in self.open_forms.items():
            if tab_idx == index:
                form_id = fid
                break
        
        # Remove tab
        self.tab_widget.removeTab(index)
        
        # Update open forms tracking
        if form_id is not None:
            del self.open_forms[form_id]
            
            # Update remaining tab indices
            for fid, tab_idx in self.open_forms.items():
                if tab_idx > index:
                    self.open_forms[fid] = tab_idx - 1
            
            # Emit signal
            self.form_closed.emit(form_id)
    
    def on_form_saved(self, form_id):
        """Handle form saved event"""
        # Update tab title to remove modification indicator
        tab_index = self.open_forms.get(form_id)
        if tab_index is not None:
            form_view = self.tab_widget.widget(tab_index)
            form_name = form_view.form_name if hasattr(form_view, 'form_name') else "Form"
            self.tab_widget.setTabText(tab_index, form_name)
        
        # Emit signal
        self.form_saved.emit(form_id)
    
    def on_form_modified(self, form_id):
        """Handle form modified event"""
        # Update tab title to indicate modification
        tab_index = self.open_forms.get(form_id)
        if tab_index is not None:
            form_view = self.tab_widget.widget(tab_index)
            form_name = form_view.form_name if hasattr(form_view, 'form_name') else "Form"
            
            # Add asterisk to indicate unsaved changes
            if not self.tab_widget.tabText(tab_index).endswith('*'):
                self.tab_widget.setTabText(tab_index, f"{form_name} *")
```

### 3.4 Dashboard View

A new dashboard view will be implemented to show form completion status across an incident:

```python
class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        
        # Header
        self.header = QLabel("Incident Dashboard")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header)
        
        # Incident selector
        self.incident_selector = QComboBox()
        self.update_incident_list()
        self.layout.addWidget(self.incident_selector)
        
        # Dashboard content
        self.dashboard_content = QScrollArea()
        self.dashboard_content.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.dashboard_content.setWidget(self.content_widget)
        self.layout.addWidget(self.dashboard_content)
        
        # Connect signals
        self.incident_selector.currentIndexChanged.connect(self.on_incident_changed)
        
        # Register with event bus
        self.event_bus = EventBus()
        self.event_bus.register("form_saved", self.on_form_saved)
        self.event_bus.register("form_created", self.on_form_created)
        self.event_bus.register("form_deleted", self.on_form_deleted)
        
        # Initialize dashboard
        self.update_dashboard()
    
    def update_incident_list(self):
        """Update the incident selector with available incidents"""
        self.incident_selector.clear()
        
        # Get incident repository
        incident_repository = IncidentRepository()
        
        # Get all incidents
        incidents = incident_repository.get_incidents()
        
        # Add incidents to selector
        for incident in incidents:
            self.incident_selector.addItem(incident["incident_name"], incident["incident_id"])
    
    def on_incident_changed(self, index):
        """Handle incident selection change"""
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update the dashboard content for the selected incident"""
        # Clear current content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get selected incident
        incident_id = self.incident_selector.currentData()
        if incident_id is None:
            return
        
        # Get form repository
        form_repository = FormRepository()
        
        # Get forms for incident
        forms = form_repository.get_forms_by_incident(incident_id)
        
        # Create completion summary
        self.create_completion_summary(forms)
        
        # Create form type sections
        form_types = {}
        for form in forms:
            form_type = form["form_type"]
            if form_type not in form_types:
                form_types[form_type] = []
            form_types[form_type].append(form)
        
        for form_type, type_forms in form_types.items():
            self.create_form_type_section(form_type, type_forms)
    
    def create_completion_summary(self, forms):
        """Create a summary of form completion status"""
        # Create summary panel
        summary_panel = QGroupBox("Completion Summary")
        summary_layout = QVBoxLayout(summary_panel)
        
        # Count forms by status
        total_forms = len(forms)
        status_counts = {}
        for form in forms:
            status = form["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Create completion progress bar
        completed = status_counts.get("Completed", 0) + status_counts.get("Submitted", 0)
        completion_rate = completed / total_forms if total_forms > 0 else 0
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(completion_rate * 100))
        progress_bar.setFormat(f"Overall Completion: {int(completion_rate * 100)}%")
        summary_layout.addWidget(progress_bar)
        
        # Create status breakdown
        status_table = QTableWidget()
        status_table.setRowCount(len(status_counts))
        status_table.setColumnCount(2)
        status_table.setHorizontalHeaderLabels(["Status", "Count"])
        status_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        status_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        status_table.verticalHeader().setVisible(False)
        
        for i, (status, count) in enumerate(status_counts.items()):
            status_table.setItem(i, 0, QTableWidgetItem(status))
            status_table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        summary_layout.addWidget(status_table)
        
        # Add to dashboard
        self.content_layout.addWidget(summary_panel)
    
    def create_form_type_section(self, form_type, forms):
        """Create a section for a specific form type"""
        # Create section panel
        section_panel = QGroupBox(form_type)
        section_layout = QVBoxLayout(section_panel)
        
        # Create form list
        form_table = QTableWidget()
        form_table.setRowCount(len(forms))
        form_table.setColumnCount(4)
        form_table.setHorizontalHeaderLabels(["Form Name", "Status", "Updated", "Actions"])
        form_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        form_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        form_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        form_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        form_table.verticalHeader().setVisible(False)
        
        for i, form in enumerate(forms):
            form_table.setItem(i, 0, QTableWidgetItem(form["form_name"]))
            form_table.setItem(i, 1, QTableWidgetItem(form["status"]))
            form_table.setItem(i, 2, QTableWidgetItem(form["updated_at"]))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.setProperty("form_id", form["form_id"])
            edit_button.clicked.connect(self.on_edit_form)
            
            export_button = QPushButton("Export")
            export_button.setProperty("form_id", form["form_id"])
            export_button.clicked.connect(self.on_export_form)
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(export_button)
            
            form_table.setCellWidget(i, 3, actions_widget)
        
        section_layout.addWidget(form_table)
        
        # Add to dashboard
        self.content_layout.addWidget(section_panel)
```

### 3.5 Form View

The form view will be enhanced to include visual indication of attachments and support for undo/redo:

```python
class FormView(QWidget):
    form_saved = Signal(int)  # Emits form_id when form is saved
    
    def __init__(self, form_id=None, form_type=None):
        super().__init__()
        
        self.form_id = form_id
        self.form_type = form_type
        self.form_controller = FormController()
        self.command_processor = CommandProcessor()
        self.has_unsaved_changes = False
        
        self.layout = QVBoxLayout(self)
        
        # Top bar with actions
        self.top_bar = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setIcon(QIcon.fromTheme("document-save"))
        self.btn_save.setToolTip("Save the current form (Ctrl+S)")
        
        self.btn_export = QPushButton("Export")
        self.btn_export.setIcon(QIcon.fromTheme("document-export"))
        self.btn_export.setToolTip("Export the form in various formats")
        
        self.btn_print = QPushButton("Print")
        self.btn_print.setIcon(QIcon.fromTheme("document-print"))
        self.btn_print.setToolTip("Print the form (Ctrl+P)")
        
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.setIcon(QIcon.fromTheme("edit-undo"))
        self.btn_undo.setToolTip("Undo the last action (Ctrl+Z)")
        self.btn_undo.setEnabled(False)
        
        self.btn_redo = QPushButton("Redo")
        self.btn_redo.setIcon(QIcon.fromTheme("edit-redo"))
        self.btn_redo.setToolTip("Redo the last undone action (Ctrl+Y)")
        self.btn_redo.setEnabled(False)
        
        self.top_bar_layout.addWidget(self.btn_save)
        self.top_bar_layout.addWidget(self.btn_export)
        self.top_bar_layout.addWidget(self.btn_print)
        self.top_bar_layout.addWidget(self.btn_undo)
        self.top_bar_layout.addWidget(self.btn_redo)
        self.top_bar_layout.addStretch(1)  # Add spacer
        
        self.layout.addWidget(self.top_bar)
        
        # Form content (scroll area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.form_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll_area)
        
        # Attachment section
        self.attachment_section = QGroupBox("Attachments")
        self.attachment_layout = QVBoxLayout(self.attachment_section)
        
        self.attachment_list = QListWidget()
        self.btn_add_attachment = QPushButton("Add Attachment")
        self.btn_add_attachment.setIcon(QIcon.fromTheme("list-add"))
        
        self.attachment_layout.addWidget(self.attachment_list)
        self.attachment_layout.addWidget(self.btn_add_attachment)
        
        self.layout.addWidget(self.attachment_section)
        
        # Connect signals
        self.btn_save.clicked.connect(self.save_form)
        self.btn_export.clicked.connect(self.show_export_dialog)
        self.btn_print.clicked.connect(self.print_form)
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo.clicked.connect(self.redo)
        self.btn_add_attachment.clicked.connect(self.add_attachment)
        
        # Initialize form
        if form_id:
            self.load_form(form_id)
        elif form_type:
            self.create_new_form(form_type)
        
        # Register with event bus
        self.event_bus = EventBus()
        self.event_bus.register("command_stack_changed", self.update_undo_redo_state)
    
    def load_form(self, form_id):
        """Load an existing form"""
        try:
            form_data = self.form_controller.get_form(form_id)
            self.form_name = form_data.get("form_name", "Unnamed Form")
            self.form_type = form_data.get("form_type")
            self.form_data = form_data.get("data", {})
            
            # Create form fields based on template
            self.create_form_ui(self.form_type, self.form_data)
            
            # Load attachments
            self.load_attachments(form_id)
            
            # Reset command stack
            self.command_processor.clear()
            self.update_undo_redo_state()
            
            # Reset unsaved changes flag
            self.has_unsaved_changes = False
            
        except Exception as e:
            error_handler = ErrorHandler(self)
            error_handler.handle_error(str(e), "ERROR", "Failed to Load Form")
    
    def create_new_form(self, form_type):
        """Create a new form based on template"""
        try:
            # Get template
            template_controller = TemplateController()
            template = template_controller.get_template(form_type)
            
            if not template:
                raise ValueError(f"Template not found for form type: {form_type}")
            
            # Set form properties
            self.form_name = template.get("meta", {}).get("display_name", form_type)
            
            # Pre-populate with default values
            form_data = template_controller.get_default_values(form_type)
            self.form_data = form_data
            
            # Create form fields based on template
            self.create_form_ui(form_type, form_data)
            
            # Reset command stack
            self.command_processor.clear()
            self.update_undo_redo_state()
            
            # Reset unsaved changes flag
            self.has_unsaved_changes = False
            
        except Exception as e:
            error_handler = ErrorHandler(self)
            error_handler.handle_error(str(e), "ERROR", "Failed to Create Form")
    
    def create_form_ui(self, form_type, form_data):
        """Create the UI for a form based on its template"""
        # Clear existing content
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create form UI using template controller
        template_controller = TemplateController()
        form_widget = template_controller.create_form_ui(form_type, self.scroll_content, form_data)
        
        # Add form widget to layout
        self.form_layout.addWidget(form_widget)
        
        # Connect field change signals
        self.connect_field_signals(form_widget)
    
    def connect_field_signals(self, form_widget):
        """Connect signals from form fields to track changes"""
        # Find all form field widgets
        for field_widget in form_widget.findChildren(QWidget):
            if hasattr(field_widget, "value_changed"):
                field_widget.value_changed.connect(self.on_field_changed)
    
    def on_field_changed(self, field_id, value):
        """Handle field value change"""
        # Create change command
        old_value = self.form_data.get(field_id)
        command = ChangeFieldCommand(field_id, old_value, value, self.form_data)
        
        # Execute command
        self.command_processor.execute_command(command)
        
        # Mark form as having unsaved changes
        self.has_unsaved_changes = True
        
        # Notify others of modification
        if self.form_id:
            self.event_bus.emit("form_modified", self.form_id)
    
    def save_form(self):
        """Save the form"""
        try:
            if self.form_id:
                # Update existing form
                self.form_id = self.form_controller.update_form(
                    self.form_id, self.form_data)
            else:
                # Create new form
                self.form_id = self.form_controller.create_form(
                    self.form_type, self.form_name, self.form_data)
            
            # Reset unsaved changes flag
            self.has_unsaved_changes = False
            
            # Emit signal
            self.form_saved.emit(self.form_id)
            
            # Show success message
            status_message = f"Form '{self.form_name}' saved successfully"
            if self.window() and hasattr(self.window(), 'statusBar'):
                self.window().statusBar().showMessage(status_message, 3000)
            
        except Exception as e:
            error_handler = ErrorHandler(self)
            error_handler.handle_error(str(e), "ERROR", "Failed to Save Form")
    
    def load_attachments(self, form_id):
        """Load attachments for the form"""
        # Clear current list
        self.attachment_list.clear()
        
        # Get attachments
        attachment_repository = AttachmentRepository()
        attachments = attachment_repository.get_attachments_for_form(form_id)
        
        # Add to list
        for attachment in attachments:
            item = QListWidgetItem()
            item.setText(attachment.get("file_name", "Unknown"))
            item.setData(Qt.UserRole, attachment)
            
            # Set icon based on file type
            file_type = attachment.get("file_type", "")
            if "image" in file_type:
                item.setIcon(QIcon.fromTheme("image-x-generic"))
            elif "pdf" in file_type:
                item.setIcon(QIcon.fromTheme("application-pdf"))
            elif "text" in file_type:
                item.setIcon(QIcon.fromTheme("text-x-generic"))
            elif "word" in file_type or "office" in file_type:
                item.setIcon(QIcon.fromTheme("x-office-document"))
            elif "excel" in file_type or "spreadsheet" in file_type:
                item.setIcon(QIcon.fromTheme("x-office-spreadsheet"))
            else:
                item.setIcon(QIcon.fromTheme("emblem-documents"))
            
            self.attachment_list.addItem(item)
    
    def add_attachment(self):
        """Add a new attachment to the form"""
        if not self.form_id:
            # Form must be saved first
            QMessageBox.warning(
                self,
                "Save Required",
                "You must save the form before adding attachments."
            )
            return
        
        # File dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Attachment",
            "",
            "All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Add attachment
            file_service = FileService()
            attachment_repository = AttachmentRepository()
            
            # Copy file to attachment directory
            stored_path = file_service.store_attachment(file_path)
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_type = file_service.get_mime_type(file_path)
            md5_hash = file_service.calculate_md5(file_path)
            
            # Add to database
            attachment_id = attachment_repository.add_attachment(
                self.form_id,
                "attachment",  # Generic section
                stored_path,
                file_name,
                file_type,
                file_size,
                md5_hash,
                "Added via form editor"
            )
            
            # Reload attachments
            self.load_attachments(self.form_id)
            
        except Exception as e:
            error_handler = ErrorHandler(self)
            error_handler.handle_error(str(e), "ERROR", "Failed to Add Attachment")
    
    def undo(self):
        """Undo the last command"""
        if self.command_processor.can_undo():
            self.command_processor.undo()
            self.has_unsaved_changes = True
            
            # Notify others of modification
            if self.form_id:
                self.event_bus.emit("form_modified", self.form_id)
    
    def redo(self):
        """Redo the last undone command"""
        if self.command_processor.can_redo():
            self.command_processor.redo()
            self.has_unsaved_changes = True
            
            # Notify others of modification
            if self.form_id:
                self.event_bus.emit("form_modified", self.form_id)
    
    def update_undo_redo_state(self):
        """Update the enabled state of undo/redo buttons"""
        self.btn_undo.setEnabled(self.command_processor.can_undo())
        self.btn_redo.setEnabled(self.command_processor.can_redo())
```

## 4. Detailed Design: Event-Driven Architecture

### 4.1 Event Bus

The event bus will enable decoupled communication between components and support the plugin system:

```python
class EventBus:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.handlers = {}
        self.logger = Logger().get_logger()
    
    def register(self, event_type, handler):
        """Register a handler for an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        if handler not in self.handlers[event_type]:
            self.handlers[event_type].append(handler)
            self.logger.debug(f"Registered handler for event: {event_type}")
    
    def unregister(self, event_type, handler):
        """Unregister a handler for an event type"""
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            self.logger.debug(f"Unregistered handler for event: {event_type}")
    
    def emit(self, event_type, *args, **kwargs):
        """Emit an event to all registered handlers"""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {str(e)}")
            
            self.logger.debug(f"Emitted event: {event_type}")
        else:
            self.logger.debug(f"No handlers for event: {event_type}")
```

### 4.2 Command Pattern for Undo/Redo

The command pattern will be implemented to provide undo/redo functionality:

```python
class Command:
    """Base class for all commands"""
    def execute(self):
        """Execute the command"""
        pass
    
    def undo(self):
        """Undo the command"""
        pass

class ChangeFieldCommand(Command):
    """Command for changing a form field value"""
    def __init__(self, field_id, old_value, new_value, form_data):
        self.field_id = field_id
        self.old_value = old_value
        self.new_value = new_value
        self.form_data = form_data
    
    def execute(self):
        """Execute the command"""
        self.form_data[self.field_id] = self.new_value
    
    def undo(self):
        """Undo the command"""
        self.form_data[self.field_id] = self.old_value

class AddItemCommand(Command):
    """Command for adding an item to a repeatable section"""
    def __init__(self, section_id, item, items_list):
        self.section_id = section_id
        self.item = item
        self.items_list = items_list
        self.index = None
    
    def execute(self):
        """Execute the command"""
        self.items_list.append(self.item)
        self.index = len(self.items_list) - 1
    
    def undo(self):
        """Undo the command"""
        if self.index is not None:
            self.items_list.pop(self.index)
            self.index = None

class RemoveItemCommand(Command):
    """Command for removing an item from a repeatable section"""
    def __init__(self, section_id, index, items_list):
        self.section_id = section_id
        self.index = index
        self.items_list = items_list
        self.item = None
    
    def execute(self):
        """Execute the command"""
        if 0 <= self.index < len(self.items_list):
            self.item = self.items_list[self.index]
            self.items_list.pop(self.index)
    
    def undo(self):
        """Undo the command"""
        if self.item is not None:
            self.items_list.insert(self.index, self.item)

class CommandProcessor:
    """Manages commands for undo/redo functionality"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandProcessor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.undo_stack = []
        self.redo_stack = []
        self.event_bus = EventBus()
    
    def execute_command(self, command):
        """Execute a command and add it to the undo stack"""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.event_bus.emit("command_stack_changed")
    
    def undo(self):
        """Undo the last command"""
        if self.can_undo():
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            self.event_bus.emit("command_stack_changed")
    
    def redo(self):
        """Redo the last undone command"""
        if self.can_redo():
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
            self.event_bus.emit("command_stack_changed")
    
    def can_undo(self):
        """Check if there are commands to undo"""
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        """Check if there are commands to redo"""
        return len(self.redo_stack) > 0
    
    def clear(self):
        """Clear command stacks"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.event_bus.emit("command_stack_changed")
```

## 5. Detailed Design: Plugin System

### 5.1 Plugin Manager

The plugin manager will handle discovery, loading, and management of plugins:

```python
class PluginManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.plugins = {}
        self.event_bus = EventBus()
        self.logger = Logger().get_logger()
    
    def discover_plugins(self):
        """Discover available plugins"""
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins", "available")
        
        if not os.path.exists(plugins_dir):
            self.logger.warning(f"Plugins directory not found: {plugins_dir}")
            return
        
        # Iterate through directories in plugins directory
        for plugin_dir in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_dir)
            
            if not os.path.isdir(plugin_path):
                continue
            
            # Check for plugin.json
            plugin_json_path = os.path.join(plugin_path, "plugin.json")
            if not os.path.exists(plugin_json_path):
                continue
            
            try:
                # Load plugin metadata
                with open(plugin_json_path, 'r') as f:
                    plugin_metadata = json.load(f)
                
                plugin_id = plugin_metadata.get("id")
                if not plugin_id:
                    continue
                
                self.plugins[plugin_id] = {
                    "id": plugin_id,
                    "name": plugin_metadata.get("name", plugin_id),
                    "description": plugin_metadata.get("description", ""),
                    "version": plugin_metadata.get("version", "1.0"),
                    "author": plugin_metadata.get("author", "Unknown"),
                    "path": plugin_path,
                    "instance": None,
                    "enabled": False
                }
                
                self.logger.info(f"Discovered plugin: {plugin_id} ({plugin_metadata.get('name', plugin_id)})")
                
            except Exception as e:
                self.logger.error(f"Error loading plugin metadata from {plugin_json_path}: {str(e)}")
    
    def load_plugin(self, plugin_id):
        """Load a specific plugin"""
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin_info = self.plugins[plugin_id]
        
        if plugin_info["instance"] is not None:
            # Already loaded
            return True
        
        try:
            # Import plugin module
            plugin_path = plugin_info["path"]
            module_name = os.path.basename(plugin_path)
            spec = importlib.util.spec_from_file_location(
                module_name,
                os.path.join(plugin_path, "__init__.py")
            )
            
            if not spec:
                self.logger.error(f"Failed to load plugin module: {plugin_id}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if not hasattr(module, "Plugin"):
                self.logger.error(f"Plugin module does not define Plugin class: {plugin_id}")
                return False
            
            # Create plugin instance
            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class()
            
            # Store plugin instance
            plugin_info["instance"] = plugin_instance
            
            self.logger.info(f"Loaded plugin: {plugin_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_id}: {str(e)}")
            return False
    
    def enable_plugin(self, plugin_id):
        """Enable a plugin"""
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin_info = self.plugins[plugin_id]
        
        if plugin_info["enabled"]:
            # Already enabled
            return True
        
        # Load plugin if not already loaded
        if plugin_info["instance"] is None:
            if not self.load_plugin(plugin_id):
                return False
        
        try:
            # Initialize plugin
            plugin_instance = plugin_info["instance"]
            plugin_instance.initialize()
            
            # Mark as enabled
            plugin_info["enabled"] = True
            
            self.logger.info(f"Enabled plugin: {plugin_id}")
            
            # Notify others
            self.event_bus.emit("plugin_enabled", plugin_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_id}: {str(e)}")
            return False
    
    def disable_plugin(self, plugin_id):
        """Disable a plugin"""
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin_info = self.plugins[plugin_id]
        
        if not plugin_info["enabled"]:
            # Already disabled
            return True
        
        try:
            # Shut down plugin
            plugin_instance = plugin_info["instance"]
            plugin_instance.shutdown()
            
            # Mark as disabled
            plugin_info["enabled"] = False
            
            self.logger.info(f"Disabled plugin: {plugin_id}")
            
            # Notify others
            self.event_bus.emit("plugin_disabled", plugin_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_id}: {str(e)}")
            return False
    
    def get_plugin_instance(self, plugin_id):
        """Get a plugin instance"""
        if plugin_id not in self.plugins:
            return None
        
        plugin_info = self.plugins[plugin_id]
        
        if not plugin_info["enabled"]:
            return None
        
        return plugin_info["instance"]
    
    def get_all_plugins(self):
        """Get information about all plugins"""
        return self.plugins
```

### 5.2 Plugin Interface

The plugin interface will define the contract that all plugins must follow:

```python
class PluginInterface:
    """Base class for all plugins"""
    def initialize(self):
        """Initialize the plugin"""
        pass
    
    def shutdown(self):
        """Shut down the plugin"""
        pass
    
    def get_info(self):
        """Get plugin information"""
        return {
            "id": "unknown",
            "name": "Unknown Plugin",
            "description": "A plugin that does something",
            "version": "1.0",
            "author": "Unknown"
        }
```

## 6. Detailed Design: Database Implementation

### 6.1 Database Service

The Database Service will be enhanced with migration support, backup strategy, and integrity checks:

```python
class DatabaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.connection = None
        self.db_path = None
        self.logger = Logger().get_logger()
        self.event_bus = EventBus()
    
    def initialize(self, db_path=None):
        """Initialize the database connection"""
        if not db_path:
            # Use default path if none provided
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(app_dir, "incident.db")
        
        self.db_path = db_path
        
        # Check if the database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Close any existing connection
        if self.connection:
            self.connection.close()
        
        # Create a new connection
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Enable WAL mode for better performance and reliability
        self.connection.execute("PRAGMA journal_mode = WAL")
        
        # Set synchronous mode for better reliability
        self.connection.execute("PRAGMA synchronous = NORMAL")
        
        # Set temp store to memory for better performance
        self.connection.execute("PRAGMA temp_store = MEMORY")
        
        # Set page size for optimal performance
        self.connection.execute("PRAGMA page_size = 4096")
        
        # Set cache size
        self.connection.execute("PRAGMA cache_size = -2000")  # 2MB cache
        
        # Check if the database exists and create it if not
        self._create_schema_if_needed()
        
        # Run migrations
        self._run_migrations()
        
        # Notify others
        self.event_bus.emit("database_initialized")
    
    def _create_schema_if_needed(self):
        """Create the database schema if it doesn't exist"""
        cursor = self.connection.cursor()
        
        # Check if migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        if cursor.fetchone() is None:
            # Create schema based on revised DB design document
            self._create_schema()
    
    def _create_schema(self):
        """Create the database schema"""
        cursor = self.connection.cursor()
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Create migrations table
            cursor.execute('''
            CREATE TABLE migrations (
                migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at DATETIME NOT NULL,
                description TEXT,
                checksum TEXT
            )
            ''')
            
            # Create incidents table
            cursor.execute('''
            CREATE TABLE incidents (
                incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_name TEXT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME,
                description TEXT,
                status TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
            ''')
            
            # Create master forms table
            cursor.execute('''
            CREATE TABLE forms (
                form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_type TEXT NOT NULL,
                form_name TEXT NOT NULL,
                current_version TEXT NOT NULL,
                status TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                is_template BOOLEAN DEFAULT FALSE,
                incident_id INTEGER,
                FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
            )
            ''')
            
            # Create form versions table
            cursor.execute('''
            CREATE TABLE form_versions (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                data TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                notes TEXT,
                FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
            )
            ''')
            
            # Create attachments table
            cursor.execute('''
            CREATE TABLE attachments (
                attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id INTEGER NOT NULL,
                section TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                md5_hash TEXT,
                description TEXT,
                created_by TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
            )
            ''')
            
            # Create audit logs table
            cursor.execute('''
            CREATE TABLE audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                user TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                details TEXT
            )
            ''')
            
            # Create specific form tables (for the MVP: ICS-213 and ICS-214)
            self._create_ics213_schema(cursor)
            self._create_ics214_schema(cursor)
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX idx_forms_type ON forms(form_type)')
            cursor.execute('CREATE INDEX idx_forms_status ON forms(status)')
            cursor.execute('CREATE INDEX idx_forms_created_at ON forms(created_at)')
            cursor.execute('CREATE INDEX idx_forms_updated_at ON forms(updated_at)')
            cursor.execute('CREATE INDEX idx_forms_created_by ON forms(created_by)')
            cursor.execute('CREATE INDEX idx_forms_incident_id ON forms(incident_id)')
            
            cursor.execute('CREATE INDEX idx_form_versions_form_id ON form_versions(form_id)')
            cursor.execute('CREATE INDEX idx_form_versions_created_at ON form_versions(created_at)')
            
            cursor.execute('CREATE INDEX idx_incidents_name ON incidents(incident_name)')
            cursor.execute('CREATE INDEX idx_incidents_status ON incidents(status)')
            cursor.execute('CREATE INDEX idx_incidents_dates ON incidents(start_date, end_date)')
            
            cursor.execute('CREATE INDEX idx_attachments_form_id ON attachments(form_id)')
            cursor.execute('CREATE INDEX idx_attachments_file_type ON attachments(file_type)')
            
            cursor.execute('CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id)')
            cursor.execute('CREATE INDEX idx_audit_logs_action ON audit_logs(action)')
            cursor.execute('CREATE INDEX idx_audit_logs_user ON audit_logs(user)')
            cursor.execute('CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp)')
            
            cursor.execute('CREATE INDEX idx_migrations_version ON migrations(version)')
            
            # Commit transaction
            cursor.execute("COMMIT")
            
            self.logger.info("Created database schema")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.logger.error(f"Error creating database schema: {str(e)}")
            raise e
    
    def _create_ics213_schema(self, cursor):
        """Create ICS-213 specific tables"""
        cursor.execute('''
        CREATE TABLE ics213 (
            ics213_id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            incident_name TEXT,
            to_name TEXT NOT NULL,
            to_position TEXT,
            from_name TEXT NOT NULL,
            from_position TEXT,
            subject TEXT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            message TEXT NOT NULL,
            approved_by TEXT,
            reply TEXT,
            replied_by TEXT,
            replied_date_time DATETIME,
            FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
        )
        ''')
    
    def _create_ics214_schema(self, cursor):
        """Create ICS-214 specific tables and child tables"""
        cursor.execute('''
        CREATE TABLE ics214 (
            ics214_id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            incident_name TEXT NOT NULL,
            operational_period_start DATETIME NOT NULL,
            operational_period_end DATETIME NOT NULL,
            name TEXT NOT NULL,
            ics_position TEXT NOT NULL,
            home_agency TEXT NOT NULL,
            prepared_by_name TEXT NOT NULL,
            prepared_by_position TEXT NOT NULL,
            prepared_by_signature TEXT,
            prepared_datetime DATETIME NOT NULL,
            page_number INTEGER,
            FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE ics214_activity_log_items (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ics214_id INTEGER NOT NULL,
            activity_datetime DATETIME NOT NULL,
            notable_activities TEXT NOT NULL,
            FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE ics214_resources_assigned (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ics214_id INTEGER NOT NULL,
            resource_name TEXT NOT NULL,
            resource_position TEXT,
            resource_home_agency TEXT,
            FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for child tables
        cursor.execute('CREATE INDEX idx_ics214_activity_log_ics214_id ON ics214_activity_log_items(ics214_id)')
        cursor.execute('CREATE INDEX idx_ics214_activity_datetime ON ics214_activity_log_items(activity_datetime)')
        cursor.execute('CREATE INDEX idx_ics214_resources_ics214_id ON ics214_resources_assigned(ics214_id)')
```

## 6. Detailed Design: Database Implementation (continued)

### 6.1 Database Service (continued)

```python
def _run_migrations(self):
    """Run any pending database migrations"""
    migration_service = MigrationService()
    migration_service.run_migrations(self.connection)

def execute_query(self, query, parameters=()):
    """Execute a query and return the cursor"""
    cursor = self.connection.cursor()
    cursor.execute(query, parameters)
    return cursor

def execute_transaction(self, queries):
    """Execute multiple queries in a transaction"""
    cursor = self.connection.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        for query, parameters in queries:
            cursor.execute(query, parameters)
        cursor.execute("COMMIT")
        return True
    except Exception as e:
        cursor.execute("ROLLBACK")
        self.logger.error(f"Transaction failed: {str(e)}")
        raise e
    
def backup_database(self, backup_path=None):
    """Create a backup of the database"""
    backup_service = BackupService()
    return backup_service.create_backup(self.connection, self.db_path, backup_path)

def check_integrity(self):
    """Check the integrity of the database"""
    cursor = self.connection.cursor()
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    return result[0] == "ok"

def vacuum(self):
    """Vacuum the database to reclaim space and optimize performance"""
    self.connection.execute("VACUUM")
    self.logger.info("Database vacuumed")

def close(self):
    """Close the database connection"""
    if self.connection:
        self.connection.close()
        self.connection = None
        self.logger.info("Database connection closed")

def compress_database(self, output_path=None):
    """Compress the database file"""
    if not output_path:
        # Generate output path
        db_dir = os.path.dirname(self.db_path)
        db_name = os.path.basename(self.db_path)
        base_name, ext = os.path.splitext(db_name)
        output_path = os.path.join(db_dir, f"{base_name}_compressed{ext}")
    
    # Create a backup
    self.backup_database(output_path)
    
    # Compress the backup
    with open(output_path, 'rb') as f_in:
        compressed_path = f"{output_path}.gz"
        with gzip.open(compressed_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove uncompressed backup
    os.remove(output_path)
    
    self.logger.info(f"Database compressed to {compressed_path}")
    
    return compressed_path
```

### 6.2 Migration Service

The Migration Service will handle database schema migrations:

```python
class MigrationService:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.migrations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "migrations"
        )
    
    def run_migrations(self, connection):
        """Run any pending migrations"""
        # Create migrations directory if it doesn't exist
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
        
        # Get current migration version
        current_version = self._get_current_version(connection)
        self.logger.info(f"Current database version: {current_version}")
        
        # Get available migrations
        available_migrations = self._get_available_migrations()
        
        # Filter migrations that need to be applied
        pending_migrations = [
            m for m in available_migrations
            if self._compare_versions(m["version"], current_version) > 0
        ]
        
        if not pending_migrations:
            self.logger.info("No pending migrations")
            return
        
        # Sort migrations by version
        pending_migrations.sort(key=lambda m: m["version"])
        
        # Apply migrations
        for migration in pending_migrations:
            self._apply_migration(connection, migration)
    
    def _get_current_version(self, connection):
        """Get the current migration version from the database"""
        cursor = connection.cursor()
        
        # Check if migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        if not cursor.fetchone():
            return "0.0.0"
        
        # Get latest migration version
        cursor.execute("SELECT version FROM migrations ORDER BY migration_id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            return "0.0.0"
        
        return row[0]
    
    def _get_available_migrations(self):
        """Get available migration files"""
        if not os.path.exists(self.migrations_dir):
            return []
        
        migrations = []
        
        # Find migration SQL files
        for filename in os.listdir(self.migrations_dir):
            if not filename.endswith(".sql"):
                continue
            
            # Extract version from filename (e.g., "V1.0.1__description.sql")
            match = re.match(r"^V([0-9\.]+)__(.+)\.sql$", filename)
            if not match:
                continue
            
            version = match.group(1)
            description = match.group(2).replace("_", " ")
            
            migrations.append({
                "version": version,
                "description": description,
                "filename": filename,
                "path": os.path.join(self.migrations_dir, filename)
            })
        
        return migrations
    
    def _compare_versions(self, version1, version2):
        """Compare two version strings"""
        v1_parts = [int(x) for x in version1.split(".")]
        v2_parts = [int(x) for x in version2.split(".")]
        
        # Pad with zeros to ensure same length
        max_length = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_length - len(v1_parts)))
        v2_parts.extend([0] * (max_length - len(v2_parts)))
        
        for i in range(max_length):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        
        return 0
    
    def _apply_migration(self, connection, migration):
        """Apply a migration to the database"""
        self.logger.info(f"Applying migration: {migration['version']} - {migration['description']}")
        
        # Open and read migration file
        with open(migration["path"], "r") as f:
            sql_content = f.read()
        
        # Calculate checksum
        checksum = hashlib.md5(sql_content.encode()).hexdigest()
        
        # Split SQL statements
        statements = self._split_sql_statements(sql_content)
        
        cursor = connection.cursor()
        
        try:
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Execute each statement
            for statement in statements:
                if statement.strip():  # Skip empty statements
                    cursor.execute(statement)
            
            # Record migration
            cursor.execute(
                "INSERT INTO migrations (version, applied_at, description, checksum) VALUES (?, ?, ?, ?)",
                (migration["version"], datetime.now().isoformat(), migration["description"], checksum)
            )
            
            # Commit transaction
            cursor.execute("COMMIT")
            
            self.logger.info(f"Migration applied successfully: {migration['version']}")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.logger.error(f"Migration failed: {str(e)}")
            raise RuntimeError(f"Migration {migration['version']} failed: {str(e)}")
    
    def _split_sql_statements(self, sql_content):
        """Split SQL content into individual statements"""
        # Simple splitting by semicolon
        # This could be improved to handle more complex SQL
        return [s.strip() for s in sql_content.split(";")]
    
    def create_migration_file(self, version, description):
        """Create a new migration file"""
        # Format filename
        formatted_description = description.replace(" ", "_").lower()
        filename = f"V{version}__{formatted_description}.sql"
        file_path = os.path.join(self.migrations_dir, filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise ValueError(f"Migration file already exists: {filename}")
        
        # Create migrations directory if it doesn't exist
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
        
        # Create empty migration file with header comment
        with open(file_path, "w") as f:
            f.write(f"-- Migration: {description}\n")
            f.write(f"-- Version: {version}\n")
            f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
        
        return file_path
```

### 6.3 Backup Service

The Backup Service will handle database backups with rotation policy:

```python
class BackupService:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.backup_dir = None
    
    def set_backup_directory(self, directory):
        """Set the backup directory"""
        self.backup_dir = directory
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_backup_directory(self, db_path=None):
        """Get the backup directory"""
        if self.backup_dir:
            return self.backup_dir
        
        if db_path:
            # Use directory of database file
            return os.path.dirname(db_path)
        
        # Use default backup directory
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = os.path.join(app_dir, "backups")
        
        # Create directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        return backup_dir
    
    def create_backup(self, connection, db_path, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            # Generate backup path based on current date/time
            backup_dir = self.get_backup_directory(db_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = os.path.basename(db_path)
            base_name, ext = os.path.splitext(db_name)
            backup_path = os.path.join(backup_dir, f"{base_name}_backup_{timestamp}{ext}")
        
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        connection.backup(backup_conn)
        backup_conn.close()
        
        self.logger.info(f"Database backup created: {backup_path}")
        
        # Apply rotation policy
        self._apply_rotation_policy(db_path)
        
        return backup_path
    
    def _apply_rotation_policy(self, db_path):
        """Apply backup rotation policy"""
        backup_dir = self.get_backup_directory(db_path)
        db_name = os.path.basename(db_path)
        base_name, ext = os.path.splitext(db_name)
        
        # Find all backups for this database
        backup_pattern = os.path.join(backup_dir, f"{base_name}_backup_*{ext}")
        backups = glob.glob(backup_pattern)
        
        if not backups:
            return
        
        # Sort backups by creation time (most recent first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Keep up to 10 daily backups
        daily_backups = self._group_backups_by_day(backups)
        days = sorted(daily_backups.keys(), reverse=True)
        
        for day in days[10:]:  # Keep first 10 days
            for backup in daily_backups[day][1:]:  # Keep only the most recent backup per day
                self._delete_backup(backup)
        
        # Keep up to 4 weekly backups (from the oldest 4 weeks of daily backups)
        if len(days) >= 10:
            weekly_backups = []
            
            for day in days[:10]:  # Use first 10 days
                # Get most recent backup for the day
                backup = daily_backups[day][0]
                
                # Extract date from backup filename
                match = re.search(r"(\d{8})_", os.path.basename(backup))
                if match:
                    date_str = match.group(1)
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    week = date_obj.strftime("%Y%W")  # Year and week number
                    
                    weekly_backups.append((week, backup))
            
            # Group by week
            weeks = {}
            for week, backup in weekly_backups:
                if week not in weeks:
                    weeks[week] = []
                weeks[week].append(backup)
            
            # Keep only one backup per week for the oldest 4 weeks
            sorted_weeks = sorted(weeks.keys(), reverse=True)
            for week in sorted_weeks[4:]:  # Keep first 4 weeks
                for backup in weeks[week][1:]:  # Keep only the most recent backup per week
                    self._delete_backup(backup)
        
        # Keep up to 3 monthly backups (from the oldest 3 months)
        monthly_backups = []
        
        for backup in backups:
            match = re.search(r"(\d{6})\d{2}_", os.path.basename(backup))
            if match:
                month_str = match.group(1)  # YYYYMM
                monthly_backups.append((month_str, backup))
        
        # Group by month
        months = {}
        for month, backup in monthly_backups:
            if month not in months:
                months[month] = []
            months[month].append(backup)
        
        # Keep only one backup per month for the oldest 3 months
        sorted_months = sorted(months.keys(), reverse=True)
        for month in sorted_months[3:]:  # Keep first 3 months
            for backup in months[month]:
                self._delete_backup(backup)
    
    def _group_backups_by_day(self, backups):
        """Group backups by day"""
        days = {}
        
        for backup in backups:
            match = re.search(r"(\d{8})_", os.path.basename(backup))
            if match:
                day = match.group(1)  # YYYYMMDD
                if day not in days:
                    days[day] = []
                days[day].append(backup)
        
        # Sort backups within each day (most recent first)
        for day in days:
            days[day].sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return days
    
    def _delete_backup(self, backup_path):
        """Delete a backup file"""
        try:
            os.remove(backup_path)
            self.logger.info(f"Deleted old backup: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_path}: {str(e)}")
    
    def restore_from_backup(self, backup_path, db_path=None):
        """Restore database from a backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        if not db_path:
            # Use database service's current path
            db_service = DatabaseService()
            db_path = db_service.db_path
            
            if not db_path:
                raise ValueError("Database path not specified")
        
        # Make backup of current database before restoring
        self.create_backup(sqlite3.connect(db_path), db_path)
        
        # Close any open connections
        db_service = DatabaseService()
        db_service.close()
        
        # Restore from backup
        try:
            shutil.copy2(backup_path, db_path)
            self.logger.info(f"Database restored from backup: {backup_path}")
            
            # Reconnect
            db_service.initialize(db_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {str(e)}")
            raise e
    
    def verify_backup(self, backup_path):
        """Verify a backup file's integrity"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Attempt to open the database
            conn = sqlite3.connect(backup_path)
            
            # Check integrity
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] == "ok"
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {str(e)}")
            return False
```

## 7. Detailed Design: Form Template System

### 7.1 Template Structure

Form templates will be defined using JSON files with the following enhanced structure:

```json
{
  "meta": {
    "form_type": "ICS-214",
    "version": "1.0",
    "display_name": "Activity Log",
    "description": "Records details of notable activities"
  },
  "schema_version": "1.1",
  "sections": [
    {
      "id": "header",
      "title": "Header Information",
      "fields": [
        {
          "id": "incident_name",
          "type": "text",
          "label": "Incident Name",
          "required": true,
          "max_length": 100,
          "default": "${incident_name}",
          "description": "The name assigned to the incident"
        },
        {
          "id": "operational_period_start",
          "type": "datetime",
          "label": "Operational Period (From)",
          "required": true,
          "default": "${current_datetime}",
          "description": "Start of the operational period"
        },
        {
          "id": "operational_period_end",
          "type": "datetime",
          "label": "Operational Period (To)",
          "required": true,
          "default": "${current_datetime + 24h}",
          "description": "End of the operational period"
        }
      ]
    },
    {
      "id": "identification",
      "title": "Identification",
      "fields": [
        {
          "id": "name",
          "type": "text",
          "label": "Name",
          "required": true,
          "default": "${user_name}",
          "description": "Your full name"
        },
        {
          "id": "ics_position",
          "type": "text",
          "label": "ICS Position",
          "required": true,
          "description": "Your ICS position/title"
        },
        {
          "id": "home_agency",
          "type": "text",
          "label": "Home Agency (and Unit)",
          "required": true,
          "description": "Your home agency and unit"
        }
      ]
    }
  ],
  "repeatable_sections": [
    {
      "id": "activity_log",
      "title": "Activity Log",
      "min_entries": 1,
      "max_entries": null,
      "fields": [
        {
          "id": "activity_datetime",
          "type": "datetime",
          "label": "Date/Time",
          "required": true,
          "default": "${current_datetime}",
          "description": "When the activity occurred"
        },
        {
          "id": "notable_activities",
          "type": "textarea",
          "label": "Notable Activities",
          "required": true,
          "rows": 4,
          "description": "Description of the activity"
        }
      ]
    },
    {
      "id": "resources_assigned",
      "title": "Resources Assigned",
      "min_entries": 0,
      "max_entries": null,
      "fields": [
        {
          "id": "resource_name",
          "type": "text",
          "label": "Name",
          "required": true,
          "description": "Resource name"
        },
        {
          "id": "resource_position",
          "type": "text",
          "label": "ICS Position",
          "required": false,
          "description": "Resource ICS position"
        },
        {
          "id": "resource_home_agency",
          "type": "text",
          "label": "Home Agency (and Unit)",
          "required": false,
          "description": "Resource home agency"
        }
      ]
    }
  ],
  "footer": {
    "id": "footer",
    "title": "Prepared By",
    "fields": [
      {
        "id": "prepared_by_name",
        "type": "text",
        "label": "Name",
        "required": true,
        "default": "${user_name}",
        "description": "Name of person preparing form"
      },
      {
        "id": "prepared_by_position",
        "type": "text",
        "label": "Position/Title",
        "required": true,
        "description": "Position of person preparing form"
      },
      {
        "id": "prepared_by_signature",
        "type": "signature",
        "label": "Signature",
        "required": true,
        "description": "Signature of person preparing form"
      },
      {
        "id": "prepared_datetime",
        "type": "datetime",
        "label": "Date/Time",
        "required": true,
        "default": "${current_datetime}",
        "description": "When the form was prepared"
      }
    ]
  },
  "attachments": {
    "enabled": true,
    "allowed_types": ["image/jpeg", "image/png", "application/pdf", "text/plain"],
    "max_size": 10485760,  // 10 MB
    "sections": [
      {
        "id": "maps",
        "title": "Maps and Diagrams",
        "description": "Attach relevant maps or diagrams"
      },
      {
        "id": "supporting_docs",
        "title": "Supporting Documents",
        "description": "Attach supporting documents"
      }
    ]
  },
  "validation_rules": [
    {
      "type": "date_range",
      "fields": ["operational_period_start", "operational_period_end"],
      "message": "The 'To' date must be after the 'From' date"
    }
  ],
  "export_options": {
    "pdf": {
      "orientation": "portrait",
      "paper_size": "letter",
      "include_attachments": true
    },
    "ics_des": {
      "field_mapping": {
        "incident_name": "1",
        "name": "6",
        "ics_position": "7",
        "activity_log": "27"
      }
    }
  },
  "ui_options": {
    "tab_order": ["header", "identification", "activity_log", "resources_assigned", "footer"],
    "help_text": "This form is used to record the activities of personnel and equipment in field situations."
  }
}
```

### 7.2 Enhanced Template Service

```python
class TemplateService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemplateService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.templates = {}
        self.logger = Logger().get_logger()
        self.event_bus = EventBus()
        self.load_templates()
    
    def load_templates(self):
        """Load all templates from the forms directory"""
        forms_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'forms')
        
        if not os.path.exists(forms_dir):
            self.logger.warning(f"Forms directory not found: {forms_dir}")
            return
        
        for filename in os.listdir(forms_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(forms_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        template_data = json.load(f)
                        
                        # Validate template
                        if self.validate_template(template_data):
                            form_type = template_data.get('meta', {}).get('form_type')
                            if form_type:
                                self.templates[form_type] = template_data
                                self.logger.info(f"Loaded template: {form_type}")
                        else:
                            self.logger.warning(f"Invalid template in file: {filename}")
                
                except Exception as e:
                    self.logger.error(f"Error loading template from {file_path}: {str(e)}")
        
        # Load templates from plugins
        self._load_plugin_templates()
        
        # Notify others
        self.event_bus.emit("templates_loaded")
    
    def _load_plugin_templates(self):
        """Load templates from plugins"""
        plugin_manager = PluginManager()
        plugins = plugin_manager.get_all_plugins()
        
        for plugin_id, plugin_info in plugins.items():
            if not plugin_info.get("enabled", False):
                continue
            
            try:
                plugin_instance = plugin_info.get("instance")
                if plugin_instance and hasattr(plugin_instance, "get_templates"):
                    plugin_templates = plugin_instance.get_templates()
                    
                    for template in plugin_templates:
                        if self.validate_template(template):
                            form_type = template.get('meta', {}).get('form_type')
                            if form_type:
                                self.templates[form_type] = template
                                self.logger.info(f"Loaded template from plugin {plugin_id}: {form_type}")
            
            except Exception as e:
                self.logger.error(f"Error loading templates from plugin {plugin_id}: {str(e)}")
    
    def get_template(self, form_type):
        """Get a template by form type"""
        return self.templates.get(form_type)
    
    def get_all_templates(self):
        """Get all available templates"""
        return self.templates
    
    def validate_template(self, template):
        """Validate a template against the schema"""
        # Check required fields
        if not template.get('meta', {}).get('form_type'):
            return False
        
        if not template.get('meta', {}).get('display_name'):
            return False
        
        if 'sections' not in template:
            return False
        
        # Validate sections
        for section in template.get('sections', []):
            if 'id' not in section or 'title' not in section or 'fields' not in section:
                return False
            
            # Validate fields
            for field in section.get('fields', []):
                if 'id' not in field or 'type' not in field or 'label' not in field:
                    return False
        
        # Validate repeatable sections
        for section in template.get('repeatable_sections', []):
            if 'id' not in section or 'title' not in section or 'fields' not in section:
                return False
            
            # Validate fields
            for field in section.get('fields', []):
                if 'id' not in field or 'type' not in field or 'label' not in field:
                    return False
        
        return True
    
    def save_template(self, template):
        """Save a template to file"""
        if not self.validate_template(template):
            raise ValueError("Invalid template format")
        
        form_type = template.get('meta', {}).get('form_type')
        if not form_type:
            raise ValueError("Template missing form_type")
        
        # Normalize filename
        filename = f"{form_type.lower().replace('-', '_')}.json"
        forms_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'forms')
        
        if not os.path.exists(forms_dir):
            os.makedirs(forms_dir)
        
        file_path = os.path.join(forms_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        # Update in-memory cache
        self.templates[form_type] = template
        
        self.logger.info(f"Saved template: {form_type}")
        
        # Notify others
        self.event_bus.emit("template_saved", form_type)
        
        return file_path
    
    def create_template(self, form_type, display_name, description=None):
        """Create a new template with basic structure"""
        # Check if template already exists
        if form_type in self.templates:
            raise ValueError(f"Template already exists: {form_type}")
        
        # Create basic template structure
        template = {
            "meta": {
                "form_type": form_type,
                "version": "1.0",
                "display_name": display_name,
                "description": description or f"{display_name} form"
            },
            "schema_version": "1.1",
            "sections": [],
            "repeatable_sections": [],
            "footer": {
                "id": "footer",
                "title": "Footer",
                "fields": []
            },
            "validation_rules": [],
            "export_options": {},
            "ui_options": {}
        }
        
        # Save template
        self.save_template(template)
        
        return template
    
    def get_default_values(self, form_type):
        """Get default values for a form based on its template"""
        template = self.get_template(form_type)
        if not template:
            return {}
        
        default_values = {}
        
        # Get settings
        settings = QSettings("ICS Forms", "ICS Forms Management")
        user_name = settings.value("user/name", "")
        user_callsign = settings.value("user/callsign", "")
        incident_name = settings.value("incident/name", "")
        
        # Process regular sections
        for section in template.get('sections', []):
            for field in section.get('fields', []):
                field_id = field.get('id')
                default = field.get('default')
                
                if default:
                    # Process variables in default value
                    if isinstance(default, str):
                        if "${user_name}" in default:
                            default = default.replace("${user_name}", user_name)
                        
                        if "${user_callsign}" in default:
                            default = default.replace("${user_callsign}", user_callsign)
                        
                        if "${incident_name}" in default:
                            default = default.replace("${incident_name}", incident_name)
                        
                        if "${current_datetime}" in default:
                            current_datetime = datetime.now().isoformat()
                            default = default.replace("${current_datetime}", current_datetime)
                        
                        # Handle time arithmetic (e.g., ${current_datetime + 24h})
                        match = re.search(r"\$\{current_datetime \+ (\d+)([hd])\}", default)
                        if match:
                            amount = int(match.group(1))
                            unit = match.group(2)
                            
                            current_datetime = datetime.now()
                            
                            if unit == 'h':
                                future_datetime = current_datetime + timedelta(hours=amount)
                            elif unit == 'd':
                                future_datetime = current_datetime + timedelta(days=amount)
                            
                            default = re.sub(
                                r"\$\{current_datetime \+ \d+[hd]\}",
                                future_datetime.isoformat(),
                                default
                            )
                    
                    default_values[field_id] = default
        
        # Process repeatable sections
        for section in template.get('repeatable_sections', []):
            section_id = section.get('id')
            min_entries = section.get('min_entries', 0)
            
            if min_entries > 0:
                # Create default entries
                entries = []
                
                for _ in range(min_entries):
                    entry = {}
                    
                    for field in section.get('fields', []):
                        field_id = field.get('id')
                        default = field.get('default')
                        
                        if default:
                            # Process variables in default value (same as above)
                            if isinstance(default, str):
                                if "${user_name}" in default:
                                    default = default.replace("${user_name}", user_name)
                                
                                if "${user_callsign}" in default:
                                    default = default.replace("${user_callsign}", user_callsign)
                                
                                if "${incident_name}" in default:
                                    default = default.replace("${incident_name}", incident_name)
                                
                                if "${current_datetime}" in default:
                                    current_datetime = datetime.now().isoformat()
                                    default = default.replace("${current_datetime}", current_datetime)
                                
                                # Handle time arithmetic
                                match = re.search(r"\$\{current_datetime \+ (\d+)([hd])\}", default)
                                if match:
                                    amount = int(match.group(1))
                                    unit = match.group(2)
                                    
                                    current_datetime = datetime.now()
                                    
                                    if unit == 'h':
                                        future_datetime = current_datetime + timedelta(hours=amount)
                                    elif unit == 'd':
                                        future_datetime = current_datetime + timedelta(days=amount)
                                    
                                    default = re.sub(
                                        r"\$\{current_datetime \+ \d+[hd]\}",
                                        future_datetime.isoformat(),
                                        default
                                    )
                            
                            entry[field_id] = default
                    
                    entries.append(entry)
                
                default_values[section_id] = entries
        
        # Process footer
        footer = template.get('footer')
        if footer:
            for field in footer.get('fields', []):
                field_id = field.get('id')
                default = field.get('default')
                
                if default:
                    # Process variables in default value (same as above)
                    if isinstance(default, str):
                        if "${user_name}" in default:
                            default = default.replace("${user_name}", user_name)
                        
                        if "${user_callsign}" in default:
                            default = default.replace("${user_callsign}", user_callsign)
                        
                        if "${incident_name}" in default:
                            default = default.replace("${incident_name}", incident_name)
                        
                        if "${current_datetime}" in default:
                            current_datetime = datetime.now().isoformat()
                            default = default.replace("${current_datetime}", current_datetime)
                    
                    default_values[field_id] = default
        
        return default_values
```

## 8. Detailed Design: Import/Export Implementation

### 8.1 Export Service

The Export Service will handle exporting forms to various formats with enhanced features:

```python
class ExportService:
    def __init__(self):
        self.form_repository = FormRepository()
        self.logger = Logger().get_logger()
        self.event_bus = EventBus()
    
    def export_to_json(self, form_id, file_path=None, include_version_history=False):
        """Export a form to JSON format"""
        # Get form data
        form = self.form_repository.get_form(form_id)
        if not form:
            raise ValueError(f"Form not found: {form_id}")
        
        # Create export data structure
        export_data = {
            'form_id': form['form_id'],
            'form_type': form['form_type'],
            'form_name': form['form_name'],
            'version': form['current_version'],
            'status': form['status'],
            'created_by': form['created_by'],
            'created_at': form['created_at'],
            'updated_at': form['updated_at'],
            'data': form['data'],
            'attachments': []
        }
        
        # Add attachment metadata (but not the actual files)
        for attachment in form.get('attachments', []):
            export_data['attachments'].append({
                'section': attachment['section'],
                'file_path': os.path.basename(attachment['file_path']),
                'file_name': attachment['file_name'],
                'file_type': attachment['file_type'],
                'file_size': attachment['file_size'],
                'md5_hash': attachment['md5_hash'],
                'description': attachment['description']
            })
        
        # Add version history if requested
        if include_version_history:
            version_repository = VersionRepository()
            versions = version_repository.get_version_history(form_id)
            export_data['version_history'] = versions
        
        # Serialize to JSON
        json_data = json.dumps(export_data, indent=2)
        
        # Write to file if path is provided
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
            
            self.logger.info(f"Exported form {form_id} to JSON: {file_path}")
            
            # Notify others
            self.event_bus.emit("form_exported", form_id, "json", file_path)
            
            return file_path
        
        return json_data
    
    def export_to_ics_des(self, form_id, file_path=None, use_differential=False):
        """Export a form to ICS-DES format (radio transmission format)"""
        # Get form data
        form = self.form_repository.get_form(form_id)
        if not form:
            raise ValueError(f"Form not found: {form_id}")
        
        form_type = form['form_type']
        data = form['data']
        
        # Create ICS-DES encoder
        encoder = IcsDESEncoder()
        
        # Get template for field mapping
        template_service = TemplateService()
        template = template_service.get_template(form_type)
        
        field_mapping = None
        if template and 'export_options' in template and 'ics_des' in template['export_options']:
            field_mapping = template['export_options']['ics_des'].get('field_mapping')
        
        # Encode the form
        if use_differential:
            # Use differential encoding for more efficient transmission
            # This requires a previous version of the form for comparison
            version_repository = VersionRepository()
            versions = version_repository.get_version_history(form_id)
            
            if len(versions) > 1:
                # Get previous version
                prev_version = versions[1]  # Current version is at index 0
                prev_data = json.loads(prev_version['data'])
                
                # Encode with differential format
                des_string = encoder.encode_differential(form_type, data, prev_data, field_mapping)
            else:
                # No previous version, use standard encoding
                des_string = encoder.encode(form_type, data, field_mapping)
        else:
            # Use standard encoding
            des_string = encoder.encode(form_type, data, field_mapping)
        
        # Write to file if path is provided
        if file_path:
            with open(file_path, 'w') as f:
                f.write(des_string)
            
            self.logger.info(f"Exported form {form_id} to ICS-DES: {file_path}")
            
            # Notify others
            self.event_bus.emit("form_exported", form_id, "ics_des", file_path)
            
            return file_path
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(des_string)
        
        self.logger.info(f"Copied ICS-DES output for form {form_id} to clipboard")
        
        return des_string
    
    def export_to_pdf(self, form_id, file_path=None, include_attachments=True):
        """Export a form to PDF format"""
        # Get form data
        form = self.form_repository.get_form(form_id)
        if not form:
            raise ValueError(f"Form not found: {form_id}")
        
        form_type = form['form_type']
        data = form['data']
        
        # Get template for PDF options
        template_service = TemplateService()
        template = template_service.get_template(form_type)
        
        pdf_options = None
        if template and 'export_options' in template and 'pdf' in template['export_options']:
            pdf_options = template['export_options']['pdf']
        
        # Create PDF generator
        pdf_generator = PDFGenerator()
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate(
            form_type,
            data,
            form.get('attachments', []) if include_attachments else [],
            pdf_options
        )
        
        # Write to file if path is provided
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            self.logger.info(f"Exported form {form_id} to PDF: {file_path}")
            
            # Notify others
            self.event_bus.emit("form_exported", form_id, "pdf", file_path)
            
            return file_path
        
        return pdf_bytes
    
    def export_package(self, form_id, file_path=None):
        """Export a form with all attachments as a package"""
        # Get form data
        form = self.form_repository.get_form(form_id)
        if not form:
            raise ValueError(f"Form not found: {form_id}")
        
        if not file_path:
            # Generate default file path
            settings = QSettings("ICS Forms", "ICS Forms Management")
            export_dir = settings.value("export/location", os.path.expanduser("~"))
            
            # Sanitize form name for filename
            safe_name = re.sub(r'[^\w\-_\.]', '_', form['form_name'])
            
            file_path = os.path.join(export_dir, f"{safe_name}_package.zip")
        
        # Create temporary directory for package contents
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export form as JSON
            json_path = os.path.join(temp_dir, "form.json")
            self.export_to_json(form_id, json_path, include_version_history=True)
            
            # Export form as PDF
            pdf_path = os.path.join(temp_dir, "form.pdf")
            self.export_to_pdf(form_id, pdf_path, include_attachments=False)
            
            # Export form as ICS-DES
            des_path = os.path.join(temp_dir, "form.des")
            self.export_to_ics_des(form_id, des_path)
            
            # Copy attachments
            attachments_dir = os.path.join(temp_dir, "attachments")
            os.makedirs(attachments_dir)
            
            for attachment in form.get('attachments', []):
                src_path = attachment['file_path']
                if os.path.exists(src_path):
                    # Create subdirectory for section
                    section_dir = os.path.join(attachments_dir, attachment['section'])
                    os.makedirs(section_dir, exist_ok=True)
                    
                    # Copy file
                    dest_path = os.path.join(section_dir, attachment['file_name'])
                    shutil.copy2(src_path, dest_path)
            
            # Create README file
            readme_path = os.path.join(temp_dir, "README.txt")
            with open(readme_path, 'w') as f:
                f.write(f"Package for {form['form_name']} ({form['form_type']})\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")
                f.write(f"Form ID: {form['form_id']}\n")
                f.write("\nContents:\n")
                f.write("- form.json: Form data in JSON format\n")
                f.write("- form.pdf: Form rendered as PDF\n")
                f.write("- form.des: Form encoded in ICS-DES format for radio transmission\n")
                f.write("- attachments/: Directory containing form attachments\n")
            
            # Create ZIP archive
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add files to ZIP
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path_full = os.path.join(root, file)
                        zipf.write(
                            file_path_full,
                            os.path.relpath(file_path_full, temp_dir)
                        )
        
        self.logger.info(f"Exported form {form_id} as package: {file_path}")
        
        # Notify others
        self.event_bus.emit("form_exported", form_id, "package", file_path)
        
        return file_path
    
    def export_incident_archive(self, incident_id, file_path=None):
        """Export all forms for an incident as a single JSON file"""
        # Get incident
        incident_repository = IncidentRepository()
        incident = incident_repository.get_incident(incident_id)
        
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")
        
        # Get all forms for the incident
        forms = self.form_repository.get_forms_by_incident(incident_id)
        
        # Create archive data structure
        archive_data = {
            'incident_id': incident_id,
            'incident_name': incident['incident_name'],
            'export_date': datetime.now().isoformat(),
            'forms_count': len(forms),
            'forms': []
        }
        
        # Add forms to archive
        for form in forms:
            form_data = {
                'form_id': form['form_id'],
                'form_type': form['form_type'],
                'form_name': form['form_name'],
                'version': form['current_version'],
                'status': form['status'],
                'created_by': form['created_by'],
                'created_at': form['created_at'],
                'updated_at': form['updated_at'],
                'data': self.form_repository.get_form_data(form['form_id']),
                'attachments': []
            }
            
            # Add attachment metadata
            attachments = self.form_repository.get_form_attachments(form['form_id'])
            for attachment in attachments:
                form_data['attachments'].append({
                    'section': attachment['section'],
                    'file_path': os.path.basename(attachment['file_path']),
                    'file_name': attachment['file_name'],
                    'file_type': attachment['file_type'],
                    'file_size': attachment['file_size'],
                    'md5_hash': attachment['md5_hash'],
                    'description': attachment['description']
                })
            
            archive_data['forms'].append(form_data)
        
        # Serialize to JSON
        json_data = json.dumps(archive_data, indent=2)
        
        # Write to file if path is provided
        if not file_path:
            # Generate default file path
            settings = QSettings("ICS Forms", "ICS Forms Management")
            export_dir = settings.value("export/location", os.path.expanduser("~"))
            
            # Sanitize incident name for filename
            safe_name = re.sub(r'[^\w\-_\.]', '_', incident['incident_name'])
            
            file_path = os.path.join(export_dir, f"{safe_name}_archive.json")
        
        with open(file_path, 'w') as f:
            f.write(json_data)
        
        self.logger.info(f"Exported incident {incident_id} archive: {file_path}")
        
        # Notify others
        self.event_bus.emit("incident_exported", incident_id, file_path)
        
        return file_path
    
    def export_batch(self, form_ids, export_format, directory=None):
        """Export multiple forms in batch"""
        if not directory:
            # Use default export directory
            settings = QSettings("ICS Forms", "ICS Forms Management")
            directory = settings.value("export/location", os.path.expanduser("~"))
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Export each form
        results = []
        
        for form_id in form_ids:
            try:
                # Get form data for filename
                form = self.form_repository.get_form(form_id)
                if not form:
                    results.append({
                        'form_id': form_id,
                        'success': False,
                        'message': f"Form not found: {form_id}"
                    })
                    continue
                
                # Sanitize form name for filename
                safe_name = re.sub(r'[^\w\-_\.]', '_', form['form_name'])
                
                if export_format == 'json':
                    # Export as JSON
                    file_path = os.path.join(directory, f"{safe_name}.json")
                    self.export_to_json(form_id, file_path)
                    
                elif export_format == 'pdf':
                    # Export as PDF
                    file_path = os.path.join(directory, f"{safe_name}.pdf")
                    self.export_to_pdf(form_id, file_path)
                    
                elif export_format == 'ics_des':
                    # Export as ICS-DES
                    file_path = os.path.join(directory, f"{safe_name}.des")
                    self.export_to_ics_des(form_id, file_path)
                    
                elif export_format == 'package':
                    # Export as package
                    file_path = os.path.join(directory, f"{safe_name}_package.zip")
                    self.export_package(form_id, file_path)
                    
                else:
                    results.append({
                        'form_id': form_id,
                        'success': False,
                        'message': f"Unsupported export format: {export_format}"
                    })
                    continue
                
                results.append({
                    'form_id': form_id,
                    'form_name': form['form_name'],
                    'success': True,
                    'file_path': file_path
                })
                
            except Exception as e:
                self.logger.error(f"Error exporting form {form_id}: {str(e)}")
                
                results.append({
                    'form_id': form_id,
                    'success': False,
                    'message': str(e)
                })
        
        return results
```

### 8.2 Enhanced ICS-DES Encoder with Differential Format

```python
class IcsDESEncoder:
    def __init__(self):
        # Load field codes mapping
        self.field_codes = self._load_field_codes()
        
        # Load form-specific requirements
        self.form_requirements = self._load_form_requirements()
        
        self.logger = Logger().get_logger()
    
    def _load_field_codes(self):
        """Load field codes from the ICS-DES specification"""
        return {
            'incident_name': '1',
            'date': '2',
            'time': '3',
            'datetime': '4',
            'incident_number': '5',
            'name': '6',
            'position': '7',
            'location': '8',
            'identifier': '9',
            'status': '10',
            'prepared_by': '11',
            'objectives': '12',
            'operational_period': '13',
            'work_assignments': '14',
            'radio_channels': '15',
            'function': '16',
            'channel_name': '17',
            'medical_aid_stations': '18',
            'organization': '19',
            'safety_message': '20',
            'situation_summary': '21',
            'status_changes': '22',
            'check_in_list': '23',
            'to': '24',
            'from': '25',
            'message': '26',
            'activity_log': '27',
            'activity': '28',
            'resources': '29',
            'resource_type': '30',
            'required': '31',
            'available': '32',
            'hazards': '33',
            'hazard': '34',
            'mitigations': '35',
            'vehicles': '36',
            'type': '37',
            'resource_name': '38',
            'aircraft': '39',
            'assignment': '40',
            'resource_identifier': '41',
            'release_date_time': '42',
            'person_name': '43',
            'rating': '44',
            'comments': '45',
            'incident_commander': '46',
            'operations_chief': '47',
            'planning_chief': '48',
            'logistics_chief': '49',
            'finance_chief': '50'
        }
    
    def _load_form_requirements(self):
        """Load form-specific field requirements from the ICS-DES specification"""
        requirements = {}
        
        # ICS-213 requirements
        requirements['ICS-213'] = [
            'to', 'from', 'message', 'date', 'time'
        ]
        
        # ICS-214 requirements
        requirements['ICS-214'] = [
            'incident_name', 'name', 'position', 'activity_log'
        ]
        
        return requirements
    
    def encode(self, form_type, data, field_mapping=None):
        """Encode form data into ICS-DES format"""
        # Get form ID without the "ICS-" prefix
        form_id = form_type.replace('ICS-', '')
        
        # Use custom field mapping if provided
        if field_mapping:
            mapped_data = {}
            for field_name, field_code in field_mapping.items():
                if field_name in data:
                    mapped_data[field_code] = data[field_name]
            
            # Start building the result
            result = f"{form_id}{{"
            
            # Add mapped fields
            encoded_fields = []
            for field_code, value in mapped_data.items():
                encoded_fields.append(f"{field_code}~{self._escape_value(value)}")
            
            # Join the encoded fields
            result += "|".join(encoded_fields)
            
            # Close the result
            result += "}"
            
            return result
        
        # Otherwise, use standard encoding
        # Get required fields for this form type
        required_fields = self.form_requirements.get(form_type, [])
        
        # Start building the result
        result = f"{form_id}{{"
        
        # Add fields
        encoded_fields = []
        
        if form_type == 'ICS-213':
            # Special case for ICS-213
            encoded_fields.extend(self._encode_ics213_fields(data))
        elif form_type == 'ICS-214':
            # Special case for ICS-214
            encoded_fields.extend(self._encode_ics214_fields(data))
        else:
            # Generic encoding for other forms
            for field_name in required_fields:
                if field_name in data and data[field_name]:
                    field_code = self.field_codes.get(field_name)
                    if field_code:
                        encoded_fields.append(f"{field_code}~{self._escape_value(data[field_name])}")
        
        # Join the encoded fields
        result += "|".join(encoded_fields)
        
        # Close the result
        result += "}"
        
        return result
    
    def encode_differential(self, form_type, current_data, previous_data, field_mapping=None):
        """Encode only the changes between versions using differential format"""
        # Get form ID without the "ICS-" prefix
        form_id = form_type.replace('ICS-', '')
        
        # Start building the result with differential indicator
        result = f"{form_id}D{{"
        
        # Find differences
        encoded_fields = []
        
        if field_mapping:
            # Use custom field mapping
            for field_name, field_code in field_mapping.items():
                current_value = current_data.get(field_name)
                previous_value = previous_data.get(field_name)
                
                if current_value != previous_value:
                    encoded_fields.append(f"{field_code}~{self._escape_value(current_value)}")
        else:
            # Use all fields
            for field_name in current_data:
                current_value = current_data.get(field_name)
                previous_value = previous_data.get(field_name)
                
                if current_value != previous_value:
                    field_code = self.field_codes.get(field_name)
                    if field_code:
                        encoded_fields.append(f"{field_code}~{self._escape_value(current_value)}")
        
        # Handle special cases for repeated sections
        if form_type == 'ICS-214':
            # Activity log
            current_activities = current_data.get('activity_log', [])
            previous_activities = previous_data.get('activity_log', [])
            
            # Check for added or modified activities
            if current_activities != previous_activities:
                activity_items = []
                
                # First determine which activities are new or changed
                for i, activity in enumerate(current_activities):
                    is_new = i >= len(previous_activities)
                    is_changed = not is_new and activity != previous_activities[i]
                    
                    if is_new or is_changed:
                        time_value = activity.get('activity_datetime', '')
                        text_value = activity.get('notable_activities', '')
                        
                        if time_value and text_value:
                            activity_items.append(f"[3~{self._escape_value(time_value)}|28~{self._escape_value(text_value)}]")
                
                if activity_items:
                    encoded_fields.append(f"27~[{"|".join(activity_items)}]")
        
        # Join the encoded fields
        result += "|".join(encoded_fields)
        
        # Close the result
        result += "}"
        
        return result
    
    def _encode_ics213_fields(self, data):
        """Encode fields specific to ICS-213"""
        encoded_fields = []
        
        # To field (recipient)
        to_value = data.get('to_name', '')
        if to_value:
            encoded_fields.append(f"24~{self._escape_value(to_value)}")
        
        # From field (sender)
        from_value = data.get('from_name', '')
        if from_value:
            encoded_fields.append(f"25~{self._escape_value(from_value)}")
        
        # Message field
        message_value = data.get('message', '')
        if message_value:
            encoded_fields.append(f"26~{self._escape_value(message_value)}")
        
        # Date field
        date_value = data.get('date', '')
        if date_value:
            encoded_fields.append(f"2~{self._escape_value(date_value)}")
        
        # Time field
        time_value = data.get('time', '')
        if time_value:
            encoded_fields.append(f"3~{self._escape_value(time_value)}")
        
        return encoded_fields
    
    def _encode_ics214_fields(self, data):
        """Encode fields specific to ICS-214"""
        encoded_fields = []
        
        # Incident Name
        incident_name = data.get('incident_name', '')
        if incident_name:
            encoded_fields.append(f"1~{self._escape_value(incident_name)}")
        
        # Name
        name_value = data.get('name', '')
        if name_value:
            encoded_fields.append(f"6~{self._escape_value(name_value)}")
        
        # Position
        position_value = data.get('ics_position', '')
        if position_value:
            encoded_fields.append(f"7~{self._escape_value(position_value)}")
        
        # Activity Log
        activities = data.get('activity_log', [])
        if activities:
            activity_items = []
            for activity in activities:
                time_value = activity.get('activity_datetime', '')
                text_value = activity.get('notable_activities', '')
                if time_value and text_value:
                    activity_items.append(f"[3~{self._escape_value(time_value)}|28~{self._escape_value(text_value)}]")
            
            if activity_items:
                encoded_fields.append(f"27~[{"|".join(activity_items)}]")
        
        return encoded_fields
    
    def _escape_value(self, value):
        """Escape special characters in values"""
        if isinstance(value, str):
            # Replace pipes with escaped version
            value = value.replace('|', '\\/')
            
            # Replace tildes with escaped version
            value = value.replace('~', '\\:')
            
            # Replace square brackets with escaped versions
            value = value.replace('[', '\\(').replace(']', '\\)')
        
        return value
```

### 8.3 Enhanced Import Service

```python
class ImportService:
    def __init__(self):
        self.form_repository = FormRepository()
        self.logger = Logger().get_logger()
        self.event_bus = EventBus()
    
    def import_from_json(self, json_data, created_by):
        """Import a form from JSON data"""
        try:
            # Parse JSON data
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Validate basic structure
            required_fields = ['form_type', 'form_name', 'data']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field in JSON: {field}")
            
            # Extract form data
            form_type = data['form_type']
            form_name = data['form_name']
            form_data = data['data']
            
            # Get incident ID if provided
            incident_id = None
            if 'incident_id' in data:
                incident_id = data['incident_id']
            
            # Create the form
            form_id = self.form_repository.create_form(
                form_type, form_name, created_by, form_data, incident_id)
            
            # Process attachment references
            attachments = data.get('attachments', [])
            attachment_references = []
            
            for attachment in attachments:
                attachment_references.append({
                    'section': attachment.get('section', 'Other'),
                    'file_name': attachment.get('file_name', attachment.get('file_path', 'Unknown')),
                    'file_type': attachment.get('file_type', 'application/octet-stream'),
                    'file_size': attachment.get('file_size', 0),
                    'md5_hash': attachment.get('md5_hash', ''),
                    'description': attachment.get('description', '')
                })
            
            # Log import
            self.logger.info(f"Imported form {form_id} ({form_type}) from JSON")
            
            # Notify others
            self.event_bus.emit("form_imported", form_id)
            
            return {
                'form_id': form_id,
                'form_type': form_type,
                'form_name': form_name,
                'attachments': attachment_references,
                'success': True
            }
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error importing form: {str(e)}")
            raise ValueError(f"Error importing form: {str(e)}")
    
    def import_from_package(self, package_path, created_by):
        """Import a form and its attachments from a package"""
        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Package file not found: {package_path}")
        
        # Create temporary directory for extracted package
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract package
                with zipfile.ZipFile(package_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Find JSON file
                json_path = os.path.join(temp_dir, "form.json")
                if not os.path.exists(json_path):
                    # Look for any JSON file
                    json_files = glob.glob(os.path.join(temp_dir, "*.json"))
                    if not json_files:
                        raise ValueError("No form JSON file found in package")
                    json_path = json_files[0]
                
                # Load JSON data
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                # Import form
                import_result = self.import_from_json(json_data, created_by)
                form_id = import_result['form_id']
                
                # Process attachments
                attachments_dir = os.path.join(temp_dir, "attachments")
                if os.path.exists(attachments_dir) and os.path.isdir(attachments_dir):
                    file_service = FileService()
                    attachment_repository = AttachmentRepository()
                    
                    # Import each attachment
                    imported_attachments = []
                    
                    for section_dir in glob.glob(os.path.join(attachments_dir, "*")):
                        if os.path.isdir(section_dir):
                            section_name = os.path.basename(section_dir)
                            
                            for file_path in glob.glob(os.path.join(section_dir, "*")):
                                if os.path.isfile(file_path):
                                    # Copy file to attachment storage
                                    stored_path = file_service.store_attachment(file_path)
                                    
                                    # Get file info
                                    file_name = os.path.basename(file_path)
                                    file_size = os.path.getsize(file_path)
                                    file_type = file_service.get_mime_type(file_path)
                                    md5_hash = file_service.calculate_md5(file_path)
                                    
                                    # Add to database
                                    attachment_id = attachment_repository.add_attachment(
                                        form_id,
                                        section_name,
                                        stored_path,
                                        file_name,
                                        file_type,
                                        file_size,
                                        md5_hash,
                                        "Imported from package"
                                    )
                                    
                                    imported_attachments.append({
                                        'attachment_id': attachment_id,
                                        'section': section_name,
                                        'file_name': file_name
                                    })
                
                # Update import result
                import_result['attachments_imported'] = imported_attachments
                
                # Log import
                self.logger.info(f"Imported form {form_id} from package with {len(imported_attachments)} attachments")
                
                return import_result
                
            except Exception as e:
                self.logger.error(f"Error importing from package: {str(e)}")
                raise ValueError(f"Error importing from package: {str(e)}")
    
    def import_incident_archive(self, json_data, created_by):
        """Import multiple forms from an incident archive"""
        try:
            # Parse JSON data
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Validate basic structure
            required_fields = ['incident_name', 'forms']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field in archive JSON: {field}")
            
            incident_name = data['incident_name']
            forms = data['forms']
            
            # Create or get incident
            incident_repository = IncidentRepository()
            
            # Check if incident already exists
            existing_incident = incident_repository.find_incident_by_name(incident_name)
            
            if existing_incident:
                incident_id = existing_incident['incident_id']
            else:
                # Create new incident
                incident_id = incident_repository.create_incident(
                    incident_name,
                    datetime.now().isoformat(),
                    None,  # end_date
                    f"Imported from archive: {incident_name}",
                    "Active",
                    created_by
                )
            
            # Import each form
            results = []
            for form_data in forms:
                try:
                    # Add incident ID to form data
                    form_data['incident_id'] = incident_id
                    
                    # Import form
                    result = self.import_from_json(form_data, created_by)
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        'form_type': form_data.get('form_type', 'Unknown'),
                        'form_name': form_data.get('form_name', 'Unknown'),
                        'success': False,
                        'error': str(e)
                    })
            
            # Log import
            self.logger.info(f"Imported incident archive with {len(results)} forms")
            
            # Notify others
            self.event_bus.emit("incident_imported", incident_id)
            
            return {
                'incident_id': incident_id,
                'incident_name': incident_name,
                'total_forms': len(forms),
                'imported_forms': len([r for r in results if r.get('success', False)]),
                'failed_forms': len([r for r in results if not r.get('success', False)]),
                'results': results
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error importing archive: {str(e)}")
            raise ValueError(f"Error importing archive: {str(e)}")
    
    def import_batch(self, file_paths, created_by):
        """Import multiple files in batch"""
        results = []
        
        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    results.append({
                        'file_path': file_path,
                        'success': False,
                        'message': f"File not found: {file_path}"
                    })
                    continue
                
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext == '.json':
                    # Import JSON file
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                    
                    # Check if it's an incident archive
                    if 'incident_name' in json_data and 'forms' in json_data:
                        # Import as incident archive
                        archive_result = self.import_incident_archive(json_data, created_by)
                        
                        results.append({
                            'file_path': file_path,
                            'success': True,
                            'type': 'incident_archive',
                            'incident_id': archive_result['incident_id'],
                            'incident_name': archive_result['incident_name'],
                            'forms_imported': archive_result['imported_forms'],
                            'forms_failed': archive_result['failed_forms']
                        })
                    else:
                        # Import as individual form
                        form_result = self.import_from_json(json_data, created_by)
                        
                        results.append({
                            'file_path': file_path,
                            'success': True,
                            'type': 'form',
                            'form_id': form_result['form_id'],
                            'form_type': form_result['form_type'],
                            'form_name': form_result['form_name']
                        })
                
                elif file_ext == '.zip':
                    # Import package
                    package_result = self.import_from_package(file_path, created_by)
                    
                    results.append({
                        'file_path': file_path,
                        'success': True,
                        'type': 'package',
                        'form_id': package_result['form_id'],
                        'form_type': package_result['form_type'],
                        'form_name': package_result['form_name'],
                        'attachments_imported': len(package_result.get('attachments_imported', []))
                    })
                
                else:
                    results.append({
                        'file_path': file_path,
                        'success': False,
                        'message': f"Unsupported file type: {file_ext}"
                    })
            
            except Exception as e:
                self.logger.error(f"Error importing file {file_path}: {str(e)}")
                
                results.append({
                    'file_path': file_path,
                    'success': False,
                    'message': str(e)
                })
        
        return results
    
    def validate_json_format(self, json_data):
        """Validate the format of JSON data for importing"""
        try:
            # Parse JSON data
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Check if it's a single form or an archive
            if 'forms' in data and isinstance(data['forms'], list):
                # It's an archive
                required_fields = ['incident_name', 'forms']
                for field in required_fields:
                    if field not in data:
                        return False, f"Missing required field in archive JSON: {field}"
                
                # Check each form
                for i, form_data in enumerate(data['forms']):
                    if not isinstance(form_data, dict):
                        return False, f"Form at index {i} is not an object"
                    
                    for field in ['form_type', 'form_name', 'data']:
                        if field not in form_data:
                            return False, f"Form at index {i} is missing required field: {field}"
            else:
                # It's a single form
                required_fields = ['form_type', 'form_name', 'data']
                for field in required_fields:
                    if field not in data:
                        return False, f"Missing required field in JSON: {field}"
            
            return True, "JSON format is valid"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON syntax: {str(e)}"
        except Exception as e:
            return False, f"Error validating JSON: {str(e)}"
```

## 9. Detailed Design: Security Enhancements

### 9.1 Security Service

```python
class SecurityService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = Logger().get_logger()
        self._encryption_key = None
    
    def initialize(self):
        """Initialize security service"""
        # Load or create encryption key
        self._load_encryption_key()
    
    def _load_encryption_key(self):
        """Load or create encryption key"""
        key_path = self._get_key_path()
        
        if os.path.exists(key_path):
            # Load existing key
            try:
                with open(key_path, 'rb') as f:
                    self._encryption_key = f.read()
                
                self.logger.debug("Loaded encryption key")
                
            except Exception as e:
                self.logger.error(f"Error loading encryption key: {str(e)}")
                # Generate new key
                self._generate_encryption_key()
        else:
            # Generate new key
            self._generate_encryption_key()
    
    def _generate_encryption_key(self):
        """Generate a new encryption key"""
        from cryptography.fernet import Fernet
        
        try:
            # Generate key
            self._encryption_key = Fernet.generate_key()
            
            # Save key
            key_path = self._get_key_path()
            key_dir = os.path.dirname(key_path)
            
            if not os.path.exists(key_dir):
                os.makedirs(key_dir)
            
            with open(key_path, 'wb') as f:
                f.write(self._encryption_key)
            
            # Set restrictive permissions
            if platform.system() != 'Windows':
                os.chmod(key_path, 0o600)  # Owner read/write only
            
            self.logger.info("Generated new encryption key")
            
        except Exception as e:
            self.logger.error(f"Error generating encryption key: {str(e)}")
            raise RuntimeError(f"Failed to generate encryption key: {str(e)}")
    
    def _get_key_path(self):
        """Get path to encryption key file"""
        # Use OS-appropriate location for sensitive data
        if platform.system() == 'Windows':
            base_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "ICS Forms")
        elif platform.system() == 'Darwin':  # macOS
            base_dir = os.path.join(os.path.expanduser('~'), "Library", "Application Support", "ICS Forms")
        else:  # Linux and other Unix-like
            base_dir = os.path.join(os.path.expanduser('~'), ".ics_forms")
        
        return os.path.join(base_dir, "security", "encryption.key")
    
    def encrypt_data(self, data):
        """Encrypt data"""
        if not self._encryption_key:
            self._load_encryption_key()
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        from cryptography.fernet import Fernet
        
        fernet = Fernet(self._encryption_key)
        return fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data"""
        if not self._encryption_key:
            self._load_encryption_key()
        
        from cryptography.fernet import Fernet
        
        fernet = Fernet(self._encryption_key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        try:
            # Try to decode as UTF-8 string
            return decrypted_data.decode('utf-8')
        except UnicodeDecodeError:
            # Return as bytes if not a valid UTF-8 string
            return decrypted_data
    
    def generate_digital_signature(self, data):
        """Generate a digital signature for data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        import hashlib
        import hmac
        
        if not self._encryption_key:
            self._load_encryption_key()
        
        # Create signature using HMAC-SHA256
        signature = hmac.new(
            self._encryption_key,
            data,
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_digital_signature(self, data, signature):
        """Verify a digital signature for data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        import hashlib
        import hmac
        
        if not self._encryption_key:
            self._load_encryption_key()
        
        # Create expected signature
        expected_signature = hmac.new(
            self._encryption_key,
            data,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    def secure_delete_file(self, file_path):
        """Securely delete a file by overwriting with random data before deleting"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite file with random data multiple times
            for _ in range(3):  # DoD standard is 3 passes
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
            
            # Delete the file
            os.remove(file_path)
            
            self.logger.info(f"Securely deleted file: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error securely deleting file {file_path}: {str(e)}")
            raise e
    
    def encrypt_sensitive_field(self, value):
        """Encrypt a sensitive field value"""
        if not value:
            return None
        
        encrypted = self.encrypt_data(value)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_sensitive_field(self, encrypted_value):
        """Decrypt a sensitive field value"""
        if not encrypted_value:
            return None
        
        encrypted_bytes = base64.b64decode(encrypted_value)
        return self.decrypt_data(encrypted_bytes)
```

## 10. Detailed Design: Performance Optimizations

### 10.1 Performance Optimizer

```python
class PerformanceOptimizer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PerformanceOptimizer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = Logger().get_logger()
        self.cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.max_cache_size = 100  # Maximum number of items in cache
        self.cache_ttl = 300  # TTL in seconds (5 minutes)
    
    def optimize_query(self, query):
        """Optimize an SQL query"""
        # Simple query optimization rules
        optimized = query
        
        # Add LIMIT/OFFSET for potentially large result sets
        if "SELECT" in query.upper() and "LIMIT" not in query.upper():
            if not query.strip().endswith(";"):
                optimized += " LIMIT 1000;"
            else:
                optimized = optimized[:-1] + " LIMIT 1000;"
        
        # Use EXISTS instead of COUNT(*) > 0
        if "COUNT(*) > 0" in query.upper():
            optimized = query.replace("COUNT(*) > 0", "EXISTS").replace("COUNT(*) > 0", "EXISTS")
        
        # Index hint for specific queries (example)
        if "WHERE form_type =" in query:
            optimized = query.replace("WHERE form_type =", "WHERE form_type /* USE INDEX(idx_forms_type) */ =")
        
        return optimized
    
    def get_from_cache(self, cache_key):
        """Get an item from cache"""
        cache_entry = self.cache.get(cache_key)
        
        if not cache_entry:
            self.cache_stats['misses'] += 1
            return None
        
        timestamp, value = cache_entry
        
        # Check TTL
        if time.time() - timestamp > self.cache_ttl:
            # Expired
            del self.cache[cache_key]
            self.cache_stats['misses'] += 1
            return None
        
        self.cache_stats['hits'] += 1
        return value
    
    def add_to_cache(self, cache_key, value):
        """Add an item to cache"""
        # Prune cache if it's too large
        if len(self.cache) >= self.max_cache_size:
            self._prune_cache()
        
        # Add to cache with timestamp
        self.cache[cache_key] = (time.time(), value)
    
    def _prune_cache(self):
        """Remove oldest or expired items from cache"""
        current_time = time.time()
        
        # First, remove expired items
        expired_keys = [
            k for k, (timestamp, _) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        # If still too large, remove oldest items
        if len(self.cache) >= self.max_cache_size:
            sorted_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k][0]  # Sort by timestamp
            )
            
            # Remove oldest 20%
            num_to_remove = max(1, int(len(sorted_keys) * 0.2))
            for key in sorted_keys[:num_to_remove]:
                del self.cache[key]
    
    def optimize_batch_operations(self, operations, chunk_size=100):
        """Split a large batch operation into smaller chunks for better performance"""
        return [operations[i:i + chunk_size] for i in range(0, len(operations), chunk_size)]
    
    def optimize_form_loading(self, form_data, lazy_sections=None):
        """Optimize form loading by implementing lazy loading for specified sections"""
        if not lazy_sections or not isinstance(form_data, dict):
            return form_data
        
        # Create a lazy loader for each specified section
        result = form_data.copy()
        
        for section in lazy_sections:
            if section in result and isinstance(result[section], list) and len(result[section]) > 10:
                # Store the original data
                original_data = result[section]
                
                # Replace with a simple proxy that loads data on demand
                class LazyLoadProxy:
                    def __init__(self, items, batch_size=20):
                        self.items = items
                        self.loaded = items[:batch_size]  # Pre-load first batch
                        self.batch_size = batch_size
                        self.fully_loaded = len(items) <= batch_size
                    
                    def __iter__(self):
                        return iter(self.loaded)
                    
                    def __len__(self):
                        return len(self.items)
                    
                    def __getitem__(self, index):
                        if isinstance(index, slice):
                            # Load all items needed for the slice
                            start = index.start or 0
                            stop = index.stop or len(self.items)
                            self.load_range(start, stop)
                            return self.loaded[index]
                        else:
                            # Load single item
                            if index >= len(self.loaded):
                                self.load_range(0, index + 1)
                            return self.loaded[index]
                    
                    def load_range(self, start, stop):
                        """Load a range of items"""
                        if stop > len(self.loaded):
                            # Calculate batch to load
                            batch_end = min(len(self.items), stop)
                            self.loaded.extend(self.items[len(self.loaded):batch_end])
                            
                            if len(self.loaded) >= len(self.items):
                                self.fully_loaded = True
                    
                    def load_all(self):
                        """Load all items"""
                        if not self.fully_loaded:
                            self.loaded = self.items
                            self.fully_loaded = True
                
                result[section] = LazyLoadProxy(original_data)
        
        return result
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total if total > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'total': total,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cache_ttl': self.cache_ttl
        }
```

## 11. Detailed Design: Testing and Quality Assurance

### 11.1 Comprehensive Testing Strategy

```python
class TestingFramework:
    def __init__(self):
        self.logger = Logger().get_logger()
    
    def run_unit_tests(self, module_path=None):
        """Run unit tests"""
        command = ["pytest", "-v"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/unit")
        
        return self._run_tests(command)
    
    def run_integration_tests(self, module_path=None):
        """Run integration tests"""
        command = ["pytest", "-v"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/integration")
        
        return self._run_tests(command)
    
    def run_ui_tests(self, module_path=None):
        """Run UI tests"""
        command = ["pytest", "-v", "--verbose"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/ui")
        
        return self._run_tests(command)
    
    def run_property_tests(self, module_path=None):
        """Run property-based tests"""
        command = ["pytest", "-v"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/property")
        
        return self._run_tests(command)
    
    def run_performance_tests(self, module_path=None):
        """Run performance benchmark tests"""
        command = ["pytest", "-v", "--benchmark-only"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/performance")
        
        return self._run_tests(command)
    
    def run_chaos_tests(self, module_path=None):
        """Run chaos engineering tests"""
        command = ["pytest", "-v"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/chaos")
        
        return self._run_tests(command)
    
    def run_visual_regression_tests(self, module_path=None):
        """Run visual regression tests"""
        command = ["pytest", "-v"]
        
        if module_path:
            command.append(module_path)
        else:
            command.append("tests/ui/visual_regression")
        
        return self._run_tests(command)
    
    def _run_tests(self, command):
        """Run tests with the specified command"""
        try:
            import subprocess
            result = subprocess.run(command, capture_output=True, text=True)
            
            output = result.stdout
            errors = result.stderr
            
            # Log results
            if result.returncode == 0:
                self.logger.info(f"Tests passed: {command}")
            else:
                self.logger.error(f"Tests failed: {command}")
                self.logger.error(errors)
            
            return {
                'success': result.returncode == 0,
                'output': output,
                'errors': errors
            }
            
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {
                'success': False,
                'output': '',
                'errors': str(e)
            }
```

### 11.2 Property-Based Testing Example

```python
def test_form_validation_properties():
    """Test form validation using property-based testing"""
    import hypothesis
    from hypothesis import given, strategies as st
    
    # Create validation service
    validation_service = ValidationService()
    
    # Define strategies for form data
    text_strategy = st.text(min_size=0, max_size=100)
    date_strategy = st.dates().map(lambda d: d.isoformat())
    time_strategy = st.times().map(lambda t: t.isoformat())
    
    # Strategy for a valid ICS-213 form
    @given(
        to_name=st.text(min_size=1, max_size=100),
        to_position=text_strategy,
        from_name=st.text(min_size=1, max_size=100),
        from_position=text_strategy,
        subject=st.text(min_size=1, max_size=100),
        date=date_strategy,
        time=time_strategy,
        message=st.text(min_size=1, max_size=1000)
    )
    def test_valid_ics213(to_name, to_position, from_name, from_position, subject, date, time, message):
        """Test validation of valid ICS-213 forms"""
        form_type = "ICS-213"
        form_data = {
            "to_name": to_name,
            "to_position": to_position,
            "from_name": from_name,
            "from_position": from_position,
            "subject": subject,
            "date": date,
            "time": time,
            "message": message
        }
        
        # Validate form
        errors = validation_service.validate_form(form_type, form_data)
        
        # A valid form should have no errors
        assert len([e for e in errors if e["field_id"] in ["to_name", "from_name", "subject", "date", "time", "message"]]) == 0
    
    # Strategy for an invalid ICS-213 form with missing required fields
    @given(
        form_data=st.fixed_dictionaries({
            "to_position": text_strategy,
            "from_position": text_strategy,
            # Missing required fields: to_name, from_name, subject, date, time, message
        })
    )
    def test_invalid_ics213_missing_required(form_data):
        """Test validation of invalid ICS-213 forms with missing required fields"""
        form_type = "ICS-213"
        
        # Validate form
        errors = validation_service.validate_form(form_type, form_data)
        
        # Should have errors for all missing required fields
        required_fields = ["to_name", "from_name", "subject", "date", "time", "message"]
        for field in required_fields:
            assert any(e["field_id"] == field for e in errors)
    
    # Run the property-based tests
    test_valid_ics213()
    test_invalid_ics213_missing_required()
```

### 11.3 Visual Regression Testing Example

```python
def test_form_view_visual_regression():
    """Test the visual appearance of the form view using regression testing"""
    import pytest
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from PIL import Image, ImageChops
    
    # Create the form view
    form_view = FormView(form_type="ICS-213")
    
    # Show the form view
    form_view.show()
    
    # Wait for rendering
    QApplication.processEvents()
    
    # Capture screenshot
    screenshot = QApplication.primaryScreen().grabWindow(form_view.winId())
    
    # Save screenshot to temp file
    temp_file = "temp_screenshot.png"
    screenshot.save(temp_file, "PNG")
    
    # Load reference image
    reference_file = "tests/ui/visual_regression/references/form_view_ics213.png"
    
    try:
        reference_image = Image.open(reference_file)
        current_image = Image.open(temp_file)
        
        # Compare images
        diff = ImageChops.difference(reference_image, current_image)
        
        # Check if images are similar
        if diff.getbbox():
            # Images differ
            diff.save("tests/ui/visual_regression/diffs/form_view_ics213_diff.png")
            pytest.fail("Visual regression detected in form_view_ics213")
        
    except FileNotFoundError:
        # Reference image doesn't exist yet, create it
        import os
        os.makedirs(os.path.dirname(reference_file), exist_ok=True)
        
        # Copy current image as reference
        import shutil
        shutil.copy(temp_file, reference_file)
        pytest.skip("Reference image created for form_view_ics213")
    
    finally:
        # Clean up
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)
```

### 11.4 Performance Benchmark Testing Example

```python
def test_form_list_performance():
    """Benchmark the performance of loading and rendering the form list"""
    import pytest
    from PySide6.QtWidgets import QApplication
    
    # Create the form list page
    form_list_page = FormListPage()
    
    # Benchmark loading forms
    @pytest.mark.benchmark(group="form_list")
    def test_load_forms(benchmark):
        """Benchmark loading forms in the form list"""
        # Use a test database with 2000 forms
        db_service = DatabaseService()
        db_service.initialize("tests/data/test_large.db")
        
        # Benchmark loading forms
        result = benchmark(form_list_page.load_forms, 1, 50)
        
        # Check result
        assert len(result["forms"]) == 50
        assert result["total_count"] > 0
    
    # Benchmark search
    @pytest.mark.benchmark(group="form_list")
    def test_search_forms(benchmark):
        """Benchmark searching forms in the form list"""
        # Use a test database with 2000 forms
        db_service = DatabaseService()
        db_service.initialize("tests/data/test_large.db")
        
        # Benchmark searching forms
        result = benchmark(form_list_page.search_forms, "incident", 1, 50)
        
        # Check result
        assert len(result["forms"]) <= 50
    
    # Run benchmarks
    test_load_forms()
    test_search_forms()
```

### 11.5 Chaos Engineering Test Example

```python
def test_database_corruption_recovery():
    """Test recovery from database corruption"""
    import pytest
    import tempfile
    import shutil
    import os
    import sqlite3
    
    # Create a temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        
        # Initialize database
        db_service = DatabaseService()
        db_service.initialize(db_path)
        
        # Create a form
        form_repository = FormRepository()
        form_id = form_repository.create_form(
            "ICS-213", "Test Form", "Test User", 
            {
                "to_name": "John Doe",
                "from_name": "Jane Smith",
                "subject": "Test",
                "date": "2025-01-01",
                "time": "12:00",
                "message": "Test message"
            }
        )
        
        # Close database connection
        db_service.close()
        
        # Create a backup of the database
        backup_path = os.path.join(temp_dir, "backup_test.db")
        shutil.copy2(db_path, backup_path)
        
        # Simulate corruption by writing garbage to the file
        with open(db_path, "ab") as f:
            f.write(b"CORRUPTION")
        
        # Try to open the corrupted database
        with pytest.raises(sqlite3.DatabaseError):
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA integrity_check")
        
        # Initialize startup manager
        startup_manager = StartupManager()
        
        # Set up backup location
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        saved_backup_path = os.path.join(os.path.dirname(db_path), backup_filename)
        shutil.copy2(backup_path, saved_backup_path)
        
        # Call recovery function
        result = startup_manager._handle_integrity_failure(db_service)
        
        # Check if recovery was successful
        assert result is True
        
        # Verify database is working
        db_service.initialize(db_path)
        form = form_repository.get_form(form_id)
        
        # Check if form was recovered
        assert form is not None
        assert form["form_name"] == "Test Form"
```

## 12. Detailed Design: Documentation System

### 12.1 Documentation Generator

```python
class DocumentationGenerator:
    def __init__(self):
        self.logger = Logger().get_logger()
    
    def generate_user_manual(self, output_dir):
        """Generate user manual documentation"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate main manual file
        manual_path = os.path.join(output_dir, "user_manual.md")
        
        with open(manual_path, "w") as f:
            f.write("# ICS Forms Management Application - User Manual\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            f.write("1. [Introduction](#introduction)\n")
            f.write("2. [Getting Started](#getting-started)\n")
            f.write("3. [Working with Forms](#working-with-forms)\n")
            f.write("4. [Importing and Exporting](#importing-and-exporting)\n")
            f.write("5. [Attachments](#attachments)\n")
            f.write("6. [Settings](#settings)\n")
            f.write("7. [Keyboard Shortcuts](#keyboard-shortcuts)\n")
            f.write("8. [Troubleshooting](#troubleshooting)\n\n")
            
            # Introduction
            f.write("## Introduction\n\n")
            f.write("The ICS Forms Management Application is a standalone, offline-first desktop application ")
            f.write("that enables users to create, manage, export, and archive FEMA Incident Command System (ICS) forms. ")
            f.write("This manual provides comprehensive instructions for using the application.\n\n")
            
            # Continue writing sections...
        
        # Generate screenshots
        self._generate_screenshots(output_dir)
        
        # Generate tutorial files
        self._generate_tutorials(output_dir)
        
        # Generate troubleshooting guide
        self._generate_troubleshooting_guide(output_dir)
        
        return manual_path
    
    def generate_developer_documentation(self, output_dir):
        """Generate developer documentation"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate API documentation
        api_path = os.path.join(output_dir, "api.md")
        
        with open(api_path, "w") as f:
            f.write("# ICS Forms Management Application - API Documentation\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            f.write("1. [Architecture Overview](#architecture-overview)\n")
            f.write("2. [Core Components](#core-components)\n")
            f.write("3. [Database Schema](#database-schema)\n")
            f.write("4. [Plugin System](#plugin-system)\n")
            f.write("5. [Event System](#event-system)\n")
            f.write("6. [Form Templates](#form-templates)\n\n")
            
            # Architecture Overview
            f.write("## Architecture Overview\n\n")
            f.write("The application follows an enhanced layered architecture with event-driven communication patterns:\n\n")
            f.write("1. **Presentation Layer (UI):** Implements the user interface using PySide6, with tabbed interface and keyboard shortcuts\n")
            f.write("2. **Application Layer:** Contains the core business logic, application services, and command pattern for undo/redo\n")
            f.write("3. **Domain Layer:** Defines the core domain models and business rules\n")
            f.write("4. **Data Access Layer:** Handles database operations with migration support and file I/O\n")
            f.write("5. **Plugin System:** Allows extending form types and functionality\n")
            f.write("6. **Services Layer:** Provides cross-cutting concerns like logging, error handling, and security\n\n")
            
            # Continue writing sections...
        
        # Generate plugin development guide
        plugin_path = os.path.join(output_dir, "plugin_development.md")
        
        with open(plugin_path, "w") as f:
            f.write("# ICS Forms Management Application - Plugin Development Guide\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            f.write("1. [Plugin Architecture](#plugin-architecture)\n")
            f.write("2. [Creating a Plugin](#creating-a-plugin)\n")
            f.write("3. [Plugin Lifecycle](#plugin-lifecycle)\n")
            f.write("4. [API Reference](#api-reference)\n")
            f.write("5. [Example Plugins](#example-plugins)\n\n")
            
            # Plugin Architecture
            f.write("## Plugin Architecture\n\n")
            f.write("The application uses a plugin system that allows extending the core functionality ")
            f.write("without modifying the base code. Plugins can add new form types, custom export formats, ")
            f.write("and integration with external systems.\n\n")
            
            # Continue writing sections...
        
        return {
            "api_documentation": api_path,
            "plugin_guide": plugin_path
        }
    
    def _generate_screenshots(self, output_dir):
        """Generate screenshots for documentation"""
        screenshots_dir = os.path.join(output_dir, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # In a real implementation, this would use QApplication and take actual screenshots
        # For this design document, we'll just log the intent
        self.logger.info("Would generate screenshots for documentation")
    
    def _generate_tutorials(self, output_dir):
        """Generate tutorial files"""
        tutorials_dir = os.path.join(output_dir, "tutorials")
        os.makedirs(tutorials_dir, exist_ok=True)
        
        # Creating a form tutorial
        creating_form_path = os.path.join(tutorials_dir, "creating_a_form.md")
        with open(creating_form_path, "w") as f:
            f.write("# Tutorial: Creating a New Form\n\n")
            f.write("This tutorial guides you through the process of creating a new ICS form in the application.\n\n")
            
            # Steps
            f.write("## Steps\n\n")
            f.write("1. Start the application\n")
            f.write("2. Click the 'New Form' button in the top toolbar\n")
            f.write("3. Select the form type from the list\n")
            # Continue with steps...
        
        # Exporting forms tutorial
        exporting_forms_path = os.path.join(tutorials_dir, "exporting_forms.md")
        with open(exporting_forms_path, "w") as f:
            f.write("# Tutorial: Exporting Forms\n\n")
            f.write("This tutorial explains how to export forms in various formats.\n\n")
            
            # Steps
            f.write("## Steps\n\n")
            f.write("1. Open the form you want to export\n")
            f.write("2. Click the 'Export' button in the top toolbar\n")
            f.write("3. Select the desired export format from the dropdown menu\n")
            # Continue with steps...
    
    def _generate_troubleshooting_guide(self, output_dir):
        """Generate troubleshooting guide"""
        troubleshooting_path = os.path.join(output_dir, "troubleshooting.md")
        
        with open(troubleshooting_path, "w") as f:
            f.write("# Troubleshooting Guide\n\n")
            f.write("This guide helps you resolve common issues that may occur while using the application.\n\n")
            
            # Common issues
            f.write("## Common Issues\n\n")
            
            # Database errors
            f.write("### Database Errors\n\n")
            f.write("#### Issue: The application shows database corruption error\n\n")
            f.write("**Solution:**\n\n")
            f.write("1. The application should automatically attempt to restore from a backup.\n")
            f.write("2. If automatic restoration fails, you can manually restore a backup:\n")
            f.write("   a. Close the application\n")
            f.write("   b. Navigate to the application data directory\n")
            f.write("   c. Find the most recent backup file in the 'backups' folder\n")
            f.write("   d. Replace the corrupted database file with the backup\n")
            f.write("   e. Restart the application\n\n")
            
            # Continue with more issues and solutions...
```

## 13. Implementation Plan

### 13.1 Revised Development Phases

The implementation will be divided into the following enhanced phases:

1. **Phase 1: Core Infrastructure**
   - Enhanced database implementation with migration support
   - Version tracking system
   - Error handling and logging with comprehensive error classification
   - Event-driven architecture foundation
   - Security Service implementation

2. **Phase 2: MVP Form Types**
   - ICS-213 (General Message) implementation
   - ICS-214 (Activity Log) implementation
   - Enhanced template system with variables
   - Attachment handling with validation

3. **Phase 3: UI Implementation**
   - Main application window
   - Tabbed interface for working with multiple forms
   - Form list with advanced search and filter
   - Dashboard view for incident status
   - Settings interface
   - Keyboard shortcuts

4. **Phase 4: Import/Export Features**
   - Enhanced JSON export/import with version history
   - PDF generation with attachment support
   - ICS-DES format with differential encoding
   - Package export format with attachments
   - Batch operations for multiple forms

5. **Phase 5: Plugin System**
   - Plugin Manager implementation
   - Plugin interface definition
   - Example plugin implementations
   - Form extension mechanism

6. **Phase 6: Performance Optimizations**
   - Lazy loading for form sections
   - Caching strategy
   - Background saving
   - Query optimization
   - Batch operations

7. **Phase 7: Testing and Documentation**
   - Unit testing
   - Property-based testing
   - UI testing with visual regression
   - Performance benchmark testing
   - User and developer documentation
   - Interactive help system

8. **Phase 8: Final Refinement**
   - Bug fixes based on testing
   - Performance tuning
   - Usability improvements
   - Final documentation updates

### 13.2 Development Environment Setup

The development environment will require:

1. Python 3.10 or later
2. PySide6 (Qt for Python)
3. SQLite 3
4. ReportLab for PDF generation
5. Cryptography library for security features
6. Pytest, pytest-qt, and hypothesis for testing
7. PIL/Pillow for image processing and visual regression testing
8. Gzip/zlib for compression

### 13.3 Build and Release Process

```python
class BuildManager:
    def __init__(self):
        self.logger = Logger().get_logger()
    
    def build_application(self, version, platform=None):
        """Build the application for the specified platform"""
        if not platform:
            # Detect current platform
            platform = self._detect_platform()
        
        # Update version information
        self._update_version_info(version)
        
        # Clean build directory
        self._clean_build_dir()
        
        # Run tests
        test_result = self._run_tests()
        if not test_result['success']:
            raise Exception("Tests failed, aborting build")
        
        # Build using PyInstaller
        build_command = self._get_build_command(platform, version)
        
        try:
            import subprocess
            result = subprocess.run(build_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Build failed: {result.stderr}")
                raise Exception(f"Build failed: {result.stderr}")
            
            # Package additional files
            self._package_additional_files(platform, version)
            
            # Create distribution archive
            dist_file = self._create_distribution(platform, version)
            
            self.logger.info(f"Build completed: {dist_file}")
            
            return {
                'success': True,
                'dist_file': dist_file,
                'version': version,
                'platform': platform
            }
            
        except Exception as e:
            self.logger.error(f"Build error: {str(e)}")
            raise
    
    def _detect_platform(self):
        """Detect the current platform"""
        import platform
        system = platform.system()
        
        if system == 'Windows':
            return 'windows'
        elif system == 'Darwin':
            return 'macos'
        else:
            return 'linux'
    
    def _update_version_info(self, version):
        """Update version information in source files"""
        # Update config.py
        with open("src/config.py", "r") as f:
            content = f.read()
        
        # Replace version
        content = re.sub(
            r"APP_VERSION\s*=\s*['\"].*['\"]",
            f"APP_VERSION = \"{version}\"",
            content
        )
        
        # Write updated content
        with open("src/config.py", "w") as f:
            f.write(content)
        
        self.logger.info(f"Updated version information to {version}")
    
    def _clean_build_dir(self):
        """Clean build directory"""
        import shutil
        
        # Clean dist directory
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # Clean build directory
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        self.logger.info("Cleaned build directories")
    
    def _run_tests(self):
        """Run tests before building"""
        testing_framework = TestingFramework()
        
        # Run unit tests
        unit_result = testing_framework.run_unit_tests()
        if not unit_result['success']:
            return unit_result
        
        # Run integration tests
        integration_result = testing_framework.run_integration_tests()
        if not integration_result['success']:
            return integration_result
        
        return {'success': True}
    
    def _get_build_command(self, platform, version):
        """Get PyInstaller command for the specified platform"""
        command = ["pyinstaller"]
        
        # Add platform-specific options
        if platform == 'windows':
            command.extend([
                "--windowed",
                "--icon=assets/icons/app_icon.ico",
                "--name=ICS_Forms_App"
            ])
        elif platform == 'macos':
            command.extend([
                "--windowed",
                "--icon=assets/icons/app_icon.icns",
                "--name=ICS_Forms_App"
            ])
        elif platform == 'linux':
            command.extend([
                "--name=ics_forms_app"
            ])
        
        # Add common options
        command.extend([
            "--onefile",
            "--clean",
            "--add-data=forms;forms",
            "--add-data=assets;assets",
            "src/main.py"
        ])
        
        return command
    
    def _package_additional_files(self, platform, version):
        """Package additional files with the distribution"""
        import shutil
        
        # Create platform-specific distribution directory
        dist_dir = f"dist/ICS_Forms_App_{version}_{platform}"
        os.makedirs(dist_dir, exist_ok=True)
        
        # Copy executable
        if platform == 'windows':
            shutil.copy2("dist/ICS_Forms_App.exe", dist_dir)
        elif platform == 'macos':
            shutil.copytree("dist/ICS_Forms_App.app", f"{dist_dir}/ICS_Forms_App.app")
        elif platform == 'linux':
            shutil.copy2("dist/ics_forms_app", dist_dir)
        
        # Copy documentation
        docs_dir = f"{dist_dir}/docs"
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generate documentation
        documentation_generator = DocumentationGenerator()
        documentation_generator.generate_user_manual(docs_dir)
        
        # Copy README
        shutil.copy2("README.md", dist_dir)
        
        # Copy license
        shutil.copy2("LICENSE", dist_dir)
        
        self.logger.info(f"Packaged additional files for {platform}")
    
    def _create_distribution(self, platform, version):
        """Create distribution archive"""
        import shutil
        
        dist_dir = f"dist/ICS_Forms_App_{version}_{platform}"
        
        if platform == 'windows':
            # Create ZIP archive
            archive_file = f"dist/ICS_Forms_App_{version}_{platform}.zip"
            shutil.make_archive(
                archive_file.replace(".zip", ""),
                'zip',
                "dist",
                f"ICS_Forms_App_{version}_{platform}"
            )
            return archive_file
            
        elif platform == 'macos':
            # Create DMG (simulation)
            archive_file = f"dist/ICS_Forms_App_{version}_{platform}.dmg"
            shutil.make_archive(
                archive_file.replace(".dmg", ""),
                'zip',
                "dist",
                f"ICS_Forms_App_{version}_{platform}"
            )
            # Rename to .dmg (in a real implementation, use hdiutil)
            os.rename(f"{archive_file}.zip", archive_file)
            return archive_file
            
        elif platform == 'linux':
            # Create tar.gz archive
            archive_file = f"dist/ICS_Forms_App_{version}_{platform}.tar.gz"
            shutil.make_archive(
                archive_file.replace(".tar.gz", ""),
                'gztar',
                "dist",
                f"ICS_Forms_App_{version}_{platform}"
            )
            return archive_file
```
