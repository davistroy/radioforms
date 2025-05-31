"""Test script for ICS-205 Radio Communications Plan template.

This script tests the complete ICS-205 form implementation including
template creation, field validation, and data export/import.
"""

import sys
import os
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ui.forms.templates.ics205_template import ICS205Template
    from ui.forms.templates.fields.table_field import TableColumn, ColumnType
    from ui.forms.templates.base.field_template import ValidationResult
    print("✅ Successfully imported ICS-205 template classes")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_ics205_creation():
    """Test ICS-205 form template creation."""
    print("\n🧪 Testing ICS-205 form creation...")
    
    try:
        # Create ICS-205 form with custom configuration
        form = ICS205Template(
            min_frequency_rows=8,
            max_frequency_rows=40,
            include_special_instructions=True
        )
        
        print(f"✅ Created ICS-205 form: {form.metadata.name}")
        print(f"   Form ID: {form.metadata.form_id}")
        print(f"   Version: {form.metadata.version}")
        print(f"   Sections: {len(form.sections)}")
        
        # Verify sections exist
        section_ids = [section.section_id for section in form.sections]
        expected_sections = ["header", "frequency_assignments", "special_instructions", "approval"]
        
        for expected in expected_sections:
            if expected in section_ids:
                print(f"   ✅ Section '{expected}' found")
            else:
                print(f"   ❌ Section '{expected}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ ICS-205 creation failed: {e}")
        return False


def test_frequency_table_structure():
    """Test the frequency assignment table structure."""
    print("\n🧪 Testing frequency assignment table...")
    
    try:
        form = ICS205Template()
        
        # Find frequency assignment section
        frequency_section = None
        for section in form.sections:
            if section.section_id == "frequency_assignments":
                frequency_section = section
                break
        
        if not frequency_section:
            print("❌ Frequency assignment section not found")
            return False
        
        # Find frequency table field
        frequency_table = None
        for field in frequency_section.fields:
            if field.field_id == "frequency_assignments":
                frequency_table = field
                break
        
        if not frequency_table:
            print("❌ Frequency assignment table not found")
            return False
        
        print(f"✅ Found frequency table with {len(frequency_table.columns)} columns")
        
        # Verify expected columns
        expected_columns = [
            "zone_group", "channel", "function", "assignment",
            "rx_freq_mhz", "rx_tone", "tx_freq_mhz", "tx_tone",
            "mode", "remarks"
        ]
        
        actual_columns = [col.column_id for col in frequency_table.columns]
        
        for expected in expected_columns:
            if expected in actual_columns:
                print(f"   ✅ Column '{expected}' found")
            else:
                print(f"   ❌ Column '{expected}' missing")
                return False
        
        # Verify table configuration
        print(f"   Min rows: {frequency_table.min_rows}")
        print(f"   Max rows: {frequency_table.max_rows}")
        print(f"   Allow add: {frequency_table.allow_add}")
        print(f"   Allow remove: {frequency_table.allow_remove}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frequency table test failed: {e}")
        return False


def test_form_data_handling():
    """Test form data population and retrieval."""
    print("\n🧪 Testing form data handling...")
    
    try:
        form = ICS205Template()
        
        # Set header data
        form.set_field_value("header", "incident_name", "Test Incident Alpha")
        form.set_field_value("header", "operational_period", "2025-05-31 08:00 - 20:00")
        form.set_field_value("header", "date_prepared", "2025-05-31")
        form.set_field_value("header", "time_prepared", "14:30")
        form.set_field_value("approval", "prepared_by_name", "Test User")
        form.set_field_value("approval", "prepared_by_position", "Communications Officer")
        
        # Set frequency assignment data
        frequency_data = [
            {
                "zone_group": "Command",
                "channel": "CMD-1",
                "function": "Command",
                "assignment": "IC Operations",
                "rx_freq_mhz": "154.7600",
                "rx_tone": "136.5",
                "tx_freq_mhz": "154.7600",
                "tx_tone": "136.5",
                "mode": "A",
                "remarks": "Primary command frequency"
            },
            {
                "zone_group": "Tactical",
                "channel": "TAC-1",
                "function": "Tactical",
                "assignment": "Division Alpha",
                "rx_freq_mhz": "154.2650",
                "rx_tone": "151.4",
                "tx_freq_mhz": "154.2650",
                "tx_tone": "151.4",
                "mode": "A",
                "remarks": "Tactical operations"
            }
        ]
        
        form.set_field_value("frequency_assignments", "frequency_assignments", frequency_data)
        
        # Verify data retrieval
        retrieved_incident = form.get_field_value("header", "incident_name")
        retrieved_frequencies = form.get_field_value("frequency_assignments", "frequency_assignments")
        
        print(f"✅ Set incident name: {retrieved_incident}")
        print(f"✅ Set {len(retrieved_frequencies)} frequency assignments")
        
        # Verify specific frequency data
        if retrieved_frequencies and len(retrieved_frequencies) >= 2:
            first_freq = retrieved_frequencies[0]
            print(f"   First frequency: {first_freq.get('rx_freq_mhz')} MHz ({first_freq.get('function')})")
            
            second_freq = retrieved_frequencies[1]
            print(f"   Second frequency: {second_freq.get('rx_freq_mhz')} MHz ({second_freq.get('function')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Form data handling test failed: {e}")
        return False


