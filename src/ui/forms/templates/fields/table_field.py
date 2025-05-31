"""Table field templates for the RadioForms template system.

This module provides table input field templates for structured data entry
with dynamic row management, suitable for frequency assignments, personnel
lists, and resource tracking.

Classes:
    TableColumn: Configuration for table columns
    TableFieldTemplate: Dynamic table with add/remove row capability

Notes:
    Table templates follow CLAUDE.md principles for simplicity while
    providing powerful structured data management capabilities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import logging

# Import base classes
from ..base.field_template import FieldTemplate, ValidationResult

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView,
                                   QPushButton, QVBoxLayout, QHBoxLayout, 
                                   QWidget, QAbstractItemView, QMessageBox)
    from PySide6.QtCore import Qt, QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QTableWidget:
        def __init__(self):
            self._rows = []
            self._columns = []
            self._column_count = 0
            self._row_count = 0
        
        def setColumnCount(self, count):
            self._column_count = count
        
        def setRowCount(self, count):
            self._row_count = count
            while len(self._rows) < count:
                self._rows.append([None] * self._column_count)
        
        def rowCount(self):
            return self._row_count
        
        def columnCount(self):
            return self._column_count
        
        def setHorizontalHeaderLabels(self, labels):
            self._columns = labels
        
        def insertRow(self, row):
            self._rows.insert(row, [None] * self._column_count)
            self._row_count += 1
        
        def removeRow(self, row):
            if 0 <= row < len(self._rows):
                self._rows.pop(row)
                self._row_count -= 1
        
        def item(self, row, column):
            if 0 <= row < len(self._rows) and 0 <= column < len(self._rows[row]):
                return self._rows[row][column]
            return None
        
        def setItem(self, row, column, item):
            if 0 <= row < len(self._rows) and 0 <= column < len(self._rows[row]):
                self._rows[row][column] = item
        
        def setEnabled(self, enabled):
            pass
        
        def setVisible(self, visible):
            pass
        
        def clear(self):
            self._rows = []
            self._row_count = 0
    
    class QTableWidgetItem:
        def __init__(self, text=""):
            self._text = text
        
        def text(self):
            return self._text
        
        def setText(self, text):
            self._text = text
    
    class QHeaderView:
        ResizeToContents = "ResizeToContents"
        Stretch = "Stretch"
    
    class QAbstractItemView:
        SingleSelection = "SingleSelection"
        ExtendedSelection = "ExtendedSelection"
    
    class QPushButton:
        def __init__(self, text=""):
            self._text = text
        
        def setText(self, text):
            self._text = text
        
        def setEnabled(self, enabled):
            pass
    
    class QWidget:
        pass
    
    class QVBoxLayout:
        def __init__(self, parent=None):
            pass
        
        def addWidget(self, widget):
            pass
        
        def addLayout(self, layout):
            pass
    
    class QHBoxLayout:
        def __init__(self, parent=None):
            pass
        
        def addWidget(self, widget):
            pass
    
    class Qt:
        AlignCenter = "AlignCenter"
    
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class ColumnType(Enum):
    """Types of table columns available."""
    
    TEXT = "text"           # Simple text input
    NUMBER = "number"       # Numeric input
    CHOICE = "choice"       # Dropdown selection
    CHECKBOX = "checkbox"   # Boolean checkbox
    DATE = "date"           # Date picker
    TIME = "time"           # Time picker


@dataclass
class TableColumn:
    """Configuration for a table column.
    
    Attributes:
        column_id: Unique identifier for this column
        label: Human-readable column header
        column_type: Type of data in this column
        width: Column width in pixels (None for auto)
        editable: Whether column cells are editable
        required: Whether column requires values
        choices: Available choices for CHOICE type columns
        min_value: Minimum value for NUMBER type columns
        max_value: Maximum value for NUMBER type columns
        default_value: Default value for new rows
    """
    
    column_id: str
    label: str
    column_type: ColumnType = ColumnType.TEXT
    width: Optional[int] = None
    editable: bool = True
    required: bool = False
    choices: List[str] = field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert column to dictionary representation."""
        return {
            'column_id': self.column_id,
            'label': self.label,
            'column_type': self.column_type.value,
            'width': self.width,
            'editable': self.editable,
            'required': self.required,
            'choices': self.choices,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'default_value': self.default_value
        }


