#!/usr/bin/env python3
"""Test script for multi-form service validation.

This script tests the multi-form database service implementation to ensure that
Task 6.2: Enhanced Database Operations works correctly and is ready for completion.

Tests:
    - Multi-form service initialization
    - Form saving and loading
    - Search functionality with full-text search
    - Version history tracking
    - Batch operations
    - Statistics and metadata

Usage:
    python3 test_multi_form_service.py
"""

import sys
import traceback
import tempfile
import os
from datetime import datetime, timedelta
from typing import List
from pathlib import Path

# Add source directory to path
sys.path.insert(0, 'src')

def test_multi_form_service_initialization():
    """Test multi-form service initialization and setup."""
    print("🧪 Testing Multi-Form Service Initialization")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    try:
        # Import required modules
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.multi_form_service import (
            MultiFormService, FormQuery, FormSortField, SortDirection,
            BatchOperationResult, create_multi_form_service
        )
        
        print("✅ Multi-form service modules imported successfully")
        
        # Test 1: Create service with temporary database
        total_tests += 1
        print("\n🔬 Test 1: Service Creation and Initialization")
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                temp_db_path = temp_db.name
            
            # Initialize database
            db_manager = DatabaseManager(Path(temp_db_path))
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            
            # Create multi-form service
            service = MultiFormService(db_manager)
            service.initialize()
            
            assert service is not None
            assert service.db_manager == db_manager
            assert service.search_index is not None
            
            print("   ✅ Multi-form service created and initialized successfully")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Service initialization failed: {e}")
            traceback.print_exc()
        finally:
            # Clean up
            try:
                os.unlink(temp_db_path)
            except:
                pass
        
        # Test 2: Factory function
        total_tests += 1
        print("\n🔬 Test 2: Factory Function")
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                temp_db_path = temp_db.name
            
            # Initialize database
            db_manager = DatabaseManager(Path(temp_db_path))
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            
            # Use factory function
            service = create_multi_form_service(db_manager)
            assert service is not None
            
            print("   ✅ Factory function works correctly")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Factory function failed: {e}")
            traceback.print_exc()
        finally:
            try:
                os.unlink(temp_db_path)
            except:
                pass
        
        # Test 3: Query and result classes
        total_tests += 1
        print("\n🔬 Test 3: Query and Result Classes")
        try:
            # Test FormQuery
            query = FormQuery()
            assert query.sort_field == FormSortField.UPDATED_DATE
            assert query.sort_direction == SortDirection.DESCENDING
            assert query.offset == 0
            
            # Test BatchOperationResult
            result = BatchOperationResult()
            result.add_success(123)
            result.add_failure(456, "Test error")
            
            assert result.success_count == 1
            assert result.failure_count == 1
            assert result.total_count == 2
            assert result.success_rate == 0.5
            assert result.has_failures is True
            assert result.is_complete_success is False
            
            print("   ✅ Query and result classes work correctly")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Query and result classes failed: {e}")
            traceback.print_exc()
        
    except ImportError as e:
        print(f"❌ Failed to import multi-form service modules: {e}")
        traceback.print_exc()
        return False
    
    # Results summary
    print(f"\n{'='*50}")
    print(f"🧪 MULTI-FORM SERVICE INITIALIZATION RESULTS")
    print(f"{'='*50}")
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests


