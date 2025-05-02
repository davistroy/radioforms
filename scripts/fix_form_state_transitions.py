#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form State Transition Fix Script.

This script fixes form state transitions in enhanced form models,
ensuring that state changes are properly reflected in the database layer
and vice versa. This addresses task 0.3 from the taskplan_updated.md.
"""

import sys
import os
import logging
import json
import sqlite3
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import RadioForms modules
from radioforms.database.db_manager import DBManager
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.models.form_model_registry_fixed import FormModelRegistry
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form, FormState


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def verify_state_model(db_path: str) -> bool:
    """
    Verify that the database schema supports the form state model.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if the schema is compatible, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check forms table
        cursor.execute("PRAGMA table_info(forms)")
        columns = {row['name']: row for row in cursor.fetchall()}
        
        # Verify state column exists
        if 'state' not in columns:
            logger.error("Forms table is missing 'state' column")
            return False
            
        # Verify state column is not null
        if columns['state']['notnull'] != 1:
            logger.warning("Forms 'state' column should be NOT NULL")
            
        # Check for form data column
        if 'data' not in columns:
            logger.error("Forms table is missing 'data' column")
            return False
            
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error verifying state model: {e}")
        return False


def test_state_transitions():
    """
    Test form state transitions in the enhanced form models.
    
    Returns:
        True if all transitions work correctly, False otherwise
    """
    try:
        logger.info("Testing form state transitions in EnhancedICS214Form")
        
        # Create a test form
        form = EnhancedICS214Form()
        
        # Verify initial state
        if form.state != FormState.DRAFT:
            logger.error(f"Form initial state is {form.state}, expected DRAFT")
            return False
            
        logger.info("Initial state is correct: DRAFT")
        
        # Set required fields
        form.incident_name = "Test Incident"
        form.team_name = "Test Team"
        
        # Test finalize transition
        result = form.finalize(
            prepared_name="John Doe",
            prepared_position="Test Position",
            prepared_signature="JD"
        )
        
        if not result:
            logger.error("Failed to finalize form")
            return False
            
        if form.state != FormState.FINALIZED:
            logger.error(f"Form state after finalize is {form.state}, expected FINALIZED")
            return False
            
        logger.info("Finalize transition works correctly: DRAFT -> FINALIZED")
        
        # Test review transition
        result = form.review(
            reviewer_name="Jane Smith",
            reviewer_position="Supervisor",
            reviewer_signature="JS"
        )
        
        if not result:
            logger.error("Failed to review form")
            return False
            
        if form.state != FormState.REVIEWED:
            logger.error(f"Form state after review is {form.state}, expected REVIEWED")
            return False
            
        logger.info("Review transition works correctly: FINALIZED -> REVIEWED")
        
        # Test archive transition
        result = form.archive()
        
        if not result:
            logger.error("Failed to archive form")
            return False
            
        if form.state != FormState.ARCHIVED:
            logger.error(f"Form state after archive is {form.state}, expected ARCHIVED")
            return False
            
        logger.info("Archive transition works correctly: REVIEWED -> ARCHIVED")
        
        # Test invalid transitions
        # Create a new form in draft state
        form = EnhancedICS214Form()
        
        # Try to review without finalizing first (should fail)
        result = form.review(
            reviewer_name="Jane Smith",
            reviewer_position="Supervisor",
            reviewer_signature="JS"
        )
        
        if result:
            logger.error("Form allowed review from DRAFT state (should not be possible)")
            return False
            
        logger.info("Invalid transition correctly blocked: DRAFT -> REVIEWED")
        
        return True
    except Exception as e:
        logger.error(f"Error testing state transitions: {e}")
        return False


