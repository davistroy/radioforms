#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Application Controller for RadioForms.

This module provides the main application controller that ties together
the various components of the RadioForms application.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget
from PySide6.QtCore import QSettings, Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QAction

from radioforms.config.config_manager import ConfigManager
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.incident_dao_refactored import IncidentDAO
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.views.startup_wizard import run_startup_wizard
from radioforms.views.ics213_form_editor import ICS213FormEditor
from radioforms.views.ics214_form_editor import ICS214FormEditor
from radioforms.views.form_tab_widget import FormTabWidget


class EnhancedAppController:
    """
    Enhanced Application Controller for RadioForms.
    
    This class coordinates the various components of the RadioForms application,
    including configuration, database access, form registry, and UI components.
    """
    
    def __init__(self):
        """Initialize the application controller."""
        # Initialize logger
        self._logger = logging.getLogger(__name__)
        
        # Set up application paths
        self._setup_paths()
        
        # Initialize configuration
        self._config_manager = ConfigManager(self._config_path)
        
        # Create application components
        self._main_window = None
        self._form_registry = None
        self._db_manager = None
        self._form_dao = None
        self._incident_dao = None
        
    def _setup_paths(self):
        """Set up application paths."""
        # Get user's home directory
        home_dir = Path.home()
        
        # Create config directory if it doesn't exist
        self._config_dir = home_dir / ".radioforms"
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set config file path
        self._config_path = str(self._config_dir / "config.ini")
        
    def _check_first_run(self) -> bool:
        """
        Check if this is the first run of the application.
        
        Returns:
            True if this is the first run, False otherwise
        """
        # Check if the configuration file exists and has a 'FirstRun' section
        if not Path(self._config_path).exists():
            return True
            
        # Check if 'FirstRun' setting is still true
        first_run = self._config_manager.get_value("General", "first_run", "true")
        return first_run.lower() == "true"
        
    def _run_startup_wizard(self) -> bool:
        """
        Run the startup wizard.
        
        Returns:
            True if the wizard completed successfully, False otherwise
        """
        # Run the startup wizard
        success = run_startup_wizard(self._config_manager)
        
        if success:
            # Update first_run setting
            self._config_manager.set_value("General", "first_run", "false")
            self._config_manager.save()
            
        return success
        
    def _initialize_database(self) -> bool:
        """
        Initialize the database connection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get database path from configuration
            db_path = self._config_manager.get_value("Database", "path", "")
            
            if not db_path:
                # Use default path if not configured
                documents_path = Path.home() / "Documents" / "RadioForms"
                documents_path.mkdir(parents=True, exist_ok=True)
                db_path = str(documents_path / "radioforms.db")
                
                # Save to configuration
                self._config_manager.set_value("Database", "path", db_path)
                self._config_manager.save()
                
            # Create database manager
            self._db_manager = DBManager(db_path)
            
            # Initialize database
            self._db_manager.init_db()
            
            # Create DAOs
            self._form_dao = FormDAO(self._db_manager)
            self._incident_dao = IncidentDAO(self._db_manager)
            
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to initialize database: {str(e)}\n\n"
                "The application may not function correctly."
            )
            return False
            
    def _initialize_form_registry(self) -> bool:
        """
        Initialize the form model registry.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get form registry instance
            self._form_registry = FormModelRegistry.get_instance()
            
            # Set the form DAO
            self._form_registry.set_form_dao(self._form_dao)
            
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize form registry: {e}")
            QMessageBox.critical(
                None,
                "Form Registry Error",
                f"Failed to initialize form registry: {str(e)}\n\n"
                "The application may not function correctly."
            )
            return False
            
    def _setup_main_window(self):
        """Set up the main application window."""
        # Create main window
        self._main_window = QMainWindow()
        self._main_window.setWindowTitle("RadioForms")
        self._main_window.setMinimumSize(QSize(1024, 768))
        
        # Create central tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self._main_window.setCentralWidget(self._tab_widget)
        
        # Create menu bar
        self._setup_menu_bar()
        
        # Create status bar
        self._main_window.statusBar().showMessage("Ready")
        
        # Create form tab widget
        self._form_tab_widget = FormTabWidget(
            self._form_registry,
            self._form_dao,
            parent=None
        )
        
        # Connect to form opened signal
        self._form_tab_widget.form_opened.connect(self._on_form_opened)
        
        # Add form tab widget to tab widget
        self._tab_widget.addTab(self._form_tab_widget, "Forms")
        
        # Create an empty tab to indicate how to add new tabs
        self._welcome_tab = QTabWidget()
        self._tab_widget.addTab(self._welcome_tab, "+")
        
        # Connect to tab change signal to handle the "+" tab
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        
    def _setup_menu_bar(self):
        """Set up the main window menu bar."""
        # Get menu bar
        menu_bar = self._main_window.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Create New Form menu
        new_form_menu = file_menu.addMenu("&New Form")
        
        # Add actions for each form type
        form_types = self._form_registry.get_registered_types()
        for form_type in form_types:
            action = QAction(form_type, self._main_window)
            action.triggered.connect(lambda checked, f=form_type: self._create_new_form(f))
            new_form_menu.addAction(action)
            
        # Open Form action
        open_action = QAction("&Open Form...", self._main_window)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_form)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self._main_window)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self._main_window.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        # Settings action
        settings_action = QAction("&Settings...", self._main_window)
        settings_action.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self._main_window)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _on_tab_close_requested(self, index: int):
        """
        Handle tab close request.
        
        Args:
            index: Index of the tab to close
        """
        # Don't close the welcome tab or form tab widget
        if index == 0 or index == self._tab_widget.count() - 1:
            return
            
        # Get the widget
        widget = self._tab_widget.widget(index)
        
        # Remove the tab
        self._tab_widget.removeTab(index)
        
        # Delete the widget
        widget.deleteLater()
        
    def _on_tab_changed(self, index: int):
        """
        Handle tab change event.
        
        Args:
            index: Index of the selected tab
        """
        # Check if the "+" tab was selected
        if index == self._tab_widget.count() - 1:
            # Switch to the first tab
            self._tab_widget.setCurrentIndex(0)
            
            # Show form creation dialog
            self._create_new_form()
            
    def _create_new_form(self, form_type: Optional[str] = None):
        """
        Create a new form.
        
        Args:
            form_type: Type of form to create, or None to show dialog
        """
        # If form type is not specified, show dialog to select form type
        if form_type is None:
            form_types = self._form_registry.get_registered_types()
            if not form_types:
                QMessageBox.warning(
                    self._main_window,
                    "No Form Types",
                    "No form types are registered. Cannot create new form."
                )
                return
                
            # This is a simplified selection dialog
            # In a real application, use a proper dialog
            form_type = form_types[0]
            
        # Create appropriate form editor based on type
        form_editor = None
        title = ""
        
        if form_type == "ICS-213":
            form_editor = ICS213FormEditor(self._form_registry)
            title = "New ICS-213 General Message"
        elif form_type == "ICS-214":
            form_editor = ICS214FormEditor(self._form_registry)
            title = "New ICS-214 Activity Log"
        else:
            # Generic handler for other form types
            # Create a new form through the registry
            form = self._form_registry.create_form(form_type)
            
            if form is None:
                QMessageBox.warning(
                    self._main_window,
                    "Form Creation Failed",
                    f"Failed to create form of type {form_type}."
                )
                return
                
            # Placeholder for generic form editor
            # In a real application, implement appropriate editors for each form type
            QMessageBox.information(
                self._main_window,
                "Not Implemented",
                f"Editor for {form_type} is not implemented yet."
            )
            return
            
        # Add the form editor to the tab widget
        index = self._tab_widget.insertTab(
            self._tab_widget.count() - 1,  # Insert before the "+" tab
            form_editor,
            title
        )
        
        # Switch to the new tab
        self._tab_widget.setCurrentIndex(index)
        
    def _open_form(self):
        """Open an existing form."""
        # This would typically show a dialog to select a form
        # For now, just show the form tab widget
        self._tab_widget.setCurrentIndex(0)
        
    def _on_form_opened(self, form_id: str, form_type: str):
        """
        Handle form opened from the form tab widget.
        
        Args:
            form_id: ID of the opened form
            form_type: Type of the opened form
        """
        # Create appropriate form editor based on type
        form_editor = None
        title = ""
        
        if form_type == "ICS-213":
            form_editor = ICS213FormEditor(self._form_registry, form_id=form_id)
            title = f"ICS-213 ({form_id})"
        elif form_type == "ICS-214":
            form_editor = ICS214FormEditor(self._form_registry, form_id=form_id)
            title = f"ICS-214 ({form_id})"
        else:
            # Generic handler for other form types
            QMessageBox.information(
                self._main_window,
                "Not Implemented",
                f"Editor for {form_type} is not implemented yet."
            )
            return
            
        # Add the form editor to the tab widget
        index = self._tab_widget.insertTab(
            self._tab_widget.count() - 1,  # Insert before the "+" tab
            form_editor,
            title
        )
        
        # Switch to the new tab
        self._tab_widget.setCurrentIndex(index)
        
    def _open_settings(self):
        """Open application settings dialog."""
        # Not implemented yet
        QMessageBox.information(
            self._main_window,
            "Settings",
            "Settings dialog not implemented yet."
        )
        
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self._main_window,
            "About RadioForms",
            "RadioForms\n\n"
            "Digital form manager for emergency communications\n\n"
            "Copyright © 2025"
        )
        
    def run(self):
        """Run the application."""
        # Check if this is the first run
        is_first_run = self._check_first_run()
        
        if is_first_run:
            # Run startup wizard
            if not self._run_startup_wizard():
                # Wizard was cancelled or failed
                QMessageBox.critical(
                    None,
                    "Setup Required",
                    "RadioForms requires initial setup to function properly. "
                    "Please run the application again to complete setup."
                )
                return False
                
        # Initialize database
        if not self._initialize_database():
            return False
            
        # Initialize form registry
        if not self._initialize_form_registry():
            return False
            
        # Set up main window
        self._setup_main_window()
        
        # Show main window
        self._main_window.show()
        
        # Check and load previously created incident if available
        # This is a placeholder for loading the user's current incident
        # In a real application, implement proper incident selection
        
        return True


def run_application():
    """Run the RadioForms application."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("RadioForms")
    app.setOrganizationName("RadioForms")
    
    # Create application controller
    controller = EnhancedAppController()
    
    # Run the application
    success = controller.run()
    
    if not success:
        return 1
        
    # Start application event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run_application())
