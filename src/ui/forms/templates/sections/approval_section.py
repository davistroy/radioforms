"""Approval section template for ICS forms.

This module provides the standard approval section used across all ICS forms
with signature lines and approval information.

Classes:
    ApprovalSectionTemplate: Standard ICS form approval section

Notes:
    The approval section follows FEMA ICS form standards for signature
    requirements and approval workflows.
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
    from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel, QFrame
    from PySide6.QtCore import Qt
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
    
    class QFrame:
        def __init__(self):
            pass
        
        def setFrameStyle(self, style):
            pass
        
        def setFixedHeight(self, height):
            pass
    
    class Qt:
        AlignCenter = "AlignCenter"
    
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class ApprovalSectionTemplate(SectionTemplate):
    """Standard approval section for ICS forms.
    
    Provides the standard approval information required by all ICS forms
    including prepared by, approved by signatures and date/time information.
    
    Attributes:
        include_approval: Whether to include approval signature line
        include_reviewed: Whether to include reviewed signature line
        signature_height: Height of signature lines in pixels
        form_type: Type of form for specific approval requirements
    
    Example:
        >>> approval = ApprovalSectionTemplate(
        ...     include_approval=True,
        ...     include_reviewed=False,
        ...     signature_height=50
        ... )
    """
    
    def __init__(self, **kwargs):
        """Initialize approval section with signature fields."""
        # Store configuration
        include_approval = kwargs.get('include_approval', True)
        include_reviewed = kwargs.get('include_reviewed', False)
        signature_height = kwargs.get('signature_height', 50)
        form_type = kwargs.get('form_type')
        
        # Create standard approval fields
        fields = [
            TextFieldTemplate(
                field_id="prepared_by_name",
                label="Prepared by (Name)",
                required=True,
                max_length=100,
                placeholder="Enter preparer name"
            ),
            TextFieldTemplate(
                field_id="prepared_by_position",
                label="Position/Title",
                required=False,
                max_length=100,
                placeholder="Enter position or title"
            ),
            TextFieldTemplate(
                field_id="prepared_by_signature",
                label="Signature",
                required=False,
                max_length=100,
                placeholder="Digital signature or initials"
            ),
            DateFieldTemplate(
                field_id="prepared_date",
                label="Date",
                required=True,
                current_section_date=True
            ),
            TimeFieldTemplate(
                field_id="prepared_time",
                label="Time",
                required=True,
                time_format="HH:mm"
            )
        ]
        
        # Add approval fields if included
        if include_approval:
            fields.extend([
                TextFieldTemplate(
                    field_id="approved_by_name",
                    label="Approved by (Name)",
                    required=False,
                    max_length=100,
                    placeholder="Enter approver name"
                ),
                TextFieldTemplate(
                    field_id="approved_by_position",
                    label="Position/Title",
                    required=False,
                    max_length=100,
                    placeholder="Enter position or title"
                ),
                TextFieldTemplate(
                    field_id="approved_by_signature",
                    label="Signature",
                    required=False,
                    max_length=100,
                    placeholder="Digital signature or initials"
                ),
                DateFieldTemplate(
                    field_id="approved_date",
                    label="Date",
                    required=False,
                    current_section_date=False
                ),
                TimeFieldTemplate(
                    field_id="approved_time",
                    label="Time",
                    required=False,
                    time_format="HH:mm"
                )
            ])
        
        # Add reviewed fields if included
        if include_reviewed:
            fields.extend([
                TextFieldTemplate(
                    field_id="reviewed_by_name",
                    label="Reviewed by (Name)",
                    required=False,
                    max_length=100,
                    placeholder="Enter reviewer name"
                ),
                TextFieldTemplate(
                    field_id="reviewed_by_position",
                    label="Position/Title",
                    required=False,
                    max_length=100,
                    placeholder="Enter position or title"
                ),
                TextFieldTemplate(
                    field_id="reviewed_by_signature",
                    label="Signature",
                    required=False,
                    max_length=100,
                    placeholder="Digital signature or initials"
                ),
                DateFieldTemplate(
                    field_id="reviewed_date",
                    label="Date",
                    required=False,
                    current_section_date=False
                ),
                TimeFieldTemplate(
                    field_id="reviewed_time",
                    label="Time",
                    required=False,
                    time_format="HH:mm"
                )
            ])
        
        # Initialize base section
        super().__init__(
            section_id="approval",
            title="APPROVAL & SIGNATURES",
            fields=fields,
            layout=LayoutType.GRID_LAYOUT
        )
        
        self.include_approval = include_approval
        self.include_reviewed = include_reviewed
        self.signature_height = signature_height
        self.form_type = form_type
    
    def create_section_widget(self) -> QGroupBox:
        """Create approval section widget with signature layout.
        
        Returns:
            QGroupBox: Approval section with signature grid layout
        """
        if not PYSIDE6_AVAILABLE:
            return QGroupBox(self.title)
        
        group_box = QGroupBox(self.title)
        layout = QGridLayout(group_box)
        
        # Create field widgets and arrange in grid
        row = 0
        
        # Prepared by section
        layout.addWidget(QLabel("PREPARED BY:"), row, 0, 1, 4)
        row += 1
        
        # Prepared by fields - name and position side by side
        prepared_name = self.get_field("prepared_by_name")
        prepared_position = self.get_field("prepared_by_position")
        if prepared_name and prepared_position:
            layout.addWidget(QLabel("Name:"), row, 0)
            layout.addWidget(prepared_name.create_widget(), row, 1)
            layout.addWidget(QLabel("Position/Title:"), row, 2)
            layout.addWidget(prepared_position.create_widget(), row, 3)
            row += 1
        
        # Prepared by signature line
        prepared_signature = self.get_field("prepared_by_signature")
        if prepared_signature:
            layout.addWidget(QLabel("Signature:"), row, 0)
            signature_widget = prepared_signature.create_widget()
            if PYSIDE6_AVAILABLE:
                signature_widget.setMinimumHeight(self.signature_height)
            layout.addWidget(signature_widget, row, 1)
            
            # Date and time for prepared by
            prepared_date = self.get_field("prepared_date")
            prepared_time = self.get_field("prepared_time")
            if prepared_date and prepared_time:
                layout.addWidget(QLabel("Date:"), row, 2)
                layout.addWidget(prepared_date.create_widget(), row, 3)
                row += 1
                layout.addWidget(QLabel("Time:"), row, 2)
                layout.addWidget(prepared_time.create_widget(), row, 3)
            row += 1
        
        # Add separator line
        if PYSIDE6_AVAILABLE:
            separator = QFrame()
            separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
            separator.setFixedHeight(2)
            layout.addWidget(separator, row, 0, 1, 4)
            row += 1
        
        # Approved by section (if included)
        if self.include_approval:
            layout.addWidget(QLabel("APPROVED BY:"), row, 0, 1, 4)
            row += 1
            
            # Approved by fields - name and position side by side
            approved_name = self.get_field("approved_by_name")
            approved_position = self.get_field("approved_by_position")
            if approved_name and approved_position:
                layout.addWidget(QLabel("Name:"), row, 0)
                layout.addWidget(approved_name.create_widget(), row, 1)
                layout.addWidget(QLabel("Position/Title:"), row, 2)
                layout.addWidget(approved_position.create_widget(), row, 3)
                row += 1
            
            # Approved by signature line
            approved_signature = self.get_field("approved_by_signature")
            if approved_signature:
                layout.addWidget(QLabel("Signature:"), row, 0)
                signature_widget = approved_signature.create_widget()
                if PYSIDE6_AVAILABLE:
                    signature_widget.setMinimumHeight(self.signature_height)
                layout.addWidget(signature_widget, row, 1)
                
                # Date and time for approved by
                approved_date = self.get_field("approved_date")
                approved_time = self.get_field("approved_time")
                if approved_date and approved_time:
                    layout.addWidget(QLabel("Date:"), row, 2)
                    layout.addWidget(approved_date.create_widget(), row, 3)
                    row += 1
                    layout.addWidget(QLabel("Time:"), row, 2)
                    layout.addWidget(approved_time.create_widget(), row, 3)
                row += 1
        
        # Reviewed by section (if included)
        if self.include_reviewed:
            if PYSIDE6_AVAILABLE:
                separator = QFrame()
                separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
                separator.setFixedHeight(2)
                layout.addWidget(separator, row, 0, 1, 4)
                row += 1
            
            layout.addWidget(QLabel("REVIEWED BY:"), row, 0, 1, 4)
            row += 1
            
            # Reviewed by fields - name and position side by side
            reviewed_name = self.get_field("reviewed_by_name")
            reviewed_position = self.get_field("reviewed_by_position")
            if reviewed_name and reviewed_position:
                layout.addWidget(QLabel("Name:"), row, 0)
                layout.addWidget(reviewed_name.create_widget(), row, 1)
                layout.addWidget(QLabel("Position/Title:"), row, 2)
                layout.addWidget(reviewed_position.create_widget(), row, 3)
                row += 1
            
            # Reviewed by signature line
            reviewed_signature = self.get_field("reviewed_by_signature")
            if reviewed_signature:
                layout.addWidget(QLabel("Signature:"), row, 0)
                signature_widget = reviewed_signature.create_widget()
                if PYSIDE6_AVAILABLE:
                    signature_widget.setMinimumHeight(self.signature_height)
                layout.addWidget(signature_widget, row, 1)
                
                # Date and time for reviewed by
                reviewed_date = self.get_field("reviewed_date")
                reviewed_time = self.get_field("reviewed_time")
                if reviewed_date and reviewed_time:
                    layout.addWidget(QLabel("Date:"), row, 2)
                    layout.addWidget(reviewed_date.create_widget(), row, 3)
                    row += 1
                    layout.addWidget(QLabel("Time:"), row, 2)
                    layout.addWidget(reviewed_time.create_widget(), row, 3)
        
        self.widget = group_box
        return group_box