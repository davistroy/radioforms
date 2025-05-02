#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database Test Fixture.

This module provides utilities for using real database fixtures in unit and integration tests,
replacing unreliable mocks with actual SQLite databases.
"""

import os
import tempfile
import sqlite3
import json
import uuid
import datetime
from pathlib import Path
import shutil
from typing import Dict, List, Any, Optional, Union, Tuple

# Add parent directory to path to import RadioForms modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from radioforms.database.db_manager import DBManager


class DatabaseFixture:
    """
    Test fixture that creates a temporary SQLite database with the proper schema.
    
    This fixture is designed to replace mocks in integration tests, providing a real
    database with consistent structure and predictable behavior.
    """
    
    def __init__(self, populate_sample_data: bool = True):
        """
        Initialize the database fixture.
        
        Args:
            populate_sample_data: Whether to populate the database with sample data
        """
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db_manager = None
        self.connection = None
        self.populate_sample_data = populate_sample_data
        
    def setup(self):
        """
        Set up the database fixture.
        
        Creates a temporary database with the proper schema and optionally populates
        it with sample data.
        
        Returns:
            DBManager instance connected to the test database
        """
        # Create the database manager
        self.db_manager = DBManager(self.db_path)
        
        # Initialize the database
        self.db_manager.init_db()
        
        # Get a connection
        self.connection = self.db_manager.connect()
        
        # Populate with sample data if requested
        if self.populate_sample_data:
            self._populate_sample_data()
            
        return self.db_manager
        
    def teardown(self):
        """
        Clean up the database fixture.
        
        Closes connections and removes temporary files.
        """
        if self.connection:
            self.connection.close()
            
        if self.db_manager:
            self.db_manager.close()
            
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _populate_sample_data(self):
        """
        Populate the database with sample data for testing.
        """
        # Create sample incidents
        self._create_sample_incidents()
        
        # Create sample operational periods
        self._create_sample_op_periods()
        
        # Create sample forms
        self._create_sample_forms()
        
        # Create sample form versions
        self._create_sample_form_versions()
        
        # Create sample attachments
        self._create_sample_attachments()
        
    def _create_sample_incidents(self):
        """
        Create sample incidents in the database.
        """
        incidents = [
            {
                "incident_id": "INC-2025-001",
                "name": "Test Incident 1",
                "description": "Test incident for testing",
                "status": "active",
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6))
            },
            {
                "incident_id": "INC-2025-002",
                "name": "Test Incident 2",
                "description": "Another test incident",
                "status": "closed",
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=14)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7))
            }
        ]
        
        for incident in incidents:
            self.connection.execute(
                """
                INSERT INTO incidents (
                    incident_id, name, description, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    incident["incident_id"],
                    incident["name"],
                    incident["description"],
                    incident["status"],
                    incident["created_at"],
                    incident["updated_at"]
                )
            )
            
        self.connection.commit()
        
    def _create_sample_op_periods(self):
        """
        Create sample operational periods in the database.
        """
        op_periods = [
            {
                "op_period_id": "OP-2025-001-1",
                "incident_id": "INC-2025-001",
                "start_time": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "end_time": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "name": "Operational Period 1",
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7))
            },
            {
                "op_period_id": "OP-2025-001-2",
                "incident_id": "INC-2025-001",
                "start_time": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "end_time": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=5)),
                "name": "Operational Period 2",
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6))
            }
        ]
        
        for op_period in op_periods:
            self.connection.execute(
                """
                INSERT INTO operational_periods (
                    op_period_id, incident_id, start_time, end_time, name, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    op_period["op_period_id"],
                    op_period["incident_id"],
                    op_period["start_time"],
                    op_period["end_time"],
                    op_period["name"],
                    op_period["created_at"],
                    op_period["updated_at"]
                )
            )
            
        self.connection.commit()
        
    def _create_sample_forms(self):
        """
        Create sample forms in the database.
        """
        forms = [
            {
                "form_id": "ICS213-2025-001-1",
                "incident_id": "INC-2025-001",
                "op_period_id": "OP-2025-001-1",
                "form_type": "ICS-213",
                "state": "draft",
                "data": json.dumps({
                    "from": "John Smith",
                    "to": "Jane Doe",
                    "subject": "Test Message",
                    "message": "This is a test message",
                    "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "time": "10:00",
                    "approved_by": "",
                    "approved_position": "",
                    "approved_date": "",
                    "approved_time": ""
                }),
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "created_by": "test_user",
                "updated_by": "test_user",
                "title": "Test Message"
            },
            {
                "form_id": "ICS214-2025-001-1",
                "incident_id": "INC-2025-001",
                "op_period_id": "OP-2025-001-1",
                "form_type": "ICS-214",
                "state": "approved",
                "data": json.dumps({
                    "name": "John Smith",
                    "position": "Test Position",
                    "home_agency": "Test Agency",
                    "prepared_by": "John Smith",
                    "activity_log": [
                        {
                            "time": "10:00",
                            "activity": "Test activity 1",
                            "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7))
                        },
                        {
                            "time": "11:00",
                            "activity": "Test activity 2",
                            "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7))
                        }
                    ],
                    "date_from": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "date_to": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "time_from": "08:00",
                    "time_to": "16:00"
                }),
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "updated_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "created_by": "test_user",
                "updated_by": "test_user",
                "title": "Activity Log for John Smith"
            }
        ]
        
        for form in forms:
            self.connection.execute(
                """
                INSERT INTO forms (
                    form_id, incident_id, op_period_id, form_type, state, data,
                    created_at, updated_at, created_by, updated_by, title
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    form["form_id"],
                    form["incident_id"],
                    form["op_period_id"],
                    form["form_type"],
                    form["state"],
                    form["data"],
                    form["created_at"],
                    form["updated_at"],
                    form["created_by"],
                    form["updated_by"],
                    form["title"]
                )
            )
            
        self.connection.commit()
        
    def _create_sample_form_versions(self):
        """
        Create sample form versions in the database.
        """
        form_versions = [
            {
                "version_id": str(uuid.uuid4()),
                "form_id": "ICS214-2025-001-1",
                "version": 1,
                "content": json.dumps({
                    "form_id": "ICS214-2025-001-1",
                    "form_type": "ICS-214",
                    "name": "John Smith",
                    "position": "Test Position",
                    "home_agency": "Test Agency",
                    "prepared_by": "John Smith",
                    "activity_log": [
                        {
                            "time": "10:00",
                            "activity": "Test activity 1",
                            "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7))
                        }
                    ],
                    "date_from": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "date_to": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "time_from": "08:00",
                    "time_to": "16:00"
                }),
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=7)),
                "comment": "Initial version",
                "user_id": "test_user"
            },
            {
                "version_id": str(uuid.uuid4()),
                "form_id": "ICS214-2025-001-1",
                "version": 2,
                "content": json.dumps({
                    "form_id": "ICS214-2025-001-1",
                    "form_type": "ICS-214",
                    "name": "John Smith",
                    "position": "Test Position",
                    "home_agency": "Test Agency",
                    "prepared_by": "John Smith",
                    "activity_log": [
                        {
                            "time": "10:00",
                            "activity": "Test activity 1",
                            "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7))
                        },
                        {
                            "time": "11:00",
                            "activity": "Test activity 2",
                            "date": self._format_date(datetime.date.today() - datetime.timedelta(days=7))
                        }
                    ],
                    "date_from": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "date_to": self._format_date(datetime.date.today() - datetime.timedelta(days=7)),
                    "time_from": "08:00",
                    "time_to": "16:00"
                }),
                "created_at": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "comment": "Added second activity",
                "user_id": "test_user"
            }
        ]
        
        for version in form_versions:
            self.connection.execute(
                """
                INSERT INTO form_versions (
                    version_id, form_id, version, content, created_at, comment, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version["version_id"],
                    version["form_id"],
                    version["version"],
                    version["content"],
                    version["created_at"],
                    version["comment"],
                    version["user_id"]
                )
            )
            
        self.connection.commit()
        
    def _create_sample_attachments(self):
        """
        Create sample attachments in the database.
        """
        attachments = [
            {
                "attachment_id": str(uuid.uuid4()),
                "form_id": "ICS213-2025-001-1",
                "filename": "test_attachment.txt",
                "file_path": "/test/path/test_attachment.txt",
                "file_size": 1024,
                "mime_type": "text/plain",
                "upload_time": self._format_datetime(datetime.datetime.now() - datetime.timedelta(days=6)),
                "uploader_id": "test_user",
                "description": "Test attachment"
            }
        ]
        
        for attachment in attachments:
            self.connection.execute(
                """
                INSERT INTO attachments (
                    attachment_id, form_id, filename, file_path, file_size,
                    mime_type, upload_time, uploader_id, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attachment["attachment_id"],
                    attachment["form_id"],
                    attachment["filename"],
                    attachment["file_path"],
                    attachment["file_size"],
                    attachment["mime_type"],
                    attachment["upload_time"],
                    attachment["uploader_id"],
                    attachment["description"]
                )
            )
            
        self.connection.commit()
        
    def _format_datetime(self, dt):
        """
        Format a datetime object as an ISO string for the database.
        
        Args:
            dt: Datetime object
            
        Returns:
            ISO format string without microseconds
        """
        return dt.replace(microsecond=0).isoformat()
        
    def _format_date(self, d):
        """
        Format a date object as an ISO string for the database.
        
        Args:
            d: Date object
            
        Returns:
            ISO format date string
        """
        return d.isoformat()


