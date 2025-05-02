#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test cases for form views.

This module tests the form view classes, ensuring that they correctly display
and interact with form models.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDateTime
from pytestqt.qt_compat import qt_api

from radioforms.models.ics213_form import ICS213Form
from radioforms.models.ics214_form import ICS214Form, ActivityLogEntry
from radioforms.views.form_view_base import FormViewBase
from unittest import mock


# Make sure QApplication exists for the tests
@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the tests."""
    return QApplication.instance() or QApplication(sys.argv)


class TestFormViewBase(unittest.TestCase):
    """Test cases for the FormViewBase class."""

    def setUp(self):
        """Set up the test case."""
        # Create a concrete subclass of FormViewBase for testing
        class TestFormView(FormViewBase):
            def update_ui_from_model(self):
                pass

            def update_model_from_ui(self):
                pass

            def _create_form_ui(self):
                pass

            def _connect_field_signals(self):
                pass

        self.form_model = MagicMock()
        self.form_model.get_form_type.return_value = "TEST-FORM"
        self.form_model.form_id = "test-form-id"
        self.form_model.validate.return_value = MagicMock(is_valid=True)

        # Patch the set_form method to prevent it from calling update_ui_from_model
        with patch.object(FormViewBase, 'set_form'):
            self.app = QApplication.instance() or QApplication(sys.argv)
            self.form_view = TestFormView(None)  # Create without form
            self.form_view._form_model = self.form_model  # Set model manually

    def tearDown(self):
        """Clean up after the test case."""
        self.form_view.deleteLater()

    def test_init(self):
        """Test that the form view initializes correctly."""
        # Basic initialization without form model
        with patch.object(FormViewBase, 'set_form'):
            view = self.form_view.__class__()
            self.assertIsNone(view._form_model)
            self.assertFalse(view._modified)
            self.assertFalse(view._read_only)

    def test_get_form(self):
        """Test that get_form returns the correct form model."""
        self.assertEqual(self.form_view.get_form(), self.form_model)

    def test_is_modified(self):
        """Test that is_modified returns the correct value."""
        self.assertFalse(self.form_view.is_modified())
        self.form_view._modified = True
        self.assertTrue(self.form_view.is_modified())

    def test_set_read_only(self):
        """Test that set_read_only sets the read-only state correctly."""
        self.assertFalse(self.form_view.is_read_only())
        self.form_view.set_read_only(True)
        self.assertTrue(self.form_view.is_read_only())
        self.form_view.set_read_only(False)
        self.assertFalse(self.form_view.is_read_only())

    def test_save_form(self):
        """Test that save_form saves the form correctly."""
        # Set up mocks
        self.form_view.update_model_from_ui = MagicMock()
        self.form_view.validate_form = MagicMock(return_value=True)
        self.form_view._show_validation_errors = MagicMock()

        # Set up a signal spy for the form_saved signal
        with patch.object(self.form_view, 'form_saved') as mock_signal:
            self.form_view.save_form()
            self.form_view.update_model_from_ui.assert_called_once()
            mock_signal.emit.assert_called_once()
            self.assertFalse(self.form_view._modified)


# Tests for ICS213FormView and ICS214FormView are omitted as they require UI components
# that are better tested in integration tests due to their dependency on Qt widgets.
# They should be tested differently, e.g., by mocking the UI components or using 
# Qt's test framework to simulate user interactions.


if __name__ == '__main__':
    unittest.main()
