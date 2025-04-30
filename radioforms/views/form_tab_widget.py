#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Tab Widget for RadioForms.

This module provides a tab widget for displaying and managing forms in the
RadioForms application. It shows a list of available forms with filtering
and sorting capabilities.
"""

import os
import sys
import datetime
from typing import Dict, List, Optional, Any, Callable, Union

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, Signal, Slot, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
    QPushButton, QComboBox, QSplitter, QFrame, QTableView, QCheckBox,
    QHeaderView, QMenu, QSpacerItem, QSizePolicy, QToolButton, QStyle
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction

from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.database.dao.form_dao_refactored import FormDAO


class FormTableModel(QStandardItemModel):
    """
    Model for displaying forms in a table view.
    
    This model displays form metadata like ID, type, date, and subject.
    """
    
    # Column indices
    COL_ID = 0
    COL_TYPE = 1
    COL_DATE = 2
    COL_SUBJECT = 3
    COL_STATUS = 4
    
    def __init__(self, parent=None):
        """Initialize the form table model."""
        super().__init__(0, 5, parent)
        
        # Set header labels
        self.setHeaderData(self.COL_ID, Qt.Horizontal, "ID")
        self.setHeaderData(self.COL_TYPE, Qt.Horizontal, "Form Type")
        self.setHeaderData(self.COL_DATE, Qt.Horizontal, "Date")
        self.setHeaderData(self.COL_SUBJECT, Qt.Horizontal, "Subject/Title")
        self.setHeaderData(self.COL_STATUS, Qt.Horizontal, "Status")
        
    def set_forms(self, forms: List[Dict[str, Any]]):
        """
        Set the forms to display in the model.
        
        Args:
            forms: List of form dictionaries
        """
        # Clear existing data
        self.removeRows(0, self.rowCount())
        
        # Add forms to model
        for form in forms:
            self.add_form(form)
            
    def add_form(self, form: Dict[str, Any]):
        """
        Add a form to the model.
        
        Args:
            form: Form dictionary
        """
        # Create row
        row = self.rowCount()
        self.insertRow(row)
        
        # ID column
        id_item = QStandardItem(form.get("form_id", ""))
        # Store the full form data in the item's data
        id_item.setData(form, Qt.UserRole)
        self.setItem(row, self.COL_ID, id_item)
        
        # Type column
        type_item = QStandardItem(form.get("form_type", ""))
        self.setItem(row, self.COL_TYPE, type_item)
        
        # Date column
        date_str = ""
        date = form.get("date") or form.get("created_at")
        if date:
            if isinstance(date, str):
                # If date is already a string, use it directly
                date_str = date
            elif isinstance(date, (datetime.datetime, datetime.date)):
                # Format datetime/date objects
                date_str = date.strftime("%Y-%m-%d %H:%M")
                
        date_item = QStandardItem(date_str)
        self.setItem(row, self.COL_DATE, date_item)
        
        # Subject/Title column
        subject_str = ""
        # Different form types use different field names for the title/subject
        if "subject" in form:
            subject_str = form.get("subject", "")
        elif "incident_name" in form:
            subject_str = form.get("incident_name", "")
        elif "title" in form:
            subject_str = form.get("title", "")
            
        subject_item = QStandardItem(subject_str)
        self.setItem(row, self.COL_SUBJECT, subject_item)
        
        # Status column
        status_item = QStandardItem(form.get("state", "").capitalize())
        self.setItem(row, self.COL_STATUS, status_item)
        
    def get_form_at_row(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Get the form at the specified row.
        
        Args:
            row: Row index
            
        Returns:
            Form dictionary, or None if row is out of range
        """
        if row < 0 or row >= self.rowCount():
            return None
            
        # Get the form data from the ID column
        id_item = self.item(row, self.COL_ID)
        if id_item:
            return id_item.data(Qt.UserRole)
            
        return None


class FormFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy model for filtering and sorting forms.
    
    This model filters forms based on search text, form type, and status.
    """
    
    def __init__(self, parent=None):
        """Initialize the form filter proxy model."""
        super().__init__(parent)
        
        # Filter settings
        self._search_text = ""
        self._form_type_filter = ""
        self._status_filter = ""
        
    def set_search_text(self, text: str):
        """
        Set the search text filter.
        
        Args:
            text: Text to search for
        """
        self._search_text = text.lower()
        self.invalidateFilter()
        
    def set_form_type_filter(self, form_type: str):
        """
        Set the form type filter.
        
        Args:
            form_type: Form type to filter by, or empty string for all
        """
        self._form_type_filter = form_type
        self.invalidateFilter()
        
    def set_status_filter(self, status: str):
        """
        Set the status filter.
        
        Args:
            status: Status to filter by, or empty string for all
        """
        self._status_filter = status
        self.invalidateFilter()
        
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Determine if a row should be included in the filtered result.
        
        Args:
            source_row: Row in the source model
            source_parent: Parent index
            
        Returns:
            True if the row should be included, False otherwise
        """
        source_model = self.sourceModel()
        
        # Get form data
        form = source_model.get_form_at_row(source_row)
        if not form:
            return False
            
        # Check form type filter
        if self._form_type_filter:
            form_type = form.get("form_type", "")
            if form_type != self._form_type_filter:
                return False
                
        # Check status filter
        if self._status_filter:
            status = form.get("state", "")
            if status != self._status_filter.lower():
                return False
                
        # Check search text
        if self._search_text:
            # Search in various fields
            for field in ["form_id", "subject", "incident_name", "message", "title"]:
                if field in form:
                    field_value = str(form[field]).lower()
                    if self._search_text in field_value:
                        return True
                        
            # If search text not found in any field
            return False
            
        # Include the row if it passes all filters
        return True