class DatabaseFixtureContext:
    """
    Context manager for using the database fixture in tests.
    
    Example usage:
    
    ```python
    def test_something():
        with DatabaseFixtureContext() as db_manager:
            # Use db_manager in tests
            forms = db_manager.query_to_dict("SELECT * FROM forms")
            assert len(forms) > 0
    ```
    """
    
    def __init__(self, populate_sample_data=True):
        """
        Initialize the context manager.
        
        Args:
            populate_sample_data: Whether to populate the database with sample data
        """
        self.fixture = DatabaseFixture(populate_sample_data=populate_sample_data)
        self.db_manager = None
        
    def __enter__(self):
        """
        Enter the context manager, setting up the database fixture.
        
        Returns:
            DBManager instance connected to the test database
        """
        self.db_manager = self.fixture.setup()
        return self.db_manager
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, cleaning up the database fixture.
        
        Args:
            exc_type: Exception type (if an exception was raised)
            exc_val: Exception value (if an exception was raised)
            exc_tb: Exception traceback (if an exception was raised)
        """
        self.fixture.teardown()
        

def create_form_fixture(form_type: str, **kwargs) -> Dict[str, Any]:
    """
    Create a form fixture dictionary for testing.
    
    Args:
        form_type: Type of form (e.g., "ICS-213", "ICS-214")
        **kwargs: Additional fields to override defaults
        
    Returns:
        Dictionary with form data
    """
    form_id = kwargs.get("form_id", f"{form_type}-{str(uuid.uuid4())[:8]}")
    
    base_form = {
        "form_id": form_id,
        "incident_id": kwargs.get("incident_id", "INC-2025-001"),
        "op_period_id": kwargs.get("op_period_id", "OP-2025-001-1"),
        "form_type": form_type,
        "state": kwargs.get("state", "draft"),
        "created_at": kwargs.get("created_at", datetime.datetime.now().isoformat()),
        "updated_at": kwargs.get("updated_at", datetime.datetime.now().isoformat()),
        "created_by": kwargs.get("created_by", "test_user"),
        "updated_by": kwargs.get("updated_by", "test_user"),
        "title": kwargs.get("title", f"Test {form_type} form")
    }
    
    if form_type == "ICS-213":
        form_data = {
            "from": kwargs.get("from", "Test Sender"),
            "to": kwargs.get("to", "Test Recipient"),
            "subject": kwargs.get("subject", "Test Subject"),
            "message": kwargs.get("message", "Test message content"),
            "date": kwargs.get("date", datetime.date.today().isoformat()),
            "time": kwargs.get("time", "12:00"),
        }
    elif form_type == "ICS-214":
        form_data = {
            "name": kwargs.get("name", "Test User"),
            "position": kwargs.get("position", "Test Position"),
            "home_agency": kwargs.get("home_agency", "Test Agency"),
            "prepared_by": kwargs.get("prepared_by", "Test User"),
            "date_from": kwargs.get("date_from", datetime.date.today().isoformat()),
            "date_to": kwargs.get("date_to", datetime.date.today().isoformat()),
            "time_from": kwargs.get("time_from", "08:00"),
            "time_to": kwargs.get("time_to", "16:00"),
            "activity_log": kwargs.get("activity_log", [
                {
                    "time": "09:00",
                    "activity": "Test activity",
                    "date": datetime.date.today().isoformat()
                }
            ])
        }
    else:
        form_data = kwargs.get("data", {})
    
    # Add any additional fields
    for key, value in kwargs.items():
        if key not in base_form and key not in form_data:
            form_data[key] = value
    
    # Set the data field
    base_form["data"] = json.dumps(form_data)
    
    return base_form


def get_test_db_path() -> str:
    """
    Get the path to a test database file.
    
    This creates a temporary database file that can be used for testing.
    The caller is responsible for deleting the file when done.
    
    Returns:
        Path to the test database file
    """
    temp_dir = tempfile.mkdtemp()
    return os.path.join(temp_dir, "test.db")


if __name__ == "__main__":
    # Example usage
    with DatabaseFixtureContext() as db_manager:
        # Query the database
        forms = db_manager.query_to_dict("SELECT * FROM forms")
        print(f"Found {len(forms)} forms in the test database")
        
        for form in forms:
            print(f"Form ID: {form['form_id']}, Type: {form['form_type']}, State: {form['state']}")
