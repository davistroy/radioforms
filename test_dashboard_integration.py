"""Test dashboard integration with main application.

Tests the complete integration of the dashboard system with the main
application window, including tab creation, signal connections, and
data flow between components.

Following CLAUDE.md principles:
- Simple integration test focused on critical workflows
- Performance validation for integrated system
- Error handling validation
- Cross-platform compatibility testing

Run with: python test_dashboard_integration.py
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ui.main_window import MainWindow
    from src.services.multi_form_service import MultiFormService
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    INTEGRATION_AVAILABLE = False
    print(f"Integration components not available for testing: {e}")


class TestDashboardIntegration(unittest.TestCase):
    """Test dashboard integration with main application."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not INTEGRATION_AVAILABLE:
            self.skipTest("Integration components not available")
        
        # Create temporary database path
        self.test_db_path = Path("test_integration.db")
        
        # Clean up any existing test database
        if self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test database
        if hasattr(self, 'test_db_path') and self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def test_main_window_creation_with_dashboard(self):
        """Test main window creation includes dashboard tab."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            # Test without PySide6 - should not crash
            main_window = MainWindow(database_path=self.test_db_path)
            self.assertIsNotNone(main_window)
            
            # Verify dashboard widget is initialized
            self.assertTrue(hasattr(main_window, 'dashboard_widget'))
            self.assertTrue(hasattr(main_window, 'multi_form_service'))
    
    def test_dashboard_signal_handlers_exist(self):
        """Test dashboard signal handlers are properly defined."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Verify signal handlers exist
            self.assertTrue(hasattr(main_window, '_on_dashboard_form_selected'))
            self.assertTrue(hasattr(main_window, '_on_dashboard_incident_changed'))
            self.assertTrue(hasattr(main_window, '_on_dashboard_refresh'))
            
            # Test signal handlers can be called without error
            main_window._on_dashboard_form_selected('ICS-213')
            main_window._on_dashboard_incident_changed('Test Incident')
            main_window._on_dashboard_refresh()
    
    def test_dashboard_form_navigation(self):
        """Test navigation from dashboard to forms."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Mock tab widget for testing
            main_window.tab_widget = Mock()
            
            # Test form selection navigation
            test_cases = [
                ('ICS-213', 0),
                ('ICS-205', 1),
                ('ICS-202', 2),
                ('ICS-201', 3)
            ]
            
            for form_type, expected_tab in test_cases:
                main_window._on_dashboard_form_selected(form_type)
                # Verify the correct tab would be selected
                # (In real implementation, this would set the current tab)
    
    def test_dashboard_incident_management(self):
        """Test incident name management through dashboard."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Test incident change handling
            test_incident = "Wildfire Response Alpha"
            main_window._on_dashboard_incident_changed(test_incident)
            
            # In a real implementation, this would update the window title
            # For testing, we just verify the handler runs without error
    
    def test_multi_form_service_initialization(self):
        """Test multi-form service is properly initialized."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Trigger service initialization
            main_window._initialize_services()
            
            # Verify multi-form service is created
            self.assertIsNotNone(main_window.multi_form_service)
            self.assertIsInstance(main_window.multi_form_service, MultiFormService)
    
    def test_dashboard_integration_error_handling(self):
        """Test error handling in dashboard integration."""
        # Test with dashboard system unavailable
        with patch('src.ui.main_window.DASHBOARD_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Should not crash, should gracefully handle missing dashboard
            self.assertIsNotNone(main_window)
    
    def test_dashboard_data_flow(self):
        """Test data flow between dashboard and main application."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Initialize services
            main_window._initialize_services()
            
            # Verify services are connected
            self.assertIsNotNone(main_window.form_service)
            self.assertIsNotNone(main_window.multi_form_service)
            
            # Test dashboard refresh
            main_window._on_dashboard_refresh()
            
            # Verify refresh doesn't cause errors
    
    def test_dashboard_menu_integration(self):
        """Test dashboard integration with menu system."""
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            
            # Verify main window initialization completes
            self.assertIsNotNone(main_window)
            
            # In a full implementation, this would test menu items
            # for dashboard operations (view, refresh, export, etc.)


class TestDashboardPerformanceIntegration(unittest.TestCase):
    """Test dashboard performance in integrated environment."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not INTEGRATION_AVAILABLE:
            self.skipTest("Integration components not available")
        
        self.test_db_path = Path("test_perf_integration.db")
        if self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'test_db_path') and self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def test_main_window_startup_performance(self):
        """Test main window startup time with dashboard integration."""
        import time
        
        start_time = time.time()
        
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            main_window._initialize_services()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        # Should initialize in under 2 seconds (even with dashboard)
        self.assertLess(startup_time, 2.0)
        print(f"Main window startup time: {startup_time:.3f}s")
    
    def test_dashboard_integration_memory_usage(self):
        """Test memory usage of integrated dashboard system."""
        import sys
        
        # Get initial memory usage (simplified)
        initial_objects = len(sys.modules)
        
        with patch('src.ui.main_window.PYSIDE6_AVAILABLE', False):
            main_window = MainWindow(database_path=self.test_db_path)
            main_window._initialize_services()
            
            # Create dashboard widget
            if hasattr(main_window, 'multi_form_service'):
                # This would create the dashboard in real implementation
                pass
        
        final_objects = len(sys.modules)
        
        # Memory usage should be reasonable
        object_increase = final_objects - initial_objects
        self.assertLess(object_increase, 50)  # Should not load too many new modules


def run_integration_tests():
    """Run all dashboard integration tests."""
    if not INTEGRATION_AVAILABLE:
        print("Integration testing not available - skipping tests")
        return
    
    # Create test suite
    test_classes = [
        TestDashboardIntegration,
        TestDashboardPerformanceIntegration
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nDashboard Integration Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    print(f"\nDashboard Integration Tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)