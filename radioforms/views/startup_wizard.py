#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Startup Wizard for RadioForms.

This module provides a wizard-style interface for first-time setup and configuration
of the RadioForms application.
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from PySide6.QtCore import Qt, Signal, Slot, QObject, Property, QSize, QSettings
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QCheckBox, QComboBox, QFileDialog,
    QGridLayout, QFormLayout, QGroupBox, QRadioButton, QSpacerItem,
    QSizePolicy, QMessageBox, QApplication
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor

from radioforms.config.config_manager import ConfigManager
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.incident_dao_refactored import IncidentDAO
from radioforms.models.form_model_registry import FormModelRegistry


class WelcomePage(QWizardPage):
    """
    Welcome page for the startup wizard.
    
    This page introduces the user to the RadioForms application and explains
    the setup process.
    """
    
    def __init__(self, parent=None):
        """Initialize the welcome page."""
        super().__init__(parent)
        
        self.setTitle("Welcome to RadioForms")
        self.setSubTitle("This wizard will help you set up RadioForms for first use.")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Welcome message
        welcome_text = (
            "<p>RadioForms is a digital form manager for emergency communications "
            "that supports ICS forms and message handling.</p>"
            "<p>This wizard will guide you through:</p>"
            "<ul>"
            "<li>Setting up your personal and organization information</li>"
            "<li>Configuring database storage locations</li>"
            "<li>Creating your first incident</li>"
            "<li>Setting up form templates</li>"
            "</ul>"
            "<p>Click 'Next' to begin.</p>"
        )
        
        welcome_label = QLabel(welcome_text)
        welcome_label.setWordWrap(True)
        welcome_label.setTextFormat(Qt.RichText)
        layout.addWidget(welcome_label)
        
        # Add spacer to push content to the top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def initializePage(self):
        """Initialize page contents when shown."""
        # Set the wizard's button text
        self.wizard().setButtonText(QWizard.NextButton, "Begin Setup")


