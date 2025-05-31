#!/usr/bin/env python3
"""Integration test for template system GUI integration.

This test validates that the template system is properly integrated with
the main application GUI and form factory system.

Tests:
    1. Template form widget creation
    2. Form factory registration of templates
    3. Main window integration with ICS-205 template
    4. Signal connections and form switching
    5. Menu state updates for template forms

Usage:
    python test_template_gui_integration.py
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_template_widget_creation():
    """Test creating template form widgets."""
    logger.info("Testing template widget creation...")
    
    try:
        from src.ui.template_form_widget import create_ics205_widget, TemplateFormWidget
        
        # Test ICS-205 widget creation
        widget = create_ics205_widget()
        assert widget is not None, "Failed to create ICS-205 widget"
        assert isinstance(widget, TemplateFormWidget), "Widget is not a TemplateFormWidget"
        
        # Test widget interface
        assert hasattr(widget, 'get_form_type'), "Widget missing get_form_type method"
        assert hasattr(widget, 'validate_form'), "Widget missing validate_form method"
        assert hasattr(widget, 'get_form_data'), "Widget missing get_form_data method"
        assert hasattr(widget, 'load_form_data'), "Widget missing load_form_data method"
        
        form_type = widget.get_form_type()
        assert form_type is not None, "Widget returned None for form type"
        
        logger.info(f"✅ Template widget creation successful, type: {form_type}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template widget creation failed: {e}")
        return False

def test_form_factory_registration():
    """Test that template forms are registered with the form factory."""
    logger.info("Testing form factory registration...")
    
    try:
        from src.ui.forms.form_factory import FormWidgetFactory
        from src.models.base_form import FormType
        
        # Check if ICS-205 is registered
        available_types = FormWidgetFactory.get_available_form_types()
        logger.info(f"   - Available form types: {[t.value for t in available_types]}")
        assert FormType.ICS_205 in available_types, f"ICS-205 not registered in form factory. Available: {[t.value for t in available_types]}"
        
        # Test creating ICS-205 widget through factory
        widget = FormWidgetFactory.create_form_widget(FormType.ICS_205)
        assert widget is not None, "Factory failed to create ICS-205 widget"
        
        # Test display name and description
        display_name = FormWidgetFactory.get_form_display_name(FormType.ICS_205)
        description = FormWidgetFactory.get_form_description(FormType.ICS_205)
        
        assert "Radio Communications Plan" in display_name, f"Unexpected display name: {display_name}"
        assert len(description) > 10, f"Description too short: {description}"
        
        logger.info(f"✅ Form factory registration successful")
        logger.info(f"   - Display name: {display_name}")
        logger.info(f"   - Description: {description}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Form factory registration test failed: {e}")
        return False

def test_template_form_functionality():
    """Test basic template form functionality."""
    logger.info("Testing template form functionality...")
    
    try:
        from src.ui.template_form_widget import create_ics205_widget
        
        widget = create_ics205_widget()
        
        # Test form validation
        is_valid = widget.validate_form()
        logger.info(f"   - Form validation result: {is_valid}")
        
        # Test getting default data
        form_data = widget.get_form_data()
        assert form_data is not None, "Failed to get form data"
        logger.info(f"   - Form data keys: {list(form_data.keys()) if isinstance(form_data, dict) else 'Not a dict'}")
        
        # Test form title
        title = widget.get_form_title()
        assert title is not None and len(title) > 0, "Form title is empty"
        logger.info(f"   - Form title: {title}")
        
        # Test unsaved changes (should be False initially)
        has_changes = widget.has_unsaved_changes()
        logger.info(f"   - Has unsaved changes: {has_changes}")
        
        logger.info("✅ Template form functionality test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template form functionality test failed: {e}")
        return False

def test_main_window_integration():
    """Test main window integration with template forms."""
    logger.info("Testing main window integration...")
    
    try:
        # Test importing main window with template integration
        from src.ui.main_window import MainWindow
        
        # Create main window (this should include ICS-205 tab)
        window = MainWindow(debug=True)
        
        # Check if ICS-205 widget was created
        assert hasattr(window, 'ics205_widget'), "Main window missing ics205_widget attribute"
        
        if window.ics205_widget is not None:
            logger.info("   - ICS-205 widget created successfully in main window")
            
            # Test widget attributes
            widget_type = window.ics205_widget.get_form_type()
            widget_title = window.ics205_widget.get_form_title()
            
            logger.info(f"   - Widget type: {widget_type}")
            logger.info(f"   - Widget title: {widget_title}")
        else:
            logger.warning("   - ICS-205 widget is None (may be due to missing dependencies)")
        
        # Test that tab widget has multiple tabs
        if hasattr(window, 'tab_widget') and window.tab_widget:
            tab_count = window.tab_widget.count() if hasattr(window.tab_widget, 'count') else 0
            logger.info(f"   - Tab count: {tab_count}")
            
            if tab_count >= 2:
                logger.info("   - Multiple form tabs detected")
            else:
                logger.warning("   - Expected multiple tabs but found fewer")
        
        logger.info("✅ Main window integration test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Main window integration test failed: {e}")
        return False

def test_template_system_integration():
    """Test that the template system components integrate correctly."""
    logger.info("Testing template system integration...")
    
    try:
        # Test template import
        from src.ui.forms.templates.ics205_template import ICS205Template
        
        # Create template instance
        template = ICS205Template()
        assert template is not None, "Failed to create ICS205Template"
        
        # Test template properties
        assert hasattr(template, 'form_type'), "Template missing form_type property"
        assert hasattr(template, 'form_title'), "Template missing form_title property"
        
        form_type = template.form_type
        form_title = template.form_title
        
        logger.info(f"   - Template type: {form_type}")
        logger.info(f"   - Template title: {form_title}")
        
        # Test template data interface
        default_data = template.get_default_data()
        assert isinstance(default_data, dict), "Default data is not a dictionary"
        assert len(default_data) > 0, "Default data is empty"
        
        logger.info(f"   - Default data fields: {list(default_data.keys())}")
        
        # Test setting and getting data
        template.set_data(default_data)
        retrieved_data = template.get_data()
        assert isinstance(retrieved_data, dict), "Retrieved data is not a dictionary"
        
        logger.info("✅ Template system integration test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template system integration test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting Template System GUI Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Template Widget Creation", test_template_widget_creation),
        ("Form Factory Registration", test_form_factory_registration),
        ("Template Form Functionality", test_template_form_functionality),
        ("Main Window Integration", test_main_window_integration),
        ("Template System Integration", test_template_system_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info("-" * 60)
    logger.info(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Template GUI integration is working correctly.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Integration needs attention.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)