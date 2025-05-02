#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Form Tab Widget.

This module contains unit tests for the FormTabWidget class to ensure
proper form listing, filtering, and management.
"""

import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from radioforms.views.form_tab_widget import FormTabWidget, FormTableModel, FormFilterProxyModel
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.database import DatabaseManager  # Import the alias from __init__
from radioforms.database.dao.form_dao_refactored import FormDAO
from unittest import mock


# Ensure QApplication exists for Qt widgets
app = QApplication.instance() or QApplication([])


class TestFormTableModel(unittest.TestCase):
    """Unit tests for the Form Table Model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model = FormTableModel()
        
    def test_add_form(self):
        """Test adding a form to the model."""
        # Create test form data
        form = {
            "form_id": "test_id_1",
            "form_type": "ICS-213",
            "subject": "Test Subject",
            "date": "2025-04-30",
            "state": "draft"
        }
        
        # Add form to model
        self.model.add_form(form)
        
        # Verify form was added correctly
        self.assertEqual(self.model.rowCount(), 1)
        
        # Check form data
        form_data = self.model.get_form_at_row(0)
        self.assertEqual(form_data["form_id"], "test_id_1")
        self.assertEqual(form_data["form_type"], "ICS-213")
        
        # Check item data
        id_item = self.model.item(0, FormTableModel.COL_ID)
        self.assertEqual(id_item.text(), "test_id_1")
        
        subject_item = self.model.item(0, FormTableModel.COL_SUBJECT)
        self.assertEqual(subject_item.text(), "Test Subject")
        
    def test_set_forms(self):
        """Test setting multiple forms in the model."""
        # Create test form data
        forms = [
            {
                "form_id": "test_id_1",
                "form_type": "ICS-213",
                "subject": "Test Subject 1",
                "date": "2025-04-30",
                "state": "draft"
            },
            {
                "form_id": "test_id_2",
                "form_type": "ICS-214",
                "incident_name": "Test Incident",
                "date": "2025-04-29",
                "state": "approved"
            }
        ]
        
        # Set forms in model
        self.model.set_forms(forms)
        
        # Verify forms were added correctly
        self.assertEqual(self.model.rowCount(), 2)
        
        # Check form data
        form_data_1 = self.model.get_form_at_row(0)
        self.assertEqual(form_data_1["form_id"], "test_id_1")
        
        form_data_2 = self.model.get_form_at_row(1)
        self.assertEqual(form_data_2["form_id"], "test_id_2")
        
    def test_get_form_at_row(self):
        """Test retrieving a form at a specific row."""
        # Create and add a test form
        form = {
            "form_id": "test_id_1",
            "form_type": "ICS-213",
            "subject": "Test Subject",
            "date": "2025-04-30",
            "state": "draft"
        }
        self.model.add_form(form)
        
        # Get form at valid row
        form_data = self.model.get_form_at_row(0)
        self.assertEqual(form_data["form_id"], "test_id_1")
        
        # Get form at invalid row
        form_data = self.model.get_form_at_row(1)  # Out of range
        self.assertIsNone(form_data)
        
        form_data = self.model.get_form_at_row(-1)  # Negative index
        self.assertIsNone(form_data)


