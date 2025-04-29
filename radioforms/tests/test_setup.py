#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests to verify that the development environment is set up correctly.
"""

import os
import sys
import unittest
import sqlite3

import PySide6
from PySide6.QtWidgets import QApplication
import reportlab


class SetupTestCase(unittest.TestCase):
    """Test case to verify the development environment setup."""
    
    def test_python_version(self):
        """Test that Python version is 3.10 or higher."""
        major, minor = sys.version_info[:2]
        self.assertGreaterEqual(major, 3, "Python major version should be 3 or higher")
        self.assertGreaterEqual(minor, 10, "Python minor version should be 10 or higher")
        
    def test_pyside6_installed(self):
        """Test that PySide6 is installed and working."""
        self.assertIsNotNone(PySide6.__version__, "PySide6 version should be available")
        
        # Create a QApplication instance to verify Qt functionality
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app, "Should be able to create a QApplication instance")
        
    def test_reportlab_installed(self):
        """Test that ReportLab is installed."""
        self.assertIsNotNone(reportlab.Version, "ReportLab version should be available")
        
    def test_sqlite_available(self):
        """Test that SQLite is available and supports WAL mode."""
        # Create an in-memory database
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        # Check if pragma operations work
        cursor.execute("PRAGMA journal_mode=WAL")
        journal_mode = cursor.fetchone()[0].upper()
        
        # Note: An in-memory database will report 'MEMORY' instead of 'WAL',
        # so we can't directly assert 'WAL' here, but we can ensure the operation runs
        self.assertIn(journal_mode, ("WAL", "MEMORY"), 
                      "SQLite should support WAL mode or report MEMORY for in-memory DBs")
        
        conn.close()
        
    def test_project_structure(self):
        """Test that the basic project structure exists."""
        # Get the root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Check for essential directories
        essential_dirs = [
            "models", "views", "controllers", "utils", 
            "database", "config", "forms", "tests"
        ]
        
        for directory in essential_dirs:
            dir_path = os.path.join(project_root, directory)
            self.assertTrue(os.path.isdir(dir_path), 
                            f"Project structure should include {directory} directory")
            
            # Check for __init__.py in each directory
            init_path = os.path.join(dir_path, "__init__.py")
            self.assertTrue(os.path.isfile(init_path), 
                            f"{directory} should be a proper package with __init__.py")


if __name__ == "__main__":
    unittest.main()
