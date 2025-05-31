"""Timeline Widget for Incident Activity Visualization.

Provides chronological visualization of incident activities, form submissions,
and key events with filtering and navigation capabilities.

Following CLAUDE.md principles:
- Clear temporal visualization of incident progression
- Performance optimized for large incident timelines
- Intuitive navigation and filtering
- Actionable information display

Example:
    >>> from src.ui.dashboard.timeline_widget import TimelineWidget
    >>> timeline = TimelineWidget()
    >>> timeline.add_event("Form submitted", "ICS-213", datetime.now())
    >>> timeline.refresh_timeline()

Classes:
    TimelineWidget: Main timeline visualization widget
    TimelineEvent: Individual timeline event data
    EventType: Event type enumeration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
        QLabel, QFrame, QPushButton, QComboBox,
        QListWidget, QListWidgetItem, QGroupBox,
        QSizePolicy, QSpacerItem
    )
    from PySide6.QtCore import Qt, Signal, QTimer
    from PySide6.QtGui import QFont, QColor, QPalette
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QScrollArea = object
    QLabel = QFrame = QPushButton = QComboBox = object
    QListWidget = QListWidgetItem = QGroupBox = object
    QSizePolicy = QSpacerItem = object
    Signal = QTimer = object
    QFont = QColor = QPalette = object
    Qt = type('Qt', (), {'AlignTop': 0, 'AlignLeft': 0})

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Timeline event type enumeration."""
    FORM_CREATED = "form_created"
    FORM_SUBMITTED = "form_submitted"
    FORM_UPDATED = "form_updated"
    RESOURCE_ASSIGNED = "resource_assigned"
    STATUS_CHANGE = "status_change"
    COMMUNICATION = "communication"
    SAFETY_ALERT = "safety_alert"
    MILESTONE = "milestone"


