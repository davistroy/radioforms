#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Startup wizard for collecting user information and configuration.

This module provides a wizard interface for first-time setup and
configuration of the RadioForms application.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QCheckBox, QMessageBox, QProgressBar, QFrame, QGroupBox,
    QFormLayout
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon

from radioforms.config.config_manager import ConfigManager, SystemIntegrityChecker
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao import IncidentDAO


class WelcomePage(QWizardPage):
    """Welcome page for the startup wizard."""
    
    def __init__(self, parent=None):
        """Initialize the welcome page."""
        super().__init__(parent)
        
        self.setTitle("Welcome to RadioForms")
        self.setSubTitle("This wizard will help you set up the application for first use.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add welcome message
        welcome_label = QLabel(
            "RadioForms is designed to help emergency communicators create, "
            "manage, and transmit ICS forms during incidents. "
            "\n\n"
            "This wizard will guide you through the initial setup process, including: "
            "\n"
            "• Creating your user profile\n"
            "• Setting up an incident\n"
            "• Checking system requirements\n"
            "\n"
            "Click 'Next' to continue."
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        # Add logo
        # logo_label = QLabel()
        # logo_pixmap = QPixmap(":/images/logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(
        #     200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        # ))
        # logo_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(logo_label)
        
        self.setLayout(layout)


class UserProfilePage(QWizardPage):
    """Page for collecting user profile information."""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        """
        Initialize the user profile page.
        
        Args:
            config_manager: Configuration manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.existing_users = self.config_manager.get_users()
        
        self.setTitle("User Profile")
        self.setSubTitle("Please provide your information or select an existing profile.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add user selector if existing users
        self.user_selector = None
        if self.existing_users:
            user_group = QGroupBox("Existing Profiles")
            user_layout = QVBoxLayout()
            
            self.user_selector = QComboBox()
            self.user_selector.addItem("Create New Profile", None)
            for user in self.existing_users:
                display_name = f"{user['name']}"
                if user.get('call_sign'):
                    display_name += f" ({user['call_sign']})"
                self.user_selector.addItem(display_name, user['id'])
            
            user_layout.addWidget(self.user_selector)
            user_group.setLayout(user_layout)
            layout.addWidget(user_group)
            
            # Connect signal
            self.user_selector.currentIndexChanged.connect(self._on_user_changed)
        
        # Create user profile form
        form_group = QGroupBox("User Information")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter your full name")
        self.registerField("user.name*", self.name_edit)
        
        self.call_sign_edit = QLineEdit()
        self.call_sign_edit.setPlaceholderText("Enter your radio call sign (optional)")
        self.registerField("user.call_sign", self.call_sign_edit)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Call Sign:", self.call_sign_edit)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Add remember me checkbox
        self.remember_checkbox = QCheckBox("Remember this profile for next time")
        self.remember_checkbox.setChecked(True)
        self.registerField("user.remember", self.remember_checkbox)
        layout.addWidget(self.remember_checkbox)
        
        self.setLayout(layout)
        
        # If we have a current user, select it by default
        current_user = self.config_manager.get_current_user()
        if current_user and self.user_selector:
            for i in range(self.user_selector.count()):
                if self.user_selector.itemData(i) == current_user['id']:
                    self.user_selector.setCurrentIndex(i)
                    break
    
    def _on_user_changed(self, index):
        """
        Handle user selection change.
        
        Args:
            index: Selected index
        """
        user_id = self.user_selector.itemData(index)
        
        if user_id is None:
            # Clear the form for new user
            self.name_edit.clear()
            self.call_sign_edit.clear()
            self.name_edit.setEnabled(True)
            self.call_sign_edit.setEnabled(True)
        else:
            # Find the selected user
            for user in self.existing_users:
                if user['id'] == user_id:
                    # Populate the form with user data
                    self.name_edit.setText(user['name'])
                    self.call_sign_edit.setText(user.get('call_sign', ''))
                    break
            
            # Disable editing for existing users
            self.name_edit.setEnabled(False)
            self.call_sign_edit.setEnabled(False)
    
    def validatePage(self):
        """Validate the page and save user information."""
        # Get form values
        name = self.field("user.name")
        call_sign = self.field("user.call_sign")
        remember = self.field("user.remember")
        
        # If using existing user
        if self.user_selector and self.user_selector.currentData() is not None:
            user_id = self.user_selector.currentData()
            
            # Update the current user if needed
            if remember:
                self.config_manager.set_current_user(user_id)
            
            return True
        
        # Otherwise create a new user
        user_data = {
            'name': name,
            'call_sign': call_sign,
            'last_login': None  # Will be set by the system
        }
        
        user_id = self.config_manager.create_or_update_user(user_data)
        
        if user_id is None:
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save user profile. Please try again."
            )
            return False
        
        # Set as current user if remember is checked
        if remember:
            self.config_manager.set_current_user(user_id)
        
        return True


class IncidentPage(QWizardPage):
    """Page for collecting incident information."""
    
    def __init__(self, config_manager: ConfigManager, db_manager: DatabaseManager, parent=None):
        """
        Initialize the incident page.
        
        Args:
            config_manager: Configuration manager instance
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.incident_dao = IncidentDAO(db_manager)
        self.existing_incidents = self.incident_dao.get_all()
        
        self.setTitle("Incident Information")
        self.setSubTitle("Please provide information about the incident or exercise.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add incident selector if existing incidents
        self.incident_selector = None
        if self.existing_incidents:
            incident_group = QGroupBox("Existing Incidents")
            incident_layout = QVBoxLayout()
            
            self.incident_selector = QComboBox()
            self.incident_selector.addItem("Create New Incident", None)
            for incident in self.existing_incidents:
                self.incident_selector.addItem(incident['name'], incident['id'])
            
            incident_layout.addWidget(self.incident_selector)
            incident_group.setLayout(incident_layout)
            layout.addWidget(incident_group)
            
            # Connect signal
            self.incident_selector.currentIndexChanged.connect(self._on_incident_changed)
        
        # Create incident form
        form_group = QGroupBox("Incident Information")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter incident name")
        self.registerField("incident.name*", self.name_edit)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter incident description (optional)")
        self.registerField("incident.description", self.description_edit)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Description:", self.description_edit)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        self.setLayout(layout)
        
        # If we have a current incident, select it by default
        current_incident_id = self.config_manager.get_setting(ConfigManager.LAST_INCIDENT_ID)
        if current_incident_id and self.incident_selector:
            try:
                incident_id = int(current_incident_id)
                for i in range(self.incident_selector.count()):
                    if self.incident_selector.itemData(i) == incident_id:
                        self.incident_selector.setCurrentIndex(i)
                        break
            except (ValueError, TypeError):
                pass
    
    def _on_incident_changed(self, index):
        """
        Handle incident selection change.
        
        Args:
            index: Selected index
        """
        incident_id = self.incident_selector.itemData(index)
        
        if incident_id is None:
            # Clear the form for new incident
            self.name_edit.clear()
            self.description_edit.clear()
            self.name_edit.setEnabled(True)
            self.description_edit.setEnabled(True)
        else:
            # Find the selected incident
            for incident in self.existing_incidents:
                if incident['id'] == incident_id:
                    # Populate the form with incident data
                    self.name_edit.setText(incident['name'])
                    self.description_edit.setText(incident.get('description', ''))
                    break
            
            # Disable editing for existing incidents
            self.name_edit.setEnabled(False)
            self.description_edit.setEnabled(False)
    
    def validatePage(self):
        """Validate the page and save incident information."""
        # If using existing incident
        if self.incident_selector and self.incident_selector.currentData() is not None:
            incident_id = self.incident_selector.currentData()
            
            # Update the current incident
            self.config_manager.set_setting(ConfigManager.LAST_INCIDENT_ID, str(incident_id))
            
            return True
        
        # Otherwise create a new incident
        name = self.field("incident.name")
        description = self.field("incident.description")
        
        incident_data = {
            'name': name,
            'description': description,
            'start_date': None  # Will be set by the system
        }
        
        incident_id = self.incident_dao.create(incident_data)
        
        if incident_id is None:
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save incident information. Please try again."
            )
            return False
        
        # Set as current incident
        self.config_manager.set_setting(ConfigManager.LAST_INCIDENT_ID, str(incident_id))
        
        return True


class DiagnosticsPage(QWizardPage):
    """Page for system diagnostics and integrity checks."""
    
    def __init__(self, checker: SystemIntegrityChecker, parent=None):
        """
        Initialize the diagnostics page.
        
        Args:
            checker: System integrity checker instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.checker = checker
        self.checks_completed = False
        self.check_results = {}
        
        self.setTitle("System Diagnostics")
        self.setSubTitle("Checking system requirements and configuration.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add status message
        self.status_label = QLabel("Click 'Run Diagnostics' to check your system.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Add check results group
        results_group = QGroupBox("Check Results")
        results_layout = QGridLayout()
        
        # Create result labels
        self.file_system_label = QLabel("File System Access:")
        self.file_system_status = QLabel("Not Checked")
        
        self.disk_space_label = QLabel("Disk Space:")
        self.disk_space_status = QLabel("Not Checked")
        
        self.database_label = QLabel("Database Connection:")
        self.database_status = QLabel("Not Checked")
        
        # Add to grid
        results_layout.addWidget(self.file_system_label, 0, 0)
        results_layout.addWidget(self.file_system_status, 0, 1)
        
        results_layout.addWidget(self.disk_space_label, 1, 0)
        results_layout.addWidget(self.disk_space_status, 1, 1)
        
        results_layout.addWidget(self.database_label, 2, 0)
        results_layout.addWidget(self.database_status, 2, 1)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Add errors group
        self.errors_group = QGroupBox("Errors")
        errors_layout = QVBoxLayout()
        self.errors_text = QLabel("No errors detected.")
        self.errors_text.setWordWrap(True)
        errors_layout.addWidget(self.errors_text)
        self.errors_group.setLayout(errors_layout)
        self.errors_group.setVisible(False)
        layout.addWidget(self.errors_group)
        
        # Add run button
        self.run_button = QPushButton("Run Diagnostics")
        self.run_button.clicked.connect(self._run_diagnostics)
        layout.addWidget(self.run_button)
        
        self.setLayout(layout)
    
    def _run_diagnostics(self):
        """Run system diagnostics checks."""
        # Update UI
        self.status_label.setText("Running diagnostics...")
        self.progress_bar.setValue(10)
        self.run_button.setEnabled(False)
        
        # Clear previous errors
        self.errors_group.setVisible(False)
        self.errors_text.setText("No errors detected.")
        
        # Run the checks
        success, results = self.checker.check_all()
        self.check_results = results
        self.checks_completed = True
        
        # Update progress
        self.progress_bar.setValue(100)
        
        # Update status labels
        all_errors = []
        
        # File system check
        fs_result = results.get('file_system', {})
        if fs_result.get('success', False):
            self.file_system_status.setText("✅ Passed")
        else:
            self.file_system_status.setText("❌ Failed")
            all_errors.extend(fs_result.get('errors', []))
        
        # Disk space check
        disk_result = results.get('disk_space', {})
        if disk_result.get('success', False):
            self.disk_space_status.setText("✅ Passed")
        else:
            self.disk_space_status.setText("❌ Failed")
            all_errors.extend(disk_result.get('errors', []))
        
        # Database check
        db_result = results.get('database', {})
        if db_result.get('success', False):
            self.database_status.setText("✅ Passed")
        else:
            self.database_status.setText("❌ Failed")
            all_errors.extend(db_result.get('errors', []))
        
        # Update overall status
        if success:
            self.status_label.setText("All diagnostics passed successfully!")
        else:
            self.status_label.setText("Some diagnostics failed. See errors below.")
            self.errors_group.setVisible(True)
            self.errors_text.setText("\n".join(all_errors))
        
        # Re-enable button
        self.run_button.setEnabled(True)
    
    def isComplete(self):
        """Check if the page is complete."""
        return self.checks_completed
    
    def validatePage(self):
        """Validate the page."""
        # If checks haven't been run, run them now
        if not self.checks_completed:
            self._run_diagnostics()
        
        # If any check failed, ask if the user wants to continue
        all_success = (
            self.check_results.get('file_system', {}).get('success', False) and
            self.check_results.get('disk_space', {}).get('success', False) and
            self.check_results.get('database', {}).get('success', False)
        )
        
        if not all_success:
            response = QMessageBox.warning(
                self,
                "Diagnostics Failed",
                "Some system checks failed. Do you want to continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return response == QMessageBox.Yes
        
        return True


class CompletionPage(QWizardPage):
    """Completion page for the startup wizard."""
    
    def __init__(self, parent=None):
        """Initialize the completion page."""
        super().__init__(parent)
        
        self.setTitle("Setup Complete")
        self.setSubTitle("The application is now ready to use.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add completion message
        complete_label = QLabel(
            "Congratulations! RadioForms is now set up and ready to use. "
            "\n\n"
            "You can now start creating and managing ICS forms for your incident. "
            "\n\n"
            "Click 'Finish' to start using the application."
        )
        complete_label.setWordWrap(True)
        layout.addWidget(complete_label)
        
        self.setLayout(layout)


class StartupWizard(QWizard):
    """
    Wizard for initial application setup and configuration.
    
    This wizard guides the user through the process of setting up the
    application for first use, including creating a user profile,
    configuring an incident, and checking system requirements.
    """
    
    def __init__(self, db_manager: DatabaseManager, app_directory: str, parent=None):
        """
        Initialize the startup wizard.
        
        Args:
            db_manager: Database manager instance
            app_directory: Application directory path
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("RadioForms Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Create configuration manager and system checker
        self.config_manager = ConfigManager(db_manager)
        self.system_checker = SystemIntegrityChecker(db_manager, app_directory)
        
        # Set up pages
        self.setPage(0, WelcomePage(self))
        self.setPage(1, UserProfilePage(self.config_manager, self))
        self.setPage(2, IncidentPage(self.config_manager, db_manager, self))
        self.setPage(3, DiagnosticsPage(self.system_checker, self))
        self.setPage(4, CompletionPage(self))
        
        # Configure wizard buttons
        self.setButtonText(QWizard.FinishButton, "Start Application")
        
        # Set minimum size
        self.setMinimumSize(600, 400)
    
    def accept(self):
        """Handle wizard completion."""
        # Mark first run as completed
        self.config_manager.set_setting(ConfigManager.FIRST_RUN, "false")
        
        # Call parent implementation
        super().accept()
