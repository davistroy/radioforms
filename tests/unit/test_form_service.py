"""Unit tests for form service."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.services.form_service import FormService
from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority, FormStatus
from src.database.connection import DatabaseManager, DatabaseError
from src.database.schema import SchemaManager


class TestFormService:
    """Test FormService class."""
    
    def test_init(self, tmp_path):
        """Test FormService initialization."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        form_service = FormService(db_manager)
        
        assert form_service.db_manager == db_manager
        assert form_service.logger is not None
    
    def test_save_new_form(self, tmp_path):
        """Test saving a new form."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create test form
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="Test message content"
        )
        form = ICS213Form(data)
        
        # Save form
        form_id = form_service.save_form(form)
        
        assert isinstance(form_id, int)
        assert form_id > 0
    
    def test_save_update_form(self, tmp_path):
        """Test updating an existing form."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create and save initial form
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Original Subject",
            date="2025-05-30",
            time="14:30",
            message="Original message"
        )
        form = ICS213Form(data)
        form_id = form_service.save_form(form)
        
        # Update form
        form.data.subject = "Updated Subject"
        form.data.message = "Updated message"
        
        updated_id = form_service.save_form(form, form_id)
        
        assert updated_id == form_id
        
        # Verify update
        loaded_form = form_service.load_form(form_id)
        assert loaded_form.data.subject == "Updated Subject"
        assert loaded_form.data.message == "Updated message"
    
    def test_load_form(self, tmp_path):
        """Test loading a form."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create and save form
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Test Subject",
            date="2025-05-30",
            time="14:30",
            message="Test message",
            priority=Priority.URGENT
        )
        form = ICS213Form(data)
        form_id = form_service.save_form(form)
        
        # Load form
        loaded_form = form_service.load_form(form_id)
        
        assert loaded_form.data.subject == "Test Subject"
        assert loaded_form.data.to.name == "Jane Doe"
        assert loaded_form.data.from_person.name == "John Smith"
        assert loaded_form.data.priority == Priority.URGENT
    
    def test_load_nonexistent_form(self, tmp_path):
        """Test loading a form that doesn't exist."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Try to load nonexistent form
        with pytest.raises(DatabaseError, match="not found"):
            form_service.load_form(999)
    
    def test_list_forms(self, tmp_path):
        """Test listing forms."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create and save multiple forms
        for i in range(3):
            data = ICS213Data(
                to=Person(name=f"Person {i}", position="IC"),
                from_person=Person(name="John Smith", position="Ops"),
                subject=f"Test Subject {i}",
                date="2025-05-30",
                time="14:30",
                message=f"Test message {i}"
            )
            form = ICS213Form(data)
            form_service.save_form(form)
        
        # List forms
        forms = form_service.list_forms()
        
        assert len(forms) == 3
        assert all('id' in form for form in forms)
        assert all('title' in form for form in forms)
        assert all('status' in form for form in forms)
    
    def test_delete_form(self, tmp_path):
        """Test deleting a form."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create and save form
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Test Subject",
            date="2025-05-30",
            time="14:30",
            message="Test message"
        )
        form = ICS213Form(data)
        form_id = form_service.save_form(form)
        
        # Delete form
        success = form_service.delete_form(form_id)
        assert success
        
        # Verify deletion
        with pytest.raises(DatabaseError):
            form_service.load_form(form_id)
    
    def test_delete_nonexistent_form(self, tmp_path):
        """Test deleting a form that doesn't exist."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Try to delete nonexistent form
        success = form_service.delete_form(999)
        assert not success
    
    def test_search_forms(self, tmp_path):
        """Test searching forms."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Create forms with different subjects
        subjects = ["Emergency Response", "Resource Request", "Status Update"]
        for subject in subjects:
            data = ICS213Data(
                to=Person(name="Jane Doe", position="IC"),
                from_person=Person(name="John Smith", position="Ops"),
                subject=subject,
                date="2025-05-30",
                time="14:30",
                message="Test message"
            )
            form = ICS213Form(data)
            form_service.save_form(form)
        
        # Search for specific forms
        results = form_service.search_forms("Emergency")
        assert len(results) == 1
        assert "Emergency Response" in results[0]['title']
        
        results = form_service.search_forms("Request")
        assert len(results) == 1
        assert "Resource Request" in results[0]['title']
        
        results = form_service.search_forms("Nonexistent")
        assert len(results) == 0
    
    def test_get_form_count(self, tmp_path):
        """Test getting form count."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        form_service = FormService(db_manager)
        
        # Initially no forms
        assert form_service.get_form_count() == 0
        
        # Create forms
        for i in range(5):
            data = ICS213Data(
                to=Person(name="Jane Doe", position="IC"),
                from_person=Person(name="John Smith", position="Ops"),
                subject=f"Test {i}",
                date="2025-05-30",
                time="14:30",
                message="Test message"
            )
            form = ICS213Form(data)
            form_service.save_form(form)
        
        assert form_service.get_form_count() == 5
    
    def test_validate_form_data(self, tmp_path):
        """Test form validation."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        form_service = FormService(db_manager)
        
        # Valid form
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops"),
            subject="Test Subject",
            date="2025-05-30",
            time="14:30",
            message="Test message"
        )
        form = ICS213Form(data)
        
        errors = form_service.validate_form_data(form)
        assert len(errors) == 0
        
        # Invalid form (missing required fields)
        invalid_data = ICS213Data()
        invalid_form = ICS213Form(invalid_data)
        
        errors = form_service.validate_form_data(invalid_form)
        assert len(errors) > 0
    
    def test_generate_form_number(self, tmp_path):
        """Test form number generation."""
        # Setup database
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        form_service = FormService(db_manager)
        
        data = ICS213Data()
        form = ICS213Form(data)
        
        form_number = form_service._generate_form_number(form)
        
        assert form_number.startswith("ICS213-")
        assert len(form_number) > 10  # Should include timestamp