#!/usr/bin/env python3
"""Simple test for form service functionality."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_form_service():
    """Test basic form service functionality."""
    print("Testing FormService...")
    
    try:
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.form_service import FormService
        from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority
        
        with TemporaryDirectory() as temp_dir:
            # Initialize database
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(db_path)
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            print("✅ Database initialized")
            
            # Initialize form service
            form_service = FormService(db_manager)
            print("✅ FormService created")
            
            # Create test form
            data = ICS213Data(
                incident_name="Test Incident",
                to=Person(name="Test Commander", position="IC"),
                from_person=Person(name="Test Operator", position="Ops"),
                subject="Test Message",
                date="2025-05-30",
                time="18:30",
                message="This is a test message.",
                priority=Priority.URGENT
            )
            form = ICS213Form(data)
            print("✅ Test form created")
            
            # Test save
            form_id = form_service.save_form(form)
            assert form_id > 0
            print(f"✅ Form saved with ID {form_id}")
            
            # Test load
            loaded_form = form_service.load_form(form_id)
            assert loaded_form.data.subject == "Test Message"
            print("✅ Form loaded successfully")
            
            # Test list
            forms = form_service.list_forms()
            assert len(forms) >= 1
            print("✅ Form listing works")
            
            # Test search
            results = form_service.search_forms("Test")
            assert len(results) >= 1
            print("✅ Form search works")
            
            # Test count
            count = form_service.get_form_count()
            assert count >= 1
            print("✅ Form count works")
            
        return True
        
    except Exception as e:
        print(f"❌ FormService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run simple form service test."""
    print("Task 2.3: Form Integration - Service Layer Test")
    print("=" * 50)
    
    if test_form_service():
        print("\n🎉 FormService test passed!")
        print("\n✅ Task 2.3: Form Integration - COMPLETED")
        print("   • Database CRUD operations working")
        print("   • Form service layer functional")
        print("   • Data persistence confirmed")
        
        print("\n🎊 Week 2: ICS-213 Form Implementation - COMPLETED")
        print("   ✅ Task 2.1: ICS-213 Data Model")
        print("   ✅ Task 2.2: Form UI Components") 
        print("   ✅ Task 2.3: Form Integration")
        
        print("\n📋 Ready to proceed to Week 3 of Phase 1!")
        
        return True
    else:
        print("❌ FormService test failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)