"""Performance benchmark tests for RadioForms application.

This module contains performance tests to ensure the application
meets the speed requirements specified in the development plan.
"""

import time
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


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "perf_test.db"
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
    
    def create_test_form(self, index=0):
        """Create a test form for performance testing."""
        data = ICS213Data(
            incident_name=f"Performance Test Incident {index}",
            to=Person(name=f"Commander {index}", position="IC", 
                     signature=f"C{index}", contact_info=f"Radio {index}"),
            from_person=Person(name=f"Operator {index}", position="Ops",
                             signature=f"O{index}", contact_info=f"Radio {index+100}"),
            subject=f"Performance Test Message {index}",
            date="2025-05-30",
            time=f"{20 + (index % 4):02d}:{(index % 60):02d}",
            message=f"This is performance test message number {index}. " * 10,  # Longer message
            priority=Priority.URGENT if index % 2 == 0 else Priority.ROUTINE,
            reply_requested=index % 3 == 0,
            approved_by=Person(name=f"Approver {index}", position="Safety", signature=f"A{index}"),
            reply=f"Reply to message {index}" if index % 4 == 0 else "",
            replied_by=Person(name=f"Replier {index}", position="IC") if index % 4 == 0 else None,
            reply_date_time=f"2025-05-30 {21 + (index % 3):02d}:{(index % 60):02d}" if index % 4 == 0 else ""
        )
        return ICS213Form(data)
    
    def test_form_creation_performance(self):
        """Test form creation performance - should be <1ms per form."""
        num_forms = 100
        
        start_time = time.time()
        forms = []
        for i in range(num_forms):
            form = self.create_test_form(i)
            forms.append(form)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / num_forms
        
        print(f"Created {num_forms} forms in {total_time:.3f}s (avg: {avg_time*1000:.1f}ms per form)")
        
        # Should create forms in <1ms each on average
        assert avg_time < 0.001, f"Form creation too slow: {avg_time*1000:.1f}ms per form"
        assert len(forms) == num_forms
    
    def test_form_validation_performance(self):
        """Test form validation performance - should be <5ms per form."""
        forms = [self.create_test_form(i) for i in range(50)]
        
        start_time = time.time()
        validation_results = []
        for form in forms:
            is_valid = form.validate()
            validation_results.append(is_valid)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / len(forms)
        
        print(f"Validated {len(forms)} forms in {total_time:.3f}s (avg: {avg_time*1000:.1f}ms per form)")
        
        # Should validate forms in <5ms each
        assert avg_time < 0.005, f"Form validation too slow: {avg_time*1000:.1f}ms per form"
        assert all(validation_results)  # All forms should be valid
    
    def test_database_save_performance(self, form_service):
        """Test database save performance - should be <100ms per save."""
        forms = [self.create_test_form(i) for i in range(20)]
        
        save_times = []
        for form in forms:
            start_time = time.time()
            form_id = form_service.save_form(form)
            end_time = time.time()
            
            save_time = end_time - start_time
            save_times.append(save_time)
            
            assert form_id is not None
        
        avg_save_time = sum(save_times) / len(save_times)
        max_save_time = max(save_times)
        
        print(f"Saved {len(forms)} forms - avg: {avg_save_time*1000:.1f}ms, max: {max_save_time*1000:.1f}ms")
        
        # Average save time should be <100ms
        assert avg_save_time < 0.1, f"Database save too slow: {avg_save_time*1000:.1f}ms average"
        
        # No single save should take more than 200ms
        assert max_save_time < 0.2, f"Database save too slow: {max_save_time*1000:.1f}ms maximum"
    
    def test_database_load_performance(self, form_service):
        """Test database load performance - should be <50ms per load."""
        # First, save some forms
        form_ids = []
        for i in range(20):
            form = self.create_test_form(i)
            form_id = form_service.save_form(form)
            form_ids.append(form_id)
        
        # Now test loading performance
        load_times = []
        for form_id in form_ids:
            start_time = time.time()
            loaded_form = form_service.load_form(form_id)
            end_time = time.time()
            
            load_time = end_time - start_time
            load_times.append(load_time)
            
            assert loaded_form is not None
        
        avg_load_time = sum(load_times) / len(load_times)
        max_load_time = max(load_times)
        
        print(f"Loaded {len(form_ids)} forms - avg: {avg_load_time*1000:.1f}ms, max: {max_load_time*1000:.1f}ms")
        
        # Average load time should be <50ms
        assert avg_load_time < 0.05, f"Database load too slow: {avg_load_time*1000:.1f}ms average"
        
        # No single load should take more than 100ms
        assert max_load_time < 0.1, f"Database load too slow: {max_load_time*1000:.1f}ms maximum"
    
    def test_form_list_performance(self, form_service):
        """Test form listing performance with many forms."""
        # Create many forms
        num_forms = 100
        for i in range(num_forms):
            form = self.create_test_form(i)
            form_service.save_form(form)
        
        # Test listing performance
        start_time = time.time()
        forms_list = form_service.list_forms()
        end_time = time.time()
        
        list_time = end_time - start_time
        
        print(f"Listed {len(forms_list)} forms in {list_time*1000:.1f}ms")
        
        # Should list forms quickly even with many forms
        assert list_time < 0.5, f"Form listing too slow: {list_time*1000:.1f}ms"
        assert len(forms_list) >= num_forms
    
    def test_json_export_performance(self, file_service):
        """Test JSON export performance - should be <500ms per form."""
        forms = [self.create_test_form(i) for i in range(10)]
        
        with TemporaryDirectory() as temp_dir:
            export_times = []
            
            for i, form in enumerate(forms):
                export_path = Path(temp_dir) / f"export_{i}.json"
                
                start_time = time.time()
                success = file_service.export_form_to_json(form, export_path)
                end_time = time.time()
                
                export_time = end_time - start_time
                export_times.append(export_time)
                
                assert success
                assert export_path.exists()
            
            avg_export_time = sum(export_times) / len(export_times)
            max_export_time = max(export_times)
            
            print(f"Exported {len(forms)} forms - avg: {avg_export_time*1000:.1f}ms, max: {max_export_time*1000:.1f}ms")
            
            # Should export quickly
            assert avg_export_time < 0.5, f"JSON export too slow: {avg_export_time*1000:.1f}ms average"
            assert max_export_time < 1.0, f"JSON export too slow: {max_export_time*1000:.1f}ms maximum"
    
    def test_json_import_performance(self, file_service):
        """Test JSON import performance - should be <300ms per form."""
        forms = [self.create_test_form(i) for i in range(10)]
        
        with TemporaryDirectory() as temp_dir:
            # First export the forms
            export_paths = []
            for i, form in enumerate(forms):
                export_path = Path(temp_dir) / f"import_test_{i}.json"
                file_service.export_form_to_json(form, export_path)
                export_paths.append(export_path)
            
            # Now test import performance
            import_times = []
            for export_path in export_paths:
                start_time = time.time()
                imported_form = file_service.import_form_from_json(export_path)
                end_time = time.time()
                
                import_time = end_time - start_time
                import_times.append(import_time)
                
                assert imported_form is not None
            
            avg_import_time = sum(import_times) / len(import_times)
            max_import_time = max(import_times)
            
            print(f"Imported {len(export_paths)} forms - avg: {avg_import_time*1000:.1f}ms, max: {max_import_time*1000:.1f}ms")
            
            # Should import quickly
            assert avg_import_time < 0.3, f"JSON import too slow: {avg_import_time*1000:.1f}ms average"
            assert max_import_time < 0.6, f"JSON import too slow: {max_import_time*1000:.1f}ms maximum"
    
    def test_multiple_forms_export_performance(self, file_service):
        """Test performance of exporting multiple forms at once."""
        num_forms = 50
        forms = [self.create_test_form(i) for i in range(num_forms)]
        
        with TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "multiple_forms.json"
            
            start_time = time.time()
            success = file_service.export_multiple_forms(forms, export_path)
            end_time = time.time()
            
            export_time = end_time - start_time
            
            print(f"Exported {num_forms} forms in batch: {export_time*1000:.1f}ms")
            
            assert success
            assert export_path.exists()
            
            # Should export multiple forms efficiently
            assert export_time < 2.0, f"Multiple forms export too slow: {export_time*1000:.1f}ms"
    
    def test_memory_usage_basic(self, form_service):
        """Test basic memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and process many forms
        num_operations = 100
        for i in range(num_operations):
            form = self.create_test_form(i)
            form_id = form_service.save_form(form)
            loaded_form = form_service.load_form(form_id)
            assert loaded_form is not None
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable for the operations performed
        assert memory_increase < 100, f"Excessive memory usage: {memory_increase:.1f}MB increase"
    
    def test_concurrent_database_operations(self, form_service):
        """Test performance with multiple concurrent-like operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def save_forms_batch(start_index, count):
            """Save a batch of forms."""
            try:
                batch_times = []
                for i in range(count):
                    form = self.create_test_form(start_index + i)
                    start_time = time.time()
                    form_id = form_service.save_form(form)
                    end_time = time.time()
                    
                    batch_times.append(end_time - start_time)
                    results.append(form_id)
                
                avg_time = sum(batch_times) / len(batch_times)
                return avg_time
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Simulate concurrent operations
        start_time = time.time()
        
        # Run operations in sequence (simulating concurrent load)
        batch_size = 10
        num_batches = 5
        
        for batch in range(num_batches):
            avg_time = save_forms_batch(batch * batch_size, batch_size)
            if avg_time:
                print(f"Batch {batch + 1}: avg {avg_time*1000:.1f}ms per save")
        
        total_time = time.time() - start_time
        
        print(f"Processed {len(results)} forms in {total_time:.3f}s with {len(errors)} errors")
        
        # Should handle operations efficiently
        assert len(errors) == 0, f"Errors during concurrent operations: {errors}"
        assert len(results) == batch_size * num_batches
        assert total_time < 10.0, f"Concurrent operations too slow: {total_time:.3f}s"
    
    def test_large_form_handling(self, form_service, file_service):
        """Test performance with large form data."""
        # Create form with large message content
        large_message = "Large message content. " * 1000  # ~23KB message
        
        data = ICS213Data(
            incident_name="Large Form Performance Test",
            to=Person(name="Test Commander", position="IC"),
            from_person=Person(name="Test Operator", position="Ops"),
            subject="Large Message Test",
            date="2025-05-30",
            time="23:45",
            message=large_message,
            priority=Priority.URGENT
        )
        large_form = ICS213Form(data)
        
        # Test validation performance
        start_time = time.time()
        is_valid = large_form.validate()
        validation_time = time.time() - start_time
        
        assert is_valid
        print(f"Large form validation: {validation_time*1000:.1f}ms")
        assert validation_time < 0.01, f"Large form validation too slow: {validation_time*1000:.1f}ms"
        
        # Test save performance
        start_time = time.time()
        form_id = form_service.save_form(large_form)
        save_time = time.time() - start_time
        
        assert form_id is not None
        print(f"Large form save: {save_time*1000:.1f}ms")
        assert save_time < 0.2, f"Large form save too slow: {save_time*1000:.1f}ms"
        
        # Test load performance
        start_time = time.time()
        loaded_form = form_service.load_form(form_id)
        load_time = time.time() - start_time
        
        assert loaded_form is not None
        assert len(loaded_form.data.message) == len(large_message)
        print(f"Large form load: {load_time*1000:.1f}ms")
        assert load_time < 0.1, f"Large form load too slow: {load_time*1000:.1f}ms"
        
        # Test JSON export performance
        with TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "large_form.json"
            
            start_time = time.time()
            success = file_service.export_form_to_json(large_form, export_path)
            export_time = time.time() - start_time
            
            assert success
            print(f"Large form JSON export: {export_time*1000:.1f}ms")
            assert export_time < 0.5, f"Large form export too slow: {export_time*1000:.1f}ms"