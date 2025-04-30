#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Controller module for RadioForms.

This module provides API-like access to the application's data, leveraging 
the dictionary-based interface provided by the DAO layer to efficiently
return data for UI components and external interfaces.
"""

from typing import Dict, Any, List, Optional, Union
import datetime
import json

from PySide6.QtCore import QObject, Signal, Slot

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao import IncidentDAO
from radioforms.database.dao.form_dao import FormDAO
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.dao.attachment_dao import AttachmentDAO
from radioforms.database.dao.setting_dao import SettingDAO
from radioforms.database.models.form import FormStatus


class APIController(QObject):
    """
    Controller that provides dictionary-based data access for UI components
    and external interfaces.
    
    This controller leverages the dictionary mode of the DAO layer to 
    efficiently retrieve and return data in a format that's easily
    consumable by UI components and API endpoints.
    """
    
    # Signals
    data_updated = Signal(str, object)  # entity_type, data
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        """
        Initialize the API controller.
        
        Args:
            db_manager: Database manager for database access
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Initialize DAOs with the provided database manager
        self.incident_dao = IncidentDAO(db_manager)
        self.form_dao = FormDAO(db_manager)
        self.user_dao = UserDAO(db_manager)
        self.attachment_dao = AttachmentDAO(db_manager)
        self.setting_dao = SettingDAO(db_manager)
    
    # ----- Incident API Methods -----
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """
        Get all active incidents as dictionaries.
        
        Returns:
            List of active incident data dictionaries
        """
        return self.incident_dao.find_active_incidents(as_dict=True)
    
    def get_incident(self, incident_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an incident by ID as a dictionary.
        
        Args:
            incident_id: ID of the incident to retrieve
            
        Returns:
            Incident data dictionary if found, None otherwise
        """
        return self.incident_dao.find_by_id(incident_id, as_dict=True)
    
    def create_incident(self, incident_data: Dict[str, Any]) -> int:
        """
        Create a new incident using dictionary data.
        
        Args:
            incident_data: Dictionary containing incident data
            
        Returns:
            ID of the created incident
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if 'name' not in incident_data or not incident_data['name']:
            raise ValueError("Incident name is required")
            
        # Validate data types
        if not isinstance(incident_data.get('name', ''), str):
            raise ValueError("Incident name must be a string")
            
        if 'description' in incident_data and not isinstance(incident_data['description'], str):
            raise ValueError("Incident description must be a string")
            
        # Ensure created_at and updated_at are set
        now = datetime.datetime.now()
        if 'created_at' not in incident_data:
            incident_data['created_at'] = now
        if 'updated_at' not in incident_data:
            incident_data['updated_at'] = now
            
        incident_id = self.incident_dao.create(incident_data)
        
        # Signal that data has been updated
        if incident_id:
            self.data_updated.emit('incident', self.get_incident(incident_id))
            
        return incident_id
    
    def update_incident(self, incident_id: int, incident_data: Dict[str, Any]) -> bool:
        """
        Update an incident using dictionary data.
        
        Args:
            incident_id: ID of the incident to update
            incident_data: Dictionary containing incident data to update
            
        Returns:
            True if the incident was updated, False otherwise
        """
        # Ensure updated_at is set
        if 'updated_at' not in incident_data:
            incident_data['updated_at'] = datetime.datetime.now()
            
        success = self.incident_dao.update(incident_id, incident_data)
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('incident', self.get_incident(incident_id))
            
        return success
    
    def close_incident(self, incident_id: int) -> bool:
        """
        Close an incident.
        
        Args:
            incident_id: ID of the incident to close
            
        Returns:
            True if the incident was closed, False otherwise
        """
        success = self.incident_dao.close_incident(incident_id)
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('incident', self.get_incident(incident_id))
            
        return success
    
    def reopen_incident(self, incident_id: int) -> bool:
        """
        Reopen an incident.
        
        Args:
            incident_id: ID of the incident to reopen
            
        Returns:
            True if the incident was reopened, False otherwise
        """
        success = self.incident_dao.reopen_incident(incident_id)
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('incident', self.get_incident(incident_id))
            
        return success
    
    def get_incident_stats(self) -> Dict[str, int]:
        """
        Get incident statistics.
        
        Returns:
            Dictionary with incident statistics
        """
        return self.incident_dao.get_incident_stats()
    
    # ----- Form API Methods -----
    
    def get_forms_for_incident(self, incident_id: int) -> List[Dict[str, Any]]:
        """
        Get all forms for an incident.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            List of form data dictionaries
        """
        return self.form_dao.find_by_incident(incident_id, as_dict=True)
    
    def get_form(self, form_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a form by ID.
        
        Args:
            form_id: ID of the form to retrieve
            
        Returns:
            Form data dictionary if found, None otherwise
        """
        return self.form_dao.find_by_id(form_id, as_dict=True)
    
    def get_form_with_content(self, form_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a form with its content by ID.
        
        Args:
            form_id: ID of the form to retrieve
            
        Returns:
            Dictionary with 'form' and 'content' keys if found, None otherwise
        """
        result = self.form_dao.find_with_content(form_id, as_dict=True)
        if result:
            form_dict, content_dict = result
            return {
                'form': form_dict,
                'content': content_dict
            }
        return None
    
    def create_form_with_content(self, form_data: Dict[str, Any], content: Dict[str, Any], 
                               user_id: Optional[int] = None) -> int:
        """
        Create a new form with content.
        
        Args:
            form_data: Dictionary containing form data
            content: Dictionary containing form content
            user_id: ID of the user creating the form (optional)
            
        Returns:
            ID of the created form
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields in form_data
        if 'incident_id' not in form_data or not form_data['incident_id']:
            raise ValueError("Form must be associated with an incident")
            
        if 'form_type' not in form_data or not form_data['form_type']:
            raise ValueError("Form type is required")
            
        if 'title' not in form_data or not form_data['title']:
            raise ValueError("Form title is required")
            
        # Validate data types
        if not isinstance(form_data.get('incident_id'), int):
            raise ValueError("Incident ID must be an integer")
            
        if not isinstance(form_data.get('form_type', ''), str):
            raise ValueError("Form type must be a string")
            
        if not isinstance(form_data.get('title', ''), str):
            raise ValueError("Form title must be a string")
            
        # Validate content is a dictionary
        if not isinstance(content, dict):
            raise ValueError("Form content must be a dictionary")
            
        # Ensure content is not empty
        if not content:
            raise ValueError("Form content cannot be empty")
            
        # Set timestamps if not present
        now = datetime.datetime.now()
        if 'created_at' not in form_data:
            form_data['created_at'] = now
        if 'updated_at' not in form_data:
            form_data['updated_at'] = now
            
        form_id = self.form_dao.create_with_content(form_data, content, user_id)
        
        # Signal that data has been updated
        if form_id:
            self.data_updated.emit('form', self.get_form(form_id))
            
        return form_id
    
    def update_form_with_content(self, form_id: int, form_data: Dict[str, Any], 
                               content: Dict[str, Any], user_id: Optional[int] = None) -> bool:
        """
        Update a form and its content.
        
        Args:
            form_id: ID of the form to update
            form_data: Dictionary containing form data
            content: Dictionary containing form content
            user_id: ID of the user updating the form (optional)
            
        Returns:
            True if the form was updated, False otherwise
        """
        # First update the form data
        self.form_dao.update(form_id, form_data)
        
        # Then update the content
        form = self.form_dao.find_by_id(form_id)
        success = self.form_dao.update_with_content(form, content, user_id)
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('form', self.get_form_with_content(form_id))
            
        return success
    
    def update_form_status(self, form_id: int, status: Union[FormStatus, str]) -> bool:
        """
        Update a form's status.
        
        Args:
            form_id: ID of the form to update
            status: New status (FormStatus enum or string)
            
        Returns:
            True if the form status was updated, False otherwise
        """
        success = self.form_dao.update_status(form_id, status)
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('form', self.get_form(form_id))
            
        return success
    
    def search_forms(self, search_term: str, incident_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for forms.
        
        Args:
            search_term: Term to search for
            incident_id: Optional incident ID to filter by
            
        Returns:
            List of matching form data dictionaries
        """
        forms = self.form_dao.search_forms(search_term, incident_id)
        return [self.form_dao.to_dict(form) for form in forms]
    
    def get_recent_forms(self, limit: int = 10, incident_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recently updated forms.
        
        Args:
            limit: Maximum number of forms to return
            incident_id: Optional incident ID to filter by
            
        Returns:
            List of recent form data dictionaries
        """
        forms = self.form_dao.find_recent_forms(limit, incident_id)
        return [self.form_dao.to_dict(form) for form in forms]
    
    # ----- User API Methods -----
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User data dictionary if found, None otherwise
        """
        return self.user_dao.find_by_id(user_id, as_dict=True)
    
    def get_user_by_call_sign(self, call_sign: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by call sign.
        
        Args:
            call_sign: Call sign to look up
            
        Returns:
            User data dictionary if found, None otherwise
        """
        user = self.user_dao.find_by_call_sign(call_sign)
        return self.user_dao.to_dict(user) if user else None
    
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            ID of the created user
        """
        user_id = self.user_dao.create(user_data)
        
        # Signal that data has been updated
        if user_id:
            self.data_updated.emit('user', self.get_user(user_id))
            
        return user_id
    
    # ----- Settings API Methods -----
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if setting is not found
            
        Returns:
            Setting value or default if not found
        """
        return self.setting_dao.get_value(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if the setting was set, False otherwise
        """
        setting = self.setting_dao.set_value(key, value)
        success = setting is not None
        
        # Signal that data has been updated
        if success:
            self.data_updated.emit('setting', {'key': key, 'value': value})
            
        return success
    
    def get_settings_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """
        Get settings by prefix.
        
        Args:
            prefix: Prefix to filter by
            
        Returns:
            Dictionary of settings
        """
        return self.setting_dao.get_settings_as_dict(prefix)
    
    # ----- Attachment API Methods -----
    
    def get_attachments_for_form(self, form_id: int) -> List[Dict[str, Any]]:
        """
        Get all attachments for a form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            List of attachment data dictionaries
        """
        attachments = self.attachment_dao.find_by_form(form_id)
        return [self.attachment_dao.to_dict(attachment) for attachment in attachments]
    
    def get_attachment_info(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get information about an attachment.
        
        Args:
            attachment_id: ID of the attachment
            
        Returns:
            Attachment information dictionary
        """
        return self.attachment_dao.get_attachment_info(attachment_id)
