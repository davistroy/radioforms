"""ICS-205 Radio Communications Plan form template.

This module provides the complete ICS-205 Radio Communications Plan form
implementation using the RadioForms template system.

Classes:
    ICS205Template: Complete ICS-205 form with radio frequency management

Notes:
    ICS-205 is the highest priority form (92% user demand) and provides
    comprehensive radio frequency assignment and communication planning.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import base classes
from .base.form_template import FormTemplate, FormMetadata
from .sections.header_section import HeaderSectionTemplate
from .sections.approval_section import ApprovalSectionTemplate
from .fields.table_field import TableFieldTemplate, TableColumn, ColumnType
from .fields.text_field import TextFieldTemplate, TextAreaFieldTemplate

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
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
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class ICS205Template(FormTemplate):
    """ICS-205 Radio Communications Plan form template.
    
    Provides the complete ICS-205 form for radio frequency assignment and
    communication planning in emergency operations. This form is the highest
    priority based on user demand analysis (92% usage).
    
    The form includes:
    - Standard ICS header with incident information
    - Radio frequency assignment table with zones/groups
    - Communication instructions and special procedures
    - Standard approval section with signatures
    
    Attributes:
        min_frequency_rows: Minimum number of frequency assignment rows
        max_frequency_rows: Maximum number of frequency assignment rows
        include_special_instructions: Whether to include special instructions section
    
    Example:
        >>> form = ICS205Template(
        ...     min_frequency_rows=10,
        ...     max_frequency_rows=50,
        ...     include_special_instructions=True
        ... )
        >>> widget = form.create_form_widget()
    """
    
    def __init__(self, **kwargs):
        """Initialize ICS-205 form template with all sections and fields."""
        
        # Extract configuration parameters
        self.min_frequency_rows = kwargs.get('min_frequency_rows', 10)
        self.max_frequency_rows = kwargs.get('max_frequency_rows', 50)
        self.include_special_instructions = kwargs.get('include_special_instructions', True)
        
        # Create form metadata
        metadata = FormMetadata(
            form_id="ics205",
            name="ICS 205 - INCIDENT RADIO COMMUNICATIONS PLAN",
            version="2020.1",
            description="Radio frequency assignment and communication planning for emergency operations",
            fema_compliant=True,
            tags=["radio", "communications", "frequency", "planning"]
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
            max_height=800
        )
        
        logger.info(f"Initialized ICS-205 form template with {len(sections)} sections")
    
    def create_form_widget(self) -> QWidget:
        """Create the Qt widget for the complete ICS-205 form.
        
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
        """Create all sections for the ICS-205 form.
        
        Returns:
            List of form sections in display order
        """
        sections = []
        
        # 1. Header Section
        header_section = HeaderSectionTemplate(
            form_title="INCIDENT RADIO COMMUNICATIONS PLAN",
            form_number="ICS 205",
            include_form_number=True,
            include_page_info=True
        )
        sections.append(header_section)
        
        # 2. Radio Frequency Assignment Section
        frequency_section = self._create_frequency_section()
        sections.append(frequency_section)
        
        # 3. Special Instructions Section (if included)
        if self.include_special_instructions:
            instructions_section = self._create_instructions_section()
            sections.append(instructions_section)
        
        # 4. Approval Section
        approval_section = ApprovalSectionTemplate(
            include_approval=True,
            include_reviewed=False,
            signature_height=60,
            form_type="ics205"
        )
        sections.append(approval_section)
        
        return sections
    
    def _create_frequency_section(self):
        """Create the radio frequency assignment table section.
        
        Returns:
            Section containing the frequency assignment table
        """
        from .base.section_template import SectionTemplate, LayoutType
        
        # Define frequency table columns based on ICS-205 requirements
        frequency_columns = [
            TableColumn(
                column_id="zone_group",
                label="Zone/Group",
                column_type=ColumnType.TEXT,
                width=120,
                required=True,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="channel",
                label="Channel #/Name",
                column_type=ColumnType.TEXT,
                width=100,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="function",
                label="Function",
                column_type=ColumnType.CHOICE,
                width=120,
                required=True,
                choices=[
                    "Command",
                    "Tactical",
                    "Support",
                    "Ground to Air",
                    "Air to Air",
                    "Medical",
                    "Logistics"
                ],
                default_value="Command",
                editable=True
            ),
            TableColumn(
                column_id="assignment",
                label="Assignment",
                column_type=ColumnType.TEXT,
                width=150,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="rx_freq_mhz",
                label="RX Freq (MHz)",
                column_type=ColumnType.TEXT,
                width=110,
                required=True,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="rx_tone",
                label="RX Tone/NAC",
                column_type=ColumnType.TEXT,
                width=100,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="tx_freq_mhz",
                label="TX Freq (MHz)",
                column_type=ColumnType.TEXT,
                width=110,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="tx_tone",
                label="TX Tone/NAC",
                column_type=ColumnType.TEXT,
                width=100,
                required=False,
                default_value="",
                editable=True
            ),
            TableColumn(
                column_id="mode",
                label="Mode (A,D,M)",
                column_type=ColumnType.CHOICE,
                width=90,
                required=False,
                choices=["A", "D", "M", "AM", "FM", "P25"],
                default_value="A",
                editable=True
            ),
            TableColumn(
                column_id="remarks",
                label="Remarks",
                column_type=ColumnType.TEXT,
                width=200,
                required=False,
                default_value="",
                editable=True
            )
        ]
        
        # Create frequency assignment table field
        frequency_table = TableFieldTemplate(
            field_id="frequency_assignments",
            label="Radio Frequency Assignments",
            columns=frequency_columns,
            min_rows=self.min_frequency_rows,
            max_rows=self.max_frequency_rows,
            allow_add=True,
            allow_remove=True,
            show_row_numbers=True,
            alternating_colors=True,
            single_selection=False,
            required=True
        )
        
        # Create section containing the frequency table
        from .base.section_template import DefaultSectionTemplate
        frequency_section = DefaultSectionTemplate(
            section_id="frequency_assignments",
            title="RADIO FREQUENCY ASSIGNMENTS",
            fields=[frequency_table],
            layout=LayoutType.SINGLE_COLUMN
        )
        
        return frequency_section
    
    def _create_instructions_section(self):
        """Create the special instructions section.
        
        Returns:
            Section containing special instructions fields
        """
        from .base.section_template import SectionTemplate, LayoutType
        
        # Create instruction fields
        instruction_fields = [
            TextAreaFieldTemplate(
                field_id="communication_procedures",
                label="Communication Procedures",
                placeholder="Enter standard communication procedures and protocols...",
                max_length=2000,
                min_rows=4,
                required=False
            ),
            TextAreaFieldTemplate(
                field_id="special_instructions",
                label="Special Instructions",
                placeholder="Enter any special instructions or emergency procedures...",
                max_length=2000,
                min_rows=4,
                required=False
            ),
            TextFieldTemplate(
                field_id="repeater_info",
                label="Repeater/System Information",
                placeholder="Enter repeater locations, system details...",
                max_length=500,
                required=False
            ),
            TextAreaFieldTemplate(
                field_id="backup_procedures",
                label="Backup Communication Procedures",
                placeholder="Enter backup communication methods and procedures...",
                max_length=1500,
                min_rows=3,
                required=False
            )
        ]
        
        # Create instructions section
        from .base.section_template import DefaultSectionTemplate
        instructions_section = DefaultSectionTemplate(
            section_id="special_instructions",
            title="COMMUNICATION INSTRUCTIONS & PROCEDURES",
            fields=instruction_fields,
            layout=LayoutType.SINGLE_COLUMN
        )
        
        return instructions_section
    
    def validate_form_ics205(self) -> Dict[str, Any]:
        """Validate the complete ICS-205 form.
        
        Returns:
            Dict containing validation results with success/error details
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sections_validated": 0
        }
        
        try:
            # Validate all sections using base form validation
            base_result = super().validate_form()
            validation_result["sections_validated"] = len(self.sections)
            
            if not base_result.is_valid:
                validation_result["is_valid"] = False
                validation_result["errors"].append(base_result.message)
            
            # Additional ICS-205 specific validation
            frequency_data = self.get_field_value("frequency_assignments", "frequency_assignments")
            if frequency_data:
                # Validate frequency assignments
                freq_errors = self._validate_frequency_assignments(frequency_data)
                if freq_errors:
                    validation_result["errors"].extend(freq_errors)
                    validation_result["is_valid"] = False
                
                # Check for duplicate frequencies
                duplicate_warnings = self._check_duplicate_frequencies(frequency_data)
                if duplicate_warnings:
                    validation_result["warnings"].extend(duplicate_warnings)
            
            # Validate required fields for operational use
            required_fields = [
                ("header", "incident_name"), 
                ("header", "operational_period"), 
                ("header", "date_prepared"), 
                ("approval", "prepared_by_name")
            ]
            for section_id, field_id in required_fields:
                value = self.get_field_value(section_id, field_id)
                if not value or (isinstance(value, str) and not value.strip()):
                    validation_result["errors"].append(f"Required field '{field_id}' is missing")
                    validation_result["is_valid"] = False
            
            logger.debug(f"ICS-205 validation completed: {validation_result['is_valid']}")
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            logger.error(f"ICS-205 validation failed: {e}")
        
        return validation_result
    
    def _validate_frequency_assignments(self, frequency_data: List[Dict[str, Any]]) -> List[str]:
        """Validate radio frequency assignment data.
        
        Args:
            frequency_data: List of frequency assignment dictionaries
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for idx, assignment in enumerate(frequency_data):
            row_num = idx + 1
            
            # Validate required frequency field
            if not assignment.get("rx_freq_mhz"):
                errors.append(f"Row {row_num}: RX Frequency is required")
            
            # Validate frequency format (basic check)
            rx_freq = assignment.get("rx_freq_mhz", "")
            if rx_freq:
                try:
                    freq_val = float(rx_freq)
                    if freq_val < 30.0 or freq_val > 1000.0:  # Reasonable frequency range
                        errors.append(f"Row {row_num}: RX Frequency {freq_val} MHz is outside normal range (30-1000 MHz)")
                except ValueError:
                    errors.append(f"Row {row_num}: RX Frequency '{rx_freq}' is not a valid number")
            
            # Validate zone/group field
            if not assignment.get("zone_group"):
                errors.append(f"Row {row_num}: Zone/Group is required")
            
            # Validate function field
            if not assignment.get("function"):
                errors.append(f"Row {row_num}: Function is required")
        
        return errors
    
    def _check_duplicate_frequencies(self, frequency_data: List[Dict[str, Any]]) -> List[str]:
        """Check for duplicate frequency assignments.
        
        Args:
            frequency_data: List of frequency assignment dictionaries
            
        Returns:
            List of warning messages about duplicates
        """
        warnings = []
        seen_frequencies = {}
        
        for idx, assignment in enumerate(frequency_data):
            rx_freq = assignment.get("rx_freq_mhz", "").strip()
            if rx_freq:
                if rx_freq in seen_frequencies:
                    prev_row = seen_frequencies[rx_freq]
                    warnings.append(f"Duplicate RX frequency {rx_freq} MHz found in rows {prev_row} and {idx + 1}")
                else:
                    seen_frequencies[rx_freq] = idx + 1
        
        return warnings
    
    def validate(self) -> bool:
        """Validate the ICS-205 form data.
        
        Returns:
            bool: True if the form is valid, False otherwise
        """
        try:
            validation_result = self.validate_form_ics205()
            return validation_result.get("is_valid", False)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export ICS-205 form data to dictionary format.
        
        Returns:
            Dict containing complete form data with metadata
        """
        form_data = super().to_dict()
        
        # Add ICS-205 specific metadata
        form_data.update({
            "form_type": "ics205",
            "form_version": "2020.1",
            "form_description": "Incident Radio Communications Plan",
            "frequency_assignment_count": len(self.get_field_value("frequency_assignments", "frequency_assignments") or []),
            "template_config": {
                "min_frequency_rows": self.min_frequency_rows,
                "max_frequency_rows": self.max_frequency_rows,
                "include_special_instructions": self.include_special_instructions
            }
        })
        
        return form_data
    
    @classmethod
    def create_from_dict(cls, form_data: Dict[str, Any]) -> 'ICS205Template':
        """Create ICS-205 form from dictionary data.
        
        Args:
            form_data: Dictionary containing form data
            
        Returns:
            ICS205Template instance with populated data
        """
        # Extract template configuration
        config = form_data.get("template_config", {})
        
        # Create form instance
        form = cls(
            min_frequency_rows=config.get("min_frequency_rows", 10),
            max_frequency_rows=config.get("max_frequency_rows", 50),
            include_special_instructions=config.get("include_special_instructions", True)
        )
        
        # Populate form data
        if "form_data" in form_data:
            form.set_form_data(form_data["form_data"])
        
        logger.info(f"Created ICS-205 form from dictionary data")
        return form
    
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
            'frequency_assignments': [],
            'communication_procedures': '',
            'special_instructions': '',
            'repeater_info': '',
            'backup_procedures': ''
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
                'frequency_assignments': {
                    'frequency_assignments': data.get('frequency_assignments', [])
                },
                'special_instructions': {
                    'communication_procedures': data.get('communication_procedures', ''),
                    'special_instructions': data.get('special_instructions', ''),
                    'repeater_info': data.get('repeater_info', ''),
                    'backup_procedures': data.get('backup_procedures', '')
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
        freq_section = sections.get('frequency_assignments', {})
        instructions = sections.get('special_instructions', {})
        
        return {
            'incident_name': header.get('incident_name', ''),
            'operational_period': header.get('operational_period', ''),
            'date_prepared': header.get('date_prepared', ''),
            'prepared_by': header.get('prepared_by', ''),
            'frequency_assignments': freq_section.get('frequency_assignments', []),
            'communication_procedures': instructions.get('communication_procedures', ''),
            'special_instructions': instructions.get('special_instructions', ''),
            'repeater_info': instructions.get('repeater_info', ''),
            'backup_procedures': instructions.get('backup_procedures', '')
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