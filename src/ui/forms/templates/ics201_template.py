"""ICS-201 Incident Briefing form template.

This module provides the complete ICS-201 Incident Briefing form
implementation using the RadioForms template system.

Classes:
    ICS201Template: Complete ICS-201 form for incident briefing management

Notes:
    ICS-201 is the primary briefing document (87% user demand) and provides
    comprehensive incident situation and initial response information.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import base classes
from .base.form_template import FormTemplate, FormMetadata
from .sections.header_section import HeaderSectionTemplate
from .sections.approval_section import ApprovalSectionTemplate
from .fields.text_field import TextFieldTemplate, TextAreaFieldTemplate
from .fields.table_field import TableFieldTemplate, TableColumn, ColumnType
from .fields.date_field import DateTimeFieldTemplate

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QCheckBox, QGroupBox
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QWidget:
        pass
    class QVBoxLayout:
        def __init__(self, parent=None):
            pass
        def addWidget(self, widget):
            pass
    class QScrollArea:
        def setWidgetResizable(self, resizable):
            pass
        def setWidget(self, widget):
            pass
    class QCheckBox:
        def __init__(self, text=""):
            pass
        def setChecked(self, checked):
            pass
        def isChecked(self):
            return False
    class QGroupBox:
        def __init__(self, title=""):
            pass
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class ICS201Template(FormTemplate):
    """ICS-201 Incident Briefing form template.
    
    Provides the complete ICS-201 form for incident briefing and initial
    response documentation. This form serves as the primary briefing document
    for Incident Commanders and provides comprehensive incident information.
    
    The form includes:
    - Standard ICS header with incident identification information
    - Map/sketch area for visual incident representation
    - Situation summary and health/safety briefing
    - Current and planned objectives section
    - Current and planned actions chronological table
    - Current organization structure
    - Resource summary table with arrival tracking
    - Prepared by approval section
    
    Attributes:
        include_map_sketch: Whether to include map/sketch section
        max_actions_rows: Maximum number of action rows
        max_resources_rows: Maximum number of resource rows
        
    Example:
        >>> form = ICS201Template(
        ...     include_map_sketch=True,
        ...     max_actions_rows=20,
        ...     max_resources_rows=15
        ... )
        >>> widget = form.create_form_widget()
    """
    
    def __init__(self, **kwargs):
        """Initialize ICS-201 form template with all sections and fields."""
        
        # Extract configuration parameters
        self.include_map_sketch = kwargs.get('include_map_sketch', True)
        self.max_actions_rows = kwargs.get('max_actions_rows', 20)
        self.max_resources_rows = kwargs.get('max_resources_rows', 15)
        
        # Create form metadata
        metadata = FormMetadata(
            form_id="ics201",
            name="ICS 201 - INCIDENT BRIEFING",
            version="2020.1",
            description="Incident briefing and initial response documentation for Command and General Staff",
            fema_compliant=True,
            tags=["briefing", "initial_response", "command", "situation", "resources", "actions"]
        )
        
        # Create form sections
        sections = self._create_form_sections(**kwargs)
        
        # Initialize base form template
        super().__init__(
            metadata=metadata,
            sections=sections,
            layout="vertical",
            scrollable=True,
            max_width=1200,
            max_height=900
        )
        
        logger.info(f"Initialized ICS-201 form template with {len(sections)} sections")
    
    def create_form_widget(self) -> QWidget:
        """Create the Qt widget for the complete ICS-201 form.
        
        Returns:
            QWidget: The complete form widget containing all sections
        """
        if not PYSIDE6_AVAILABLE:
            # Return mock widget for testing
            return QWidget()
        
        if self.scrollable:
            # Create scrollable form
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            content_widget = QWidget()
            self._create_form_layout(content_widget)
            scroll_area.setWidget(content_widget)
            
            # Set size constraints if specified
            if self.max_width:
                scroll_area.setMaximumWidth(self.max_width)
            if self.max_height:
                scroll_area.setMaximumHeight(self.max_height)
            
            self.widget = scroll_area
            return scroll_area
        else:
            # Create non-scrollable form
            form_widget = QWidget()
            self._create_form_layout(form_widget)
            
            # Set size constraints if specified
            if self.max_width:
                form_widget.setMaximumWidth(self.max_width)
            if self.max_height:
                form_widget.setMaximumHeight(self.max_height)
            
            self.widget = form_widget
            return form_widget
    
    def _create_form_sections(self, **kwargs) -> List:
        """Create all sections for the ICS-201 form.
        
        Returns:
            List of form sections in display order
        """
        sections = []
        
        # 1. Header Section
        header_section = HeaderSectionTemplate(
            form_title="INCIDENT BRIEFING",
            form_number="ICS 201",
            include_form_number=True,
            include_page_info=True,
            page_prefix="Page"
        )
        sections.append(header_section)
        
        # 2. Map/Sketch Section (if included)
        if self.include_map_sketch:
            map_section = self._create_map_sketch_section()
            sections.append(map_section)
        
        # 3. Situation Summary Section
        situation_section = self._create_situation_summary_section()
        sections.append(situation_section)
        
        # 4. Current and Planned Objectives Section
        objectives_section = self._create_objectives_section()
        sections.append(objectives_section)
        
        # 5. Current and Planned Actions Section
        actions_section = self._create_actions_section()
        sections.append(actions_section)
        
        # 6. Current Organization Section
        organization_section = self._create_organization_section()
        sections.append(organization_section)
        
        # 7. Resource Summary Section
        resource_section = self._create_resource_summary_section()
        sections.append(resource_section)
        
        # 8. Approval Section
        approval_section = ApprovalSectionTemplate(
            include_approval=True,
            include_reviewed=False,
            approval_title="Prepared by (Initial Incident Commander)",
            signature_height=60,
            form_type="ics201"
        )
        sections.append(approval_section)
        
        return sections
    
    def _create_map_sketch_section(self):
        """Create the map/sketch section.
        
        Returns:
            Section containing the map/sketch text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Map/sketch area - using text area as placeholder
        map_field = TextAreaFieldTemplate(
            field_id="map_sketch",
            label="Map/Sketch (Attach sketch, diagram, or map)",
            required=False,
            placeholder="Describe the incident area layout, reference points, and key geographic features...",
            max_length=1500,
            min_rows=6,
            validation_rules=[]
        )
        
        section = DefaultSectionTemplate(
            section_id="map_sketch",
            title="MAP/SKETCH",
            fields=[map_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Visual representation of the incident area - attach sketches, diagrams, or maps as needed"
        )
        
        return section
    
    def _create_situation_summary_section(self):
        """Create the situation summary and health/safety briefing section.
        
        Returns:
            Section containing the situation summary text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Situation summary text area
        situation_field = TextAreaFieldTemplate(
            field_id="situation_summary",
            label="Situation Summary and Health and Safety Briefing",
            required=True,
            placeholder="Describe the current incident situation, status, and critical health/safety considerations...",
            max_length=3000,
            min_rows=8,
            validation_rules=[
                {
                    "type": "required",
                    "message": "Situation summary is required for incident briefing"
                },
                {
                    "type": "min_length",
                    "value": 20,
                    "message": "Situation summary must be at least 20 characters"
                }
            ]
        )
        
        section = DefaultSectionTemplate(
            section_id="situation_summary",
            title="SITUATION SUMMARY AND HEALTH AND SAFETY BRIEFING",
            fields=[situation_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Comprehensive summary of incident situation and critical safety information"
        )
        
        return section
    
    def _create_objectives_section(self):
        """Create the current and planned objectives section.
        
        Returns:
            Section containing the objectives text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Objectives text area
        objectives_field = TextAreaFieldTemplate(
            field_id="current_planned_objectives",
            label="Current and Planned Objectives",
            required=True,
            placeholder="List current and planned incident objectives in priority order...",
            max_length=2000,
            min_rows=6,
            validation_rules=[
                {
                    "type": "required",
                    "message": "Current and planned objectives are required"
                },
                {
                    "type": "min_length",
                    "value": 10,
                    "message": "Objectives must be at least 10 characters"
                }
            ]
        )
        
        section = DefaultSectionTemplate(
            section_id="objectives",
            title="CURRENT AND PLANNED OBJECTIVES",
            fields=[objectives_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="List of incident objectives in priority order"
        )
        
        return section
    
    def _create_actions_section(self):
        """Create the current and planned actions table section.
        
        Returns:
            Section containing the actions table
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Define actions table columns
        actions_columns = [
            TableColumn(
                column_id="action_time",
                label="Time",
                column_type=ColumnType.TEXT,
                width=80,
                required=True,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="action_description",
                label="Actions (Taken and Planned)",
                column_type=ColumnType.TEXT,
                width=400,
                required=True,
                default_value="",
                editable=True
            )
        ]
        
        # Create actions table field
        actions_table = TableFieldTemplate(
            field_id="current_planned_actions",
            label="Current and Planned Actions",
            columns=actions_columns,
            min_rows=5,
            max_rows=self.max_actions_rows,
            allow_add=True,
            allow_remove=True,
            show_row_numbers=True,
            alternating_colors=True,
            single_selection=False,
            required=True
        )
        
        section = DefaultSectionTemplate(
            section_id="actions",
            title="CURRENT AND PLANNED ACTIONS",
            fields=[actions_table],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Chronological list of actions taken and planned (in time order)"
        )
        
        return section
    
    def _create_organization_section(self):
        """Create the current organization section.
        
        Returns:
            Section containing organization fields
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Organization text area - simplified for now
        organization_field = TextAreaFieldTemplate(
            field_id="current_organization",
            label="Current Organization",
            required=True,
            placeholder="List the current incident organization structure (IC, Operations, Planning, Logistics, Finance/Admin, Safety, etc.)...",
            max_length=2000,
            min_rows=8,
            validation_rules=[
                {
                    "type": "required",
                    "message": "Current organization structure is required"
                },
                {
                    "type": "min_length",
                    "value": 15,
                    "message": "Organization must include at minimum the Incident Commander"
                }
            ]
        )
        
        section = DefaultSectionTemplate(
            section_id="organization",
            title="CURRENT ORGANIZATION",
            fields=[organization_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Current incident organization structure and personnel assignments"
        )
        
        return section
    
    def _create_resource_summary_section(self):
        """Create the resource summary table section.
        
        Returns:
            Section containing the resource summary table
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Define resource summary table columns
        resource_columns = [
            TableColumn(
                column_id="resource_name",
                label="Resource",
                column_type=ColumnType.TEXT,
                width=120,
                required=True,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="resource_identifier",
                label="Resource Identifier",
                column_type=ColumnType.TEXT,
                width=100,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="datetime_ordered",
                label="Date/Time Ordered",
                column_type=ColumnType.TEXT,
                width=120,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="eta",
                label="ETA",
                column_type=ColumnType.TEXT,
                width=80,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="arrived",
                label="Arrived",
                column_type=ColumnType.CHOICE,
                width=70,
                required=False,
                choices=["Yes", "No", ""],
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="notes",
                label="Notes (Location, Assignment, Status)",
                column_type=ColumnType.TEXT,
                width=200,
                required=False,
                default_value="",
                editable=True
            )
        ]
        
        # Create resource summary table field
        resource_table = TableFieldTemplate(
            field_id="resource_summary",
            label="Resource Summary",
            columns=resource_columns,
            min_rows=5,
            max_rows=self.max_resources_rows,
            allow_add=True,
            allow_remove=True,
            show_row_numbers=True,
            alternating_colors=True,
            single_selection=False,
            required=False
        )
        
        section = DefaultSectionTemplate(
            section_id="resources",
            title="RESOURCE SUMMARY",
            fields=[resource_table],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Summary of resources allocated to the incident"
        )
        
        return section
    
    def validate(self) -> bool:
        """Validate the ICS-201 form data.
        
        Returns:
            bool: True if the form is valid, False otherwise
        """
        try:
            # Get form data
            form_data = self.get_form_data()
            
            # Validate required fields
            situation_summary = form_data.get('sections', {}).get('situation_summary', {}).get('situation_summary', '').strip()
            if not situation_summary or len(situation_summary) < 20:
                return False
            
            objectives = form_data.get('sections', {}).get('objectives', {}).get('current_planned_objectives', '').strip()
            if not objectives or len(objectives) < 10:
                return False
            
            organization = form_data.get('sections', {}).get('organization', {}).get('current_organization', '').strip()
            if not organization or len(organization) < 15:
                return False
            
            # Validate that at least one action is provided
            actions = form_data.get('sections', {}).get('actions', {}).get('current_planned_actions', [])
            if not actions or not any(action.get('action_description', '').strip() for action in actions):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            form_data = self.get_form_data()
            
            # Check required fields
            situation_summary = form_data.get('sections', {}).get('situation_summary', {}).get('situation_summary', '').strip()
            if not situation_summary:
                errors.append("Situation summary is required for incident briefing")
            elif len(situation_summary) < 20:
                errors.append("Situation summary must be at least 20 characters long")
            
            objectives = form_data.get('sections', {}).get('objectives', {}).get('current_planned_objectives', '').strip()
            if not objectives:
                errors.append("Current and planned objectives are required")
            elif len(objectives) < 10:
                errors.append("Objectives must be at least 10 characters long")
            
            organization = form_data.get('sections', {}).get('organization', {}).get('current_organization', '').strip()
            if not organization:
                errors.append("Current organization structure is required")
            elif len(organization) < 15:
                errors.append("Organization must include at minimum the Incident Commander")
            
            # Check actions
            actions = form_data.get('sections', {}).get('actions', {}).get('current_planned_actions', [])
            if not actions or not any(action.get('action_description', '').strip() for action in actions):
                errors.append("At least one current or planned action must be specified")
            
            # Validate action times for chronological order
            valid_actions = [action for action in actions if action.get('action_description', '').strip()]
            if len(valid_actions) > 1:
                for i, action in enumerate(valid_actions[1:], 1):
                    prev_time = valid_actions[i-1].get('action_time', '').strip()
                    curr_time = action.get('action_time', '').strip()
                    if prev_time and curr_time:
                        # Simple validation - could be enhanced with proper time parsing
                        if prev_time > curr_time:
                            errors.append(f"Action times should be in chronological order (row {i} vs {i+1})")
                            break
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    # Required properties for integration testing
    
    @property
    def form_type(self) -> str:
        """Get the form type identifier."""
        return self.metadata.form_id
    
    @property
    def form_title(self) -> str:
        """Get the form title."""
        return self.metadata.name
    
    def get_default_data(self) -> Dict[str, Any]:
        """Get default data structure for the form."""
        return {
            'incident_name': '',
            'operational_period': '',
            'date_prepared': '',
            'prepared_by': '',
            'map_sketch': '',
            'situation_summary': '',
            'current_planned_objectives': '',
            'current_planned_actions': [],
            'current_organization': '',
            'resource_summary': []
        }
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set form data using simplified interface."""
        # Convert simple data format to full form data structure
        form_data = {
            'sections': {
                'header': {
                    'incident_name': data.get('incident_name', ''),
                    'operational_period': data.get('operational_period', ''),
                    'date_prepared': data.get('date_prepared', ''),
                    'prepared_by': data.get('prepared_by', '')
                },
                'map_sketch': {
                    'map_sketch': data.get('map_sketch', '')
                },
                'situation_summary': {
                    'situation_summary': data.get('situation_summary', '')
                },
                'objectives': {
                    'current_planned_objectives': data.get('current_planned_objectives', '')
                },
                'actions': {
                    'current_planned_actions': data.get('current_planned_actions', [])
                },
                'organization': {
                    'current_organization': data.get('current_organization', '')
                },
                'resources': {
                    'resource_summary': data.get('resource_summary', [])
                }
            }
        }
        self.set_form_data(form_data)
    
    def get_data(self) -> Dict[str, Any]:
        """Get form data using simplified interface."""
        form_data = self.get_form_data()
        sections = form_data.get('sections', {})
        
        # Extract data in simplified format
        header = sections.get('header', {})
        map_sketch = sections.get('map_sketch', {})
        situation_summary = sections.get('situation_summary', {})
        objectives = sections.get('objectives', {})
        actions = sections.get('actions', {})
        organization = sections.get('organization', {})
        resources = sections.get('resources', {})
        
        return {
            'incident_name': header.get('incident_name', ''),
            'operational_period': header.get('operational_period', ''),
            'date_prepared': header.get('date_prepared', ''),
            'prepared_by': header.get('prepared_by', ''),
            'map_sketch': map_sketch.get('map_sketch', ''),
            'situation_summary': situation_summary.get('situation_summary', ''),
            'current_planned_objectives': objectives.get('current_planned_objectives', ''),
            'current_planned_actions': actions.get('current_planned_actions', []),
            'current_organization': organization.get('current_organization', ''),
            'resource_summary': resources.get('resource_summary', [])
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export form data with metadata."""
        return {
            'metadata': {
                'form_type': self.form_type,
                'form_title': self.form_title,
                'version': self.metadata.version,
                'export_date': datetime.now().isoformat()
            },
            'form_data': self.get_data()
        }
    
    def import_data(self, export_data: Dict[str, Any]) -> bool:
        """Import form data from exported format."""
        try:
            if 'form_data' in export_data:
                self.set_data(export_data['form_data'])
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            return False