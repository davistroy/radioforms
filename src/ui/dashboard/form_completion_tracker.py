"""Form Completion Tracker for Dashboard.

Tracks and visualizes form completion status across different form types
with progress indicators, completion rates, and actionable insights for
emergency management operations.

Following CLAUDE.md principles:
- Clear visual indicators for completion status
- Performance optimized for real-time tracking
- Actionable information for decision making
- Comprehensive form lifecycle management

Example:
    >>> from src.ui.dashboard.form_completion_tracker import FormCompletionTracker
    >>> tracker = FormCompletionTracker()
    >>> tracker.set_required_forms(['ICS-213', 'ICS-214', 'ICS-205'])
    >>> tracker.update_completion_status(forms_data)

Classes:
    FormCompletionTracker: Main completion tracking widget
    FormCompletionData: Data container for completion metrics
    CompletionStatus: Status enumeration for forms
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
        QGroupBox, QHeaderView, QPushButton, QFrame
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QColor, QBrush
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QProgressBar = QTableWidget = QTableWidgetItem = object
    QGroupBox = QHeaderView = QPushButton = QFrame = object
    Signal = object
    QFont = QColor = QBrush = object
    Qt = type('Qt', (), {'AlignCenter': 0, 'red': 0, 'green': 0, 'yellow': 0})

logger = logging.getLogger(__name__)


class CompletionStatus(Enum):
    """Form completion status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    VALIDATED = "validated"


@dataclass
class FormCompletionData:
    """Container for form completion tracking data."""
    form_type: str
    required_count: int = 1
    completed_count: int = 0
    in_progress_count: int = 0
    overdue_count: int = 0
    last_update: datetime = None
    completion_rate: float = 0.0
    status: CompletionStatus = CompletionStatus.NOT_STARTED
    priority_level: str = "Normal"
    estimated_completion: datetime = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()
        self._calculate_completion_rate()
        self._determine_status()
    
    def _calculate_completion_rate(self):
        """Calculate completion rate percentage."""
        if self.required_count > 0:
            self.completion_rate = (self.completed_count / self.required_count) * 100
        else:
            self.completion_rate = 0.0
    
    def _determine_status(self):
        """Determine overall completion status."""
        if self.overdue_count > 0:
            self.status = CompletionStatus.OVERDUE
        elif self.completed_count >= self.required_count:
            self.status = CompletionStatus.VALIDATED
        elif self.completed_count > 0 or self.in_progress_count > 0:
            self.status = CompletionStatus.IN_PROGRESS
        else:
            self.status = CompletionStatus.NOT_STARTED


