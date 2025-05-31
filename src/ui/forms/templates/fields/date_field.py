"""Date and time field templates for the RadioForms template system.

This module provides date and time input field templates with validation
and formatting options suitable for operational periods and timestamps.

Classes:
    DateFieldTemplate: Date input field
    TimeFieldTemplate: Time input field  
    DateTimeFieldTemplate: Combined date and time field

Notes:
    Date/time templates follow CLAUDE.md principles for simplicity while
    providing proper validation and formatting for emergency operations.
"""

from dataclasses import dataclass
from typing import Optional, Any, Union
from datetime import datetime, date, time
import logging

# Import base classes
from ..base.field_template import FieldTemplate, ValidationResult, ValidationRule

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QDateEdit, QTimeEdit, QDateTimeEdit, QHBoxLayout, QWidget
    from PySide6.QtCore import QDate, QTime, QDateTime, Qt
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QDateEdit:
        def __init__(self):
            self._date = "2025-05-31"
        
        def date(self):
            return self._date
        
        def setDate(self, date_val):
            self._date = date_val
        
        def setEnabled(self, enabled):
            pass
        
        def setVisible(self, visible):
            pass
        
        def setCalendarPopup(self, popup):
            pass
    
    class QTimeEdit:
        def __init__(self):
            self._time = "12:00"
        
        def time(self):
            return self._time
        
        def setTime(self, time_val):
            self._time = time_val
        
        def setEnabled(self, enabled):
            pass
        
        def setVisible(self, visible):
            pass
    
    class QDateTimeEdit:
        def __init__(self):
            self._datetime = "2025-05-31T12:00"
        
        def dateTime(self):
            return self._datetime
        
        def setDateTime(self, datetime_val):
            self._datetime = datetime_val
        
        def setEnabled(self, enabled):
            pass
        
        def setVisible(self, visible):
            pass
        
        def setCalendarPopup(self, popup):
            pass
    
    class QWidget:
        pass
    
    class QHBoxLayout:
        def __init__(self, parent=None):
            pass
        
        def addWidget(self, widget):
            pass
    
    class QDate:
        @staticmethod
        def fromString(date_str, format_str):
            return date_str
        
        @staticmethod
        def currentDate():
            return "2025-05-31"
    
    class QTime:
        @staticmethod
        def fromString(time_str, format_str):
            return time_str
        
        @staticmethod
        def currentTime():
            return "12:00"
    
    class QDateTime:
        @staticmethod
        def fromString(datetime_str, format_str):
            return datetime_str
        
        @staticmethod
        def currentDateTime():
            return "2025-05-31T12:00"
    
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class DateRangeRule(ValidationRule):
    """Validation rule for date ranges."""
    
    def __init__(self, min_date: Optional[date] = None, max_date: Optional[date] = None, 
                 field_label: str = "Date"):
        self.min_date = min_date
        self.max_date = max_date
        self.field_label = field_label
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate that date is within specified range."""
        if value is None:
            return ValidationResult.success()
        
        try:
            if isinstance(value, str):
                date_value = datetime.fromisoformat(value).date()
            elif isinstance(value, datetime):
                date_value = value.date()
            elif isinstance(value, date):
                date_value = value
            else:
                return ValidationResult.error(f"{self.field_label} must be a valid date")
            
            if self.min_date and date_value < self.min_date:
                return ValidationResult.error(
                    f"{self.field_label} must be on or after {self.min_date.isoformat()}"
                )
            
            if self.max_date and date_value > self.max_date:
                return ValidationResult.error(
                    f"{self.field_label} must be on or before {self.max_date.isoformat()}"
                )
            
            return ValidationResult.success()
            
        except (ValueError, AttributeError):
            return ValidationResult.error(f"{self.field_label} must be a valid date")


@dataclass
class DateFieldTemplate(FieldTemplate):
    """Date input field template.
    
    Provides a date picker widget with validation and formatting
    suitable for operational periods and form dates.
    
    Attributes:
        date_format: Display format for dates (e.g., "yyyy-MM-dd")
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        calendar_popup: Whether to show calendar popup
        current_section_date: Whether to default to current date
    
    Example:
        >>> field = DateFieldTemplate(
        ...     field_id="operational_date",
        ...     label="Operational Period Date",
        ...     date_format="yyyy-MM-dd",
        ...     calendar_popup=True,
        ...     required=True
        ... )
    """
    
    date_format: str = "yyyy-MM-dd"
    min_date: Optional[date] = None
    max_date: Optional[date] = None
    calendar_popup: bool = True
    current_section_date: bool = True
    
    def __post_init__(self):
        """Initialize date field template."""
        super().__post_init__()
        
        # Add date range validation if specified
        if self.min_date or self.max_date:
            self.validation_rules.append(DateRangeRule(self.min_date, self.max_date, self.label))
    
    def create_widget(self) -> QDateEdit:
        """Create QDateEdit widget for date input.
        
        Returns:
            QDateEdit: Configured date input widget
        """
        widget = QDateEdit()
        
        # Configure calendar popup
        if PYSIDE6_AVAILABLE and self.calendar_popup:
            widget.setCalendarPopup(True)
        
        # Set date format
        if PYSIDE6_AVAILABLE:
            widget.setDisplayFormat(self.date_format)
        
        # Set date range if specified
        if PYSIDE6_AVAILABLE and self.min_date:
            widget.setMinimumDate(QDate.fromString(self.min_date.isoformat(), Qt.ISODate))
        if PYSIDE6_AVAILABLE and self.max_date:
            widget.setMaximumDate(QDate.fromString(self.max_date.isoformat(), Qt.ISODate))
        
        # Set initial value
        if self.default_value:
            self.set_value(self.default_value)
        elif self.current_section_date:
            if PYSIDE6_AVAILABLE:
                widget.setDate(QDate.currentDate())
            else:
                widget.setDate(QDate.currentDate())
        
        # Configure enabled/visible state
        widget.setEnabled(self.enabled)
        widget.setVisible(self.visible)
        
        # Connect value changed signal if PySide6 is available
        if PYSIDE6_AVAILABLE:
            widget.dateChanged.connect(self._notify_value_changed)
        
        self.widget = widget
        logger.debug(f"Created date field widget for {self.field_id}")
        
        return widget
    
    def get_value(self) -> Optional[str]:
        """Get current date value as ISO string.
        
        Returns:
            str: Date in ISO format (YYYY-MM-DD) or None
        """
        if hasattr(self, 'widget') and self.widget:
            if PYSIDE6_AVAILABLE:
                qt_date = self.widget.date()
                return qt_date.toString(Qt.ISODate)
            else:
                return self.widget.date()
        elif self.default_value:
            if isinstance(self.default_value, str):
                return self.default_value
            elif isinstance(self.default_value, (date, datetime)):
                return self.default_value.isoformat()[:10]
        return None
    
    def set_value(self, value: Any) -> None:
        """Set date value in the widget.
        
        Args:
            value: Date value (string, date, or datetime)
        """
        if value is None:
            return
        
        try:
            if isinstance(value, str):
                date_value = datetime.fromisoformat(value).date()
            elif isinstance(value, datetime):
                date_value = value.date()
            elif isinstance(value, date):
                date_value = value
            else:
                logger.warning(f"Invalid date value type for {self.field_id}: {type(value)}")
                return
            
            if hasattr(self, 'widget') and self.widget:
                if PYSIDE6_AVAILABLE:
                    qt_date = QDate.fromString(date_value.isoformat(), Qt.ISODate)
                    self.widget.setDate(qt_date)
                else:
                    self.widget.setDate(date_value.isoformat())
            else:
                self.default_value = date_value.isoformat()
            
            logger.debug(f"Set date value for {self.field_id}: {date_value.isoformat()}")
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to set date value for {self.field_id}: {e}")


@dataclass
class TimeFieldTemplate(FieldTemplate):
    """Time input field template.
    
    Provides a time picker widget with validation suitable
    for operational times and timestamps.
    
    Attributes:
        time_format: Display format for times (e.g., "HH:mm")
        twenty_four_hour: Whether to use 24-hour format
        show_seconds: Whether to show seconds
    
    Example:
        >>> field = TimeFieldTemplate(
        ...     field_id="start_time",
        ...     label="Start Time",
        ...     time_format="HH:mm",
        ...     twenty_four_hour=True,
        ...     required=True
        ... )
    """
    
    time_format: str = "HH:mm"
    twenty_four_hour: bool = True
    show_seconds: bool = False
    
    def create_widget(self) -> QTimeEdit:
        """Create QTimeEdit widget for time input.
        
        Returns:
            QTimeEdit: Configured time input widget
        """
        widget = QTimeEdit()
        
        # Set time format
        if PYSIDE6_AVAILABLE:
            widget.setDisplayFormat(self.time_format)
        
        # Set initial value
        if self.default_value:
            self.set_value(self.default_value)
        else:
            if PYSIDE6_AVAILABLE:
                widget.setTime(QTime.currentTime())
            else:
                widget.setTime(QTime.currentTime())
        
        # Configure enabled/visible state
        widget.setEnabled(self.enabled)
        widget.setVisible(self.visible)
        
        # Connect value changed signal if PySide6 is available
        if PYSIDE6_AVAILABLE:
            widget.timeChanged.connect(self._notify_value_changed)
        
        self.widget = widget
        logger.debug(f"Created time field widget for {self.field_id}")
        
        return widget
    
    def get_value(self) -> Optional[str]:
        """Get current time value as string.
        
        Returns:
            str: Time in HH:MM format or None
        """
        if hasattr(self, 'widget') and self.widget:
            if PYSIDE6_AVAILABLE:
                qt_time = self.widget.time()
                return qt_time.toString("HH:mm")
            else:
                return self.widget.time()
        elif self.default_value:
            if isinstance(self.default_value, str):
                return self.default_value
            elif isinstance(self.default_value, (time, datetime)):
                return self.default_value.strftime("%H:%M")
        return None
    
    def set_value(self, value: Any) -> None:
        """Set time value in the widget.
        
        Args:
            value: Time value (string, time, or datetime)
        """
        if value is None:
            return
        
        try:
            if isinstance(value, str):
                if ":" in value:
                    time_parts = value.split(":")
                    hour = int(time_parts[0])
                    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    time_value = time(hour, minute)
                else:
                    time_value = datetime.fromisoformat(value).time()
            elif isinstance(value, datetime):
                time_value = value.time()
            elif isinstance(value, time):
                time_value = value
            else:
                logger.warning(f"Invalid time value type for {self.field_id}: {type(value)}")
                return
            
            if hasattr(self, 'widget') and self.widget:
                if PYSIDE6_AVAILABLE:
                    qt_time = QTime.fromString(time_value.strftime("%H:%M"), "HH:mm")
                    self.widget.setTime(qt_time)
                else:
                    self.widget.setTime(time_value.strftime("%H:%M"))
            else:
                self.default_value = time_value.strftime("%H:%M")
            
            logger.debug(f"Set time value for {self.field_id}: {time_value.strftime('%H:%M')}")
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to set time value for {self.field_id}: {e}")


@dataclass 
class DateTimeFieldTemplate(FieldTemplate):
    """Combined date and time field template.
    
    Provides a combined date and time picker for complete timestamps.
    
    Attributes:
        datetime_format: Display format for date/time
        calendar_popup: Whether to show calendar popup
        current_datetime: Whether to default to current date/time
    
    Example:
        >>> field = DateTimeFieldTemplate(
        ...     field_id="prepared_datetime",
        ...     label="Date/Time Prepared",
        ...     datetime_format="yyyy-MM-dd HH:mm",
        ...     required=True
        ... )
    """
    
    datetime_format: str = "yyyy-MM-dd HH:mm"
    calendar_popup: bool = True
    current_datetime: bool = True
    
    def create_widget(self) -> QDateTimeEdit:
        """Create QDateTimeEdit widget for date/time input.
        
        Returns:
            QDateTimeEdit: Configured date/time input widget
        """
        widget = QDateTimeEdit()
        
        # Configure calendar popup
        if PYSIDE6_AVAILABLE and self.calendar_popup:
            widget.setCalendarPopup(True)
        
        # Set datetime format
        if PYSIDE6_AVAILABLE:
            widget.setDisplayFormat(self.datetime_format)
        
        # Set initial value
        if self.default_value:
            self.set_value(self.default_value)
        elif self.current_datetime:
            if PYSIDE6_AVAILABLE:
                widget.setDateTime(QDateTime.currentDateTime())
            else:
                widget.setDateTime(QDateTime.currentDateTime())
        
        # Configure enabled/visible state
        widget.setEnabled(self.enabled)
        widget.setVisible(self.visible)
        
        # Connect value changed signal if PySide6 is available
        if PYSIDE6_AVAILABLE:
            widget.dateTimeChanged.connect(self._notify_value_changed)
        
        self.widget = widget
        logger.debug(f"Created datetime field widget for {self.field_id}")
        
        return widget
    
    def get_value(self) -> Optional[str]:
        """Get current datetime value as ISO string.
        
        Returns:
            str: DateTime in ISO format or None
        """
        if hasattr(self, 'widget') and self.widget:
            if PYSIDE6_AVAILABLE:
                qt_datetime = self.widget.dateTime()
                return qt_datetime.toString(Qt.ISODate)
            else:
                return self.widget.dateTime()
        elif self.default_value:
            if isinstance(self.default_value, str):
                return self.default_value
            elif isinstance(self.default_value, datetime):
                return self.default_value.isoformat()
        return None
    
    def set_value(self, value: Any) -> None:
        """Set datetime value in the widget.
        
        Args:
            value: DateTime value (string or datetime)
        """
        if value is None:
            return
        
        try:
            if isinstance(value, str):
                datetime_value = datetime.fromisoformat(value)
            elif isinstance(value, datetime):
                datetime_value = value
            else:
                logger.warning(f"Invalid datetime value type for {self.field_id}: {type(value)}")
                return
            
            if hasattr(self, 'widget') and self.widget:
                if PYSIDE6_AVAILABLE:
                    qt_datetime = QDateTime.fromString(datetime_value.isoformat(), Qt.ISODate)
                    self.widget.setDateTime(qt_datetime)
                else:
                    self.widget.setDateTime(datetime_value.isoformat())
            else:
                self.default_value = datetime_value.isoformat()
            
            logger.debug(f"Set datetime value for {self.field_id}: {datetime_value.isoformat()}")
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to set datetime value for {self.field_id}: {e}")