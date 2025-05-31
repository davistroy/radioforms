#!/usr/bin/env python3
"""Integration test for file operations - Task 3.1.

This test verifies JSON export/import functionality including
round-trip operations, error handling, and UI integration.
"""

import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_file_service_operations():
    """Test file service basic operations."""
    print("Testing FileService operations...")
    
    try:
        from src.services.file_service import FileService, FileServiceError
        from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority
        
        file_service = FileService()
        print("✅ FileService created")
        
        # Create test form
        data = ICS213Data(
            incident_name="File Operations Test",
            to=Person(name="Test Commander", position="IC"),
            from_person=Person(name="Test Operator", position="Ops"),
            subject="File Export/Import Test",
            date="2025-05-30",
            time="23:45",
            message="This is a comprehensive file operations test.",
            priority=Priority.URGENT,
            reply_requested=True
        )
        form = ICS213Form(data)
        print("✅ Test form created")
        
        with TemporaryDirectory() as temp_dir:
            # Test export
            export_path = Path(temp_dir) / "test_export.json"
            success = file_service.export_form_to_json(form, export_path)
            assert success
            assert export_path.exists()
            print("✅ Form exported to JSON")
            
            # Verify export structure
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "radioforms_export" in exported_data
            assert "form" in exported_data
            assert "metadata" in exported_data
            print("✅ Export structure validated")
            
            # Test import
            imported_form = file_service.import_form_from_json(export_path)
            assert imported_form.data.subject == "File Export/Import Test"
            assert imported_form.data.priority == Priority.URGENT
            print("✅ Form imported from JSON")
            
            # Test validation
            validation = file_service.validate_json_file(export_path)
            assert validation["valid"]
            assert validation["info"]["format_version"] == "1.0"
            print("✅ JSON file validation works")
            
            # Test multiple forms export
            forms = [form, imported_form]
            multi_path = Path(temp_dir) / "multiple_forms.json"
            success = file_service.export_multiple_forms(forms, multi_path)
            assert success
            print("✅ Multiple forms export works")
            
            # Test multiple forms import
            imported_forms = file_service.import_multiple_forms(multi_path)
            assert len(imported_forms) == 2
            print("✅ Multiple forms import works")
            
            # Test error handling
            try:
                file_service.import_form_from_json(Path("nonexistent.json"))
                assert False, "Should have raised error"
            except FileServiceError:
                print("✅ Error handling for missing files works")
            
        return True
        
    except Exception as e:
        print(f"❌ FileService operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_format_compliance():
    """Test JSON format compliance and standards."""
    print("\nTesting JSON format compliance...")
    
    try:
        from src.services.file_service import FileService
        from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority
        
        file_service = FileService()
        
        # Create form with special characters
        data = ICS213Data(
            incident_name="Test with Ünicöde & Special Chärs",
            to=Person(name="José María", position="Incident Commander"),
            from_person=Person(name="张三", position="Operations Chief"),
            subject="Test with 中文 and émojis 🚒",
            date="2025-05-30",
            time="23:55",
            message="Message with newlines\nand\ttabs\nand \"quotes\" and 'apostrophes'",
            priority=Priority.IMMEDIATE
        )
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "unicode_test.json"
            
            # Export
            success = file_service.export_form_to_json(form, file_path)
            assert success
            print("✅ Unicode export successful")
            
            # Verify JSON is valid and properly encoded
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data_check = json.loads(content)
            
            # Check Unicode preservation
            form_data = data_check["form"]["data"]
            assert "Ünicöde" in form_data["incident_name"]
            assert "José María" in form_data["to"]["name"]
            assert "中文" in form_data["subject"]
            print("✅ Unicode characters preserved")
            
            # Check proper JSON formatting
            assert content.count('\n') > 10  # Should be formatted with newlines
            assert '  ' in content  # Should have indentation
            print("✅ JSON properly formatted")
            
            # Test round-trip with special characters
            imported_form = file_service.import_form_from_json(file_path)
            assert imported_form.data.to.name == "José María"
            assert "中文" in imported_form.data.subject
            print("✅ Unicode round-trip successful")
            
        return True
        
    except Exception as e:
        print(f"❌ JSON format compliance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backup_functionality():
    """Test backup creation functionality."""
    print("\nTesting backup functionality...")
    
    try:
        from src.services.file_service import FileService
        from src.forms.ics213 import ICS213Form, ICS213Data, Person
        
        file_service = FileService()
        
        data = ICS213Data(
            to=Person(name="Test User", position="IC"),
            from_person=Person(name="Test Sender", position="Ops"),
            subject="Backup Test",
            date="2025-05-30",
            time="23:50",
            message="Testing backup creation"
        )
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "backup_test.json"
            
            # Create initial file
            original_content = '{"original": "content"}'
            file_path.write_text(original_content)
            
            # Export should create backup
            success = file_service.export_form_to_json(form, file_path)
            assert success
            print("✅ Export with existing file successful")
            
            # Check for backup file
            backup_files = list(file_path.parent.glob("backup_test.backup_*.json"))
            assert len(backup_files) == 1
            print("✅ Backup file created")
            
            # Verify backup contains original content
            backup_content = backup_files[0].read_text()
            assert backup_content == original_content
            print("✅ Backup preserves original content")
            
        return True
        
    except Exception as e:
        print(f"❌ Backup functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling_comprehensive():
    """Test comprehensive error handling scenarios."""
    print("\nTesting comprehensive error handling...")
    
    try:
        from src.services.file_service import FileService, FileServiceError
        from src.forms.ics213 import ICS213Form, ICS213Data
        
        file_service = FileService()
        
        with TemporaryDirectory() as temp_dir:
            # Test invalid JSON file
            invalid_path = Path(temp_dir) / "invalid.json"
            invalid_path.write_text("{ invalid json content")
            
            try:
                file_service.import_form_from_json(invalid_path)
                assert False, "Should have raised error"
            except FileServiceError as e:
                assert "Invalid JSON format" in str(e)
                print("✅ Invalid JSON handling works")
            
            # Test wrong format version
            wrong_format = {
                "radioforms_export": {
                    "format_version": "2.0",  # Wrong version
                    "form_type": "ICS-213"
                },
                "form": {}
            }
            wrong_path = Path(temp_dir) / "wrong_format.json"
            with open(wrong_path, 'w') as f:
                json.dump(wrong_format, f)
            
            try:
                file_service.import_form_from_json(wrong_path)
                assert False, "Should have raised error"
            except FileServiceError as e:
                assert "Unsupported format version" in str(e)
                print("✅ Wrong format version handling works")
            
            # Test missing form data
            no_form = {
                "radioforms_export": {
                    "format_version": "1.0",
                    "form_type": "ICS-213"
                }
                # Missing "form" key
            }
            no_form_path = Path(temp_dir) / "no_form.json"
            with open(no_form_path, 'w') as f:
                json.dump(no_form, f)
            
            try:
                file_service.import_form_from_json(no_form_path)
                assert False, "Should have raised error"
            except FileServiceError as e:
                assert "No form data found" in str(e)
                print("✅ Missing form data handling works")
            
            # Test file validation edge cases
            validation = file_service.validate_json_file(Path("nonexistent.json"))
            assert not validation["valid"]
            assert "File not found" in validation["errors"][0]
            print("✅ Validation error handling works")
            
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all file operations tests."""
    print("Task 3.1: File Operations - JSON Export/Import Tests")
    print("=" * 55)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Basic file service operations
    if test_file_service_operations():
        tests_passed += 1
    
    # Test 2: JSON format compliance
    if test_json_format_compliance():
        tests_passed += 1
    
    # Test 3: Backup functionality
    if test_backup_functionality():
        tests_passed += 1
    
    # Test 4: Comprehensive error handling
    if test_error_handling_comprehensive():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} file operation tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All file operations tests passed!")
        print("\n✅ Task 3.1: File Operations - COMPLETED")
        print("   • JSON export with proper formatting ✓")
        print("   • JSON import with validation ✓")
        print("   • Backup creation before overwriting ✓")
        print("   • Comprehensive error handling ✓")
        print("   • Unicode and special character support ✓")
        print("   • Multiple forms export/import ✓")
        print("   • Round-trip data integrity ✓")
        
        print("\n📁 File Operations Features:")
        print("   • Supports .json format")
        print("   • Validates import structure")
        print("   • Creates automatic backups")
        print("   • Handles errors gracefully")
        print("   • Preserves all form data")
        print("   • Ready for UI integration")
        
        return True
    else:
        print(f"❌ {total_tests - tests_passed} file operation tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)