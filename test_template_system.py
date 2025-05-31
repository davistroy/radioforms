#!/usr/bin/env python3
"""
Test script for Template System functionality.

This script validates the template system foundation including:
- Base template classes and validation
- Field template implementations
- Section template coordination
- Form template structure
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def test_validation_system():
    """Test validation system components."""
    try:
        from ui.forms.templates.base.field_template import (
            ValidationResult, ValidationRule, RequiredRule, MaxLengthRule
        )
        
        print("✅ Validation system:")
        
        # Test ValidationResult
        success = ValidationResult.success("Test passed")
        assert success.is_valid
        assert success.message == "Test passed"
        print("   - ValidationResult creation works")
        
        error = ValidationResult.error("Test failed", "test_field", "TEST_ERROR")
        assert not error.is_valid
        assert error.message == "Test failed"
        assert error.field_id == "test_field"
        assert error.error_code == "TEST_ERROR"
        print("   - ValidationResult error handling works")
        
        # Test combining results
        results = [success, error]
        combined = ValidationResult.combine(results)
        assert not combined.is_valid
        assert "Test failed" in combined.message
        print("   - ValidationResult combination works")
        
        # Test RequiredRule
        required_rule = RequiredRule("Test Field")
        
        # Test with empty value
        result = required_rule.validate("")
        assert not result.is_valid
        assert "required" in result.message.lower()
        
        # Test with valid value
        result = required_rule.validate("Valid text")
        assert result.is_valid
        print("   - RequiredRule validation works")
        
        # Test MaxLengthRule
        max_length_rule = MaxLengthRule(10, "Test Field")
        
        # Test with valid length
        result = max_length_rule.validate("Short")
        assert result.is_valid
        
        # Test with excessive length
        result = max_length_rule.validate("This text is too long")
        assert not result.is_valid
        assert "10 characters" in result.message
        print("   - MaxLengthRule validation works")
        
        return True
    except Exception as e:
        print(f"❌ Validation system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_field_templates():
    """Test text field template implementations."""
    try:
        from ui.forms.templates.fields.text_field import TextFieldTemplate, TextAreaFieldTemplate
        from ui.forms.templates.base.field_template import RequiredRule
        
        print("✅ Text field templates:")
        
        # Test TextFieldTemplate
        text_field = TextFieldTemplate(
            field_id="test_text",
            label="Test Text Field",
            max_length=50,
            placeholder="Enter text",
            required=True
        )
        
        # Test widget creation
        widget = text_field.create_widget()
        assert widget is not None
        print("   - TextFieldTemplate widget creation works")
        
        # Test value operations
        text_field.set_value("Test value")
        assert text_field.get_value() == "Test value"
        print("   - TextFieldTemplate value operations work")
        
        # Test validation
        text_field.set_value("")
        result = text_field.validate()
        assert not result.is_valid  # Should fail because required
        
        text_field.set_value("Valid text")
        result = text_field.validate()
        assert result.is_valid
        print("   - TextFieldTemplate validation works")
        
        # Test TextAreaFieldTemplate
        text_area = TextAreaFieldTemplate(
            field_id="test_area",
            label="Test Text Area",
            max_length=200,
            min_rows=3,
            required=True
        )
        
        # Test widget creation
        widget = text_area.create_widget()
        assert widget is not None
        print("   - TextAreaFieldTemplate widget creation works")
        
        # Test value operations
        text_area.set_value("Multi-line\ntext content")
        assert "Multi-line" in text_area.get_value()
        print("   - TextAreaFieldTemplate value operations work")
        
        # Test validation with long text
        long_text = "x" * 250  # Exceeds max_length of 200
        text_area.set_value(long_text)
        result = text_area.validate()
        assert not result.is_valid  # Should fail because too long
        
        text_area.set_value("Valid content")
        result = text_area.validate()
        assert result.is_valid
        print("   - TextAreaFieldTemplate validation works")
        
        return True
    except Exception as e:
        print(f"❌ Text field templates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_section_templates():
    """Test section template functionality."""
    try:
        from ui.forms.templates.base.section_template import (
            SectionTemplate, LayoutType, DefaultSectionTemplate
        )
        from ui.forms.templates.fields.text_field import TextFieldTemplate
        
        print("✅ Section templates:")
        
        # Create test fields
        field1 = TextFieldTemplate(
            field_id="field1",
            label="Field 1",
            required=True
        )
        
        field2 = TextFieldTemplate(
            field_id="field2", 
            label="Field 2",
            max_length=50
        )
        
        # Create section with fields
        section = DefaultSectionTemplate(
            section_id="test_section",
            title="Test Section",
            fields=[field1, field2],
            layout=LayoutType.SINGLE_COLUMN
        )
        
        assert len(section.fields) == 2
        print("   - Section creation with fields works")
        
        # Test field operations
        section.add_field(TextFieldTemplate(field_id="field3", label="Field 3"))
        assert len(section.fields) == 3
        
        assert section.remove_field("field3")
        assert len(section.fields) == 2
        print("   - Section field management works")
        
        # Test field lookup
        found_field = section.get_field("field1")
        assert found_field is not None
        assert found_field.field_id == "field1"
        print("   - Section field lookup works")
        
        # Test section data operations
        field1.set_value("Value 1")
        field2.set_value("Value 2")
        
        section_data = section.get_section_data()
        assert section_data["field1"] == "Value 1"
        assert section_data["field2"] == "Value 2"
        print("   - Section data operations work")
        
        # Test section validation
        field1.set_value("")  # Should fail validation (required)
        result = section.validate_section()
        assert not result.is_valid
        
        field1.set_value("Valid value")
        result = section.validate_section()
        assert result.is_valid
        print("   - Section validation works")
        
        # Test widget creation
        widget = section.create_section_widget()
        assert widget is not None
        print("   - Section widget creation works")
        
        return True
    except Exception as e:
        print(f"❌ Section templates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_templates():
    """Test form template functionality."""
    try:
        from ui.forms.templates.base.form_template import (
            FormTemplate, FormMetadata, DefaultFormTemplate
        )
        from ui.forms.templates.base.section_template import DefaultSectionTemplate
        from ui.forms.templates.fields.text_field import TextFieldTemplate
        
        print("✅ Form templates:")
        
        # Create form metadata
        metadata = FormMetadata(
            form_id="TEST-001",
            name="Test Form",
            version="1.0",
            description="Test form for validation"
        )
        
        # Create test sections
        section1 = DefaultSectionTemplate(
            section_id="header",
            title="Header Section",
            fields=[
                TextFieldTemplate(
                    field_id="incident_name",
                    label="Incident Name",
                    required=True
                )
            ]
        )
        
        section2 = DefaultSectionTemplate(
            section_id="content",
            title="Content Section",
            fields=[
                TextFieldTemplate(
                    field_id="description",
                    label="Description",
                    max_length=200
                )
            ]
        )
        
        # Create form with sections
        form = DefaultFormTemplate(
            metadata=metadata,
            sections=[section1, section2],
            layout="vertical",
            scrollable=True
        )
        
        assert len(form.sections) == 2
        assert form.metadata.form_id == "TEST-001"
        print("   - Form creation with sections works")
        
        # Test section operations
        form.add_section(DefaultSectionTemplate(
            section_id="footer",
            title="Footer Section",
            fields=[]
        ))
        assert len(form.sections) == 3
        
        assert form.remove_section("footer")
        assert len(form.sections) == 2
        print("   - Form section management works")
        
        # Test form data operations
        form.set_field_value("header", "incident_name", "Test Incident")
        form.set_field_value("content", "description", "Test description")
        
        form_data = form.get_form_data()
        assert "sections" in form_data
        assert form_data["sections"]["header"]["incident_name"] == "Test Incident"
        print("   - Form data operations work")
        
        # Test form validation
        form.set_field_value("header", "incident_name", "")  # Should fail (required)
        result = form.validate_form()
        assert not result.is_valid
        
        form.set_field_value("header", "incident_name", "Valid incident")
        result = form.validate_form()
        assert result.is_valid
        print("   - Form validation works")
        
        # Test widget creation
        widget = form.create_form_widget()
        assert widget is not None
        print("   - Form widget creation works")
        
        return True
    except Exception as e:
        print(f"❌ Form templates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_integration():
    """Test integration between template components."""
    try:
        from ui.forms.templates.base.form_template import FormMetadata, DefaultFormTemplate
        from ui.forms.templates.base.section_template import DefaultSectionTemplate, LayoutType
        from ui.forms.templates.fields.text_field import TextFieldTemplate, TextAreaFieldTemplate
        
        print("✅ Template integration:")
        
        # Create a complete form resembling a simple ICS form
        metadata = FormMetadata(
            form_id="ICS-TEST",
            name="Test ICS Form",
            version="1.0",
            description="Integration test form"
        )
        
        # Header section
        header_section = DefaultSectionTemplate(
            section_id="header",
            title="Form Header",
            layout=LayoutType.FORM_LAYOUT,
            fields=[
                TextFieldTemplate(
                    field_id="incident_name",
                    label="Incident Name",
                    required=True,
                    max_length=100
                ),
                TextFieldTemplate(
                    field_id="form_number",
                    label="Form Number",
                    default_value="001"
                ),
                TextFieldTemplate(
                    field_id="prepared_by",
                    label="Prepared By",
                    required=True
                )
            ]
        )
        
        # Content section
        content_section = DefaultSectionTemplate(
            section_id="content",
            title="Form Content", 
            layout=LayoutType.SINGLE_COLUMN,
            fields=[
                TextAreaFieldTemplate(
                    field_id="situation",
                    label="Situation Summary",
                    required=True,
                    max_length=500,
                    min_rows=4
                ),
                TextAreaFieldTemplate(
                    field_id="actions",
                    label="Actions Taken",
                    max_length=500,
                    min_rows=3
                )
            ]
        )
        
        # Create complete form
        form = DefaultFormTemplate(
            metadata=metadata,
            sections=[header_section, content_section],
            layout="vertical",
            scrollable=True
        )
        
        # Test complete workflow
        print("   - Created complex form structure")
        
        # Set form data
        form.set_field_value("header", "incident_name", "Integration Test Fire")
        form.set_field_value("header", "prepared_by", "Test User")
        form.set_field_value("content", "situation", "Testing template system integration")
        form.set_field_value("content", "actions", "Created test form with multiple sections")
        
        # Validate form
        result = form.validate_form()
        assert result.is_valid
        print("   - Form validation passes with valid data")
        
        # Test invalid data
        form.set_field_value("header", "incident_name", "")  # Remove required field
        result = form.validate_form()
        assert not result.is_valid
        print("   - Form validation fails with invalid data")
        
        # Test data serialization
        form.set_field_value("header", "incident_name", "Integration Test Fire")  # Restore
        form_data = form.get_form_data()
        assert "metadata" in form_data
        assert "sections" in form_data
        assert form_data["metadata"]["form_id"] == "ICS-TEST"
        print("   - Form data serialization works")
        
        # Test widget creation
        widget = form.create_form_widget()
        assert widget is not None
        print("   - Complete form widget creation works")
        
        return True
    except Exception as e:
        print(f"❌ Template integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution."""
    print("Template System Test Suite")
    print("=" * 50)
    print("Testing template system foundation and components")
    
    tests = [
        ("Validation System", test_validation_system),
        ("Text Field Templates", test_text_field_templates),
        ("Section Templates", test_section_templates),
        ("Form Templates", test_form_templates),
        ("Template Integration", test_template_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results")
    print("=" * 50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n✅ All template system tests passed!")
        print("\n🏗️ Template System Foundation Validated:")
        print("   • Validation framework with composable rules")
        print("   • Base template classes with proper inheritance")
        print("   • Text field templates with validation and formatting")
        print("   • Section templates with layout management")
        print("   • Form templates with complete structure coordination")
        print("   • Integration between all template components")
        print("\n🎯 Template system ready for ICS form implementation!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()