class UserInfoPage(QWizardPage):
    """
    User information page for the startup wizard.
    
    This page collects basic user and organization information.
    """
    
    def __init__(self, parent=None):
        """Initialize the user information page."""
        super().__init__(parent)
        
        self.setTitle("User Information")
        self.setSubTitle("Please enter your information and organization details.")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # User information group
        user_group = QGroupBox("Your Information")
        user_form = QFormLayout()
        user_group.setLayout(user_form)
        
        # Name fields
        self.name_field = QLineEdit()
        self.registerField("user.name*", self.name_field)
        user_form.addRow("Name:", self.name_field)
        
        self.callsign_field = QLineEdit()
        self.registerField("user.callsign", self.callsign_field)
        user_form.addRow("Callsign:", self.callsign_field)
        
        self.position_field = QLineEdit()
        self.registerField("user.position", self.position_field)
        user_form.addRow("ICS Position:", self.position_field)
        
        layout.addWidget(user_group)
        
        # Organization information group
        org_group = QGroupBox("Organization Information")
        org_form = QFormLayout()
        org_group.setLayout(org_form)
        
        self.org_name_field = QLineEdit()
        self.registerField("org.name", self.org_name_field)
        org_form.addRow("Organization Name:", self.org_name_field)
        
        self.org_type_combo = QComboBox()
        self.org_type_combo.addItems([
            "Emergency Management",
            "Amateur Radio",
            "Fire Department",
            "Law Enforcement",
            "EMS/Medical",
            "NGO/Volunteer",
            "Government",
            "Other"
        ])
        self.registerField("org.type", self.org_type_combo, "currentText")
        org_form.addRow("Organization Type:", self.org_type_combo)
        
        layout.addWidget(org_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_form = QFormLayout()
        additional_group.setLayout(additional_form)
        
        self.email_field = QLineEdit()
        self.registerField("user.email", self.email_field)
        additional_form.addRow("Email (optional):", self.email_field)
        
        self.phone_field = QLineEdit()
        self.registerField("user.phone", self.phone_field)
        additional_form.addRow("Phone (optional):", self.phone_field)
        
        layout.addWidget(additional_group)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def initializePage(self):
        """Initialize page contents when shown."""
        # Load any saved user information if available
        settings = QSettings("RadioForms", "App")
        self.name_field.setText(settings.value("UserInfo/Name", ""))
        self.callsign_field.setText(settings.value("UserInfo/Callsign", ""))
        self.position_field.setText(settings.value("UserInfo/Position", ""))
        self.org_name_field.setText(settings.value("OrgInfo/Name", ""))
        
        # Set org type if saved
        org_type = settings.value("OrgInfo/Type", "")
        if org_type and self.org_type_combo.findText(org_type) >= 0:
            self.org_type_combo.setCurrentText(org_type)
            
        # Set additional info
        self.email_field.setText(settings.value("UserInfo/Email", ""))
        self.phone_field.setText(settings.value("UserInfo/Phone", ""))


class DatabaseConfigPage(QWizardPage):
    """
    Database configuration page for the startup wizard.
    
    This page allows the user to configure where their data will be stored.
    """
    
    def __init__(self, parent=None):
        """Initialize the database configuration page."""
        super().__init__(parent)
        
        self.setTitle("Database Configuration")
        self.setSubTitle("Configure where RadioForms will store your data.")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Storage type group
        storage_group = QGroupBox("Storage Type")
        storage_layout = QVBoxLayout()
        storage_group.setLayout(storage_layout)
        
        # Radio buttons for storage options
        self.local_radio = QRadioButton("Local Storage (Recommended)")
        self.local_radio.setChecked(True)
        storage_layout.addWidget(self.local_radio)
        
        local_description = QLabel(
            "Store data in a local database file. This option works offline and "
            "is best for most users."
        )
        local_description.setWordWrap(True)
        local_description.setIndent(20)
        storage_layout.addWidget(local_description)
        
        self.custom_radio = QRadioButton("Custom Database Location")
        storage_layout.addWidget(self.custom_radio)
        
        custom_description = QLabel(
            "Specify a custom location for the database file. Use this option "
            "if you want to store the database on a removable drive or specific folder."
        )
        custom_description.setWordWrap(True)
        custom_description.setIndent(20)
        storage_layout.addWidget(custom_description)
        
        # Add storage group to layout
        layout.addWidget(storage_group)
        
        # Custom location container (shown only when custom option selected)
        self.custom_container = QWidget()
        custom_layout = QHBoxLayout()
        custom_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_container.setLayout(custom_layout)
        
        self.db_path_field = QLineEdit()
        self.registerField("db.custom_path", self.db_path_field)
        custom_layout.addWidget(self.db_path_field)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_db_location)
        custom_layout.addWidget(self.browse_button)
        
        layout.addWidget(self.custom_container)
        self.custom_container.setVisible(False)
        
        # Connect radio buttons to show/hide custom container
        self.local_radio.toggled.connect(self._on_storage_option_changed)
        self.custom_radio.toggled.connect(self._on_storage_option_changed)
        
        # Data retention group
        retention_group = QGroupBox("Data Retention")
        retention_layout = QVBoxLayout()
        retention_group.setLayout(retention_layout)
        
        retention_description = QLabel(
            "RadioForms can automatically create backup copies of your data. "
            "Backups are useful for recovering from data corruption or accidental deletions."
        )
        retention_description.setWordWrap(True)
        retention_layout.addWidget(retention_description)
        
        self.backup_check = QCheckBox("Enable automatic backups")
        self.backup_check.setChecked(True)
        self.registerField("db.auto_backup", self.backup_check)
        retention_layout.addWidget(self.backup_check)
        
        layout.addWidget(retention_group)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def _browse_db_location(self):
        """Open file dialog to select database location."""
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Database Files (*.db);;All Files (*)")
        file_dialog.setDefaultSuffix("db")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.db_path_field.setText(file_path)
            
    def _on_storage_option_changed(self):
        """Handle storage option radio button changes."""
        self.custom_container.setVisible(self.custom_radio.isChecked())
        
    def validatePage(self):
        """Validate page contents before proceeding."""
        if self.custom_radio.isChecked() and not self.db_path_field.text():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please specify a database file location or select the Local Storage option."
            )
            return False
            
        return True
        
    def initializePage(self):
        """Initialize page contents when shown."""
        # Set default database path to user's documents folder
        documents_path = Path.home() / "Documents" / "RadioForms"
        default_db_path = str(documents_path / "radioforms.db")
        self.db_path_field.setText(default_db_path)


