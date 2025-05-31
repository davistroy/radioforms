"""Comprehensive test suite for Dashboard and Analytics System.

Tests all dashboard components including widget integration, data flow,
reporting capabilities, and user interaction workflows.

Following CLAUDE.md principles:
- Comprehensive test coverage for all dashboard components
- Performance validation for real-time updates
- Integration testing with existing form system
- User workflow validation

Run with: python test_dashboard_system.py
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ui.dashboard import (
        DashboardWidget, IncidentOverview, FormCompletionTracker,
        TimelineWidget, ResourceSummary, DashboardReports
    )
    from src.ui.dashboard.dashboard_widget import DashboardMetrics, DashboardUpdatePriority
    from src.ui.dashboard.incident_overview import IncidentData, IncidentStatus
    from src.ui.dashboard.form_completion_tracker import FormCompletionData, CompletionStatus
    from src.ui.dashboard.timeline_widget import TimelineEvent, EventType
    from src.ui.dashboard.resource_summary import ResourceData, ResourceType
    from src.ui.dashboard.dashboard_reports import ReportData, ReportType
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    DASHBOARD_AVAILABLE = False
    print(f"Dashboard system not available for testing: {e}")


class TestDashboardMetrics(unittest.TestCase):
    """Test dashboard metrics and data structures."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_dashboard_metrics_initialization(self):
        """Test DashboardMetrics initialization."""
        metrics = DashboardMetrics()
        
        self.assertEqual(metrics.incident_name, "")
        self.assertEqual(metrics.total_forms, 0)
        self.assertEqual(metrics.completion_rate, 0.0)
        self.assertIsInstance(metrics.forms_by_type, dict)
        self.assertIsInstance(metrics.timeline_events, list)
        self.assertIsInstance(metrics.last_updated, datetime)
    
    def test_dashboard_metrics_with_data(self):
        """Test DashboardMetrics with populated data."""
        metrics = DashboardMetrics(
            incident_name="Test Incident",
            total_forms=25,
            completion_rate=85.5,
            forms_by_type={"ICS-213": 10, "ICS-214": 15},
            recent_activity=5,
            critical_updates=2
        )
        
        self.assertEqual(metrics.incident_name, "Test Incident")
        self.assertEqual(metrics.total_forms, 25)
        self.assertEqual(metrics.completion_rate, 85.5)
        self.assertEqual(metrics.forms_by_type["ICS-213"], 10)
        self.assertEqual(metrics.recent_activity, 5)
        self.assertEqual(metrics.critical_updates, 2)