def test_form_storage_and_retrieval():
    """Test form storage and retrieval operations."""
    print("\n💾 Testing Form Storage and Retrieval")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    try:
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.multi_form_service import MultiFormService
        from src.forms.ics213 import ICS213Form, Person
        from src.models.ics214 import ICS214Form, ActivityEntry
        from datetime import datetime
        
        # Create temporary database and service
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            db_manager = DatabaseManager(Path(temp_db_path))
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            service = MultiFormService(db_manager)
            service.initialize()
            
            # Test 1: Save ICS-213 form
            total_tests += 1
            print("\n🔬 Test 1: Save ICS-213 Form")
            try:
                form_213 = ICS213Form()
                form_213.data.incident_name = "Test Incident Alpha"
                form_213.data.to = Person(name="John Doe", position="IC")
                form_213.data.from_person = Person(name="Jane Smith", position="Operations")
                form_213.data.subject = "Test Message Subject"
                form_213.data.message = "This is a test message for ICS-213 form storage."
                form_213.data.date = "2025-05-30"
                form_213.data.time = "14:30"
                # Ensure the form validates before saving
                form_213.validate()
                
                form_id = service.save_form(form_213, "Test User")
                assert form_id is not None
                assert form_id > 0
                
                print(f"   ✅ ICS-213 form saved with ID {form_id}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ ICS-213 form save failed: {e}")
                traceback.print_exc()
            
            # Test 2: Save ICS-214 form
            total_tests += 1
            print("\n🔬 Test 2: Save ICS-214 Form")
            try:
                form_214 = ICS214Form()
                form_214.data.incident_name = "Test Incident Bravo"
                form_214.data.name = "John Doe"
                form_214.data.ics_position = "Operations Section Chief"
                form_214.data.home_agency = "Fire Department Alpha"
                
                # Add an activity
                activity = ActivityEntry(
                    datetime=datetime.now(),
                    notable_activities="Arrived on scene and established command post"
                )
                form_214.data.add_activity(activity)
                
                form_214_id = service.save_form(form_214, "Test User")
                assert form_214_id is not None
                assert form_214_id > 0
                
                print(f"   ✅ ICS-214 form saved with ID {form_214_id}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ ICS-214 form save failed: {e}")
                traceback.print_exc()
            
            # Test 3: Load forms
            total_tests += 1
            print("\n🔬 Test 3: Load Forms")
            try:
                # Load the ICS-213 form
                loaded_213 = service.load_form(form_id)
                assert loaded_213 is not None
                assert loaded_213.data.incident_name == "Test Incident Alpha"
                assert loaded_213.data.subject == "Test Message Subject"
                
                # Load the ICS-214 form
                loaded_214 = service.load_form(form_214_id)
                assert loaded_214 is not None
                assert loaded_214.data.incident_name == "Test Incident Bravo"
                assert loaded_214.data.name == "John Doe"
                
                print("   ✅ Forms loaded successfully")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Form loading failed: {e}")
                traceback.print_exc()
            
            # Test 4: Bulk load forms
            total_tests += 1
            print("\n🔬 Test 4: Bulk Load Forms")
            try:
                forms = service.load_forms([form_id, form_214_id])
                assert len(forms) == 2
                
                # Check form types
                form_types = [form.get_form_type().value for form in forms]
                assert 'ICS-213' in form_types
                assert 'ICS-214' in form_types
                
                print("   ✅ Bulk form loading works correctly")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Bulk form loading failed: {e}")
                traceback.print_exc()
        
        finally:
            os.unlink(temp_db_path)
        
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return False
    
    # Results summary
    print(f"\n{'='*50}")
    print(f"💾 FORM STORAGE AND RETRIEVAL RESULTS")
    print(f"{'='*50}")
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests


