#!/usr/bin/env python3
"""Debug script for multi-form service issues."""

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
    # Initialize
    db_manager = DatabaseManager(Path(temp_db_path))
    schema_manager = SchemaManager(db_manager)
    schema_manager.initialize_database()
    service = MultiFormService(db_manager)
    service.initialize()
    
    # Create form
    form = ICS213Form()
    form.data.incident_name = "Debug Incident"
    form.data.to = Person(name="John Doe", position="IC")
    form.data.from_person = Person(name="Jane Smith", position="Operations")
    form.data.subject = "Debug Subject"
    form.data.message = "Debug message content"
    form.data.date = "2025-05-30"
    form.data.time = "14:30"
    
    print(f"Original form incident: {form.data.incident_name}")
    print(f"Original form subject: {form.data.subject}")
    
    # Check JSON serialization
    form_json = form.to_json()
    print(f"Form JSON length: {len(form_json)}")
    print(f"Form JSON snippet: {form_json[:200]}...")
    
    form_dict = form.to_dict()
    print(f"Form dict keys: {list(form_dict.keys())}")
    if 'data' in form_dict:
        print(f"Form data keys: {list(form_dict['data'].keys())}")
    
    # Save form
    form_id = service.save_form(form, "Debug User")
    print(f"Saved form with ID: {form_id}")
    
    # Load form
    loaded = service.load_form(form_id)
    if loaded:
        print(f"Loaded form incident: {loaded.data.incident_name}")
        print(f"Loaded form subject: {loaded.data.subject}")
        print(f"Loaded form type: {type(loaded.data)}")
        print(f"Loaded form has incident_name attr: {hasattr(loaded.data, 'incident_name')}")
    else:
        print("Failed to load form")
    
    # Check what's actually in the forms table
    with db_manager.get_connection() as conn:
        cursor = conn.execute("SELECT id, form_type, title, incident_name, data FROM forms LIMIT 1")
        form_row = cursor.fetchone()
        if form_row:
            print(f"Forms table entry: id={form_row[0]}, type={form_row[1]}, title='{form_row[2]}', incident='{form_row[3]}'")
            print(f"Data snippet: {form_row[4][:100]}...")
        
        cursor = conn.execute("SELECT COUNT(*) FROM forms_fts")
        fts_count = cursor.fetchone()[0]
        print(f"FTS index has {fts_count} entries")
        
        if fts_count > 0:
            cursor = conn.execute("SELECT form_id, content FROM forms_fts LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                content = sample[1] if sample[1] else "(empty content)"
                print(f"Sample FTS entry: form_id={sample[0]}, content snippet='{content[:100]}...'")
            else:
                print("No FTS entries found despite count > 0")
    
    # Test search
    from src.services.multi_form_service import FormQuery
    query = service.search_forms(FormQuery(search_text="debug"))
    print(f"Search for 'debug' found {len(query)} results")
    
    # Test manual FTS population
    with db_manager.get_connection() as conn:
        conn.execute("""
            INSERT INTO forms_fts(form_id, content) 
            SELECT id, form_type || ' ' || 
                   COALESCE(title, '') || ' ' || 
                   COALESCE(incident_name, '') || ' ' ||
                   COALESCE(data, '')
            FROM forms WHERE id = ?
        """, (form_id,))
    
    print("Manually populated FTS index")
    
    # Test search again
    query2 = service.search_forms(FormQuery(search_text="debug"))
    print(f"Search for 'debug' after manual populate found {len(query2)} results")
    
finally:
    os.unlink(temp_db_path)