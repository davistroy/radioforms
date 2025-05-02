#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Configuration Manager.

This module contains unit tests for the ConfigManager class to ensure
proper handling of configuration values and persistence.
"""

import os
import unittest
import tempfile
import shutil
from pathlib import Path

from radioforms.config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Unit tests for the Configuration Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test config path
        self.config_path = os.path.join(self.test_dir, "test_config.ini")
        
        # Create config manager
        self.config_manager = ConfigManager(self.config_path)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_set_get_value(self):
        """Test setting and getting string values."""
        # Set values
        self.config_manager.set_value("Test", "string_value", "test")
        self.config_manager.set_value("Test", "empty_value", "")
        
        # Get values
        self.assertEqual(self.config_manager.get_value("Test", "string_value"), "test")
        self.assertEqual(self.config_manager.get_value("Test", "empty_value"), "")
        self.assertEqual(self.config_manager.get_value("Test", "nonexistent_value"), "")
        self.assertEqual(self.config_manager.get_value("Test", "nonexistent_value", "default"), "default")
        
    def test_boolean_values(self):
        """Test boolean values."""
        # Test true values
        for true_value in ["true", "yes", "1", "t", "y"]:
            self.config_manager.set_value("Test", "bool_value", true_value)
            self.assertTrue(self.config_manager.get_boolean("Test", "bool_value"))
            
        # Test false values
        for false_value in ["false", "no", "0", "f", "n"]:
            self.config_manager.set_value("Test", "bool_value", false_value)
            self.assertFalse(self.config_manager.get_boolean("Test", "bool_value"))
            
        # Test default value
        self.assertTrue(self.config_manager.get_boolean("Test", "nonexistent_value", True))
        self.assertFalse(self.config_manager.get_boolean("Test", "nonexistent_value", False))
        
    def test_int_values(self):
        """Test integer values."""
        # Set integer values
        self.config_manager.set_value("Test", "int_value", "42")
        self.config_manager.set_value("Test", "zero_value", "0")
        self.config_manager.set_value("Test", "negative_value", "-10")
        
        # Get integer values
        self.assertEqual(self.config_manager.get_int("Test", "int_value"), 42)
        self.assertEqual(self.config_manager.get_int("Test", "zero_value"), 0)
        self.assertEqual(self.config_manager.get_int("Test", "negative_value"), -10)
        self.assertEqual(self.config_manager.get_int("Test", "nonexistent_value"), 0)
        self.assertEqual(self.config_manager.get_int("Test", "nonexistent_value", 100), 100)
        
        # Test invalid integer value
        self.config_manager.set_value("Test", "invalid_int", "not_an_int")
        self.assertEqual(self.config_manager.get_int("Test", "invalid_int"), 0)
        self.assertEqual(self.config_manager.get_int("Test", "invalid_int", 100), 100)
        
    def test_float_values(self):
        """Test float values."""
        # Set float values
        self.config_manager.set_value("Test", "float_value", "3.14")
        self.config_manager.set_value("Test", "zero_float", "0.0")
        self.config_manager.set_value("Test", "negative_float", "-2.5")
        
        # Get float values
        self.assertEqual(self.config_manager.get_float("Test", "float_value"), 3.14)
        self.assertEqual(self.config_manager.get_float("Test", "zero_float"), 0.0)
        self.assertEqual(self.config_manager.get_float("Test", "negative_float"), -2.5)
        self.assertEqual(self.config_manager.get_float("Test", "nonexistent_value"), 0.0)
        self.assertEqual(self.config_manager.get_float("Test", "nonexistent_value", 1.5), 1.5)
        
        # Test invalid float value
        self.config_manager.set_value("Test", "invalid_float", "not_a_float")
        self.assertEqual(self.config_manager.get_float("Test", "invalid_float"), 0.0)
        self.assertEqual(self.config_manager.get_float("Test", "invalid_float", 1.5), 1.5)
        
    def test_list_values(self):
        """Test list values."""
        # Set list values
        self.config_manager.set_value("Test", "list_value", "a,b,c")
        self.config_manager.set_value("Test", "empty_list", "")
        self.config_manager.set_value("Test", "single_item", "item")
        self.config_manager.set_value("Test", "spaced_list", "a, b, c")
        
        # Get list values
        self.assertEqual(self.config_manager.get_list("Test", "list_value"), ["a", "b", "c"])
        self.assertEqual(self.config_manager.get_list("Test", "empty_list"), [])
        self.assertEqual(self.config_manager.get_list("Test", "single_item"), ["item"])
        self.assertEqual(self.config_manager.get_list("Test", "spaced_list"), ["a", "b", "c"])
        self.assertEqual(self.config_manager.get_list("Test", "nonexistent_value"), [])
        self.assertEqual(self.config_manager.get_list("Test", "nonexistent_value", ["default"]), ["default"])
        
    def test_persistence(self):
        """Test saving and loading configuration."""
        # Set values
        self.config_manager.set_value("Section1", "key1", "value1")
        self.config_manager.set_value("Section1", "key2", "value2")
        self.config_manager.set_value("Section2", "key1", "value3")
        
        # Save configuration
        self.config_manager.save()
        
        # Create a new config manager with the same path
        new_config_manager = ConfigManager(self.config_path)
        
        # Verify values are loaded
        self.assertEqual(new_config_manager.get_value("Section1", "key1"), "value1")
        self.assertEqual(new_config_manager.get_value("Section1", "key2"), "value2")
        self.assertEqual(new_config_manager.get_value("Section2", "key1"), "value3")
        
    def test_sections(self):
        """Test section operations."""
        # Set values in multiple sections
        self.config_manager.set_value("Section1", "key1", "value1")
        self.config_manager.set_value("Section2", "key1", "value2")
        self.config_manager.set_value("Section3", "key1", "value3")
        
        # Get sections
        sections = self.config_manager.get_sections()
        self.assertIn("Section1", sections)
        self.assertIn("Section2", sections)
        self.assertIn("Section3", sections)
        
        # Get section values
        section1_values = self.config_manager.get_section_values("Section1")
        self.assertEqual(section1_values["key1"], "value1")
        
        # Remove section
        self.config_manager.remove_section("Section2")
        sections = self.config_manager.get_sections()
        self.assertIn("Section1", sections)
        self.assertNotIn("Section2", sections)
        self.assertIn("Section3", sections)
        
        # Remove option
        self.config_manager.remove_option("Section1", "key1")
        section1_values = self.config_manager.get_section_values("Section1")
        self.assertNotIn("key1", section1_values)


if __name__ == "__main__":
    unittest.main()