class TestIncidentOverview(unittest.TestCase):
    """Test incident overview component."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_incident_data_initialization(self):
        """Test IncidentData initialization."""
        data = IncidentData()
        
        self.assertEqual(data.name, "")
        self.assertEqual(data.status, IncidentStatus.ACTIVE)
        self.assertEqual(data.total_personnel, 0)
        self.assertEqual(data.total_resources, 0)
        self.assertIsInstance(data.start_time, datetime)
        self.assertIsInstance(data.safety_concerns, list)
    
    def test_incident_data_with_values(self):
        """Test IncidentData with specific values."""
        start_time = datetime.now() - timedelta(hours=5)
        safety_concerns = ["High winds", "Steep terrain"]
        
        data = IncidentData(
            name="Mountain Wildfire",
            status=IncidentStatus.CONTAINED,
            start_time=start_time,
            location="North Ridge",
            incident_commander="Chief Johnson",
            total_personnel=45,
            total_resources=20,
            priority_level="High",
            weather_conditions="Clear, 15mph winds",
            safety_concerns=safety_concerns
        )
        
        self.assertEqual(data.name, "Mountain Wildfire")
        self.assertEqual(data.status, IncidentStatus.CONTAINED)
        self.assertEqual(data.start_time, start_time)
        self.assertEqual(data.location, "North Ridge")
        self.assertEqual(data.incident_commander, "Chief Johnson")
        self.assertEqual(data.total_personnel, 45)
        self.assertEqual(data.total_resources, 20)
        self.assertEqual(data.priority_level, "High")
        self.assertEqual(data.weather_conditions, "Clear, 15mph winds")
        self.assertEqual(len(data.safety_concerns), 2)
    
    def test_incident_status_enum(self):
        """Test IncidentStatus enumeration."""
        self.assertEqual(IncidentStatus.ACTIVE.value, "active")
        self.assertEqual(IncidentStatus.MONITORING.value, "monitoring")
        self.assertEqual(IncidentStatus.CONTAINED.value, "contained")
        self.assertEqual(IncidentStatus.CONTROLLED.value, "controlled")
        self.assertEqual(IncidentStatus.CLOSED.value, "closed")


class TestFormCompletionTracker(unittest.TestCase):
    """Test form completion tracking component."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_form_completion_data_initialization(self):
        """Test FormCompletionData initialization."""
        data = FormCompletionData(form_type="ICS-213")
        
        self.assertEqual(data.form_type, "ICS-213")
        self.assertEqual(data.required_count, 1)
        self.assertEqual(data.completed_count, 0)
        self.assertEqual(data.in_progress_count, 0)
        self.assertEqual(data.overdue_count, 0)
        self.assertEqual(data.completion_rate, 0.0)
        self.assertEqual(data.status, CompletionStatus.NOT_STARTED)
        self.assertIsInstance(data.last_update, datetime)
    
    def test_completion_rate_calculation(self):
        """Test completion rate calculation."""
        data = FormCompletionData(
            form_type="ICS-214",
            required_count=10,
            completed_count=7
        )
        
        self.assertEqual(data.completion_rate, 70.0)
        self.assertEqual(data.status, CompletionStatus.IN_PROGRESS)
    
    def test_completion_status_determination(self):
        """Test status determination logic."""
        # Not started
        data1 = FormCompletionData(form_type="Test", required_count=5)
        self.assertEqual(data1.status, CompletionStatus.NOT_STARTED)
        
        # In progress
        data2 = FormCompletionData(
            form_type="Test", 
            required_count=5, 
            completed_count=2
        )
        self.assertEqual(data2.status, CompletionStatus.IN_PROGRESS)
        
        # Completed/Validated
        data3 = FormCompletionData(
            form_type="Test", 
            required_count=5, 
            completed_count=5
        )
        self.assertEqual(data3.status, CompletionStatus.VALIDATED)
        
        # Overdue
        data4 = FormCompletionData(
            form_type="Test", 
            required_count=5, 
            completed_count=2,
            overdue_count=1
        )
        self.assertEqual(data4.status, CompletionStatus.OVERDUE)


class TestTimelineWidget(unittest.TestCase):
    """Test timeline visualization component."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_timeline_event_initialization(self):
        """Test TimelineEvent initialization."""
        timestamp = datetime.now()
        event = TimelineEvent(
            timestamp=timestamp,
            event_type=EventType.FORM_CREATED,
            title="Form Created",
            description="New ICS-213 form created"
        )
        
        self.assertEqual(event.timestamp, timestamp)
        self.assertEqual(event.event_type, EventType.FORM_CREATED)
        self.assertEqual(event.title, "Form Created")
        self.assertEqual(event.description, "New ICS-213 form created")
        self.assertEqual(event.form_id, "")
        self.assertEqual(event.form_type, "")
        self.assertIsInstance(event.metadata, dict)
    
    def test_event_type_enum(self):
        """Test EventType enumeration."""
        self.assertEqual(EventType.FORM_CREATED.value, "form_created")
        self.assertEqual(EventType.FORM_SUBMITTED.value, "form_submitted")
        self.assertEqual(EventType.FORM_UPDATED.value, "form_updated")
        self.assertEqual(EventType.RESOURCE_ASSIGNED.value, "resource_assigned")
        self.assertEqual(EventType.STATUS_CHANGE.value, "status_change")
        self.assertEqual(EventType.COMMUNICATION.value, "communication")
        self.assertEqual(EventType.SAFETY_ALERT.value, "safety_alert")
        self.assertEqual(EventType.MILESTONE.value, "milestone")


class TestResourceSummary(unittest.TestCase):
    """Test resource summary component."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_resource_data_initialization(self):
        """Test ResourceData initialization."""
        data = ResourceData(
            resource_type=ResourceType.PERSONNEL,
            name="Fire Crew Alpha"
        )
        
        self.assertEqual(data.resource_type, ResourceType.PERSONNEL)
        self.assertEqual(data.name, "Fire Crew Alpha")
        self.assertEqual(data.quantity, 1)
        self.assertEqual(data.available, 1)
        self.assertEqual(data.assigned, 0)
        self.assertEqual(data.status, "Available")
        self.assertIsInstance(data.last_updated, datetime)
    
    def test_utilization_rate_calculation(self):
        """Test utilization rate calculation."""
        data = ResourceData(
            resource_type=ResourceType.EQUIPMENT,
            name="Engine 42",
            quantity=10,
            assigned=6
        )
        
        self.assertEqual(data.utilization_rate, 60.0)
    
    def test_resource_type_enum(self):
        """Test ResourceType enumeration."""
        self.assertEqual(ResourceType.PERSONNEL.value, "personnel")
        self.assertEqual(ResourceType.EQUIPMENT.value, "equipment")
        self.assertEqual(ResourceType.VEHICLES.value, "vehicles")
        self.assertEqual(ResourceType.AIRCRAFT.value, "aircraft")
        self.assertEqual(ResourceType.FACILITIES.value, "facilities")
        self.assertEqual(ResourceType.COMMUNICATIONS.value, "communications")


