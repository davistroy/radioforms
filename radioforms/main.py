#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RadioForms - ICS Forms Management Application

A desktop application for managing, creating and sharing FEMA Incident Command System forms.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from radioforms.controllers.app_controller import AppController


def main():
    """Main entry point for the application."""
    # Set application information
    QCoreApplication.setApplicationName("RadioForms")
    QCoreApplication.setApplicationVersion("0.1.0")
    QCoreApplication.setOrganizationName("RadioForms")
    
    # Create and set up the Qt application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent look across platforms
    
    # Initialize the main controller
    controller = AppController()
    
    # Start the application
    controller.start()
    
    # Execute the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
