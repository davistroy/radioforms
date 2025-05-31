"""Unit tests for file service."""

import pytest
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.services.file_service import FileService, FileServiceError
from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority, ValidationError


class TestFileService:
    """Test FileService class."""
    
    def test_init(self):
        """Test FileService initialization."""
        file_service = FileService()
        assert file_service.logger is not None
    
    def test_export_form_to_json(self):
        """Test exporting form to JSON."""
        file_service = FileService()
        
        # Create test form
        data = ICS213Data(
            incident_name="Test Incident",
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Test Export",
            date="2025-05-30",
            time="19:00",
            message="Test export message",
            priority=Priority.URGENT
        )
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_export.json"
            
            # Export form
            success = file_service.export_form_to_json(form, file_path)
            assert success
            assert file_path.exists()
            
            # Verify file content
            with open(file_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "radioforms_export" in exported_data
            assert "form" in exported_data
            assert "metadata" in exported_data
            
            export_info = exported_data["radioforms_export"]
            assert export_info["format_version"] == "1.0"
            assert export_info["form_type"] == "ICS-213"
            
            form_data = exported_data["form"]
            assert form_data["data"]["subject"] == "Test Export"
    
    def test_export_without_metadata(self):
        """Test exporting form without metadata."""
        file_service = FileService()
        
        data = ICS213Data(subject="Test No Metadata")
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_no_metadata.json"
            
            success = file_service.export_form_to_json(form, file_path, include_metadata=False)
            assert success
            
            with open(file_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "radioforms_export" in exported_data
            assert "form" in exported_data
            assert "metadata" not in exported_data
    
    def test_export_with_backup(self):
        """Test export creates backup of existing file."""
        file_service = FileService()
        
        data = ICS213Data(subject="Test Backup")
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_backup.json"
            
            # Create existing file
            file_path.write_text('{"old": "data"}')
            
            # Export should create backup
            success = file_service.export_form_to_json(form, file_path)
            assert success
            
            # Check for backup file
            backup_files = list(file_path.parent.glob("test_backup.backup_*.json"))
            assert len(backup_files) == 1
    
    def test_import_form_from_json(self):
        """Test importing form from JSON."""
        file_service = FileService()
        
        # Create test form and export it
        data = ICS213Data(
            to=Person(name="Test User", position="IC"),
            from_person=Person(name="Test Sender", position="Ops"),
            subject="Test Import",
            date="2025-05-30",
            time="20:00",
            message="Test import message",
            priority=Priority.IMMEDIATE
        )
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_import.json"
            
            # Export first
            file_service.export_form_to_json(form, file_path)
            
            # Import back
            imported_form = file_service.import_form_from_json(file_path)
            
            assert imported_form.data.subject == "Test Import"
            assert imported_form.data.to.name == "Test User"
            assert imported_form.data.priority == Priority.IMMEDIATE
            assert imported_form.data.message == "Test import message"
    
    def test_import_nonexistent_file(self):
        """Test importing from non-existent file."""
        file_service = FileService()
        
        with pytest.raises(FileServiceError, match="File not found"):
            file_service.import_form_from_json(Path("nonexistent.json"))
    
    def test_import_invalid_json(self):
        """Test importing invalid JSON."""
        file_service = FileService()
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"
            file_path.write_text("invalid json content")
            
            with pytest.raises(FileServiceError, match="Invalid JSON format"):
                file_service.import_form_from_json(file_path)
    
    def test_import_invalid_format(self):
        """Test importing JSON with invalid format."""
        file_service = FileService()
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid_format.json"
            
            # Write JSON without proper RadioForms structure
            invalid_data = {"some": "data"}
            with open(file_path, 'w') as f:
                json.dump(invalid_data, f)
            
            with pytest.raises(FileServiceError, match="Missing RadioForms export header"):
                file_service.import_form_from_json(file_path)
    
    def test_export_multiple_forms(self):
        """Test exporting multiple forms."""
        file_service = FileService()
        
        # Create multiple forms
        forms = []
        for i in range(3):
            data = ICS213Data(
                to=Person(name=f"User {i}", position="IC"),
                from_person=Person(name="Sender", position="Ops"),
                subject=f"Message {i}",
                date="2025-05-30",
                time="21:00",
                message=f"Test message {i}"
            )
            forms.append(ICS213Form(data))
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "multiple_forms.json"
            
            success = file_service.export_multiple_forms(forms, file_path)
            assert success
            
            # Verify content
            with open(file_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "radioforms_export" in exported_data
            assert "forms" in exported_data
            assert exported_data["radioforms_export"]["form_count"] == 3
            assert len(exported_data["forms"]) == 3
    
    def test_import_multiple_forms(self):
        """Test importing multiple forms."""
        file_service = FileService()
        
        # Create and export multiple forms
        forms = []
        for i in range(2):
            data = ICS213Data(
                to=Person(name=f"User {i}", position="IC"),
                from_person=Person(name="Sender", position="Ops"),
                subject=f"Multi Message {i}",
                date="2025-05-30",
                time="22:00",
                message=f"Multi test message {i}"
            )
            forms.append(ICS213Form(data))
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "import_multiple.json"
            
            # Export first
            file_service.export_multiple_forms(forms, file_path)
            
            # Import back
            imported_forms = file_service.import_multiple_forms(file_path)
            
            assert len(imported_forms) == 2
            assert imported_forms[0].data.subject == "Multi Message 0"
            assert imported_forms[1].data.subject == "Multi Message 1"
    
    def test_validate_json_file(self):
        """Test JSON file validation."""
        file_service = FileService()
        
        # Create valid file
        data = ICS213Data(subject="Test Validation")
        form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "validate_test.json"
            file_service.export_form_to_json(form, file_path)
            
            # Validate
            result = file_service.validate_json_file(file_path)
            
            assert result["valid"]
            assert len(result["errors"]) == 0
            assert result["info"]["format_version"] == "1.0"
            assert result["info"]["form_type"] == "ICS-213"
            assert not result["info"]["is_multiple"]
    
    def test_validate_nonexistent_file(self):
        """Test validating non-existent file."""
        file_service = FileService()
        
        result = file_service.validate_json_file(Path("nonexistent.json"))
        
        assert not result["valid"]
        assert len(result["errors"]) > 0
        assert "File not found" in result["errors"][0]
    
    def test_validate_invalid_json_file(self):
        """Test validating invalid JSON file."""
        file_service = FileService()
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"
            file_path.write_text("invalid json")
            
            result = file_service.validate_json_file(file_path)
            
            assert not result["valid"]
            assert len(result["errors"]) > 0
            assert "Invalid JSON format" in result["errors"][0]
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        file_service = FileService()
        
        formats = file_service.get_supported_formats()
        
        assert ".json" in formats
        assert len(formats) >= 1
    
    def test_get_file_info(self):
        """Test getting file information."""
        file_service = FileService()
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "info_test.json"
            file_path.write_text('{"test": "data"}')
            
            info = file_service.get_file_info(file_path)
            
            assert info["exists"]
            assert info["size"] > 0
            assert info["readable"]
            assert info["writable"]
            assert "modified" in info
    
    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file."""
        file_service = FileService()
        
        info = file_service.get_file_info(Path("nonexistent.json"))
        
        assert not info["exists"]
        assert info["size"] == 0
    
    def test_round_trip_export_import(self):
        """Test complete round-trip export/import."""
        file_service = FileService()
        
        # Create complex form
        data = ICS213Data(
            incident_name="Round Trip Test",
            to=Person(name="Test Commander", position="IC", signature="T.C.", contact_info="Radio 1"),
            from_person=Person(name="Test Operator", position="Ops", signature="T.O.", contact_info="Radio 2"),
            subject="Complete Round Trip Test",
            date="2025-05-30",
            time="23:30",
            message="This is a complete round-trip test with all fields populated.",
            priority=Priority.URGENT,
            reply_requested=True,
            approved_by=Person(name="Approver", position="Safety", signature="A.P."),
            reply="This is a test reply",
            replied_by=Person(name="Replier", position="IC", signature="R.E."),
            reply_date_time="2025-05-30 23:45"
        )
        original_form = ICS213Form(data)
        
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "roundtrip_test.json"
            
            # Export
            success = file_service.export_form_to_json(original_form, file_path)
            assert success
            
            # Import
            imported_form = file_service.import_form_from_json(file_path)
            
            # Verify all data matches
            assert imported_form.data.incident_name == original_form.data.incident_name
            assert imported_form.data.to.name == original_form.data.to.name
            assert imported_form.data.to.signature == original_form.data.to.signature
            assert imported_form.data.from_person.contact_info == original_form.data.from_person.contact_info
            assert imported_form.data.subject == original_form.data.subject
            assert imported_form.data.message == original_form.data.message
            assert imported_form.data.priority == original_form.data.priority
            assert imported_form.data.reply_requested == original_form.data.reply_requested
            assert imported_form.data.reply == original_form.data.reply
            assert imported_form.data.replied_by.name == original_form.data.replied_by.name