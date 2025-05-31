"""Unit tests for application module."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.app.application import Application


class TestApplication:
    """Test Application class."""
    
    def test_application_init(self):
        """Test application initialization."""
        app = Application(debug=True)
        
        assert app.debug is True
        assert app.database_path == Path("radioforms.db")
        assert app.qt_app is None
        assert app.main_window is None
    
    def test_application_init_with_database(self):
        """Test application with custom database path."""
        db_path = Path("custom.db")
        app = Application(database_path=db_path)
        
        assert app.database_path == db_path
    
    def test_application_run_without_pyside6(self):
        """Test application run without PySide6 (test mode)."""
        # Patch PYSIDE6_AVAILABLE to False to simulate missing PySide6
        with patch('src.app.application.PYSIDE6_AVAILABLE', False):
            app = Application(debug=True)
            exit_code = app.run()
            
        # Should return 0 in test mode
        assert exit_code == 0
    
    def test_application_shutdown(self):
        """Test application shutdown."""
        app = Application()
        
        # Should not raise exception
        app.shutdown()
    
    @patch('src.app.application.PYSIDE6_AVAILABLE', True)
    @patch('src.app.application.QApplication')
    @patch('src.app.application.QCoreApplication')
    def test_setup_qt_application(self, mock_qcore, mock_qapp):
        """Test Qt application setup."""
        app = Application()
        
        # Mock Qt classes
        mock_qt_instance = MagicMock()
        mock_qapp.return_value = mock_qt_instance
        
        qt_app = app._setup_qt_application()
        
        # Verify Qt application was configured
        mock_qcore.setAttribute.assert_called()
        mock_qapp.assert_called_once()
        assert qt_app == mock_qt_instance
        
        # Verify metadata was set
        qt_app.setOrganizationName.assert_called_with("RadioForms")
        qt_app.setApplicationName.assert_called_with("RadioForms")
    
    def test_setup_qt_application_no_pyside6(self):
        """Test Qt setup without PySide6."""
        with patch('src.app.application.PYSIDE6_AVAILABLE', False):
            app = Application()
            
            with pytest.raises(RuntimeError) as exc_info:
                app._setup_qt_application()
            
            assert "PySide6 is not available" in str(exc_info.value)
    
    @patch('src.app.application.PYSIDE6_AVAILABLE', False)
    def test_show_error_dialog_no_gui(self, caplog):
        """Test error dialog without GUI."""
        app = Application()
        
        with caplog.at_level("ERROR"):
            app._show_error_dialog("Test Error", "Test message")
        
        # Should log the error
        assert "Test Error: Test message" in caplog.text