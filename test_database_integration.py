#!/usr/bin/env python3
"""Integration test for database functionality.

This test verifies the database system works correctly with the application.
"""

import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.connection import DatabaseManager
from src.database.schema import SchemaManager
from src.database.migrations import MigrationManager


def test_database_integration():
    """Test complete database integration."""
    print("Database Integration Test")
    print("=" * 30)
    
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_radioforms.db"
        
        print(f"Creating test database: {db_path}")
        
        # Initialize database manager
        db_manager = DatabaseManager(db_path)
        print("✅ DatabaseManager created")
        
        # Initialize schema
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        print("✅ Database schema initialized")
        
        # Test migration system
        migration_manager = MigrationManager(db_manager)
        status = migration_manager.get_migration_status()
        print(f"✅ Migration status: {status['current_version']}/{status['latest_version']}")
        
        # Create sample data
        schema_manager.create_sample_data()
        print("✅ Sample data created")
        
        # Test form data operations
        print("\nTesting form operations:")
        
        # Insert a test form
        form_data = {
            "to": "Test Commander",
            "from": "Test Operator", 
            "subject": "Integration Test",
            "date": "2025-05-30",
            "time": "18:15",
            "message": "This is a test message for database integration testing.",
            "priority": "routine"
        }
        
        with db_manager.get_transaction() as conn:
            conn.execute(
                """
                INSERT INTO forms (form_type, form_number, incident_name, title, data, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "ICS-213",
                    "TEST-001",
                    "Integration Test Incident",
                    "Test Form",
                    json.dumps(form_data),
                    "Integration Test"
                )
            )
        print("✅ Test form inserted")
        
        # Query forms
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM forms WHERE form_type = 'ICS-213'"
            )
            count = cursor.fetchone()[0]
            print(f"✅ Found {count} ICS-213 forms")
            
            # Get the test form
            cursor = conn.execute(
                """
                SELECT form_number, title, data FROM forms 
                WHERE form_number = 'TEST-001'
                """
            )
            result = cursor.fetchone()
            
            if result:
                form_number, title, data_json = result
                loaded_data = json.loads(data_json)
                print(f"✅ Retrieved form: {form_number} - {title}")
                print(f"   Subject: {loaded_data['subject']}")
                print(f"   Message: {loaded_data['message'][:50]}...")
            else:
                print("❌ Test form not found")
                return False
        
        # Test database info
        info = db_manager.get_database_info()
        print(f"\n✅ Database info:")
        print(f"   SQLite version: {info['sqlite_version']}")
        print(f"   Journal mode: {info['journal_mode']}")
        print(f"   Page count: {info['page_count']}")
        print(f"   Tables: {len(info['tables'])}")
        
        # Test backup
        backup_path = Path(temp_dir) / "backup.db"
        db_manager.backup_database(backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        
        # Verify backup
        backup_manager = DatabaseManager(backup_path)
        with backup_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM forms")
            backup_count = cursor.fetchone()[0]
            print(f"✅ Backup contains {backup_count} forms")
        
        print("\n🎉 All database integration tests passed!")
        return True


def main():
    """Run the integration test."""
    try:
        success = test_database_integration()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())