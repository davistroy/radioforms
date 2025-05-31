"""ICS-202 Incident Objectives form template.

This module provides the complete ICS-202 Incident Objectives form
implementation using the RadioForms template system.

Classes:
    ICS202Template: Complete ICS-202 form for incident objectives management

Notes:
    ICS-202 is the cornerstone of the Incident Action Plan (IAP) and serves as
    the opening/cover page. It has 85% user demand and provides clear, concise
    incident objectives and command emphasis for operational periods.
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


class ICS202Template(FormTemplate):
    """ICS-202 Incident Objectives form template.
    
    Provides the complete ICS-202 form for incident objectives and command
    emphasis definition. This form serves as the cornerstone of the Incident
    Action Plan (IAP) and is used during each operational period.
    
    The form includes:
    - Standard ICS header with incident information and operational period
    - Incident objectives (clear, concise statements)
    - Operational period command emphasis
    - General situational awareness and safety information
    - Site safety plan requirements
    - Incident Action Plan components checklist
    - Prepared by and approved by sections
    
    Attributes:
        include_safety_plan: Whether to include site safety plan section
        max_objectives_length: Maximum length for objectives text
        
    Example:
        >>> form = ICS202Template(
        ...     include_safety_plan=True,
        ...     max_objectives_length=2000
        ... )
        >>> widget = form.create_form_widget()
    """
    
    def __init__(self, **kwargs):
        """Initialize ICS-202 form template with all sections and fields."""
        
        # Extract configuration parameters
        self.include_safety_plan = kwargs.get('include_safety_plan', True)
        self.max_objectives_length = kwargs.get('max_objectives_length', 2000)
        
        # Create form metadata
        metadata = FormMetadata(
            form_id="ics202",
            name="ICS 202 - INCIDENT OBJECTIVES",
            version="2020.1",
            description="Incident objectives and command emphasis for operational periods - cornerstone of the IAP",
            fema_compliant=True,
            tags=["objectives", "command", "iac", "planning", "operational_period"]
        )
        
        # Create form sections
        sections = self._create_form_sections(**kwargs)
        
        # Initialize base form template
        super().__init__(
            metadata=metadata,
            sections=sections,
            layout="vertical",
            scrollable=True,
            max_width=1000,
            max_height=800
        )
        
        logger.info(f"Initialized ICS-202 form template with {len(sections)} sections")
    
    def create_form_widget(self) -> QWidget:
        """Create the Qt widget for the complete ICS-202 form.
        
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
        """Create all sections for the ICS-202 form.
        
        Returns:
            List of form sections in display order
        """
        sections = []
        
        # 1. Header Section
        header_section = HeaderSectionTemplate(
            form_title="INCIDENT OBJECTIVES",
            form_number="ICS 202",
            include_form_number=True,
            include_page_info=True,
            page_prefix="IAP Page"
        )
        sections.append(header_section)
        
        # 2. Objectives Section
        objectives_section = self._create_objectives_section()
        sections.append(objectives_section)
        
        # 3. Command Emphasis Section
        command_section = self._create_command_emphasis_section()
        sections.append(command_section)
        
        # 4. Situational Awareness Section
        situational_section = self._create_situational_awareness_section()
        sections.append(situational_section)
        
        # 5. Safety Plan Section (if included)
        if self.include_safety_plan:
            safety_section = self._create_safety_plan_section()
            sections.append(safety_section)
        
        # 6. IAP Components Section
        iap_section = self._create_iap_components_section()
        sections.append(iap_section)
        
        # 7. Approval Section
        approval_section = ApprovalSectionTemplate(
            include_approval=True,
            include_reviewed=True,
            approval_title="Incident Commander/Unified Command",
            reviewed_title="Planning Section Chief",
            signature_height=60,
            form_type="ics202"
        )
        sections.append(approval_section)
        
        return sections
    
    def _create_objectives_section(self):
        """Create the incident objectives section.
        
        Returns:
            Section containing the objectives text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Objectives text area
        objectives_field = TextAreaFieldTemplate(
            field_id="objectives",
            label="Objective(s)",
            required=True,
            placeholder="Enter clear, concise statements of incident objectives...",
            max_length=self.max_objectives_length,
            min_rows=6,
            validation_rules=[
                {
                    "type": "required",
                    "message": "At least one objective must be provided"
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
            title="INCIDENT OBJECTIVES",
            fields=[objectives_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Clear, concise statements of what you want to accomplish during the operational period"
        )
        
        return section
    
    def _create_command_emphasis_section(self):
        """Create the operational period command emphasis section.
        
        Returns:
            Section containing the command emphasis text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Command emphasis text area
        emphasis_field = TextAreaFieldTemplate(
            field_id="command_emphasis",
            label="Command Emphasis",
            required=False,
            placeholder="Enter command emphasis and priorities for this operational period...",
            max_length=1500,
            min_rows=4,
            validation_rules=[]
        )
        
        section = DefaultSectionTemplate(
            section_id="command_emphasis",
            title="OPERATIONAL PERIOD COMMAND EMPHASIS",
            fields=[emphasis_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Command priorities and emphasis for this operational period"
        )
        
        return section
    
    def _create_situational_awareness_section(self):
        """Create the general situational awareness section.
        
        Returns:
            Section containing the situational awareness text area
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Situational awareness text area
        awareness_field = TextAreaFieldTemplate(
            field_id="general_situational_awareness",
            label="General Situational Awareness",
            required=False,
            placeholder="Enter weather forecast, incident conditions, or general safety message...",
            max_length=1000,
            min_rows=3,
            validation_rules=[]
        )
        
        section = DefaultSectionTemplate(
            section_id="situational_awareness",
            title="GENERAL SITUATIONAL AWARENESS",
            fields=[awareness_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Weather forecast, incident conditions, or general safety message"
        )
        
        return section
    
    def _create_safety_plan_section(self):
        """Create the site safety plan section.
        
        Returns:
            Section containing safety plan fields
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # Safety plan required checkbox - using text field as placeholder
        safety_required_field = TextFieldTemplate(
            field_id="site_safety_plan_required",
            label="Site Safety Plan Required (Yes/No)",
            required=True,
            placeholder="Yes or No",
            max_length=3,
            validation_rules=[
                {
                    "type": "choice",
                    "choices": ["Yes", "No"],
                    "message": "Must be either 'Yes' or 'No'"
                }
            ]
        )
        
        # Safety plan location
        safety_location_field = TextFieldTemplate(
            field_id="site_safety_plan_location",
            label="Approved Site Safety Plan(s) Located At",
            required=False,
            placeholder="Enter location of approved site safety plans...",
            max_length=200,
            validation_rules=[]
        )
        
        section = DefaultSectionTemplate(
            section_id="safety_plan",
            title="SITE SAFETY PLAN",
            fields=[safety_required_field, safety_location_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Site safety plan requirements and location"
        )
        
        return section
    
    def _create_iap_components_section(self):
        """Create the Incident Action Plan components section.
        
        Returns:
            Section containing IAP components checklist
        """
        from .base.section_template import DefaultSectionTemplate, LayoutType
        
        # IAP components as a text area with predefined options
        # In a real implementation, this would be checkboxes
        iap_components_field = TextAreaFieldTemplate(
            field_id="incident_action_plan_components",
            label="IAP Components (List included forms)",
            required=True,
            placeholder="List the ICS forms included in this IAP (e.g., ICS 203, ICS 204, ICS 205, etc.)",
            max_length=500,
            min_rows=4,
            validation_rules=[
                {
                    "type": "required",
                    "message": "At least one IAP component must be specified"
                }
            ]
        )
        
        section = DefaultSectionTemplate(
            section_id="iap_components",
            title="INCIDENT ACTION PLAN COMPONENTS",
            fields=[iap_components_field],
            layout=LayoutType.SINGLE_COLUMN,
            help_text="Check the ICS forms included in this Incident Action Plan"
        )
        
        return section
    
    def validate(self) -> bool:
        """Validate the ICS-202 form data.
        
        Returns:
            bool: True if the form is valid, False otherwise
        """
        try:
            # Get form data
            form_data = self.get_form_data()
            
            # Validate required fields
            objectives = form_data.get('sections', {}).get('objectives', {}).get('objectives', '').strip()
            if not objectives:
                return False
            
            iap_components = form_data.get('sections', {}).get('iap_components', {}).get('incident_action_plan_components', '').strip()
            if not iap_components:
                return False
            
            # Validate safety plan logic
            safety_plan_required = form_data.get('sections', {}).get('safety_plan', {}).get('site_safety_plan_required', '').strip().lower()
            safety_plan_location = form_data.get('sections', {}).get('safety_plan', {}).get('site_safety_plan_location', '').strip()
            
            if safety_plan_required == 'yes' and not safety_plan_location:
                logger.warning("Site safety plan required but location not specified")
                # Return False for strict validation, True for warning only
                return True  # Warning only per business rules
            
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
            objectives = form_data.get('sections', {}).get('objectives', {}).get('objectives', '').strip()
            if not objectives:
                errors.append("Incident objectives are required")
            elif len(objectives) < 10:
                errors.append("Objectives must be at least 10 characters long")
            
            iap_components = form_data.get('sections', {}).get('iap_components', {}).get('incident_action_plan_components', '').strip()
            if not iap_components:
                errors.append("At least one IAP component must be specified")
            
            # Check safety plan logic
            safety_plan_required = form_data.get('sections', {}).get('safety_plan', {}).get('site_safety_plan_required', '').strip().lower()
            safety_plan_location = form_data.get('sections', {}).get('safety_plan', {}).get('site_safety_plan_location', '').strip()
            
            if safety_plan_required == 'yes' and not safety_plan_location:
                errors.append("Site safety plan location must be specified when safety plan is required")
            
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
            'objectives': '',
            'command_emphasis': '',
            'general_situational_awareness': '',
            'site_safety_plan_required': 'No',
            'site_safety_plan_location': '',
            'incident_action_plan_components': ''
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
                'objectives': {
                    'objectives': data.get('objectives', '')
                },
                'command_emphasis': {
                    'command_emphasis': data.get('command_emphasis', '')
                },
                'situational_awareness': {
                    'general_situational_awareness': data.get('general_situational_awareness', '')
                },
                'safety_plan': {
                    'site_safety_plan_required': data.get('site_safety_plan_required', 'No'),
                    'site_safety_plan_location': data.get('site_safety_plan_location', '')
                },
                'iap_components': {
                    'incident_action_plan_components': data.get('incident_action_plan_components', '')
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
        objectives = sections.get('objectives', {})
        command_emphasis = sections.get('command_emphasis', {})
        situational_awareness = sections.get('situational_awareness', {})
        safety_plan = sections.get('safety_plan', {})
        iap_components = sections.get('iap_components', {})
        
        return {
            'incident_name': header.get('incident_name', ''),
            'operational_period': header.get('operational_period', ''),
            'date_prepared': header.get('date_prepared', ''),
            'prepared_by': header.get('prepared_by', ''),
            'objectives': objectives.get('objectives', ''),
            'command_emphasis': command_emphasis.get('command_emphasis', ''),
            'general_situational_awareness': situational_awareness.get('general_situational_awareness', ''),
            'site_safety_plan_required': safety_plan.get('site_safety_plan_required', 'No'),
            'site_safety_plan_location': safety_plan.get('site_safety_plan_location', ''),
            'incident_action_plan_components': iap_components.get('incident_action_plan_components', '')
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