class TestDashboardReports(unittest.TestCase):
    """Test dashboard reports component."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_report_data_initialization(self):
        """Test ReportData initialization."""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        test_data = {"metrics": {"total_forms": 25}}
        
        report = ReportData(
            report_type=ReportType.INCIDENT_SUMMARY,
            incident_name="Test Incident",
            start_date=start_date,
            end_date=end_date,
            data=test_data
        )
        
        self.assertEqual(report.report_type, ReportType.INCIDENT_SUMMARY)
        self.assertEqual(report.incident_name, "Test Incident")
        self.assertEqual(report.start_date, start_date)
        self.assertEqual(report.end_date, end_date)
        self.assertEqual(report.data, test_data)
        self.assertIsInstance(report.generated_at, datetime)
    
    def test_report_type_enum(self):
        """Test ReportType enumeration."""
        self.assertEqual(ReportType.INCIDENT_SUMMARY.value, "incident_summary")
        self.assertEqual(ReportType.FORM_COMPLETION.value, "form_completion")
        self.assertEqual(ReportType.RESOURCE_ALLOCATION.value, "resource_allocation")
        self.assertEqual(ReportType.TIMELINE_EXPORT.value, "timeline_export")
        self.assertEqual(ReportType.ANALYTICS_REPORT.value, "analytics_report")
        self.assertEqual(ReportType.COMPREHENSIVE.value, "comprehensive")


class TestDashboardIntegration(unittest.TestCase):
    """Test dashboard component integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
        
        # Mock form service
        self.mock_form_service = Mock()
        self.mock_form_service.search_forms.return_value = []
    
    def test_dashboard_widget_creation(self):
        """Test dashboard widget creation without PySide6."""
        # This tests the fallback behavior when PySide6 is not available
        with patch('src.ui.dashboard.dashboard_widget.HAS_PYSIDE6', False):
            widget = DashboardWidget(self.mock_form_service)
            # Should not crash, just return gracefully
            self.assertIsNotNone(widget)
    
    def test_incident_overview_creation(self):
        """Test incident overview creation without PySide6."""
        with patch('src.ui.dashboard.incident_overview.HAS_PYSIDE6', False):
            overview = IncidentOverview()
            self.assertIsNotNone(overview)
    
    def test_form_completion_tracker_creation(self):
        """Test form completion tracker creation without PySide6."""
        with patch('src.ui.dashboard.form_completion_tracker.HAS_PYSIDE6', False):
            tracker = FormCompletionTracker()
            self.assertIsNotNone(tracker)
    
    def test_timeline_widget_creation(self):
        """Test timeline widget creation without PySide6."""
        with patch('src.ui.dashboard.timeline_widget.HAS_PYSIDE6', False):
            timeline = TimelineWidget()
            self.assertIsNotNone(timeline)
    
    def test_resource_summary_creation(self):
        """Test resource summary creation without PySide6."""
        with patch('src.ui.dashboard.resource_summary.HAS_PYSIDE6', False):
            summary = ResourceSummary()
            self.assertIsNotNone(summary)
    
    def test_dashboard_reports_creation(self):
        """Test dashboard reports creation without PySide6."""
        with patch('src.ui.dashboard.dashboard_reports.HAS_PYSIDE6', False):
            reports = DashboardReports()
            self.assertIsNotNone(reports)


