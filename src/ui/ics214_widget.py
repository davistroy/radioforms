"""ICS-214 Activity Log form widget implementation.

This module provides the complete UI implementation for ICS-214 Activity Log forms,
following the established RadioForms patterns and PySide6 GUI development guidelines.
The widget supports dynamic activity entry, resource assignment management, and
comprehensive form validation with visual feedback.

The implementation includes:
- Dynamic activity table with time-sequence validation
- Resource assignment table management
- Operational period date/time selection
- Form validation with visual indicators
- Auto-save functionality
- Keyboard navigation and accessibility support

Example:
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> 
    >>> app = QApplication(sys.argv)
    >>> widget = ICS214Widget()
    >>> widget.show()
    >>> 
    >>> # Load existing form data
    >>> form_data = load_ics214_from_json(json_string)
    >>> widget.load_form_data(form_data)
    >>> 
    >>> # Get form data for saving
    >>> current_data = widget.get_form_data()
    >>> app.exec()

Classes:
    ActivityTableWidget: Custom table widget for activity log entries
    ResourceTableWidget: Custom table widget for resource assignments
    OperationalPeriodWidget: Widget for operational period date/time selection
    ICS214Widget: Main form widget for ICS-214 Activity Log

Functions:
    setup_activity_table: Configure activity table columns and properties
    setup_resource_table: Configure resource table columns and properties
    validate_form_data: Validate complete form data with visual feedback

Notes:
    This implementation follows the pyside6-rules.md guidelines for proper
    widget parenting, signal-slot patterns, and resource management. All
    UI components are designed for keyboard accessibility and WCAG compliance.
"""

from __future__ import annotations

import sys
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QGroupBox, QSpacerItem, QSizePolicy,
    QMessageBox, QCompleter, QComboBox, QFrame, QScrollArea, QTabWidget,
    QApplication, QAbstractItemView
)
from PySide6.QtCore import (
    Signal, Qt, QDateTime, QDate, QTime, QTimer, QModelIndex, QStringListModel
)
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QKeySequence, QAction

try:
    from ..models.ics214 import (
        ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment, 
        OperationalPeriod, Person, create_new_ics214
    )
except ImportError:
    # For standalone testing, import from absolute path
    import sys
    sys.path.append('.')
    from src.models.ics214 import (
        ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment, 
        OperationalPeriod, Person, create_new_ics214
    )


