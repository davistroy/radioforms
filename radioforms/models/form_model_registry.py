#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Model Registry for RadioForms.

This module provides a registry for form models, allowing the application
to create, load, and manipulate form data using a common interface.
"""

import logging
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional, Type, Union, cast

from radioforms.database.dao.form_dao_refactored import FormDAO


class FormModelRegistry:
    """
    Registry for form models.
    
    This class provides a central registry for form models, allowing the application
    to create, load, and manipulate form data using a common interface.
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'FormModelRegistry':
        """
        Get the singleton instance of the registry.
        
        Returns:
            FormModelRegistry instance
        """
        if cls._instance is None:
            cls._instance = FormModelRegistry()
        return cls._instance
        
    def __init__(self):
        """Initialize the form model registry."""
        # Logger
        self._logger = logging.getLogger(__name__)
        
        # Form type to model class mapping
        self._form_types = {}
        
        # Form DAO for data access
        self._form_dao = None
        
        # Register built-in form types
        self._register_builtin_types()
        
    def _register_builtin_types(self):
        """Register built-in form types."""
        try:
            # Import form models
            from radioforms.models.enhanced_ics213_form import EnhancedICS213Form
            from radioforms.models.enhanced_ics214_form import EnhancedICS214Form
            
            # Register form types
            self.register_form_type("ICS-213", EnhancedICS213Form)
            self.register_form_type("ICS-214", EnhancedICS214Form)
            
        except ImportError as e:
            self._logger.warning(f"Could not register built-in form types: {e}")
            
    def set_form_dao(self, form_dao: FormDAO):
        """
        Set the form DAO for data access.
        
        Args:
            form_dao: Form DAO instance
        """
        self._form_dao = form_dao
        
    def register_form_type(self, form_type: str, model_class: Type):
        """
        Register a form type with a model class.
        
        Args:
            form_type: Form type identifier
            model_class: Form model class
        """
        self._form_types[form_type] = model_class
        self._logger.debug(f"Registered form type {form_type}")
        
    def register_model(self, form_type: str, model_class: Type):
        """
        Alias for register_form_type for backward compatibility.
        
        Args:
            form_type: Form type identifier
            model_class: Form model class
        """
        return self.register_form_type(form_type, model_class)
        
    def unregister_model(self, form_type: str):
        """
        Unregister a form type.
        
        Args:
            form_type: Form type identifier to unregister
        """
        if form_type in self._form_types:
            del self._form_types[form_type]
            self._logger.debug(f"Unregistered form type {form_type}")
        
    def get_model_class(self, form_type: str) -> Optional[Type]:
        """
        Get the model class for a form type.
        
        Args:
            form_type: Form type identifier
            
        Returns:
            Model class, or None if type not registered
        """
        return self._form_types.get(form_type)
        
    def get_registered_types(self) -> List[str]:
        """
        Get the list of registered form types.
        
        Returns:
            List of form type identifiers
        """
        return list(self._form_types.keys())
        
    def get_form_template(self, form_type: str) -> Optional[Any]:
        """
        Get a blank template for a form type.
        
        Args:
            form_type: Form type identifier
            
        Returns:
            A new form instance configured as a template, or None if type not registered
        """
        if form_type not in self._form_types:
            self._logger.warning(f"Form type {form_type} not registered")
            return None
            
        # Create form instance
        model_class = self._form_types[form_type]
        form = model_class()
        
        # Set as template
        form.form_type = form_type
        form.form_id = None  # Templates have no ID
        form.created_at = datetime.datetime.now()
        form.updated_at = form.created_at
        form.state = "draft"
        form.is_template = True
        
        return form
        
    def create_form_with_dao(self, form_type: str) -> Optional[Any]:
        """
        Create a form and save it using the DAO.
        
        Args:
            form_type: Form type identifier
            
        Returns:
            The created form, or None if failed
        """
        form = self.create_form(form_type)
        if form and self._form_dao:
            form_id = self.save_form(form)
            if form_id:
                return form
        return None
        
    def create_form(self, form_type: str) -> Optional[Any]:
        """
        Create a new form instance of the specified type.
        
        Args:
            form_type: Form type identifier
            
        Returns:
            Form instance, or None if type not registered
        """
        if form_type not in self._form_types:
            self._logger.warning(f"Form type {form_type} not registered")
            return None
            
        # Create form instance
        model_class = self._form_types[form_type]
        form = model_class()
        
        # Set initial values
        form.form_type = form_type
        form.form_id = str(uuid.uuid4())
        form.created_at = datetime.datetime.now()
        form.updated_at = form.created_at
        form.state = "draft"
        
        self._logger.debug(f"Created form of type {form_type} with ID {form.form_id}")
        
        return form
        
    def load_form(self, form_id: str, version_id: str = None) -> Optional[Any]:
        """
        Load a form from the database.
        
        Args:
            form_id: Form ID
            version_id: Optional version ID to load a specific version
            
        Returns:
            Form instance, or None if not found
        """
        if self._form_dao is None:
            self._logger.error("Form DAO not set")
            return None
            
        try:
            # Load form data from DAO
            form_data = self._form_dao.find_by_id(form_id, as_dict=True)
            
            if not form_data:
                self._logger.warning(f"Form with ID {form_id} not found")
                return None
                
            # Get form type
            form_type = form_data.get("form_type")
            
            if form_type not in self._form_types:
                self._logger.warning(f"Form type {form_type} not registered")
                return None
                
            # Create form instance
            model_class = self._form_types[form_type]
            form = model_class()
            
            # Load data into form
            try:
                # First try to parse as JSON
                form_data_json = json.loads(form_data.get("data", "{}"))
                form.__dict__.update(form_data_json)
            except (json.JSONDecodeError, TypeError):
                # If that fails, just use the data directly for test mocks
                for key, value in form_data.items():
                    if key not in ["form_id", "form_type", "state", "created_at", "updated_at"]:
                        setattr(form, key, value)
            
            # Set metadata
            form.form_id = form_id
            form.form_type = form_type
            form.state = form_data.get("state", "draft")
            form.created_at = form_data.get("created_at")
            form.updated_at = form_data.get("updated_at")
            
            self._logger.debug(f"Loaded form of type {form_type} with ID {form_id}")
            
            return form
            
        except Exception as e:
            self._logger.error(f"Failed to load form {form_id}: {e}")
            return None
            
    def save_form(self, form: Any, create_version: bool = False) -> Optional[str]:
        """
        Save a form to the database.
        
        Args:
            form: Form instance
            create_version: Whether to create a version of the form
            
        Returns:
            Form ID, or None if save failed
        """
        if self._form_dao is None:
            self._logger.error("Form DAO not set")
            return None
            
        try:
            # Ensure form has required fields
            if not hasattr(form, "form_id") or not form.form_id:
                form.form_id = str(uuid.uuid4())
                
            if not hasattr(form, "created_at") or not form.created_at:
                form.created_at = datetime.datetime.now()
                
            if not hasattr(form, "updated_at") or not form.updated_at:
                form.updated_at = datetime.datetime.now()
            else:
                form.updated_at = datetime.datetime.now()
                
            if not hasattr(form, "state") or not form.state:
                form.state = "draft"
            
            # Ensure form_type is set
            if not hasattr(form, "form_type") or not form.form_type:
                # Try to get form type from get_form_type method if available
                if hasattr(form, "get_form_type") and callable(getattr(form, "get_form_type")):
                    form.form_type = form.get_form_type()
                else:
                    self._logger.error("Form type not set and cannot be determined")
                    return None
                
            # Try to use the form's to_dict method first
            if hasattr(form, "to_dict") and callable(getattr(form, "to_dict")):
                try:
                    form_dict = form.to_dict()
                    
                    # Create DAO object from form dict
                    dao_object = {
                        "form_id": form.form_id,
                        "form_type": form.form_type,
                        "state": form_dict.get("state", "draft"),
                        "status": form_dict.get("status", "draft"),
                        "data": json.dumps(form_dict),
                        "created_at": form.created_at.isoformat() if isinstance(form.created_at, datetime.datetime) else form.created_at,
                        "updated_at": form.updated_at.isoformat() if isinstance(form.updated_at, datetime.datetime) else form.updated_at,
                        "title": form_dict.get("title", "") or form_dict.get("subject", "") or form_dict.get("incident_name", "") or form.form_type,
                        "incident_id": form_dict.get("incident_id", None),
                        "creator_id": form_dict.get("creator_id", None),
                    }
                except Exception as e:
                    self._logger.warning(f"Failed to use to_dict method, falling back: {e}")
                    
                    # Fall back to the old approach
                    form_data = {}
                    for key, value in form.__dict__.items():
                        # Skip special fields that will be stored separately
                        if key.startswith("_") or key in ["form_id", "form_type", "state", "created_at", "updated_at"]:
                            continue
                            
                        # Handle special types
                        if isinstance(value, (datetime.datetime, datetime.date)):
                            form_data[key] = value.isoformat()
                        else:
                            form_data[key] = value
                            
                    # Create DAO object from form attributes
                    dao_object = {
                        "form_id": form.form_id,
                        "form_type": form.form_type,
                        "state": getattr(form.state, "value", form.state) if hasattr(form, "state") else "draft",
                        "status": getattr(form.state, "value", form.state) if hasattr(form, "state") else "draft",
                        "data": json.dumps(form_data),
                        "created_at": form.created_at.isoformat() if isinstance(form.created_at, datetime.datetime) else form.created_at,
                        "updated_at": form.updated_at.isoformat() if isinstance(form.updated_at, datetime.datetime) else form.updated_at,
                        "title": getattr(form, "subject", "") or getattr(form, "incident_name", "") or form.form_type,
                    }
            else:
                # Fall back to the old approach
                form_data = {}
                for key, value in form.__dict__.items():
                    # Skip special fields that will be stored separately
                    if key.startswith("_") or key in ["form_id", "form_type", "state", "created_at", "updated_at"]:
                        continue
                        
                    # Handle special types
                    if isinstance(value, (datetime.datetime, datetime.date)):
                        form_data[key] = value.isoformat()
                    else:
                        form_data[key] = value
                        
                # Create DAO object from form attributes
                dao_object = {
                    "form_id": form.form_id,
                    "form_type": form.form_type,
                    "state": getattr(form.state, "value", form.state) if hasattr(form, "state") else "draft",
                    "status": getattr(form.state, "value", form.state) if hasattr(form, "state") else "draft",
                    "data": json.dumps(form_data),
                    "created_at": form.created_at.isoformat() if isinstance(form.created_at, datetime.datetime) else form.created_at,
                    "updated_at": form.updated_at.isoformat() if isinstance(form.updated_at, datetime.datetime) else form.updated_at,
                    "title": getattr(form, "subject", "") or getattr(form, "incident_name", "") or form.form_type,
                }
            
            # First try the form's save_to_dao method for best integration
            if hasattr(form, "save_to_dao") and callable(getattr(form, "save_to_dao")):
                try:
                    form_id = form.save_to_dao(self._form_dao, create_version)
                    if form_id:
                        return form_id
                except Exception as save_dao_error:
                    self._logger.warning(f"Form.save_to_dao failed, trying direct DAO methods: {save_dao_error}")
            
            # Fall back to direct DAO operations
            try:
                existing_form = self._form_dao.find_by_id(form.form_id)
                
                if existing_form:
                    # Update existing form
                    self._form_dao.update(form.form_id, dao_object)
                else:
                    # Create new form
                    self._form_dao.create(dao_object)
            except Exception as e:
                self._logger.error(f"Failed to save form using DAO: {e}")
                raise
                
            self._logger.debug(f"Saved form of type {form.form_type} with ID {form.form_id}")
            
            return form.form_id
            
        except Exception as e:
            self._logger.error(f"Failed to save form: {e}")
            return None
            
    def find_forms(self, criteria: Dict[str, Any], as_dict: bool = False) -> List[Any]:
        """
        Find forms matching the criteria.
        
        Args:
            criteria: Search criteria
            as_dict: Whether to return dictionaries instead of form objects
            
        Returns:
            List of form objects or dictionaries
        """
        if self._form_dao is None:
            self._logger.error("Form DAO not set")
            return []
            
        try:
            # Find forms using DAO
            forms = self._form_dao.find_by_fields(criteria, as_dict=True)
            
            if as_dict:
                return forms
                
            # Convert to form objects
            result = []
            for form_data in forms:
                form_id = form_data.get("form_id")
                form = self.load_form(form_id)
                if form:
                    result.append(form)
                    
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to find forms: {e}")
            return []
            
    def delete_form(self, form_id: str) -> bool:
        """
        Delete a form from the database.
        
        Args:
            form_id: Form ID
            
        Returns:
            True if the delete was successful, False otherwise
        """
        if self._form_dao is None:
            self._logger.error("Form DAO not set")
            return False
            
        try:
            # Delete form using DAO
            success = self._form_dao.delete(form_id)
            
            if success:
                self._logger.debug(f"Deleted form with ID {form_id}")
                
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to delete form {form_id}: {e}")
            return False