def test_search_functionality():
    """Test search and query functionality."""
    print("\n🔍 Testing Search Functionality")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    try:
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.multi_form_service import (
            MultiFormService, FormQuery, FormSortField, SortDirection
        )
        from src.models.base_form import FormType
        from src.forms.ics213 import ICS213Form, Person
        
        # Create temporary database and service
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            db_manager = DatabaseManager(Path(temp_db_path))
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            service = MultiFormService(db_manager)
            service.initialize()
            
            # Create test forms with different content
            forms_data = [
                ("Urgent Medical Emergency", "urgent medical situation", "Alpha Incident"),
                ("Routine Status Update", "normal operations continuing", "Bravo Incident"),
                ("Equipment Request", "need additional fire engines", "Alpha Incident"),
                ("Personnel Assignment", "assign medical team to sector", "Charlie Incident")
            ]
            
            form_ids = []
            for subject, message, incident in forms_data:
                form = ICS213Form()
                form.data.incident_name = incident
                form.data.to = Person(name="Command", position="IC")
                form.data.from_person = Person(name="Operations", position="Ops")
                form.data.subject = subject
                form.data.message = message
                form.data.date = "2025-05-30"
                form.data.time = "14:30"
                
                form_id = service.save_form(form, "Test User")
                form_ids.append(form_id)
            
            # Test 1: Basic search without filters
            total_tests += 1
            print("\n🔬 Test 1: Basic Search")
            try:
                query = FormQuery()
                results = service.search_forms(query)
                
                assert len(results) == 4  # Should find all forms
                assert all('id' in result for result in results)
                assert all('form_type' in result for result in results)
                
                print(f"   ✅ Basic search found {len(results)} forms")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Basic search failed: {e}")
                traceback.print_exc()
            
            # Test 2: Text search
            total_tests += 1
            print("\n🔬 Test 2: Text Search")
            try:
                query = FormQuery(search_text="urgent")
                results = service.search_forms(query)
                
                # Should find forms with "urgent" in content
                assert len(results) >= 1
                
                # Check that results contain expected form
                subjects = [r.get('title', '') for r in results]
                assert any('urgent' in s.lower() for s in subjects)
                
                print(f"   ✅ Text search found {len(results)} forms with 'urgent'")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Text search failed: {e}")
                traceback.print_exc()
            
            # Test 3: Filter by form type
            total_tests += 1
            print("\n🔬 Test 3: Filter by Form Type")
            try:
                query = FormQuery(form_types=[FormType.ICS_213])
                results = service.search_forms(query)
                
                # Should find all ICS-213 forms
                assert len(results) == 4
                assert all(r['form_type'] == 'ICS-213' for r in results)
                
                print(f"   ✅ Form type filter found {len(results)} ICS-213 forms")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Form type filter failed: {e}")
                traceback.print_exc()
            
            # Test 4: Sort and limit
            total_tests += 1
            print("\n🔬 Test 4: Sort and Limit")
            try:
                query = FormQuery(
                    sort_field=FormSortField.TITLE,
                    sort_direction=SortDirection.ASCENDING,
                    limit=2
                )
                results = service.search_forms(query)
                
                assert len(results) == 2  # Limited to 2 results
                # Should be sorted by title ascending
                
                print(f"   ✅ Sort and limit returned {len(results)} forms")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Sort and limit failed: {e}")
                traceback.print_exc()
        
        finally:
            os.unlink(temp_db_path)
    
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return False
    
    # Results summary
    print(f"\n{'='*50}")
    print(f"🔍 SEARCH FUNCTIONALITY RESULTS")
    print(f"{'='*50}")
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests


