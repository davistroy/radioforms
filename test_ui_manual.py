#!/usr/bin/env python3
"""Manual test for UI components.

This script creates a simple application to test the ICS-213 widget
and verify the UI components work correctly.
"""

import sys
import logging
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_ui_import():
    """Test importing UI components."""
    print("Testing UI component imports...")
    
    try:
        from src.ui.ics213_widget import ICS213Widget, PersonWidget
        print("✅ ICS213Widget imported successfully")
        
        from src.ui.main_window import MainWindow
        print("✅ MainWindow imported successfully")
        
        from src.forms.ics213 import ICS213Form, ICS213Data, Person
        print("✅ ICS213 form classes imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_ui_creation():
    """Test creating UI components without showing them."""
    print("\nTesting UI component creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.ics213_widget import ICS213Widget
        from src.ui.main_window import MainWindow
        
        # Create application (required for widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test PersonWidget creation
        print("Creating PersonWidget...")
        from src.ui.ics213_widget import PersonWidget
        person_widget = PersonWidget()
        print("✅ PersonWidget created successfully")
        
        # Test ICS213Widget creation
        print("Creating ICS213Widget...")
        ics213_widget = ICS213Widget()
        print("✅ ICS213Widget created successfully")
        
        # Test MainWindow creation
        print("Creating MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Test form operations
        print("Testing form operations...")
        form = ics213_widget.get_form()
        assert form is not None
        print("✅ Form object retrieved")
        
        # Test person widget functionality
        print("Testing PersonWidget functionality...")
        person_widget.name_edit.setText("Test User")
        person_widget.position_edit.setText("Test Position")
        person = person_widget.get_person()
        assert person.name == "Test User"
        assert person.position == "Test Position"
        assert person.is_complete
        print("✅ PersonWidget functionality works")
        
        # Clean up
        person_widget.deleteLater()
        ics213_widget.deleteLater()
        main_window.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"❌ UI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_form_integration():
    """Test ICS-213 form integration with UI."""
    print("\nTesting form integration...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.ics213_widget import ICS213Widget
        from src.forms.ics213 import ICS213Data, Person, Priority
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create widget
        widget = ICS213Widget()
        
        # Create test form data
        test_data = ICS213Data(
            incident_name="Test Incident",
            to=Person(name="Jane Doe", position="Incident Commander"),
            from_person=Person(name="John Smith", position="Operations Chief"),
            subject="Test Integration Message",
            date="2025-05-30",
            time="15:30",
            message="This is a test message for UI integration testing.",
            priority=Priority.URGENT,
            reply_requested=True
        )
        
        # Test setting form data
        from src.forms.ics213 import ICS213Form
        test_form = ICS213Form(test_data)
        widget.set_form(test_form)
        
        # Verify data was loaded
        assert widget.incident_name_edit.text() == "Test Incident"
        assert widget.subject_edit.text() == "Test Integration Message"
        assert widget.to_widget.name_edit.text() == "Jane Doe"
        assert widget.from_widget.name_edit.text() == "John Smith"
        assert widget.priority_combo.currentIndex() == 1  # Urgent
        assert widget.reply_requested_check.isChecked()
        print("✅ Form data loading works")
        
        # Test retrieving form data
        retrieved_form = widget.get_form()
        assert retrieved_form.data.subject == "Test Integration Message"
        assert retrieved_form.data.to.name == "Jane Doe"
        print("✅ Form data retrieval works")
        
        # Test validation
        is_valid = retrieved_form.validate()
        assert is_valid
        print("✅ Form validation works")
        
        # Clean up
        widget.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"❌ Form integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_manual_ui_test():
    """Run a manual UI test (shows the actual window)."""
    print("\nRunning manual UI test...")
    print("This will show the actual application window.")
    print("Close the window to continue with the tests.")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.main_window import MainWindow
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("✅ Application window displayed")
        print("   - Try creating a new form")
        print("   - Fill in some fields")
        print("   - Test validation")
        print("   - Close the window to continue")
        
        # Run event loop until window is closed
        app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ Manual UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all UI tests."""
    print("ICS-213 UI Component Tests")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Import test
    if test_ui_import():
        tests_passed += 1
    
    # Test 2: UI creation test
    if test_ui_creation():
        tests_passed += 1
    
    # Test 3: Form integration test
    if test_form_integration():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All automated UI tests passed!")
        
        # Ask user if they want to run manual test
        try:
            response = input("\nRun manual UI test? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                run_manual_ui_test()
                print("\n✅ Manual UI test completed")
        except KeyboardInterrupt:
            print("\n\nManual test skipped")
        
        return True
    else:
        print("❌ Some UI tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)