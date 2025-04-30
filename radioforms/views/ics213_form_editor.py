#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-213 General Message Form Editor.

This module provides a form editor for ICS-213 General Message forms,
implementing the form editor architecture with the enhanced ICS-213 form model.
"""

import datetime
from typing import Dict, Any, List, Optional, Set, Union, Callable

from PySide6.QtCore import Qt, Signal, Slot, QObject, Property, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QCheckBox, QComboBox, QDateTimeEdit,
    QGridLayout, QScrollArea, QFrame, QSplitter, QTableView, 
    QHeaderView, QSpacerItem, QSizePolicy, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QMessageBox, QTabWidget
)
from PySide6.QtGui import QFont

from radioforms.models.enhanced_ics213_form import EnhancedICS213Form, FormState
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.views.form_editor_base import (
    FormEditorContainer, FormField, TextField, TextAreaField, 
    DateTimeField, ChoiceField, CheckboxField, ValidationSummary
)


class SignatureDialog(QDialog):
    """
    Dialog for collecting signature information.
    
    This dialog is used for approval, transmission, receipt, and reply operations.
    """
    
    def __init__(self, title: str, fields: List[tuple], parent=None, defaults: Dict[str, str] = None):
        """
        Initialize the dialog.
        
        Args:
            title: Dialog title
            fields: List of (field_name, field_label) tuples
            parent: Parent widget
            defaults: Default values for fields
        """
        super().__init__(parent)
        
        self._title = title
        self._fields = fields
        self._defaults = defaults or {}
        self._field_widgets = {}
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle(self._title)
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Create fields
        for field_name, field_label in self._fields:
            field = QLineEdit()
            if field_name in self._defaults:
                field.setText(self._defaults[field_name])
            form_layout.addRow(field_label + ":", field)
            self._field_widgets[field_name] = field
            
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set width
        self.setMinimumWidth(400)
        
    def get_values(self) -> Dict[str, str]:
        """
        Get the values entered in the dialog.
        
        Returns:
            Dictionary of field values
        """
        values = {}
        for field_name, field_widget in self._field_widgets.items():
            values[field_name] = field_widget.text()
        return values


class ICS213FormEditor(FormEditorContainer):
    """
    Form editor for ICS-213 General Message forms.
    
    This class extends FormEditorContainer to provide a specialized
    editor for ICS-213 General Message forms.
    """
    
    def __init__(self, form_registry: FormModelRegistry, 
                form: Optional[EnhancedICS213Form] = None, 
                form_id: Optional[str] = None, 
                parent: Optional[QWidget] = None):
        """
        Initialize the ICS-213 form editor.
        
        Args:
            form_registry: FormModelRegistry instance
            form: Existing form to edit
            form_id: ID of form to load
            parent: Parent widget
        """
        super().__init__(form_registry, form, form_id, "ICS-213", parent)
        
    def _get_form_title(self, form: EnhancedICS213Form) -> str:
        """
        Get the title for the form.
        
        Args:
            form: The form to get the title for
            
        Returns:
            The form title
        """
        return "ICS-213 General Message"
        
    def _create_form_body(self, form: EnhancedICS213Form) -> QWidget:
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
        
        # Tab 1: Message
        message_tab = self._create_message_tab(form)
        tab_widget.addTab(message_tab, "Message")
        
        # Tab 2: Routing
        routing_tab = self._create_routing_tab(form)
        tab_widget.addTab(routing_tab, "Routing")
        
        # Tab 3: Reply (if applicable)
        if form.state in [FormState.RECEIVED, FormState.REPLIED]:
            reply_tab = self._create_reply_tab(form)
            tab_widget.addTab(reply_tab, "Reply")
            
        main_layout.addWidget(tab_widget)
        
        # Bind fields to form
        self.bind_fields_to_form()
        
        return widget
        
    def _create_message_tab(self, form: EnhancedICS213Form) -> QWidget:
        """
        Create the message tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Header section
        header_group = QGroupBox("Message Header")
        header_layout = QFormLayout()
        header_group.setLayout(header_layout)
        
        # To field
        to_field = TextField("to", "To", required=True)
        self.register_field(to_field)
        header_layout.addRow("To:", to_field)
        
        # From field
        from_field = TextField("from_field", "From", required=True)
        self.register_field(from_field)
        header_layout.addRow("From:", from_field)
        
        # Subject field
        subject_field = TextField("subject", "Subject", required=True)
        self.register_field(subject_field)
        header_layout.addRow("Subject:", subject_field)
        
        # Date/time field
        date_field = DateTimeField("date", "Date/Time")
        self.register_field(date_field)
        header_layout.addRow("Date/Time:", date_field)
        
        main_layout.addWidget(header_group)
        
        # Message section
        message_group = QGroupBox("Message Body")
        message_layout = QVBoxLayout()
        message_group.setLayout(message_layout)
        
        # Message field
        message_field = TextAreaField("message", "Message", required=True)
        self.register_field(message_field)
        message_layout.addWidget(message_field)
        
        main_layout.addWidget(message_group)
        
        # Show sender info if approved
        if form.state != FormState.DRAFT:
            sender_group = QGroupBox("Approved By")
            sender_layout = QFormLayout()
            sender_group.setLayout(sender_layout)
            
            if form.state == FormState.DRAFT:
                # Editable fields
                sender_name_field = TextField("sender_name", "Name")
                self.register_field(sender_name_field)
                sender_layout.addRow("Name:", sender_name_field)
                
                sender_position_field = TextField("sender_position", "Position")
                self.register_field(sender_position_field)
                sender_layout.addRow("Position:", sender_position_field)
            else:
                # Display-only fields when already approved
                sender_name_label = QLabel(form.sender_name)
                sender_layout.addRow("Name:", sender_name_label)
                
                sender_position_label = QLabel(form.sender_position)
                sender_layout.addRow("Position:", sender_position_label)
                
                sender_signature_label = QLabel(f"Signature: {form.sender_signature}")
                sender_layout.addRow("", sender_signature_label)
                
                sender_date_label = QLabel(
                    form.sender_date.strftime("%Y-%m-%d %H:%M") if form.sender_date else ""
                )
                sender_layout.addRow("Date/Time:", sender_date_label)
                
            main_layout.addWidget(sender_group)
            
        return widget
        
    def _create_routing_tab(self, form: EnhancedICS213Form) -> QWidget:
        """
        Create the routing tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Transmission section (if applicable)
        if form.state in [FormState.TRANSMITTED, FormState.RECEIVED, FormState.REPLIED]:
            transmission_group = QGroupBox("Transmission")
            transmission_layout = QFormLayout()
            transmission_group.setLayout(transmission_layout)
            
            # Display transmission information
            operator_label = QLabel(form.transmitted_by_operator)
            transmission_layout.addRow("Operator:", operator_label)
            
            date_time_label = QLabel(
                form.transmitted_date_time.strftime("%Y-%m-%d %H:%M") 
                if form.transmitted_date_time else ""
            )
            transmission_layout.addRow("Date/Time:", date_time_label)
            
            main_layout.addWidget(transmission_group)
            
        # Receipt section (if applicable)
        if form.state in [FormState.RECEIVED, FormState.REPLIED]:
            receipt_group = QGroupBox("Receipt")
            receipt_layout = QFormLayout()
            receipt_group.setLayout(receipt_layout)
            
            # Display receipt information
            operator_label = QLabel(form.received_by_operator)
            receipt_layout.addRow("Operator:", operator_label)
            
            date_time_label = QLabel(
                form.received_date_time.strftime("%Y-%m-%d %H:%M") 
                if form.received_date_time else ""
            )
            receipt_layout.addRow("Date/Time:", date_time_label)
            
            main_layout.addWidget(receipt_group)
            
        # Add spacer if no routing information
        if form.state == FormState.DRAFT or form.state == FormState.APPROVED:
            main_layout.addWidget(QLabel("Routing information will be shown here after the message is transmitted."))
            
        main_layout.addStretch()
        
        return widget
        
    def _create_reply_tab(self, form: EnhancedICS213Form) -> QWidget:
        """
        Create the reply tab.
        
        Args:
            form: The form
            
        Returns:
            The tab widget
        """
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        
        # Reply section
        reply_group = QGroupBox("Reply Message")
        reply_layout = QVBoxLayout()
        reply_group.setLayout(reply_layout)
        
        if form.state == FormState.RECEIVED:
            # Editable reply
            reply_field = TextAreaField("reply_text", "Reply", required=True)
            self.register_field(reply_field)
            reply_layout.addWidget(reply_field)
            
            # Replier information fields
            replier_group = QGroupBox("Reply By")
            replier_layout = QFormLayout()
            replier_group.setLayout(replier_layout)
            
            replier_name_field = TextField("replier_name", "Name")
            self.register_field(replier_name_field)
            replier_layout.addRow("Name:", replier_name_field)
            
            replier_position_field = TextField("replier_position", "Position")
            self.register_field(replier_position_field)
            replier_layout.addRow("Position:", replier_position_field)
            
            reply_layout.addWidget(replier_group)
        else:
            # Display reply
            reply_text_label = QLabel(form.reply_text)
            reply_text_label.setWordWrap(True)
            reply_text_label.setTextFormat(Qt.PlainText)
            reply_text_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            reply_text_label.setMinimumHeight(100)
            reply_layout.addWidget(reply_text_label)
            
            # Replier information
            replier_group = QGroupBox("Reply By")
            replier_layout = QFormLayout()
            replier_group.setLayout(replier_layout)
            
            replier_name_label = QLabel(form.replier_name)
            replier_layout.addRow("Name:", replier_name_label)
            
            replier_position_label = QLabel(form.replier_position)
            replier_layout.addRow("Position:", replier_position_label)
            
            replier_signature_label = QLabel(f"Signature: {form.replier_signature}")
            replier_layout.addRow("", replier_signature_label)
            
            replier_date_label = QLabel(
                form.replier_date.strftime("%Y-%m-%d %H:%M") if form.replier_date else ""
            )
            replier_layout.addRow("Date/Time:", replier_date_label)
            
            reply_layout.addWidget(replier_group)
            
        main_layout.addWidget(reply_group)
        
        return widget
        
    def _on_approve(self):
        """Handle approve button click."""
        # Create custom dialog for collecting approver information
        dialog = SignatureDialog(
            "Approve Message",
            [
                ("name", "Name"),
                ("position", "Position/Title"),
                ("signature", "Signature")
            ],
            self,
            {
                "name": self._form.sender_name,
                "position": self._form.sender_position
            }
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            values = dialog.get_values()
            name = values.get("name", "")
            position = values.get("position", "")
            signature = values.get("signature", "")
            
            if not name or not position or not signature:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide name, position, and signature to approve the message."
                )
                return
                
            # Call approve method on form
            if hasattr(self._form, 'approve'):
                self._form.approve(name, position, signature)
                self._update_state_after_transition()
                
    def _on_transmit(self):
        """Handle transmit button click."""
        # Create custom dialog for collecting transmission information
        dialog = SignatureDialog(
            "Transmit Message",
            [
                ("operator", "Operator"),
            ],
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            values = dialog.get_values()
            operator = values.get("operator", "")
            
            if not operator:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide operator name to transmit the message."
                )
                return
                
            # Call transmit method on form
            if hasattr(self._form, 'transmit'):
                self._form.transmit(operator, datetime.datetime.now())
                self._update_state_after_transition()
                
    def _on_receive(self):
        """Handle receive button click."""
        # Create custom dialog for collecting receiver information
        dialog = SignatureDialog(
            "Receive Message",
            [
                ("operator", "Operator"),
            ],
            self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            values = dialog.get_values()
            operator = values.get("operator", "")
            
            if not operator:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide operator name to mark the message as received."
                )
                return
                
            # Call receive method on form
            if hasattr(self._form, 'receive'):
                self._form.receive(operator, datetime.datetime.now())
                self._update_state_after_transition()
                
    def _on_reply(self):
        """Handle reply button click."""
        # Check if reply text is entered
        if not self._form.reply_text:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a reply message before submitting the reply."
            )
            return
            
        # Create custom dialog for collecting replier information
        dialog = SignatureDialog(
            "Submit Reply",
            [
                ("name", "Name"),
                ("position", "Position/Title"),
                ("signature", "Signature")
            ],
            self,
            {
                "name": self._form.replier_name,
                "position": self._form.replier_position
            }
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            values = dialog.get_values()
            name = values.get("name", "")
            position = values.get("position", "")
            signature = values.get("signature", "")
            
            if not name or not position or not signature:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please provide name, position, and signature to submit the reply."
                )
                return
                
            # Call reply method on form
            if hasattr(self._form, 'reply'):
                self._form.reply(self._form.reply_text, name, position, signature)
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