def test_advanced_features():
    """Test advanced features like version history and statistics."""
    print("\n⚡ Testing Advanced Features")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    try:
        from src.database.connection import DatabaseManager
        from src.database.schema import SchemaManager
        from src.services.multi_form_service import MultiFormService
        from src.forms.ics213 import ICS213Form, Person
        
        # Create temporary database and service
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            db_manager = DatabaseManager(Path(temp_db_path))
            schema_manager = SchemaManager(db_manager)
            schema_manager.initialize_database()
            service = MultiFormService(db_manager)
            service.initialize()
            
            # Create and save a form
            form = ICS213Form()
            form.data.incident_name = "Version Test Incident"
            form.data.to = Person(name="Command", position="IC")
            form.data.from_person = Person(name="Operations", position="Ops")
            form.data.subject = "Original Subject"
            form.data.message = "Original message content"
            form.data.date = "2025-05-30"
            form.data.time = "14:30"
            
            form_id = service.save_form(form, "Test User")
            
            # Test 1: Update form and version history
            total_tests += 1
            print("\n🔬 Test 1: Form Updates and Version History")
            try:
                # Update the form
                form.data.subject = "Updated Subject"
                form.data.message = "Updated message content"
                
                updated = service.update_form(form_id, form, "Update User", "Changed subject and message")
                assert updated is True
                
                # Get version history
                versions = service.get_form_versions(form_id)
                assert len(versions) == 2  # Original + update
                
                # Check version details
                assert versions[0]['version'] == 2  # Most recent first
                assert versions[0]['changed_by'] == "Update User"
                assert versions[1]['version'] == 1
                assert versions[1]['changed_by'] == "Test User"
                
                print("   ✅ Form updates and version history work correctly")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Form updates and version history failed: {e}")
                traceback.print_exc()
            
            # Test 2: Statistics
            total_tests += 1
            print("\n🔬 Test 2: Database Statistics")
            try:
                stats = service.get_statistics()
                
                assert 'total_forms' in stats
                assert 'forms_by_type' in stats
                assert 'forms_by_status' in stats
                assert 'recent_forms' in stats
                
                assert stats['total_forms'] >= 1
                assert 'ICS-213' in stats['forms_by_type']
                
                print(f"   ✅ Statistics: {stats['total_forms']} total forms")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Statistics failed: {e}")
                traceback.print_exc()
            
            # Test 3: Delete form
            total_tests += 1
            print("\n🔬 Test 3: Form Deletion")
            try:
                deleted = service.delete_form(form_id)
                assert deleted is True
                
                # Try to load deleted form
                loaded = service.load_form(form_id)
                assert loaded is None
                
                print("   ✅ Form deletion works correctly")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Form deletion failed: {e}")
                traceback.print_exc()
            
            # Test 4: Batch operations
            total_tests += 1
            print("\n🔬 Test 4: Batch Operations")
            try:
                # Create multiple forms for batch testing
                batch_ids = []
                for i in range(3):
                    batch_form = ICS213Form()
                    batch_form.data.incident_name = f"Batch Test {i}"
                    batch_form.data.to = Person(name="Command", position="IC")
                    batch_form.data.from_person = Person(name="Ops", position="Operations")
                    batch_form.data.subject = f"Batch Subject {i}"
                    batch_form.data.message = f"Batch message {i}"
                    batch_form.data.date = "2025-05-30"
                    batch_form.data.time = "15:00"
                    
                    batch_id = service.save_form(batch_form, "Batch User")
                    batch_ids.append(batch_id)
                
                # Batch delete
                result = service.bulk_delete_forms(batch_ids)
                
                assert result.success_count == 3
                assert result.failure_count == 0
                assert result.is_complete_success is True
                
                print(f"   ✅ Batch deletion: {result.success_count}/{result.total_count} successful")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Batch operations failed: {e}")
                traceback.print_exc()
        
        finally:
            os.unlink(temp_db_path)
    
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return False
    
    # Results summary
    print(f"\n{'='*50}")
    print(f"⚡ ADVANCED FEATURES RESULTS")
    print(f"{'='*50}")
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests


def main():
    """Run all multi-form service tests."""
    print("🚀 RadioForms Multi-Form Service Validation")
    print("=" * 60)
    print("Testing Phase 2 Task 6.2 implementation")
    print()
    
    # Test initialization
    init_success = test_multi_form_service_initialization()
    
    # Test storage and retrieval
    storage_success = test_form_storage_and_retrieval()
    
    # Test search functionality
    search_success = test_search_functionality()
    
    # Test advanced features
    advanced_success = test_advanced_features()
    
    print(f"\n{'='*60}")
    print("📋 OVERALL MULTI-FORM SERVICE VALIDATION RESULTS")
    print("=" * 60)
    
    if init_success and storage_success and search_success and advanced_success:
        print("🎯 MULTI-FORM SERVICE STATUS: ✅ READY")
        print("   • Service initialization working")
        print("   • Form storage and retrieval functional")
        print("   • Search and filtering capabilities implemented")
        print("   • Version history tracking working")
        print("   • Batch operations functional")
        print("   • Database statistics available")
        print("   • Ready for Task 6.2 completion")
        return True
    else:
        print("🎯 MULTI-FORM SERVICE STATUS: ⚠️ NEEDS ATTENTION")
        if not init_success:
            print("   • Service initialization issues need resolution")
        if not storage_success:
            print("   • Storage and retrieval issues need attention")
        if not search_success:
            print("   • Search functionality issues need resolution")
        if not advanced_success:
            print("   • Advanced features issues need attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)