#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-214 Activity Log Form Editor.

This module provides a form editor for ICS-214 Activity Log forms,
implementing the form editor architecture with the enhanced ICS-214 form model.
"""

import datetime
from typing import Dict, Any, List, Optional, Set, Union, Callable

from PySide6.QtCore import Qt, Signal, Slot, QObject, Property, QTimer, QModelIndex, QSortFilterProxyModel
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QCheckBox, QComboBox, QDateTimeEdit,
    QGridLayout, QScrollArea, QFrame, QSplitter, QTableView, 
    QHeaderView, QSpacerItem, QSizePolicy, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QMessageBox, QTabWidget
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

from radioforms.models.enhanced_ics214_form import EnhancedICS214Form, ActivityLogEntry, FormState
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.views.form_editor_base import (
    FormEditorContainer, FormField, TextField, TextAreaField, 
    DateTimeField, ChoiceField, CheckboxField, ValidationSummary
)


class ActivityLogEntryDialog(QDialog):
    """
    Dialog for adding/editing activity log entries.
    """
    
    def __init__(self, parent=None, entry=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            entry: Existing entry to edit (None for new entry)
        """
        super().__init__(parent)
        
        self._entry = entry or ActivityLogEntry()
        
        self._init_ui()
        
        # Set initial values if editing existing entry
        if entry:
            self._time_field.setTime(entry.time)
            self._activity_field.setPlainText(entry.activity)
            self._notable_checkbox.setChecked(entry.notable)
            
    def _init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Activity Log Entry")
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Time field
        self._time_field = QDateTimeEdit()
        self._time_field.setDisplayFormat("HH:mm")
        self._time_field.setTime(datetime.datetime.now().time())
        form_layout.addRow("Time:", self._time_field)
        
        # Activity field
        self._activity_field = QTextEdit()
        form_layout.addRow("Activity:", self._activity_field)
        
        # Notable checkbox
        self._notable_checkbox = QCheckBox("Mark as notable/significant")
        form_layout.addRow("", self._notable_checkbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_entry(self) -> ActivityLogEntry:
        """
        Get the activity log entry from the dialog.
        
        Returns:
            The activity log entry
        """
        # Update entry with values from UI
        time = self._time_field.time().toPython()
        self._entry.time = time
        self._entry.activity = self._activity_field.toPlainText()
        self._entry.notable = self._notable_checkbox.isChecked()
        
        return self._entry


class PersonnelDialog(QDialog):
    """
    Dialog for adding/editing personnel entries.
    """
    
    def __init__(self, parent=None, person=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            person: Existing person to edit (None for new person)
        """
        super().__init__(parent)
        
        self._person = person or {"name": "", "position": "", "agency": ""}
        
        self._init_ui()
        
        # Set initial values if editing existing person
        if person:
            self._name_field.setText(person.get("name", ""))
            self._position_field.setText(person.get("position", ""))
            self._agency_field.setText(person.get("agency", ""))
            
    def _init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Personnel Entry")
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self._name_field = QLineEdit()
        form_layout.addRow("Name:", self._name_field)
        
        # Position field
        self._position_field = QLineEdit()
        form_layout.addRow("ICS Position:", self._position_field)
        
        # Agency field
        self._agency_field = QLineEdit()
        form_layout.addRow("Home Agency:", self._agency_field)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_person(self) -> Dict[str, str]:
        """
        Get the personnel entry from the dialog.
        
        Returns:
            The personnel entry
        """
        # Update person with values from UI
        self._person["name"] = self._name_field.text()
        self._person["position"] = self._position_field.text()
        self._person["agency"] = self._agency_field.text()
        
        return self._person


class ActivityLogEntryModel(QStandardItemModel):
    """
    Model for activity log entries in a table view.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(0, 3, parent)
        
        # Set headers
        self.setHeaderData(0, Qt.Horizontal, "Time")
        self.setHeaderData(1, Qt.Horizontal, "Activity")
        self.setHeaderData(2, Qt.Horizontal, "Notable")
        
        self._entries = []
        
    def set_entries(self, entries: List[ActivityLogEntry]):
        """
        Set the activity log entries.
        
        Args:
            entries: List of activity log entries
        """
        self._entries = entries
        self.update_model()
        
    def get_entries(self) -> List[ActivityLogEntry]:
        """
        Get the activity log entries.
        
        Returns:
            List of activity log entries
        """
        return self._entries
        
    def update_model(self):
        """Update the model with the current entries."""
        self.removeRows(0, self.rowCount())
        
        for entry in self._entries:
            self.append_entry(entry)
            
    def append_entry(self, entry: ActivityLogEntry):
        """
        Append an entry to the model.
        
        Args:
            entry: Activity log entry to append
        """
        row = self.rowCount()
        self.insertRow(row)
        
        # Set time
        time_item = QStandardItem(entry.time.strftime("%H:%M") if entry.time else "")
        time_item.setData(entry, Qt.UserRole)
        self.setItem(row, 0, time_item)
        
        # Set activity
        activity_text = entry.activity
        if len(activity_text) > 50:
            activity_text = activity_text[:47] + "..."
        activity_item = QStandardItem(activity_text)
        self.setItem(row, 1, activity_item)
        
        # Set notable
        notable_item = QStandardItem("✓" if entry.notable else "")
        notable_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 2, notable_item)
        
    def get_entry_at_row(self, row: int) -> Optional[ActivityLogEntry]:
        """
        Get the activity log entry at the specified row.
        
        Args:
            row: Row index
            
        Returns:
            Activity log entry, or None if not found
        """
        if row < 0 or row >= self.rowCount():
            return None
            
        item = self.item(row, 0)
        if item:
            return item.data(Qt.UserRole)
            
        return None


class PersonnelModel(QStandardItemModel):
    """
    Model for personnel entries in a table view.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(0, 3, parent)
        
        # Set headers
        self.setHeaderData(0, Qt.Horizontal, "Name")
        self.setHeaderData(1, Qt.Horizontal, "ICS Position")
        self.setHeaderData(2, Qt.Horizontal, "Home Agency")
        
        self._personnel = []
        
    def set_personnel(self, personnel: List[Dict[str, str]]):
        """
        Set the personnel entries.
        
        Args:
            personnel: List of personnel entries
        """
        self._personnel = personnel
        self.update_model()
        
    def get_personnel(self) -> List[Dict[str, str]]:
        """
        Get the personnel entries.
        
        Returns:
            List of personnel entries
        """
        return self._personnel
        
    def update_model(self):
        """Update the model with the current personnel."""
        self.removeRows(0, self.rowCount())
        
        for person in self._personnel:
            self.append_person(person)
            
    def append_person(self, person: Dict[str, str]):
        """
        Append a person to the model.
        
        Args:
            person: Personnel entry to append
        """
        row = self.rowCount()
        self.insertRow(row)
        
        # Set name
        name_item = QStandardItem(person.get("name", ""))
        name_item.setData(person, Qt.UserRole)
        self.setItem(row, 0, name_item)
        
        # Set position
        position_item = QStandardItem(person.get("position", ""))
        self.setItem(row, 1, position_item)
        
        # Set agency
        agency_item = QStandardItem(person.get("agency", ""))
        self.setItem(row, 2, agency_item)
        
    def get_person_at_row(self, row: int) -> Optional[Dict[str, str]]:
        """
        Get the personnel entry at the specified row.
        
        Args:
            row: Row index
            
        Returns:
            Personnel entry, or None if not found
        """
        if row < 0 or row >= self.rowCount():
            return None
            
        item = self.item(row, 0)
        if item:
            return item.data(Qt.UserRole)
            
        return None


class ICS214FormEditor(FormEditorContainer):
    """
    Form editor for ICS-214 Activity Log forms.
    
    This class extends FormEditorContainer to provide a specialized
    editor for ICS-214 Activity Log forms.
    """
    
    def __init__(self, form_registry: FormModelRegistry, 
                form: Optional[EnhancedICS214Form] = None, 
                form_id: Optional[str] = None, 
                parent: Optional[QWidget] = None):
        """
        Initialize the ICS-214 form editor.
        
        Args:
            form_registry: FormModelRegistry instance
            form: Existing form to edit
            form_id: ID of form to load
            parent: Parent widget
        """
        super().__init__(form_registry, form, form_id, "ICS-214", parent)
        
    def _get_form_title(self, form: EnhancedICS214Form) -> str:
        """
        Get the title for the form.
        
        Args:
            form: The form to get the title for
            
        Returns:
            The form title
        """
        return "ICS-214 Activity Log"
        
    def _create_form_body(self, form: EnhancedICS214Form) -> QWidget:
        """
        Create the form body widget.
        
        Args:
            form: The form to create the body for
            
        Returns:
            The form body widget
        """
        # Clear existing fields
        self._fields = {}
        
        # Main widget
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Tabs
        tab_widget = QTabWidget()
        
        # Tab 1: Incident Information
        incident_tab = self._create_incident_tab(form)
        tab_widget.addTab(incident_tab, "Incident Information")
        
        # Tab 2: Activity Log
        activity_tab = self._create_activity_tab(form)
        tab_widget.addTab(activity_tab, "Activity Log")
        
        # Tab 3: Personnel
        personnel_tab = self._create_personnel_tab(form)
        tab_widget.addTab(personnel_tab, "Personnel")
        
        main_layout.addWidget(tab_widget)
        
        # Bind fields to form
        self.bind_fields_to_form()
        
        return widget
        
    def _create_incident_tab(self, form: EnhancedICS214Form) -> QWidget:
        """
        Create the incident information tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Incident information section
        incident_group = QGroupBox("Incident Information")
        incident_layout = QFormLayout()
        incident_group.setLayout(incident_layout)
        
        # Incident name
        incident_name_field = TextField("incident_name", "Incident Name", required=True)
        self.register_field(incident_name_field)
        incident_layout.addRow("Incident Name:", incident_name_field)
        
        # Incident number
        incident_number_field = TextField("incident_number", "Incident Number")
        self.register_field(incident_number_field)
        incident_layout.addRow("Incident Number:", incident_number_field)
        
        # Operational period
        operational_period_field = TextField("operational_period", "Operational Period")
        self.register_field(operational_period_field)
        incident_layout.addRow("Operational Period:", operational_period_field)
        
        main_layout.addWidget(incident_group)
        
        # Team information section
        team_group = QGroupBox("Team Information")
        team_layout = QFormLayout()
        team_group.setLayout(team_layout)
        
        # Team name
        team_name_field = TextField("team_name", "Team/Unit Name", required=True)
        self.register_field(team_name_field)
        team_layout.addRow("Team/Unit Name:", team_name_field)
        
        # ICS position
        ics_position_field = TextField("ics_position", "ICS Position")
        self.register_field(ics_position_field)
        team_layout.addRow("ICS Position:", ics_position_field)
        
        # Home agency
        home_agency_field = TextField("home_agency", "Home Agency")
        self.register_field(home_agency_field)
        team_layout.addRow("Home Agency:", home_agency_field)
        
        main_layout.addWidget(team_group)
        
        main_layout.addStretch()
        
        return widget
        
    def _create_activity_tab(self, form: EnhancedICS214Form) -> QWidget:
        """
        Create the activity log tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Activity log table
        table_group = QGroupBox("Activity Log")
        table_layout = QVBoxLayout()
        table_group.setLayout(table_layout)
        
        # Instruction label
        instruction_label = QLabel("Record significant events, actions taken, and decisions made.")
        table_layout.addWidget(instruction_label)
        
        # Create table view
        self._activity_table = QTableView()
        self._activity_table.setSelectionBehavior(QTableView.SelectRows)
        self._activity_table.setSelectionMode(QTableView.SingleSelection)
        
        # Configure table columns
        self._activity_table.horizontalHeader().setStretchLastSection(False)
        self._activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # Create model
        self._activity_model = ActivityLogEntryModel()
        self._activity_model.set_entries(form.activity_log)
        self._activity_table.setModel(self._activity_model)
        
        table_layout.addWidget(self._activity_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Entry")
        add_button.clicked.connect(self._add_activity_entry)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Entry")
        edit_button.clicked.connect(self._edit_activity_entry)
        button_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Entry")
        remove_button.clicked.connect(self._remove_activity_entry)
        button_layout.addWidget(remove_button)
        
        button_layout.addStretch()
        
        table_layout.addLayout(button_layout)
        
        main_layout.addWidget(table_group)
        
        return widget
        
    def _create_personnel_tab(self, form: EnhancedICS214Form) -> QWidget:
        """
        Create the personnel tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Personnel table
        table_group = QGroupBox("Personnel Assigned")
        table_layout = QVBoxLayout()
        table_group.setLayout(table_layout)
        
        # Instruction label
        instruction_label = QLabel("List personnel assigned to this unit for this operational period.")
        table_layout.addWidget(instruction_label)
        
        # Create table view
        self._personnel_table = QTableView()
        self._personnel_table.setSelectionBehavior(QTableView.SelectRows)
        self._personnel_table.setSelectionMode(QTableView.SingleSelection)
        
        # Configure table columns
        self._personnel_table.horizontalHeader().setStretchLastSection(False)
        self._personnel_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._personnel_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._personnel_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Create model
        self._personnel_model = PersonnelModel()
        self._personnel_model.set_personnel(form.personnel)
        self._personnel_table.setModel(self._personnel_model)
        
        table_layout.addWidget(self._personnel_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Person")
        add_button.clicked.connect(self._add_personnel_entry)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Person")
        edit_button.clicked.connect(self._edit_personnel_entry)
        button_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Person")
        remove_button.clicked.connect(self._remove_personnel_entry)
        button_layout.addWidget(remove_button)
        
        button_layout.addStretch()
        
        table_layout.addLayout(button_layout)
        
        main_layout.addWidget(table_group)
        
        # Prepared by section
        prepared_group = QGroupBox("Prepared By")
        prepared_layout = QFormLayout()
        prepared_group.setLayout(prepared_layout)
        
        # Preparer name
        prepared_name_field = TextField("prepared_name", "Name")
        self.register_field(prepared_name_field)
        prepared_layout.addRow("Name:", prepared_name_field)
        
        # Preparer position
        prepared_position_field = TextField("prepared_position", "Position")
        self.register_field(prepared_position_field)
        prepared_layout.addRow("Position:", prepared_position_field)
        
        # Preparer signature (when finalized)
        if form.state == FormState.FINALIZED or form.state == FormState.REVIEWED:
            prepared_signature_label = QLabel(f"Signature: {form.prepared_signature}")
            prepared_layout.addRow("", prepared_signature_label)
            
            prepared_date_label = QLabel(
                form.prepared_date.strftime("%Y-%m-%d %H:%M") if form.prepared_date else ""
            )
            prepared_layout.addRow("Date/Time:", prepared_date_label)
            
        main_layout.addWidget(prepared_group)
        
        # Reviewer info (when reviewed)
        if form.state == FormState.REVIEWED:
            reviewer_group = QGroupBox("Reviewed By")
            reviewer_layout = QFormLayout()
            reviewer_group.setLayout(reviewer_layout)
            
            reviewer_name_label = QLabel(form.reviewer_name)
            reviewer_layout.addRow("Name:", reviewer_name_label)
            
            reviewer_position_label = QLabel(form.reviewer_position)
            reviewer_layout.addRow("Position:", reviewer_position_label)
            
            reviewer_signature_label = QLabel(f"Signature: {form.reviewer_signature}")
            reviewer_layout.addRow("", reviewer_signature_label)
            
            reviewer_date_label = QLabel(
                form.reviewer_date.strftime("%Y-%m-%d %H:%M") if form.reviewer_date else ""
            )
            reviewer_layout.addRow("Date/Time:", reviewer_date_label)
            
            main_layout.addWidget(reviewer_group)
            
        return widget
        
    def _add_activity_entry(self):
        """Add a new activity log entry."""
        dialog = ActivityLogEntryDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            entry = dialog.get_entry()
            
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Add entry to form
                form.add_activity(
                    time=entry.time,
                    activity=entry.activity,
                    notable=entry.notable
                )
                
                # Update model
                self._activity_model.set_entries(form.activity_log)
                
    def _edit_activity_entry(self):
        """Edit the selected activity log entry."""
        # Get selected row
        selection = self._activity_table.selectionModel()
        if not selection.hasSelection():
            return
            
        row = selection.selectedRows()[0].row()
        entry = self._activity_model.get_entry_at_row(row)
        
        if not entry:
            return
            
        # Show dialog
        dialog = ActivityLogEntryDialog(self, entry)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            updated_entry = dialog.get_entry()
            
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Update entry in form
                form.update_activity(
                    entry_id=updated_entry.entry_id,
                    time=updated_entry.time,
                    activity=updated_entry.activity,
                    notable=updated_entry.notable
                )
                
                # Update model
                self._activity_model.set_entries(form.activity_log)
                
    def _remove_activity_entry(self):
        """Remove the selected activity log entry."""
        # Get selected row
        selection = self._activity_table.selectionModel()
        if not selection.hasSelection():
            return
            
        row = selection.selectedRows()[0].row()
        entry = self._activity_model.get_entry_at_row(row)
        
        if not entry:
            return
            
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Remove Entry",
            "Are you sure you want to remove this activity log entry?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Remove entry from form
                form.remove_activity(entry.entry_id)
                
                # Update model
                self._activity_model.set_entries(form.activity_log)
                
    def _add_personnel_entry(self):
        """Add a new personnel entry."""
        dialog = PersonnelDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            person = dialog.get_person()
            
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Add person to form
                form.add_personnel(
                    name=person.get("name", ""),
                    position=person.get("position", ""),
                    agency=person.get("agency", "")
                )
                
                # Update model
                self._personnel_model.set_personnel(form.personnel)
                
    def _edit_personnel_entry(self):
        """Edit the selected personnel entry."""
        # Get selected row
        selection = self._personnel_table.selectionModel()
        if not selection.hasSelection():
            return
            
        row = selection.selectedRows()[0].row()
        person = self._personnel_model.get_person_at_row(row)
        
        if not person:
            return
            
        # Show dialog
        dialog = PersonnelDialog(self, person)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            updated_person = dialog.get_person()
            
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Update person in form
                form.update_personnel(
                    index=row,
                    name=updated_person.get("name", ""),
                    position=updated_person.get("position", ""),
                    agency=updated_person.get("agency", "")
                )
                
                # Update model
                self._personnel_model.set_personnel(form.personnel)
                
    def _remove_personnel_entry(self):
        """Remove the selected personnel entry."""
        # Get selected row
        selection = self._personnel_table.selectionModel()
        if not selection.hasSelection():
            return
            
        row = selection.selectedRows()[0].row()
        person = self._personnel_model.get_person_at_row(row)
        
        if not person:
            return
            
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Remove Person",
            "Are you sure you want to remove this personnel entry?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Get the form
            form = self._form
            if form and isinstance(form, EnhancedICS214Form):
                # Remove person from form
                form.remove_personnel(row)
                
                # Update model
                self._personnel_model.set_personnel(form.personnel)
                
    def _on_finalize(self):
        """Handle finalize button click."""
        # Create custom dialog for collecting finalizer information
        dialog = QDialog(self)
        dialog.setWindowTitle("Finalize Activity Log")
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        form_layout = QFormLayout()
        
        name_field = QLineEdit()
        if self._form.prepared_name:
            name_field.setText(self._form.prepared_name)
        form_layout.addRow("Preparer Name:", name_field)
        
        position_field = QLineEdit()
        if self._form.prepared_position:
            position_field.setText(self._form.prepared_position)
        form_layout.addRow("Position/Title:", position_field)
        
        signature_field = QLineEdit()
        form_layout.addRow("Signature:", signature_field)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            name = name_field.text()
            position = position_field.text()
            signature = signature_field.text()
            
            if not name or not position or not signature:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide name, position, and signature to finalize the form."
                )
                return
                
            # Call finalize method on form
            if hasattr(self._form, 'finalize'):
                self._form.finalize(name, position, signature)
                self._update_state_after_transition()
                
    def _on_review(self):
        """Handle review button click."""
        # Create custom dialog for collecting reviewer information
        dialog = QDialog(self)
        dialog.setWindowTitle("Review Activity Log")
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        form_layout = QFormLayout()
        
        name_field = QLineEdit()
        form_layout.addRow("Reviewer Name:", name_field)
        
        position_field = QLineEdit()
        form_layout.addRow("Position/Title:", position_field)
        
        signature_field = QLineEdit()
        form_layout.addRow("Signature:", signature_field)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            name = name_field.text()
            position = position_field.text()
            signature = signature_field.text()
            
            if not name or not position or not signature:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide name, position, and signature to review the form."
                )
                return
                
            # Call review method on form
            if hasattr(self._form, 'review'):
                self._form.review(name, position, signature)
                self._update_state_after_transition()
                
    def _on_state_changed(self, state_id: str, display_text: str):
        """
        Handle form state changes.
        
        Args:
            state_id: ID of the new state
            display_text: Display text for the new state
        """
        # Reload the form to update UI based on new state
        if self._form:
            self.set_form(self._form)
