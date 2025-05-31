"""Main application window.

This module contains the MainWindow class which serves as the primary
user interface for the RadioForms application.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# Conditional import for PySide6
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QMenuBar, QStatusBar, QLabel, QPushButton, QMessageBox,
        QTabWidget, QFileDialog
    )
    from PySide6.QtCore import Qt, Signal, QTimer
    from PySide6.QtGui import QAction, QKeySequence
    PYSIDE6_AVAILABLE = True
    
    # Import our components
    from .ics213_widget import ICS213Widget
    from ..services.form_service import FormService
    from ..services.file_service import FileService, FileServiceError
    from ..database.connection import DatabaseManager
    from ..forms.ics213 import Priority
    
except ImportError:
    PYSIDE6_AVAILABLE = False
    ICS213Widget = None
    FormService = None
    DatabaseManager = None
    # Dummy classes for development
    class QMainWindow:
        def __init__(self, parent=None): pass
        def setWindowTitle(self, title): pass
        def setMinimumSize(self, w, h): pass
        def setCentralWidget(self, widget): pass
        def menuBar(self): return None
        def statusBar(self): return None
        def show(self): pass
        def close(self): pass
        def resize(self, w, h): pass
    
    class Signal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass


class MainWindow(QMainWindow):
    """Main application window for RadioForms.
    
    This class provides the primary user interface including:
    - Menu bar with file operations
    - Central area for form display
    - Status bar for application feedback
    - Basic window management
    
    Example:
        window = MainWindow(database_path=Path("data.db"))
        window.show()
    """
    
    # Signals for application events
    database_error = Signal(str) if PYSIDE6_AVAILABLE else Signal()
    form_saved = Signal(str) if PYSIDE6_AVAILABLE else Signal()
    form_loaded = Signal(str) if PYSIDE6_AVAILABLE else Signal()
    
    def __init__(
        self, 
        database_path: Optional[Path] = None,
        debug: bool = False,
        parent: Optional[QMainWindow] = None
    ) -> None:
        """Initialize the main window.
        
        Args:
            database_path: Path to the database file
            debug: Enable debug mode
            parent: Parent widget (usually None for main window)
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.database_path = database_path or Path("radioforms.db")
        self.debug = debug
        self.current_form = None
        
        # Track window state
        self.is_form_modified = False
        
        # UI components
        self.ics213_widget = None
        self.form_service = None
        self.file_service = None
        self.db_manager = None
        
        # Menu actions for state management
        self.actions = {}
        
        self.logger.info(f"MainWindow initializing with database: {self.database_path}")
        
        # Setup the user interface
        self._setup_window()
        self._setup_ui()
        self._setup_menus()
        self._setup_status_bar()
        self._connect_signals()
        
        # Initialize application state
        self._initialize_application()
        
        self.logger.info("MainWindow initialization complete")
    
    def _setup_window(self) -> None:
        """Configure basic window properties."""
        self.setWindowTitle("RadioForms - ICS Forms Management")
        self.setMinimumSize(800, 600)
        
        # TODO: Restore window geometry from settings
        if PYSIDE6_AVAILABLE:
            self.resize(1200, 800)
        
        self.logger.debug("Window properties configured")
    
    def _setup_ui(self) -> None:
        """Set up the central user interface."""
        if not PYSIDE6_AVAILABLE:
            self.logger.info("PySide6 not available - UI setup skipped")
            return
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Application title
        title_label = QLabel("RadioForms - Phase 1 MVP")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget for different forms
        self.tab_widget = QTabWidget()
        
        # Add ICS-213 tab
        if ICS213Widget:
            # Initialize database and form service
            self._initialize_services()
            
            self.ics213_widget = ICS213Widget(form_service=self.form_service)
            self.tab_widget.addTab(self.ics213_widget, "ICS-213 General Message")
            
            # Connect form signals
            self.ics213_widget.form_changed.connect(self._on_form_changed)
            self.ics213_widget.form_saved.connect(self._on_form_saved_signal)
            self.ics213_widget.form_loaded.connect(self._on_form_loaded_signal)
            
            # Connect form change signal to menu state updates
            self.ics213_widget.form_changed.connect(self._update_menu_states)
        else:
            # Placeholder when PySide6 not available
            placeholder = QLabel("ICS-213 Form (PySide6 not available)")
            placeholder.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(placeholder, "ICS-213 General Message")
        
        main_layout.addWidget(self.tab_widget)
        
        self.logger.debug("UI layout created")
    
    def _setup_menus(self) -> None:
        """Set up the application menu bar with proper action management."""
        if not PYSIDE6_AVAILABLE:
            return
        
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New action
        self.actions['new'] = QAction("&New ICS-213", self)
        self.actions['new'].setShortcut(QKeySequence.New)
        self.actions['new'].setStatusTip("Create a new ICS-213 form")
        self.actions['new'].triggered.connect(self._on_new_form)
        file_menu.addAction(self.actions['new'])
        
        file_menu.addSeparator()
        
        # Save action
        self.actions['save'] = QAction("&Save", self)
        self.actions['save'].setShortcut(QKeySequence.Save)
        self.actions['save'].setStatusTip("Save the current form to database")
        self.actions['save'].triggered.connect(self._on_save_form)
        self.actions['save'].setEnabled(False)  # Initially disabled
        file_menu.addAction(self.actions['save'])
        
        # Save As action
        self.actions['save_as'] = QAction("Save &As...", self)
        self.actions['save_as'].setShortcut(QKeySequence.SaveAs)
        self.actions['save_as'].setStatusTip("Save the current form with a new name")
        self.actions['save_as'].triggered.connect(self._on_save_as_form)
        file_menu.addAction(self.actions['save_as'])
        
        file_menu.addSeparator()
        
        # Import action
        self.actions['import'] = QAction("&Import JSON...", self)
        self.actions['import'].setShortcut("Ctrl+I")
        self.actions['import'].setStatusTip("Import form from JSON file")
        self.actions['import'].triggered.connect(self._on_import_form)
        file_menu.addAction(self.actions['import'])
        
        # Export action
        self.actions['export'] = QAction("&Export JSON...", self)
        self.actions['export'].setShortcut("Ctrl+E")
        self.actions['export'].setStatusTip("Export current form as JSON")
        self.actions['export'].triggered.connect(self._on_export_form)
        file_menu.addAction(self.actions['export'])
        
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("&Recent Files")
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        # Exit action
        self.actions['exit'] = QAction("E&xit", self)
        self.actions['exit'].setShortcut(QKeySequence.Quit)
        self.actions['exit'].setStatusTip("Exit the application")
        self.actions['exit'].triggered.connect(self.close)
        file_menu.addAction(self.actions['exit'])
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Validate action
        self.actions['validate'] = QAction("&Validate Form", self)
        self.actions['validate'].setShortcut("F5")
        self.actions['validate'].setStatusTip("Validate the current form")
        self.actions['validate'].triggered.connect(self._on_validate_form)
        edit_menu.addAction(self.actions['validate'])
        
        edit_menu.addSeparator()
        
        # Clear action
        self.actions['clear'] = QAction("&Clear Form", self)
        self.actions['clear'].setShortcut("Ctrl+L")
        self.actions['clear'].setStatusTip("Clear all form data")
        self.actions['clear'].triggered.connect(self._on_clear_form)
        edit_menu.addAction(self.actions['clear'])
        
        # Form menu
        form_menu = menubar.addMenu("&Form")
        
        # Approve action
        self.actions['approve'] = QAction("&Approve Form", self)
        self.actions['approve'].setShortcut("Ctrl+A")
        self.actions['approve'].setStatusTip("Approve the current form")
        self.actions['approve'].triggered.connect(self._on_approve_form)
        self.actions['approve'].setEnabled(False)
        form_menu.addAction(self.actions['approve'])
        
        # Add Reply action
        self.actions['add_reply'] = QAction("Add &Reply", self)
        self.actions['add_reply'].setShortcut("Ctrl+R")
        self.actions['add_reply'].setStatusTip("Add a reply to the form")
        self.actions['add_reply'].triggered.connect(self._on_add_reply)
        self.actions['add_reply'].setEnabled(False)
        form_menu.addAction(self.actions['add_reply'])
        
        form_menu.addSeparator()
        
        # Priority actions
        priority_group = menubar.addMenu("&Priority")
        
        self.actions['priority_routine'] = QAction("&Routine", self)
        self.actions['priority_routine'].setShortcut("Ctrl+1")
        self.actions['priority_routine'].setStatusTip("Set priority to Routine")
        self.actions['priority_routine'].triggered.connect(lambda: self._set_priority(Priority.ROUTINE))
        self.actions['priority_routine'].setCheckable(True)
        priority_group.addAction(self.actions['priority_routine'])
        
        self.actions['priority_urgent'] = QAction("&Urgent", self)
        self.actions['priority_urgent'].setShortcut("Ctrl+2")
        self.actions['priority_urgent'].setStatusTip("Set priority to Urgent")
        self.actions['priority_urgent'].triggered.connect(lambda: self._set_priority(Priority.URGENT))
        self.actions['priority_urgent'].setCheckable(True)
        priority_group.addAction(self.actions['priority_urgent'])
        
        self.actions['priority_immediate'] = QAction("&Immediate", self)
        self.actions['priority_immediate'].setShortcut("Ctrl+3")
        self.actions['priority_immediate'].setStatusTip("Set priority to Immediate")
        self.actions['priority_immediate'].triggered.connect(lambda: self._set_priority(Priority.IMMEDIATE))
        self.actions['priority_immediate'].setCheckable(True)
        priority_group.addAction(self.actions['priority_immediate'])
        
        form_menu.addMenu(priority_group)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Refresh action
        self.actions['refresh'] = QAction("&Refresh", self)
        self.actions['refresh'].setShortcut("F5")
        self.actions['refresh'].setStatusTip("Refresh the current view")
        self.actions['refresh'].triggered.connect(self._on_refresh)
        view_menu.addAction(self.actions['refresh'])
        
        view_menu.addSeparator()
        
        # Status bar toggle
        self.actions['toggle_statusbar'] = QAction("&Status Bar", self)
        self.actions['toggle_statusbar'].setStatusTip("Show or hide the status bar")
        self.actions['toggle_statusbar'].setCheckable(True)
        self.actions['toggle_statusbar'].setChecked(True)
        self.actions['toggle_statusbar'].triggered.connect(self._toggle_status_bar)
        view_menu.addAction(self.actions['toggle_statusbar'])
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # Documentation action
        self.actions['documentation'] = QAction("&Documentation", self)
        self.actions['documentation'].setShortcut("F1")
        self.actions['documentation'].setStatusTip("Open documentation")
        self.actions['documentation'].triggered.connect(self._on_documentation)
        help_menu.addAction(self.actions['documentation'])
        
        # Keyboard shortcuts action
        self.actions['shortcuts'] = QAction("&Keyboard Shortcuts", self)
        self.actions['shortcuts'].setStatusTip("Show keyboard shortcuts")
        self.actions['shortcuts'].triggered.connect(self._on_show_shortcuts)
        help_menu.addAction(self.actions['shortcuts'])
        
        help_menu.addSeparator()
        
        # About action
        self.actions['about'] = QAction("&About RadioForms", self)
        self.actions['about'].setStatusTip("About this application")
        self.actions['about'].triggered.connect(self._on_about)
        help_menu.addAction(self.actions['about'])
        
        self.logger.debug("Enhanced menu bar configured")
    
    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        if not PYSIDE6_AVAILABLE:
            return
        
        status_bar = self.statusBar()
        
        # Default message
        status_bar.showMessage("Ready", 2000)
        
        # Version info (permanent widget)
        version_label = QLabel("v0.1.0")
        version_label.setStyleSheet("color: #6c757d;")
        status_bar.addPermanentWidget(version_label)
        
        self.logger.debug("Status bar configured")
    
    def _connect_signals(self) -> None:
        """Connect internal signals and slots."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Connect application signals
        self.database_error.connect(self._on_database_error)
        self.form_saved.connect(self._on_form_saved)
        self.form_loaded.connect(self._on_form_loaded)
        
        self.logger.debug("Signals connected")
    
    def _initialize_services(self) -> None:
        """Initialize database and form services."""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(self.database_path)
            
            # Initialize and validate database schema
            from ..database.schema import SchemaManager
            schema_manager = SchemaManager(self.db_manager)
            schema_manager.initialize_database()
            
            # Initialize form service
            self.form_service = FormService(self.db_manager)
            
            # Initialize file service
            self.file_service = FileService()
            
            self.logger.info("Database, form, and file services initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize services: {e}"
            self.logger.error(error_msg)
            
            if PYSIDE6_AVAILABLE:
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to initialize database:\n\n{error_msg}\n\nThe application will continue without database functionality."
                )
    
    def _initialize_application(self) -> None:
        """Initialize application state."""
        self.logger.info("Initializing application state")
        
        # Services are initialized when creating widgets
        # Update status
        if self.form_service:
            self._update_status("Application ready - Database connected")
        else:
            self._update_status("Application ready - No database")
        
        # Initialize menu states
        self._update_menu_states()
        
        self.logger.info("Application state initialized")
    
    def _update_status(self, message: str, timeout: int = 0) -> None:
        """Update status bar message.
        
        Args:
            message: Status message to display
            timeout: Message timeout in milliseconds (0 = permanent)
        """
        if PYSIDE6_AVAILABLE:
            self.statusBar().showMessage(message, timeout)
        
        self.logger.info(f"Status: {message}")
    
    # Menu action handlers
    def _on_new_form(self) -> None:
        """Handle new form action."""
        self.logger.info("New form requested")
        self._update_status("Creating new ICS-213 form...", 2000)
        
        if self.ics213_widget:
            self.ics213_widget.new_form()
            self._update_status("New ICS-213 form created", 3000)
        else:
            QTimer.singleShot(1000, lambda: self._update_status("New form created", 3000))
    
    def _on_load_form(self) -> None:
        """Handle load form action."""
        self.logger.info("Load form requested")
        self._update_status("Loading form...", 2000)
        
        # TODO: Show file dialog and load form
        QTimer.singleShot(1000, lambda: self._update_status("Load cancelled", 3000))
    
    def _on_save_form(self) -> None:
        """Handle save form action."""
        self.logger.info("Save form requested")
        self._update_status("Saving form...", 2000)
        
        if self.ics213_widget:
            self.ics213_widget.save_form()
        else:
            QTimer.singleShot(1000, lambda: self._update_status("Form saved", 3000))
    
    def _on_import_form(self) -> None:
        """Handle import form action."""
        self.logger.info("Import form requested")
        
        if not PYSIDE6_AVAILABLE or not self.file_service:
            self._update_status("Import not available")
            return
        
        # Check for unsaved changes first
        if self.ics213_widget and self.ics213_widget.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before importing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.ics213_widget.save_form()
                if self.ics213_widget.has_unsaved_changes():
                    return  # Save failed
            elif reply == QMessageBox.Cancel:
                return
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import ICS-213 Form",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            self._update_status("Importing form...", 1000)
            
            # Import form
            form = self.file_service.import_form_from_json(Path(file_path))
            
            # Load into UI
            if self.ics213_widget:
                self.ics213_widget.set_form(form)
                self._update_status(f"Form imported from {Path(file_path).name}", 3000)
                
                # Update window title
                title = f"RadioForms - {self.ics213_widget.get_form_title()}"
                self.setWindowTitle(title)
                
                self.logger.info(f"Form imported from {file_path}")
            else:
                self._update_status("No form widget available", 3000)
                
        except FileServiceError as e:
            error_msg = f"Import failed: {e}"
            self._update_status("Import failed")
            QMessageBox.critical(self, "Import Failed", error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected import error: {e}"
            self._update_status("Import failed")
            QMessageBox.critical(self, "Import Failed", error_msg)
            self.logger.error(error_msg)
    
    def _on_export_form(self) -> None:
        """Handle export form action."""
        self.logger.info("Export form requested")
        
        if not PYSIDE6_AVAILABLE or not self.file_service or not self.ics213_widget:
            self._update_status("Export not available")
            return
        
        # Get current form
        form = self.ics213_widget.get_form()
        if not form:
            QMessageBox.warning(self, "Export Failed", "No form to export")
            return
        
        # Validate form before export
        if not form.validate():
            reply = QMessageBox.question(
                self,
                "Invalid Form",
                "The current form has validation errors. Do you want to export it anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Generate default filename
        subject = form.data.subject.strip() if form.data.subject else "Untitled"
        # Clean filename
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        default_name = f"ICS213_{safe_subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export ICS-213 Form",
            str(Path.home() / default_name),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            self._update_status("Exporting form...", 1000)
            
            # Export form
            success = self.file_service.export_form_to_json(form, Path(file_path))
            
            if success:
                self._update_status(f"Form exported to {Path(file_path).name}", 3000)
                self.logger.info(f"Form exported to {file_path}")
                
                # Show success message with option to open folder
                reply = QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Form exported successfully to:\n{file_path}\n\nWould you like to open the containing folder?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Open containing folder (platform-specific)
                    import subprocess
                    import sys
                    
                    folder_path = Path(file_path).parent
                    if sys.platform == "win32":
                        subprocess.run(["explorer", str(folder_path)])
                    elif sys.platform == "darwin":
                        subprocess.run(["open", str(folder_path)])
                    else:
                        subprocess.run(["xdg-open", str(folder_path)])
            else:
                self._update_status("Export failed")
                QMessageBox.critical(self, "Export Failed", "Failed to export form")
                
        except FileServiceError as e:
            error_msg = f"Export failed: {e}"
            self._update_status("Export failed")
            QMessageBox.critical(self, "Export Failed", error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected export error: {e}"
            self._update_status("Export failed")
            QMessageBox.critical(self, "Export Failed", error_msg)
            self.logger.error(error_msg)
    
    def _on_about(self) -> None:
        """Handle about action."""
        if not PYSIDE6_AVAILABLE:
            self.logger.info("About dialog requested (PySide6 not available)")
            return
        
        QMessageBox.about(
            self,
            "About RadioForms",
            """
            <h3>RadioForms v0.1.0</h3>
            <p>ICS Forms Management Application</p>
            <p>Phase 1 MVP - ICS-213 General Message</p>
            <p>Built with Python and PySide6</p>
            <p><small>Following CLAUDE.md development principles</small></p>
            """
        )
    
    # Signal handlers
    def _on_database_error(self, error_message: str) -> None:
        """Handle database errors.
        
        Args:
            error_message: Error description
        """
        self.logger.error(f"Database error: {error_message}")
        self._update_status(f"Database error: {error_message}")
        
        if PYSIDE6_AVAILABLE:
            QMessageBox.critical(
                self,
                "Database Error",
                f"A database error occurred:\n\n{error_message}"
            )
    
    def _on_form_saved(self, form_path: str) -> None:
        """Handle form saved event.
        
        Args:
            form_path: Path where form was saved
        """
        self.logger.info(f"Form saved: {form_path}")
        self._update_status(f"Form saved to {form_path}", 5000)
        self.is_form_modified = False
    
    def _on_form_loaded(self, form_path: str) -> None:
        """Handle form loaded event.
        
        Args:
            form_path: Path of loaded form
        """
        self.logger.info(f"Form loaded: {form_path}")
        self._update_status(f"Form loaded from {form_path}", 5000)
        self.is_form_modified = False
    
    def _on_form_changed(self) -> None:
        """Handle form data changes."""
        self.is_form_modified = True
        
        # Update window title with modification indicator
        if self.ics213_widget:
            title = f"RadioForms - {self.ics213_widget.get_form_title()}"
            if self.ics213_widget.has_unsaved_changes():
                title += " *"
            self.setWindowTitle(title)
        
        self._update_status("Form modified", 1000)
    
    def _on_form_saved_signal(self, form_id: int) -> None:
        """Handle form saved signal from widget."""
        self.is_form_modified = False
        
        # Update window title
        if self.ics213_widget:
            title = f"RadioForms - {self.ics213_widget.get_form_title()}"
            self.setWindowTitle(title)
        
        self._update_status(f"Form saved successfully (ID: {form_id})", 3000)
    
    def _on_form_loaded_signal(self, form_id: int) -> None:
        """Handle form loaded signal from widget."""
        self.is_form_modified = False
        
        # Update window title
        if self.ics213_widget:
            title = f"RadioForms - {self.ics213_widget.get_form_title()}"
            self.setWindowTitle(title)
        
        self._update_status(f"Form loaded (ID: {form_id})", 3000)
        
        # Update menu states
        self._update_menu_states()
    
    # Additional menu action handlers
    def _update_recent_files_menu(self) -> None:
        """Update the recent files menu."""
        if not PYSIDE6_AVAILABLE or not hasattr(self, 'recent_files_menu'):
            return
            
        # TODO: Implement recent files functionality
        self.recent_files_menu.clear()
        
        # Add placeholder for now
        no_recent = self.recent_files_menu.addAction("No recent files")
        no_recent.setEnabled(False)
        
        self.logger.debug("Recent files menu updated")
    
    def _on_save_as_form(self) -> None:
        """Handle save as form action."""
        self.logger.info("Save as form requested")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Save as not available")
            return
        
        # Get current form
        form = self.ics213_widget.get_form()
        if not form:
            QMessageBox.warning(self, "Save As Failed", "No form to save")
            return
        
        # For now, delegate to the widget's save functionality
        # TODO: Implement proper "Save As" with file dialog
        self.ics213_widget.save_form()
        self._update_status("Form saved", 3000)
    
    def _on_validate_form(self) -> None:
        """Handle validate form action."""
        self.logger.info("Form validation requested")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Validation not available")
            return
        
        # Get current form and validate
        form = self.ics213_widget.get_form()
        if not form:
            QMessageBox.information(self, "Validation", "No form to validate")
            return
        
        try:
            is_valid = form.validate()
            if is_valid:
                QMessageBox.information(
                    self, 
                    "Form Validation", 
                    "✅ Form is valid and ready for submission."
                )
                self._update_status("Form validation passed", 3000)
            else:
                # Get validation errors
                errors = []
                if not form.data.to or not form.data.to.name:
                    errors.append("'To' field is required")
                if not form.data.from_person or not form.data.from_person.name:
                    errors.append("'From' field is required")
                if not form.data.subject:
                    errors.append("Subject is required")
                if not form.data.message:
                    errors.append("Message is required")
                
                error_text = "\n• ".join(["Form has validation errors:"] + errors)
                QMessageBox.warning(self, "Form Validation Failed", error_text)
                self._update_status("Form validation failed", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Error validating form: {e}")
            self.logger.error(f"Form validation error: {e}")
    
    def _on_clear_form(self) -> None:
        """Handle clear form action."""
        self.logger.info("Clear form requested")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Clear not available")
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Clear Form",
            "Are you sure you want to clear all form data?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.ics213_widget.new_form()
            self._update_status("Form cleared", 3000)
            self.setWindowTitle("RadioForms - ICS Forms Management")
    
    def _on_approve_form(self) -> None:
        """Handle approve form action."""
        self.logger.info("Form approval requested")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Approval not available")
            return
        
        # Get current form
        form = self.ics213_widget.get_form()
        if not form:
            QMessageBox.warning(self, "Approval Failed", "No form to approve")
            return
        
        # Check if form is valid first
        if not form.validate():
            QMessageBox.warning(
                self, 
                "Cannot Approve", 
                "Form must be valid before approval. Please validate and fix any errors first."
            )
            return
        
        # TODO: Implement proper approval workflow
        QMessageBox.information(
            self,
            "Form Approved",
            "Form has been marked as approved.\n\nNote: Full approval workflow will be implemented in future versions."
        )
        self._update_status("Form approved", 3000)
    
    def _on_add_reply(self) -> None:
        """Handle add reply action."""
        self.logger.info("Add reply requested")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Reply not available")
            return
        
        # TODO: Implement reply functionality
        QMessageBox.information(
            self,
            "Add Reply",
            "Reply functionality will be implemented in future versions.\n\nFor now, you can manually edit the form to add reply information."
        )
        self._update_status("Reply feature coming soon", 3000)
    
    def _set_priority(self, priority: 'Priority') -> None:
        """Set form priority.
        
        Args:
            priority: Priority level to set
        """
        self.logger.info(f"Setting priority to {priority.value}")
        
        if not PYSIDE6_AVAILABLE or not self.ics213_widget:
            self._update_status("Priority setting not available")
            return
        
        # Update form priority
        form = self.ics213_widget.get_form()
        if form:
            form.data.priority = priority
            self.ics213_widget.set_form(form)
            self._update_status(f"Priority set to {priority.value}", 3000)
            
            # Update priority action states
            self.actions['priority_routine'].setChecked(priority == Priority.ROUTINE)
            self.actions['priority_urgent'].setChecked(priority == Priority.URGENT)
            self.actions['priority_immediate'].setChecked(priority == Priority.IMMEDIATE)
        else:
            QMessageBox.warning(self, "Priority Setting", "No form available to set priority")
    
    def _on_refresh(self) -> None:
        """Handle refresh action."""
        self.logger.info("Refresh requested")
        
        if not PYSIDE6_AVAILABLE:
            return
        
        # Refresh current view
        if self.ics213_widget:
            # Force UI update
            self.ics213_widget.update()
            self._update_status("View refreshed", 2000)
        
        # Update menu states
        self._update_menu_states()
        
        self.logger.debug("View refreshed")
    
    def _toggle_status_bar(self) -> None:
        """Toggle status bar visibility."""
        if not PYSIDE6_AVAILABLE:
            return
        
        status_bar = self.statusBar()
        is_visible = status_bar.isVisible()
        status_bar.setVisible(not is_visible)
        
        # Update action state
        self.actions['toggle_statusbar'].setChecked(not is_visible)
        
        if not is_visible:
            self._update_status("Status bar shown", 2000)
        
        self.logger.debug(f"Status bar {'shown' if not is_visible else 'hidden'}")
    
    def _on_documentation(self) -> None:
        """Handle documentation action."""
        if not PYSIDE6_AVAILABLE:
            return
        
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation will be available in future versions.\n\n"
            "For now, refer to the README.md file in the project directory "
            "for basic usage instructions."
        )
    
    def _on_show_shortcuts(self) -> None:
        """Show keyboard shortcuts dialog."""
        if not PYSIDE6_AVAILABLE:
            return
        
        shortcuts_text = """
