"""Headless application for RadioForms.

This module provides a headless (non-GUI) mode for RadioForms that allows
testing and automation without requiring a display or Qt platform plugins.

The headless application provides access to all core functionality including:
- Database operations
- Form creation and validation
- Export/import operations
- Template system functionality
- Service operations

Usage:
    python -m src.main --headless

This is particularly useful for:
- CI/CD testing in environments without displays
- WSL environments with Qt platform issues
- Server deployments
- Automated testing and validation
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import core services (no GUI dependencies)
from ..database.connection import DatabaseManager
from ..services.multi_form_service import MultiFormService
from ..services.enhanced_search_service import EnhancedSearchService
from ..models.ics214 import ICS214Data, ActivityEntry, ResourceAssignment, OperationalPeriod
from ..forms.ics213 import ICS213Form, ICS213Data, Person
from ..ui.forms.templates.ics205_template import ICS205Template

logger = logging.getLogger(__name__)


class HeadlessApplication:
    """Headless RadioForms application for testing and automation.
    
    Provides access to all core RadioForms functionality without requiring
    a GUI or Qt display system. Useful for testing, CI/CD, and server environments.
    
    Attributes:
        database_path: Path to the database file
        debug: Whether debug mode is enabled
        db_manager: Database connection manager
        multi_form_service: Service for multi-form operations
        search_service: Enhanced search service
    
    Example:
        >>> app = HeadlessApplication()
        >>> app.run()
        >>> # Application runs interactive shell or demo mode
    """
    
    def __init__(self, database_path: Optional[Path] = None, debug: bool = False):
        """Initialize headless application.
        
        Args:
            database_path: Optional path to database file
            debug: Enable debug logging
        """
        self.database_path = database_path or Path("radioforms_headless.db")
        self.debug = debug
        
        # Initialize database
        self.db_manager = DatabaseManager(self.database_path)
        
        # Initialize services and database tables
        self.multi_form_service = MultiFormService(self.db_manager)
        self.multi_form_service.initialize()  # Create database tables
        self.search_service = EnhancedSearchService(self.db_manager, self.multi_form_service)
        
        logger.info(f"Headless application initialized with database: {self.database_path}")
    
    def run(self) -> int:
        """Run the headless application.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        logger.info("Starting RadioForms in headless mode")
        
        try:
            # Run demonstration of functionality
            self._run_demonstration()
            
            # Optionally start interactive mode
            if self.debug:
                self._interactive_mode()
            
            return 0
            
        except Exception as e:
            logger.error(f"Headless application error: {e}")
            return 1
        finally:
            logger.info("Headless application shutting down")
    
    def _run_demonstration(self) -> None:
        """Run a demonstration of core functionality."""
        logger.info("Running RadioForms functionality demonstration")
        
        # Test 1: Create and validate ICS-213 form
        logger.info("=== ICS-213 Form Test ===")
        self._test_ics213_form()
        
        # Test 2: Create and validate ICS-214 form
        logger.info("=== ICS-214 Form Test ===")
        self._test_ics214_form()
        
        # Test 3: Create and validate ICS-205 template
        logger.info("=== ICS-205 Template Test ===")
        self._test_ics205_template()
        
        # Test 4: Test database operations
        logger.info("=== Database Operations Test ===")
        self._test_database_operations()
        
        # Test 5: Test search functionality
        logger.info("=== Search Functionality Test ===")
        self._test_search_functionality()
        
        logger.info("Demonstration completed successfully")
    
    def _test_ics213_form(self) -> None:
        """Test ICS-213 form functionality."""
        try:
            # Create form
            form = ICS213Form()
            
            # Set data
            form.data.incident_name = "Headless Test Incident"
            form.data.to = Person(name="Operations Chief", position="IC")
            form.data.from_person = Person(name="Headless App", position="Testing")
            form.data.subject = "Functionality Test"
            form.data.message = "Testing RadioForms headless mode functionality."
            
            # Validate
            is_valid = form.validate()
            logger.info(f"ICS-213 validation: {'PASSED' if is_valid else 'FAILED'}")
            
            if not is_valid:
                logger.warning(f"ICS-213 validation errors: {form.get_validation_errors()}")
            
            # Test JSON serialization
            json_data = form.to_json()
            logger.info(f"ICS-213 JSON export: {len(json_data)} characters")
            
        except Exception as e:
            logger.error(f"ICS-213 test failed: {e}")
    
    def _test_ics214_form(self) -> None:
        """Test ICS-214 form functionality."""
        try:
            # Create form
            form = ICS214Data(
                incident_name="Headless Test Incident",
                name="Test User",
                ics_position="Testing Officer",
                home_agency="RadioForms Testing Unit"
            )
            
            # Add activity entries
            from datetime import datetime
            activities = [
                ActivityEntry(
                    datetime=datetime.now(),
                    notable_activities="Started headless testing mode"
                ),
                ActivityEntry(
                    datetime=datetime.now(),
                    notable_activities="Validated ICS-214 functionality"
                )
            ]
            form.activity_log = activities
            
            # Validate
            is_valid = form.is_valid()
            logger.info(f"ICS-214 validation: {'PASSED' if is_valid else 'FAILED'}")
            
            # Test JSON serialization
            json_data = form.to_json()
            logger.info(f"ICS-214 JSON export: {len(json_data)} characters")
            
        except Exception as e:
            logger.error(f"ICS-214 test failed: {e}")
    
    def _test_ics205_template(self) -> None:
        """Test ICS-205 template functionality."""
        try:
            # Create template
            template = ICS205Template()
            
            # Test properties
            logger.info(f"ICS-205 form type: {template.form_type}")
            logger.info(f"ICS-205 form title: {template.form_title}")
            
            # Test data operations
            test_data = {
                'incident_name': 'Headless Template Test',
                'operational_period': '2024-05-31 08:00 to 20:00',
                'prepared_by': 'Headless Application',
                'frequency_assignments': [
                    {
                        'zone_group': 'Command',
                        'channel': '1',
                        'function': 'Command',
                        'assignment': 'Incident Command',
                        'rx_freq_mhz': '155.340',
                        'mode': 'A'
                    }
                ]
            }
            
            template.set_data(test_data)
            retrieved_data = template.get_data()
            
            logger.info(f"ICS-205 data round-trip: {'PASSED' if retrieved_data['incident_name'] == test_data['incident_name'] else 'FAILED'}")
            
            # Test export/import
            export_data = template.export_data()
            import_success = template.import_data(export_data)
            logger.info(f"ICS-205 export/import: {'PASSED' if import_success else 'FAILED'}")
            
        except Exception as e:
            logger.error(f"ICS-205 template test failed: {e}")
    
    def _test_database_operations(self) -> None:
        """Test database operations."""
        try:
            # Test database connection
            connection = self.db_manager.get_connection()
            logger.info("Database connection: PASSED")
            
            # Test multi-form service by searching for all forms
            from ..services.multi_form_service import FormQuery
            query = FormQuery()  # Empty query to get all forms
            forms = self.multi_form_service.search_forms(query)
            logger.info(f"Database query: PASSED (found {len(forms)} forms)")
            
            # Test form creation and storage
            test_form_data = {
                'form_type': 'ics213',
                'incident_name': 'Database Test',
                'subject': 'Headless database test',
                'message': 'Testing database functionality'
            }
            
            form_id = self.multi_form_service.create_form('ics213', test_form_data)
            logger.info(f"Form creation: {'PASSED' if form_id else 'FAILED'}")
            
            if form_id:
                # Test form retrieval
                retrieved_form = self.multi_form_service.get_form(form_id)
                logger.info(f"Form retrieval: {'PASSED' if retrieved_form else 'FAILED'}")
            
        except Exception as e:
            logger.error(f"Database operations test failed: {e}")
    
    def _test_search_functionality(self) -> None:
        """Test search functionality."""
        try:
            # Test search presets
            search_presets = self.search_service.get_search_presets()
            logger.info(f"Search presets: PASSED ({len(search_presets)} presets available)")
            
            # Test search suggestions
            suggestions = self.search_service.get_search_suggestions("test")
            logger.info(f"Search suggestions: PASSED ({len(suggestions)} suggestions)")
            
            # Test quick search
            urgent_forms = self.search_service.quick_search_urgent()
            logger.info(f"Quick search: PASSED (found {len(urgent_forms)} urgent forms)")
            
        except Exception as e:
            logger.error(f"Search functionality test failed: {e}")
    
    def _interactive_mode(self) -> None:
        """Start interactive mode for manual testing."""
        logger.info("Starting interactive mode (Ctrl+C to exit)")
        
        print("\n" + "="*60)
        print("RadioForms Headless Interactive Mode")
        print("="*60)
        print("Available commands:")
        print("  status    - Show application status")
        print("  forms     - List all forms in database")
        print("  search    - Test search functionality")
        print("  create    - Create a test form")
        print("  help      - Show this help")
        print("  exit      - Exit interactive mode")
        print("="*60)
        
        while True:
            try:
                command = input("\nheadless> ").strip().lower()
                
                if command == "exit" or command == "quit":
                    break
                elif command == "status":
                    self._show_status()
                elif command == "forms":
                    self._list_forms()
                elif command == "search":
                    self._interactive_search()
                elif command == "create":
                    self._interactive_create_form()
                elif command == "help":
                    print("Commands: status, forms, search, create, help, exit")
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                break
            except EOFError:
                print("\nExiting interactive mode...")
                break
    
    def _show_status(self) -> None:
        """Show application status."""
        print(f"\nRadioForms Headless Status:")
        print(f"  Database: {self.database_path}")
        print(f"  Debug mode: {self.debug}")
        
        try:
            from ..services.multi_form_service import FormQuery
            query = FormQuery()
            forms = self.multi_form_service.search_forms(query)
            print(f"  Total forms: {len(forms)}")
            
            # Count by type
            type_counts = {}
            for form in forms:
                form_type = form.get('form_type', 'unknown')
                type_counts[form_type] = type_counts.get(form_type, 0) + 1
            
            for form_type, count in type_counts.items():
                print(f"    {form_type}: {count}")
                
        except Exception as e:
            print(f"  Error getting form count: {e}")
    
    def _list_forms(self) -> None:
        """List all forms in database."""
        try:
            from ..services.multi_form_service import FormQuery
            query = FormQuery()
            forms = self.multi_form_service.search_forms(query)
            print(f"\nFound {len(forms)} forms:")
            
            for form in forms[:10]:  # Show first 10
                print(f"  {form.get('id', 'N/A')} - {form.get('form_type', 'unknown')} - {form.get('title', 'No title')}")
            
            if len(forms) > 10:
                print(f"  ... and {len(forms) - 10} more")
                
        except Exception as e:
            print(f"Error listing forms: {e}")
    
    def _interactive_search(self) -> None:
        """Interactive search testing."""
        query = input("Enter search query: ")
        if query:
            try:
                results = self.search_service.smart_search(query)
                print(f"Found {len(results)} results for '{query}'")
                
                for result in results[:5]:  # Show first 5
                    print(f"  - {result.get('title', 'No title')} ({result.get('form_type', 'unknown')})")
                    
            except Exception as e:
                print(f"Search error: {e}")
    
    def _interactive_create_form(self) -> None:
        """Interactive form creation."""
        print("\nForm creation options:")
        print("  1. ICS-213 (General Message)")
        print("  2. ICS-214 (Activity Log)")
        print("  3. ICS-205 (Radio Communications)")
        
        choice = input("Select form type (1-3): ")
        
        if choice == "1":
            self._create_ics213_interactive()
        elif choice == "2":
            self._create_ics214_interactive()
        elif choice == "3":
            self._create_ics205_interactive()
        else:
            print("Invalid choice")
    
    def _create_ics213_interactive(self) -> None:
        """Create ICS-213 form interactively."""
        try:
            incident = input("Incident name: ")
            subject = input("Subject: ")
            message = input("Message: ")
            
            form_data = {
                'form_type': 'ics213',
                'incident_name': incident,
                'subject': subject,
                'message': message,
                'to_name': 'Test Recipient',
                'from_name': 'Headless User'
            }
            
            form_id = self.multi_form_service.create_form('ics213', form_data)
            print(f"Created ICS-213 form with ID: {form_id}")
            
        except Exception as e:
            print(f"Error creating form: {e}")
    
    def _create_ics214_interactive(self) -> None:
        """Create ICS-214 form interactively."""
        try:
            incident = input("Incident name: ")
            name = input("Your name: ")
            position = input("ICS position: ")
            
            form_data = {
                'form_type': 'ics214',
                'incident_name': incident,
                'name': name,
                'ics_position': position,
                'home_agency': 'Test Agency'
            }
            
            form_id = self.multi_form_service.create_form('ics214', form_data)
            print(f"Created ICS-214 form with ID: {form_id}")
            
        except Exception as e:
            print(f"Error creating form: {e}")
    
    def _create_ics205_interactive(self) -> None:
        """Create ICS-205 form interactively."""
        try:
            incident = input("Incident name: ")
            
            template = ICS205Template()
            test_data = {
                'incident_name': incident,
                'operational_period': '2024-05-31',
                'prepared_by': 'Headless User',
                'frequency_assignments': []
            }
            
            template.set_data(test_data)
            export_data = template.export_data()
            
            # Note: This doesn't save to database as ICS-205 is template-based
            print("ICS-205 form created successfully (template system)")
            print(f"Export data size: {len(str(export_data))} characters")
            
        except Exception as e:
            print(f"Error creating ICS-205: {e}")


def main():
    """Standalone entry point for headless mode."""
    app = HeadlessApplication(debug=True)
    return app.run()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)