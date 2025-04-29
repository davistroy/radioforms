#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application window implementation.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStatusBar, QToolBar, QMenuBar,
    QMenu, QDialog, QListWidget, QListWidgetItem, 
    QFileDialog, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QFont

from radioforms.views.form_tab_widget import FormTabWidget


class FormSelectionDialog(QDialog):
    """Dialog for selecting a form type to create."""
    
    def __init__(self, form_types, parent=None):
        """
        Initialize the form selection dialog.
        
        Args:
            form_types: List of (form_type, display_name) tuples
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.form_types = form_types
        self.selected_type = None
        
        self.setWindowTitle("Select Form Type")
        self.resize(400, 300)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create list widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Add form types to list
        for form_type, display_name in form_types:
            item = QListWidgetItem(f"{display_name} ({form_type})")
            item.setData(Qt.UserRole, form_type)
            self.list_widget.addItem(item)
            
        # Connect double click to accept
        self.list_widget.itemDoubleClicked.connect(self.accept)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)
        
    def accept(self):
        """Handle dialog acceptance."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_type = selected_items[0].data(Qt.UserRole)
        super().accept()
        
    def get_selected_type(self):
        """
        Get the selected form type.
        
        Returns:
            Selected form type, or None if no selection
        """
        return self.selected_type