class IncidentSetupPage(QWizardPage):
    """
    Incident setup page for the startup wizard.
    
    This page allows creating an initial incident to work with.
    """
    
    def __init__(self, parent=None):
        """Initialize the incident setup page."""
        super().__init__(parent)
        
        self.setTitle("Incident Setup")
        self.setSubTitle("Create your first incident or training exercise.")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        instruction_label = QLabel(
            "An incident represents an event or training exercise that you'll be creating forms for. "
            "You can create additional incidents later."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Incident information group
        incident_group = QGroupBox("Incident Information")
        incident_form = QFormLayout()
        incident_group.setLayout(incident_form)
        
        # Incident name
        self.name_field = QLineEdit()
        self.registerField("incident.name*", self.name_field)
        incident_form.addRow("Incident Name:", self.name_field)
        
        # Incident number
        self.number_field = QLineEdit()
        self.registerField("incident.number", self.number_field)
        incident_form.addRow("Incident Number:", self.number_field)
        
        # Incident type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Training/Exercise",
            "Planned Event",
            "Emergency Response",
            "Disaster Response",
            "Search and Rescue",
            "Other"
        ])
        self.registerField("incident.type", self.type_combo, "currentText")
        incident_form.addRow("Incident Type:", self.type_combo)
        
        # Start date
        self.date_field = QLineEdit()
        self.date_field.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.registerField("incident.date", self.date_field)
        incident_form.addRow("Start Date:", self.date_field)
        
        # Location
        self.location_field = QLineEdit()
        self.registerField("incident.location", self.location_field)
        incident_form.addRow("Location:", self.location_field)
        
        layout.addWidget(incident_group)
        
        # Operational period group
        op_group = QGroupBox("Operational Period")
        op_form = QFormLayout()
        op_group.setLayout(op_form)
        
        # Operational period
        self.op_field = QLineEdit()
        self.op_field.setText("1")
        self.registerField("incident.op_period", self.op_field)
        op_form.addRow("Operational Period:", self.op_field)
        
        # Op period start
        self.op_start_field = QLineEdit()
        self.op_start_field.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.registerField("incident.op_start", self.op_start_field)
        op_form.addRow("Period Start:", self.op_start_field)
        
        # Op period end
        end_time = datetime.datetime.now() + datetime.timedelta(hours=12)
        self.op_end_field = QLineEdit()
        self.op_end_field.setText(end_time.strftime("%Y-%m-%d %H:%M"))
        self.registerField("incident.op_end", self.op_end_field)
        op_form.addRow("Period End:", self.op_end_field)
        
        layout.addWidget(op_group)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def initializePage(self):
        """Initialize page contents when shown."""
        # Get user name to suggest incident name
        user_name = self.field("user.name")
        
        # Suggest training incident name
        if user_name:
            self.name_field.setText(f"{user_name}'s Training Incident")
        else:
            self.name_field.setText("Training Incident")
            
        # Set default incident type to Training
        self.type_combo.setCurrentText("Training/Exercise")


