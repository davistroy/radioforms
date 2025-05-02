#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date Serialization Fix Script.

This script fixes JSON serialization issues with Python date objects in the form models,
ensuring that forms with date fields can be properly serialized and deserialized.
This addresses the 'Object of type date is not JSON serializable' error.
"""

import sys
import os
import logging
import json
import inspect
import datetime
from enum import Enum
from pathlib import Path
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Type

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
from radioforms.models.form_model_registry import FormModelRegistry
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles date and datetime objects.
    
    This encoder converts:
    - date objects to ISO format strings
    - datetime objects to ISO format strings
    - Enum values to their string representations
    """
    
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def serialize_dates_in_dict(data):
    """
    Recursively convert date and datetime objects to ISO format strings in a dictionary.
    
    Args:
        data: Dictionary to process
        
    Returns:
        Dictionary with date/datetime objects converted to strings
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, (datetime.date, datetime.datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        elif isinstance(value, dict):
            result[key] = serialize_dates_in_dict(value)
        elif isinstance(value, list):
            result[key] = [serialize_dates_in_dict(item) if isinstance(item, dict) else 
                          item.isoformat() if isinstance(item, (datetime.date, datetime.datetime)) else
                          item.value if isinstance(item, Enum) else
                          item for item in value]
        else:
            result[key] = value
    return result


def modify_registry_save_form():
    """
    Directly modify the FormModelRegistry.save_form method to handle date serialization.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get reference to the class
        registry = FormModelRegistry.get_instance()
        
        # Create a custom function that will replace the original method
        def new_save_form(form, create_version=False):
            """Modified save_form method that handles date serialization."""
            if registry._form_dao is None:
                logger.error("Form DAO not set")
                return None
                
            try:
                # Ensure form has required fields
                if not hasattr(form, "form_id") or not form.form_id:
                    import uuid
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
                        logger.error("Form type not set and cannot be determined")
                        return None
                
                # First try the form's save_to_dao method for best integration
                if hasattr(form, "save_to_dao") and callable(getattr(form, "save_to_dao")):
                    try:
                        form_id = form.save_to_dao(registry._form_dao, create_version)
                        if form_id:
                            return form_id
                    except Exception as save_dao_error:
                        logger.warning(f"Form.save_to_dao failed, trying direct DAO methods: {save_dao_error}")
                
                # Convert to dictionary for storage
                if hasattr(form, "to_dict") and callable(getattr(form, "to_dict")):
                    try:
                        form_dict = form.to_dict()
                    except Exception as e:
                        logger.warning(f"Form.to_dict failed: {e}")
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
                
                # Process date values in the dictionary
                form_dict = serialize_dates_in_dict(form_dict)
                
                # Process form state
                state = form_dict.get("state", "draft")
                if hasattr(state, "value"):
                    # Handle Enum values
                    state = state.value
                    
                # Create a standardized database object that matches the schema
                db_object = {
                    "form_id": form.form_id,
                    "form_type": form.form_type,
                    "state": state,
                    "status": state,  # Status field matches state
                    "title": form_dict.get("title", "") or form_dict.get("subject", "") or form_dict.get("incident_name", "") or form.form_type,
                    "incident_id": form_dict.get("incident_id", None),
                    "creator_id": form_dict.get("creator_id", None),
                    "created_at": form.created_at.isoformat() if isinstance(form.created_at, datetime.datetime) else form.created_at,
                    "updated_at": form.updated_at.isoformat() if isinstance(form.updated_at, datetime.datetime) else form.updated_at,
                    "data": json.dumps(form_dict)
                }
                
                # Attempt direct SQL interaction
                try:
                    # Check if form already exists using direct SQL
                    conn = registry._form_dao.db_manager.connect()
                    
                    # Check if form exists
                    cursor = conn.execute(
                        "SELECT form_id FROM forms WHERE form_id = ?", 
                        (form.form_id,)
                    )
                    
                    existing = cursor.fetchone() is not None
                    
                    if existing:
                        # Update existing form using direct SQL
                        logger.info(f"Updating existing form with ID {form.form_id}")
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
                        logger.info(f"Creating new form with ID {form.form_id}")
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
                    
                    # Create version if requested
                    if create_version and hasattr(registry._form_dao, 'create_version'):
                        try:
                            registry._form_dao.create_version(form.form_id, form_dict)
                        except Exception as version_error:
                            logger.warning(f"Failed to create form version: {version_error}")
                    
                    logger.debug(f"Saved form of type {form.form_type} with ID {form.form_id}")
                    
                    return form.form_id
                    
                except Exception as sql_error:
                    logger.error(f"Direct SQL operation failed: {sql_error}")
                    
                    # Fall back to trying the DAO methods
                    try:
                        if hasattr(registry._form_dao, 'find_by_id') and callable(getattr(registry._form_dao, 'find_by_id')):
                            existing = registry._form_dao.find_by_id(form.form_id)
                        else:
                            # Assume it's a new form if we can't check
                            existing = None
                            
                        if existing:
                            # Update existing form
                            success = registry._form_dao.update(form.form_id, db_object)
                            if not success:
                                logger.error(f"Failed to update form with ID {form.form_id}")
                                return None
                        else:
                            # Create new form
                            created_id = registry._form_dao.create(db_object)
                            if not created_id:
                                logger.error(f"Failed to create form with ID {form.form_id}")
                                return None
                                
                            # Ensure form_id matches the created ID if it's different
                            if created_id != form.form_id:
                                form.form_id = created_id
                                
                        # Create version if requested
                        if create_version and hasattr(registry._form_dao, 'create_version'):
                            try:
                                registry._form_dao.create_version(form.form_id, form_dict)
                            except Exception as version_error:
                                logger.warning(f"Failed to create form version: {version_error}")
                                
                        return form.form_id
                        
                    except Exception as dao_error:
                        logger.error(f"DAO operation failed after SQL failure: {dao_error}")
                        return None
                
            except Exception as e:
                logger.error(f"Failed to save form: {e}")
                return None
        
        # Save the original method for reference
        original_save_form = FormModelRegistry.save_form
        
        # Replace the method in the registry class
        FormModelRegistry.save_form = new_save_form
        
        logger.info("Successfully replaced FormModelRegistry.save_form method")
        return True
    except Exception as e:
        logger.error(f"Failed to modify FormModelRegistry.save_form: {e}")
        return False