class MainWindow(QMainWindow):
    """
    Main application window implementing the primary user interface.
    This provides the shell for the application, including menu bar,
    status bar, and main content area.
    """
    
    def __init__(self, controller, parent=None):
        """
        Initialize the main window.
        
        Args:
            controller: Application controller reference
            parent: Parent widget, if any
        """
        super().__init__(parent)
        self.controller = controller
        
        # Configure window
        self.setWindowTitle("RadioForms")
        self.resize(1024, 768)
        
        # Set up the UI components
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._create_central_widget()
        
        # Connect signals and slots
        self._connect_signals()
        
    def _create_menus(self):
        """Create the main menu bar and menus."""
        # Create menu bar
        self.menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("&File")
        
        # New form action
        self.new_form_action = QAction("&New Form", self)
        self.new_form_action.setShortcut("Ctrl+N")
        self.new_form_action.setStatusTip("Create a new form")
        self.file_menu.addAction(self.new_form_action)
        
        # Open form action
        self.open_form_action = QAction("&Open Form", self)
        self.open_form_action.setShortcut("Ctrl+O")
        self.open_form_action.setStatusTip("Open an existing form")
        self.file_menu.addAction(self.open_form_action)
        
        self.file_menu.addSeparator()
        
        # Save form action
        self.save_form_action = QAction("&Save", self)
        self.save_form_action.setShortcut("Ctrl+S")
        self.save_form_action.setStatusTip("Save the current form")
        self.file_menu.addAction(self.save_form_action)
        
        # Save As action
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Save the current form with a new name")
        self.file_menu.addAction(self.save_as_action)
        
        self.file_menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.setStatusTip("Exit the application")
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("&Edit")
        
        # Undo action
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.edit_menu.addAction(self.undo_action)
        
        # Redo action
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.edit_menu.addAction(self.redo_action)
        
        self.edit_menu.addSeparator()
        
        # Preferences action
        self.preferences_action = QAction("&Preferences", self)
        self.edit_menu.addAction(self.preferences_action)
        
        # Forms menu
        self.forms_menu = self.menu_bar.addMenu("&Forms")
        
        # Create ICS-213 form action
        self.new_ics213_action = QAction("New ICS-213 General Message", self)
        self.forms_menu.addAction(self.new_ics213_action)
        
        # Create ICS-214 form action
        self.new_ics214_action = QAction("New ICS-214 Activity Log", self)
        self.forms_menu.addAction(self.new_ics214_action)
        
        # View menu
        self.view_menu = self.menu_bar.addMenu("&View")
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu("&Help")
        
        # About action
        self.about_action = QAction("&About", self)
        self.help_menu.addAction(self.about_action)
        
    def _create_toolbar(self):
        """Create the main toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        
        # Add actions to toolbar
        self.toolbar.addAction(self.new_form_action)
        self.toolbar.addAction(self.open_form_action)
        self.toolbar.addAction(self.save_form_action)
        
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _create_central_widget(self):
        """Create the central widget containing the main UI components."""
        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create a form tab widget
        self.form_tab_widget = FormTabWidget(self.controller)
        
        # Create a welcome tab
        self.welcome_widget = self._create_welcome_widget()
        self.form_tab_widget.addTab(self.welcome_widget, "Welcome")
        
        # Add the tab widget to the main layout
        self.main_layout.addWidget(self.form_tab_widget)
        
    def _create_welcome_widget(self):
        """Create the welcome widget shown on startup."""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        
        # Add a welcome label
        welcome_label = QLabel("Welcome to RadioForms")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        
        # Add a subtitle
        subtitle_label = QLabel("ICS Forms Management Application")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        
        # Add a description
        description_label = QLabel(
            "A desktop application for managing, creating and sharing "
            "FEMA Incident Command System forms."
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        
        # Add buttons for quick actions
        button_layout = QHBoxLayout()
        
        self.new_form_button = QPushButton("Create New Form")
        self.open_form_button = QPushButton("Open Existing Form")
        
        button_layout.addStretch()
        button_layout.addWidget(self.new_form_button)
        button_layout.addWidget(self.open_form_button)
        button_layout.addStretch()
        
        # Add everything to the layout
        welcome_layout.addStretch()
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(subtitle_label)
        welcome_layout.addSpacing(20)
        welcome_layout.addWidget(description_label)
        welcome_layout.addSpacing(40)
        welcome_layout.addLayout(button_layout)
        welcome_layout.addStretch()
        
        return welcome_widget
        
    def _connect_signals(self):
        """Connect signals to slots."""
        # File menu
        self.new_form_action.triggered.connect(self._on_new_form)
        self.open_form_action.triggered.connect(self._on_open_form)
        self.save_form_action.triggered.connect(self._on_save_form)
        self.save_as_action.triggered.connect(self._on_save_form_as)
        self.exit_action.triggered.connect(self.close)
        
        # Forms menu
        self.new_ics213_action.triggered.connect(
            lambda: self._create_specific_form("ICS-213")
        )
        self.new_ics214_action.triggered.connect(
            lambda: self._create_specific_form("ICS-214")
        )
        
        # Welcome widget buttons
        self.new_form_button.clicked.connect(self._on_new_form)
        self.open_form_button.clicked.connect(self._on_open_form)
        
    @Slot()
    def _on_new_form(self):
        """Handle creating a new form."""
        # Get available form types
        form_types = self.controller.get_available_form_types()
        
        if not form_types:
            QMessageBox.warning(
                self,
                "No Form Types",
                "No form types are available. Please check your installation."
            )
            return
            
        # Show form selection dialog
        dialog = FormSelectionDialog(form_types, self)
        if dialog.exec() != QDialog.Accepted:
            return
            
        # Get selected form type
        form_type = dialog.get_selected_type()
        if not form_type:
            return
            
        # Create the form
        self._create_specific_form(form_type)
        
    def _create_specific_form(self, form_type):
        """
        Create a form of a specific type.
        
        Args:
            form_type: Type of form to create
        """
        # Create the form
        form = self.controller.create_form(form_type)
        
        if not form:
            QMessageBox.warning(
                self,
                "Form Creation Failed",
                f"Failed to create form of type {form_type}."
            )
            return
            
        # Add a tab for the form
        self.form_tab_widget.add_form_tab(form)
        
    @Slot()
    def _on_open_form(self):
        """Handle opening an existing form."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Form",
            "",
            "Form Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            # User cancelled
            return
            
        # Load the form
        form = self.controller.load_form(file_path)
        
        if not form:
            QMessageBox.warning(
                self,
                "Form Loading Failed",
                f"Failed to load form from {file_path}."
            )
            return
            
        # Add a tab for the form
        self.form_tab_widget.add_form_tab(form)
        
    @Slot()
    def _on_save_form(self):
        """Handle saving the current form."""
        # Get the current tab index
        index = self.form_tab_widget.currentIndex()
        
        # Skip if it's the welcome tab
        if index == 0:
            return
            
        # Save the tab
        self.form_tab_widget._save_tab(index)
        
    @Slot()
    def _on_save_form_as(self):
        """Handle saving the current form with a new name."""
        # Get the current tab index
        index = self.form_tab_widget.currentIndex()
        
        # Skip if it's the welcome tab
        if index == 0:
            return
            
        # Save the tab as
        self.form_tab_widget._save_tab_as(index)
            
    def closeEvent(self, event):
        """
        Handle the window close event.
        
        Args:
            event: Close event
        """
        # Check for unsaved changes in all tabs
        # For simplicity, we'll just close all tabs, which will prompt for saving
        self.form_tab_widget._close_all_tabs()
        
        # Notify the controller that the application is closing
        if self.controller:
            self.controller.shutdown()
            
        event.accept()