class FormSetupPage(QWizardPage):
    """
    Form setup page for the startup wizard.
    
    This page allows selecting which form types to enable.
    """
    
    def __init__(self, parent=None):
        """Initialize the form setup page."""
        super().__init__(parent)
        
        self.setTitle("Form Types")
        self.setSubTitle("Select the forms you want to use in RadioForms.")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        instruction_label = QLabel(
            "RadioForms supports a variety of ICS form types. Select the forms "
            "you expect to use. You can change these settings later."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Form selection grid
        form_grid = QGridLayout()
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 1)
        form_grid.setColumnStretch(2, 1)
        
        # Add form checkboxes
        self.form_checkboxes = {}
        
        # Most common forms
        common_group = QGroupBox("Common Forms")
        common_layout = QVBoxLayout()
        common_group.setLayout(common_layout)
        
        common_forms = [
            ("ICS-213", "General Message", True),
            ("ICS-214", "Activity Log", True),
            ("ICS-205", "Communications Plan", True),
            ("ICS-205A", "Communications List", True),
            ("ICS-309", "Communications Log", True)
        ]
        
        for form_id, form_name, default_enabled in common_forms:
            checkbox = QCheckBox(f"{form_id}: {form_name}")
            checkbox.setChecked(default_enabled)
            self.registerField(f"forms.{form_id}", checkbox)
            self.form_checkboxes[form_id] = checkbox
            common_layout.addWidget(checkbox)
            
        layout.addWidget(common_group)
        
        # Other forms group
        other_group = QGroupBox("Other Forms")
        other_layout = QGridLayout()
        other_group.setLayout(other_layout)
        
        other_forms = [
            ("ICS-201", "Incident Briefing", False),
            ("ICS-202", "Incident Objectives", False),
            ("ICS-203", "Organization Assignment List", False),
            ("ICS-204", "Assignment List", False),
            ("ICS-206", "Medical Plan", False),
            ("ICS-207", "Incident Organization Chart", False),
            ("ICS-208", "Safety Message/Plan", False),
            ("ICS-209", "Incident Status Summary", False),
            ("ICS-210", "Resource Status Change", False),
            ("ICS-211", "Check-In List", False),
            ("ICS-215", "Operational Planning Worksheet", False),
            ("ICS-215A", "Safety Analysis", False),
            ("ICS-217A", "Communications Resource Availability", False),
            ("ICS-218", "Support Vehicle/Equipment Inventory", False),
            ("ICS-220", "Air Operations Summary", False),
            ("ICS-221", "Demobilization Check-Out", False),
            ("ICS-225", "Incident Personnel Performance Rating", False)
        ]
        
        row, col = 0, 0
        for form_id, form_name, default_enabled in other_forms:
            checkbox = QCheckBox(f"{form_id}: {form_name}")
            checkbox.setChecked(default_enabled)
            self.registerField(f"forms.{form_id}", checkbox)
            self.form_checkboxes[form_id] = checkbox
            other_layout.addWidget(checkbox, row, col)
            
            col += 1
            if col > 2:  # 3 columns layout
                col = 0
                row += 1
                
        layout.addWidget(other_group)
        
        # Selection buttons
        button_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self._select_all_forms)
        button_layout.addWidget(select_all_button)
        
        select_none_button = QPushButton("Select None")
        select_none_button.clicked.connect(self._select_no_forms)
        button_layout.addWidget(select_none_button)
        
        select_common_button = QPushButton("Select Common Only")
        select_common_button.clicked.connect(self._select_common_forms)
        button_layout.addWidget(select_common_button)
        
        layout.addLayout(button_layout)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def _select_all_forms(self):
        """Select all form checkboxes."""
        for checkbox in self.form_checkboxes.values():
            checkbox.setChecked(True)
            
    def _select_no_forms(self):
        """Deselect all form checkboxes."""
        for checkbox in self.form_checkboxes.values():
            checkbox.setChecked(False)
            
    def _select_common_forms(self):
        """Select only common forms."""
        # First deselect all
        self._select_no_forms()
        
        # Then select common forms
        common_forms = ["ICS-213", "ICS-214", "ICS-205", "ICS-205A", "ICS-309"]
        for form_id in common_forms:
            if form_id in self.form_checkboxes:
                self.form_checkboxes[form_id].setChecked(True)