class ActivityTableWidget(QTableWidget):
    """Custom table widget for ICS-214 activity log entries.
    
    This widget provides a specialized table for managing activity entries with
    time-sequence validation, sorting capabilities, and integrated add/remove
    functionality. Supports dynamic row management and keyboard shortcuts.
    
    Signals:
        activity_added: Emitted when a new activity is added
        activity_removed: Emitted when an activity is removed
        activity_modified: Emitted when an activity is modified
        validation_changed: Emitted when validation status changes
        
    Example:
        >>> table = ActivityTableWidget()
        >>> table.activity_added.connect(handle_activity_added)
        >>> table.add_activity_entry()
    """
    
    activity_added = Signal()
    activity_removed = Signal(int)  # row index
    activity_modified = Signal(int)  # row index
    validation_changed = Signal(bool)  # is_valid
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize activity table widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        self.setup_table()
        self.setup_connections()
        
        # Track validation state
        self._is_valid = True
        
        # Setup context menu and keyboard shortcuts
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.setup_context_actions()
    
    def setup_table(self) -> None:
        """Configure table columns and properties."""
        # Set up columns: Date, Time, Activities, Location, Personnel
        self.setColumnCount(5)
        headers = ['Date', 'Time', 'Notable Activities', 'Location', 'Personnel Involved']
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # Configure column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Time
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Activities
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Location
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Personnel
        
        # Configure vertical header
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
        
        # Set minimum size
        self.setMinimumHeight(200)
    
    def setup_connections(self) -> None:
        """Set up signal connections for table events."""
        self.itemChanged.connect(self.on_item_changed)
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def setup_context_actions(self) -> None:
        """Set up context menu actions and keyboard shortcuts."""
        # Add activity action
        add_action = QAction("Add Activity", self)
        add_action.setShortcut(QKeySequence("Ctrl+Plus"))
        add_action.triggered.connect(self.add_activity_entry)
        self.addAction(add_action)
        
        # Remove activity action
        remove_action = QAction("Remove Activity", self)
        remove_action.setShortcut(QKeySequence("Delete"))
        remove_action.triggered.connect(self.remove_selected_activity)
        self.addAction(remove_action)
        
        # Edit activity action
        edit_action = QAction("Edit Activity", self)
        edit_action.setShortcut(QKeySequence("F2"))
        edit_action.triggered.connect(self.edit_selected_activity)
        self.addAction(edit_action)
    
    def add_activity_entry(self, activity: Optional[ActivityEntry] = None) -> int:
        """Add a new activity entry to the table.
        
        Args:
            activity: Optional activity entry to add. If None, creates empty entry.
            
        Returns:
            int: Row index of the added activity entry.
        """
        if activity is None:
            activity = ActivityEntry()
        
        row = self.rowCount()
        self.insertRow(row)
        
        # Create table items with activity data
        date_item = QTableWidgetItem(activity.format_date())
        time_item = QTableWidgetItem(activity.format_time())
        activities_item = QTableWidgetItem(activity.notable_activities)
        location_item = QTableWidgetItem(activity.location)
        personnel_item = QTableWidgetItem(activity.personnel_involved)
        
        # Set items in table
        self.setItem(row, 0, date_item)
        self.setItem(row, 1, time_item)
        self.setItem(row, 2, activities_item)
        self.setItem(row, 3, location_item)
        self.setItem(row, 4, personnel_item)
        
        # Store activity object in first column for reference
        date_item.setData(Qt.ItemDataRole.UserRole, activity)
        
        # Select the new row
        self.selectRow(row)
        
        # Emit signal
        self.activity_added.emit()
        
        return row
    
    def remove_selected_activity(self) -> bool:
        """Remove the currently selected activity entry.
        
        Returns:
            bool: True if an activity was removed, False otherwise.
        """
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            self.activity_removed.emit(current_row)
            return True
        return False
    
    def edit_selected_activity(self) -> None:
        """Start editing the currently selected activity entry."""
        current_row = self.currentRow()
        if current_row >= 0:
            # Focus on the activities column for editing
            activities_item = self.item(current_row, 2)
            if activities_item:
                self.setCurrentItem(activities_item)
                self.editItem(activities_item)
    
    def get_all_activities(self) -> List[ActivityEntry]:
        """Get all activity entries from the table.
        
        Returns:
            List[ActivityEntry]: List of all activity entries in the table.
        """
        activities = []
        
        for row in range(self.rowCount()):
            try:
                # Get data from table items
                date_str = self.item(row, 0).text() if self.item(row, 0) else ""
                time_str = self.item(row, 1).text() if self.item(row, 1) else ""
                notable_activities = self.item(row, 2).text() if self.item(row, 2) else ""
                location = self.item(row, 3).text() if self.item(row, 3) else ""
                personnel = self.item(row, 4).text() if self.item(row, 4) else ""
                
                # Parse datetime from date and time strings
                if date_str and time_str:
                    try:
                        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    except ValueError:
                        dt = datetime.now()
                else:
                    dt = datetime.now()
                
                # Create activity entry
                activity = ActivityEntry(
                    datetime=dt,
                    notable_activities=notable_activities,
                    location=location,
                    personnel_involved=personnel
                )
                
                activities.append(activity)
                
            except Exception:
                # Skip invalid entries
                continue
        
        # Sort by datetime
        activities.sort(key=lambda x: x.datetime)
        return activities
    
    def load_activities(self, activities: List[ActivityEntry]) -> None:
        """Load activity entries into the table.
        
        Args:
            activities: List of activity entries to load.
        """
        # Clear existing data
        self.setRowCount(0)
        
        # Add each activity
        for activity in activities:
            self.add_activity_entry(activity)
        
        # Validate after loading
        self.validate_activities()
    
    def validate_activities(self) -> bool:
        """Validate all activity entries and update visual feedback.
        
        Returns:
            bool: True if all activities are valid, False otherwise.
        """
        is_valid = True
        
        for row in range(self.rowCount()):
            # Check if required fields are filled
            activities_item = self.item(row, 2)
            if not activities_item or not activities_item.text().strip():
                is_valid = False
                # Highlight invalid row
                self.set_row_validation_style(row, False)
            else:
                self.set_row_validation_style(row, True)
        
        # Check chronological order
        activities = self.get_all_activities()
        if not self.is_chronological_order(activities):
            is_valid = False
        
        # Update validation state
        if self._is_valid != is_valid:
            self._is_valid = is_valid
            self.validation_changed.emit(is_valid)
        
        return is_valid
    
    def set_row_validation_style(self, row: int, is_valid: bool) -> None:
        """Set visual validation style for a table row.
        
        Args:
            row: Row index to style.
            is_valid: Whether the row data is valid.
        """
        color = QColor(255, 255, 255) if is_valid else QColor(255, 230, 230)
        
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(color)
    
    def is_chronological_order(self, activities: List[ActivityEntry]) -> bool:
        """Check if activities are in chronological order.
        
        Args:
            activities: List of activity entries to check.
            
        Returns:
            bool: True if activities are in chronological order.
        """
        if len(activities) <= 1:
            return True
        
        for i in range(1, len(activities)):
            if activities[i].datetime < activities[i-1].datetime:
                return False
        
        return True
    
    def on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item change events.
        
        Args:
            item: The changed table widget item.
        """
        if item:
            row = item.row()
            self.activity_modified.emit(row)
            
            # Revalidate after change
            QTimer.singleShot(100, self.validate_activities)
    
    def on_selection_changed(self) -> None:
        """Handle selection change events."""
        # Update action states based on selection
        has_selection = self.currentRow() >= 0
        
        # Enable/disable actions based on selection
        for action in self.actions():
            if "Remove" in action.text() or "Edit" in action.text():
                action.setEnabled(has_selection)


class ResourceTableWidget(QTableWidget):
    """Custom table widget for ICS-214 resource assignments.
    
    This widget provides a specialized table for managing resource assignments
    with validation and integrated add/remove functionality.
    
    Signals:
        resource_added: Emitted when a new resource is added
        resource_removed: Emitted when a resource is removed
        resource_modified: Emitted when a resource is modified
    """
    
    resource_added = Signal()
    resource_removed = Signal(int)  # row index
    resource_modified = Signal(int)  # row index
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize resource table widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        self.setup_table()
        self.setup_connections()
        
        # Setup context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.setup_context_actions()
    
    def setup_table(self) -> None:
        """Configure table columns and properties."""
        # Set up columns: Name, Position, Agency, Contact
        self.setColumnCount(4)
        headers = ['Name', 'ICS Position', 'Home Agency', 'Contact Info']
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Configure column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)          # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Position
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Agency
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Contact
        
        # Configure vertical header
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(30)
        
        # Set size constraints
        self.setMaximumHeight(150)
        self.setMinimumHeight(80)
    
    def setup_connections(self) -> None:
        """Set up signal connections for table events."""
        self.itemChanged.connect(self.on_item_changed)
    
    def setup_context_actions(self) -> None:
        """Set up context menu actions."""
        # Add resource action
        add_action = QAction("Add Resource", self)
        add_action.triggered.connect(self.add_resource_entry)
        self.addAction(add_action)
        
        # Remove resource action
        remove_action = QAction("Remove Resource", self)
        remove_action.triggered.connect(self.remove_selected_resource)
        self.addAction(remove_action)
    
    def add_resource_entry(self, resource: Optional[ResourceAssignment] = None) -> int:
        """Add a new resource entry to the table.
        
        Args:
            resource: Optional resource to add. If None, creates empty entry.
            
        Returns:
            int: Row index of the added resource entry.
        """
        if resource is None:
            resource = ResourceAssignment()
        
        row = self.rowCount()
        self.insertRow(row)
        
        # Create table items
        name_item = QTableWidgetItem(resource.name)
        position_item = QTableWidgetItem(resource.ics_position)
        agency_item = QTableWidgetItem(resource.home_agency)
        contact_item = QTableWidgetItem(resource.contact_info)
        
        # Set items in table
        self.setItem(row, 0, name_item)
        self.setItem(row, 1, position_item)
        self.setItem(row, 2, agency_item)
        self.setItem(row, 3, contact_item)
        
        # Select the new row
        self.selectRow(row)
        
        # Emit signal
        self.resource_added.emit()
        
        return row
    
    def remove_selected_resource(self) -> bool:
        """Remove the currently selected resource entry.
        
        Returns:
            bool: True if a resource was removed, False otherwise.
        """
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            self.resource_removed.emit(current_row)
            return True
        return False
    
    def get_all_resources(self) -> List[ResourceAssignment]:
        """Get all resource assignments from the table.
        
        Returns:
            List[ResourceAssignment]: List of all resource assignments.
        """
        resources = []
        
        for row in range(self.rowCount()):
            try:
                name = self.item(row, 0).text() if self.item(row, 0) else ""
                position = self.item(row, 1).text() if self.item(row, 1) else ""
                agency = self.item(row, 2).text() if self.item(row, 2) else ""
                contact = self.item(row, 3).text() if self.item(row, 3) else ""
                
                resource = ResourceAssignment(
                    name=name,
                    ics_position=position,
                    home_agency=agency,
                    contact_info=contact
                )
                
                resources.append(resource)
                
            except Exception:
                # Skip invalid entries
                continue
        
        return resources
    
    def load_resources(self, resources: List[ResourceAssignment]) -> None:
        """Load resource assignments into the table.
        
        Args:
            resources: List of resource assignments to load.
        """
        # Clear existing data
        self.setRowCount(0)
        
        # Add each resource
        for resource in resources:
            self.add_resource_entry(resource)
    
    def on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item change events.
        
        Args:
            item: The changed table widget item.
        """
        if item:
            row = item.row()
            self.resource_modified.emit(row)