class FormCompletionTracker(QWidget):
    """Form completion tracking widget for dashboard.
    
    Provides comprehensive tracking of form completion status across
    different form types with visual indicators and actionable insights.
    """
    
    form_selected = Signal(str) if HAS_PYSIDE6 else None
    completion_updated = Signal(dict) if HAS_PYSIDE6 else None
    
    def __init__(self, parent=None):
        """Initialize form completion tracker."""
        self.completion_data: Dict[str, FormCompletionData] = {}
        self.required_forms = []
        
        if not HAS_PYSIDE6:
            logger.info("Form completion tracker initialized (no PySide6)")
            return
            
        super().__init__(parent)
        self._init_ui()
        
        logger.info("Form completion tracker initialized")
    
    def _init_ui(self):
        """Initialize user interface components."""
        self.setObjectName("FormCompletionTracker")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Summary section
        summary_frame = self._create_summary_section()
        main_layout.addWidget(summary_frame)
        
        # Completion table
        table_frame = self._create_completion_table()
        main_layout.addWidget(table_frame)
        
        # Action buttons
        actions_frame = self._create_actions_section()
        main_layout.addWidget(actions_frame)
    
    def _create_summary_section(self) -> QFrame:
        """Create completion summary section."""
        frame = QGroupBox("Completion Summary")
        layout = QHBoxLayout(frame)
        
        # Overall progress
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("Overall Progress"))
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        progress_layout.addWidget(self.overall_progress)
        layout.addLayout(progress_layout)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # Completed forms
        metrics_layout.addWidget(QLabel("Completed:"), 0, 0)
        self.completed_label = QLabel("0")
        self.completed_label.setObjectName("CompletedMetric")
        metrics_layout.addWidget(self.completed_label, 0, 1)
        
        # In progress forms
        metrics_layout.addWidget(QLabel("In Progress:"), 1, 0)
        self.in_progress_label = QLabel("0")
        self.in_progress_label.setObjectName("InProgressMetric")
        metrics_layout.addWidget(self.in_progress_label, 1, 1)
        
        # Overdue forms
        metrics_layout.addWidget(QLabel("Overdue:"), 0, 2)
        self.overdue_label = QLabel("0")
        self.overdue_label.setObjectName("OverdueMetric")
        metrics_layout.addWidget(self.overdue_label, 0, 3)
        
        # Required forms
        metrics_layout.addWidget(QLabel("Required:"), 1, 2)
        self.required_label = QLabel("0")
        self.required_label.setObjectName("RequiredMetric")
        metrics_layout.addWidget(self.required_label, 1, 3)
        
        layout.addLayout(metrics_layout)
        
        return frame
    
    def _create_completion_table(self) -> QFrame:
        """Create form completion table."""
        frame = QGroupBox("Form Completion Details")
        layout = QVBoxLayout(frame)
        
        self.completion_table = QTableWidget()
        self.completion_table.setColumnCount(6)
        self.completion_table.setHorizontalHeaderLabels([
            "Form Type", "Required", "Completed", "Progress", "Status", "Priority"
        ])
        
        # Configure table
        header = self.completion_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.completion_table.setAlternatingRowColors(True)
        self.completion_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Connect selection signal
        if hasattr(self.completion_table, 'itemDoubleClicked'):
            self.completion_table.itemDoubleClicked.connect(self._on_form_selected)
        
        layout.addWidget(self.completion_table)
        
        return frame
    
    def _create_actions_section(self) -> QFrame:
        """Create action buttons section."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Create form button
        self.create_form_button = QPushButton("Create Required Form")
        self.create_form_button.clicked.connect(self._on_create_form)
        layout.addWidget(self.create_form_button)
        
        # View overdue button
        self.view_overdue_button = QPushButton("View Overdue Forms")
        self.view_overdue_button.clicked.connect(self._on_view_overdue)
        layout.addWidget(self.view_overdue_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Status")
        self.refresh_button.clicked.connect(self._on_refresh)
        layout.addWidget(self.refresh_button)
        
        layout.addStretch()
        
        return frame
    
    def set_required_forms(self, form_types: List[str], 
                          requirements: Dict[str, int] = None):
        """Set required forms for tracking.
        
        Args:
            form_types: List of required form types
            requirements: Dict mapping form types to required counts
        """
        self.required_forms = form_types
        
        # Initialize completion data
        for form_type in form_types:
            required_count = requirements.get(form_type, 1) if requirements else 1
            self.completion_data[form_type] = FormCompletionData(
                form_type=form_type,
                required_count=required_count
            )
        
        self._update_display()
        logger.info(f"Required forms set: {form_types}")
    
    def update_completion_status(self, forms_data: List[Dict[str, Any]]):
        """Update completion status from forms data.
        
        Args:
            forms_data: List of form data dictionaries
        """
        # Reset counts
        for data in self.completion_data.values():
            data.completed_count = 0
            data.in_progress_count = 0
            data.overdue_count = 0
        
        # Count forms by type and status
        for form in forms_data:
            form_type = form.get('form_type', '')
            if form_type not in self.completion_data:
                continue
            
            data = self.completion_data[form_type]
            
            # Determine form status
            status = form.get('status', 'draft')
            created_time = form.get('created_at')
            
            if status == 'completed' or status == 'submitted':
                data.completed_count += 1
            elif status == 'draft' or status == 'in_progress':
                data.in_progress_count += 1
            
            # Check for overdue forms (simplified logic)
            if created_time:
                try:
                    created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    if datetime.now() - created_dt > timedelta(hours=24):
                        if status != 'completed' and status != 'submitted':
                            data.overdue_count += 1
                except ValueError:
                    pass
            
            data.last_update = datetime.now()
            data._calculate_completion_rate()
            data._determine_status()
        
        self._update_display()
        
        if self.completion_updated:
            self.completion_updated.emit(self._get_summary_data())
        
        logger.debug("Completion status updated")
    
    def _update_display(self):
        """Update all display components."""
        if not HAS_PYSIDE6:
            return
            
        self._update_summary()
        self._update_table()
    
    def _update_summary(self):
        """Update summary metrics display."""
        total_completed = sum(data.completed_count for data in self.completion_data.values())
        total_in_progress = sum(data.in_progress_count for data in self.completion_data.values())
        total_overdue = sum(data.overdue_count for data in self.completion_data.values())
        total_required = sum(data.required_count for data in self.completion_data.values())
        
        # Update labels
        self.completed_label.setText(str(total_completed))
        self.in_progress_label.setText(str(total_in_progress))
        self.overdue_label.setText(str(total_overdue))
        self.required_label.setText(str(total_required))
        
        # Update overall progress
        if total_required > 0:
            overall_progress = (total_completed / total_required) * 100
            self.overall_progress.setValue(int(overall_progress))
        else:
            self.overall_progress.setValue(0)
    
    def _update_table(self):
        """Update completion table display."""
        table = self.completion_table
        data_items = list(self.completion_data.values())
        
        table.setRowCount(len(data_items))
        
        for row, data in enumerate(data_items):
            # Form type
            table.setItem(row, 0, QTableWidgetItem(data.form_type))
            
            # Required count
            table.setItem(row, 1, QTableWidgetItem(str(data.required_count)))
            
            # Completed count
            completed_item = QTableWidgetItem(str(data.completed_count))
            if data.completed_count >= data.required_count:
                completed_item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
            table.setItem(row, 2, completed_item)
            
            # Progress bar (as text for simplicity)
            progress_text = f"{data.completion_rate:.1f}%"
            progress_item = QTableWidgetItem(progress_text)
            progress_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 3, progress_item)
            
            # Status
            status_item = QTableWidgetItem(data.status.value.replace('_', ' ').title())
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Apply status-specific coloring
            if data.status == CompletionStatus.COMPLETED or data.status == CompletionStatus.VALIDATED:
                status_item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
            elif data.status == CompletionStatus.OVERDUE:
                status_item.setBackground(QBrush(QColor(255, 182, 193)))  # Light red
            elif data.status == CompletionStatus.IN_PROGRESS:
                status_item.setBackground(QBrush(QColor(255, 255, 224)))  # Light yellow
            
            table.setItem(row, 4, status_item)
            
            # Priority
            table.setItem(row, 5, QTableWidgetItem(data.priority_level))
    
    def _get_summary_data(self) -> Dict[str, Any]:
        """Get completion summary data.
        
        Returns:
            Dict containing completion summary
        """
        total_completed = sum(data.completed_count for data in self.completion_data.values())
        total_in_progress = sum(data.in_progress_count for data in self.completion_data.values())
        total_overdue = sum(data.overdue_count for data in self.completion_data.values())
        total_required = sum(data.required_count for data in self.completion_data.values())
        
        overall_rate = (total_completed / total_required * 100) if total_required > 0 else 0
        
        return {
            'total_completed': total_completed,
            'total_in_progress': total_in_progress,
            'total_overdue': total_overdue,
            'total_required': total_required,
            'overall_completion_rate': overall_rate,
            'completion_data': {
                form_type: {
                    'required': data.required_count,
                    'completed': data.completed_count,
                    'in_progress': data.in_progress_count,
                    'overdue': data.overdue_count,
                    'completion_rate': data.completion_rate,
                    'status': data.status.value
                }
                for form_type, data in self.completion_data.items()
            }
        }
    
    def get_overdue_forms(self) -> List[str]:
        """Get list of overdue form types.
        
        Returns:
            List of form types that are overdue
        """
        return [
            form_type for form_type, data in self.completion_data.items()
            if data.overdue_count > 0
        ]
    
    def get_missing_forms(self) -> List[str]:
        """Get list of missing required form types.
        
        Returns:
            List of form types that haven't been started
        """
        return [
            form_type for form_type, data in self.completion_data.items()
            if data.completed_count == 0 and data.in_progress_count == 0
        ]
    
    def _on_form_selected(self, item):
        """Handle form selection from table."""
        if not item:
            return
            
        row = item.row()
        if row < self.completion_table.rowCount():
            form_type = self.completion_table.item(row, 0).text()
            if self.form_selected:
                self.form_selected.emit(form_type)
            
            logger.info(f"Form type selected from completion tracker: {form_type}")
    
    def _on_create_form(self):
        """Handle create form button click."""
        # Get the first missing or incomplete form type
        missing_forms = self.get_missing_forms()
        if missing_forms:
            form_type = missing_forms[0]
            if self.form_selected:
                self.form_selected.emit(form_type)
            logger.info(f"Create form requested for: {form_type}")
    
    def _on_view_overdue(self):
        """Handle view overdue forms button click."""
        overdue_forms = self.get_overdue_forms()
        if overdue_forms:
            # Signal to show overdue forms
            logger.info(f"View overdue forms requested: {overdue_forms}")
    
    def _on_refresh(self):
        """Handle refresh button click."""
        # Signal parent to refresh data
        logger.info("Completion status refresh requested")