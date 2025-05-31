#!/usr/bin/env python3
"""Test script to verify FTS fix works."""

import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, 'src')

from src.database.connection import DatabaseManager
from src.database.schema import SchemaManager
from src.services.multi_form_service import MultiFormService
from src.forms.ics213 import ICS213Form, Person

# Create temporary database
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
    temp_db_path = temp_db.name

try:
    # Initialize with fresh database
    db_manager = DatabaseManager(Path(temp_db_path))
    schema_manager = SchemaManager(db_manager)
    schema_manager.initialize_database()
    service = MultiFormService(db_manager)
    service.initialize()
    
    # Create and save form
    form = ICS213Form()
    form.data.incident_name = "FTS Test Incident"
    form.data.to = Person(name="John Doe", position="IC")
    form.data.from_person = Person(name="Jane Smith", position="Operations")
    form.data.subject = "FTS Test Subject"
    form.data.message = "This message contains urgent keywords for testing"
    form.data.date = "2025-05-30"
    form.data.time = "14:30"
    
    form_id = service.save_form(form, "Test User")
    print(f"Saved form with ID: {form_id}")
    
    # Check FTS content
    with db_manager.get_connection() as conn:
        cursor = conn.execute("SELECT form_id, content FROM forms_fts WHERE form_id = ?", (form_id,))
        fts_row = cursor.fetchone()
        if fts_row:
            print(f"FTS entry: form_id={fts_row[0]}")
            print(f"FTS content: '{fts_row[1][:200]}...'")
        else:
            print("No FTS entry found")
    
    # Test search
    from src.services.multi_form_service import FormQuery
    results = service.search_forms(FormQuery(search_text="urgent"))
    print(f"Search for 'urgent' found {len(results)} results")
    
    results = service.search_forms(FormQuery(search_text="test"))
    print(f"Search for 'test' found {len(results)} results")

finally:
    os.unlink(temp_db_path)