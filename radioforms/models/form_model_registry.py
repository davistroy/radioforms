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
from radioforms.models.enhanced_form_resolver import resolve_form_type, extract_form_type_from_id


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
            # Use direct SQL to bypass DAO issues
            conn = self._form_dao.db_manager.connect()
            
            # Load form data
            if version_id:
                cursor = conn.execute(
                    """
                    SELECT content FROM form_versions
                    WHERE version_id = ?
                    """,
                    (version_id,)
                )
                version_row = cursor.fetchone()
                if not version_row:
                    self._logger.warning(f"Form version with ID {version_id} not found")
                    return None
                
                # Parse version content
                try:
                    form_data = json.loads(version_row['content'])
                except (json.JSONDecodeError, TypeError):
                    form_data = {}
                
                # Get form type from form data
                form_type = form_data.get("form_type")
                
                # Also get form metadata
                cursor = conn.execute(
                    """
                    SELECT * FROM forms
                    WHERE form_id = ?
                    """,
                    (form_id,)
                )
                form_row = cursor.fetchone()
                if form_row:
                    # Add form metadata to form data
                    form_data.update({
                        "form_id": form_id,
                        "form_type": form_row["form_type"],
                        "state": form_row["state"],
                        "created_at": form_row["created_at"],
                        "updated_at": form_row["updated_at"]
                    })
            else:
                # Load current form data
                cursor = conn.execute(
                    """
                    SELECT * FROM forms
                    WHERE form_id = ?
                    """,
                    (form_id,)
                )
                form_row = cursor.fetchone()
                
                if not form_row:
                    self._logger.warning(f"Form with ID {form_id} not found")
                    return None
                    
                # Get form metadata
                form_data = dict(form_row)
                
                # Parse form content from data field
                if "data" in form_data and form_data["data"]:
                    try:
                        content_data = json.loads(form_data["data"])
                        # Add content data to form data
                        for key, value in content_data.items():
                            if key not in form_data:
                                form_data[key] = value
                    except json.JSONDecodeError:
                        self._logger.warning(f"Could not parse form data for form {form_id}")
            
            # Use enhanced form resolver for type resolution
            form_type = form_data.get("form_type")
            
            # If form type is not explicitly set, use the resolver
            if not form_type or not form_type.strip():
                resolved_type = resolve_form_type(form_data, form_id)
                form_type = resolved_type
                self._logger.info(f"Resolved form type {form_type} for form {form_id} using enhanced resolver")
                
            # Final check - ensure the form type is registered
            if not form_type:
                self._logger.warning(f"Could not resolve form type for form {form_id}")
                return None
                
            if form_type not in self._form_types:
                self._logger.warning(f"Form type {form_type} not registered")
                return None
                
            # Create form instance
            model_class = self._form_types[form_type]
            
            # Check if the form has a from_dict method
            if hasattr(model_class, 'from_dict') and callable(getattr(model_class, 'from_dict')):
                # Use the form's from_dict method
                form = model_class.from_dict(form_data)
            else:
                # Create a new instance and manually set attributes
                form = model_class()
                
                # Process JSON data if present
                if "data" in form_data and form_data["data"]:
                    try:
                        # Try to parse JSON data
                        json_data = json.loads(form_data["data"])
                        
                        # Update form attributes from JSON data
                        for key, value in json_data.items():
                            if hasattr(form, key):
                                setattr(form, key, value)
                    except json.JSONDecodeError:
                        self._logger.warning(f"Could not parse JSON data for form {form_id}")
                        
                # Set form metadata fields directly from form_data
                for key in ["form_id", "form_type", "state", "status", "created_at", "updated_at", "title"]:
                    if key in form_data and hasattr(form, key):
                        setattr(form, key, form_data[key])
                        
                # Also try to copy any other fields that might be in the form
                for key, value in form_data.items():
                    if key not in ["form_id", "form_type", "state", "status", "created_at", "updated_at", "data", "title"]:
                        if hasattr(form, key):
                            setattr(form, key, value)
            
            # Ensure the form ID is set
            form.form_id = form_id
            
            self._logger.debug(f"Loaded form of type {form_type} with ID {form_id}")
            
            return form
            
        except Exception as e:
            self._logger.error(f"Failed to load form {form_id}: {e}")
            return None
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
            
            # First try the form's save_to_dao method for best integration
            if hasattr(form, "save_to_dao") and callable(getattr(form, "save_to_dao")):
                try:
                    form_id = form.save_to_dao(self._form_dao, create_version)
                    if form_id:
                        return form_id
                except Exception as save_dao_error:
                    self._logger.warning(f"Form.save_to_dao failed, trying direct DAO methods: {save_dao_error}")
            
            # Convert to dictionary for storage
            if hasattr(form, "to_dict") and callable(getattr(form, "to_dict")):
                try:
                    form_dict = form.to_dict()
                except Exception as e:
                    self._logger.warning(f"Form.to_dict failed: {e}")
                    form_dict = {}
                    
                    # Fallback: manually extract attributes
                    for key, value in form.__dict__.items():
                        if not key.startswith("_"):
                            form_dict[key] = value
            else:
                # Extract attributes manually
                form_dict = {}
                for key, value in form.__dict__.items():
                    if not key.startswith("_"):
                        form_dict[key] = value
            
            # Process form state
            state = form_dict.get("state", "draft")
            if hasattr(state, "value"):
                # Handle Enum values
                state = state.value
                
            # Create a standardized database object that matches the schema
            db_object = {
                "form_id": form.form_id,
                "form_type": form.form_type,
                "state": state,  # Status field matches state
                "title": form_dict.get("title", "") or form_dict.get("subject", "") or form_dict.get("incident_name", "") or form.form_type,
                "incident_id": form_dict.get("incident_id", None),
                "creator_id": form_dict.get("creator_id", None),
                "created_at": form.created_at.isoformat() if isinstance(form.created_at, datetime.datetime) else form.created_at,
                "updated_at": form.updated_at.isoformat() if isinstance(form.updated_at, datetime.datetime) else form.updated_at,
                "data": json.dumps(form_dict)
            }
            
            # Attempt direct SQL interaction if needed 
            try:
                # Check if form already exists using direct SQL
                conn = self._form_dao.db_manager.connect()
                
                # Check if form exists
                cursor = conn.execute(
                    "SELECT form_id FROM forms WHERE form_id = ?", 
                    (form.form_id,)
                )
                
                existing = cursor.fetchone() is not None
                
                if existing:
                    # Update existing form using direct SQL
                    self._logger.info(f"Updating existing form with ID {form.form_id}")
                    conn.execute(
                        """
                        UPDATE forms SET
                            form_type = ?,
                            state = ?,
                            title = ?,
                            data = ?,
                            updated_at = ?
                        WHERE form_id = ?
                        """,
                        (
                            form.form_type,
                            state,
                            db_object["title"],
                            db_object["data"],
                            db_object["updated_at"],
                            form.form_id
                        )
                    )
                else:
                    # Create new form using direct SQL
                    self._logger.info(f"Creating new form with ID {form.form_id}")
                    conn.execute(
                        """
                        INSERT INTO forms (
                            form_id, form_type, state, title, 
                            data, created_at, updated_at, incident_id, created_by
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            form.form_id,
                            form.form_type,
                            state,
                            db_object["title"],
                            db_object["data"],
                            db_object["created_at"],
                            db_object["updated_at"],
                            db_object.get("incident_id"),
                            db_object.get("creator_id")
                        )
                    )
                
                conn.commit()
                
                # Fall back to DAO methods
                if hasattr(self._form_dao, 'create') and callable(getattr(self._form_dao, 'create')) and not existing:
                    try:
                        # Also try the DAO methods for logging purposes
                        created_id = self._form_dao.create(db_object)
                        if created_id != form.form_id:
                            self._logger.warning(f"DAO created ID ({created_id}) differs from form ID ({form.form_id})")
                    except Exception as e:
                        self._logger.debug(f"DAO create method failed, but direct SQL succeeded: {e}")
                elif hasattr(self._form_dao, 'update') and callable(getattr(self._form_dao, 'update')) and existing:
                    try:
                        # Also try the DAO methods for logging purposes
                        self._form_dao.update(form.form_id, db_object)
                    except Exception as e:
                        self._logger.debug(f"DAO update method failed, but direct SQL succeeded: {e}")
            except Exception as sql_error:
                self._logger.error(f"Direct SQL operation failed: {sql_error}")
                
                # Fall back to trying the DAO methods
                try:
                    if hasattr(self._form_dao, 'find_by_id') and callable(getattr(self._form_dao, 'find_by_id')):
                        existing = self._form_dao.find_by_id(form.form_id)
                    else:
                        # Assume it's a new form if we can't check
                        existing = None
                        
                    if existing:
                        # Update existing form
                        success = self._form_dao.update(form.form_id, db_object)
                        if not success:
                            self._logger.error(f"Failed to update form with ID {form.form_id}")
                            return None
                    else:
                        # Create new form
                        created_id = self._form_dao.create(db_object)
                        if not created_id:
                            self._logger.error(f"Failed to create form with ID {form.form_id}")
                            return None
                            
                        # Ensure form_id matches the created ID if it's different
                        if created_id != form.form_id:
                            form.form_id = created_id
                except Exception as dao_error:
                    self._logger.error(f"DAO operation failed after SQL failure: {dao_error}")
                    return None
            
            # Create version if requested
            if create_version and hasattr(self._form_dao, 'create_version'):
                try:
                    self._form_dao.create_version(form.form_id, form_dict)
                except Exception as version_error:
                    self._logger.warning(f"Failed to create form version: {version_error}")
            
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
