"""ICS-213 General Message form widget.

This module provides a PySide6 widget for creating and editing ICS-213 forms
following CLAUDE.md principles: simple first, incremental enhancement.
"""

import logging
from datetime import datetime
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QPushButton, QLabel,
    QGroupBox, QScrollArea, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..forms.ics213 import ICS213Form, ICS213Data, Person, Priority, FormStatus
from ..services.form_service import FormService
from ..database.connection import DatabaseError


logger = logging.getLogger(__name__)


class PersonWidget(QWidget):
    """Widget for entering person information (name, position, etc.)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the person widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create form layout for person fields
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter full name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Position field
        self.position_edit = QLineEdit()
        self.position_edit.setPlaceholderText("Enter position/title")
        form_layout.addRow("Position:", self.position_edit)
        
        # Optional signature field
        self.signature_edit = QLineEdit()
        self.signature_edit.setPlaceholderText("Enter signature (optional)")
        form_layout.addRow("Signature:", self.signature_edit)
        
        # Optional contact info field
        self.contact_edit = QLineEdit()
        self.contact_edit.setPlaceholderText("Enter contact info (optional)")
        form_layout.addRow("Contact:", self.contact_edit)
        
        layout.addLayout(form_layout)
    
    def get_person(self) -> Person:
        """Get Person object from widget fields."""
        return Person(
            name=self.name_edit.text().strip(),
            position=self.position_edit.text().strip(),
            signature=self.signature_edit.text().strip(),
            contact_info=self.contact_edit.text().strip()
        )
    
    def set_person(self, person: Person):
        """Set widget fields from Person object."""
        self.name_edit.setText(person.name)
        self.position_edit.setText(person.position)
        self.signature_edit.setText(person.signature)
        self.contact_edit.setText(person.contact_info)
    
    def clear(self):
        """Clear all fields."""
        self.name_edit.clear()
        self.position_edit.clear()
        self.signature_edit.clear()
        self.contact_edit.clear()
    
    def is_complete(self) -> bool:
        """Check if person has required minimum information."""
        return bool(self.name_edit.text().strip() and self.position_edit.text().strip())


class ICS213Widget(QWidget):
    """Main widget for ICS-213 General Message form."""
    
    # Signals
    form_changed = Signal()
    form_saved = Signal(int)  # Emits form ID when saved
    form_loaded = Signal(int)  # Emits form ID when loaded
    
    def __init__(self, form_service: Optional[FormService] = None, parent=None):
        super().__init__(parent)
        self.form: Optional[ICS213Form] = None
        self.form_service = form_service
        self.current_form_id: Optional[int] = None
        self.is_modified = False
        
        self.setup_ui()
        self.connect_signals()
        self.new_form()
        logger.debug("ICS213Widget initialized")
    
    def setup_ui(self):
        """Set up the main UI layout."""
        main_layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Form widget
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Sections
        form_layout.addWidget(self.create_header_section())
        form_layout.addWidget(self.create_message_section())
        form_layout.addWidget(self.create_reply_section())
        
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)
        
        # Button bar
        main_layout.addLayout(self.create_button_bar())
        
        # Status
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def create_header_section(self) -> QGroupBox:
        """Create the header section."""
        group = QGroupBox("Message Header")
        layout = QGridLayout(group)
        
        # Incident name
        layout.addWidget(QLabel("Incident Name:"), 0, 0)
        self.incident_name_edit = QLineEdit()
        layout.addWidget(self.incident_name_edit, 0, 1, 1, 3)
        
        # To/From
        layout.addWidget(QLabel("To:"), 1, 0)
        self.to_widget = PersonWidget()
        layout.addWidget(self.to_widget, 1, 1, 1, 3)
        
        layout.addWidget(QLabel("From:"), 2, 0)
        self.from_widget = PersonWidget()
        layout.addWidget(self.from_widget, 2, 1, 1, 3)
        
        # Subject
        layout.addWidget(QLabel("Subject:"), 3, 0)
        self.subject_edit = QLineEdit()
        layout.addWidget(self.subject_edit, 3, 1, 1, 3)
        
        # Date/Time
        layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.now().strftime("%Y-%m-%d"))
        layout.addWidget(self.date_edit, 4, 1)
        
        layout.addWidget(QLabel("Time:"), 4, 2)
        self.time_edit = QLineEdit()
        self.time_edit.setText(datetime.now().strftime("%H:%M"))
        layout.addWidget(self.time_edit, 4, 3)
        
        # Priority
        layout.addWidget(QLabel("Priority:"), 5, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Routine", "Urgent", "Immediate"])
        layout.addWidget(self.priority_combo, 5, 1)
        
        self.reply_requested_check = QCheckBox("Reply Requested")
        layout.addWidget(self.reply_requested_check, 5, 2, 1, 2)
        
        return group
    
    def create_message_section(self) -> QGroupBox:
        """Create the message section."""
        group = QGroupBox("Message")
        layout = QVBoxLayout(group)
        
        # Message content
        layout.addWidget(QLabel("Message Content:"))
        self.message_edit = QTextEdit()
        self.message_edit.setMinimumHeight(150)
        layout.addWidget(self.message_edit)
        
        # Approved by
        layout.addWidget(QLabel("Approved by:"))
        self.approved_by_widget = PersonWidget()
        layout.addWidget(self.approved_by_widget)
        
        # Approval button
        approval_layout = QHBoxLayout()
        self.approve_button = QPushButton("Approve Form")
        approval_layout.addWidget(self.approve_button)
        approval_layout.addStretch()
        layout.addLayout(approval_layout)
        
        return group
    
    def create_reply_section(self) -> QGroupBox:
        """Create the reply section."""
        group = QGroupBox("Reply")
        layout = QVBoxLayout(group)
        
        # Reply content
        layout.addWidget(QLabel("Reply Content:"))
        self.reply_edit = QTextEdit()
        self.reply_edit.setMinimumHeight(100)
        layout.addWidget(self.reply_edit)
        
        # Replied by
        layout.addWidget(QLabel("Replied by:"))
        self.replied_by_widget = PersonWidget()
        layout.addWidget(self.replied_by_widget)
        
        # Reply date/time
        layout.addWidget(QLabel("Reply Date/Time:"))
        self.reply_datetime_edit = QLineEdit()
        self.reply_datetime_edit.setReadOnly(True)
        layout.addWidget(self.reply_datetime_edit)
        
        # Reply button
        reply_layout = QHBoxLayout()
        self.add_reply_button = QPushButton("Add Reply")
        reply_layout.addWidget(self.add_reply_button)
        reply_layout.addStretch()
        layout.addLayout(reply_layout)
        
        return group
    
    def create_button_bar(self) -> QHBoxLayout:
        """Create the button bar."""
        layout = QHBoxLayout()
        
        self.new_button = QPushButton("New Form")
        self.save_button = QPushButton("Save Form")
        self.validate_button = QPushButton("Validate")
        self.clear_button = QPushButton("Clear")
        
        layout.addWidget(self.new_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.validate_button)
        layout.addWidget(self.clear_button)
        layout.addStretch()
        
        self.status_indicator = QLabel("Status: Draft")
        layout.addWidget(self.status_indicator)
        
        return layout
    
    def connect_signals(self):
        """Connect signals."""
        # Form changes
        self.incident_name_edit.textChanged.connect(self.on_form_changed)
        self.subject_edit.textChanged.connect(self.on_form_changed)
        self.message_edit.textChanged.connect(self.on_form_changed)
        
        # Buttons
        self.new_button.clicked.connect(self.new_form)
        self.save_button.clicked.connect(self.save_form)
        self.validate_button.clicked.connect(self.validate_form)
        self.clear_button.clicked.connect(self.clear_form)
        self.approve_button.clicked.connect(self.approve_form)
        self.add_reply_button.clicked.connect(self.add_reply)
    
    def new_form(self):
        """Create new form."""
        self.form = ICS213Form()
        self.current_form_id = None
        self.is_modified = False
        self.load_form_data()
        self.update_ui_state()
        self.set_status("New form created")
    
    def load_form_data(self):
        """Load form data into UI."""
        if not self.form:
            return
        
        data = self.form.data
        self.incident_name_edit.setText(data.incident_name)
        self.to_widget.set_person(data.to)
        self.from_widget.set_person(data.from_person)
        self.subject_edit.setText(data.subject)
        self.date_edit.setText(data.date)
        self.time_edit.setText(data.time)
        self.message_edit.setPlainText(data.message)
        
        # Priority
        priority_map = {Priority.ROUTINE: 0, Priority.URGENT: 1, Priority.IMMEDIATE: 2}
        self.priority_combo.setCurrentIndex(priority_map.get(data.priority, 0))
        self.reply_requested_check.setChecked(data.reply_requested)
        
        # Approval and reply
        self.approved_by_widget.set_person(data.approved_by)
        self.reply_edit.setPlainText(data.reply)
        self.replied_by_widget.set_person(data.replied_by)
        self.reply_datetime_edit.setText(data.reply_date_time)
    
    def save_form_data(self):
        """Save UI data to form."""
        if not self.form:
            return
        
        priority_map = {0: Priority.ROUTINE, 1: Priority.URGENT, 2: Priority.IMMEDIATE}
        
        self.form.data.incident_name = self.incident_name_edit.text().strip()
        self.form.data.to = self.to_widget.get_person()
        self.form.data.from_person = self.from_widget.get_person()
        self.form.data.subject = self.subject_edit.text().strip()
        self.form.data.date = self.date_edit.text().strip()
        self.form.data.time = self.time_edit.text().strip()
        self.form.data.message = self.message_edit.toPlainText().strip()
        self.form.data.priority = priority_map.get(self.priority_combo.currentIndex(), Priority.ROUTINE)
        self.form.data.reply_requested = self.reply_requested_check.isChecked()
        self.form.data.approved_by = self.approved_by_widget.get_person()
        self.form.data.reply = self.reply_edit.toPlainText().strip()
        self.form.data.replied_by = self.replied_by_widget.get_person()
        self.form.updated_at = datetime.now()
    
    def validate_form(self):
        """Validate form."""
        if not self.form:
            return
        
        self.save_form_data()
        is_valid = self.form.validate()
        errors = self.form.get_validation_errors()
        
        if is_valid:
            self.set_status("Form validation passed")
            QMessageBox.information(self, "Validation", "Form is valid!")
        else:
            error_msg = "Validation failed:\n\n" + "\n".join(f"• {error}" for error in errors)
            self.set_status(f"Validation failed ({len(errors)} errors)")
            QMessageBox.warning(self, "Validation", error_msg)
        
        self.update_ui_state()
        return is_valid
    
    def save_form(self):
        """Save form to database."""
        if not self.form:
            return
        
        self.save_form_data()
        
        # Validate before saving
        if not self.validate_form():
            return
        
        if not self.form_service:
            self.set_status("Database not available")
            QMessageBox.warning(self, "Save Failed", "Database service not available")
            return
        
        try:
            # Save to database
            form_id = self.form_service.save_form(self.form, self.current_form_id)
            
            # Update current form ID and modified state
            self.current_form_id = form_id
            self.is_modified = False
            
            self.set_status(f"Form saved successfully (ID: {form_id})")
            self.form_saved.emit(form_id)
            
            logger.info(f"Form saved with ID {form_id}")
            
        except DatabaseError as e:
            error_msg = f"Failed to save form: {e}"
            self.set_status("Save failed")
            QMessageBox.critical(self, "Save Failed", error_msg)
            logger.error(error_msg)
    
    def load_form_by_id(self, form_id: int):
        """Load form from database by ID."""
        if not self.form_service:
            self.set_status("Database not available")
            QMessageBox.warning(self, "Load Failed", "Database service not available")
            return
        
        try:
            # Load from database
            form = self.form_service.load_form(form_id)
            
            # Set form and update UI
            self.form = form
            self.current_form_id = form_id
            self.is_modified = False
            
            self.load_form_data()
            self.update_ui_state()
            self.set_status(f"Form loaded (ID: {form_id})")
            self.form_loaded.emit(form_id)
            
            logger.info(f"Form loaded with ID {form_id}")
            
        except DatabaseError as e:
            error_msg = f"Failed to load form: {e}"
            self.set_status("Load failed")
            QMessageBox.critical(self, "Load Failed", error_msg)
            logger.error(error_msg)
    
    def clear_form(self):
        """Clear form."""
        reply = QMessageBox.question(self, "Clear Form", "Clear all data?")
        if reply == QMessageBox.Yes:
            self.new_form()
    
    def approve_form(self):
        """Approve form."""
        if not self.form:
            return
        
        self.save_form_data()
        if not self.form.is_ready_for_approval():
            QMessageBox.warning(self, "Cannot Approve", "Form must be valid first.")
            return
        
        approver = self.approved_by_widget.get_person()
        if not approver.is_complete:
            QMessageBox.warning(self, "Cannot Approve", "Approver info required.")
            return
        
        if self.form.approve(approver):
            self.set_status("Form approved")
            self.update_ui_state()
            QMessageBox.information(self, "Approved", f"Approved by {approver.display_name}")
    
    def add_reply(self):
        """Add reply."""
        if not self.form:
            return
        
        self.save_form_data()
        reply_text = self.reply_edit.toPlainText().strip()
        replier = self.replied_by_widget.get_person()
        
        if not reply_text:
            QMessageBox.warning(self, "Cannot Reply", "Reply text required.")
            return
        
        if not replier.is_complete:
            QMessageBox.warning(self, "Cannot Reply", "Replier info required.")
            return
        
        if self.form.add_reply(reply_text, replier):
            self.reply_datetime_edit.setText(self.form.data.reply_date_time)
            self.set_status("Reply added")
            self.update_ui_state()
            QMessageBox.information(self, "Reply Added", f"Reply by {replier.display_name}")
    
    def update_ui_state(self):
        """Update UI state."""
        if not self.form:
            return
        
        # Update status with modification indicator
        status_text = f"Status: {self.form.status.value.title()}"
        if self.is_modified:
            status_text += " (Modified)"
        self.status_indicator.setText(status_text)
        
        is_valid = self.form.validate()
        is_draft = self.form.status == FormStatus.DRAFT
        
        self.approve_button.setEnabled(is_valid and is_draft)
        self.add_reply_button.setEnabled(is_valid)
        
        # Update save button based on modification status
        self.save_button.setEnabled(self.is_modified and self.form_service is not None)
    
    def on_form_changed(self):
        """Handle form changes."""
        self.save_form_data()
        self.is_modified = True
        self.update_ui_state()
        self.form_changed.emit()
    
    def set_status(self, message: str):
        """Set status message."""
        self.status_label.setText(message)
    
    def get_form(self) -> Optional[ICS213Form]:
        """Get current form."""
        if self.form:
            self.save_form_data()
        return self.form
    
    def set_form(self, form: ICS213Form):
        """Set form."""
        self.form = form
        self.current_form_id = None
        self.is_modified = False
        self.load_form_data()
        self.update_ui_state()
        self.set_status("Form loaded")
    
    def has_unsaved_changes(self) -> bool:
        """Check if form has unsaved changes."""
        return self.is_modified
    
    def get_form_title(self) -> str:
        """Get descriptive title for current form."""
        if not self.form:
            return "Empty Form"
        
        subject = self.form.data.subject.strip() if self.form.data.subject else ""
        if subject:
            return f"ICS-213: {subject}"
        else:
            return "ICS-213: Untitled"