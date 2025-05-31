"""Resource Summary Component for Dashboard.

Provides resource allocation summary and tracking for incident management
with personnel, equipment, and assignment visualization.

Following CLAUDE.md principles:
- Clear resource allocation overview
- Performance optimized for real-time updates
- Actionable resource management information
- Comprehensive resource tracking

Example:
    >>> from src.ui.dashboard.resource_summary import ResourceSummary
    >>> summary = ResourceSummary()
    >>> summary.update_resources(resource_data)
    >>> summary.set_personnel_count(45)

Classes:
    ResourceSummary: Main resource summary widget
    ResourceData: Resource information container
    ResourceType: Resource type enumeration
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QFrame, QGroupBox, QTableWidget,
        QTableWidgetItem, QProgressBar, QPushButton
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QColor, QBrush
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QFrame = QGroupBox = QTableWidget = object
    QTableWidgetItem = QProgressBar = QPushButton = object
    Signal = object
    QFont = QColor = QBrush = object
    Qt = type('Qt', (), {'AlignCenter': 0, 'UserRole': 0})

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource type enumeration."""
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    VEHICLES = "vehicles"
    AIRCRAFT = "aircraft"
    FACILITIES = "facilities"
    COMMUNICATIONS = "communications"


@dataclass
class ResourceData:
    """Resource information container."""
    resource_type: ResourceType
    name: str
    quantity: int = 1
    available: int = 1
    assigned: int = 0
    status: str = "Available"
    location: str = ""
    notes: str = ""
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def utilization_rate(self) -> float:
        """Calculate resource utilization rate."""
        if self.quantity == 0:
            return 0.0
        return (self.assigned / self.quantity) * 100


