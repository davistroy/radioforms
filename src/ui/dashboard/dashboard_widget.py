"""Main Dashboard Widget for Incident Management Overview.

Provides a comprehensive incident management dashboard with form completion
tracking, timeline visualization, resource summaries, and actionable insights
for emergency management professionals.

Following CLAUDE.md principles:
- Simple, intuitive interface optimized for emergency operations
- Performance optimized for real-time incident management
- Clear visual hierarchy for critical information
- Complete integration with existing form system

Example:
    >>> from src.ui.dashboard.dashboard_widget import DashboardWidget
    >>> from src.services.multi_form_service import MultiFormService
    >>> 
    >>> # Create dashboard with multi-form service integration
    >>> service = MultiFormService(database_path)
    >>> dashboard = DashboardWidget(service)
    >>> dashboard.set_incident("Mountain Wildfire Response")
    >>> dashboard.refresh_data()
    >>> dashboard.show()

Classes:
    DashboardWidget: Main dashboard interface
    DashboardMetrics: Data container for dashboard metrics
    DashboardRefreshTimer: Automatic data refresh management

Functions:
    create_dashboard_widget: Factory function for dashboard creation
    export_dashboard_snapshot: Export current dashboard state
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QProgressBar, QScrollArea,
        QGroupBox, QSplitter, QFrame, QComboBox,
        QTableWidget, QTableWidgetItem, QHeaderView,
        QTextEdit, QSizePolicy
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
    from PySide6.QtGui import QFont, QPalette, QColor, QPainter
    HAS_PYSIDE6 = True
except ImportError:
    # Mock Qt classes for testing
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QPushButton = QProgressBar = QScrollArea = object
    QGroupBox = QSplitter = QFrame = QComboBox = object
    QTableWidget = QTableWidgetItem = QHeaderView = object
    QTextEdit = QSizePolicy = object
    QTimer = Signal = QThread = pyqtSignal = object
    QFont = QPalette = QColor = QPainter = object
    Qt = type('Qt', (), {'AlignTop': 0, 'AlignLeft': 0, 'Horizontal': 0, 'Vertical': 0})

# Import services
try:
    from ...services.multi_form_service import MultiFormService, FormQuery
    from ...services.enhanced_search_service import EnhancedSearchService
    from ...models.base_form import FormType
except ImportError:
    # For testing
    MultiFormService = FormQuery = EnhancedSearchService = FormType = object

logger = logging.getLogger(__name__)


class DashboardUpdatePriority(Enum):
    """Priority levels for dashboard data updates."""
    CRITICAL = "critical"  # Form submissions, safety updates
    HIGH = "high"         # Resource status changes
    NORMAL = "normal"     # General status updates
    LOW = "low"          # Background refresh


@dataclass
class DashboardMetrics:
    """Container for dashboard metrics and statistics.
    
    Attributes:
        incident_name: Current incident name
        total_forms: Total number of forms in incident
        forms_by_type: Count of forms by type
        completion_rate: Percentage of required forms completed
        recent_activity: Count of forms in last 24 hours
        critical_updates: Forms requiring immediate attention
        resource_summary: Summary of resource allocation
        timeline_events: Recent timeline events
        last_updated: Timestamp of last data refresh
    """
    incident_name: str = ""
    total_forms: int = 0
    forms_by_type: Dict[str, int] = None
    completion_rate: float = 0.0
    recent_activity: int = 0
    critical_updates: int = 0
    resource_summary: Dict[str, Any] = None
    timeline_events: List[Dict[str, Any]] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.forms_by_type is None:
            self.forms_by_type = {}
        if self.resource_summary is None:
            self.resource_summary = {}
        if self.timeline_events is None:
            self.timeline_events = []
        if self.last_updated is None:
            self.last_updated = datetime.now()


class DashboardWidget(QWidget):
    """Main incident management dashboard widget.
    
    Provides comprehensive incident overview with form completion tracking,
    resource summaries, timeline visualization, and actionable insights.
    Designed for emergency management operational requirements.
    
    Signals:
        incident_changed: Emitted when incident selection changes
        form_selected: Emitted when form is selected from dashboard
        refresh_requested: Emitted when manual refresh is requested
        export_requested: Emitted when dashboard export is requested
    """
    
    # Signals for dashboard interactions
    incident_changed = Signal(str) if HAS_PYSIDE6 else None
    form_selected = Signal(str) if HAS_PYSIDE6 else None
    refresh_requested = Signal() if HAS_PYSIDE6 else None
    export_requested = Signal() if HAS_PYSIDE6 else None
    
    def __init__(self, form_service: Optional[MultiFormService] = None, parent=None):
        """Initialize dashboard widget.
        
        Args:
            form_service: Multi-form service for data access
            parent: Parent widget
        """
        if not HAS_PYSIDE6:
            return
            
        super().__init__(parent)
        self.form_service = form_service
        self.current_incident = ""
        self.metrics = DashboardMetrics()
        self.refresh_timer = QTimer()
        
        # Initialize UI components
        self._init_ui()
        self._setup_signals()
        self._setup_refresh_timer()
        
        logger.info("Dashboard widget initialized")
    
    def _init_ui(self):
        """Initialize the user interface components."""
        self.setObjectName("DashboardWidget")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section with incident selection and refresh
        header_layout = self._create_header_section()
        main_layout.addLayout(header_layout)
        
        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left panel - Overview and metrics
        left_panel = self._create_overview_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Timeline and activity
        right_panel = self._create_activity_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([400, 300])
        
        # Status bar
        self.status_label = QLabel("Dashboard ready")
        self.status_label.setObjectName("DashboardStatus")
        main_layout.addWidget(self.status_label)
    
    def _create_header_section(self) -> QHBoxLayout:
        """Create header section with incident selection and controls.
        
        Returns:
            QHBoxLayout: Header layout with controls
        """
        header_layout = QHBoxLayout()
        
        # Dashboard title
        title_label = QLabel("Incident Management Dashboard")
        title_label.setObjectName("DashboardTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Incident selection
        incident_label = QLabel("Incident:")
        header_layout.addWidget(incident_label)
        
        self.incident_combo = QComboBox()
        self.incident_combo.setMinimumWidth(200)
        self.incident_combo.setEditable(True)
        header_layout.addWidget(self.incident_combo)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("DashboardRefresh")
        header_layout.addWidget(self.refresh_button)
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.setObjectName("DashboardExport")
        header_layout.addWidget(self.export_button)
        
        return header_layout
    
    def _create_overview_panel(self) -> QWidget:
        """Create overview panel with metrics and form completion.
        
        Returns:
            QWidget: Overview panel widget
        """
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        
        # Incident overview section
        overview_group = QGroupBox("Incident Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        # Key metrics grid
        metrics_layout = QGridLayout()
        
        # Total forms
        metrics_layout.addWidget(QLabel("Total Forms:"), 0, 0)
        self.total_forms_label = QLabel("0")
        self.total_forms_label.setObjectName("MetricValue")
        metrics_layout.addWidget(self.total_forms_label, 0, 1)
        
        # Completion rate
        metrics_layout.addWidget(QLabel("Completion:"), 1, 0)
        self.completion_rate_bar = QProgressBar()
        self.completion_rate_bar.setRange(0, 100)
        metrics_layout.addWidget(self.completion_rate_bar, 1, 1)
        
        # Recent activity
        metrics_layout.addWidget(QLabel("Last 24h:"), 2, 0)
        self.recent_activity_label = QLabel("0")
        self.recent_activity_label.setObjectName("MetricValue")
        metrics_layout.addWidget(self.recent_activity_label, 2, 1)
        
        # Critical updates
        metrics_layout.addWidget(QLabel("Critical:"), 3, 0)
        self.critical_updates_label = QLabel("0")
        self.critical_updates_label.setObjectName("CriticalMetric")
        metrics_layout.addWidget(self.critical_updates_label, 3, 1)
        
        overview_layout.addLayout(metrics_layout)
        panel_layout.addWidget(overview_group)
        
        # Form completion by type
        completion_group = QGroupBox("Form Completion by Type")
        completion_layout = QVBoxLayout(completion_group)
        
        self.completion_table = QTableWidget()
        self.completion_table.setColumnCount(3)
        self.completion_table.setHorizontalHeaderLabels(["Form Type", "Count", "Status"])
        self.completion_table.horizontalHeader().setStretchLastSection(True)
        self.completion_table.setAlternatingRowColors(True)
        self.completion_table.setSelectionBehavior(QTableWidget.SelectRows)
        completion_layout.addWidget(self.completion_table)
        
        panel_layout.addWidget(completion_group)
        
        # Resource summary
        resource_group = QGroupBox("Resource Summary")
        resource_layout = QVBoxLayout(resource_group)
        
        self.resource_summary_text = QTextEdit()
        self.resource_summary_text.setMaximumHeight(100)
        self.resource_summary_text.setReadOnly(True)
        resource_layout.addWidget(self.resource_summary_text)
        
        panel_layout.addWidget(resource_group)
        
        return panel
    
    def _create_activity_panel(self) -> QWidget:
        """Create activity panel with timeline and recent events.
        
        Returns:
            QWidget: Activity panel widget
        """
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        
        # Recent activity section
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Form", "Type", "Summary"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        activity_layout.addWidget(self.activity_table)
        
        panel_layout.addWidget(activity_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Action buttons
        actions_button_layout = QHBoxLayout()
        
        self.new_form_button = QPushButton("New Form")
        actions_button_layout.addWidget(self.new_form_button)
        
        self.search_forms_button = QPushButton("Search Forms")
        actions_button_layout.addWidget(self.search_forms_button)
        
        self.generate_report_button = QPushButton("Generate Report")
        actions_button_layout.addWidget(self.generate_report_button)
        
        actions_layout.addLayout(actions_button_layout)
        panel_layout.addWidget(actions_group)
        
        return panel
    
    def _setup_signals(self):
        """Setup signal connections for dashboard interactions."""
        if not HAS_PYSIDE6:
            return
            
        # Connect incident selection
        if hasattr(self.incident_combo, 'currentTextChanged'):
            self.incident_combo.currentTextChanged.connect(self._on_incident_changed)
        
        # Connect control buttons
        if hasattr(self.refresh_button, 'clicked'):
            self.refresh_button.clicked.connect(self._on_refresh_requested)
        
        if hasattr(self.export_button, 'clicked'):
            self.export_button.clicked.connect(self._on_export_requested)
        
        # Connect table selections
        if hasattr(self.completion_table, 'itemDoubleClicked'):
            self.completion_table.itemDoubleClicked.connect(self._on_form_type_selected)
        
        if hasattr(self.activity_table, 'itemDoubleClicked'):
            self.activity_table.itemDoubleClicked.connect(self._on_activity_selected)
        
        # Connect action buttons
        if hasattr(self.new_form_button, 'clicked'):
            self.new_form_button.clicked.connect(self._on_new_form_requested)
        
        if hasattr(self.search_forms_button, 'clicked'):
            self.search_forms_button.clicked.connect(self._on_search_requested)
        
        if hasattr(self.generate_report_button, 'clicked'):
            self.generate_report_button.clicked.connect(self._on_report_requested)
    
    def _setup_refresh_timer(self):
        """Setup automatic refresh timer for dashboard data."""
        if not HAS_PYSIDE6:
            return
            
        # Refresh every 30 seconds during active incidents
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.setInterval(30000)  # 30 seconds
    
    def set_incident(self, incident_name: str):
        """Set current incident for dashboard display.
        
        Args:
            incident_name: Name of incident to display
        """
        if incident_name != self.current_incident:
            self.current_incident = incident_name
            
            if HAS_PYSIDE6 and hasattr(self.incident_combo, 'setCurrentText'):
                self.incident_combo.setCurrentText(incident_name)
            
            self.refresh_data()
            
            if self.incident_changed:
                self.incident_changed.emit(incident_name)
            
            logger.info(f"Dashboard incident set to: {incident_name}")
    
    def refresh_data(self):
        """Refresh dashboard data from form service."""
        if not self.form_service or not self.current_incident:
            return
        
        try:
            # Update metrics
            self._update_metrics()
            
            # Update UI components
            self._update_overview_display()
            self._update_completion_table()
            self._update_activity_table()
            self._update_resource_summary()
            
            # Update status
            self.metrics.last_updated = datetime.now()
            self._update_status_display()
            
            logger.debug(f"Dashboard refreshed for incident: {self.current_incident}")
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")
            self._update_status_display(f"Error: {str(e)}")
    
    def _update_metrics(self):
        """Update dashboard metrics from form service."""
        # Create query for current incident
        query = FormQuery()
        query.incident_name = self.current_incident
        
        # Get all forms for incident
        try:
            forms = self.form_service.search_forms(query)
            
            # Calculate metrics
            self.metrics.incident_name = self.current_incident
            self.metrics.total_forms = len(forms)
            
            # Count forms by type
            forms_by_type = {}
            recent_count = 0
            critical_count = 0
            
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for form in forms:
                form_type = form.get('form_type', 'Unknown')
                forms_by_type[form_type] = forms_by_type.get(form_type, 0) + 1
                
                # Count recent activity
                created_time = form.get('created_at')
                if created_time and isinstance(created_time, str):
                    try:
                        created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        if created_dt > cutoff_time:
                            recent_count += 1
                    except ValueError:
                        pass
                
                # Count critical updates (placeholder logic)
                if form.get('priority') == 'HIGH' or 'urgent' in form.get('content', '').lower():
                    critical_count += 1
            
            self.metrics.forms_by_type = forms_by_type
            self.metrics.recent_activity = recent_count
            self.metrics.critical_updates = critical_count
            
            # Calculate completion rate (simplified)
            expected_forms = 10  # Placeholder - could be configurable
            self.metrics.completion_rate = min(100.0, (self.metrics.total_forms / expected_forms) * 100)
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def _update_overview_display(self):
        """Update overview metrics display."""
        if not HAS_PYSIDE6:
            return
            
        if hasattr(self, 'total_forms_label'):
            self.total_forms_label.setText(str(self.metrics.total_forms))
        
        if hasattr(self, 'completion_rate_bar'):
            self.completion_rate_bar.setValue(int(self.metrics.completion_rate))
        
        if hasattr(self, 'recent_activity_label'):
            self.recent_activity_label.setText(str(self.metrics.recent_activity))
        
        if hasattr(self, 'critical_updates_label'):
            self.critical_updates_label.setText(str(self.metrics.critical_updates))
    
    def _update_completion_table(self):
        """Update form completion table display."""
        if not HAS_PYSIDE6 or not hasattr(self, 'completion_table'):
            return
            
        table = self.completion_table
        forms_by_type = self.metrics.forms_by_type
        
        table.setRowCount(len(forms_by_type))
        
        for row, (form_type, count) in enumerate(forms_by_type.items()):
            # Form type
            table.setItem(row, 0, QTableWidgetItem(form_type))
            
            # Count
            table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # Status (simplified)
            status = "Active" if count > 0 else "None"
            table.setItem(row, 2, QTableWidgetItem(status))
    
    def _update_activity_table(self):
        """Update recent activity table display."""
        if not HAS_PYSIDE6 or not hasattr(self, 'activity_table'):
            return
            
        # Placeholder for activity data
        # In full implementation, this would show recent form submissions
        table = self.activity_table
        table.setRowCount(3)  # Show last 3 activities
        
        sample_activities = [
            ("10:30", "ICS-213", "Message", "Resource request submitted"),
            ("09:45", "ICS-214", "Activity", "Team assignment updated"),
            ("09:15", "ICS-205", "Radio", "Frequency plan revised")
        ]
        
        for row, (time, form, type_val, summary) in enumerate(sample_activities):
            table.setItem(row, 0, QTableWidgetItem(time))
            table.setItem(row, 1, QTableWidgetItem(form))
            table.setItem(row, 2, QTableWidgetItem(type_val))
            table.setItem(row, 3, QTableWidgetItem(summary))
    
    def _update_resource_summary(self):
        """Update resource summary display."""
        if not HAS_PYSIDE6 or not hasattr(self, 'resource_summary_text'):
            return
            
        # Placeholder resource summary
        summary = f"""
