#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application controller that coordinates between the different components
of the application.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal, Slot

from radioforms.views.main_window import MainWindow
from radioforms.views.startup_wizard import StartupWizard
from radioforms.database.db_manager import DatabaseManager
from radioforms.config.app_config import AppConfig
from radioforms.config.config_manager import ConfigManager, SystemIntegrityChecker
from radioforms.controllers.forms_controller import FormsController
from radioforms.controllers.api_controller import APIController


class AppController(QObject):
    """
    Main application controller that coordinates the application flow and
    manages interactions between models, views, and other controllers.
    """
    
    def __init__(self, parent=None):
        """Initialize the application controller."""
        super().__init__(parent)
        self.config = AppConfig()
        self.db_manager = None
        self.main_window = None
        self.config_manager = None
        self.api_controller = None
        
        # Initialize sub-controllers
        self.forms_controller = FormsController(self)
        
    def start(self):
        """Start the application."""
        # Initialize database connection
        self.init_database()
        
        # Initialize configuration manager
        self.init_config()
        
        # Check if this is the first run and show startup wizard if needed
        if self.check_first_run():
            self.show_startup_wizard()
        
        # Create and show the main window
        self.init_ui()
        
    def init_database(self):
        """Initialize the database connection."""
        try:
            self.db_manager = DatabaseManager(self.config.get('database', 'path'))
            # Perform any necessary database setup or migrations
            
            # Initialize the API controller once we have a database connection
            self.api_controller = APIController(self.db_manager, self)
        except Exception as e:
            # In a real application, this would use the error handling system
            print(f"Database initialization error: {e}")
            sys.exit(1)
    
    def init_config(self):
        """Initialize the configuration manager."""
        if self.db_manager:
            self.config_manager = ConfigManager(self.db_manager)
            
    def init_ui(self):
        """Initialize and display the user interface."""
        self.main_window = MainWindow(self)
        self.main_window.show()
        
        # Connect signals from forms controller to UI
        self._connect_form_signals()
        
    def check_first_run(self):
        """
        Check if this is the first run of the application.
        
        Returns:
            True if this is the first run, False otherwise
        """
        if not self.config_manager:
            return True
        
        return self.config_manager.is_first_run()
    
    def show_startup_wizard(self):
        """Show the startup wizard."""
        app_directory = Path(self.config.get('application', 'data_dir'))
        wizard = StartupWizard(self.db_manager, app_directory)
        result = wizard.exec()
        
        # If the user cancels the wizard, exit the application
        if result == 0:
            sys.exit(0)
    
    def _connect_form_signals(self):
        """Connect signals from the forms controller to UI handlers."""
        # These will be implemented as the UI is developed
        # Example:
        # self.forms_controller.form_created.connect(self.main_window.add_form_tab)
        pass
        
    def create_form(self, form_type):
        """
        Create a new form.
        
        Args:
            form_type: Type of form to create
            
        Returns:
            The created form or None if creation failed
        """
        return self.forms_controller.create_form(form_type)
        
    def load_form(self, path):
        """
        Load a form from disk.
        
        Args:
            path: Path to the form file
            
        Returns:
            The loaded form or None if loading failed
        """
        return self.forms_controller.load_form(path)
        
    def save_form(self, form_id, path=None):
        """
        Save a form to disk.
        
        Args:
            form_id: ID of the form to save
            path: Path to save to, or None to use default
            
        Returns:
            Path where the form was saved, or None if saving failed
        """
        return self.forms_controller.save_form(form_id, path)
        
    def close_form(self, form_id):
        """
        Close a form.
        
        Args:
            form_id: ID of the form to close
            
        Returns:
            True if the form was closed, False if not found
        """
        return self.forms_controller.close_form(form_id)
        
    def get_available_form_types(self):
        """
        Get a list of available form types.
        
        Returns:
            List of (form_type, display_name) tuples
        """
        return self.forms_controller.get_available_form_types()
        
    # ----- API-style dictionary interface methods -----
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """
        Get all active incidents as dictionaries.
        
        This method provides an API-style interface for UI components
        that need incident data in dictionary format.
        
        Returns:
            List of incident dictionaries
        """
        if self.api_controller:
            return self.api_controller.get_active_incidents()
        return []
    
    def get_forms_for_incident(self, incident_id: int) -> List[Dict[str, Any]]:
        """
        Get all forms for an incident as dictionaries.
        
        This method provides an API-style interface for UI components
        that need form data in dictionary format.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            List of form dictionaries
        """
        if self.api_controller:
            return self.api_controller.get_forms_for_incident(incident_id)
        return []
    
    def get_form_with_content(self, form_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a form with its content as dictionaries.
        
        This method provides an API-style interface for UI components
        that need form and content data in dictionary format.
        
        Args:
            form_id: ID of the form
            
        Returns:
            Dictionary with 'form' and 'content' keys, or None if not found
        """
        if self.api_controller:
            return self.api_controller.get_form_with_content(form_id)
        return None
    
    def get_incident_stats(self) -> Dict[str, int]:
        """
        Get incident statistics.
        
        This method provides an API-style interface for UI components
        that need incident statistics in dictionary format.
        
        Returns:
            Dictionary with incident statistics
        """
        if self.api_controller:
            return self.api_controller.get_incident_stats()
        return {'total': 0, 'active': 0, 'closed': 0}
    
    def get_recent_forms(self, limit: int = 10, incident_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recently updated forms as dictionaries.
        
        This method provides an API-style interface for UI components
        that need recent forms data in dictionary format.
        
        Args:
            limit: Maximum number of forms to return
            incident_id: Optional incident ID to filter by
            
        Returns:
            List of form dictionaries
        """
        if self.api_controller:
            return self.api_controller.get_recent_forms(limit, incident_id)
        return []
    
    def shutdown(self):
        """Clean up resources and prepare for application shutdown."""
        # Close database connections
        if self.db_manager:
            self.db_manager.close()
            
        # Save any unsaved forms or prompt user before closing
        # This would be implemented as the application develops
        
        # Perform any other necessary cleanup