class ResourceSummary(QWidget):
    """Resource summary widget for dashboard display.
    
    Provides comprehensive resource allocation summary including
    personnel, equipment, vehicles, and assignment tracking.
    """
    
    resource_selected = Signal(dict) if HAS_PYSIDE6 else None
    assignment_requested = Signal(str) if HAS_PYSIDE6 else None
    
    def __init__(self, parent=None):
        """Initialize resource summary widget."""
        if not HAS_PYSIDE6:
            return
            
        super().__init__(parent)
        self.resources: Dict[str, ResourceData] = {}
        self.personnel_count = 0
        self.equipment_count = 0
        self.vehicle_count = 0
        self._init_ui()
        
        logger.info("Resource summary widget initialized")
    
    def _init_ui(self):
        """Initialize user interface components."""
        self.setObjectName("ResourceSummary")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Summary metrics
        metrics_frame = self._create_metrics_section()
        main_layout.addWidget(metrics_frame)
        
        # Resource allocation table
        allocation_frame = self._create_allocation_section()
        main_layout.addWidget(allocation_frame)
        
        # Quick actions
        actions_frame = self._create_actions_section()
        main_layout.addWidget(actions_frame)
    
    def _create_metrics_section(self) -> QFrame:
        """Create resource metrics summary section."""
        frame = QGroupBox("Resource Summary")
        layout = QGridLayout(frame)
        
        # Personnel summary
        layout.addWidget(QLabel("Personnel:"), 0, 0)
        self.personnel_label = QLabel("0")
        self.personnel_label.setObjectName("ResourceMetric")
        layout.addWidget(self.personnel_label, 0, 1)
        
        # Equipment summary
        layout.addWidget(QLabel("Equipment:"), 0, 2)
        self.equipment_label = QLabel("0")
        self.equipment_label.setObjectName("ResourceMetric")
        layout.addWidget(self.equipment_label, 0, 3)
        
        # Vehicles summary
        layout.addWidget(QLabel("Vehicles:"), 1, 0)
        self.vehicle_label = QLabel("0")
        self.vehicle_label.setObjectName("ResourceMetric")
        layout.addWidget(self.vehicle_label, 1, 1)
        
        # Utilization rate
        layout.addWidget(QLabel("Utilization:"), 1, 2)
        self.utilization_bar = QProgressBar()
        self.utilization_bar.setRange(0, 100)
        layout.addWidget(self.utilization_bar, 1, 3)
        
        return frame
    
    def _create_allocation_section(self) -> QFrame:
        """Create resource allocation table section."""
        frame = QGroupBox("Resource Allocation")
        layout = QVBoxLayout(frame)
        
        self.allocation_table = QTableWidget()
        self.allocation_table.setColumnCount(6)
        self.allocation_table.setHorizontalHeaderLabels([
            "Resource", "Type", "Total", "Available", "Assigned", "Status"
        ])
        
        # Configure table
        header = self.allocation_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        self.allocation_table.setAlternatingRowColors(True)
        self.allocation_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.allocation_table.itemDoubleClicked.connect(self._on_resource_selected)
        
        layout.addWidget(self.allocation_table)
        
        return frame
    
    def _create_actions_section(self) -> QFrame:
        """Create quick actions section."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Assign resource button
        self.assign_button = QPushButton("Assign Resource")
        self.assign_button.clicked.connect(self._on_assign_resource)
        layout.addWidget(self.assign_button)
        
        # View assignments button
        self.view_assignments_button = QPushButton("View Assignments")
        self.view_assignments_button.clicked.connect(self._on_view_assignments)
        layout.addWidget(self.view_assignments_button)
        
        # Update status button
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.clicked.connect(self._on_update_status)
        layout.addWidget(self.update_status_button)
        
        layout.addStretch()
        
        return frame
    
    def set_personnel_count(self, count: int):
        """Set total personnel count.
        
        Args:
            count: Total personnel assigned to incident
        """
        self.personnel_count = count
        self._update_metrics_display()
        
        logger.debug(f"Personnel count set to: {count}")
    
    def set_equipment_count(self, count: int):
        """Set total equipment count.
        
        Args:
            count: Total equipment assigned to incident
        """
        self.equipment_count = count
        self._update_metrics_display()
        
        logger.debug(f"Equipment count set to: {count}")
    
    def set_vehicle_count(self, count: int):
        """Set total vehicle count.
        
        Args:
            count: Total vehicles assigned to incident
        """
        self.vehicle_count = count
        self._update_metrics_display()
        
        logger.debug(f"Vehicle count set to: {count}")
    
    def add_resource(self, name: str, resource_type: ResourceType,
                    quantity: int = 1, available: int = None,
                    assigned: int = 0, **kwargs):
        """Add or update resource information.
        
        Args:
            name: Resource name/identifier
            resource_type: Type of resource
            quantity: Total quantity available
            available: Currently available (defaults to quantity - assigned)
            assigned: Currently assigned count
            **kwargs: Additional resource metadata
        """
        if available is None:
            available = quantity - assigned
        
        resource = ResourceData(
            resource_type=resource_type,
            name=name,
            quantity=quantity,
            available=available,
            assigned=assigned,
            **kwargs
        )
        
        self.resources[name] = resource
        self._update_display()
        
        logger.debug(f"Resource added/updated: {name}")
    
    def update_resources(self, resources_data: List[Dict[str, Any]]):
        """Update resources from data list.
        
        Args:
            resources_data: List of resource data dictionaries
        """
        self.resources.clear()
        
        for resource_info in resources_data:
            name = resource_info.get('name', 'Unknown')
            type_str = resource_info.get('type', 'equipment').lower()
            
            # Map string to ResourceType
            resource_type = ResourceType.EQUIPMENT  # Default
            for rt in ResourceType:
                if rt.value in type_str:
                    resource_type = rt
                    break
            
            self.add_resource(
                name=name,
                resource_type=resource_type,
                quantity=resource_info.get('quantity', 1),
                available=resource_info.get('available', 1),
                assigned=resource_info.get('assigned', 0),
                status=resource_info.get('status', 'Available'),
                location=resource_info.get('location', ''),
                notes=resource_info.get('notes', '')
            )
        
        logger.debug(f"Resources updated from data: {len(resources_data)} items")
    
    def _update_display(self):
        """Update all display components."""
        if not HAS_PYSIDE6:
            return
            
        self._update_metrics_display()
        self._update_allocation_table()
    
    def _update_metrics_display(self):
        """Update metrics summary display."""
        # Update counts
        self.personnel_label.setText(str(self.personnel_count))
        self.equipment_label.setText(str(self.equipment_count))
        self.vehicle_label.setText(str(self.vehicle_count))
        
        # Calculate overall utilization
        total_resources = sum(r.quantity for r in self.resources.values())
        total_assigned = sum(r.assigned for r in self.resources.values())
        
        if total_resources > 0:
            utilization = (total_assigned / total_resources) * 100
            self.utilization_bar.setValue(int(utilization))
        else:
            self.utilization_bar.setValue(0)
    
    def _update_allocation_table(self):
        """Update resource allocation table."""
        table = self.allocation_table
        resources = list(self.resources.values())
        
        table.setRowCount(len(resources))
        
        for row, resource in enumerate(resources):
            # Resource name
            table.setItem(row, 0, QTableWidgetItem(resource.name))
            
            # Resource type
            table.setItem(row, 1, QTableWidgetItem(resource.resource_type.value.title()))
            
            # Total quantity
            table.setItem(row, 2, QTableWidgetItem(str(resource.quantity)))
            
            # Available
            available_item = QTableWidgetItem(str(resource.available))
            if resource.available == 0:
                available_item.setBackground(QBrush(QColor(255, 182, 193)))  # Light red
            table.setItem(row, 3, available_item)
            
            # Assigned
            assigned_item = QTableWidgetItem(str(resource.assigned))
            if resource.assigned > 0:
                assigned_item.setBackground(QBrush(QColor(255, 255, 224)))  # Light yellow
            table.setItem(row, 4, assigned_item)
            
            # Status
            status_item = QTableWidgetItem(resource.status)
            if resource.status.lower() in ['unavailable', 'maintenance', 'offline']:
                status_item.setBackground(QBrush(QColor(255, 182, 193)))  # Light red
            elif resource.status.lower() in ['available', 'ready']:
                status_item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
            table.setItem(row, 5, status_item)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource summary data.
        
        Returns:
            Dict containing resource summary information
        """
        # Calculate totals by type
        type_totals = {}
        for resource_type in ResourceType:
            type_resources = [r for r in self.resources.values() if r.resource_type == resource_type]
            type_totals[resource_type.value] = {
                'total': sum(r.quantity for r in type_resources),
                'available': sum(r.available for r in type_resources),
                'assigned': sum(r.assigned for r in type_resources),
                'count': len(type_resources)
            }
        
        # Calculate overall metrics
        total_resources = sum(r.quantity for r in self.resources.values())
        total_available = sum(r.available for r in self.resources.values())
        total_assigned = sum(r.assigned for r in self.resources.values())
        
        utilization = (total_assigned / total_resources * 100) if total_resources > 0 else 0
        
        return {
            'personnel_count': self.personnel_count,
            'equipment_count': self.equipment_count,
            'vehicle_count': self.vehicle_count,
            'total_resources': total_resources,
            'total_available': total_available,
            'total_assigned': total_assigned,
            'utilization_rate': utilization,
            'by_type': type_totals,
            'resource_count': len(self.resources),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_available_resources(self, resource_type: ResourceType = None) -> List[ResourceData]:
        """Get list of available resources.
        
        Args:
            resource_type: Filter by resource type (optional)
            
        Returns:
            List of available resources
        """
        available = []
        for resource in self.resources.values():
            if resource.available > 0:
                if resource_type is None or resource.resource_type == resource_type:
                    available.append(resource)
        return available
    
    def get_overallocated_resources(self) -> List[ResourceData]:
        """Get list of overallocated resources.
        
        Returns:
            List of resources where assigned > quantity
        """
        return [r for r in self.resources.values() if r.assigned > r.quantity]
    
    def _on_resource_selected(self, item):
        """Handle resource selection from table."""
        if not item:
            return
            
        row = item.row()
        if row < self.allocation_table.rowCount():
            resource_name = self.allocation_table.item(row, 0).text()
            resource = self.resources.get(resource_name)
            
            if resource and self.resource_selected:
                resource_data = {
                    'name': resource.name,
                    'type': resource.resource_type.value,
                    'quantity': resource.quantity,
                    'available': resource.available,
                    'assigned': resource.assigned,
                    'status': resource.status,
                    'location': resource.location,
                    'notes': resource.notes,
                    'utilization_rate': resource.utilization_rate
                }
                self.resource_selected.emit(resource_data)
                
                logger.info(f"Resource selected: {resource_name}")
    
    def _on_assign_resource(self):
        """Handle assign resource button click."""
        # Get selected resource
        current_row = self.allocation_table.currentRow()
        if current_row >= 0:
            resource_name = self.allocation_table.item(current_row, 0).text()
            if self.assignment_requested:
                self.assignment_requested.emit(resource_name)
            logger.info(f"Resource assignment requested: {resource_name}")
    
    def _on_view_assignments(self):
        """Handle view assignments button click."""
        logger.info("View resource assignments requested")
    
    def _on_update_status(self):
        """Handle update status button click."""
        logger.info("Update resource status requested")