class FormTabWidget(QWidget):
    """
    Widget for displaying and managing forms.
    
    This widget shows a list of forms with filtering and sorting capabilities,
    and allows the user to create new forms and open existing ones.
    """
    
    # Signal emitted when a form is opened
    form_opened = Signal(str, str)  # form_id, form_type
    
    def __init__(self, form_registry: FormModelRegistry, form_dao: FormDAO, parent=None):
        """
        Initialize the form tab widget.
        
        Args:
            form_registry: Form model registry
            form_dao: Form DAO for data access
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._form_registry = form_registry
        self._form_dao = form_dao
        
        # Initialize UI
        self._init_ui()
        
        # Load forms
        self._load_forms()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Controls container
        controls_layout = QHBoxLayout()
        
        # Search field
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search forms...")
        self._search_field.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self._search_field)
        
        # Clear search button
        clear_search_button = QToolButton()
        clear_search_button.setText("×")
        clear_search_button.setToolTip("Clear search")
        clear_search_button.clicked.connect(self._clear_search)
        search_layout.addWidget(clear_search_button)
        
        controls_layout.addLayout(search_layout, 1)  # Search takes more space
        
        # Form type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Form Type:"))
        self._type_combo = QComboBox()
        self._type_combo.addItem("All", "")
        self._type_combo.currentIndexChanged.connect(self._on_type_filter_changed)
        type_layout.addWidget(self._type_combo)
        controls_layout.addLayout(type_layout)
        
        # Status filter
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self._status_combo = QComboBox()
        self._status_combo.addItem("All", "")
        status_list = ["Draft", "Approved", "Transmitted", "Received", "Replied", "Archived"]
        for status in status_list:
            self._status_combo.addItem(status, status.lower())
        self._status_combo.currentIndexChanged.connect(self._on_status_filter_changed)
        status_layout.addWidget(self._status_combo)
        controls_layout.addLayout(status_layout)
        
        # Add controls layout to main layout
        main_layout.addLayout(controls_layout)
        
        # Table view
        self._table_view = QTableView()
        self._table_view.setSelectionBehavior(QTableView.SelectRows)
        self._table_view.setSelectionMode(QTableView.SingleSelection)
        self._table_view.setEditTriggers(QTableView.NoEditTriggers)
        self._table_view.setAlternatingRowColors(True)
        self._table_view.verticalHeader().setVisible(False)
        self._table_view.doubleClicked.connect(self._on_form_double_clicked)
        self._table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Configure table columns
        self._table_view.horizontalHeader().setStretchLastSection(False)
        self._table_view.horizontalHeader().setSectionResizeMode(FormTableModel.COL_ID, QHeaderView.ResizeToContents)
        self._table_view.horizontalHeader().setSectionResizeMode(FormTableModel.COL_TYPE, QHeaderView.ResizeToContents)
        self._table_view.horizontalHeader().setSectionResizeMode(FormTableModel.COL_DATE, QHeaderView.ResizeToContents)
        self._table_view.horizontalHeader().setSectionResizeMode(FormTableModel.COL_SUBJECT, QHeaderView.Stretch)
        self._table_view.horizontalHeader().setSectionResizeMode(FormTableModel.COL_STATUS, QHeaderView.ResizeToContents)
        
        # Create table model
        self._table_model = FormTableModel()
        
        # Create filter proxy model
        self._proxy_model = FormFilterProxyModel()
        self._proxy_model.setSourceModel(self._table_model)
        self._proxy_model.setDynamicSortFilter(True)
        self._proxy_model.setSortRole(Qt.DisplayRole)
        
        # Set model on table view
        self._table_view.setModel(self._proxy_model)
        
        # Sort by date, descending
        self._table_view.sortByColumn(FormTableModel.COL_DATE, Qt.DescendingOrder)
        
        main_layout.addWidget(self._table_view)
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._load_forms)
        buttons_layout.addWidget(refresh_button)
        
        # Spacer
        buttons_layout.addStretch()
        
        # New form button
        self._new_form_button = QPushButton("New Form")
        self._new_form_button.clicked.connect(self._on_new_form_clicked)
        buttons_layout.addWidget(self._new_form_button)
        
        # Open form button
        open_button = QPushButton("Open")
        open_button.clicked.connect(self._on_open_form_clicked)
        buttons_layout.addWidget(open_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Set style
        self.setStyleSheet("""
            QTableView {
                selection-background-color: #d0e0ff;
            }
        """)
        
    def _load_forms(self):
        """Load forms from the database."""
        try:
            # Get forms from DAO
            forms = self._form_dao.find_all(as_dict=True)
            
            # Set forms in table model
            self._table_model.set_forms(forms)
            
            # Populate form type filter
            self._populate_type_filter()
            
            # If no form selected, select the first one
            if not self._table_view.selectionModel().hasSelection() and self._proxy_model.rowCount() > 0:
                self._table_view.selectRow(0)
                
        except Exception as e:
            print(f"Error loading forms: {e}")
            
    def _populate_type_filter(self):
        """Populate the form type filter with available form types."""
        # Get all form types in the current data
        form_types = set()
        for row in range(self._table_model.rowCount()):
            form = self._table_model.get_form_at_row(row)
            if form and "form_type" in form:
                form_types.add(form.get("form_type"))
                
        # Add form types to combo box
        current_text = self._type_combo.currentText()
        
        # Clear combo box but keep the "All" item
        while self._type_combo.count() > 1:
            self._type_combo.removeItem(1)
            
        # Add form types
        for form_type in sorted(form_types):
            self._type_combo.addItem(form_type, form_type)
            
        # Restore selection if possible
        if current_text != "All":
            index = self._type_combo.findText(current_text)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
                
    def _on_search_text_changed(self, text: str):
        """
        Handle search text changes.
        
        Args:
            text: The new search text
        """
        self._proxy_model.set_search_text(text)
        
    def _clear_search(self):
        """Clear the search field."""
        self._search_field.setText("")
        
    def _on_type_filter_changed(self, index: int):
        """
        Handle form type filter changes.
        
        Args:
            index: The new index in the combo box
        """
        form_type = self._type_combo.itemData(index)
        self._proxy_model.set_form_type_filter(form_type)
        
    def _on_status_filter_changed(self, index: int):
        """
        Handle status filter changes.
        
        Args:
            index: The new index in the combo box
        """
        status = self._status_combo.itemData(index)
        self._proxy_model.set_status_filter(status)
        
    def _on_form_double_clicked(self, index: QModelIndex):
        """
        Handle form double click event.
        
        Args:
            index: The clicked index
        """
        # Get the form
        source_index = self._proxy_model.mapToSource(index)
        row = source_index.row()
        form = self._table_model.get_form_at_row(row)
        
        if form:
            # Emit signal with form ID and type
            self.form_opened.emit(form.get("form_id", ""), form.get("form_type", ""))
            
    def _on_open_form_clicked(self):
        """Handle open form button click."""
        # Get selected form
        selected_indexes = self._table_view.selectionModel().selectedRows()
        if not selected_indexes:
            return
            
        # Get the form
        source_index = self._proxy_model.mapToSource(selected_indexes[0])
        row = source_index.row()
        form = self._table_model.get_form_at_row(row)
        
        if form:
            # Emit signal with form ID and type
            self.form_opened.emit(form.get("form_id", ""), form.get("form_type", ""))
            
    def _on_new_form_clicked(self):
        """Handle new form button click."""
        # Create a menu with form types
        menu = QMenu(self)
        
        # Add an item for each registered form type
        form_types = self._form_registry.get_registered_types()
        for form_type in form_types:
            action = QAction(form_type, self)
            action.triggered.connect(lambda checked, f=form_type: self._create_new_form(f))
            menu.addAction(action)
            
        # Show the menu at the button position
        menu.exec_(self._new_form_button.mapToGlobal(self._new_form_button.rect().bottomLeft()))
        
    def _create_new_form(self, form_type: str):
        """
        Create a new form of the specified type.
        
        Args:
            form_type: Type of form to create
        """
        # Create a new form through the registry
        form = self._form_registry.create_form(form_type)
        
        if form:
            # Save the form to get an ID
            form_id = self._form_registry.save_form(form)
            
            # Reload forms to include the new one
            self._load_forms()
            
            # Open the form
            self.form_opened.emit(form_id, form_type)
            
    def _show_context_menu(self, position):
        """
        Show context menu for forms.
        
        Args:
            position: Position where the menu should be shown
        """
        # Get selected form
        selected_indexes = self._table_view.selectionModel().selectedRows()
        if not selected_indexes:
            return
            
        # Get the form
        source_index = self._proxy_model.mapToSource(selected_indexes[0])
        row = source_index.row()
        form = self._table_model.get_form_at_row(row)
        
        if not form:
            return
            
        # Create context menu
        menu = QMenu(self)
        
        # Open action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._on_open_form_clicked)
        menu.addAction(open_action)
        
        # Divider
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_form(form))
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec_(self._table_view.mapToGlobal(position))
        
    def _delete_form(self, form: Dict[str, Any]):
        """
        Delete a form.
        
        Args:
            form: Form to delete
        """
        # This is a placeholder - in a real application, show a confirmation dialog
        # and then delete the form
        form_id = form.get("form_id", "")
        if form_id:
            try:
                # Delete the form
                self._form_dao.delete(form_id)
                
                # Reload forms
                self._load_forms()
            except Exception as e:
                print(f"Error deleting form: {e}")