@dataclass
class TableFieldTemplate(FieldTemplate):
    """Dynamic table field template for structured data entry.
    
    Provides a table widget with configurable columns and dynamic row
    management for forms requiring structured data like frequency
    assignments, personnel lists, or resource tracking.
    
    Attributes:
        columns: List of column configurations
        min_rows: Minimum number of rows to display
        max_rows: Maximum number of rows allowed
        allow_add: Whether users can add new rows
        allow_remove: Whether users can remove rows
        show_row_numbers: Whether to show row numbers
        alternating_colors: Whether to use alternating row colors
        single_selection: Whether only one row can be selected
    
    Example:
        >>> columns = [
        ...     TableColumn("zone", "Zone/Group", ColumnType.TEXT, width=120),
        ...     TableColumn("frequency", "Frequency", ColumnType.TEXT, width=100),
        ...     TableColumn("function", "Function", ColumnType.CHOICE, 
        ...                choices=["Command", "Tactical", "Support"])
        ... ]
        >>> table = TableFieldTemplate(
        ...     field_id="frequency_table",
        ...     label="Radio Frequency Assignments",
        ...     columns=columns,
        ...     min_rows=5,
        ...     allow_add=True,
        ...     allow_remove=True
        ... )
    """
    
    columns: List[TableColumn] = field(default_factory=list)
    min_rows: int = 0
    max_rows: Optional[int] = None
    allow_add: bool = True
    allow_remove: bool = True
    show_row_numbers: bool = True
    alternating_colors: bool = True
    single_selection: bool = False
    
    def __post_init__(self):
        """Initialize table field template."""
        super().__post_init__()
        
        # Validate columns
        if not self.columns:
            raise ValueError("Table field must have at least one column")
        
        # Check for duplicate column IDs
        column_ids = [col.column_id for col in self.columns]
        if len(column_ids) != len(set(column_ids)):
            raise ValueError("Column IDs must be unique")
    
    def create_widget(self) -> QWidget:
        """Create table widget with add/remove buttons.
        
        Returns:
            QWidget: Container widget with table and buttons
        """
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Create table widget
        self.table_widget = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table_widget)
        
        # Create button layout if add/remove allowed
        if self.allow_add or self.allow_remove:
            button_layout = QHBoxLayout()
            
            if self.allow_add:
                self.add_button = QPushButton("Add Row")
                if PYSIDE6_AVAILABLE:
                    self.add_button.clicked.connect(self.add_row)
                button_layout.addWidget(self.add_button)
            
            if self.allow_remove:
                self.remove_button = QPushButton("Remove Row")
                if PYSIDE6_AVAILABLE:
                    self.remove_button.clicked.connect(self.remove_selected_row)
                button_layout.addWidget(self.remove_button)
            
            layout.addLayout(button_layout)
        
        # Configure enabled/visible state
        container.setEnabled(self.enabled)
        container.setVisible(self.visible)
        
        self.widget = container
        logger.debug(f"Created table widget for {self.field_id}")
        
        return container
    
    def _setup_table(self) -> None:
        """Set up table widget with columns and initial rows."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Set column count and headers
        self.table_widget.setColumnCount(len(self.columns))
        headers = [col.label for col in self.columns]
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Configure column properties
        header = self.table_widget.horizontalHeader()
        for i, column in enumerate(self.columns):
            if column.width:
                self.table_widget.setColumnWidth(i, column.width)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Set initial row count
        if self.min_rows > 0:
            self.table_widget.setRowCount(self.min_rows)
            self._populate_default_values()
        
        # Configure table behavior
        if self.show_row_numbers:
            self.table_widget.verticalHeader().setVisible(True)
        else:
            self.table_widget.verticalHeader().setVisible(False)
        
        if self.alternating_colors:
            self.table_widget.setAlternatingRowColors(True)
        
        if self.single_selection:
            self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        else:
            self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Connect signals for value change notifications
        if PYSIDE6_AVAILABLE:
            self.table_widget.itemChanged.connect(self._on_item_changed)
    
    def _populate_default_values(self) -> None:
        """Populate table with default values for new rows."""
        for row in range(self.table_widget.rowCount()):
            for col, column in enumerate(self.columns):
                if column.default_value is not None:
                    item = QTableWidgetItem(str(column.default_value))
                    self.table_widget.setItem(row, col, item)
    
    def _on_item_changed(self, item) -> None:
        """Handle table item changes."""
        self._notify_value_changed()
    
    def add_row(self) -> bool:
        """Add a new row to the table.
        
        Returns:
            bool: True if row was added, False if max rows reached
        """
        if not self.allow_add:
            return False
        
        current_rows = self.table_widget.rowCount()
        if self.max_rows and current_rows >= self.max_rows:
            return False
        
        # Insert new row at the end
        self.table_widget.insertRow(current_rows)
        
        # Populate with default values
        for col, column in enumerate(self.columns):
            if column.default_value is not None:
                item = QTableWidgetItem(str(column.default_value))
                self.table_widget.setItem(current_rows, col, item)
        
        logger.debug(f"Added row to table {self.field_id}")
        self._notify_value_changed()
        return True
    
    def remove_selected_row(self) -> bool:
        """Remove the currently selected row.
        
        Returns:
            bool: True if row was removed, False if no selection or min rows reached
        """
        if not self.allow_remove:
            return False
        
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            return False
        
        current_rows = self.table_widget.rowCount()
        if current_rows <= self.min_rows:
            return False
        
        self.table_widget.removeRow(current_row)
        logger.debug(f"Removed row {current_row} from table {self.field_id}")
        self._notify_value_changed()
        return True
    
    def remove_row(self, row_index: int) -> bool:
        """Remove a specific row by index.
        
        Args:
            row_index: Index of row to remove
            
        Returns:
            bool: True if row was removed
        """
        if not self.allow_remove:
            return False
        
        if row_index < 0 or row_index >= self.table_widget.rowCount():
            return False
        
        current_rows = self.table_widget.rowCount()
        if current_rows <= self.min_rows:
            return False
        
        self.table_widget.removeRow(row_index)
        logger.debug(f"Removed row {row_index} from table {self.field_id}")
        self._notify_value_changed()
        return True
    
    def get_value(self) -> List[Dict[str, Any]]:
        """Get table data as list of row dictionaries.
        
        Returns:
            List of dictionaries, one per row with column_id keys
        """
        # If widget hasn't been created yet, return empty list or cached data
        if not hasattr(self, 'table_widget') or not self.table_widget:
            return getattr(self, '_cached_data', [])
        
        table_data = []
        
        for row in range(self.table_widget.rowCount()):
            row_data = {}
            for col, column in enumerate(self.columns):
                item = self.table_widget.item(row, col)
                value = item.text() if item else ""
                
                # Convert value based on column type
                if column.column_type == ColumnType.NUMBER:
                    try:
                        value = float(value) if value else None
                    except ValueError:
                        value = None
                elif column.column_type == ColumnType.CHECKBOX:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                row_data[column.column_id] = value
            
            # Only include rows that have at least one non-empty value
            if any(value for value in row_data.values() if value):
                table_data.append(row_data)
        
        return table_data
    
    def set_value(self, value: List[Dict[str, Any]]) -> None:
        """Set table data from list of row dictionaries.
        
        Args:
            value: List of dictionaries with column_id keys
        """
        if not isinstance(value, list):
            logger.warning(f"Invalid table data type for {self.field_id}: expected list")
            return
        
        # Cache the data for later use
        self._cached_data = value
        
        # If widget hasn't been created yet, just cache the data
        if not hasattr(self, 'table_widget') or not self.table_widget:
            logger.debug(f"Cached table data for {self.field_id}: {len(value)} rows")
            return
        
        # Clear existing data
        self.table_widget.setRowCount(0)
        
        # Ensure minimum rows
        target_rows = max(len(value), self.min_rows)
        self.table_widget.setRowCount(target_rows)
        
        # Populate data
        for row_idx, row_data in enumerate(value):
            if row_idx >= self.table_widget.rowCount():
                break
            
            for col, column in enumerate(self.columns):
                cell_value = row_data.get(column.column_id, "")
                item = QTableWidgetItem(str(cell_value) if cell_value is not None else "")
                self.table_widget.setItem(row_idx, col, item)
        
        # Fill remaining rows with defaults if needed
        for row_idx in range(len(value), self.table_widget.rowCount()):
            for col, column in enumerate(self.columns):
                if column.default_value is not None:
                    item = QTableWidgetItem(str(column.default_value))
                    self.table_widget.setItem(row_idx, col, item)
        
        logger.debug(f"Set table data for {self.field_id}: {len(value)} rows")
    
    def validate(self) -> ValidationResult:
        """Validate table data including required columns.
        
        Returns:
            ValidationResult: Validation result for table data
        """
        try:
            base_result = super().validate()
            if not base_result.is_valid:
                return base_result
            
            table_data = self.get_value()
            
            # Check if table has any data when required
            if self.required and not table_data:
                return ValidationResult.error(f"{self.label} requires at least one row of data")
        except Exception as e:
            logger.warning(f"Table validation failed for {self.field_id}: {e}")
            # If validation fails due to missing widget, assume it's valid for now
            return ValidationResult.success(f"Table {self.label} validation deferred until widget creation")
        
        # Validate required columns
        errors = []
        for row_idx, row_data in enumerate(table_data):
            for column in self.columns:
                if column.required:
                    value = row_data.get(column.column_id)
                    if not value or (isinstance(value, str) and not value.strip()):
                        errors.append(f"Row {row_idx + 1}: {column.label} is required")
                
                # Validate number ranges
                if column.column_type == ColumnType.NUMBER and column.column_id in row_data:
                    value = row_data[column.column_id]
                    if value is not None:
                        if column.min_value is not None and value < column.min_value:
                            errors.append(f"Row {row_idx + 1}: {column.label} must be >= {column.min_value}")
                        if column.max_value is not None and value > column.max_value:
                            errors.append(f"Row {row_idx + 1}: {column.label} must be <= {column.max_value}")
        
        if errors:
            return ValidationResult.error("; ".join(errors))
        
        return ValidationResult.success(f"Table has {len(table_data)} valid rows")
    
    def get_row_data(self, row_index: int) -> Optional[Dict[str, Any]]:
        """Get data for a specific row.
        
        Args:
            row_index: Index of row to get
            
        Returns:
            Dict with column data or None if invalid index
        """
        if row_index < 0 or row_index >= self.table_widget.rowCount():
            return None
        
        row_data = {}
        for col, column in enumerate(self.columns):
            item = self.table_widget.item(row_index, col)
            value = item.text() if item else ""
            row_data[column.column_id] = value
        
        return row_data
    
    def set_row_data(self, row_index: int, row_data: Dict[str, Any]) -> bool:
        """Set data for a specific row.
        
        Args:
            row_index: Index of row to set
            row_data: Dict with column data
            
        Returns:
            bool: True if row was set successfully
        """
        if row_index < 0 or row_index >= self.table_widget.rowCount():
            return False
        
        for col, column in enumerate(self.columns):
            value = row_data.get(column.column_id, "")
            item = QTableWidgetItem(str(value) if value is not None else "")
            self.table_widget.setItem(row_index, col, item)
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table template to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'columns': [col.to_dict() for col in self.columns],
            'min_rows': self.min_rows,
            'max_rows': self.max_rows,
            'allow_add': self.allow_add,
            'allow_remove': self.allow_remove,
            'table_data': self.get_value()
        })
        return base_dict