@dataclass
class TimelineEvent:
    """Timeline event data container."""
    timestamp: datetime
    event_type: EventType
    title: str
    description: str = ""
    form_id: str = ""
    form_type: str = ""
    priority: str = "Normal"
    user: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TimelineWidget(QWidget):
    """Timeline visualization widget for incident activities.
    
    Displays chronological view of incident events with filtering
    and navigation capabilities for emergency management operations.
    """
    
    event_selected = Signal(dict) if HAS_PYSIDE6 else None
    timeline_filtered = Signal(str) if HAS_PYSIDE6 else None
    
    def __init__(self, parent=None):
        """Initialize timeline widget."""
        self.events: List[TimelineEvent] = []
        self.filtered_events: List[TimelineEvent] = []
        self.current_filter = "all"
        
        if not HAS_PYSIDE6:
            logger.info("Timeline widget initialized (no PySide6)")
            return
            
        super().__init__(parent)
        self._init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        
        logger.info("Timeline widget initialized")
    
    def _init_ui(self):
        """Initialize user interface components."""
        self.setObjectName("TimelineWidget")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Controls section
        controls_frame = self._create_controls_section()
        main_layout.addWidget(controls_frame)
        
        # Timeline display
        timeline_frame = self._create_timeline_section()
        main_layout.addWidget(timeline_frame)
    
    def _create_controls_section(self) -> QFrame:
        """Create timeline controls section."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Filter controls
        filter_label = QLabel("Filter:")
        layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Events",
            "Form Activities",
            "Resource Changes",
            "Communications",
            "Safety Alerts",
            "Milestones"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.filter_combo)
        
        layout.addStretch()
        
        # Time range controls
        range_label = QLabel("Range:")
        layout.addWidget(range_label)
        
        self.range_combo = QComboBox()
        self.range_combo.addItems([
            "Last Hour",
            "Last 4 Hours", 
            "Last 12 Hours",
            "Last 24 Hours",
            "All Time"
        ])
        self.range_combo.setCurrentText("Last 12 Hours")
        self.range_combo.currentTextChanged.connect(self._on_range_changed)
        layout.addWidget(self.range_combo)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_timeline)
        layout.addWidget(self.refresh_button)
        
        return frame
    
    def _create_timeline_section(self) -> QFrame:
        """Create timeline display section."""
        frame = QGroupBox("Incident Timeline")
        layout = QVBoxLayout(frame)
        
        # Timeline list with scroll area
        self.timeline_list = QListWidget()
        self.timeline_list.setAlternatingRowColors(True)
        self.timeline_list.itemDoubleClicked.connect(self._on_event_selected)
        
        layout.addWidget(self.timeline_list)
        
        # Status info
        self.status_label = QLabel("No events to display")
        self.status_label.setObjectName("TimelineStatus")
        layout.addWidget(self.status_label)
        
        return frame
    
    def add_event(self, title: str, description: str = "", 
                  event_type: EventType = EventType.MILESTONE,
                  timestamp: datetime = None, **kwargs):
        """Add event to timeline.
        
        Args:
            title: Event title
            description: Event description
            event_type: Type of event
            timestamp: Event timestamp (defaults to now)
            **kwargs: Additional event metadata
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        event = TimelineEvent(
            timestamp=timestamp,
            event_type=event_type,
            title=title,
            description=description,
            **kwargs
        )
        
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp, reverse=True)  # Most recent first
        
        self._apply_filters()
        self._update_display()
        
        logger.debug(f"Timeline event added: {title}")
    
    def add_form_event(self, form_data: Dict[str, Any], action: str):
        """Add form-related event to timeline.
        
        Args:
            form_data: Form data dictionary
            action: Action taken (created, updated, submitted)
        """
        form_type = form_data.get('form_type', 'Unknown')
        form_id = form_data.get('id', '')
        
        event_types = {
            'created': EventType.FORM_CREATED,
            'updated': EventType.FORM_UPDATED,
            'submitted': EventType.FORM_SUBMITTED
        }
        
        event_type = event_types.get(action, EventType.FORM_UPDATED)
        title = f"{form_type} {action}"
        description = f"Form {form_id} was {action}"
        
        self.add_event(
            title=title,
            description=description,
            event_type=event_type,
            form_id=form_id,
            form_type=form_type,
            metadata=form_data
        )
    
    def update_from_forms_data(self, forms_data: List[Dict[str, Any]]):
        """Update timeline from forms data.
        
        Args:
            forms_data: List of form data dictionaries
        """
        # Clear existing form events
        self.events = [e for e in self.events if not e.event_type.value.startswith('form_')]
        
        # Add events from forms data
        for form in forms_data:
            created_time = form.get('created_at')
            updated_time = form.get('updated_at')
            
            if created_time:
                try:
                    created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    self.add_event(
                        title=f"{form.get('form_type', 'Form')} Created",
                        description=f"New {form.get('form_type', 'form')} created",
                        event_type=EventType.FORM_CREATED,
                        timestamp=created_dt,
                        form_id=form.get('id', ''),
                        form_type=form.get('form_type', ''),
                        metadata=form
                    )
                except ValueError:
                    pass
            
            if updated_time and updated_time != created_time:
                try:
                    updated_dt = datetime.fromisoformat(updated_time.replace('Z', '+00:00'))
                    self.add_event(
                        title=f"{form.get('form_type', 'Form')} Updated",
                        description=f"{form.get('form_type', 'Form')} was modified",
                        event_type=EventType.FORM_UPDATED,
                        timestamp=updated_dt,
                        form_id=form.get('id', ''),
                        form_type=form.get('form_type', ''),
                        metadata=form
                    )
                except ValueError:
                    pass
        
        self._apply_filters()
        self._update_display()
        
        logger.debug(f"Timeline updated from {len(forms_data)} forms")
    
    def _apply_filters(self):
        """Apply current filters to events list."""
        # Time range filter
        time_ranges = {
            "Last Hour": timedelta(hours=1),
            "Last 4 Hours": timedelta(hours=4),
            "Last 12 Hours": timedelta(hours=12),
            "Last 24 Hours": timedelta(hours=24),
            "All Time": None
        }
        
        current_range = self.range_combo.currentText() if HAS_PYSIDE6 else "All Time"
        time_limit = time_ranges.get(current_range)
        
        now = datetime.now()
        filtered_events = []
        
        for event in self.events:
            # Apply time range filter
            if time_limit and (now - event.timestamp) > time_limit:
                continue
            
            # Apply event type filter
            if self.current_filter == "all":
                filtered_events.append(event)
            elif self.current_filter == "forms" and event.event_type.value.startswith('form_'):
                filtered_events.append(event)
            elif self.current_filter == "resources" and event.event_type == EventType.RESOURCE_ASSIGNED:
                filtered_events.append(event)
            elif self.current_filter == "communications" and event.event_type == EventType.COMMUNICATION:
                filtered_events.append(event)
            elif self.current_filter == "safety" and event.event_type == EventType.SAFETY_ALERT:
                filtered_events.append(event)
            elif self.current_filter == "milestones" and event.event_type == EventType.MILESTONE:
                filtered_events.append(event)
        
        self.filtered_events = filtered_events
    
    def _update_display(self):
        """Update timeline display with filtered events."""
        if not HAS_PYSIDE6:
            return
            
        self.timeline_list.clear()
        
        if not self.filtered_events:
            self.status_label.setText(f"No events match current filter ({len(self.events)} total events)")
            return
        
        for event in self.filtered_events:
            item = self._create_timeline_item(event)
            self.timeline_list.addItem(item)
        
        self.status_label.setText(f"Showing {len(self.filtered_events)} of {len(self.events)} events")
    
    def _create_timeline_item(self, event: TimelineEvent) -> QListWidgetItem:
        """Create timeline list item for event.
        
        Args:
            event: Timeline event
            
        Returns:
            QListWidgetItem: Configured list item
        """
        time_str = event.timestamp.strftime("%H:%M")
        date_str = event.timestamp.strftime("%m/%d")
        
        # Format item text
        item_text = f"[{time_str}] {event.title}"
        if event.description:
            item_text += f"\n          {event.description}"
        
        item = QListWidgetItem(item_text)
        
        # Set item data for event selection
        item.setData(Qt.UserRole, event)
        
        # Apply styling based on event type
        if event.event_type == EventType.SAFETY_ALERT:
            item.setBackground(QColor(255, 182, 193))  # Light red
        elif event.event_type == EventType.MILESTONE:
            item.setBackground(QColor(173, 216, 230))  # Light blue
        elif event.event_type.value.startswith('form_'):
            item.setBackground(QColor(240, 248, 255))  # Alice blue
        elif event.priority == "High":
            item.setBackground(QColor(255, 255, 224))  # Light yellow
        
        return item
    
    def refresh_timeline(self):
        """Refresh timeline display."""
        self._apply_filters()
        self._update_display()
        logger.debug("Timeline refreshed")
    
    def _on_filter_changed(self, filter_text: str):
        """Handle filter change."""
        filter_map = {
            "All Events": "all",
            "Form Activities": "forms",
            "Resource Changes": "resources",
            "Communications": "communications", 
            "Safety Alerts": "safety",
            "Milestones": "milestones"
        }
        
        self.current_filter = filter_map.get(filter_text, "all")
        self.refresh_timeline()
        
        if self.timeline_filtered:
            self.timeline_filtered.emit(self.current_filter)
    
    def _on_range_changed(self, range_text: str):
        """Handle time range change."""
        self.refresh_timeline()
    
    def _on_event_selected(self, item: QListWidgetItem):
        """Handle event selection."""
        if not item:
            return
            
        event = item.data(Qt.UserRole)
        if event and self.event_selected:
            event_data = {
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type.value,
                'title': event.title,
                'description': event.description,
                'form_id': event.form_id,
                'form_type': event.form_type,
                'priority': event.priority,
                'user': event.user,
                'metadata': event.metadata
            }
            self.event_selected.emit(event_data)
            
            logger.info(f"Timeline event selected: {event.title}")
    
    def _auto_refresh(self):
        """Auto-refresh timeline (called by timer)."""
        self.refresh_timeline()
    
    def start_auto_refresh(self, interval: int = 30000):
        """Start auto-refresh timer.
        
        Args:
            interval: Refresh interval in milliseconds
        """
        if HAS_PYSIDE6:
            self.refresh_timer.setInterval(interval)
            self.refresh_timer.start()
            logger.info(f"Timeline auto-refresh started (interval: {interval}ms)")
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        if HAS_PYSIDE6:
            self.refresh_timer.stop()
            logger.info("Timeline auto-refresh stopped")
    
    def get_timeline_summary(self) -> Dict[str, Any]:
        """Get timeline summary data.
        
        Returns:
            Dict containing timeline summary information
        """
        event_counts = {}
        for event_type in EventType:
            event_counts[event_type.value] = sum(
                1 for e in self.filtered_events if e.event_type == event_type
            )
        
        return {
            'total_events': len(self.events),
            'filtered_events': len(self.filtered_events),
            'current_filter': self.current_filter,
            'event_counts': event_counts,
            'latest_event': self.filtered_events[0].timestamp.isoformat() if self.filtered_events else None,
            'oldest_event': self.filtered_events[-1].timestamp.isoformat() if self.filtered_events else None
        }
    
    def clear_timeline(self):
        """Clear all timeline events."""
        self.events.clear()
        self.filtered_events.clear()
        self._update_display()
        logger.info("Timeline cleared")