<h3>Keyboard Shortcuts</h3>
<table>
<tr><td><b>File Operations:</b></td><td></td></tr>
<tr><td>Ctrl+N</td><td>New Form</td></tr>
<tr><td>Ctrl+S</td><td>Save Form</td></tr>
<tr><td>Ctrl+Shift+S</td><td>Save As</td></tr>
<tr><td>Ctrl+I</td><td>Import JSON</td></tr>
<tr><td>Ctrl+E</td><td>Export JSON</td></tr>
<tr><td>Ctrl+Q</td><td>Exit</td></tr>

<tr><td><b>Form Operations:</b></td><td></td></tr>
<tr><td>F5</td><td>Validate Form</td></tr>
<tr><td>Ctrl+L</td><td>Clear Form</td></tr>
<tr><td>Ctrl+A</td><td>Approve Form</td></tr>
<tr><td>Ctrl+R</td><td>Add Reply</td></tr>

<tr><td><b>Priority:</b></td><td></td></tr>
<tr><td>Ctrl+1</td><td>Routine</td></tr>
<tr><td>Ctrl+2</td><td>Urgent</td></tr>
<tr><td>Ctrl+3</td><td>Immediate</td></tr>

<tr><td><b>View:</b></td><td></td></tr>
<tr><td>F5</td><td>Refresh</td></tr>