class TestDashboardDataFlow(unittest.TestCase):
    """Test data flow between dashboard components."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_form_completion_data_flow(self):
        """Test form completion data processing."""
        # Mock form data
        forms_data = [
            {
                'form_type': 'ICS-213',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            },
            {
                'form_type': 'ICS-213', 
                'status': 'draft',
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                'form_type': 'ICS-214',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # Create tracker and set required forms
        with patch('src.ui.dashboard.form_completion_tracker.HAS_PYSIDE6', False):
            tracker = FormCompletionTracker()
            tracker.set_required_forms(['ICS-213', 'ICS-214'])
            tracker.update_completion_status(forms_data)
            
            # Verify completion data
            self.assertIn('ICS-213', tracker.completion_data)
            self.assertIn('ICS-214', tracker.completion_data)
            
            ics213_data = tracker.completion_data['ICS-213']
            self.assertEqual(ics213_data.completed_count, 1)
            self.assertEqual(ics213_data.in_progress_count, 1)
            
            ics214_data = tracker.completion_data['ICS-214']
            self.assertEqual(ics214_data.completed_count, 1)
            self.assertEqual(ics214_data.in_progress_count, 0)
    
    def test_timeline_data_flow(self):
        """Test timeline data processing."""
        # Mock form data
        forms_data = [
            {
                'id': '1',
                'form_type': 'ICS-213',
                'created_at': datetime.now().isoformat(),
                'updated_at': None
            },
            {
                'id': '2',
                'form_type': 'ICS-214',
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'updated_at': (datetime.now() - timedelta(hours=1)).isoformat()
            }
        ]
        
        with patch('src.ui.dashboard.timeline_widget.HAS_PYSIDE6', False):
            timeline = TimelineWidget()
            timeline.update_from_forms_data(forms_data)
            
            # Verify events were created
            self.assertGreater(len(timeline.events), 0)
            
            # Check for created events
            created_events = [e for e in timeline.events if e.event_type == EventType.FORM_CREATED]
            self.assertEqual(len(created_events), 2)
            
            # Check for updated events
            updated_events = [e for e in timeline.events if e.event_type == EventType.FORM_UPDATED]
            self.assertEqual(len(updated_events), 1)


class TestDashboardPerformance(unittest.TestCase):
    """Test dashboard performance with realistic data loads."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard system not available")
    
    def test_large_form_dataset_performance(self):
        """Test dashboard performance with large form dataset."""
        # Generate large form dataset
        forms_data = []
        for i in range(1000):
            forms_data.append({
                'id': str(i),
                'form_type': f'ICS-{213 + (i % 3)}',
                'status': 'completed' if i % 3 == 0 else 'draft',
                'created_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                'updated_at': None if i % 2 == 0 else (datetime.now() - timedelta(hours=i-1)).isoformat()
            })
        
        with patch('src.ui.dashboard.form_completion_tracker.HAS_PYSIDE6', False):
            tracker = FormCompletionTracker()
            
            # Measure performance
            start_time = datetime.now()
            tracker.set_required_forms(['ICS-213', 'ICS-214', 'ICS-215'])
            tracker.update_completion_status(forms_data)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            # Should process 1000 forms in under 1 second
            self.assertLess(processing_time, 1.0)
            
            # Verify data integrity
            self.assertEqual(len(tracker.completion_data), 3)
    
    def test_timeline_performance_with_large_dataset(self):
        """Test timeline performance with large event dataset."""
        with patch('src.ui.dashboard.timeline_widget.HAS_PYSIDE6', False):
            timeline = TimelineWidget()
            
            # Add many events
            start_time = datetime.now()
            for i in range(500):
                timeline.add_event(
                    title=f"Event {i}",
                    description=f"Test event {i}",
                    event_type=EventType.FORM_CREATED,
                    timestamp=datetime.now() - timedelta(minutes=i)
                )
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            # Should add 500 events in under 0.5 seconds
            self.assertLess(processing_time, 0.5)
            
            # Verify data
            self.assertEqual(len(timeline.events), 500)


def run_dashboard_tests():
    """Run all dashboard system tests."""
    if not DASHBOARD_AVAILABLE:
        print("Dashboard system not available - skipping tests")
        return
    
    # Create test suite
    test_classes = [
        TestDashboardMetrics,
        TestIncidentOverview,
        TestFormCompletionTracker,
        TestTimelineWidget,
        TestResourceSummary,
        TestDashboardReports,
        TestDashboardIntegration,
        TestDashboardDataFlow,
        TestDashboardPerformance
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
    print(f"\nDashboard System Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_dashboard_tests()
    print(f"\nDashboard System Tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)