def test_form_validation():
    """Test ICS-205 form validation."""
    print("\n🧪 Testing form validation...")
    
    try:
        form = ICS205Template()
        
        # Test empty form validation (should fail)
        empty_validation = form.validate_form_ics205()
        print(f"Empty form validation - Valid: {empty_validation['is_valid']}")
        if empty_validation['errors']:
            print(f"   Expected errors: {len(empty_validation['errors'])}")
        
        # Set minimum required data
        form.set_field_value("header", "incident_name", "Test Incident")
        form.set_field_value("header", "operational_period", "2025-05-31 08:00 - 20:00")
        form.set_field_value("header", "date_prepared", "2025-05-31")
        form.set_field_value("approval", "prepared_by_name", "Test User")
        
        # Add valid frequency data
        valid_frequencies = [
            {
                "zone_group": "Command",
                "function": "Command",
                "rx_freq_mhz": "154.7600",
                "mode": "A"
            }
        ]
        form.set_field_value("frequency_assignments", "frequency_assignments", valid_frequencies)
        
        # Test valid form validation
        valid_validation = form.validate_form_ics205()
        print(f"Valid form validation - Valid: {valid_validation['is_valid']}")
        if valid_validation['errors']:
            print(f"   Unexpected errors: {valid_validation['errors']}")
        if valid_validation['warnings']:
            print(f"   Warnings: {valid_validation['warnings']}")
        
        # Test invalid frequency validation
        invalid_frequencies = [
            {
                "zone_group": "Test",
                "function": "Command",
                "rx_freq_mhz": "invalid_frequency",  # Invalid frequency
                "mode": "A"
            }
        ]
        form.set_field_value("frequency_assignments", "frequency_assignments", invalid_frequencies)
        
        invalid_validation = form.validate_form_ics205()
        print(f"Invalid frequency validation - Valid: {invalid_validation['is_valid']}")
        if invalid_validation['errors']:
            print(f"   Expected errors: {len(invalid_validation['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Form validation test failed: {e}")
        return False


def test_form_export_import():
    """Test form data export and import."""
    print("\n🧪 Testing form export/import...")
    
    try:
        # Create and populate original form
        original_form = ICS205Template()
        
        original_form.set_field_value("header", "incident_name", "Export Test Incident")
        original_form.set_field_value("header", "operational_period", "2025-05-31 12:00 - 2025-06-01 12:00")
        original_form.set_field_value("approval", "prepared_by_name", "Export Test User")
        
        frequency_data = [
            {
                "zone_group": "Export Test",
                "function": "Command",
                "rx_freq_mhz": "155.1234",
                "mode": "D"
            }
        ]
        original_form.set_field_value("frequency_assignments", "frequency_assignments", frequency_data)
        
        # Export form data
        exported_data = original_form.export_to_dict()
        print(f"✅ Exported form data: {len(exported_data)} top-level keys")
        print(f"   Form type: {exported_data.get('form_type')}")
        print(f"   Sections: {len(exported_data.get('sections', {}))}")
        
        # Import form data
        imported_form = ICS205Template.create_from_dict(exported_data)
        print(f"✅ Created imported form: {imported_form.metadata.name}")
        
        # Verify data preservation
        imported_incident = imported_form.get_field_value("header", "incident_name")
        imported_frequencies = imported_form.get_field_value("frequency_assignments", "frequency_assignments")
        
        print(f"   Imported incident: {imported_incident}")
        print(f"   Imported frequencies: {len(imported_frequencies) if imported_frequencies else 0}")
        
        # Verify data matches
        if imported_incident == "Export Test Incident":
            print("   ✅ Incident name preserved")
        else:
            print("   ❌ Incident name not preserved")
            return False
        
        if imported_frequencies and len(imported_frequencies) == 1:
            if imported_frequencies[0].get("rx_freq_mhz") == "155.1234":
                print("   ✅ Frequency data preserved")
            else:
                print("   ❌ Frequency data not preserved")
                return False
        else:
            print("   ❌ Frequency count not preserved")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Export/import test failed: {e}")
        return False


def main():
    """Run all ICS-205 template tests."""
    print("🚀 Starting ICS-205 Radio Communications Plan Template Tests")
    print("=" * 60)
    
    tests = [
        ("ICS-205 Creation", test_ics205_creation),
        ("Frequency Table Structure", test_frequency_table_structure),
        ("Form Data Handling", test_form_data_handling),
        ("Form Validation", test_form_validation),
        ("Form Export/Import", test_form_export_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Running: {test_name}")
        print(f"{'=' * 60}")
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print(f"{'=' * 60}")
    
    if passed == total:
        print("🎉 All ICS-205 template tests PASSED!")
        return True
    else:
        print(f"💥 {total - passed} test(s) FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)