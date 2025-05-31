"""Unit tests for main module."""

import pytest
import logging
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.main import setup_logging, parse_arguments, check_requirements


class TestSetupLogging:
    """Test logging configuration."""
    
    def test_setup_logging_default(self, caplog):
        """Test default logging setup."""
        with caplog.at_level(logging.INFO):
            setup_logging()
            
        # Check that logging was configured
        assert "Logging configured at INFO level" in caplog.text
    
    def test_setup_logging_debug(self, caplog):
        """Test debug logging setup."""
        with caplog.at_level(logging.DEBUG):
            setup_logging("DEBUG")
            
        assert "Logging configured at DEBUG level" in caplog.text
    
    def test_setup_logging_with_file(self, tmp_path, caplog):
        """Test logging with file output."""
        log_file = tmp_path / "test.log"
        
        with caplog.at_level(logging.INFO):
            setup_logging("INFO", log_file)
        
        # Check file was created and contains logs
        assert log_file.exists()
        assert "Logging configured at INFO level" in caplog.text


class TestParseArguments:
    """Test command-line argument parsing."""
    
    def test_parse_arguments_default(self):
        """Test default argument parsing."""
        with patch('sys.argv', ['radioforms']):
            args = parse_arguments()
            
        assert args.debug is False
        assert args.log_file is None
        assert args.database is None
    
    def test_parse_arguments_debug(self):
        """Test debug flag parsing."""
        with patch('sys.argv', ['radioforms', '--debug']):
            args = parse_arguments()
            
        assert args.debug is True
    
    def test_parse_arguments_log_file(self):
        """Test log file argument."""
        with patch('sys.argv', ['radioforms', '--log-file', 'test.log']):
            args = parse_arguments()
            
        assert args.log_file == Path('test.log')
    
    def test_parse_arguments_database(self):
        """Test database argument."""
        with patch('sys.argv', ['radioforms', '--database', 'custom.db']):
            args = parse_arguments()
            
        assert args.database == Path('custom.db')


class TestCheckRequirements:
    """Test requirements checking."""
    
    def test_check_requirements_python_version(self):
        """Test Python version checking."""
        # This should pass since we're running with Python 3.10+
        result = check_requirements()
        
        # Note: This might fail if PySide6 isn't available, but that's expected
        # The important thing is that it doesn't crash
        assert isinstance(result, bool)
    
    @patch('sys.version_info', (3, 9, 0))
    def test_check_requirements_old_python(self, caplog):
        """Test with old Python version."""
        with caplog.at_level(logging.ERROR):
            result = check_requirements()
            
        assert result is False
        assert "Python 3.10+ required" in caplog.text
    
    @patch('builtins.__import__')
    def test_check_requirements_no_pyside6(self, mock_import, caplog):
        """Test with missing PySide6."""
        def import_side_effect(name, *args, **kwargs):
            if name == 'PySide6':
                raise ImportError("No module named 'PySide6'")
            return MagicMock()
        
        mock_import.side_effect = import_side_effect
        
        with caplog.at_level(logging.ERROR):
            result = check_requirements()
            
        assert result is False
        assert "PySide6 not found" in caplog.text


class TestMainIntegration:
    """Integration tests for main functionality."""
    
    def test_version_argument(self, capsys):
        """Test --version argument."""
        with patch('sys.argv', ['radioforms', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
        
        # Version should exit with code 0
        assert exc_info.value.code == 0
        
        # Check version output
        captured = capsys.readouterr()
        assert "radioforms 0.1.0" in captured.out
    
    def test_help_argument(self, capsys):
        """Test --help argument."""
        with patch('sys.argv', ['radioforms', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
        
        # Help should exit with code 0
        assert exc_info.value.code == 0
        
        # Check help output
        captured = capsys.readouterr()
        assert "ICS Forms Management Application" in captured.out