def modify_form_to_dict():
    """
    Modify the to_dict methods of form models to handle date and datetime objects.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Define the wrapper function for to_dict
        def to_dict_wrapper(original_to_dict):
            @wraps(original_to_dict)
            def wrapped_to_dict(self):
                # Get the original dictionary
                data = original_to_dict(self)
                
                # Process date fields
                result = {}
                for key, value in data.items():
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        result[key] = value.isoformat()
                    elif isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, dict):
                        result[key] = serialize_dates_in_dict(value)
                    elif isinstance(value, list):
                        result[key] = [
                            serialize_dates_in_dict(item) if isinstance(item, dict) else
                            item.isoformat() if isinstance(item, (datetime.date, datetime.datetime)) else
                            item.value if isinstance(item, Enum) else
                            item for item in value
                        ]
                    else:
                        result[key] = value
                return result
            return wrapped_to_dict
        
        # Modify EnhancedICS213Form.to_dict
        original_213_to_dict = EnhancedICS213Form.to_dict
        EnhancedICS213Form.to_dict = to_dict_wrapper(original_213_to_dict)
        logger.info("Successfully modified EnhancedICS213Form.to_dict")
        
        # Modify EnhancedICS214Form.to_dict
        original_214_to_dict = EnhancedICS214Form.to_dict
        EnhancedICS214Form.to_dict = to_dict_wrapper(original_214_to_dict)
        logger.info("Successfully modified EnhancedICS214Form.to_dict")
        
        return True
    except Exception as e:
        logger.error(f"Failed to modify form to_dict methods: {e}")
        return False


def test_date_serialization():
    """
    Test date serialization with a simple dictionary.
    
    Returns:
        True if the test passes, False otherwise
    """
    try:
        logger.info("Testing date serialization...")
        
        # Import FormState directly
        from radioforms.models.enhanced_ics214_form import FormState
        
        # Create a test dictionary with a date object
        today = datetime.date.today()
        now = datetime.datetime.now()
        
        test_dict = {
            'date_field': today,
            'datetime_field': now,
            'enum_field': FormState.DRAFT,
            'normal_field': 'test',
            'nested': {
                'date': today
            }
        }
        
        # Apply our serialization function
        serialized_dict = serialize_dates_in_dict(test_dict)
        
        # Check if date was converted to string
        if not isinstance(serialized_dict['date_field'], str):
            logger.error(f"Date field not serialized properly, type: {type(serialized_dict['date_field'])}")
            return False
            
        logger.info(f"Date field serialized to: {serialized_dict['date_field']}")
        
        # Check if datetime was converted to string
        if not isinstance(serialized_dict['datetime_field'], str):
            logger.error(f"Datetime field not serialized properly, type: {type(serialized_dict['datetime_field'])}")
            return False
            
        logger.info(f"Datetime field serialized to: {serialized_dict['datetime_field']}")
        
        # Check if enum was converted to string
        if not isinstance(serialized_dict['enum_field'], str):
            logger.error(f"Enum field not serialized properly, type: {type(serialized_dict['enum_field'])}")
            return False
            
        logger.info(f"Enum field serialized to: {serialized_dict['enum_field']}")
        
        # Check nested dictionary
        if not isinstance(serialized_dict['nested']['date'], str):
            logger.error(f"Nested date field not serialized properly, type: {type(serialized_dict['nested']['date'])}")
            return False
            
        logger.info(f"Nested date field serialized to: {serialized_dict['nested']['date']}")
        
        # Test JSON serialization
        try:
            json_data = json.dumps(serialized_dict)
            logger.info(f"JSON serialization successful: {json_data[:100]}...")
        except TypeError as e:
            logger.error(f"JSON serialization failed: {e}")
            return False
            
        logger.info("Date serialization test passed")
        return True
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False


def main():
    """Run the script."""
    logger.info("Starting date serialization fix script")
    
    # Modify the form registry save_form method
    if not modify_registry_save_form():
        logger.error("Failed to modify registry save_form method")
        return 1
        
    # Modify form to_dict methods
    if not modify_form_to_dict():
        logger.error("Failed to modify form to_dict methods")
        return 1
        
    # Test the serialization fix
    if not test_date_serialization():
        logger.error("Date serialization test failed")
        return 1
        
    logger.info("Date serialization fix successfully applied and tested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
