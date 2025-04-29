#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-213 General Message form view implementation.

This module provides a UI view for the ICS-213 General Message form.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QDateTimeEdit,
    QGroupBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Slot, QDateTime

from radioforms.views.form_view_base import FormViewBase
from radioforms.models.ics213_form import ICS213Form


class ICS213FormView(FormViewBase):
    """
    ICS-213 General Message form view.
    
    This view provides a UI for creating and editing ICS-213 forms.
    """
    
    def __init__(self, form_model=None, parent=None):
        """
        Initialize the ICS-213 form view.
        
        Args:
            form_model: ICS213Form model instance to display and edit
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
        """Create the ICS-213 form-specific UI elements."""
        # Set form title and subtitle
        self.form_title_label.setText("ICS-213: General Message")
        self.form_subtitle_label.setText("Used for sending general messages during incident operations")
        
        # Create form sections
        self._create_header_section()
        self._create_message_section()
        self._create_reply_section()
        
        # Add sections to form layout
        self.form_layout.addWidget(self.header_group)
        self.form_layout.addWidget(self.message_group)
        self.form_layout.addWidget(self.reply_group)
        self.form_layout.addStretch()
    
    def _create_header_section(self):
        """Create the form header section with routing information."""
        self.header_group = QGroupBox("Message Routing")
        header_layout = QFormLayout(self.header_group)
        header_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # To field
        self.to_edit = QLineEdit()
        header_layout.addRow("To:", self.to_edit)
        
        # From field
        self.from_edit = QLineEdit()
        header_layout.addRow("From:", self.from_edit)
        
        # Subject field
        self.subject_edit = QLineEdit()
        header_layout.addRow("Subject:", self.subject_edit)
        
        # Date field
        self.date_edit = QDateTimeEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("MM/dd/yyyy HH:mm")
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        header_layout.addRow("Date/Time:", self.date_edit)
    
    def _create_message_section(self):
        """Create the message content section."""
        self.message_group = QGroupBox("Message")
        message_layout = QVBoxLayout(self.message_group)
        
        # Message text
        self.message_edit = QTextEdit()
        self.message_edit.setMinimumHeight(150)
        message_layout.addWidget(self.message_edit)
        
        # Sender information
        sender_frame = QFrame()
        sender_layout = QFormLayout(sender_frame)
        
        self.sender_name_edit = QLineEdit()
        sender_layout.addRow("Sender Name:", self.sender_name_edit)
        
        self.sender_position_edit = QLineEdit()
        sender_layout.addRow("Position/Title:", self.sender_position_edit)
        
        message_layout.addWidget(sender_frame)
    
    def _create_reply_section(self):
        """Create the reply section."""
        self.reply_group = QGroupBox("Reply/Approval")
        reply_layout = QVBoxLayout(self.reply_group)
        
        # Reply message
        self.reply_edit = QTextEdit()
        self.reply_edit.setMinimumHeight(100)
        self.reply_edit.setPlaceholderText("Enter reply message here (if any)")
        reply_layout.addWidget(self.reply_edit)
        
        # Recipient information
        recipient_frame = QFrame()
        recipient_layout = QFormLayout(recipient_frame)
        
        self.recipient_name_edit = QLineEdit()
        recipient_layout.addRow("Recipient Name:", self.recipient_name_edit)
        
        self.recipient_position_edit = QLineEdit()
        recipient_layout.addRow("Position/Title:", self.recipient_position_edit)
        
        self.reply_date_edit = QDateTimeEdit()
        self.reply_date_edit.setCalendarPopup(True)
        self.reply_date_edit.setDisplayFormat("MM/dd/yyyy HH:mm")
        self.reply_date_edit.setDateTime(QDateTime.currentDateTime())
        recipient_layout.addRow("Reply Date/Time:", self.reply_date_edit)
        
        reply_layout.addWidget(recipient_frame)
    
    def _connect_field_signals(self):
        """Connect signals from UI fields to track changes."""
        # Connect text changed signals for all editable fields
        self.to_edit.textChanged.connect(lambda: self._field_modified("to"))
        self.from_edit.textChanged.connect(lambda: self._field_modified("from_field"))
        self.subject_edit.textChanged.connect(lambda: self._field_modified("subject"))
        self.date_edit.dateTimeChanged.connect(lambda: self._field_modified("message_date"))
        
        self.message_edit.textChanged.connect(lambda: self._field_modified("message"))
        self.sender_name_edit.textChanged.connect(lambda: self._field_modified("sender_name"))
        self.sender_position_edit.textChanged.connect(lambda: self._field_modified("sender_position"))
        
        self.reply_edit.textChanged.connect(lambda: self._field_modified("reply"))
        self.recipient_name_edit.textChanged.connect(lambda: self._field_modified("recipient_name"))
        self.recipient_position_edit.textChanged.connect(lambda: self._field_modified("recipient_position"))
        self.reply_date_edit.dateTimeChanged.connect(lambda: self._field_modified("reply_date"))
    
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
        if self._form_model and isinstance(self._form_model, ICS213Form):
            # Connect to the form's property change signals
            self._form_model.add_observer(self._on_form_field_changed)
    
    def update_ui_from_model(self):
        """Update UI fields from the form model's data."""
        if not self._form_model or not isinstance(self._form_model, ICS213Form):
            return
        
        # Update header fields
        self.to_edit.setText(self._form_model.to)
        self.from_edit.setText(self._form_model.from_field)
        self.subject_edit.setText(self._form_model.subject)
        
        if self._form_model.message_date:
            qt_date = QDateTime.fromString(self._form_model.message_date.isoformat(), Qt.ISODate)
            self.date_edit.setDateTime(qt_date)
        
        # Update message fields
        self.message_edit.setText(self._form_model.message)
        self.sender_name_edit.setText(self._form_model.sender_name)
        self.sender_position_edit.setText(self._form_model.sender_position)
        
        # Update reply fields
        self.reply_edit.setText(self._form_model.reply)
        self.recipient_name_edit.setText(self._form_model.recipient_name)
        self.recipient_position_edit.setText(self._form_model.recipient_position)
        
        if self._form_model.reply_date:
            qt_reply_date = QDateTime.fromString(self._form_model.reply_date.isoformat(), Qt.ISODate)
            self.reply_date_edit.setDateTime(qt_reply_date)
        
        # Reset modification flag
        self._modified = False
    
    def update_model_from_ui(self):
        """Update the form model from UI field values."""
        if not self._form_model or not isinstance(self._form_model, ICS213Form):
            return
        
        # Update header fields
        self._form_model.to = self.to_edit.text()
        self._form_model.from_field = self.from_edit.text()
        self._form_model.subject = self.subject_edit.text()
        self._form_model.message_date = self.date_edit.dateTime().toPython()
        
        # Update message fields
        self._form_model.message = self.message_edit.toPlainText()
        self._form_model.sender_name = self.sender_name_edit.text()
        self._form_model.sender_position = self.sender_position_edit.text()
        
        # Update reply fields
        self._form_model.reply = self.reply_edit.toPlainText()
        self._form_model.recipient_name = self.recipient_name_edit.text()
        self._form_model.recipient_position = self.recipient_position_edit.text()
        self._form_model.reply_date = self.reply_date_edit.dateTime().toPython()
    
    def _update_read_only_state(self):
        """Update the UI elements based on the read-only state."""
        # Call base class implementation
        super()._update_read_only_state()
        
        # Update form-specific fields
        self.to_edit.setReadOnly(self._read_only)
        self.from_edit.setReadOnly(self._read_only)
        self.subject_edit.setReadOnly(self._read_only)
        self.date_edit.setReadOnly(self._read_only)
        
        self.message_edit.setReadOnly(self._read_only)
        self.sender_name_edit.setReadOnly(self._read_only)
        self.sender_position_edit.setReadOnly(self._read_only)
        
        self.reply_edit.setReadOnly(self._read_only)
        self.recipient_name_edit.setReadOnly(self._read_only)
        self.recipient_position_edit.setReadOnly(self._read_only)
        self.reply_date_edit.setReadOnly(self._read_only)