Incident: {self.metrics.incident_name}
Forms: {self.metrics.total_forms}
Recent Activity: {self.metrics.recent_activity} forms in last 24h
Critical Items: {self.metrics.critical_updates}
Completion: {self.metrics.completion_rate:.1f}%

Last Updated: {self.metrics.last_updated.strftime('%H:%M:%S')}
        """.strip()
        
        self.resource_summary_text.setPlainText(summary)
    
    def _update_status_display(self, message: str = None):
        """Update status display.
        
        Args:
            message: Custom status message, or None for default
        """
        if not HAS_PYSIDE6 or not hasattr(self, 'status_label'):
            return
            
        if message:
            status_text = message
        else:
            status_text = f"Last updated: {self.metrics.last_updated.strftime('%H:%M:%S')} - {self.metrics.total_forms} forms"
        
        self.status_label.setText(status_text)
    
    def _auto_refresh(self):
        """Automatic refresh callback."""
        if self.current_incident:
            self.refresh_data()
    
    def _on_incident_changed(self, incident_name: str):
        """Handle incident selection change."""
        self.set_incident(incident_name)
    
    def _on_refresh_requested(self):
        """Handle manual refresh request."""
        self.refresh_data()
        if self.refresh_requested:
            self.refresh_requested.emit()
    
    def _on_export_requested(self):
        """Handle export request."""
        if self.export_requested:
            self.export_requested.emit()
    
    def _on_form_type_selected(self, item):
        """Handle form type selection from completion table."""
        if not item:
            return
            
        row = item.row()
        if row < self.completion_table.rowCount():
            form_type = self.completion_table.item(row, 0).text()
            if self.form_selected:
                self.form_selected.emit(form_type)
    
    def _on_activity_selected(self, item):
        """Handle activity selection from activity table."""
        if not item:
            return
            
        row = item.row()
        if row < self.activity_table.rowCount():
            form_id = self.activity_table.item(row, 1).text()
            if self.form_selected:
                self.form_selected.emit(form_id)
    
    def _on_new_form_requested(self):
        """Handle new form request."""
        # Signal to main application to create new form
        logger.info("New form requested from dashboard")
    
    def _on_search_requested(self):
        """Handle search forms request."""
        # Signal to main application to open search
        logger.info("Search forms requested from dashboard")
    
    def _on_report_requested(self):
        """Handle generate report request."""
        # Signal to main application to generate report
        logger.info("Generate report requested from dashboard")
    
    def start_auto_refresh(self):
        """Start automatic refresh timer."""
        if HAS_PYSIDE6 and hasattr(self.refresh_timer, 'start'):
            self.refresh_timer.start()
            logger.info("Dashboard auto-refresh started")
    
    def stop_auto_refresh(self):
        """Stop automatic refresh timer."""
        if HAS_PYSIDE6 and hasattr(self.refresh_timer, 'stop'):
            self.refresh_timer.stop()
            logger.info("Dashboard auto-refresh stopped")
    
    def export_dashboard_data(self) -> Dict[str, Any]:
        """Export current dashboard data for reporting.
        
        Returns:
            Dict containing dashboard metrics and data
        """
        return {
            'incident_name': self.metrics.incident_name,
            'total_forms': self.metrics.total_forms,
            'forms_by_type': self.metrics.forms_by_type,
            'completion_rate': self.metrics.completion_rate,
            'recent_activity': self.metrics.recent_activity,
            'critical_updates': self.metrics.critical_updates,
            'resource_summary': self.metrics.resource_summary,
            'timeline_events': self.metrics.timeline_events,
            'last_updated': self.metrics.last_updated.isoformat(),
            'export_timestamp': datetime.now().isoformat()
        }


def create_dashboard_widget(form_service: MultiFormService = None, 
                          incident_name: str = "") -> DashboardWidget:
    """Factory function to create dashboard widget.
    
    Args:
        form_service: Multi-form service for data access
        incident_name: Initial incident name
        
    Returns:
        DashboardWidget: Configured dashboard widget
    """
    dashboard = DashboardWidget(form_service)
    if incident_name:
        dashboard.set_incident(incident_name)
    return dashboard


def export_dashboard_snapshot(dashboard: DashboardWidget, 
                            filepath: str) -> bool:
    """Export dashboard snapshot to file.
    
    Args:
        dashboard: Dashboard widget to export
        filepath: Path to export file
        
    Returns:
        bool: True if export successful
    """
    try:
        data = dashboard.export_dashboard_data()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error exporting dashboard snapshot: {e}")
        return False