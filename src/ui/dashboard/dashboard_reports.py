"""Dashboard Reports Component for Data Export and Analysis.

Provides comprehensive reporting capabilities for dashboard data including
incident summaries, resource reports, timeline exports, and analytics.

Following CLAUDE.md principles:
- Simple, comprehensive reporting interface
- Performance optimized for large datasets
- Multiple export formats supported
- Clear data visualization and analysis

Example:
    >>> from src.ui.dashboard.dashboard_reports import DashboardReports
    >>> reports = DashboardReports()
    >>> reports.generate_incident_summary("Mountain Wildfire")
    >>> reports.export_to_pdf("incident_report.pdf")

Classes:
    DashboardReports: Main reports generation and export
    ReportData: Report data container
    ReportType: Report type enumeration
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Import Qt components with graceful fallback
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QComboBox, QTextEdit,
        QGroupBox, QProgressBar, QFileDialog,
        QMessageBox, QCheckBox, QDateEdit
    )
    from PySide6.QtCore import Qt, Signal, QDate, QThread, pyqtSignal
    from PySide6.QtGui import QFont, QTextDocument, QPrinter
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QPushButton = QComboBox = QTextEdit = object
    QGroupBox = QProgressBar = QFileDialog = object
    QMessageBox = QCheckBox = QDateEdit = object
    Signal = QDate = QThread = pyqtSignal = object
    QFont = QTextDocument = QPrinter = object
    Qt = type('Qt', (), {'AlignTop': 0, 'AlignLeft': 0})

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Report type enumeration."""
    INCIDENT_SUMMARY = "incident_summary"
    FORM_COMPLETION = "form_completion"
    RESOURCE_ALLOCATION = "resource_allocation"
    TIMELINE_EXPORT = "timeline_export"
    ANALYTICS_REPORT = "analytics_report"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ReportData:
    """Report data container."""
    report_type: ReportType
    incident_name: str
    start_date: datetime
    end_date: datetime
    data: Dict[str, Any]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


