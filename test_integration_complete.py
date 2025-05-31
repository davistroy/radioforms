#!/usr/bin/env python3
"""Complete integration test for form, UI, and database integration.

This test verifies the complete workflow from UI to database following
the Task 2.3 requirements in CLAUDE_CODE_DEVELOPMENT_PLAN.md.
"""

import sys
import os
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up headless environment for UI testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Setup logging
logging.basicConfig(level=logging.WARNING)

def test_database_service_integration():
    """Test database service integration."""
    print("Testing database service integration...")
    
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
            
            # Initialize form service
            form_service = FormService(db_manager)
            
            # Create test form
            data = ICS213Data(
                incident_name="Integration Test Incident",
                to=Person(name="Test Commander", position="IC"),
                from_person=Person(name="Test Operator", position="Ops"),
                subject="Integration Test Message",
                date="2025-05-30",
                time="18:30",
                message="This is a complete integration test message.",
                priority=Priority.URGENT,
                reply_requested=True
            )
            form = ICS213Form(data)
            
            # Test save operation
            form_id = form_service.save_form(form)
            assert form_id > 0
            print(f"✅ Form saved with ID {form_id}")
            
            # Test load operation
            loaded_form = form_service.load_form(form_id)
            assert loaded_form.data.subject == "Integration Test Message"
            assert loaded_form.data.priority == Priority.URGENT
            print("✅ Form loaded successfully")
            
            # Test update operation
            loaded_form.data.message = "Updated integration test message"
            updated_id = form_service.save_form(loaded_form, form_id)
            assert updated_id == form_id
            
            # Verify update
            final_form = form_service.load_form(form_id)
            assert "Updated" in final_form.data.message
            print("✅ Form updated successfully")
            
            # Test list operation
            forms = form_service.list_forms()
            assert len(forms) >= 1
            assert any(f['id'] == form_id for f in forms)
            print("✅ Form listing works")
            
            # Test search operation
            search_results = form_service.search_forms("Integration")
            assert len(search_results) >= 1
            print("✅ Form search works")
            
            # Test form count
            count = form_service.get_form_count()
            assert count >= 1
            print("✅ Form count works")
            
        return True
        
    except Exception as e:
        print(f"❌ Database service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_database_integration():
    """Test UI to database integration."""
    print("\nTesting UI-Database integration...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.ics213_widget import ICS213Widget
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.form_service import FormService
        from src.forms.ics213 import ICS213Data, Person, Priority
        
        # Create app
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        with TemporaryDirectory() as temp_dir:
            # Setup database
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(db_path)
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            
            # Create form service
            form_service = FormService(db_manager)
            
            # Create widget with database service
            widget = ICS213Widget(form_service=form_service)
            
            # Fill out form in UI
            widget.incident_name_edit.setText("UI Integration Test")
            widget.to_widget.name_edit.setText("UI Commander")
            widget.to_widget.position_edit.setText("IC")
            widget.from_widget.name_edit.setText("UI Operator")
            widget.from_widget.position_edit.setText("Ops")
            widget.subject_edit.setText("UI Integration Test Subject")
            widget.date_edit.setText("2025-05-30")
            widget.time_edit.setText("19:00")
            widget.message_edit.setPlainText("This is a UI integration test message.")
            widget.priority_combo.setCurrentIndex(1)  # Urgent
            widget.reply_requested_check.setChecked(True)
            
            # Trigger save
            widget.save_form()
            
            # Verify form was saved
            assert widget.current_form_id is not None
            assert not widget.is_modified
            print(f"✅ Form saved from UI with ID {widget.current_form_id}")
            
            # Create new widget and load the form
            widget2 = ICS213Widget(form_service=form_service)
            widget2.load_form_by_id(widget.current_form_id)
            
            # Verify data was loaded correctly
            assert widget2.subject_edit.text() == "UI Integration Test Subject"
            assert widget2.to_widget.name_edit.text() == "UI Commander"
            assert widget2.priority_combo.currentIndex() == 1
            assert widget2.reply_requested_check.isChecked()
            print("✅ Form loaded into UI correctly")
            
            # Test modification tracking
            widget2.message_edit.setPlainText("Modified message")
            assert widget2.is_modified
            assert widget2.has_unsaved_changes()
            print("✅ Modification tracking works")
            
            # Test form title generation
            title = widget2.get_form_title()
            assert "UI Integration Test Subject" in title
            print("✅ Form title generation works")
            
        return True
        
    except Exception as e:
        print(f"❌ UI-Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_integration():
    """Test main window integration."""
    print("\nTesting MainWindow integration...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        # Create app
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Create main window with database
            window = MainWindow(database_path=db_path)
            
            # Verify services were initialized
            assert window.db_manager is not None
            assert window.form_service is not None
            assert window.ics213_widget is not None
            assert window.ics213_widget.form_service is not None
            print("✅ MainWindow initialized with database services")
            
            # Test form operations through main window
            form_widget = window.ics213_widget
            
            # Fill out form
            form_widget.subject_edit.setText("MainWindow Integration Test")
            form_widget.to_widget.name_edit.setText("Test User")
            form_widget.to_widget.position_edit.setText("IC")
            form_widget.from_widget.name_edit.setText("Test Sender")
            form_widget.from_widget.position_edit.setText("Ops")
            form_widget.date_edit.setText("2025-05-30")
            form_widget.time_edit.setText("20:00")
            form_widget.message_edit.setPlainText("MainWindow integration test")
            
            # Save through main window menu action
            window._on_save_form()
            
            # Verify save worked
            assert form_widget.current_form_id is not None
            print("✅ Save through MainWindow works")
            
            # Test unsaved changes detection
            form_widget.subject_edit.setText("Modified Subject")
            assert form_widget.has_unsaved_changes()
            
            # Test window title updates
            title = window.windowTitle()
            assert "Modified Subject" in title
            assert "*" in title  # Should show modification indicator
            print("✅ Window title updates with changes")
            
        return True
        
    except Exception as e:
        print(f"❌ MainWindow integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in integration."""
    print("\nTesting error handling...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.ics213_widget import ICS213Widget
        from src.services.form_service import FormService
        from src.database.connection import DatabaseManager
        
        # Create app
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test widget without database service
        widget = ICS213Widget(form_service=None)
        
        # Try to save - should show error
        widget.subject_edit.setText("Test")
        widget.save_form()  # Should fail gracefully
        
        assert widget.current_form_id is None
        print("✅ Graceful handling of missing database service")
        
        # Test loading non-existent form
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(db_path)
            from src.database.schema import SchemaManager
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            
            form_service = FormService(db_manager)
            widget2 = ICS213Widget(form_service=form_service)
            
            # Try to load non-existent form
            widget2.load_form_by_id(999)  # Should fail gracefully
            
            assert widget2.current_form_id is None
            print("✅ Graceful handling of missing form")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete integration tests."""
    print("Complete Integration Tests - Task 2.3: Form Integration")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Database service integration
    if test_database_service_integration():
        tests_passed += 1
    
    # Test 2: UI-Database integration
    if test_ui_database_integration():
        tests_passed += 1
    
    # Test 3: MainWindow integration
    if test_main_window_integration():
        tests_passed += 1
    
    # Test 4: Error handling
    if test_error_handling():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} integration tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All integration tests passed!")
        print("\n✅ Task 2.3: Form Integration - COMPLETED")
        print("   • FormService connects UI to database")
        print("   • CRUD operations work correctly")
        print("   • MainWindow integrates all components")
        print("   • Error handling is robust")
        print("   • Unsaved changes detection works")
        print("   • Form lifecycle management complete")
        
        print("\n🎊 Week 2: ICS-213 Form Implementation - COMPLETED")
        print("   ✅ Task 2.1: ICS-213 Data Model")
        print("   ✅ Task 2.2: Form UI Components") 
        print("   ✅ Task 2.3: Form Integration")
        
        return True
    else:
        print(f"❌ {total_tests - tests_passed} integration tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)