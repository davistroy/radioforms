#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-214 Activity Log form view implementation.

This module provides a UI view for the ICS-214 Activity Log form.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QDateTimeEdit,
    QGroupBox, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView, QTimeEdit, QFrame,
    QDialog, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, Slot, QDateTime, QTime
from PySide6.QtGui import QFont

from radioforms.views.form_view_base import FormViewBase
from radioforms.models.ics214_form import ICS214Form, ActivityLogEntry


class ActivityEntryDialog(QDialog):
    """Dialog for adding or editing an activity log entry."""
    
    def __init__(self, activity_entry=None, parent=None):
        """
        Initialize the activity entry dialog.
        
        Args:
            activity_entry: ActivityLogEntry to edit, or None for a new entry
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.activity_entry = activity_entry
        self.setWindowTitle("Activity Entry")
        self.resize(400, 300)
        
        self._create_ui()
        
        # If editing an existing entry, populate the fields
        if activity_entry:
            self._populate_fields()
    
    def _create_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Time field
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_edit)
        
        # Activity field
        self.activity_edit = QTextEdit()
        form_layout.addRow("Activity:", self.activity_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def _populate_fields(self):
        """Populate fields with existing activity entry data."""
        if self.activity_entry:
            if self.activity_entry.time:
                qt_time = QTime.fromString(self.activity_entry.time.isoformat(), Qt.ISODate)
                self.time_edit.setTime(qt_time)
            
            self.activity_edit.setText(self.activity_entry.activity)
    
    def get_entry_data(self):
        """
        Get the activity entry data from the dialog.
        
        Returns:
            Tuple of (time, activity_text)
        """
        return (self.time_edit.time(), self.activity_edit.toPlainText())


class ICS214FormView(FormViewBase):
    """
    ICS-214 Activity Log form view.
    
    This view provides a UI for creating and editing ICS-214 Activity Log forms.
    """
    
    def __init__(self, form_model=None, parent=None):
        """
        Initialize the ICS-214 form view.
        
        Args:
            form_model: ICS214Form model instance to display and edit
            parent: Parent widget
        """
        # Initialize with the base class
        super().__init__(form_model, parent)
        
        # Set up form-specific UI elements
        self._create_form_ui()
        
        # Connect field signals
        self._connect_field_signals()
        
        # If a form model was provided, update the UI
        if form_model:
            self.update_ui_from_model()
    
    def _create_form_ui(self):
        """Create the ICS-214 form-specific UI elements."""
        # Set form title and subtitle
        self.form_title_label.setText("ICS-214: Activity Log")
        self.form_subtitle_label.setText("Used to record details of notable activities during incident operations")
        
        # Create form sections
        self._create_incident_section()
        self._create_activity_log_section()
        self._create_prepared_by_section()
        
        # Add sections to form layout
        self.form_layout.addWidget(self.incident_group)
        self.form_layout.addWidget(self.activity_log_group)
        self.form_layout.addWidget(self.prepared_by_group)
        self.form_layout.addStretch()
    
    def _create_incident_section(self):
        """Create the incident information section."""
        self.incident_group = QGroupBox("Incident Information")
        incident_layout = QFormLayout(self.incident_group)
        incident_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Incident name
        self.incident_name_edit = QLineEdit()
        incident_layout.addRow("Incident Name:", self.incident_name_edit)
        
        # Date prepared
        self.date_prepared_edit = QDateTimeEdit()
        self.date_prepared_edit.setCalendarPopup(True)
        self.date_prepared_edit.setDisplayFormat("MM/dd/yyyy")
        self.date_prepared_edit.setDateTime(QDateTime.currentDateTime())
        incident_layout.addRow("Date Prepared:", self.date_prepared_edit)
        
        # Time prepared
        self.time_prepared_edit = QTimeEdit()
        self.time_prepared_edit.setDisplayFormat("HH:mm")
        self.time_prepared_edit.setTime(QTime.currentTime())
        incident_layout.addRow("Time Prepared:", self.time_prepared_edit)
        
        # Team section
        incident_layout.addItem(QFormLayout.FullRow, QWidget())  # Add spacing
        
        # Team name
        self.team_name_edit = QLineEdit()
        incident_layout.addRow("Team Name:", self.team_name_edit)
        
        # ICS position
        self.ics_position_edit = QLineEdit()
        incident_layout.addRow("ICS Position:", self.ics_position_edit)
        
        # Home agency
        self.home_agency_edit = QLineEdit()
        incident_layout.addRow("Home Agency:", self.home_agency_edit)
    
    def _create_activity_log_section(self):
        """Create the activity log section."""
        self.activity_log_group = QGroupBox("Activity Log")
        activity_layout = QVBoxLayout(self.activity_log_group)
        
        # Create table for activity entries
        self.activity_table = QTableWidget(0, 2)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Activity"])
        self.activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.activity_table.verticalHeader().setVisible(True)
        self.activity_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.activity_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Add buttons for activity management
        button_layout = QHBoxLayout()
        
        self.add_activity_button = QPushButton("Add Activity")
        self.edit_activity_button = QPushButton("Edit Activity")
        self.remove_activity_button = QPushButton("Remove Activity")
        
        button_layout.addWidget(self.add_activity_button)
        button_layout.addWidget(self.edit_activity_button)
        button_layout.addWidget(self.remove_activity_button)
        button_layout.addStretch()
        
        # Connect activity button signals
        self.add_activity_button.clicked.connect(self._on_add_activity)
        self.edit_activity_button.clicked.connect(self._on_edit_activity)
        self.remove_activity_button.clicked.connect(self._on_remove_activity)
        
        # Add widgets to layout
        activity_layout.addWidget(self.activity_table)
        activity_layout.addLayout(button_layout)
    
    def _create_prepared_by_section(self):
        """Create the prepared by section."""
        self.prepared_by_group = QGroupBox("Prepared By")
        prepared_layout = QFormLayout(self.prepared_by_group)
        prepared_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Name
        self.prepared_name_edit = QLineEdit()
        prepared_layout.addRow("Name:", self.prepared_name_edit)
        
        # Position
        self.prepared_position_edit = QLineEdit()
        prepared_layout.addRow("Position/Title:", self.prepared_position_edit)
        
        # Signature
        self.prepared_signature_edit = QLineEdit()
        prepared_layout.addRow("Signature:", self.prepared_signature_edit)
    
    def _connect_field_signals(self):
        """Connect signals from UI fields to track changes."""
        # Connect text changed signals for all editable fields
        self.incident_name_edit.textChanged.connect(lambda: self._field_modified("incident_name"))
        self.date_prepared_edit.dateTimeChanged.connect(lambda: self._field_modified("date_prepared"))
        self.time_prepared_edit.timeChanged.connect(lambda: self._field_modified("time_prepared"))
        
        self.team_name_edit.textChanged.connect(lambda: self._field_modified("team_name"))
        self.ics_position_edit.textChanged.connect(lambda: self._field_modified("ics_position"))
        self.home_agency_edit.textChanged.connect(lambda: self._field_modified("home_agency"))
        
        self.prepared_name_edit.textChanged.connect(lambda: self._field_modified("prepared_name"))
        self.prepared_position_edit.textChanged.connect(lambda: self._field_modified("prepared_position"))
        self.prepared_signature_edit.textChanged.connect(lambda: self._field_modified("prepared_signature"))
    
    def _field_modified(self, field_name):
        """
        Handle field modifications.
        
        Args:
            field_name: Name of the modified field
        """
        self._modified = True
        self.form_modified.emit()
    
    def _connect_form_signals(self):
        """Connect signals from the form model to view update handlers."""
        if self._form_model and isinstance(self._form_model, ICS214Form):
            # Connect to the form's property change signals
            self._form_model.add_observer(self._on_form_field_changed)
    
    def update_ui_from_model(self):
        """Update UI fields from the form model's data."""
        if not self._form_model or not isinstance(self._form_model, ICS214Form):
            return
        
        # Update incident information
        self.incident_name_edit.setText(self._form_model.incident_name)
        
        if self._form_model.date_prepared:
            qt_date = QDateTime.fromString(self._form_model.date_prepared.isoformat(), Qt.ISODate)
            self.date_prepared_edit.setDateTime(qt_date)
        
        if self._form_model.time_prepared:
            qt_time = QTime.fromString(self._form_model.time_prepared.isoformat(), Qt.ISODate)
            self.time_prepared_edit.setTime(qt_time)
        
        # Update team information
        self.team_name_edit.setText(self._form_model.team_name)
        self.ics_position_edit.setText(self._form_model.ics_position)
        self.home_agency_edit.setText(self._form_model.home_agency)
        
        # Update prepared by information
        self.prepared_name_edit.setText(self._form_model.prepared_name)
        self.prepared_position_edit.setText(self._form_model.prepared_position)
        self.prepared_signature_edit.setText(self._form_model.prepared_signature)
        
        # Update activity log table
        self._update_activity_table()
        
        # Reset modification flag
        self._modified = False
    
    def _update_activity_table(self):
        """Update the activity table from the model."""
        if not self._form_model:
            return
            
        activities = self._form_model.activity_log
        
        # Clear existing rows
        self.activity_table.setRowCount(0)
        
        # Add rows for each activity
        for i, activity in enumerate(activities):
            self.activity_table.insertRow(i)
            
            # Time column
            time_item = QTableWidgetItem()
            if activity.time:
                time_text = activity.time.strftime("%H:%M")
                time_item.setText(time_text)
            self.activity_table.setItem(i, 0, time_item)
            
            # Activity column
            activity_item = QTableWidgetItem(activity.activity)
            self.activity_table.setItem(i, 1, activity_item)
            
            # Store the entry_id as item data
            time_item.setData(Qt.UserRole, activity.entry_id)
            activity_item.setData(Qt.UserRole, activity.entry_id)
    
    def update_model_from_ui(self):
        """Update the form model from UI field values."""
        if not self._form_model or not isinstance(self._form_model, ICS214Form):
            return
        
        # Update incident information
        self._form_model.incident_name = self.incident_name_edit.text()
        self._form_model.date_prepared = self.date_prepared_edit.dateTime().toPython()
        
        # Convert QTime to Python time
        time_prepared = self.time_prepared_edit.time().toPython()
        self._form_model.time_prepared = time_prepared
        
        # Update team information
        self._form_model.team_name = self.team_name_edit.text()
        self._form_model.ics_position = self.ics_position_edit.text()
        self._form_model.home_agency = self.home_agency_edit.text()
        
        # Update prepared by information
        self._form_model.prepared_name = self.prepared_name_edit.text()
        self._form_model.prepared_position = self.prepared_position_edit.text()
        self._form_model.prepared_signature = self.prepared_signature_edit.text()
        
        # Note: Activity log is updated directly through add/edit/remove methods
    
    def _update_read_only_state(self):
        """Update the UI elements based on the read-only state."""
        # Call base class implementation
        super()._update_read_only_state()
        
        # Update form-specific fields
        self.incident_name_edit.setReadOnly(self._read_only)
        self.date_prepared_edit.setReadOnly(self._read_only)
        self.time_prepared_edit.setReadOnly(self._read_only)
        
        self.team_name_edit.setReadOnly(self._read_only)
        self.ics_position_edit.setReadOnly(self._read_only)
        self.home_agency_edit.setReadOnly(self._read_only)
        
        self.prepared_name_edit.setReadOnly(self._read_only)
        self.prepared_position_edit.setReadOnly(self._read_only)
        self.prepared_signature_edit.setReadOnly(self._read_only)
        
        # Update activity buttons
        self.add_activity_button.setEnabled(not self._read_only)
        self.edit_activity_button.setEnabled(not self._read_only)
        self.remove_activity_button.setEnabled(not self._read_only)
    
    @Slot()
    def _on_add_activity(self):
        """Handle adding a new activity."""
        dialog = ActivityEntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            time, activity_text = dialog.get_entry_data()
            
            # Convert QTime to Python time
            python_time = time.toPython()
            
            # Add to the model
            if self._form_model:
                self._form_model.add_activity(python_time, activity_text)
                self._update_activity_table()
                self._modified = True
                self.form_modified.emit()
    
    @Slot()
    def _on_edit_activity(self):
        """Handle editing the selected activity."""
        # Get the selected row
        selected_rows = self.activity_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "Edit Activity", "Please select an activity to edit.")
            return
            
        # Get the entry ID from the selected row
        selected_row = selected_rows[0].row()
        entry_id = self.activity_table.item(selected_row, 0).data(Qt.UserRole)
        
        # Find the corresponding activity entry
        activity_entry = None
        for entry in self._form_model.activity_log:
            if entry.entry_id == entry_id:
                activity_entry = entry
                break
                
        if not activity_entry:
            return
            
        # Create and show the dialog
        dialog = ActivityEntryDialog(activity_entry, parent=self)
        if dialog.exec() == QDialog.Accepted:
            time, activity_text = dialog.get_entry_data()
            
            # Convert QTime to Python time
            python_time = time.toPython()
            
            # Update the model
            if self._form_model:
                self._form_model.update_activity(entry_id, python_time, activity_text)
                self._update_activity_table()
                self._modified = True
                self.form_modified.emit()
    
    @Slot()
    def _on_remove_activity(self):
        """Handle removing the selected activity."""
        # Get the selected row
        selected_rows = self.activity_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "Remove Activity", "Please select an activity to remove.")
            return
            
        # Confirm deletion
        response = QMessageBox.question(
            self, "Remove Activity", 
            "Are you sure you want to remove this activity?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if response == QMessageBox.No:
            return
            
        # Get the entry ID from the selected row
        selected_row = selected_rows[0].row()
        entry_id = self.activity_table.item(selected_row, 0).data(Qt.UserRole)
        
        # Remove from the model
        if self._form_model:
            self._form_model.remove_activity(entry_id)
            self._update_activity_table()
            self._modified = True
            self.form_modified.emit()
