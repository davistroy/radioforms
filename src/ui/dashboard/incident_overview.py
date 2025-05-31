"""Incident Overview Component for Dashboard.

Provides detailed incident summary with key metrics, status indicators,
and critical information display for emergency management operations.

Following CLAUDE.md principles:
- Clear, actionable information display
- Performance optimized for real-time updates
- Intuitive emergency management workflow
- Comprehensive status visualization

Example:
    >>> from src.ui.dashboard.incident_overview import IncidentOverview
    >>> overview = IncidentOverview()
    >>> overview.set_incident_data(incident_data)
    >>> overview.update_status("active")

Classes:
    IncidentOverview: Main incident overview widget
    IncidentStatus: Status enumeration and management
    IncidentMetrics: Metrics calculation and display
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QFrame, QProgressBar, QGroupBox
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QPalette, QColor
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QFrame = QProgressBar = QGroupBox = object
    Signal = object
    QFont = QPalette = QColor = object
    Qt = type('Qt', (), {'AlignTop': 0, 'AlignLeft': 0})

logger = logging.getLogger(__name__)


class IncidentStatus(Enum):
    """Incident status enumeration."""
    ACTIVE = "active"
    MONITORING = "monitoring"
    CONTAINED = "contained"
    CONTROLLED = "controlled"
    CLOSED = "closed"


@dataclass
class IncidentData:
    """Container for incident data and metrics."""
    name: str = ""
    status: IncidentStatus = IncidentStatus.ACTIVE
    start_time: datetime = None
    location: str = ""
    incident_commander: str = ""
    total_personnel: int = 0
    total_resources: int = 0
    priority_level: str = "Normal"
    weather_conditions: str = ""
    safety_concerns: List[str] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.safety_concerns is None:
            self.safety_concerns = []


class IncidentOverview(QWidget):
    """Incident overview widget for dashboard display.
    
    Provides comprehensive incident information including status,
    metrics, personnel, resources, and safety information.
    """
    
    status_changed = Signal(str) if HAS_PYSIDE6 else None
    
    def __init__(self, parent=None):
        """Initialize incident overview widget."""
        if not HAS_PYSIDE6:
            return
            
        super().__init__(parent)
        self.incident_data = IncidentData()
        self._init_ui()
        
        logger.info("Incident overview widget initialized")
    
    def _init_ui(self):
        """Initialize user interface components."""
        self.setObjectName("IncidentOverview")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Incident header
        header_frame = self._create_header_section()
        main_layout.addWidget(header_frame)
        
        # Status and metrics
        metrics_frame = self._create_metrics_section()
        main_layout.addWidget(metrics_frame)
        
        # Personnel and resources
        resources_frame = self._create_resources_section()
        main_layout.addWidget(resources_frame)
        
        # Safety information
        safety_frame = self._create_safety_section()
        main_layout.addWidget(safety_frame)
    
    def _create_header_section(self) -> QFrame:
        """Create incident header section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(frame)
        
        # Incident name
        self.name_label = QLabel("No Incident Selected")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        layout.addWidget(self.name_label)
        
        # Basic info grid
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_label = QLabel("Unknown")
        self.status_label.setObjectName("IncidentStatus")
        info_layout.addWidget(self.status_label, 0, 1)
        
        info_layout.addWidget(QLabel("Duration:"), 0, 2)
        self.duration_label = QLabel("--")
        info_layout.addWidget(self.duration_label, 0, 3)
        
        info_layout.addWidget(QLabel("Location:"), 1, 0)
        self.location_label = QLabel("--")
        info_layout.addWidget(self.location_label, 1, 1)
        
        info_layout.addWidget(QLabel("IC:"), 1, 2)
        self.ic_label = QLabel("--")
        info_layout.addWidget(self.ic_label, 1, 3)
        
        layout.addLayout(info_layout)
        
        return frame
    
    def _create_metrics_section(self) -> QFrame:
        """Create metrics section with key indicators."""
        frame = QGroupBox("Key Metrics")
        layout = QHBoxLayout(frame)
        
        # Personnel metric
        personnel_layout = QVBoxLayout()
        personnel_layout.addWidget(QLabel("Personnel"))
        self.personnel_label = QLabel("0")
        self.personnel_label.setObjectName("MetricValue")
        personnel_layout.addWidget(self.personnel_label)
        layout.addLayout(personnel_layout)
        
        # Resources metric
        resources_layout = QVBoxLayout()
        resources_layout.addWidget(QLabel("Resources"))
        self.resources_label = QLabel("0")
        self.resources_label.setObjectName("MetricValue")
        resources_layout.addWidget(self.resources_label)
        layout.addLayout(resources_layout)
        
        # Priority indicator
        priority_layout = QVBoxLayout()
        priority_layout.addWidget(QLabel("Priority"))
        self.priority_label = QLabel("Normal")
        self.priority_label.setObjectName("PriorityLevel")
        priority_layout.addWidget(self.priority_label)
        layout.addLayout(priority_layout)
        
        # Progress indicator
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("Progress"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(25)  # Default value
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        return frame
    
    def _create_resources_section(self) -> QFrame:
        """Create resources and personnel section."""
        frame = QGroupBox("Resources & Personnel")
        layout = QVBoxLayout(frame)
        
        resources_layout = QGridLayout()
        
        # Personnel breakdown
        resources_layout.addWidget(QLabel("Command Staff:"), 0, 0)
        self.command_staff_label = QLabel("--")
        resources_layout.addWidget(self.command_staff_label, 0, 1)
        
        resources_layout.addWidget(QLabel("Operations:"), 1, 0)
        self.operations_label = QLabel("--")
        resources_layout.addWidget(self.operations_label, 1, 1)
        
        resources_layout.addWidget(QLabel("Equipment:"), 0, 2)
        self.equipment_label = QLabel("--")
        resources_layout.addWidget(self.equipment_label, 0, 3)
        
        resources_layout.addWidget(QLabel("Vehicles:"), 1, 2)
        self.vehicles_label = QLabel("--")
        resources_layout.addWidget(self.vehicles_label, 1, 3)
        
        layout.addLayout(resources_layout)
        
        return frame
    
    def _create_safety_section(self) -> QFrame:
        """Create safety information section."""
        frame = QGroupBox("Safety & Weather")
        layout = QVBoxLayout(frame)
        
        # Weather conditions
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel("Weather:"))
        self.weather_label = QLabel("--")
        weather_layout.addWidget(self.weather_label)
        weather_layout.addStretch()
        layout.addLayout(weather_layout)
        
        # Safety concerns
        safety_layout = QHBoxLayout()
        safety_layout.addWidget(QLabel("Safety Concerns:"))
        self.safety_label = QLabel("None reported")
        self.safety_label.setObjectName("SafetyStatus")
        safety_layout.addWidget(self.safety_label)
        safety_layout.addStretch()
        layout.addLayout(safety_layout)
        
        return frame
    
    def set_incident_data(self, data: IncidentData):
        """Set incident data for display.
        
        Args:
            data: IncidentData object with incident information
        """
        self.incident_data = data
        self._update_display()
        
        logger.debug(f"Incident overview updated for: {data.name}")
    
    def update_status(self, status: IncidentStatus):
        """Update incident status.
        
        Args:
            status: New incident status
        """
        self.incident_data.status = status
        self._update_status_display()
        
        if self.status_changed:
            self.status_changed.emit(status.value)
    
    def _update_display(self):
        """Update all display components with current data."""
        if not HAS_PYSIDE6:
            return
            
        # Update header
        self.name_label.setText(self.incident_data.name or "No Incident Selected")
        self.location_label.setText(self.incident_data.location or "--")
        self.ic_label.setText(self.incident_data.incident_commander or "--")
        
        # Update duration
        if self.incident_data.start_time:
            duration = datetime.now() - self.incident_data.start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            self.duration_label.setText(f"{hours:02d}:{minutes:02d}")
        
        # Update status
        self._update_status_display()
        
        # Update metrics
        self.personnel_label.setText(str(self.incident_data.total_personnel))
        self.resources_label.setText(str(self.incident_data.total_resources))
        self.priority_label.setText(self.incident_data.priority_level)
        
        # Update weather
        self.weather_label.setText(self.incident_data.weather_conditions or "--")
        
        # Update safety
        if self.incident_data.safety_concerns:
            safety_text = f"{len(self.incident_data.safety_concerns)} active"
        else:
            safety_text = "None reported"
        self.safety_label.setText(safety_text)
        
        # Update progress (simplified calculation)
        progress = self._calculate_progress()
        self.progress_bar.setValue(progress)
    
    def _update_status_display(self):
        """Update status display with appropriate styling."""
        if not HAS_PYSIDE6:
            return
            
        status = self.incident_data.status
        self.status_label.setText(status.value.title())
        
        # Apply status-specific styling
        if status == IncidentStatus.ACTIVE:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        elif status == IncidentStatus.MONITORING:
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        elif status == IncidentStatus.CONTAINED:
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        elif status == IncidentStatus.CONTROLLED:
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == IncidentStatus.CLOSED:
            self.status_label.setStyleSheet("color: gray; font-weight: bold;")
    
    def _calculate_progress(self) -> int:
        """Calculate incident progress percentage.
        
        Returns:
            int: Progress percentage (0-100)
        """
        # Simplified progress calculation based on status
        status_progress = {
            IncidentStatus.ACTIVE: 25,
            IncidentStatus.MONITORING: 50,
            IncidentStatus.CONTAINED: 75,
            IncidentStatus.CONTROLLED: 90,
            IncidentStatus.CLOSED: 100
        }
        
        return status_progress.get(self.incident_data.status, 0)
    
    def get_incident_summary(self) -> Dict[str, Any]:
        """Get incident summary data.
        
        Returns:
            Dict containing incident summary information
        """
        return {
            'name': self.incident_data.name,
            'status': self.incident_data.status.value,
            'duration': self._get_duration_hours(),
            'location': self.incident_data.location,
            'incident_commander': self.incident_data.incident_commander,
            'personnel': self.incident_data.total_personnel,
            'resources': self.incident_data.total_resources,
            'priority': self.incident_data.priority_level,
            'weather': self.incident_data.weather_conditions,
            'safety_concerns': len(self.incident_data.safety_concerns),
            'progress': self._calculate_progress()
        }
    
    def _get_duration_hours(self) -> float:
        """Get incident duration in hours.
        
        Returns:
            float: Duration in hours
        """
        if not self.incident_data.start_time:
            return 0.0
            
        duration = datetime.now() - self.incident_data.start_time
        return duration.total_seconds() / 3600.0