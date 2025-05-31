"""Dashboard and Analytics Components.

This package provides incident management dashboard components for
visualizing form completion status, incident timelines, and resource
summaries. Designed for emergency management operational overview.

Components:
    dashboard_widget: Main dashboard interface
    incident_overview: Incident summary and status
    form_completion_tracker: Form completion visualization
    timeline_widget: Incident activity timeline
    resource_summary: Resource allocation overview
    dashboard_reports: Exportable dashboard reports

Following CLAUDE.md principles:
- Simple, clear visualizations
- Performance optimized for large incidents
- Intuitive emergency management workflow
- Comprehensive testing and validation
"""

__all__ = [
    'DashboardWidget',
    'IncidentOverview',
    'FormCompletionTracker',
    'TimelineWidget',
    'ResourceSummary',
    'DashboardReports'
]

# Import main components
try:
    from .dashboard_widget import DashboardWidget
    from .incident_overview import IncidentOverview
    from .form_completion_tracker import FormCompletionTracker
    from .timeline_widget import TimelineWidget
    from .resource_summary import ResourceSummary
    from .dashboard_reports import DashboardReports
except ImportError:
    # Graceful fallback for testing or missing dependencies
    pass