<tr><td><b>Help:</b></td><td></td></tr>
<tr><td>F1</td><td>Documentation</td></tr>
</table>
        """
        
        QMessageBox.about(self, "Keyboard Shortcuts", shortcuts_text)
    
    def _update_menu_states(self) -> None:
        """Update menu action states based on current application state."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Check if we have a form loaded
        has_form = self.ics213_widget and self.ics213_widget.get_form() is not None
        has_unsaved_changes = self.ics213_widget and self.ics213_widget.has_unsaved_changes() if has_form else False
        
        # Update save action
        self.actions['save'].setEnabled(has_unsaved_changes)
        
        # Update form-dependent actions
        form_actions = ['validate', 'clear', 'export', 'save_as']
        for action_name in form_actions:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(has_form)
        
        # Update approval actions (require valid form)
        approval_actions = ['approve', 'add_reply']
        for action_name in approval_actions:
            if action_name in self.actions:
                # For now, just check if form exists. Later we can add validation check
                self.actions[action_name].setEnabled(has_form)
        
        # Update priority actions
        priority_actions = ['priority_routine', 'priority_urgent', 'priority_immediate']
        for action_name in priority_actions:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(has_form)
        
        # Update priority checkboxes based on current form
        if has_form:
            current_priority = self.ics213_widget.get_form().data.priority
            self.actions['priority_routine'].setChecked(current_priority == Priority.ROUTINE)
            self.actions['priority_urgent'].setChecked(current_priority == Priority.URGENT)
            self.actions['priority_immediate'].setChecked(current_priority == Priority.IMMEDIATE)
        else:
            # Uncheck all priority actions when no form
            for action_name in priority_actions:
                self.actions[action_name].setChecked(False)
        
        self.logger.debug(f"Menu states updated: has_form={has_form}, has_changes={has_unsaved_changes}")
    
    def closeEvent(self, event) -> None:
        """Handle window close event.
        
        Args:
            event: Close event object
        """
        self.logger.info("Main window close requested")
        
        # Check for unsaved changes
        if self.ics213_widget and self.ics213_widget.has_unsaved_changes():
            if PYSIDE6_AVAILABLE:
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"You have unsaved changes in '{self.ics213_widget.get_form_title()}'.\n\nDo you want to save before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    self.ics213_widget.save_form()
                    # Only close if save was successful (no errors)
                    if self.ics213_widget.has_unsaved_changes():
                        event.ignore()
                        return
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
        
        # Save window state
        # TODO: Save window geometry and settings
        
        self.logger.info("Main window closing")
        event.accept()