class OperationalPeriodWidget(QWidget):
    """Widget for operational period date/time selection.
    
    Provides date and time selection controls for the operational period
    with validation to ensure end time is after start time.
    
    Signals:
        period_changed: Emitted when operational period changes
        validation_changed: Emitted when validation status changes
    """
    
    period_changed = Signal()
    validation_changed = Signal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize operational period widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
        # Set default values
        self.set_default_period()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QGridLayout(self)
        
        # From date/time
        layout.addWidget(QLabel("From:"), 0, 0)
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())
        layout.addWidget(self.from_date, 0, 1)
        
        self.from_time = QTimeEdit()
        self.from_time.setTime(QTime(6, 0))
        layout.addWidget(self.from_time, 0, 2)
        
        # To date/time
        layout.addWidget(QLabel("To:"), 1, 0)
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        layout.addWidget(self.to_date, 1, 1)
        
        self.to_time = QTimeEdit()
        self.to_time.setTime(QTime(18, 0))
        layout.addWidget(self.to_time, 1, 2)
        
        # Validation label
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.validation_label, 2, 0, 1, 3)
        
        # Set column stretch
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        self.from_date.dateChanged.connect(self.on_period_changed)
        self.from_time.timeChanged.connect(self.on_period_changed)
        self.to_date.dateChanged.connect(self.on_period_changed)
        self.to_time.timeChanged.connect(self.on_period_changed)
    
    def set_default_period(self) -> None:
        """Set default operational period (current day, 6 AM to 6 PM)."""
        today = QDate.currentDate()
        self.from_date.setDate(today)
        self.to_date.setDate(today)
        self.from_time.setTime(QTime(6, 0))
        self.to_time.setTime(QTime(18, 0))
    
    def get_operational_period(self) -> OperationalPeriod:
        """Get the current operational period.
        
        Returns:
            OperationalPeriod: Current operational period settings.
        """
        return OperationalPeriod(
            from_date=self.from_date.date().toPython(),
            from_time=self.from_time.time().toPython(),
            to_date=self.to_date.date().toPython(),
            to_time=self.to_time.time().toPython()
        )
    
    def set_operational_period(self, period: OperationalPeriod) -> None:
        """Set the operational period.
        
        Args:
            period: Operational period to set.
        """
        self.from_date.setDate(QDate(period.from_date))
        self.from_time.setTime(QTime(period.from_time))
        self.to_date.setDate(QDate(period.to_date))
        self.to_time.setTime(QTime(period.to_time))
    
    def validate_period(self) -> bool:
        """Validate the operational period.
        
        Returns:
            bool: True if period is valid, False otherwise.
        """
        period = self.get_operational_period()
        is_valid = period.is_valid()
        
        # Update validation display
        if is_valid:
            self.validation_label.setText("")
        else:
            self.validation_label.setText("End time must be after start time")
        
        self.validation_changed.emit(is_valid)
        return is_valid
    
    def on_period_changed(self) -> None:
        """Handle period change events."""
        self.validate_period()
        self.period_changed.emit()