class CompletionPage(QWizardPage):
    """
    Completion page for the startup wizard.
    
    This page confirms the configuration and creates necessary resources.
    """
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        """
        Initialize the completion page.
        
        Args:
            config_manager: The application's configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setTitle("Setup Complete")
        self.setSubTitle("RadioForms has been configured and is ready to use.")
        
        self._config_manager = config_manager
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Status message
        self.status_label = QLabel(
            "Click 'Finish' to save your configuration and start using RadioForms."
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Summary of configuration
        summary_group = QGroupBox("Configuration Summary")
        summary_layout = QVBoxLayout()
        summary_group.setLayout(summary_layout)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def initializePage(self):
        """Initialize page contents when shown."""
        # Generate configuration summary
        summary = "Configuration Summary:\n\n"
        
        # User info
        summary += "User Information:\n"
        summary += f"- Name: {self.field('user.name')}\n"
        summary += f"- Callsign: {self.field('user.callsign')}\n"
        summary += f"- Position: {self.field('user.position')}\n\n"
        
        # Organization info
        summary += "Organization Information:\n"
        summary += f"- Name: {self.field('org.name')}\n"
        summary += f"- Type: {self.field('org.type')}\n\n"
        
        # Database info
        summary += "Database Configuration:\n"
        db_type = "Local Storage" if not self.field("db.custom_path") else "Custom Location"
        summary += f"- Storage Type: {db_type}\n"
        
        if db_type == "Custom Location":
            summary += f"- Database Path: {self.field('db.custom_path')}\n"
            
        summary += f"- Automatic Backups: {'Enabled' if self.field('db.auto_backup') else 'Disabled'}\n\n"
        
        # Incident info
        summary += "Incident Information:\n"
        summary += f"- Name: {self.field('incident.name')}\n"
        summary += f"- Number: {self.field('incident.number')}\n"
        summary += f"- Type: {self.field('incident.type')}\n"
        summary += f"- Date: {self.field('incident.date')}\n"
        summary += f"- Location: {self.field('incident.location')}\n\n"
        
        # Enabled forms
        summary += "Enabled Forms:\n"
        enabled_forms = []
        
        for field_name in self.wizard().registeredFields():
            if field_name.startswith("forms.") and self.field(field_name):
                form_id = field_name.split(".")[-1]
                enabled_forms.append(form_id)
                
        if enabled_forms:
            for form_id in enabled_forms:
                summary += f"- {form_id}\n"
        else:
            summary += "- No forms selected\n"
            
        # Set summary text
        self.summary_text.setPlainText(summary)
        
        # Apply the configuration
        try:
            self._apply_configuration()
            self.status_label.setText(
                "Configuration has been applied successfully. "
                "Click 'Finish' to start using RadioForms."
            )
        except Exception as e:
            self.status_label.setText(
                f"Error applying configuration: {str(e)}\n"
                "You can still click 'Finish' to continue, but some settings may not be applied."
            )
            
    def _apply_configuration(self):
        """Apply the configuration settings."""
        # Save user and organization information
        settings = QSettings("RadioForms", "App")
        
        # User info
        settings.setValue("UserInfo/Name", self.field("user.name"))
        settings.setValue("UserInfo/Callsign", self.field("user.callsign"))
        settings.setValue("UserInfo/Position", self.field("user.position"))
        settings.setValue("UserInfo/Email", self.field("user.email"))
        settings.setValue("UserInfo/Phone", self.field("user.phone"))
        
        # Organization info
        settings.setValue("OrgInfo/Name", self.field("org.name"))
        settings.setValue("OrgInfo/Type", self.field("org.type"))
        
        # Database settings
        db_path = ""
        if self.field("db.custom_path"):
            db_path = self.field("db.custom_path")
        else:
            # Use default path
            documents_path = Path.home() / "Documents" / "RadioForms"
            documents_path.mkdir(parents=True, exist_ok=True)
            db_path = str(documents_path / "radioforms.db")
            
        # Save database path to config manager
        self._config_manager.set_value("Database", "path", db_path)
        self._config_manager.set_value("Database", "auto_backup", 
                                      "true" if self.field("db.auto_backup") else "false")
                                      
        # Save enabled forms
        enabled_forms = []
        for field_name in self.wizard().registeredFields():
            if field_name.startswith("forms.") and self.field(field_name):
                form_id = field_name.split(".")[-1]
                enabled_forms.append(form_id)
                
        self._config_manager.set_value("Forms", "enabled_forms", ",".join(enabled_forms))
        
        # Save config file
        self._config_manager.save()


class StartupWizard(QWizard):
    """
    Startup wizard for RadioForms.
    
    This wizard guides the user through the initial setup process for
    the RadioForms application.
    """
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        """
        Initialize the startup wizard.
        
        Args:
            config_manager: The application's configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("RadioForms Setup Wizard")
        self.setMinimumSize(QSize(700, 500))
        
        # Set wizard style
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(UserInfoPage())
        self.addPage(DatabaseConfigPage())
        self.addPage(IncidentSetupPage())
        self.addPage(FormSetupPage())
        self.addPage(CompletionPage(config_manager))
        
        # Set button text
        self.setButtonText(QWizard.FinishButton, "Start RadioForms")
        self.setButtonText(QWizard.CancelButton, "Exit")
        
        # Connect signals
        self.finished.connect(self._on_finished)
        
    def _on_finished(self, result: int):
        """
        Handle wizard completion.
        
        Args:
            result: Wizard result (QDialog.Accepted or QDialog.Rejected)
        """
        if result == QWizard.Rejected:
            # Exit the application if wizard is cancelled
            if QMessageBox.question(
                self,
                "Exit Application?",
                "Setup is required for first use. Exit application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            ) == QMessageBox.Yes:
                QApplication.quit()
                

def run_startup_wizard(config_manager: ConfigManager) -> bool:
    """
    Run the startup wizard.
    
    Args:
        config_manager: The application's configuration manager
        
    Returns:
        True if the wizard was completed successfully, False otherwise
    """
    wizard = StartupWizard(config_manager)
    result = wizard.exec_()
    
    return result == QWizard.Accepted