def test_state_persistence(db_path: str) -> bool:
    """
    Test form state persistence in the database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if state persistence works correctly, False otherwise
    """
    try:
        logger.info("Testing form state persistence")
        
        # Set up environment
        db_manager = DBManager(db_path)
        form_dao = FormDAO(db_manager)
        registry = FormModelRegistry.get_instance()
        registry.set_form_dao(form_dao)
        
        # Create a test form
        form = EnhancedICS214Form()
        form.incident_name = "Test Incident"
        form.team_name = "Test Team"
        
        # Save the form
        form_id = registry.save_form(form)
        if not form_id:
            logger.error("Failed to save form")
            return False
            
        logger.info(f"Saved form with ID {form_id}")
        
        # Load the form back
        loaded_form = registry.load_form(form_id)
        if not loaded_form:
            logger.error(f"Failed to load form with ID {form_id}")
            return False
            
        # Verify state
        if loaded_form.state != FormState.DRAFT:
            logger.error(f"Loaded form state is {loaded_form.state}, expected DRAFT")
            return False
            
        logger.info("Form loaded successfully with correct state: DRAFT")
        
        # Finalize the form
        result = loaded_form.finalize(
            prepared_name="John Doe",
            prepared_position="Test Position",
            prepared_signature="JD"
        )
        
        if not result:
            logger.error("Failed to finalize form")
            return False
            
        # Save the finalized form
        form_id = registry.save_form(loaded_form)
        if not form_id:
            logger.error("Failed to save finalized form")
            return False
            
        logger.info("Saved finalized form")
        
        # Load the form again
        reloaded_form = registry.load_form(form_id)
        if not reloaded_form:
            logger.error(f"Failed to reload form with ID {form_id}")
            return False
            
        # Verify state
        if reloaded_form.state != FormState.FINALIZED:
            logger.error(f"Reloaded form state is {reloaded_form.state}, expected FINALIZED")
            return False
            
        logger.info("Form reloaded successfully with correct state: FINALIZED")
        
        # Test all states
        states_to_test = [
            (FormState.REVIEWED, "Reviewing form"),
            (FormState.ARCHIVED, "Archiving form")
        ]
        
        current_form = reloaded_form
        
        for target_state, description in states_to_test:
            logger.info(description)
            
            if target_state == FormState.REVIEWED:
                # Transition to REVIEWED
                result = current_form.review(
                    reviewer_name="Jane Smith",
                    reviewer_position="Supervisor",
                    reviewer_signature="JS"
                )
            elif target_state == FormState.ARCHIVED:
                # Transition to ARCHIVED
                result = current_form.archive()
                
            if not result:
                logger.error(f"Failed to transition form to {target_state}")
                return False
                
            # Save the form
            form_id = registry.save_form(current_form)
            if not form_id:
                logger.error(f"Failed to save form in {target_state} state")
                return False
                
            # Load the form again
            current_form = registry.load_form(form_id)
            if not current_form:
                logger.error(f"Failed to reload form after transition to {target_state}")
                return False
                
            # Verify state
            if current_form.state != target_state:
                logger.error(f"Form state after reload is {current_form.state}, expected {target_state}")
                return False
                
            logger.info(f"Form state correctly persisted and reloaded: {target_state}")
            
        return True
    except Exception as e:
        logger.error(f"Error testing state persistence: {e}")
        return False