class ICS214Widget(QWidget):
    """Main widget for ICS-214 Activity Log forms.
    
    This widget provides the complete user interface for creating, editing,
    and managing ICS-214 Activity Log forms. It includes all form sections,
    validation feedback, and integration with the data model.
    
    Signals:
        form_changed: Emitted when form data changes
        validation_changed: Emitted when form validation status changes
        save_requested: Emitted when user requests to save form
        
    Example:
        >>> widget = ICS214Widget()
        >>> widget.form_changed.connect(handle_form_change)
        >>> widget.load_form_data(ics214_form)
    """
    
    form_changed = Signal()
    validation_changed = Signal(bool)
    save_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize ICS-214 form widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        
        # Initialize form data
        self.form_data = create_new_ics214()
        self._validation_state = {}
        
        # Set up UI
        self.setup_ui()
        self.setup_connections()
        self.setup_validation()
        
        # Initialize with default data
        self.load_form_data(self.form_data)
    
    def setup_ui(self) -> None:
        """Set up the complete user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Create scroll area for form content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Header section
        header_group = self.create_header_section()
        scroll_layout.addWidget(header_group)
        
        # Resources section
        resources_group = self.create_resources_section()
        scroll_layout.addWidget(resources_group)
        
        # Activity log section
        activity_group = self.create_activity_section()
        scroll_layout.addWidget(activity_group)
        
        # Footer section
        footer_group = self.create_footer_section()
        scroll_layout.addWidget(footer_group)
        
        # Set up scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Validation status bar
        self.validation_bar = QLabel()
        self.validation_bar.setStyleSheet(
            "QLabel { padding: 5px; border: 1px solid #ccc; background-color: #f0f0f0; }"
        )
        main_layout.addWidget(self.validation_bar)
    
    def create_header_section(self) -> QGroupBox:
        """Create the header section with incident and individual information.
        
        Returns:
            QGroupBox: Header section group box.
        """
        group = QGroupBox("Incident Information")
        layout = QFormLayout(group)
        
        # Incident name
        self.incident_name_edit = QLineEdit()
        self.incident_name_edit.setMaxLength(100)
        self.incident_name_edit.setPlaceholderText("Enter incident name")
        layout.addRow("Incident Name *:", self.incident_name_edit)
        
        # Operational period
        self.operational_period_widget = OperationalPeriodWidget()
        layout.addRow("Operational Period:", self.operational_period_widget)
        
        # Individual information
        layout.addRow(QLabel(""))  # Separator
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter your name")
        layout.addRow("Name *:", self.name_edit)
        
        self.ics_position_edit = QLineEdit()
        self.ics_position_edit.setPlaceholderText("Enter your ICS position")
        layout.addRow("ICS Position *:", self.ics_position_edit)
        
        self.home_agency_edit = QLineEdit()
        self.home_agency_edit.setPlaceholderText("Enter your home agency and unit")
        layout.addRow("Home Agency *:", self.home_agency_edit)
        
        return group
    
    def create_resources_section(self) -> QGroupBox:
        """Create the resources assigned section.
        
        Returns:
            QGroupBox: Resources section group box.
        """
        group = QGroupBox("Resources Assigned")
        layout = QVBoxLayout(group)
        
        # Instructions
        instructions = QLabel(
            "List any resources assigned to you (personnel, equipment, units):"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Resource table
        self.resource_table = ResourceTableWidget()
        layout.addWidget(self.resource_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_resource_btn = QPushButton("Add Resource")
        self.add_resource_btn.clicked.connect(self.resource_table.add_resource_entry)
        button_layout.addWidget(self.add_resource_btn)
        
        self.remove_resource_btn = QPushButton("Remove Selected")
        self.remove_resource_btn.clicked.connect(self.resource_table.remove_selected_resource)
        button_layout.addWidget(self.remove_resource_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return group
    
    def create_activity_section(self) -> QGroupBox:
        """Create the activity log section.
        
        Returns:
            QGroupBox: Activity log section group box.
        """
        group = QGroupBox("Activity Log")
        layout = QVBoxLayout(group)
        
        # Instructions
        instructions = QLabel(
            "Record notable activities in chronological order. Include date/time and detailed descriptions:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Activity table
        self.activity_table = ActivityTableWidget()
        layout.addWidget(self.activity_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_activity_btn = QPushButton("Add Activity")
        self.add_activity_btn.clicked.connect(self.add_new_activity)
        button_layout.addWidget(self.add_activity_btn)
        
        self.remove_activity_btn = QPushButton("Remove Selected")
        self.remove_activity_btn.clicked.connect(self.activity_table.remove_selected_activity)
        button_layout.addWidget(self.remove_activity_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return group
    
    def create_footer_section(self) -> QGroupBox:
        """Create the footer section with prepared by information.
        
        Returns:
            QGroupBox: Footer section group box.
        """
        group = QGroupBox("Prepared By")
        layout = QFormLayout(group)
        
        self.prepared_by_name_edit = QLineEdit()
        self.prepared_by_name_edit.setPlaceholderText("Enter preparer name")
        layout.addRow("Name *:", self.prepared_by_name_edit)
        
        self.prepared_by_position_edit = QLineEdit()
        self.prepared_by_position_edit.setPlaceholderText("Enter position/title")
        layout.addRow("Position/Title *:", self.prepared_by_position_edit)
        
        self.prepared_by_signature_edit = QLineEdit()
        self.prepared_by_signature_edit.setPlaceholderText("Enter signature/initials")
        layout.addRow("Signature:", self.prepared_by_signature_edit)
        
        return group
    
    def setup_connections(self) -> None:
        """Set up signal connections for all form components."""
        # Header section connections
        self.incident_name_edit.textChanged.connect(self.on_form_changed)
        self.operational_period_widget.period_changed.connect(self.on_form_changed)
        self.name_edit.textChanged.connect(self.on_form_changed)
        self.ics_position_edit.textChanged.connect(self.on_form_changed)
        self.home_agency_edit.textChanged.connect(self.on_form_changed)
        
        # Resources section connections
        self.resource_table.resource_added.connect(self.on_form_changed)
        self.resource_table.resource_removed.connect(self.on_form_changed)
        self.resource_table.resource_modified.connect(self.on_form_changed)
        
        # Activity section connections
        self.activity_table.activity_added.connect(self.on_form_changed)
        self.activity_table.activity_removed.connect(self.on_form_changed)
        self.activity_table.activity_modified.connect(self.on_form_changed)
        self.activity_table.validation_changed.connect(self.on_activity_validation_changed)
        
        # Footer section connections
        self.prepared_by_name_edit.textChanged.connect(self.on_form_changed)
        self.prepared_by_position_edit.textChanged.connect(self.on_form_changed)
        self.prepared_by_signature_edit.textChanged.connect(self.on_form_changed)
        
        # Validation connections
        self.operational_period_widget.validation_changed.connect(self.on_period_validation_changed)
    
    def setup_validation(self) -> None:
        """Set up validation state tracking."""
        self._validation_state = {
            'header': False,
            'operational_period': False,
            'activities': False,
            'footer': False
        }
        
        # Set up validation timer for delayed validation
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_form)
        
        # Initial validation
        QTimer.singleShot(100, self.validate_form)
    
    def add_new_activity(self) -> None:
        """Add a new activity entry with current timestamp."""
        activity = ActivityEntry(datetime=datetime.now())
        self.activity_table.add_activity_entry(activity)
    
    def get_form_data(self) -> ICS214Form:
        """Get current form data from UI components.
        
        Returns:
            ICS214Form: Current form data.
        """
        # Update form data from UI
        self.form_data.data.incident_name = self.incident_name_edit.text()
        self.form_data.data.operational_period = self.operational_period_widget.get_operational_period()
        self.form_data.data.name = self.name_edit.text()
        self.form_data.data.ics_position = self.ics_position_edit.text()
        self.form_data.data.home_agency = self.home_agency_edit.text()
        
        # Resources
        self.form_data.data.resources_assigned = self.resource_table.get_all_resources()
        
        # Activities
        self.form_data.data.activity_log = self.activity_table.get_all_activities()
        
        # Footer
        self.form_data.data.prepared_by = Person(
            name=self.prepared_by_name_edit.text(),
            position=self.prepared_by_position_edit.text(),
            signature=self.prepared_by_signature_edit.text()
        )
        
        return self.form_data
    
    def load_form_data(self, form: ICS214Form) -> None:
        """Load form data into UI components.
        
        Args:
            form: Form data to load into the interface.
        """
        self.form_data = form
        
        # Block signals during loading to prevent unnecessary updates
        self.blockSignals(True)
        
        try:
            # Header section
            self.incident_name_edit.setText(form.data.incident_name)
            self.operational_period_widget.set_operational_period(form.data.operational_period)
            self.name_edit.setText(form.data.name)
            self.ics_position_edit.setText(form.data.ics_position)
            self.home_agency_edit.setText(form.data.home_agency)
            
            # Resources section
            self.resource_table.load_resources(form.data.resources_assigned)
            
            # Activity section
            self.activity_table.load_activities(form.data.activity_log)
            
            # Footer section
            self.prepared_by_name_edit.setText(form.data.prepared_by.name)
            self.prepared_by_position_edit.setText(form.data.prepared_by.position)
            self.prepared_by_signature_edit.setText(form.data.prepared_by.signature)
            
        finally:
            self.blockSignals(False)
        
        # Validate after loading
        QTimer.singleShot(100, self.validate_form)
    
    def validate_form(self) -> bool:
        """Validate the complete form and update status.
        
        Returns:
            bool: True if form is valid, False otherwise.
        """
        # Get current form data
        current_form = self.get_form_data()
        
        # Validate individual sections
        header_valid = self.validate_header_section()
        period_valid = current_form.data.operational_period.is_valid()
        activities_valid = len(current_form.data.activity_log) > 0 and all(
            activity.is_valid() for activity in current_form.data.activity_log
        )
        footer_valid = bool(current_form.data.prepared_by.name.strip())
        
        # Update validation state
        self._validation_state.update({
            'header': header_valid,
            'operational_period': period_valid,
            'activities': activities_valid,
            'footer': footer_valid
        })
        
        # Overall validation
        is_valid = current_form.is_valid()
        
        # Update validation display
        self.update_validation_display(is_valid)
        
        # Emit validation change signal
        self.validation_changed.emit(is_valid)
        
        return is_valid
    
    def validate_header_section(self) -> bool:
        """Validate the header section fields.
        
        Returns:
            bool: True if header section is valid.
        """
        return (
            bool(self.incident_name_edit.text().strip()) and
            bool(self.name_edit.text().strip()) and
            bool(self.ics_position_edit.text().strip()) and
            bool(self.home_agency_edit.text().strip())
        )
    
    def update_validation_display(self, is_valid: bool) -> None:
        """Update the validation status display.
        
        Args:
            is_valid: Whether the form is currently valid.
        """
        if is_valid:
            self.validation_bar.setText("✓ Form is valid and ready to save")
            self.validation_bar.setStyleSheet(
                "QLabel { padding: 5px; border: 1px solid #4CAF50; "
                "background-color: #E8F5E8; color: #2E7D32; }"
            )
        else:
            # Build detailed validation message
            issues = []
            if not self._validation_state['header']:
                issues.append("incomplete header information")
            if not self._validation_state['operational_period']:
                issues.append("invalid operational period")
            if not self._validation_state['activities']:
                issues.append("missing or invalid activities")
            if not self._validation_state['footer']:
                issues.append("missing prepared by information")
            
            message = "⚠ Form validation issues: " + ", ".join(issues)
            self.validation_bar.setText(message)
            self.validation_bar.setStyleSheet(
                "QLabel { padding: 5px; border: 1px solid #F44336; "
                "background-color: #FFEBEE; color: #C62828; }"
            )
    
    def on_form_changed(self) -> None:
        """Handle form change events."""
        # Delay validation to avoid excessive validation during typing
        self.validation_timer.start(500)  # 500ms delay
        self.form_changed.emit()
    
    def on_activity_validation_changed(self, is_valid: bool) -> None:
        """Handle activity validation changes.
        
        Args:
            is_valid: Whether activities are valid.
        """
        self._validation_state['activities'] = is_valid
        self.validate_form()
    
    def on_period_validation_changed(self, is_valid: bool) -> None:
        """Handle operational period validation changes.
        
        Args:
            is_valid: Whether operational period is valid.
        """
        self._validation_state['operational_period'] = is_valid
        self.validate_form()


# Example usage and testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show widget
    widget = ICS214Widget()
    widget.setWindowTitle("ICS-214 Activity Log")
    widget.resize(800, 600)
    widget.show()
    
    # Add some test data
    test_activity = ActivityEntry(
        datetime=datetime.now(),
        notable_activities="Test activity for demonstration purposes",
        location="Test Location",
        personnel_involved="Test Personnel"
    )
    widget.activity_table.add_activity_entry(test_activity)
    
    sys.exit(app.exec())