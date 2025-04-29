#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test cases for form tab widget.

This module tests the FormTabWidget class, ensuring that it correctly manages
form tabs and interacts with the controller.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, Signal, QPoint

from radioforms.views.form_tab_widget import FormTabWidget


# Make sure QApplication exists for the tests
@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the tests."""
    return QApplication.instance() or QApplication(sys.argv)


class TestFormTabWidget(unittest.TestCase):
    """Test cases for the FormTabWidget class."""

    def setUp(self):
        """Set up the test case."""
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create a mock controller with a forms_controller
        self.controller = MagicMock()
        self.forms_controller = MagicMock()
        self.controller.forms_controller = self.forms_controller
        
        # Create a form tab widget
        self.tab_widget = FormTabWidget(self.controller)
        
        # Create a mock welcome tab
        welcome_widget = QWidget()
        self.tab_widget.addTab(welcome_widget, "Welcome")
        
        # Create a mock form model
        self.form_model = MagicMock()
        self.form_model.form_id = "test-form-id"
        self.form_model.get_form_type.return_value = "TEST-FORM"
        
        # Create a mock form view with necessary signals
        self.form_view = MagicMock()
        self.form_view.form_modified = MagicMock()
        self.form_view.form_saved = MagicMock() 
        self.form_view.validation_failed = MagicMock()
        self.form_view.get_form.return_value = self.form_model
        
        # Mock the controller to return our mock form view
        self.forms_controller.create_view_for_form.return_value = self.form_view
        
        # Mock the forms_controller's open_forms dictionary
        self.forms_controller.open_forms = {self.form_model.form_id: self.form_model}

    def tearDown(self):
        """Clean up after the test case."""
        self.tab_widget.deleteLater()

    def test_init(self):
        """Test that the form tab widget initializes correctly."""
        self.assertEqual(self.tab_widget.controller, self.controller)
        self.assertEqual(len(self.tab_widget.tab_forms), 0)
        self.assertTrue(self.tab_widget.tabsClosable())
        self.assertTrue(self.tab_widget.isMovable())

    @patch('radioforms.views.form_tab_widget.QVBoxLayout.addWidget')
    def test_add_form_tab(self, mock_add_widget):
        """Test that add_form_tab adds a tab correctly."""
        # Add a tab
        index = self.tab_widget.add_form_tab(self.form_model, "Test Tab")
        
        # Check that the tab was added correctly
        self.assertEqual(index, 1)  # Index 0 is the welcome tab
        self.assertEqual(self.tab_widget.tabText(index), "Test Tab")
        self.assertEqual(self.tab_widget.tab_forms[index], "test-form-id")
        self.assertEqual(self.tab_widget.currentIndex(), index)
        
        # Check that the controller's create_view_for_form method was called
        self.forms_controller.create_view_for_form.assert_called_once_with(
            "test-form-id", self.tab_widget
        )
        
        # Check that addWidget was called with the form view
        mock_add_widget.assert_called_once()

    @patch('radioforms.views.form_tab_widget.QVBoxLayout.addWidget')
    def test_update_tab_modified(self, mock_add_widget):
        """Test that _update_tab_modified updates the tab label correctly."""
        # Add a tab
        index = self.tab_widget.add_form_tab(self.form_model, "Test Tab")
        
        # Update the tab label to indicate modification
        self.tab_widget._update_tab_modified(self.form_model)
        
        # Check that the tab label was updated correctly
        self.assertEqual(self.tab_widget.tabText(index), "Test Tab*")
        
        # Update again to ensure the * isn't added twice
        self.tab_widget._update_tab_modified(self.form_model)
        self.assertEqual(self.tab_widget.tabText(index), "Test Tab*")

    @patch('radioforms.views.form_tab_widget.QVBoxLayout.addWidget')
    def test_update_tab_saved(self, mock_add_widget):
        """Test that _update_tab_saved updates the tab label correctly."""
        # Add a tab
        index = self.tab_widget.add_form_tab(self.form_model, "Test Tab")
        
        # Update the tab label to indicate modification
        self.tab_widget._update_tab_modified(self.form_model)
        self.assertEqual(self.tab_widget.tabText(index), "Test Tab*")
        
        # Update the tab label to indicate saving
        self.tab_widget._update_tab_saved(self.form_model)
        
        # Check that the tab label was updated correctly
        self.assertEqual(self.tab_widget.tabText(index), "Test Tab")

    @patch('radioforms.views.form_tab_widget.QMessageBox')
    @patch('radioforms.views.form_tab_widget.QVBoxLayout.addWidget')
    def test_on_tab_close_requested_not_modified(self, mock_add_widget, mock_messagebox):
        """Test that _on_tab_close_requested closes the tab correctly when not modified."""
        # Add a tab
        index = self.tab_widget.add_form_tab(self.form_model, "Test Tab")
        
        # Set up the controller's is_form_modified method
        self.forms_controller.is_form_modified.return_value = False
        
        # Mock the form_closed signal
        with patch.object(self.tab_widget, 'form_closed') as mock_signal:
            # Close the tab
            self.tab_widget._on_tab_close_requested(index)
            
            # Check that the controller's close_form method was called
            self.forms_controller.close_form.assert_called_once_with("test-form-id")
            
            # Check that the form_closed signal was emitted
            mock_signal.emit.assert_called_once_with("test-form-id")
            
            # Check that QMessageBox was not called (no unsaved changes)
            mock_messagebox.question.assert_not_called()


if __name__ == '__main__':
    unittest.main()
