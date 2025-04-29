#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application controller that coordinates between the different components
of the application.
"""

import sys
import os
from PySide6.QtCore import QObject, Signal, Slot

from radioforms.views.main_window import MainWindow
from radioforms.database.db_manager import DatabaseManager
from radioforms.config.app_config import AppConfig


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
        
        # Initialize sub-controllers here as needed
        
    def start(self):
        """Start the application."""
        # Initialize database connection
        self.init_database()
        
        # Create and show the main window
        self.init_ui()
        
    def init_database(self):
        """Initialize the database connection."""
        try:
            self.db_manager = DatabaseManager(self.config.get('database', 'path'))
            # Perform any necessary database setup or migrations
        except Exception as e:
            # In a real application, this would use the error handling system
            print(f"Database initialization error: {e}")
            sys.exit(1)
            
    def init_ui(self):
        """Initialize and display the user interface."""
        self.main_window = MainWindow(self)
        self.main_window.show()
        
    def shutdown(self):
        """Clean up resources and prepare for application shutdown."""
        # Close database connections
        if self.db_manager:
            self.db_manager.close()
            
        # Perform any other necessary cleanup