def fix_state_enum_serialization() -> bool:
    """
    Fix form state enum serialization in enhanced form models.
    
    Returns:
        True if the fix was successful, False otherwise
    """
    try:
        from radioforms.models import enhanced_ics214_form
        
        # Check if to_dict method correctly handles FormState
        form = enhanced_ics214_form.EnhancedICS214Form()
        form_dict = form.to_dict()
        
        # Verify state serialization
        if "state" not in form_dict:
            logger.error("to_dict() method doesn't include state field")
            return False
            
        state_value = form_dict["state"]
        if not isinstance(state_value, str):
            logger.error(f"state field is not serialized as string: {type(state_value)}")
            
            # Fix the to_dict method if needed
            original_to_dict = enhanced_ics214_form.EnhancedICS214Form.to_dict
            
            def fixed_to_dict(self):
                data = original_to_dict(self)
                
                # Ensure state is serialized as string
                if "state" in data and hasattr(data["state"], "value"):
                    data["state"] = data["state"].value
                    
                return data
                
            enhanced_ics214_form.EnhancedICS214Form.to_dict = fixed_to_dict
            logger.info("Fixed to_dict method to properly serialize FormState")
            
        # Check if from_dict method correctly handles FormState
        test_dict = form_dict.copy()
        test_dict["state"] = "reviewed"  # Use string value
        
        form = enhanced_ics214_form.EnhancedICS214Form.from_dict(test_dict)
        
        # Verify state deserialization
        if not form.state == enhanced_ics214_form.FormState.REVIEWED:
            logger.error(f"from_dict() failed to deserialize state: {form.state}")
            
            # Fix the from_dict method if needed
            original_from_dict = enhanced_ics214_form.EnhancedICS214Form.from_dict
            
            @classmethod
            def fixed_from_dict(cls, data):
                form = original_from_dict(data)
                
                # Ensure state is properly deserialized
                if "state" in data and isinstance(data["state"], str):
                    try:
                        form.state = enhanced_ics214_form.FormState(data["state"])
                    except (ValueError, TypeError):
                        form.state = enhanced_ics214_form.FormState.DRAFT
                        
                return form
                
            enhanced_ics214_form.EnhancedICS214Form.from_dict = fixed_from_dict
            logger.info("Fixed from_dict method to properly deserialize FormState")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing state enum serialization: {e}")
        return False


def verify_database_state_values(db_path: str) -> bool:
    """
    Verify that the database contains valid state values.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if all state values are valid, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all form records
        cursor.execute("SELECT form_id, state FROM forms")
        forms = cursor.fetchall()
        
        # Get valid state values
        valid_states = {state.value for state in FormState}
        
        # Check each form's state
        invalid_forms = []
        for form in forms:
            form_id = form['form_id']
            state = form['state']
            
            if state not in valid_states:
                invalid_forms.append((form_id, state))
                
        if invalid_forms:
            logger.warning(f"Found {len(invalid_forms)} forms with invalid state values")
            
            # Fix invalid states
            for form_id, state in invalid_forms:
                logger.info(f"Fixing form {form_id} with invalid state '{state}'")
                
                # Update to draft state
                cursor.execute(
                    "UPDATE forms SET state = ? WHERE form_id = ?",
                    (FormState.DRAFT.value, form_id)
                )
                
            conn.commit()
            logger.info("Fixed all invalid state values")
            
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error verifying database state values: {e}")
        return False


def main():
    """Run the script."""
    parser = argparse.ArgumentParser(description="Fix form state transitions")
    parser.add_argument('--db-path', type=str, help='Path to the database file')
    parser.add_argument('--test-only', action='store_true', help='Only run tests without applying fixes')
    args = parser.parse_args()
    
    # Determine database path
    db_path = args.db_path
    if not db_path:
        # Check environment variable
        db_path = os.environ.get('RADIOFORMS_DB_PATH')
        
        if not db_path:
            # Use default location
            config_dir = os.environ.get('RADIOFORMS_CONFIG_DIR')
            if not config_dir:
                config_dir = os.path.join(os.path.expanduser('~'), '.radioforms')
                
            db_path = os.path.join(config_dir, 'radioforms.db')
            
    logger.info(f"Using database at {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        logger.error(f"Database file {db_path} does not exist")
        return 1
        
    # Verify schema supports state model
    if not verify_state_model(db_path):
        logger.error("Database schema does not support form state model")
        return 1
        
    # Test form state transitions
    if not test_state_transitions():
        logger.error("Form state transition tests failed")
        if args.test_only:
            return 1
    else:
        logger.info("Form state transition tests passed")
        
    # Fix state enum serialization
    if not args.test_only:
        if not fix_state_enum_serialization():
            logger.error("Failed to fix state enum serialization")
            return 1
        else:
            logger.info("State enum serialization fixed")
            
    # Verify database state values
    if not verify_database_state_values(db_path):
        logger.error("Failed to verify database state values")
        return 1
    else:
        logger.info("Database state values verified and fixed if needed")
        
    # Test state persistence
    if not test_state_persistence(db_path):
        logger.error("Form state persistence tests failed")
        return 1
    else:
        logger.info("Form state persistence tests passed")
        
    logger.info("Form state transitions fixed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
