#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the fixed form model registry.

This script tests the integration between the fixed form model registry and
the database layer to ensure proper functionality. It performs basic operations
like creating, saving, and loading forms to validate the fixes.
"""

import sys
import os
import logging
import datetime
from pathlib import Path

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import required modules
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.models.form_model_registry_fixed import FormModelRegistry


def setup_test_environment():
    """Set up the test environment with a database connection and DAO."""
    # Create a temporary database file instead of in-memory
    # (DBManager requires a directory path)
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    db_path = os.path.join(temp_dir, "test_forms.db")
    logger.info(f"Setting up test environment with database at {db_path}")
    
    # Remove the database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create the database manager
    db_manager = DBManager(db_path)
    
    # Initialize the database schema
    db_manager.init_db()
    
    # Create and return a form DAO
    form_dao = FormDAO(db_manager)
    
    return db_manager, form_dao


def test_form_creation(registry):
    """Test creating a form with the registry."""
    logger.info("Testing form creation")
    
    # Create an ICS-213 form
    form = registry.create_form("ICS-213")
    
    if form:
        logger.info(f"Successfully created ICS-213 form with ID {form.form_id}")
        
        # Set some basic properties
        form.to = "Test Recipient"
        form.from_field = "Test Sender"
        form.subject = "Test Subject"
        form.message = "This is a test message."
        
        return form
    else:
        logger.error("Failed to create form")
        return None


def test_form_save(registry, form):
    """Test saving a form with the registry."""
    logger.info("Testing form saving")
    
    # Save the form
    form_id = registry.save_form(form)
    
    if form_id:
        logger.info(f"Successfully saved form with ID {form_id}")
        return form_id
    else:
        logger.error("Failed to save form")
        return None


def test_form_load(registry, form_id):
    """Test loading a form with the registry."""
    logger.info("Testing form loading")
    
    # Load the form
    form = registry.load_form(form_id)
    
    if form:
        logger.info(f"Successfully loaded form with ID {form_id}")
        logger.info(f"Form properties: to={form.to}, from={form.from_field}, subject={form.subject}")
        return form
    else:
        logger.error(f"Failed to load form with ID {form_id}")
        return None


def test_form_ics214(registry):
    """Test creating and saving an ICS-214 form."""
    logger.info("Testing ICS-214 form creation and saving")
    
    # Create an ICS-214 form
    form = registry.create_form("ICS-214")
    
    if not form:
        logger.error("Failed to create ICS-214 form")
        return None
        
    logger.info(f"Successfully created ICS-214 form with ID {form.form_id}")
    
    # Set some basic properties
    form.incident_name = "Test Incident"
    form.team_name = "Test Team"
    
    # Add an activity
    current_time = datetime.datetime.now().time()
    form.add_activity(time=current_time, activity="Test activity", notable=True)
    
    # Add a person
    form.add_personnel("Test Person", "Test Position", "Test Agency")
    
    # Save the form
    form_id = registry.save_form(form)
    
    if form_id:
        logger.info(f"Successfully saved ICS-214 form with ID {form_id}")
        
        # Load the form back
        loaded_form = registry.load_form(form_id)
        
        if loaded_form:
            logger.info(f"Successfully loaded ICS-214 form with ID {form_id}")
            logger.info(f"Form properties: incident_name={loaded_form.incident_name}, team_name={loaded_form.team_name}")
            logger.info(f"Activities: {len(loaded_form.activity_log)}")
            logger.info(f"Personnel: {len(loaded_form.personnel)}")
            
            if len(loaded_form.activity_log) > 0:
                activity = loaded_form.activity_log[0]
                logger.info(f"First activity: {activity.activity}, notable: {activity.notable}")
                
            if len(loaded_form.personnel) > 0:
                person = loaded_form.personnel[0]
                logger.info(f"First person: {person['name']}, position: {person['position']}")
                
            return loaded_form
    
    logger.error("Failed in ICS-214 form test")
    return None


def main():
    """Run the test script."""
    logger.info("Starting form model registry integration test")
    
    # Set up test environment
    db_manager, form_dao = setup_test_environment()
    
    # Create registry and set DAO
    registry = FormModelRegistry.get_instance()
    registry.set_form_dao(form_dao)
    
    # Test form creation
    form = test_form_creation(registry)
    if not form:
        logger.error("Form creation test failed")
        return 1
        
    # Test form saving
    form_id = test_form_save(registry, form)
    if not form_id:
        logger.error("Form saving test failed")
        return 1
        
    # Test form loading
    loaded_form = test_form_load(registry, form_id)
    if not loaded_form:
        logger.error("Form loading test failed")
        return 1
        
    # Test ICS-214 specific functionality
    ics214_form = test_form_ics214(registry)
    if not ics214_form:
        logger.error("ICS-214 form test failed")
        return 1
        
    logger.info("All tests completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
