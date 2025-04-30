#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the RadioForms startup wizard.

This script demonstrates the use of the startup wizard and can be used
for testing the wizard functionality.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

from radioforms.config.config_manager import ConfigManager
from radioforms.views.startup_wizard import run_startup_wizard


def main():
    """Run the startup wizard test."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("RadioForms")
    app.setOrganizationName("RadioForms")
    
    # Create a temporary config file for testing
    config_dir = Path.home() / ".radioforms" / "test"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.ini"
    
    # Initialize config manager
    config_manager = ConfigManager(str(config_path))
    
    # Run the startup wizard
    success = run_startup_wizard(config_manager)
    
    if success:
        print("Wizard completed successfully!")
        print("Configuration values:")
        for section in config_manager.get_sections():
            print(f"[{section}]")
            for key, value in config_manager.get_section_values(section).items():
                print(f"  {key} = {value}")
    else:
        print("Wizard was cancelled or failed.")
        
    # Clean up the temporary config file
    # Uncomment to remove the test config file after running
    # if config_path.exists():
    #     config_path.unlink()
    # if config_dir.exists():
    #     config_dir.rmdir()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
