"""Standard header section template for ICS forms.

This module provides the standard header section used across all ICS forms
with incident information, operational period, and form metadata.

Classes:
    HeaderSectionTemplate: Standard ICS form header

Notes:
    The header section follows FEMA ICS form standards while providing
    flexibility for different form types.
"""

from dataclasses import dataclass
from typing import Optional
import logging

# Import base classes and field templates
from ..base.section_template import SectionTemplate, LayoutType
from ..fields.text_field import TextFieldTemplate
from ..fields.date_field import DateFieldTemplate, TimeFieldTemplate

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QGroupBox:
        def __init__(self, title=""):
            self._title = title
        
        def setTitle(self, title):
            self._title = title
    
    class QGridLayout:
        def __init__(self, parent=None):
            pass
        
        def addWidget(self, widget, row, col, row_span=1, col_span=1):
            pass
    
    class QLabel:
        def __init__(self, text=""):
            self._text = text
    
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class HeaderSectionTemplate(SectionTemplate):
    """Standard header section for ICS forms.
    
    Provides the standard header information required by all ICS forms
    including incident name, operational period, and form metadata.
    
    Attributes:
        include_form_number: Whether to include form number field
        include_page_info: Whether to include page number fields
        form_title: Title to display in header (e.g., "INCIDENT RADIO COMMUNICATIONS PLAN")
        form_number: Form number (e.g., "ICS 205")
    
    Example:
        >>> header = HeaderSectionTemplate(
        ...     form_title="INCIDENT RADIO COMMUNICATIONS PLAN",
        ...     form_number="ICS 205",
        ...     include_form_number=True
        ... )
    """
    
    def __init__(self, form_title: str, form_number: str, **kwargs):
        """Initialize header section with form-specific information."""
        # Store configuration
        include_form_number = kwargs.get('include_form_number', True)
        include_page_info = kwargs.get('include_page_info', False)
        
        # Create standard header fields
        fields = [
            TextFieldTemplate(
                field_id="incident_name",
                label="1. Incident Name",
                required=True,
                max_length=100,
                placeholder="Enter incident name"
            ),
            TextFieldTemplate(
                field_id="operational_period",
                label="2. Operational Period",
                required=True,
                max_length=50,
                placeholder="Date/Time From - To"
            ),
            DateFieldTemplate(
                field_id="date_prepared",
                label="3. Date Prepared",
                required=True,
                current_section_date=True
            ),
            TimeFieldTemplate(
                field_id="time_prepared",
                label="4. Time Prepared",
                required=True,
                time_format="HH:mm"
            )
        ]
        
        # Add form number field if included
        if include_form_number:
            fields.insert(0, TextFieldTemplate(
                field_id="form_number",
                label="Form Number",
                default_value=form_number,
                max_length=20,
                read_only=True
            ))
        
        # Add page info fields if included
        if include_page_info:
            fields.extend([
                TextFieldTemplate(
                    field_id="page_number",
                    label="Page",
                    default_value="1",
                    max_length=5
                ),
                TextFieldTemplate(
                    field_id="total_pages",
                    label="of",
                    default_value="1",
                    max_length=5
                )
            ])
        
        # Initialize base section
        super().__init__(
            section_id="header",
            title=form_title,
            fields=fields,
            layout=LayoutType.GRID_LAYOUT
        )
        
        self.form_title = form_title
        self.form_number = form_number
        self.include_form_number = include_form_number
        self.include_page_info = include_page_info
    
    def create_section_widget(self) -> QGroupBox:
        """Create header section widget with ICS-standard layout.
        
        Returns:
            QGroupBox: Header section with grid layout
        """
        if not PYSIDE6_AVAILABLE:
            return QGroupBox(self.title)
        
        group_box = QGroupBox(self.title)
        layout = QGridLayout(group_box)
        
        # Create field widgets and arrange in grid
        row = 0
        
        # Form number (if included) - spans full width
        if self.include_form_number:
            form_number_field = self.get_field("form_number")
            if form_number_field:
                layout.addWidget(QLabel("Form:"), row, 0)
                layout.addWidget(form_number_field.create_widget(), row, 1, 1, 3)
                row += 1
        
        # Incident name - spans most of width
        incident_field = self.get_field("incident_name")
        if incident_field:
            layout.addWidget(QLabel("1. Incident Name:"), row, 0)
            layout.addWidget(incident_field.create_widget(), row, 1, 1, 3)
            row += 1
        
        # Operational period - spans most of width
        op_period_field = self.get_field("operational_period")
        if op_period_field:
            layout.addWidget(QLabel("2. Operational Period:"), row, 0)
            layout.addWidget(op_period_field.create_widget(), row, 1, 1, 3)
            row += 1
        
        # Date and time prepared - side by side
        date_field = self.get_field("date_prepared")
        time_field = self.get_field("time_prepared")
        if date_field and time_field:
            layout.addWidget(QLabel("3. Date Prepared:"), row, 0)
            layout.addWidget(date_field.create_widget(), row, 1)
            layout.addWidget(QLabel("4. Time Prepared:"), row, 2)
            layout.addWidget(time_field.create_widget(), row, 3)
            row += 1
        
        # Page info (if included) - side by side
        if self.include_page_info:
            page_field = self.get_field("page_number")
            total_field = self.get_field("total_pages")
            if page_field and total_field:
                layout.addWidget(QLabel("Page:"), row, 0)
                layout.addWidget(page_field.create_widget(), row, 1)
                layout.addWidget(QLabel("of:"), row, 2)
                layout.addWidget(total_field.create_widget(), row, 3)
        
        self.widget = group_box
        return group_box