class TestFormFilterProxyModel(unittest.TestCase):
    """Unit tests for the Form Filter Proxy Model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create source model and add test forms
        self.source_model = FormTableModel()
        
        # Create test forms
        forms = [
            {
                "form_id": "test_id_1",
                "form_type": "ICS-213",
                "subject": "Test Message 1",
                "date": "2025-04-30",
                "state": "draft"
            },
            {
                "form_id": "test_id_2",
                "form_type": "ICS-214",
                "incident_name": "Test Incident",
                "date": "2025-04-29",
                "state": "approved"
            },
            {
                "form_id": "test_id_3",
                "form_type": "ICS-213",
                "subject": "Important Message",
                "date": "2025-04-28",
                "state": "transmitted"
            }
        ]
        self.source_model.set_forms(forms)
        
        # Create proxy model
        self.proxy_model = FormFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        
    def test_search_text_filter(self):
        """Test filtering by search text."""
        # Test with no filter
        self.assertEqual(self.proxy_model.rowCount(), 3)
        
        # Filter by text that matches one form
        self.proxy_model.set_search_text("important")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Get the matching form
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(0, 0))
        matching_form = self.source_model.get_form_at_row(source_index.row())
        self.assertEqual(matching_form["form_id"], "test_id_3")
        
        # Clear filter
        self.proxy_model.set_search_text("")
        self.assertEqual(self.proxy_model.rowCount(), 3)
        
    def test_form_type_filter(self):
        """Test filtering by form type."""
        # Filter by ICS-213
        self.proxy_model.set_form_type_filter("ICS-213")
        self.assertEqual(self.proxy_model.rowCount(), 2)
        
        # Filter by ICS-214
        self.proxy_model.set_form_type_filter("ICS-214")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Filter by non-existent type
        self.proxy_model.set_form_type_filter("ICS-999")
        self.assertEqual(self.proxy_model.rowCount(), 0)
        
        # Clear filter
        self.proxy_model.set_form_type_filter("")
        self.assertEqual(self.proxy_model.rowCount(), 3)
        
    def test_status_filter(self):
        """Test filtering by status."""
        # Filter by draft status
        self.proxy_model.set_status_filter("draft")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Filter by approved status
        self.proxy_model.set_status_filter("approved")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Filter by non-existent status
        self.proxy_model.set_status_filter("unknown")
        self.assertEqual(self.proxy_model.rowCount(), 0)
        
        # Clear filter
        self.proxy_model.set_status_filter("")
        self.assertEqual(self.proxy_model.rowCount(), 3)
        
    def test_combined_filters(self):
        """Test combining multiple filters."""
        # Apply form type and search text filters
        self.proxy_model.set_form_type_filter("ICS-213")
        self.proxy_model.set_search_text("important")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Apply form type and status filters
        self.proxy_model.set_search_text("")
        self.proxy_model.set_form_type_filter("ICS-213")
        self.proxy_model.set_status_filter("draft")
        self.assertEqual(self.proxy_model.rowCount(), 1)
        
        # Apply all filters with no matches
        self.proxy_model.set_form_type_filter("ICS-213")
        self.proxy_model.set_status_filter("approved")  # No ICS-213 forms are approved
        self.proxy_model.set_search_text("important")
        self.assertEqual(self.proxy_model.rowCount(), 0)


@unittest.skip("UI test requires manual interaction")
class TestFormTabWidget(unittest.TestCase):
    """Unit tests for the Form Tab Widget."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks
        self.form_registry = MagicMock()
        self.form_dao = MagicMock()
        # Add mock db_manager attribute
        self.form_dao.db_manager = MagicMock()
        # Add mock connect method that returns a connection with execute method
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"form_id": "test_id_123"}
        mock_connection.execute.return_value = mock_cursor
        self.form_dao.db_manager.connect.return_value = mock_connection
        
        # Create widget
        self.widget = FormTabWidget(self.form_registry, self.form_dao)
        
    def test_initialization(self):
        """Test widget initialization."""
        # Verify widget was initialized correctly
        self.assertIsNotNone(self.widget._table_view)
        self.assertIsNotNone(self.widget._table_model)
        self.assertIsNotNone(self.widget._proxy_model)
        
        # Verify DAO was called to load forms
        self.form_dao.find_all.assert_called_once()
        
    def test_load_forms(self):
        """Test loading forms."""
        # Set up mock to return forms
        forms = [
            {"form_id": "test_id_1", "form_type": "ICS-213"},
            {"form_id": "test_id_2", "form_type": "ICS-214"}
        ]
        self.form_dao.find_all.return_value = forms
        
        # Load forms
        self.widget._load_forms()
        
        # Verify forms were loaded
        self.assertEqual(self.widget._table_model.rowCount(), 2)
        
    def test_on_form_double_clicked(self):
        """Test double-clicking a form."""
        # Set up signal spy
        self.signal_received = False
        self.form_id_received = None
        self.form_type_received = None
        
        def handle_form_opened(form_id, form_type):
            self.signal_received = True
            self.form_id_received = form_id
            self.form_type_received = form_type
            
        self.widget.form_opened.connect(handle_form_opened)
        
        # Set up mock model with a form
        form = {
            "form_id": "test_id_1",
            "form_type": "ICS-213"
        }
        self.widget._table_model.add_form(form)
        
        # Simulate double click on the form
        index = self.widget._proxy_model.index(0, 0)
        self.widget._on_form_double_clicked(index)
        
        # Verify signal was emitted
        self.assertTrue(self.signal_received)
        self.assertEqual(self.form_id_received, "test_id_1")
        self.assertEqual(self.form_type_received, "ICS-213")


if __name__ == "__main__":
    unittest.main()
