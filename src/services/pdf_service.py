"""PDF generation service for ICS forms.

This module provides PDF generation capabilities for ICS forms using ReportLab,
following FEMA-style formatting and ensuring professional appearance for
print-ready output. Supports both ICS-213 and ICS-214 forms with proper
page layouts, headers, and consistent styling.

The service follows CLAUDE.md principles:
- Simple and focused implementation
- Clear error handling
- Professional output quality
- Extensible design for future forms

Example:
    >>> from src.forms.ics213 import ICS213Form
    >>> from src.services.pdf_service import PDFService
    >>> 
    >>> # Generate PDF for ICS-213 form
    >>> form = ICS213Form()
    >>> # ... populate form data ...
    >>> 
    >>> pdf_service = PDFService()
    >>> pdf_path = pdf_service.generate_pdf(form, "/path/to/output.pdf")
    >>> print(f"PDF generated: {pdf_path}")

Classes:
    PDFService: Main service for generating PDF documents from ICS forms
    FormPDFGenerator: Base class for form-specific PDF generators
    ICS213PDFGenerator: PDF generator specifically for ICS-213 forms
    ICS214PDFGenerator: PDF generator specifically for ICS-214 forms

Functions:
    create_pdf_service: Factory function for creating PDF service instances
    generate_form_pdf: Convenience function for generating PDFs from forms

Notes:
    This implementation uses ReportLab for PDF generation and follows FEMA
    form layouts with professional styling suitable for emergency management
    documentation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Tuple
from abc import ABC, abstractmethod

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Frame, PageTemplate, BaseDocTemplate
    )
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    REPORTLAB_ERROR = str(e)
    
    # Create dummy classes for type hints when ReportLab isn't available
    class DummyClass:
        pass
    
    colors = DummyClass()
    letter = (612, 792)
    A4 = (595, 842)
    inch = 72
    mm = 2.834645669
    Paragraph = Table = TableStyle = Spacer = SimpleDocTemplate = DummyClass

# Import form models
try:
    from ..forms.ics213 import ICS213Form
    from ..models.ics214 import ICS214Form
    from ..models.base_form import BaseForm, FormType
except ImportError:
    # For standalone testing
    try:
        from forms.ics213 import ICS213Form
        from models.ics214 import ICS214Form
        from models.base_form import BaseForm, FormType
    except ImportError:
        import sys
        sys.path.append('.')
        from src.forms.ics213 import ICS213Form
        from src.models.ics214 import ICS214Form
        from src.models.base_form import BaseForm, FormType


logger = logging.getLogger(__name__)


class PDFGenerationError(Exception):
    """Raised when PDF generation fails."""
    pass


class FormPDFGenerator(ABC):
    """Abstract base class for form-specific PDF generators.
    
    This class defines the interface that all form PDF generators must implement.
    Each form type (ICS-213, ICS-214, etc.) should have its own concrete
    implementation that handles the specific layout and content requirements.
    
    Attributes:
        styles (Dict[str, ParagraphStyle]): ReportLab paragraph styles for formatting.
        page_width (float): Page width in points.
        page_height (float): Page height in points.
        margin (float): Page margin in points.
        
    Methods:
        generate: Generate PDF for the specific form type.
        _create_header: Create form header section.
        _create_content: Create form content section.
        _create_footer: Create form footer section.
    """
    
    def __init__(self, page_size: Tuple[float, float] = letter):
        """Initialize PDF generator with page configuration.
        
        Args:
            page_size: Page size tuple (width, height) in points.
        """
        self.page_width, self.page_height = page_size
        self.margin = 0.75 * inch
        self.content_width = self.page_width - (2 * self.margin)
        
        # Initialize styles
        self.styles = self._create_styles()
        
        logger.debug(f"PDF generator initialized with page size {page_size}")
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create and return paragraph styles for PDF formatting.
        
        Returns:
            Dict[str, ParagraphStyle]: Dictionary of named paragraph styles.
        """
        # Get base styles
        base_styles = getSampleStyleSheet()
        
        # Create custom styles
        styles = {
            'title': ParagraphStyle(
                'FormTitle',
                parent=base_styles['Title'],
                fontSize=16,
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            'heading': ParagraphStyle(
                'FormHeading',
                parent=base_styles['Heading1'],
                fontSize=12,
                spaceAfter=6,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ),
            'label': ParagraphStyle(
                'FieldLabel',
                parent=base_styles['Normal'],
                fontSize=9,
                spaceAfter=2,
                fontName='Helvetica-Bold'
            ),
            'value': ParagraphStyle(
                'FieldValue',
                parent=base_styles['Normal'],
                fontSize=10,
                spaceAfter=8,
                fontName='Helvetica'
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=base_styles['Normal'],
                fontSize=10,
                fontName='Helvetica'
            ),
            'small': ParagraphStyle(
                'Small',
                parent=base_styles['Normal'],
                fontSize=8,
                fontName='Helvetica'
            ),
            'footer': ParagraphStyle(
                'Footer',
                parent=base_styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        }
        
        return styles
    
    @abstractmethod
    def generate(self, form: BaseForm, output_path: Union[str, Path]) -> Path:
        """Generate PDF for the given form.
        
        Args:
            form: Form instance to generate PDF for.
            output_path: Path where PDF should be saved.
            
        Returns:
            Path: Path to the generated PDF file.
            
        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        pass
    
    @abstractmethod
    def _create_header(self, form: BaseForm) -> List[Any]:
        """Create header section elements for the form.
        
        Args:
            form: Form instance to create header for.
            
        Returns:
            List[Any]: List of ReportLab flowables for the header.
        """
        pass
    
    @abstractmethod
    def _create_content(self, form: BaseForm) -> List[Any]:
        """Create content section elements for the form.
        
        Args:
            form: Form instance to create content for.
            
        Returns:
            List[Any]: List of ReportLab flowables for the content.
        """
        pass
    
    @abstractmethod
    def _create_footer(self, form: BaseForm) -> List[Any]:
        """Create footer section elements for the form.
        
        Args:
            form: Form instance to create footer for.
            
        Returns:
            List[Any]: List of ReportLab flowables for the footer.
        """
        pass
    
    def _create_field_table(self, fields: List[Tuple[str, str]], 
                           num_columns: int = 2) -> Table:
        """Create a table for displaying form fields.
        
        Args:
            fields: List of (label, value) tuples.
            num_columns: Number of columns in the table.
            
        Returns:
            Table: ReportLab table with formatted fields.
        """
        if not fields:
            return Table([])
        
        # Create table data
        table_data = []
        for i in range(0, len(fields), num_columns):
            row = []
            for j in range(num_columns):
                if i + j < len(fields):
                    label, value = fields[i + j]
                    # Create label/value pair
                    cell_content = [
                        Paragraph(f"<b>{label}:</b>", self.styles['label']),
                        Paragraph(value or "", self.styles['value'])
                    ]
                    row.append(cell_content)
                else:
                    row.append("")
            table_data.append(row)
        
        # Calculate column widths
        col_width = self.content_width / num_columns
        col_widths = [col_width] * num_columns
        
        # Create and style table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return table


class ICS213PDFGenerator(FormPDFGenerator):
    """PDF generator for ICS-213 General Message forms.
    
    Generates professional PDF output for ICS-213 forms following FEMA layout
    standards. Includes proper header information, message content, and
    approval/reply sections with clear visual organization.
    """
    
    def generate(self, form: ICS213Form, output_path: Union[str, Path]) -> Path:
        """Generate PDF for ICS-213 form.
        
        Args:
            form: ICS-213 form instance to generate PDF for.
            output_path: Path where PDF should be saved.
            
        Returns:
            Path: Path to the generated PDF file.
            
        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        try:
            output_path = Path(output_path)
            
            # Create document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build content
            story = []
            story.extend(self._create_header(form))
            story.extend(self._create_content(form))
            story.extend(self._create_footer(form))
            
            # Generate PDF
            doc.build(story)
            
            logger.info(f"ICS-213 PDF generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate ICS-213 PDF: {e}")
            raise PDFGenerationError(f"PDF generation failed: {e}") from e
    
    def _create_header(self, form: ICS213Form) -> List[Any]:
        """Create header section for ICS-213 form.
        
        Args:
            form: ICS-213 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the header.
        """
        elements = []
        
        # Form title
        title = Paragraph("GENERAL MESSAGE (ICS 213)", self.styles['title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Header fields
        header_fields = [
            ("Incident Name", form.data.incident_name),
            ("Date", form.data.date),
            ("Time", form.data.time),
            ("Message No.", "")  # Could be added to form data later
        ]
        
        header_table = self._create_field_table(header_fields, num_columns=2)
        elements.append(header_table)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_content(self, form: ICS213Form) -> List[Any]:
        """Create content section for ICS-213 form.
        
        Args:
            form: ICS-213 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the content.
        """
        elements = []
        
        # To/From section
        to_from_fields = [
            ("TO (Name and Position)", form.data.to.display_name),
            ("FROM (Name and Position)", form.data.from_person.display_name)
        ]
        
        to_from_table = self._create_field_table(to_from_fields, num_columns=1)
        elements.append(to_from_table)
        elements.append(Spacer(1, 12))
        
        # Subject
        elements.append(Paragraph("<b>SUBJECT:</b>", self.styles['label']))
        elements.append(Paragraph(form.data.subject, self.styles['value']))
        elements.append(Spacer(1, 12))
        
        # Message content
        elements.append(Paragraph("<b>MESSAGE:</b>", self.styles['label']))
        message_style = ParagraphStyle(
            'MessageContent',
            parent=self.styles['value'],
            leftIndent=12,
            rightIndent=12,
            spaceBefore=6,
            spaceAfter=12,
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=8
        )
        elements.append(Paragraph(form.data.message, message_style))
        elements.append(Spacer(1, 12))
        
        # Approval section
        if form.data.approved_by.name or form.data.approved_by.position:
            elements.append(Paragraph("<b>APPROVED BY:</b>", self.styles['heading']))
            approval_fields = [
                ("Name", form.data.approved_by.name),
                ("Position", form.data.approved_by.position),
                ("Signature", form.data.approved_by.signature),
                ("Date/Time", "")  # Could be approval timestamp
            ]
            approval_table = self._create_field_table(approval_fields, num_columns=2)
            elements.append(approval_table)
            elements.append(Spacer(1, 12))
        
        # Reply section
        if form.data.reply:
            elements.append(Paragraph("<b>REPLY:</b>", self.styles['heading']))
            elements.append(Paragraph(form.data.reply, message_style))
            elements.append(Spacer(1, 8))
            
            reply_fields = [
                ("Replied by", form.data.replied_by.display_name),
                ("Position", form.data.replied_by.position),
                ("Date/Time", form.data.reply_date_time)
            ]
            reply_table = self._create_field_table(reply_fields, num_columns=1)
            elements.append(reply_table)
        
        return elements
    
    def _create_footer(self, form: ICS213Form) -> List[Any]:
        """Create footer section for ICS-213 form.
        
        Args:
            form: ICS-213 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the footer.
        """
        elements = []
        
        # Add some space before footer
        elements.append(Spacer(1, 24))
        
        # Form information
        footer_text = f"ICS 213 - Generated by RadioForms on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        elements.append(Paragraph(footer_text, self.styles['footer']))
        
        return elements


class ICS214PDFGenerator(FormPDFGenerator):
    """PDF generator for ICS-214 Activity Log forms.
    
    Generates professional PDF output for ICS-214 forms with activity tables,
    resource assignments, and proper FEMA layout formatting.
    """
    
    def generate(self, form: ICS214Form, output_path: Union[str, Path]) -> Path:
        """Generate PDF for ICS-214 form.
        
        Args:
            form: ICS-214 form instance to generate PDF for.
            output_path: Path where PDF should be saved.
            
        Returns:
            Path: Path to the generated PDF file.
            
        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        try:
            output_path = Path(output_path)
            
            # Create document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build content
            story = []
            story.extend(self._create_header(form))
            story.extend(self._create_content(form))
            story.extend(self._create_footer(form))
            
            # Generate PDF
            doc.build(story)
            
            logger.info(f"ICS-214 PDF generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate ICS-214 PDF: {e}")
            raise PDFGenerationError(f"PDF generation failed: {e}") from e
    
    def _create_header(self, form: ICS214Form) -> List[Any]:
        """Create header section for ICS-214 form.
        
        Args:
            form: ICS-214 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the header.
        """
        elements = []
        
        # Form title
        title = Paragraph("ACTIVITY LOG (ICS 214)", self.styles['title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Header fields
        header_fields = [
            ("Incident Name", form.data.incident_name),
            ("Operational Period", f"{form.data.operational_period.from_date} to {form.data.operational_period.to_date}"),
            ("Name", form.data.name),
            ("ICS Position", form.data.ics_position),
            ("Home Agency", form.data.home_agency),
            ("Prepared by", form.data.prepared_by.display_name if form.data.prepared_by else "")
        ]
        
        header_table = self._create_field_table(header_fields, num_columns=2)
        elements.append(header_table)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_content(self, form: ICS214Form) -> List[Any]:
        """Create content section for ICS-214 form.
        
        Args:
            form: ICS-214 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the content.
        """
        elements = []
        
        # Resources assigned section
        if form.data.resources_assigned:
            elements.append(Paragraph("<b>RESOURCES ASSIGNED:</b>", self.styles['heading']))
            
            # Create resources table
            resource_data = [["Name", "ICS Position", "Home Agency"]]
            for resource in form.data.resources_assigned:
                resource_data.append([
                    resource.name,
                    resource.ics_position,
                    resource.home_agency
                ])
            
            resource_table = Table(resource_data, colWidths=[2*inch, 2*inch, 2.5*inch])
            resource_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elements.append(resource_table)
            elements.append(Spacer(1, 16))
        
        # Activity log section
        elements.append(Paragraph("<b>ACTIVITY LOG:</b>", self.styles['heading']))
        
        if form.data.activity_log:
            # Create activity table
            activity_data = [["Date/Time", "Notable Activities"]]
            for activity in form.data.activity_log:
                date_time_str = activity.datetime.strftime("%m/%d/%Y %H:%M") if activity.datetime else ""
                activity_data.append([
                    date_time_str,
                    activity.notable_activities
                ])
            
            activity_table = Table(activity_data, colWidths=[1.5*inch, 5*inch])
            activity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elements.append(activity_table)
        else:
            elements.append(Paragraph("No activities recorded.", self.styles['normal']))
        
        return elements
    
    def _create_footer(self, form: ICS214Form) -> List[Any]:
        """Create footer section for ICS-214 form.
        
        Args:
            form: ICS-214 form instance.
            
        Returns:
            List[Any]: List of ReportLab flowables for the footer.
        """
        elements = []
        
        # Add some space before footer
        elements.append(Spacer(1, 24))
        
        # Form information
        footer_text = f"ICS 214 - Generated by RadioForms on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        elements.append(Paragraph(footer_text, self.styles['footer']))
        
        return elements


class PDFService:
    """Main service for generating PDF documents from ICS forms.
    
    This service provides a unified interface for generating PDFs from different
    types of ICS forms. It automatically selects the appropriate generator based
    on form type and handles common PDF generation tasks.
    
    Attributes:
        generators (Dict[FormType, FormPDFGenerator]): Mapping of form types to generators.
        default_output_dir (Path): Default directory for PDF output.
        
    Example:
        >>> service = PDFService()
        >>> pdf_path = service.generate_pdf(ics213_form, "output.pdf")
        >>> print(f"PDF saved to: {pdf_path}")
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize PDF service with configuration.
        
        Args:
            output_dir: Default output directory for generated PDFs.
            
        Raises:
            PDFGenerationError: If ReportLab is not available.
        """
        if not REPORTLAB_AVAILABLE:
            raise PDFGenerationError(
                f"ReportLab is required for PDF generation but is not available. "
                f"Error: {REPORTLAB_ERROR}. Install with: pip install reportlab"
            )
        
        self.default_output_dir = Path(output_dir) if output_dir else Path.cwd()
        
        # Initialize generators
        self.generators: Dict[FormType, FormPDFGenerator] = {
            FormType.ICS_213: ICS213PDFGenerator(),
            FormType.ICS_214: ICS214PDFGenerator()
        }
        
        logger.debug("PDFService initialized")
    
    def generate_pdf(self, form: BaseForm, output_path: Optional[Union[str, Path]] = None) -> Path:
        """Generate PDF for the given form.
        
        Args:
            form: Form instance to generate PDF for.
            output_path: Path where PDF should be saved. If None, generates
                automatic filename in default output directory.
            
        Returns:
            Path: Path to the generated PDF file.
            
        Raises:
            PDFGenerationError: If form type is not supported or generation fails.
        """
        # Get form type
        form_type = form.get_form_type()
        
        # Check if generator exists for this form type
        if form_type not in self.generators:
            raise PDFGenerationError(f"PDF generation not supported for form type: {form_type}")
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{form_type.value}_{timestamp}.pdf"
            output_path = self.default_output_dir / filename
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate PDF using appropriate generator
        generator = self.generators[form_type]
        return generator.generate(form, output_path)
    
    def get_supported_form_types(self) -> List[FormType]:
        """Get list of form types supported for PDF generation.
        
        Returns:
            List[FormType]: List of supported form types.
        """
        return list(self.generators.keys())
    
    def add_generator(self, form_type: FormType, generator: FormPDFGenerator) -> None:
        """Add or replace generator for a form type.
        
        Args:
            form_type: Form type to add generator for.
            generator: PDF generator instance.
        """
        self.generators[form_type] = generator
        logger.debug(f"PDF generator added for form type: {form_type}")


def create_pdf_service(output_dir: Optional[Union[str, Path]] = None) -> PDFService:
    """Factory function for creating PDF service instances.
    
    Args:
        output_dir: Default output directory for generated PDFs.
        
    Returns:
        PDFService: Configured PDF service instance.
    """
    return PDFService(output_dir)


def generate_form_pdf(form: BaseForm, output_path: Union[str, Path]) -> Path:
    """Convenience function for generating PDFs from forms.
    
    Args:
        form: Form instance to generate PDF for.
        output_path: Path where PDF should be saved.
        
    Returns:
        Path: Path to the generated PDF file.
        
    Raises:
        PDFGenerationError: If PDF generation fails.
    """
    service = PDFService()
    return service.generate_pdf(form, output_path)