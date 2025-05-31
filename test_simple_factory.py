#!/usr/bin/env python3
"""Simple test for form factory registration."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_simple():
    print("=== Test 1: Direct template widget creation ===")
    from src.ui.template_form_widget import create_ics205_widget
    widget1 = create_ics205_widget()
    print(f"Widget created: {widget1 is not None}")
    print(f"Widget type: {widget1.get_form_type()}")
    
    print("\n=== Test 2: Form factory after template widget ===")
    from src.ui.forms.form_factory import FormWidgetFactory
    from src.models.base_form import FormType
    
    available_types = FormWidgetFactory.get_available_form_types()
    print(f"Available types: {[t.value for t in available_types]}")
    print(f"ICS_205 in available: {FormType.ICS_205 in available_types}")
    
    if FormType.ICS_205 in available_types:
        widget2 = FormWidgetFactory.create_form_widget(FormType.ICS_205)
        print(f"Factory widget created: {widget2 is not None}")
    
    print("\n=== Test 3: Fresh import ===")
    # Clear relevant modules
    modules_to_clear = [m for m in sys.modules.keys() if 'form_factory' in m]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    from src.ui.forms.form_factory import FormWidgetFactory
    available_types = FormWidgetFactory.get_available_form_types()
    print(f"Fresh available types: {[t.value for t in available_types]}")

if __name__ == "__main__":
    test_simple()