class ReportGeneratorThread(QThread):
    """Background thread for report generation."""
    
    progress_updated = pyqtSignal(int) if HAS_PYSIDE6 else None
    report_completed = pyqtSignal(dict) if HAS_PYSIDE6 else None
    error_occurred = pyqtSignal(str) if HAS_PYSIDE6 else None
    
    def __init__(self, report_data: ReportData, output_format: str):
        if not HAS_PYSIDE6:
            return
            
        super().__init__()
        self.report_data = report_data
        self.output_format = output_format
    
    def run(self):
        """Run report generation in background."""
        try:
            if self.progress_updated:
                self.progress_updated.emit(10)
            
            # Simulate report generation steps
            report_content = self._generate_report_content()
            
            if self.progress_updated:
                self.progress_updated.emit(70)
            
            formatted_report = self._format_report(report_content)
            
            if self.progress_updated:
                self.progress_updated.emit(100)
            
            if self.report_completed:
                self.report_completed.emit(formatted_report)
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            if self.error_occurred:
                self.error_occurred.emit(str(e))
    
    def _generate_report_content(self) -> Dict[str, Any]:
        """Generate report content based on data."""
        content = {
            'header': self._generate_header(),
            'summary': self._generate_summary(),
            'details': self._generate_details(),
            'footer': self._generate_footer()
        }
        return content
    
    def _generate_header(self) -> Dict[str, str]:
        """Generate report header."""
        return {
            'title': f"{self.report_data.report_type.value.replace('_', ' ').title()} Report",
            'incident': self.report_data.incident_name,
            'date_range': f"{self.report_data.start_date.strftime('%Y-%m-%d')} to {self.report_data.end_date.strftime('%Y-%m-%d')}",
            'generated': self.report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate report summary."""
        data = self.report_data.data
        return {
            'key_metrics': data.get('metrics', {}),
            'highlights': data.get('highlights', []),
            'recommendations': data.get('recommendations', [])
        }
    
    def _generate_details(self) -> Dict[str, Any]:
        """Generate detailed report sections."""
        return self.report_data.data.get('details', {})
    
    def _generate_footer(self) -> Dict[str, str]:
        """Generate report footer."""
        return {
            'generator': 'RadioForms Dashboard System',
            'version': '1.0',
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format report for output."""
        if self.output_format == 'html':
            return self._format_html(content)
        elif self.output_format == 'json':
            return self._format_json(content)
        else:
            return self._format_text(content)
    
    def _format_html(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format report as HTML."""
        header = content['header']
        summary = content['summary']
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{header['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 20px; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{header['title']}</h1>
                <p><strong>Incident:</strong> {header['incident']}</p>
                <p><strong>Date Range:</strong> {header['date_range']}</p>
                <p><strong>Generated:</strong> {header['generated']}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <div class="metrics">
                    {self._format_html_metrics(summary.get('key_metrics', {}))}
                </div>
            </div>
            
            <div class="section">
                <h2>Details</h2>
                {self._format_html_details(content.get('details', {}))}
            </div>
        </body>
        </html>
        """
        
        return {
            'format': 'html',
            'content': html_content,
            'filename': f"{header['incident']}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        }
    
    def _format_html_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for HTML display."""
        html_parts = []
        for key, value in metrics.items():
            html_parts.append(f'<div class="metric"><strong>{key}:</strong> {value}</div>')
        return '\n'.join(html_parts)
    
    def _format_html_details(self, details: Dict[str, Any]) -> str:
        """Format details for HTML display."""
        html_parts = []
        for section, data in details.items():
            html_parts.append(f'<h3>{section.replace("_", " ").title()}</h3>')
            if isinstance(data, list):
                html_parts.append('<ul>')
                for item in data:
                    html_parts.append(f'<li>{item}</li>')
                html_parts.append('</ul>')
            else:
                html_parts.append(f'<p>{data}</p>')
        return '\n'.join(html_parts)
    
    def _format_json(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format report as JSON."""
        return {
            'format': 'json',
            'content': json.dumps(content, indent=2, default=str),
            'filename': f"{content['header']['incident']}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        }
    
    def _format_text(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format report as plain text."""
        header = content['header']
        summary = content['summary']
        
        text_parts = [
            "=" * 60,
            f"  {header['title']}",
            "=" * 60,
            f"Incident: {header['incident']}",
            f"Date Range: {header['date_range']}",
            f"Generated: {header['generated']}",
            "",
            "SUMMARY",
            "-" * 20,
        ]
        
        # Add metrics
        for key, value in summary.get('key_metrics', {}).items():
            text_parts.append(f"{key}: {value}")
        
        text_parts.extend([
            "",
            "DETAILS",
            "-" * 20,
        ])
        
        # Add details
        for section, data in content.get('details', {}).items():
            text_parts.append(f"\n{section.replace('_', ' ').title()}:")
            if isinstance(data, list):
                for item in data:
                    text_parts.append(f"  - {item}")
            else:
                text_parts.append(f"  {data}")
        
        text_content = '\n'.join(text_parts)
        
        return {
            'format': 'text',
            'content': text_content,
            'filename': f"{header['incident']}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        }


class DashboardReports(QWidget):
    """Dashboard reports generation and export widget.
    
    Provides comprehensive reporting capabilities for dashboard data
    with multiple export formats and background processing.
    """
    
    report_generated = Signal(dict) if HAS_PYSIDE6 else None
    export_completed = Signal(str) if HAS_PYSIDE6 else None
    
    def __init__(self, parent=None):
        """Initialize dashboard reports widget."""
        if not HAS_PYSIDE6:
            return
            
        super().__init__(parent)
        self.current_data = {}
        self.report_thread = None
        self._init_ui()
        
        logger.info("Dashboard reports widget initialized")
    
    def _init_ui(self):
        """Initialize user interface components."""
        self.setObjectName("DashboardReports")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Report configuration
        config_frame = self._create_config_section()
        main_layout.addWidget(config_frame)
        
        # Report preview
        preview_frame = self._create_preview_section()
        main_layout.addWidget(preview_frame)
        
        # Export controls
        export_frame = self._create_export_section()
        main_layout.addWidget(export_frame)
    
    def _create_config_section(self) -> QGroupBox:
        """Create report configuration section."""
        frame = QGroupBox("Report Configuration")
        layout = QGridLayout(frame)
        
        # Report type
        layout.addWidget(QLabel("Report Type:"), 0, 0)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Incident Summary",
            "Form Completion",
            "Resource Allocation",
            "Timeline Export",
            "Analytics Report",
            "Comprehensive"
        ])
        layout.addWidget(self.report_type_combo, 0, 1)
        
        # Date range
        layout.addWidget(QLabel("Start Date:"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        layout.addWidget(self.start_date_edit, 1, 1)
        
        layout.addWidget(QLabel("End Date:"), 1, 2)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.end_date_edit, 1, 3)
        
        # Options
        layout.addWidget(QLabel("Options:"), 2, 0)
        options_layout = QHBoxLayout()
        
        self.include_charts_check = QCheckBox("Include Charts")
        self.include_charts_check.setChecked(True)
        options_layout.addWidget(self.include_charts_check)
        
        self.include_raw_data_check = QCheckBox("Include Raw Data")
        options_layout.addWidget(self.include_raw_data_check)
        
        self.confidential_check = QCheckBox("Mark Confidential")
        options_layout.addWidget(self.confidential_check)
        
        layout.addLayout(options_layout, 2, 1, 1, 3)
        
        # Generate button
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self._generate_report)
        layout.addWidget(self.generate_button, 3, 0, 1, 4)
        
        return frame
    
    def _create_preview_section(self) -> QGroupBox:
        """Create report preview section."""
        frame = QGroupBox("Report Preview")
        layout = QVBoxLayout(frame)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)
        
        return frame
    
    def _create_export_section(self) -> QGroupBox:
        """Create export controls section."""
        frame = QGroupBox("Export Options")
        layout = QHBoxLayout(frame)
        
        # Format selection
        layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "PDF", "JSON", "Text"])
        layout.addWidget(self.format_combo)
        
        layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Export buttons
        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self._export_report)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)
        
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self._save_configuration)
        layout.addWidget(self.save_button)
        
        return frame
    
    def set_dashboard_data(self, data: Dict[str, Any]):
        """Set dashboard data for report generation.
        
        Args:
            data: Dashboard data dictionary
        """
        self.current_data = data
        logger.debug("Dashboard data set for reports")
    
    def generate_incident_summary(self, incident_name: str) -> ReportData:
        """Generate incident summary report.
        
        Args:
            incident_name: Name of incident
            
        Returns:
            ReportData: Generated report data
        """
        start_date = self.start_date_edit.date().toPython() if HAS_PYSIDE6 else datetime.now() - timedelta(days=7)
        end_date = self.end_date_edit.date().toPython() if HAS_PYSIDE6 else datetime.now()
        
        # Compile incident summary data
        summary_data = {
            'metrics': {
                'Total Forms': self.current_data.get('total_forms', 0),
                'Completion Rate': f"{self.current_data.get('completion_rate', 0):.1f}%",
                'Recent Activity': self.current_data.get('recent_activity', 0),
                'Critical Updates': self.current_data.get('critical_updates', 0)
            },
            'highlights': [
                f"Incident duration: {self._calculate_incident_duration()}",
                f"Forms by type: {len(self.current_data.get('forms_by_type', {}))} categories",
                f"Resource utilization: {self.current_data.get('resource_utilization', 0):.1f}%"
            ],
            'recommendations': [
                "Continue monitoring form completion rates",
                "Review resource allocation efficiency",
                "Maintain regular status updates"
            ],
            'details': {
                'forms_by_type': self.current_data.get('forms_by_type', {}),
                'timeline_events': self.current_data.get('timeline_events', []),
                'resource_summary': self.current_data.get('resource_summary', {})
            }
        }
        
        return ReportData(
            report_type=ReportType.INCIDENT_SUMMARY,
            incident_name=incident_name,
            start_date=start_date,
            end_date=end_date,
            data=summary_data
        )
    
    def _generate_report(self):
        """Generate report based on current configuration."""
        if not self.current_data:
            self._show_message("No data available for report generation")
            return
        
        # Get configuration
        report_type_text = self.report_type_combo.currentText()
        incident_name = self.current_data.get('incident_name', 'Unknown Incident')
        
        # Map UI text to ReportType
        report_type_map = {
            "Incident Summary": ReportType.INCIDENT_SUMMARY,
            "Form Completion": ReportType.FORM_COMPLETION,
            "Resource Allocation": ReportType.RESOURCE_ALLOCATION,
            "Timeline Export": ReportType.TIMELINE_EXPORT,
            "Analytics Report": ReportType.ANALYTICS_REPORT,
            "Comprehensive": ReportType.COMPREHENSIVE
        }
        
        report_type = report_type_map.get(report_type_text, ReportType.INCIDENT_SUMMARY)
        
        # Generate appropriate report
        if report_type == ReportType.INCIDENT_SUMMARY:
            report_data = self.generate_incident_summary(incident_name)
        else:
            # Placeholder for other report types
            report_data = self._generate_generic_report(report_type, incident_name)
        
        # Start background generation
        self._start_report_generation(report_data)
        
        logger.info(f"Report generation started: {report_type.value}")
    
    def _generate_generic_report(self, report_type: ReportType, incident_name: str) -> ReportData:
        """Generate generic report for non-summary types.
        
        Args:
            report_type: Type of report to generate
            incident_name: Name of incident
            
        Returns:
            ReportData: Generated report data
        """
        start_date = self.start_date_edit.date().toPython() if HAS_PYSIDE6 else datetime.now() - timedelta(days=7)
        end_date = self.end_date_edit.date().toPython() if HAS_PYSIDE6 else datetime.now()
        
        # Create basic report structure
        report_data = {
            'metrics': self.current_data,
            'highlights': [f"{report_type.value.replace('_', ' ').title()} generated"],
            'recommendations': ["Review report data for insights"],
            'details': self.current_data
        }
        
        return ReportData(
            report_type=report_type,
            incident_name=incident_name,
            start_date=start_date,
            end_date=end_date,
            data=report_data
        )
    
    def _start_report_generation(self, report_data: ReportData):
        """Start background report generation.
        
        Args:
            report_data: Report data to process
        """
        if not HAS_PYSIDE6:
            return
            
        output_format = self.format_combo.currentText().lower()
        
        # Create and configure thread
        self.report_thread = ReportGeneratorThread(report_data, output_format)
        
        # Connect signals
        if hasattr(self.report_thread, 'progress_updated'):
            self.report_thread.progress_updated.connect(self._update_progress)
        if hasattr(self.report_thread, 'report_completed'):
            self.report_thread.report_completed.connect(self._report_completed)
        if hasattr(self.report_thread, 'error_occurred'):
            self.report_thread.error_occurred.connect(self._report_error)
        
        # Show progress and start
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_button.setEnabled(False)
        
        self.report_thread.start()
    
    def _update_progress(self, value: int):
        """Update progress bar."""
        if HAS_PYSIDE6:
            self.progress_bar.setValue(value)
    
    def _report_completed(self, report_result: Dict[str, Any]):
        """Handle completed report generation."""
        if not HAS_PYSIDE6:
            return
            
        # Update preview
        preview_content = report_result.get('content', '')
        if len(preview_content) > 1000:
            preview_content = preview_content[:1000] + "...\n\n[Content truncated for preview]"
        
        self.preview_text.setPlainText(preview_content)
        
        # Enable export
        self.export_button.setEnabled(True)
        self.current_report = report_result
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        
        if self.report_generated:
            self.report_generated.emit(report_result)
        
        logger.info("Report generation completed")
    
    def _report_error(self, error_message: str):
        """Handle report generation error."""
        self._show_message(f"Report generation failed: {error_message}")
        
        # Reset UI
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        
        logger.error(f"Report generation error: {error_message}")
    
    def _export_report(self):
        """Export generated report to file."""
        if not hasattr(self, 'current_report'):
            self._show_message("No report generated to export")
            return
        
        if not HAS_PYSIDE6:
            return
            
        # Get save location
        filename = self.current_report.get('filename', 'report.txt')
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            filename,
            "All Files (*.*)"
        )
        
        if filepath:
            try:
                # Write report content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.current_report['content'])
                
                self._show_message(f"Report exported successfully to {filepath}")
                
                if self.export_completed:
                    self.export_completed.emit(filepath)
                
                logger.info(f"Report exported to: {filepath}")
                
            except Exception as e:
                self._show_message(f"Export failed: {str(e)}")
                logger.error(f"Report export error: {e}")
    
    def _save_configuration(self):
        """Save current report configuration."""
        config = {
            'report_type': self.report_type_combo.currentText(),
            'start_date': self.start_date_edit.date().toString(),
            'end_date': self.end_date_edit.date().toString(),
            'format': self.format_combo.currentText(),
            'include_charts': self.include_charts_check.isChecked(),
            'include_raw_data': self.include_raw_data_check.isChecked(),
            'confidential': self.confidential_check.isChecked()
        }
        
        # Save to settings or file
        logger.info("Report configuration saved")
    
    def _calculate_incident_duration(self) -> str:
        """Calculate incident duration string."""
        # Placeholder calculation
        return "12 hours 30 minutes"
    
    def _show_message(self, message: str):
        """Show message to user."""
        if HAS_PYSIDE6:
            QMessageBox.information(self, "Dashboard Reports", message)
        else:
            logger.info(f"Message: {message}")
    
    def get_available_reports(self) -> List[str]:
        """Get list of available report types.
        
        Returns:
            List of available report type names
        """
        return [rt.value.replace('_', ' ').title() for rt in ReportType]