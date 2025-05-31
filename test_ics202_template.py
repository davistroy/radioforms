#!/usr/bin/env python3
"""Test suite for ICS-202 Incident Objectives template.

This test validates the ICS-202 template implementation including:
- Template creation and basic functionality
- Form data management and validation
- Integration with template form widget
- Form factory registration

Usage:
    python test_ics202_template.py
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ics202_template_creation():
    """Test creating ICS-202 template instance."""
    logger.info("Testing ICS-202 template creation...")
    
    try:
        from src.ui.forms.templates.ics202_template import ICS202Template
        
        # Create template instance
        template = ICS202Template()
        assert template is not None, "Failed to create ICS202Template"
        
        # Test template properties
        assert template.form_type == "ics202", f"Unexpected form type: {template.form_type}"
        assert "INCIDENT OBJECTIVES" in template.form_title, f"Unexpected form title: {template.form_title}"
        
        # Test metadata
        assert template.metadata.form_id == "ics202"
        assert template.metadata.version == "2020.1"
        assert template.metadata.fema_compliant == True
        
        logger.info(f"✅ Template creation successful")
        logger.info(f"   - Form type: {template.form_type}")
        logger.info(f"   - Form title: {template.form_title}")
        logger.info(f"   - Version: {template.metadata.version}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template creation failed: {e}")
        return False

def test_ics202_data_management():
    """Test ICS-202 data management functionality."""
    logger.info("Testing ICS-202 data management...")
    
    try:
        from src.ui.forms.templates.ics202_template import ICS202Template
        
        template = ICS202Template()
        
        # Test default data
        default_data = template.get_default_data()
        assert isinstance(default_data, dict), "Default data is not a dictionary"
        
        required_fields = [
            'incident_name', 'operational_period', 'objectives',
            'site_safety_plan_required', 'incident_action_plan_components'
        ]
        
        for field in required_fields:
            assert field in default_data, f"Missing required field: {field}"
        
        logger.info(f"   - Default data fields: {list(default_data.keys())}")
        
        # Test setting and getting data
        test_data = {
            'incident_name': 'Test Incident',
            'operational_period': '2023-11-15 08:00 to 2023-11-15 20:00',
            'objectives': 'Contain the incident and protect life and property',
            'command_emphasis': 'Safety is the top priority',
            'general_situational_awareness': 'Weather conditions are clear',
            'site_safety_plan_required': 'Yes',
            'site_safety_plan_location': 'ICP Safety Board',
            'incident_action_plan_components': 'ICS 203, ICS 204, ICS 205'
        }
        
        template.set_data(test_data)
        retrieved_data = template.get_data()
        
        assert isinstance(retrieved_data, dict), "Retrieved data is not a dictionary"
        
        # Validate key fields were set correctly
        assert retrieved_data['incident_name'] == test_data['incident_name']
        assert retrieved_data['objectives'] == test_data['objectives']
        assert retrieved_data['site_safety_plan_required'] == test_data['site_safety_plan_required']
        
        logger.info("✅ Data management successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data management test failed: {e}")
        return False

def test_ics202_validation():
    """Test ICS-202 form validation."""
    logger.info("Testing ICS-202 validation...")
    
    try:
        from src.ui.forms.templates.ics202_template import ICS202Template
        
        template = ICS202Template()
        
        # Test invalid form (missing required fields)
        invalid_data = {
            'incident_name': 'Test Incident',
            'objectives': '',  # Missing required field
            'incident_action_plan_components': ''  # Missing required field
        }
        
        template.set_data(invalid_data)
        is_valid = template.validate()
        validation_errors = template.get_validation_errors()
        
        assert not is_valid, "Form should be invalid with missing required fields"
        assert len(validation_errors) > 0, "Should have validation errors"
        
        logger.info(f"   - Validation errors for invalid form: {validation_errors}")
        
        # Test valid form
        valid_data = {
            'incident_name': 'Test Incident',
            'objectives': 'Contain the incident and protect life and property',
            'incident_action_plan_components': 'ICS 203, ICS 204, ICS 205',
            'site_safety_plan_required': 'No'
        }
        
        template.set_data(valid_data)
        is_valid = template.validate()
        validation_errors = template.get_validation_errors()
        
        assert is_valid, f"Form should be valid but got errors: {validation_errors}"
        
        # Test safety plan validation
        safety_data = {
            'incident_name': 'Test Incident',
            'objectives': 'Contain the incident and protect life and property',
            'incident_action_plan_components': 'ICS 203, ICS 204, ICS 205',
            'site_safety_plan_required': 'Yes',
            'site_safety_plan_location': ''  # Missing location when required
        }
        
        template.set_data(safety_data)
        validation_errors = template.get_validation_errors()
        
        # Should have warning about missing safety plan location
        safety_error_found = any('safety plan location' in error.lower() for error in validation_errors)
        assert safety_error_found, f"Should warn about missing safety plan location: {validation_errors}"
        
        logger.info("✅ Validation testing successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation test failed: {e}")
        return False

def test_ics202_export_import():
    """Test ICS-202 export and import functionality."""
    logger.info("Testing ICS-202 export/import...")
    
    try:
        from src.ui.forms.templates.ics202_template import ICS202Template
        
        template1 = ICS202Template()
        
        # Set test data
        test_data = {
            'incident_name': 'Export Test Incident',
            'operational_period': '2023-11-15 08:00 to 2023-11-15 20:00',
            'objectives': 'Test objectives for export/import functionality',
            'command_emphasis': 'Test command emphasis',
            'general_situational_awareness': 'Test situational awareness',
            'site_safety_plan_required': 'Yes',
            'site_safety_plan_location': 'Test Safety Board',
            'incident_action_plan_components': 'ICS 203, ICS 204, ICS 205, ICS 206'
        }
        
        template1.set_data(test_data)
        
        # Export data
        export_data = template1.export_data()
        assert isinstance(export_data, dict), "Export data is not a dictionary"
        assert 'metadata' in export_data, "Export missing metadata"
        assert 'form_data' in export_data, "Export missing form_data"
        
        # Create new template and import data
        template2 = ICS202Template()
        import_success = template2.import_data(export_data)
        assert import_success, "Import failed"
        
        # Verify data was imported correctly
        imported_data = template2.get_data()
        assert imported_data['incident_name'] == test_data['incident_name']
        assert imported_data['objectives'] == test_data['objectives']
        assert imported_data['site_safety_plan_location'] == test_data['site_safety_plan_location']
        
        logger.info("✅ Export/import testing successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Export/import test failed: {e}")
        return False

def test_ics202_template_widget():
    """Test ICS-202 template widget creation and functionality."""
    logger.info("Testing ICS-202 template widget...")
    
    try:
        from src.ui.template_form_widget import create_ics202_widget
        
        # Create widget
        widget = create_ics202_widget()
        assert widget is not None, "Failed to create ICS-202 widget"
        
        # Test widget interface
        assert hasattr(widget, 'get_form_type'), "Widget missing get_form_type method"
        assert hasattr(widget, 'validate_form'), "Widget missing validate_form method"
        assert hasattr(widget, 'get_form_data'), "Widget missing get_form_data method"
        
        form_type = widget.get_form_type()
        assert form_type == "ics202", f"Unexpected widget form type: {form_type}"
        
        title = widget.get_form_title()
        assert "INCIDENT OBJECTIVES" in title, f"Unexpected widget title: {title}"
        
        # Test validation
        is_valid = widget.validate_form()
        logger.info(f"   - Initial validation result: {is_valid}")
        
        # Test form data
        form_data = widget.get_form_data()
        assert form_data is not None, "Widget returned None for form data"
        
        logger.info("✅ Template widget testing successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template widget test failed: {e}")
        return False

def test_ics202_form_factory_registration():
    """Test ICS-202 form factory registration."""
    logger.info("Testing ICS-202 form factory registration...")
    
    try:
        from src.ui.forms.form_factory import FormWidgetFactory
        from src.models.base_form import FormType
        
        # Check if ICS-202 is registered
        available_types = FormWidgetFactory.get_available_form_types()
        logger.info(f"   - Available form types: {[t.value for t in available_types]}")
        
        assert FormType.ICS_202 in available_types, f"ICS-202 not registered in form factory. Available: {[t.value for t in available_types]}"
        
        # Test creating ICS-202 widget through factory
        widget = FormWidgetFactory.create_form_widget(FormType.ICS_202)
        assert widget is not None, "Factory failed to create ICS-202 widget"
        
        # Test display name and description
        display_name = FormWidgetFactory.get_form_display_name(FormType.ICS_202)
        description = FormWidgetFactory.get_form_description(FormType.ICS_202)
        
        assert "Incident Objectives" in display_name, f"Unexpected display name: {display_name}"
        assert len(description) > 10, f"Description too short: {description}"
        
        logger.info(f"   - Display name: {display_name}")
        logger.info(f"   - Description: {description}")
        logger.info("✅ Form factory registration successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Form factory registration test failed: {e}")
        return False

def run_all_tests():
    """Run all ICS-202 template tests."""
    logger.info("🚀 Starting ICS-202 Template Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Template Creation", test_ics202_template_creation),
        ("Data Management", test_ics202_data_management),
        ("Form Validation", test_ics202_validation),
        ("Export/Import", test_ics202_export_import),
        ("Template Widget", test_ics202_template_widget),
        ("Form Factory Registration", test_ics202_form_factory_registration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 ICS-202 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info("-" * 50)
    logger.info(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        logger.info("🎉 ALL ICS-202 TESTS PASSED! Template is ready for integration.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Template needs attention.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)