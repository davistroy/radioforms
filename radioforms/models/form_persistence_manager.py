#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Persistence Manager for RadioForms.

This module provides a central manager for form persistence operations,
integrating the form models with the DAO layer.
"""

from typing import Dict, Any, List, Optional, Type, Union, TypeVar
import os
import datetime
import uuid
from pathlib import Path

from radioforms.models.base_form import BaseFormModel
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.attachment_dao_refactored import AttachmentDAO

# Type variable for form classes
T = TypeVar('T', bound=BaseFormModel)


class FormPersistenceManager:
    """
    Manages form persistence operations using the DAO layer.
    
    This class provides a centralized interface for loading and saving forms,
    handling attachments, and managing form versions.
    """
    
    # Map form types to their model classes
    FORM_TYPE_MAP = {
        "ICS-213": EnhancedICS213Form,
        # Add other form types here as they're implemented
    }
    
    def __init__(self, form_dao: FormDAO, attachment_dao: Optional[AttachmentDAO] = None):
        """
        Initialize the form persistence manager.
        
        Args:
            form_dao: DAO for form operations
            attachment_dao: Optional DAO for attachment operations
        """
        self.form_dao = form_dao
        self.attachment_dao = attachment_dao
        
    def create_form(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new form of the specified type.
        
        Args:
            form_type: Type of form to create (e.g., "ICS-213")
            
        Returns:
            A new form instance, or None if the form type is not supported
        """
        form_class = self.FORM_TYPE_MAP.get(form_type)
        if not form_class:
            return None
            
        return form_class.create_with_dao(self.form_dao)
        
    def save_form(self, form: BaseFormModel, create_version: bool = True) -> str:
        """
        Save a form to the database.
        
        Args:
            form: Form to save
            create_version: Whether to create a new version of the form
            
        Returns:
            The saved form ID
        """
        # Update last_modified timestamp
        form.last_modified = datetime.datetime.now()
        
        # Convert to dictionary
        form_dict = form.to_dict()
        
        # Save or update the form
        if form.form_id and self.form_dao.find_by_id(form.form_id):
            # Update existing form
            self.form_dao.update(form_dict)
            form_id = form.form_id
            
            # Create version if requested
            if create_version and hasattr(self.form_dao, 'create_version'):
                try:
                    self.form_dao.create_version(form_id, form_dict)
                except (AttributeError, TypeError):
                    pass  # Version creation not supported
        else:
            # Create new form
            form_id = self.form_dao.create(form_dict)
            form.form_id = str(form_id)
            
        return form.form_id
        
    def load_form(self, form_id: str, version_id: Optional[str] = None) -> Optional[BaseFormModel]:
        """
        Load a form from the database.
        
        Args:
            form_id: ID of the form to load
            version_id: Optional version ID to load
            
        Returns:
            The loaded form instance, or None if not found
        """
        # Determine if we're loading a specific version
        if version_id and hasattr(self.form_dao, 'find_version_by_id'):
            try:
                form_dict = self.form_dao.find_version_by_id(version_id)
            except (AttributeError, TypeError):
                form_dict = None
        else:
            # Load current version
            form_dict = self.form_dao.find_by_id(form_id)
            
        # Return None if form not found
        if not form_dict:
            return None
            
        # Determine form type and instantiate appropriate class
        form_type = form_dict.get("form_type")
        form_class = self.FORM_TYPE_MAP.get(form_type)
        
        if not form_class:
            # If form_type not recognized, try finding "form_type" field or infer from structure
            for type_name, cls in self.FORM_TYPE_MAP.items():
                if form_dict.get("form_type") == type_name:
                    form_class = cls
                    break
                    
        if not form_class:
            # Default to first form type if we can't determine it
            form_class = next(iter(self.FORM_TYPE_MAP.values()))
            
        # Create form instance from dictionary
        return form_class.from_dict(form_dict)
        
    def delete_form(self, form_id: str) -> bool:
        """
        Delete a form from the database.
        
        Args:
            form_id: ID of the form to delete
            
        Returns:
            True if the form was deleted, False otherwise
        """
        return self.form_dao.delete(form_id)
        
    def get_form_versions(self, form_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            List of form version dictionaries, or empty list if not supported
        """
        if hasattr(self.form_dao, 'find_versions_by_form_id'):
            try:
                return self.form_dao.find_versions_by_form_id(form_id)
            except (AttributeError, TypeError):
                pass
                
        return []
        
    def find_forms(self, criteria: Dict[str, Any] = None, as_dict: bool = False) -> List[Union[BaseFormModel, Dict[str, Any]]]:
        """
        Find forms matching the specified criteria.
        
        Args:
            criteria: Dictionary of search criteria
            as_dict: Whether to return dictionaries (True) or form instances (False)
            
        Returns:
            List of forms or form dictionaries
        """
        criteria = criteria or {}
        
        # Use find_by method if available
        if hasattr(self.form_dao, 'find_by'):
            try:
                results = self.form_dao.find_by(criteria, as_dict=True)
            except (AttributeError, TypeError):
                # Fall back to find_all
                results = self.form_dao.find_all(as_dict=True)
                
                # Filter results manually if find_by not available
                if criteria:
                    filtered_results = []
                    for form_dict in results:
                        match = True
                        for key, value in criteria.items():
                            if key not in form_dict or form_dict[key] != value:
                                match = False
                                break
                        if match:
                            filtered_results.append(form_dict)
                    results = filtered_results
        else:
            # Fall back to find_all
            results = self.form_dao.find_all(as_dict=True)
            
            # Filter results manually if find_by not available
            if criteria:
                filtered_results = []
                for form_dict in results:
                    match = True
                    for key, value in criteria.items():
                        if key not in form_dict or form_dict[key] != value:
                            match = False
                            break
                    if match:
                        filtered_results.append(form_dict)
                results = filtered_results
                
        # Return dictionaries if requested
        if as_dict:
            return results
            
        # Convert dictionaries to form instances
        forms = []
        for form_dict in results:
            form_type = form_dict.get("form_type")
            form_class = self.FORM_TYPE_MAP.get(form_type)
            
            if not form_class:
                # If type not recognized, try finding form_type field
                for type_name, cls in self.FORM_TYPE_MAP.items():
                    if form_dict.get("form_type") == type_name:
                        form_class = cls
                        break
                        
            if not form_class:
                # Skip if we can't determine form type
                continue
                
            form = form_class.from_dict(form_dict)
            forms.append(form)
            
        return forms
        
    def add_attachment(self, form: BaseFormModel, file_path: str) -> Optional[str]:
        """
        Add an attachment to a form.
        
        Args:
            form: Form to add attachment to
            file_path: Path to the file to attach
            
        Returns:
            The attachment ID if successful, None otherwise
        """
        if not self.attachment_dao:
            return None
            
        if not os.path.exists(file_path):
            return None
            
        # Create the attachment
        try:
            form_id = form.form_id
            if not form_id:
                # Save the form if it doesn't have an ID yet
                form_id = self.save_form(form)
                form.form_id = form_id
                
            attachment = self.attachment_dao.create_from_file(
                int(form_id), file_path
            )
            
            # Add the attachment ID to the form
            if attachment and attachment.id:
                form.add_attachment(str(attachment.id))
                
                # Save the form again to update attachments list
                self.save_form(form, create_version=False)
                
                return str(attachment.id)
        except Exception as e:
            # Log error in a real application
            print(f"Error adding attachment: {e}")
            
        return None
        
    def remove_attachment(self, form: BaseFormModel, attachment_id: str) -> bool:
        """
        Remove an attachment from a form.
        
        Args:
            form: Form to remove attachment from
            attachment_id: ID of the attachment to remove
            
        Returns:
            True if the attachment was removed, False otherwise
        """
        if not self.attachment_dao:
            return False
            
        try:
            # First remove it from the form
            if not form.remove_attachment(attachment_id):
                return False
                
            # Save the form to update the attachments list
            self.save_form(form, create_version=False)
            
            # Delete the attachment from the database
            return self.attachment_dao.delete_with_file(int(attachment_id))
        except Exception as e:
            # Log error in a real application
            print(f"Error removing attachment: {e}")
            
        return False
        
    def get_form_attachments(self, form: BaseFormModel) -> List[Dict[str, Any]]:
        """
        Get all attachments for a form.
        
        Args:
            form: Form to get attachments for
            
        Returns:
            List of attachment dictionaries
        """
        if not self.attachment_dao or not form.attachments:
            return []
            
        attachments = []
        for attachment_id in form.attachments:
            try:
                attachment_info = self.attachment_dao.find_attachment_info(int(attachment_id))
                if attachment_info:
                    attachments.append(attachment_info)
            except Exception as e:
                # Log error in a real application
                print(f"Error getting attachment info: {e}")
                
        return attachments
