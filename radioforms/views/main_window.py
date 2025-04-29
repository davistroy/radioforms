#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application window implementation.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStatusBar, QToolBar, QMenuBar,
    QMenu, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QFont


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
        
        # Create a tab widget for forms
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        
        # Create a welcome tab
        self.welcome_widget = self._create_welcome_widget()
        self.tab_widget.addTab(self.welcome_widget, "Welcome")
        
        # Add the tab widget to the main layout
        self.main_layout.addWidget(self.tab_widget)
        
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
        
        new_form_button = QPushButton("Create New Form")
        open_form_button = QPushButton("Open Existing Form")
        
        button_layout.addStretch()
        button_layout.addWidget(new_form_button)
        button_layout.addWidget(open_form_button)
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
        self.exit_action.triggered.connect(self.close)
        
        # Tab widget
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        
    @Slot(int)
    def _on_tab_close_requested(self, index):
        """
        Handle a request to close a tab.
        
        Args:
            index: Index of the tab to close
        """
        # Don't close the welcome tab (index 0)
        if index > 0:
            self.tab_widget.removeTab(index)
            
    def closeEvent(self, event):
        """
        Handle the window close event.
        
        Args:
            event: Close event
        """
        # Notify the controller that the application is closing
        # In a real app, we would check for unsaved changes here
        if self.controller:
            self.controller.shutdown()
            
        event.accept()
