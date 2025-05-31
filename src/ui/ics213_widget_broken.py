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
    """Main widget for ICS-213 General Message form.
    
    This widget provides a complete interface for creating, editing,
    and managing ICS-213 forms following CLAUDE.md principles.
    """
    
    # Signals
    form_changed = Signal()  # Emitted when form data changes
    form_saved = Signal()   # Emitted when form is saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.form: Optional[ICS213Form] = None
        self.setup_ui()
        self.connect_signals()
        
        # Start with new form
        self.new_form()
        
        logger.debug("ICS213Widget initialized")
    
    def setup_ui(self):
        """Set up the main UI layout."""
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for form content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main form widget
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Header section
        header_group = self.create_header_section()
        form_layout.addWidget(header_group)
        
        # Message section
        message_group = self.create_message_section()
        form_layout.addWidget(message_group)
        
        # Reply section
        reply_group = self.create_reply_section()
        form_layout.addWidget(reply_group)
        
        # Set form widget in scroll area
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)
        
        # Button bar
        button_layout = self.create_button_bar()
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def create_header_section(self) -> QGroupBox:
        """Create the header section of the form."""
        group = QGroupBox("Message Header")
        layout = QGridLayout(group)
        
        # Row 0: Incident name (optional)
        layout.addWidget(QLabel("Incident Name:"), 0, 0)
        self.incident_name_edit = QLineEdit()
        self.incident_name_edit.setPlaceholderText("Enter incident name (optional)")
        layout.addWidget(self.incident_name_edit, 0, 1, 1, 3)
        
        # Row 1: To section
        layout.addWidget(QLabel("To:"), 1, 0)
        self.to_widget = PersonWidget()
        layout.addWidget(self.to_widget, 1, 1, 1, 3)
        
        # Row 2: From section
        layout.addWidget(QLabel("From:"), 2, 0)
        self.from_widget = PersonWidget()
        layout.addWidget(self.from_widget, 2, 1, 1, 3)
        
        # Row 3: Subject
        layout.addWidget(QLabel("Subject:"), 3, 0)
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter message subject")
        layout.addWidget(self.subject_edit, 3, 1, 1, 3)
        
        # Row 4: Date, Time, Priority
        layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.now().strftime("%Y-%m-%d"))
        layout.addWidget(self.date_edit, 4, 1)
        
        layout.addWidget(QLabel("Time:"), 4, 2)
        self.time_edit = QLineEdit()
        self.time_edit.setText(datetime.now().strftime("%H:%M"))
        layout.addWidget(self.time_edit, 4, 3)
        
        # Row 5: Priority and Reply Requested
        layout.addWidget(QLabel("Priority:"), 5, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Routine", "Urgent", "Immediate"])
        layout.addWidget(self.priority_combo, 5, 1)
        
        self.reply_requested_check = QCheckBox("Reply Requested")
        layout.addWidget(self.reply_requested_check, 5, 2, 1, 2)
        
        return group
    
    def create_message_section(self) -> QGroupBox:\n        \"\"\"Create the message section of the form.\"\"\"\n        group = QGroupBox(\"Message\")\n        layout = QVBoxLayout(group)\n        \n        # Message content\n        layout.addWidget(QLabel(\"Message Content:\"))\n        self.message_edit = QTextEdit()\n        self.message_edit.setPlaceholderText(\"Enter your message here...\")\n        self.message_edit.setMinimumHeight(150)\n        layout.addWidget(self.message_edit)\n        \n        # Approved by section\n        approved_label = QLabel(\"Approved by:\")\n        approved_label.setFont(QFont(approved_label.font().family(), approved_label.font().pointSize(), QFont.Bold))\n        layout.addWidget(approved_label)\n        \n        self.approved_by_widget = PersonWidget()\n        layout.addWidget(self.approved_by_widget)\n        \n        # Approval buttons\n        approval_layout = QHBoxLayout()\n        self.approve_button = QPushButton(\"Approve Form\")\n        self.approve_button.setEnabled(False)\n        approval_layout.addWidget(self.approve_button)\n        approval_layout.addStretch()\n        layout.addLayout(approval_layout)\n        \n        return group\n    \n    def create_reply_section(self) -> QGroupBox:\n        \"\"\"Create the reply section of the form.\"\"\"\n        group = QGroupBox(\"Reply\")\n        layout = QVBoxLayout(group)\n        \n        # Reply content\n        layout.addWidget(QLabel(\"Reply Content:\"))\n        self.reply_edit = QTextEdit()\n        self.reply_edit.setPlaceholderText(\"Enter reply here...\")\n        self.reply_edit.setMinimumHeight(100)\n        layout.addWidget(self.reply_edit)\n        \n        # Replied by section\n        replied_label = QLabel(\"Replied by:\")\n        replied_label.setFont(QFont(replied_label.font().family(), replied_label.font().pointSize(), QFont.Bold))\n        layout.addWidget(replied_label)\n        \n        self.replied_by_widget = PersonWidget()\n        layout.addWidget(self.replied_by_widget)\n        \n        # Reply date/time (read-only)\n        self.reply_datetime_edit = QLineEdit()\n        self.reply_datetime_edit.setReadOnly(True)\n        self.reply_datetime_edit.setPlaceholderText(\"Reply date/time will be set automatically\")\n        layout.addWidget(QLabel(\"Reply Date/Time:\"))\n        layout.addWidget(self.reply_datetime_edit)\n        \n        # Reply buttons\n        reply_layout = QHBoxLayout()\n        self.add_reply_button = QPushButton(\"Add Reply\")\n        self.add_reply_button.setEnabled(False)\n        reply_layout.addWidget(self.add_reply_button)\n        reply_layout.addStretch()\n        layout.addLayout(reply_layout)\n        \n        return group\n    \n    def create_button_bar(self) -> QHBoxLayout:\n        \"\"\"Create the button bar at the bottom of the form.\"\"\"\n        layout = QHBoxLayout()\n        \n        # Form actions\n        self.new_button = QPushButton(\"New Form\")\n        self.save_button = QPushButton(\"Save Form\")\n        self.validate_button = QPushButton(\"Validate\")\n        self.clear_button = QPushButton(\"Clear\")\n        \n        layout.addWidget(self.new_button)\n        layout.addWidget(self.save_button)\n        layout.addWidget(self.validate_button)\n        layout.addWidget(self.clear_button)\n        layout.addStretch()\n        \n        # Form status indicator\n        self.status_indicator = QLabel(\"Status: Draft\")\n        status_font = QFont(self.status_indicator.font().family(), \n                           self.status_indicator.font().pointSize(), \n                           QFont.Bold)\n        self.status_indicator.setFont(status_font)\n        layout.addWidget(self.status_indicator)\n        \n        return layout\n    \n    def connect_signals(self):\n        \"\"\"Connect widget signals to handlers.\"\"\"\n        # Form field changes\n        self.incident_name_edit.textChanged.connect(self.on_form_changed)\n        self.subject_edit.textChanged.connect(self.on_form_changed)\n        self.date_edit.textChanged.connect(self.on_form_changed)\n        self.time_edit.textChanged.connect(self.on_form_changed)\n        self.message_edit.textChanged.connect(self.on_form_changed)\n        self.reply_edit.textChanged.connect(self.on_form_changed)\n        self.priority_combo.currentTextChanged.connect(self.on_form_changed)\n        self.reply_requested_check.toggled.connect(self.on_form_changed)\n        \n        # Person widget changes\n        for widget in [self.to_widget, self.from_widget, \n                      self.approved_by_widget, self.replied_by_widget]:\n            for line_edit in widget.findChildren(QLineEdit):\n                line_edit.textChanged.connect(self.on_form_changed)\n        \n        # Button clicks\n        self.new_button.clicked.connect(self.new_form)\n        self.save_button.clicked.connect(self.save_form)\n        self.validate_button.clicked.connect(self.validate_form)\n        self.clear_button.clicked.connect(self.clear_form)\n        self.approve_button.clicked.connect(self.approve_form)\n        self.add_reply_button.clicked.connect(self.add_reply)\n    \n    def new_form(self):\n        \"\"\"Create a new empty form.\"\"\"\n        self.form = ICS213Form()\n        self.load_form_data()\n        self.update_ui_state()\n        self.set_status(\"New form created\")\n        logger.info(\"New ICS-213 form created\")\n    \n    def load_form_data(self):\n        \"\"\"Load form data into UI widgets.\"\"\"\n        if not self.form:\n            return\n        \n        data = self.form.data\n        \n        # Header fields\n        self.incident_name_edit.setText(data.incident_name)\n        self.to_widget.set_person(data.to)\n        self.from_widget.set_person(data.from_person)\n        self.subject_edit.setText(data.subject)\n        self.date_edit.setText(data.date)\n        self.time_edit.setText(data.time)\n        self.message_edit.setPlainText(data.message)\n        \n        # Priority\n        priority_map = {\n            Priority.ROUTINE: 0,\n            Priority.URGENT: 1,\n            Priority.IMMEDIATE: 2\n        }\n        self.priority_combo.setCurrentIndex(priority_map.get(data.priority, 0))\n        self.reply_requested_check.setChecked(data.reply_requested)\n        \n        # Approval\n        self.approved_by_widget.set_person(data.approved_by)\n        \n        # Reply\n        self.reply_edit.setPlainText(data.reply)\n        self.replied_by_widget.set_person(data.replied_by)\n        self.reply_datetime_edit.setText(data.reply_date_time)\n    \n    def save_form_data(self):\n        \"\"\"Save UI data to form object.\"\"\"\n        if not self.form:\n            return\n        \n        # Priority mapping\n        priority_map = {\n            0: Priority.ROUTINE,\n            1: Priority.URGENT,\n            2: Priority.IMMEDIATE\n        }\n        \n        # Update form data\n        self.form.data.incident_name = self.incident_name_edit.text().strip()\n        self.form.data.to = self.to_widget.get_person()\n        self.form.data.from_person = self.from_widget.get_person()\n        self.form.data.subject = self.subject_edit.text().strip()\n        self.form.data.date = self.date_edit.text().strip()\n        self.form.data.time = self.time_edit.text().strip()\n        self.form.data.message = self.message_edit.toPlainText().strip()\n        self.form.data.priority = priority_map.get(self.priority_combo.currentIndex(), Priority.ROUTINE)\n        self.form.data.reply_requested = self.reply_requested_check.isChecked()\n        \n        # Approval data\n        self.form.data.approved_by = self.approved_by_widget.get_person()\n        \n        # Reply data\n        self.form.data.reply = self.reply_edit.toPlainText().strip()\n        self.form.data.replied_by = self.replied_by_widget.get_person()\n        \n        # Update timestamp\n        self.form.updated_at = datetime.now()\n    \n    def validate_form(self):\n        \"\"\"Validate the current form and show results.\"\"\"\n        if not self.form:\n            return\n        \n        self.save_form_data()\n        is_valid = self.form.validate()\n        errors = self.form.get_validation_errors()\n        \n        if is_valid:\n            self.set_status(\"Form validation passed\")\n            QMessageBox.information(self, \"Validation Result\", \"Form is valid!\")\n        else:\n            error_msg = \"Form validation failed:\\n\\n\" + \"\\n\".join(f\"• {error}\" for error in errors)\n            self.set_status(f\"Form validation failed ({len(errors)} errors)\")\n            QMessageBox.warning(self, \"Validation Result\", error_msg)\n        \n        self.update_ui_state()\n        return is_valid\n    \n    def save_form(self):\n        \"\"\"Save the form (placeholder for actual save functionality).\"\"\"\n        if not self.form:\n            return\n        \n        self.save_form_data()\n        \n        # For now, just validate and show success\n        if self.validate_form():\n            self.set_status(\"Form saved successfully\")\n            self.form_saved.emit()\n            logger.info(\"ICS-213 form saved\")\n    \n    def clear_form(self):\n        \"\"\"Clear all form fields.\"\"\"\n        reply = QMessageBox.question(\n            self, \"Clear Form\",\n            \"Are you sure you want to clear all form data?\",\n            QMessageBox.Yes | QMessageBox.No,\n            QMessageBox.No\n        )\n        \n        if reply == QMessageBox.Yes:\n            self.new_form()\n    \n    def approve_form(self):\n        \"\"\"Approve the current form.\"\"\"\n        if not self.form:\n            return\n        \n        self.save_form_data()\n        \n        # Check if form is ready for approval\n        if not self.form.is_ready_for_approval():\n            QMessageBox.warning(\n                self, \"Cannot Approve\",\n                \"Form must be valid before it can be approved.\"\n            )\n            return\n        \n        # Get approver from UI\n        approver = self.approved_by_widget.get_person()\n        if not approver.is_complete:\n            QMessageBox.warning(\n                self, \"Cannot Approve\",\n                \"Approver information (name and position) is required.\"\n            )\n            return\n        \n        # Approve the form\n        success = self.form.approve(approver)\n        if success:\n            self.set_status(\"Form approved\")\n            self.update_ui_state()\n            QMessageBox.information(\n                self, \"Form Approved\",\n                f\"Form approved by {approver.display_name}\"\n            )\n            logger.info(f\"ICS-213 form approved by {approver.display_name}\")\n        else:\n            QMessageBox.warning(\n                self, \"Approval Failed\",\n                \"Failed to approve form. Please check approver information.\"\n            )\n    \n    def add_reply(self):\n        \"\"\"Add a reply to the form.\"\"\"\n        if not self.form:\n            return\n        \n        self.save_form_data()\n        \n        # Get reply data from UI\n        reply_text = self.reply_edit.toPlainText().strip()\n        replier = self.replied_by_widget.get_person()\n        \n        if not reply_text:\n            QMessageBox.warning(\n                self, \"Cannot Add Reply\",\n                \"Reply text is required.\"\n            )\n            return\n        \n        if not replier.is_complete:\n            QMessageBox.warning(\n                self, \"Cannot Add Reply\",\n                \"Replier information (name and position) is required.\"\n            )\n            return\n        \n        # Add the reply\n        success = self.form.add_reply(reply_text, replier)\n        if success:\n            self.reply_datetime_edit.setText(self.form.data.reply_date_time)\n            self.set_status(\"Reply added\")\n            self.update_ui_state()\n            QMessageBox.information(\n                self, \"Reply Added\",\n                f\"Reply added by {replier.display_name}\"\n            )\n            logger.info(f\"Reply added to ICS-213 form by {replier.display_name}\")\n        else:\n            QMessageBox.warning(\n                self, \"Reply Failed\",\n                \"Failed to add reply. Please check reply information.\"\n            )\n    \n    def update_ui_state(self):\n        \"\"\"Update UI state based on current form status.\"\"\"\n        if not self.form:\n            return\n        \n        # Update status indicator\n        status_text = f\"Status: {self.form.status.value.title()}\"\n        self.status_indicator.setText(status_text)\n        \n        # Update button states\n        is_valid = self.form.validate()\n        is_draft = self.form.status == FormStatus.DRAFT\n        is_approved = self.form.status == FormStatus.APPROVED\n        has_approver = self.approved_by_widget.is_complete()\n        \n        self.approve_button.setEnabled(is_valid and is_draft)\n        self.add_reply_button.setEnabled(is_valid and (is_approved or self.form.status == FormStatus.TRANSMITTED))\n        \n        # Enable/disable reply section based on status\n        reply_enabled = self.form.status in [FormStatus.TRANSMITTED, FormStatus.RECEIVED]\n        self.reply_edit.setEnabled(reply_enabled)\n        self.replied_by_widget.setEnabled(reply_enabled)\n    \n    def on_form_changed(self):\n        \"\"\"Handle form data changes.\"\"\"\n        self.save_form_data()\n        self.update_ui_state()\n        self.form_changed.emit()\n    \n    def set_status(self, message: str):\n        \"\"\"Set status message.\"\"\"\n        self.status_label.setText(message)\n        logger.debug(f\"ICS213Widget status: {message}\")\n    \n    def get_form(self) -> Optional[ICS213Form]:\n        \"\"\"Get the current form object.\"\"\"\n        if self.form:\n            self.save_form_data()\n        return self.form\n    \n    def set_form(self, form: ICS213Form):\n        \"\"\"Set a new form object.\"\"\"\n        self.form = form\n        self.load_form_data()\n        self.update_ui_state()\n        self.set_status(\"Form loaded\")\n        logger.info(\"ICS-213 form loaded into widget\")"