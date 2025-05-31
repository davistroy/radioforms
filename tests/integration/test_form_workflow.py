"""Integration tests for complete form workflows.

This module tests end-to-end workflows including form creation,
editing, validation, saving, and loading operations.
"""

import pytest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority
from src.services.form_service import FormService
from src.services.file_service import FileService
from src.database.connection import DatabaseManager
from src.database.schema import SchemaManager


class TestFormWorkflow:
    """Test complete form workflows."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(db_path)
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            yield db_manager
    
    @pytest.fixture
    def form_service(self, temp_db):
        """Create form service with temporary database."""
        return FormService(temp_db)
    
    @pytest.fixture
    def file_service(self):
        """Create file service."""
        return FileService()
    
    @pytest.fixture
    def sample_form(self):
        """Create sample form for testing."""
        data = ICS213Data(
            incident_name="Integration Test Incident",
            to=Person(name="Integration Commander", position="IC"),
            from_person=Person(name="Integration Operator", position="Ops"),
            subject="Integration Test Message",
            date="2025-05-30",
            time="23:45",
            message="This is an integration test message for workflow testing.",
            priority=Priority.URGENT,
            reply_requested=True
        )
        return ICS213Form(data)
    
    def test_complete_form_lifecycle(self, form_service, sample_form):
        """Test complete form lifecycle: create, save, load, update, delete."""
        # Save form
        form_id = form_service.save_form(sample_form)
        assert form_id is not None
        assert form_id > 0
        
        # Load form
        loaded_form = form_service.load_form(form_id)
        assert loaded_form is not None
        assert loaded_form.data.subject == sample_form.data.subject
        assert loaded_form.data.message == sample_form.data.message
        assert loaded_form.data.priority == sample_form.data.priority
        
        # Update form
        loaded_form.data.message = "Updated message for integration test"
        loaded_form.data.priority = Priority.IMMEDIATE
        
        updated_id = form_service.save_form(loaded_form)
        assert updated_id == form_id  # Should be same ID for update
        
        # Reload and verify update
        reloaded_form = form_service.load_form(form_id)
        assert reloaded_form.data.message == "Updated message for integration test"
        assert reloaded_form.data.priority == Priority.IMMEDIATE
        
        # List forms
        forms = form_service.list_forms()
        assert len(forms) >= 1
        assert any(f['id'] == form_id for f in forms)
        
        # Delete form
        success = form_service.delete_form(form_id)
        assert success
        
        # Verify deletion
        deleted_form = form_service.load_form(form_id)
        assert deleted_form is None
    
    def test_form_validation_workflow(self, form_service):
        """Test form validation workflow."""
        # Create invalid form
        invalid_data = ICS213Data()  # Missing required fields
        invalid_form = ICS213Form(invalid_data)
        
        # Validation should fail
        assert not invalid_form.validate()
        
        # Should still be able to save (as draft)
        form_id = form_service.save_form(invalid_form)
        assert form_id is not None
        
        # Load and fix form
        loaded_form = form_service.load_form(form_id)
        loaded_form.data.to = Person(name="Test Recipient", position="IC")
        loaded_form.data.from_person = Person(name="Test Sender", position="Ops")
        loaded_form.data.subject = "Test Subject"
        loaded_form.data.message = "Test Message"
        
        # Now validation should pass
        assert loaded_form.validate()
        
        # Save corrected form
        form_service.save_form(loaded_form)
        
        # Reload and verify
        final_form = form_service.load_form(form_id)
        assert final_form.validate()
    
    def test_file_export_import_workflow(self, form_service, file_service, sample_form):
        """Test complete file export/import workflow."""
        # Save form to database
        form_id = form_service.save_form(sample_form)
        
        with TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "exported_form.json"
            
            # Export form
            success = file_service.export_form_to_json(sample_form, export_path)
            assert success
            assert export_path.exists()
            
            # Import form
            imported_form = file_service.import_form_from_json(export_path)
            assert imported_form.data.subject == sample_form.data.subject
            assert imported_form.data.message == sample_form.data.message
            assert imported_form.data.priority == sample_form.data.priority
            
            # Save imported form as new form
            new_form_id = form_service.save_form(imported_form)
            assert new_form_id != form_id  # Should be different ID
            
            # Verify both forms exist
            original_form = form_service.load_form(form_id)
            new_form = form_service.load_form(new_form_id)
            
            assert original_form.data.subject == new_form.data.subject
            assert original_form.data.message == new_form.data.message
    
    def test_multiple_forms_workflow(self, form_service, file_service):
        """Test workflow with multiple forms."""
        forms = []
        form_ids = []
        
        # Create multiple forms
        for i in range(5):
            data = ICS213Data(
                incident_name=f"Incident {i+1}",
                to=Person(name=f"Commander {i+1}", position="IC"),
                from_person=Person(name=f"Operator {i+1}", position="Ops"),
                subject=f"Message {i+1}",
                date="2025-05-30",
                time=f"{20+i}:00",
                message=f"Test message number {i+1}",
                priority=Priority.ROUTINE if i % 2 == 0 else Priority.URGENT
            )
            form = ICS213Form(data)
            forms.append(form)
            
            # Save each form
            form_id = form_service.save_form(form)
            form_ids.append(form_id)
        
        # Verify all forms saved
        assert len(form_ids) == 5
        assert all(fid is not None for fid in form_ids)
        
        # List all forms
        all_forms = form_service.list_forms()
        assert len(all_forms) >= 5
        
        # Export multiple forms
        with TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "multiple_forms.json"
            success = file_service.export_multiple_forms(forms, export_path)
            assert success
            
            # Import multiple forms
            imported_forms = file_service.import_multiple_forms(export_path)
            assert len(imported_forms) == 5
            
            # Verify imported forms match originals
            for original, imported in zip(forms, imported_forms):
                assert original.data.subject == imported.data.subject
                assert original.data.message == imported.data.message
                assert original.data.priority == imported.data.priority
    
    def test_error_handling_workflow(self, form_service, file_service):
        """Test error handling in workflows."""
        # Test loading non-existent form
        non_existent_form = form_service.load_form(99999)
        assert non_existent_form is None
        
        # Test deleting non-existent form
        success = form_service.delete_form(99999)
        assert not success
        
        # Test importing non-existent file
        with pytest.raises(Exception):  # Should raise FileServiceError
            file_service.import_form_from_json(Path("nonexistent.json"))
        
        # Test exporting to invalid path
        data = ICS213Data(subject="Test")
        form = ICS213Form(data)
        
        # This should handle gracefully
        success = file_service.export_form_to_json(form, Path("/invalid/path/file.json"))
        assert not success
    
    def test_concurrent_operations_workflow(self, form_service, sample_form):
        """Test workflow with concurrent-like operations."""
        # Save initial form
        form_id = form_service.save_form(sample_form)
        
        # Load form multiple times (simulating concurrent access)
        form1 = form_service.load_form(form_id)
        form2 = form_service.load_form(form_id)
        
        # Modify both copies differently
        form1.data.message = "Modified by user 1"
        form2.data.message = "Modified by user 2"
        
        # Save both (last write wins)
        form_service.save_form(form1)
        form_service.save_form(form2)
        
        # Load final form
        final_form = form_service.load_form(form_id)
        assert final_form.data.message == "Modified by user 2"
    
    def test_form_search_workflow(self, form_service):
        """Test form search functionality."""
        # Create forms with different subjects
        subjects = ["Emergency Response", "Status Update", "Resource Request", "Emergency Response Follow-up"]
        form_ids = []
        
        for subject in subjects:
            data = ICS213Data(
                to=Person(name="Commander", position="IC"),
                from_person=Person(name="Operator", position="Ops"),
                subject=subject,
                message=f"Message for {subject}",
                date="2025-05-30",
                time="20:00"
            )
            form = ICS213Form(data)
            form_id = form_service.save_form(form)
            form_ids.append(form_id)
        
        # Test search functionality if available
        all_forms = form_service.list_forms()
        
        # Manual search through results
        emergency_forms = [f for f in all_forms if "Emergency" in f.get('subject', '')]
        assert len(emergency_forms) >= 2  # Should find both emergency forms
        
        status_forms = [f for f in all_forms if "Status" in f.get('subject', '')]
        assert len(status_forms) >= 1