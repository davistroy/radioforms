"""Form list widget for managing and navigating between forms.

This module provides the form list widget that displays saved forms with metadata,
enables navigation between forms, and supports form management operations like
creation, editing, deletion, and search/filter functionality.

The widget follows the established PySide6 patterns and integrates with the
form factory system for comprehensive multi-form management.

Example:
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> 
    >>> app = QApplication(sys.argv)
    >>> form_list = FormListWidget()
    >>> form_list.show()
    >>> 
    >>> # Connect to form selection events
    >>> form_list.form_selected.connect(handle_form_selection)
    >>> form_list.form_creation_requested.connect(handle_form_creation)
    >>> 
    >>> app.exec()

Classes:
    FormListItem: Individual item in the form list with metadata
    FormListWidget: Main form list widget with navigation and management
    FormSearchWidget: Search and filter controls for forms
    FormListModel: Data model for form list display

Functions:
    create_form_list_widget: Factory function for creating form list widgets
    format_form_metadata: Utility for formatting form metadata display

Notes:
    This implementation follows the pyside6-rules.md guidelines for proper
    widget architecture, signal-slot patterns, and keyboard accessibility.
    All UI components support both mouse and keyboard navigation.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set, Callable
from dataclasses import dataclass
from enum import Enum

# Handle PySide6 imports gracefully for testing environments
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem,
        QPushButton, QLabel, QLineEdit, QComboBox, QGroupBox, QMessageBox, QFrame,
        QScrollArea, QSizePolicy, QApplication, QMenu, QAbstractItemView,
        QHeaderView, QTreeWidget, QTreeWidgetItem, QSplitter, QTabWidget,
        QProgressBar, QCheckBox, QDateEdit, QSpacerItem, QToolButton, QButtonGroup
    )
    from PySide6.QtCore import (
        Signal, Qt, QTimer, QModelIndex, QStringListModel, QDate, QSize, 
        QPropertyAnimation, QEasingCurve, QRect, QPoint
    )
    from PySide6.QtGui import (
        QFont, QPalette, QColor, QIcon, QPixmap, QKeySequence, QAction,
        QPainter, QFontMetrics, QBrush, QPen
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Create stub classes for testing environments
    PYSIDE6_AVAILABLE = False
    
    class QWidget:
        def __init__(self, parent=None): 
            self.parent = parent
        def show(self): pass
        def hide(self): pass
        def setMinimumSize(self, w, h): pass
        def setMaximumSize(self, w, h): pass
        def setSizePolicy(self, h, v): pass
    
    class QListWidget(QWidget):
        def addItem(self, item): pass
        def clear(self): pass
        def currentItem(self): return None
        def takeItem(self, row): return None
        def count(self): return 0
    
    class QListWidgetItem:
        def __init__(self, text="", parent=None):
            self.text_value = text
        def setText(self, text): self.text_value = text
        def text(self): return self.text_value
        def setData(self, role, data): pass
        def data(self, role): return None
    
    class Signal:
        def __init__(self, *args): pass
        def connect(self, slot): pass
        def emit(self, *args): pass
        def disconnect(self): pass
    
    class QTimer:
        def __init__(self): pass
        def setSingleShot(self, single): pass
        def start(self, ms): pass
        def stop(self): pass
        def timeout(self): return Signal()
    
    Qt = type('Qt', (), {
        'ItemDataRole': type('ItemDataRole', (), {'UserRole': 256})(),
        'ContextMenuPolicy': type('ContextMenuPolicy', (), {'ActionsContextMenu': 3})(),
        'Key': type('Key', (), {'Key_Delete': 16777223, 'Key_F2': 16777245})()
    })()

# Import form system with fallback handling
try:
    from ...models.base_form import BaseForm, FormType, FormStatus, FormMetadata
    from ..forms.form_factory import FormWidgetFactory, create_form_widget_by_type
except ImportError:
    # For standalone testing
    sys.path.append('.')
    try:
        from src.models.base_form import BaseForm, FormType, FormStatus, FormMetadata
        from src.ui.forms.form_factory import FormWidgetFactory, create_form_widget_by_type
    except ImportError:
        # Create stub classes for testing
        BaseForm = object
        FormType = type('FormType', (), {'ICS_213': 'ICS-213', 'ICS_214': 'ICS-214'})()
        FormStatus = type('FormStatus', (), {'DRAFT': 'draft', 'COMPLETED': 'completed'})()
        FormMetadata = object
        FormWidgetFactory = type('FormWidgetFactory', (), {})()
        create_form_widget_by_type = lambda x: None


class FormSortOrder(Enum):
    """Form list sorting options."""
    
    MODIFIED_DESC = "modified_desc"
    MODIFIED_ASC = "modified_asc"
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    TYPE_ASC = "type_asc"
    TYPE_DESC = "type_desc"


class FormFilterType(Enum):
    """Form list filtering options."""
    
    ALL = "all"
    DRAFTS = "drafts"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    ICS_213_ONLY = "ics_213_only"
    ICS_214_ONLY = "ics_214_only"
    RECENT = "recent"  # Last 7 days
    TODAY = "today"


@dataclass
class FormListItemData:
    """Data structure for form list items.
    
    Contains all metadata and form reference needed for display
    and operations in the form list widget.
    
    Attributes:
        form (BaseForm): Reference to the actual form instance.
        display_name (str): Human-readable name for display.
        form_type_name (str): Form type display name.
        status_text (str): Human-readable status.
        modified_text (str): Formatted modification time.
        created_text (str): Formatted creation time.
        tags (Set[str]): Set of form tags.
        has_unsaved_changes (bool): Whether form has unsaved changes.
    """
    
    form: BaseForm
    display_name: str = ""
    form_type_name: str = ""
    status_text: str = ""
    modified_text: str = ""
    created_text: str = ""
    tags: Set[str] = None
    has_unsaved_changes: bool = False
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.tags is None:
            self.tags = set()


class FormListItem(QListWidgetItem):
    """Custom list widget item for form display.
    
    Extends QListWidgetItem to provide rich form metadata display
    with proper formatting, icons, and status indicators.
    
    Example:
        >>> form = create_new_ics213()
        >>> item = FormListItem(form)
        >>> list_widget.addItem(item)
    """
    
    def __init__(self, form: BaseForm, parent: Optional[QWidget] = None) -> None:
        """Initialize form list item.
        
        Args:
            form: Form instance to represent.
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        
        self.form = form
        self.item_data = self._create_item_data(form)
        
        # Set item data for sorting and filtering
        self.setData(Qt.ItemDataRole.UserRole, self.item_data)
        
        # Update display
        self.update_display()
    
    def _create_item_data(self, form: BaseForm) -> FormListItemData:
        """Create item data from form instance.
        
        Args:
            form: Form instance to extract data from.
            
        Returns:
            FormListItemData: Structured item data.
        """
        # Get form type display name
        form_type = form.get_form_type()
        if hasattr(FormWidgetFactory, 'get_form_display_name'):
            form_type_name = FormWidgetFactory.get_form_display_name(form_type)
        else:
            form_type_name = form_type.value if hasattr(form_type, 'value') else str(form_type)
        
        # Create display name from form content
        display_name = self._generate_display_name(form)
        
        # Format status
        status = form.get_status() if hasattr(form, 'get_status') else FormStatus.DRAFT
        status_text = status.value if hasattr(status, 'value') else str(status)
        status_text = status_text.replace('_', ' ').title()
        
        # Format timestamps
        modified_date = form.get_modified_date() if hasattr(form, 'get_modified_date') else datetime.now()
        created_date = form.get_created_date() if hasattr(form, 'get_created_date') else datetime.now()
        
        modified_text = self._format_relative_time(modified_date)
        created_text = self._format_relative_time(created_date)
        
        # Get tags
        tags = form.get_tags() if hasattr(form, 'get_tags') else set()
        
        return FormListItemData(
            form=form,
            display_name=display_name,
            form_type_name=form_type_name,
            status_text=status_text,
            modified_text=modified_text,
            created_text=created_text,
            tags=tags,
            has_unsaved_changes=False  # TODO: Implement dirty checking
        )
    
    def _generate_display_name(self, form: BaseForm) -> str:
        """Generate a display name from form content.
        
        Args:
            form: Form instance to generate name from.
            
        Returns:
            str: Human-readable display name.
        """
        form_type = form.get_form_type()
        
        # Try to get meaningful content from form
        try:
            if hasattr(form, 'data'):
                data = form.data
                
                if form_type.value == 'ICS-213' and hasattr(data, 'subject'):
                    if data.subject and data.subject.strip():
                        return data.subject.strip()[:50]
                    elif hasattr(data, 'to') and hasattr(data.to, 'name') and data.to.name:
                        return f"Message to {data.to.name}"
                    elif hasattr(data, 'incident_name') and data.incident_name:
                        return f"Message - {data.incident_name}"
                
                elif form_type.value == 'ICS-214' and hasattr(data, 'incident_name'):
                    if data.incident_name and data.incident_name.strip():
                        name_part = data.name if hasattr(data, 'name') and data.name else ""
                        if name_part:
                            return f"{data.incident_name} - {name_part}"
                        return data.incident_name
                
                # Generic fallback - try incident_name
                if hasattr(data, 'incident_name') and data.incident_name:
                    return data.incident_name[:50]
        
        except Exception:
            pass  # Fallback to generic name
        
        # Final fallback
        form_id = form.get_form_id() if hasattr(form, 'get_form_id') else "Unknown"
        return f"Untitled {form_type.value} ({form_id[:8]})"
    
    def _format_relative_time(self, dt: datetime) -> str:
        """Format datetime as relative time.
        
        Args:
            dt: Datetime to format.
            
        Returns:
            str: Relative time string (e.g., "2 hours ago").
        """
        try:
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 7:
                return dt.strftime("%Y-%m-%d")
            elif diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        except Exception:
            return "Unknown"
    
    def update_display(self) -> None:
        """Update the item's display text and appearance."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Create multi-line display text
        lines = []
        
        # Main line: display name with status indicator
        main_line = self.item_data.display_name
        if self.item_data.has_unsaved_changes:
            main_line += " •"  # Bullet to indicate unsaved changes
        lines.append(main_line)
        
        # Secondary line: form type and modification time
        secondary_line = f"{self.item_data.form_type_name} • {self.item_data.modified_text}"
        lines.append(secondary_line)
        
        # Status and tags line (if any)
        status_parts = [self.item_data.status_text]
        if self.item_data.tags:
            tag_text = ", ".join(sorted(self.item_data.tags)[:3])  # Show first 3 tags
            if len(self.item_data.tags) > 3:
                tag_text += f" +{len(self.item_data.tags) - 3}"
            status_parts.append(f"Tags: {tag_text}")
        
        if len(status_parts) > 1 or status_parts[0] != "Draft":
            lines.append(" • ".join(status_parts))
        
        # Set the display text
        self.setText("\n".join(lines))
        
        # Set tooltip with full details
        self.setToolTip(self._create_tooltip())
    
    def _create_tooltip(self) -> str:
        """Create detailed tooltip for the item.
        
        Returns:
            str: Formatted tooltip text.
        """
        lines = [
            f"Form: {self.item_data.form_type_name}",
            f"Status: {self.item_data.status_text}",
            f"Modified: {self.item_data.modified_text}",
            f"Created: {self.item_data.created_text}",
        ]
        
        if self.item_data.tags:
            lines.append(f"Tags: {', '.join(sorted(self.item_data.tags))}")
        
        form_id = self.form.get_form_id() if hasattr(self.form, 'get_form_id') else "Unknown"
        lines.append(f"ID: {form_id}")
        
        return "\n".join(lines)
    
    def matches_filter(self, filter_type: FormFilterType, search_text: str = "") -> bool:
        """Check if item matches filter criteria.
        
        Args:
            filter_type: Type of filter to apply.
            search_text: Text to search for.
            
        Returns:
            bool: True if item matches filter criteria.
        """
        # Search text filter
        if search_text:
            search_lower = search_text.lower()
            searchable_text = " ".join([
                self.item_data.display_name.lower(),
                self.item_data.form_type_name.lower(),
                self.item_data.status_text.lower(),
                " ".join(self.item_data.tags).lower()
            ])
            
            if search_lower not in searchable_text:
                return False
        
        # Type and status filters
        if filter_type == FormFilterType.ALL:
            return True
        elif filter_type == FormFilterType.DRAFTS:
            return "draft" in self.item_data.status_text.lower()
        elif filter_type == FormFilterType.COMPLETED:
            return "completed" in self.item_data.status_text.lower()
        elif filter_type == FormFilterType.SUBMITTED:
            return "submitted" in self.item_data.status_text.lower()
        elif filter_type == FormFilterType.ICS_213_ONLY:
            return "213" in self.item_data.form_type_name
        elif filter_type == FormFilterType.ICS_214_ONLY:
            return "214" in self.item_data.form_type_name
        elif filter_type == FormFilterType.TODAY:
            try:
                modified_date = self.form.get_modified_date()
                return modified_date.date() == datetime.now().date()
            except Exception:
                return False
        elif filter_type == FormFilterType.RECENT:
            try:
                modified_date = self.form.get_modified_date()
                week_ago = datetime.now() - timedelta(days=7)
                return modified_date >= week_ago
            except Exception:
                return False
        
        return True


class FormSearchWidget(QWidget):
    """Search and filter controls for the form list.
    
    Provides search box, filter dropdown, and sort controls
    for finding and organizing forms in the list.
    
    Signals:
        search_changed: Emitted when search text changes (str)
        filter_changed: Emitted when filter selection changes (FormFilterType)
        sort_changed: Emitted when sort order changes (FormSortOrder)
    """
    
    search_changed = Signal(str)
    filter_changed = Signal(object)  # FormFilterType
    sort_changed = Signal(object)    # FormSortOrder
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize search widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        if not PYSIDE6_AVAILABLE:
            return
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Search box
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search forms...")
        self.search_box.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # Filter and sort controls
        controls_layout = QHBoxLayout()
        
        # Filter dropdown
        filter_label = QLabel("Filter:")
        controls_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Forms", FormFilterType.ALL)
        self.filter_combo.addItem("Drafts", FormFilterType.DRAFTS)
        self.filter_combo.addItem("Completed", FormFilterType.COMPLETED)
        self.filter_combo.addItem("Submitted", FormFilterType.SUBMITTED)
        self.filter_combo.addItem("ICS-213 Only", FormFilterType.ICS_213_ONLY)
        self.filter_combo.addItem("ICS-214 Only", FormFilterType.ICS_214_ONLY)
        self.filter_combo.addItem("Recent (7 days)", FormFilterType.RECENT)
        self.filter_combo.addItem("Today", FormFilterType.TODAY)
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addItem(QSpacerItem(10, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        
        # Sort dropdown
        sort_label = QLabel("Sort:")
        controls_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Modified (Newest)", FormSortOrder.MODIFIED_DESC)
        self.sort_combo.addItem("Modified (Oldest)", FormSortOrder.MODIFIED_ASC)
        self.sort_combo.addItem("Created (Newest)", FormSortOrder.CREATED_DESC)
        self.sort_combo.addItem("Created (Oldest)", FormSortOrder.CREATED_ASC)
        self.sort_combo.addItem("Name (A-Z)", FormSortOrder.NAME_ASC)
        self.sort_combo.addItem("Name (Z-A)", FormSortOrder.NAME_DESC)
        self.sort_combo.addItem("Type (A-Z)", FormSortOrder.TYPE_ASC)
        self.sort_combo.addItem("Type (Z-A)", FormSortOrder.TYPE_DESC)
        controls_layout.addWidget(self.sort_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        if not PYSIDE6_AVAILABLE:
            return
        
        self.search_box.textChanged.connect(self.search_changed.emit)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
    
    def on_filter_changed(self) -> None:
        """Handle filter selection change."""
        filter_type = self.filter_combo.currentData()
        if filter_type:
            self.filter_changed.emit(filter_type)
    
    def on_sort_changed(self) -> None:
        """Handle sort selection change."""
        sort_order = self.sort_combo.currentData()
        if sort_order:
            self.sort_changed.emit(sort_order)
    
    def get_search_text(self) -> str:
        """Get current search text.
        
        Returns:
            str: Current search text.
        """
        if PYSIDE6_AVAILABLE and hasattr(self, 'search_box'):
            return self.search_box.text()
        return ""
    
    def get_current_filter(self) -> FormFilterType:
        """Get current filter selection.
        
        Returns:
            FormFilterType: Current filter type.
        """
        if PYSIDE6_AVAILABLE and hasattr(self, 'filter_combo'):
            return self.filter_combo.currentData() or FormFilterType.ALL
        return FormFilterType.ALL
    
    def get_current_sort(self) -> FormSortOrder:
        """Get current sort selection.
        
        Returns:
            FormSortOrder: Current sort order.
        """
        if PYSIDE6_AVAILABLE and hasattr(self, 'sort_combo'):
            return self.sort_combo.currentData() or FormSortOrder.MODIFIED_DESC
        return FormSortOrder.MODIFIED_DESC


class FormListWidget(QWidget):
    """Main form list widget with navigation and management capabilities.
    
    This widget provides the primary interface for viewing, navigating,
    and managing forms in the RadioForms application. It includes search,
    filtering, context menus, and keyboard navigation.
    
    Signals:
        form_selected: Emitted when a form is selected (BaseForm)
        form_activated: Emitted when a form is double-clicked (BaseForm)
        form_creation_requested: Emitted when new form creation is requested (FormType)
        form_deletion_requested: Emitted when form deletion is requested (BaseForm)
        form_duplication_requested: Emitted when form duplication is requested (BaseForm)
        
    Example:
        >>> widget = FormListWidget()
        >>> widget.form_activated.connect(handle_form_editing)
        >>> widget.add_form(my_form)
        >>> widget.show()
    """
    
    form_selected = Signal(object)        # BaseForm
    form_activated = Signal(object)       # BaseForm (double-click)
    form_creation_requested = Signal(object)  # FormType
    form_deletion_requested = Signal(object)  # BaseForm
    form_duplication_requested = Signal(object)  # BaseForm
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize form list widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        
        # Internal state
        self.forms: List[BaseForm] = []
        self.current_search = ""
        self.current_filter = FormFilterType.ALL
        self.current_sort = FormSortOrder.MODIFIED_DESC
        
        # Initialize UI attributes for testing when PySide6 not available
        if not PYSIDE6_AVAILABLE:
            self.form_list = QListWidget()
            self.status_label = None
            self.search_widget = FormSearchWidget()
        
        # Set up UI
        self.setup_ui()
        self.setup_connections()
        self.setup_context_menu()
        
        # Initialize with empty state
        self.update_display()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        if not PYSIDE6_AVAILABLE:
            return
            
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header with title and new form button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Forms")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        if PYSIDE6_AVAILABLE:
            self.new_form_btn = QPushButton("New Form")
            self.new_form_btn.clicked.connect(self.show_new_form_dialog)
            header_layout.addWidget(self.new_form_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter controls
        self.search_widget = FormSearchWidget()
        layout.addWidget(self.search_widget)
        
        # Form list
        if PYSIDE6_AVAILABLE:
            self.form_list = QListWidget()
            self.form_list.setAlternatingRowColors(True)
            self.form_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            layout.addWidget(self.form_list)
        else:
            # Placeholder for testing
            self.form_list = QListWidget()
            
        # Status bar
        self.status_label = QLabel("0 forms")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Set minimum size
        if PYSIDE6_AVAILABLE:
            self.setMinimumSize(300, 400)
    
    def setup_connections(self) -> None:
        """Set up signal connections."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Search widget connections
        self.search_widget.search_changed.connect(self.on_search_changed)
        self.search_widget.filter_changed.connect(self.on_filter_changed)
        self.search_widget.sort_changed.connect(self.on_sort_changed)
        
        # List widget connections
        self.form_list.currentItemChanged.connect(self.on_selection_changed)
        self.form_list.itemDoubleClicked.connect(self.on_item_activated)
    
    def setup_context_menu(self) -> None:
        """Set up context menu actions."""
        if not PYSIDE6_AVAILABLE:
            return
        
        self.form_list.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        
        # Open action
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Return"))
        open_action.triggered.connect(self.open_selected_form)
        self.form_list.addAction(open_action)
        
        # Edit action
        edit_action = QAction("Edit", self)
        edit_action.setShortcut(QKeySequence("F2"))
        edit_action.triggered.connect(self.open_selected_form)
        self.form_list.addAction(edit_action)
        
        # Separator
        separator1 = QAction(self)
        separator1.setSeparator(True)
        self.form_list.addAction(separator1)
        
        # Duplicate action
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        duplicate_action.triggered.connect(self.duplicate_selected_form)
        self.form_list.addAction(duplicate_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence("Delete"))
        delete_action.triggered.connect(self.delete_selected_form)
        self.form_list.addAction(delete_action)
        
        # Separator
        separator2 = QAction(self)
        separator2.setSeparator(True)
        self.form_list.addAction(separator2)
        
        # Properties action
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(self.show_form_properties)
        self.form_list.addAction(properties_action)
    
    def add_form(self, form: BaseForm) -> None:
        """Add a form to the list.
        
        Args:
            form: Form instance to add to the list.
        """
        if form not in self.forms:
            self.forms.append(form)
            self.update_display()
    
    def remove_form(self, form: BaseForm) -> bool:
        """Remove a form from the list.
        
        Args:
            form: Form instance to remove from the list.
            
        Returns:
            bool: True if form was removed, False if not found.
        """
        if form in self.forms:
            self.forms.remove(form)
            self.update_display()
            return True
        return False
    
    def get_selected_form(self) -> Optional[BaseForm]:
        """Get the currently selected form.
        
        Returns:
            BaseForm: Selected form or None if no selection.
        """
        if not PYSIDE6_AVAILABLE:
            return None
        
        current_item = self.form_list.currentItem()
        if current_item and isinstance(current_item, FormListItem):
            return current_item.form
        return None
    
    def set_selected_form(self, form: BaseForm) -> bool:
        """Set the selected form.
        
        Args:
            form: Form to select in the list.
            
        Returns:
            bool: True if form was found and selected.
        """
        if not PYSIDE6_AVAILABLE:
            return False
        
        for i in range(self.form_list.count()):
            item = self.form_list.item(i)
            if isinstance(item, FormListItem) and item.form == form:
                self.form_list.setCurrentItem(item)
                return True
        return False
    
    def update_display(self) -> None:
        """Update the form list display with current filters and sorting."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Clear current display
        self.form_list.clear()
        
        # Filter forms
        filtered_forms = []
        for form in self.forms:
            item_data = FormListItem(form)._create_item_data(form)
            temp_item = FormListItem(form)
            temp_item.item_data = item_data
            
            if temp_item.matches_filter(self.current_filter, self.current_search):
                filtered_forms.append((form, item_data))
        
        # Sort forms
        filtered_forms = self._sort_forms(filtered_forms)
        
        # Add to display
        for form, item_data in filtered_forms:
            item = FormListItem(form)
            self.form_list.addItem(item)
        
        # Update status
        total_count = len(self.forms)
        shown_count = len(filtered_forms)
        
        if hasattr(self, 'status_label') and self.status_label:
            if total_count == shown_count:
                self.status_label.setText(f"{total_count} form{'s' if total_count != 1 else ''}")
            else:
                self.status_label.setText(f"{shown_count} of {total_count} forms")
    
    def _sort_forms(self, forms_with_data: List[tuple]) -> List[tuple]:
        """Sort forms according to current sort order.
        
        Args:
            forms_with_data: List of (form, item_data) tuples.
            
        Returns:
            List[tuple]: Sorted list of (form, item_data) tuples.
        """
        def sort_key(form_data_tuple):
            form, item_data = form_data_tuple
            
            if self.current_sort == FormSortOrder.MODIFIED_DESC:
                return form.get_modified_date() if hasattr(form, 'get_modified_date') else datetime.min
            elif self.current_sort == FormSortOrder.MODIFIED_ASC:
                return form.get_modified_date() if hasattr(form, 'get_modified_date') else datetime.max
            elif self.current_sort == FormSortOrder.CREATED_DESC:
                return form.get_created_date() if hasattr(form, 'get_created_date') else datetime.min
            elif self.current_sort == FormSortOrder.CREATED_ASC:
                return form.get_created_date() if hasattr(form, 'get_created_date') else datetime.max
            elif self.current_sort == FormSortOrder.NAME_ASC:
                return item_data.display_name.lower()
            elif self.current_sort == FormSortOrder.NAME_DESC:
                return item_data.display_name.lower()
            elif self.current_sort == FormSortOrder.TYPE_ASC:
                return item_data.form_type_name.lower()
            elif self.current_sort == FormSortOrder.TYPE_DESC:
                return item_data.form_type_name.lower()
            else:
                return datetime.now()
        
        reverse = self.current_sort in [
            FormSortOrder.MODIFIED_DESC, FormSortOrder.CREATED_DESC,
            FormSortOrder.NAME_DESC, FormSortOrder.TYPE_DESC
        ]
        
        return sorted(forms_with_data, key=sort_key, reverse=reverse)
    
    def on_search_changed(self, search_text: str) -> None:
        """Handle search text change.
        
        Args:
            search_text: New search text.
        """
        self.current_search = search_text
        self.update_display()
    
    def on_filter_changed(self, filter_type: FormFilterType) -> None:
        """Handle filter change.
        
        Args:
            filter_type: New filter type.
        """
        self.current_filter = filter_type
        self.update_display()
    
    def on_sort_changed(self, sort_order: FormSortOrder) -> None:
        """Handle sort order change.
        
        Args:
            sort_order: New sort order.
        """
        self.current_sort = sort_order
        self.update_display()
    
    def on_selection_changed(self, current_item, previous_item) -> None:
        """Handle selection change in the form list.
        
        Args:
            current_item: Currently selected item.
            previous_item: Previously selected item.
        """
        if isinstance(current_item, FormListItem):
            self.form_selected.emit(current_item.form)
    
    def on_item_activated(self, item) -> None:
        """Handle item activation (double-click).
        
        Args:
            item: Activated list item.
        """
        if isinstance(item, FormListItem):
            self.form_activated.emit(item.form)
    
    def show_new_form_dialog(self) -> None:
        """Show new form creation dialog."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Import form selection widget
        try:
            from ..forms.form_factory import FormSelectionWidget
            
            dialog = FormSelectionWidget(self)
            dialog.setWindowTitle("Create New Form")
            dialog.form_creation_requested.connect(self.form_creation_requested.emit)
            dialog.show()
            
        except ImportError:
            # Fallback - emit a default form type
            self.form_creation_requested.emit(FormType.ICS_213)
    
    def open_selected_form(self) -> None:
        """Open the currently selected form for editing."""
        selected_form = self.get_selected_form()
        if selected_form:
            self.form_activated.emit(selected_form)
    
    def duplicate_selected_form(self) -> None:
        """Duplicate the currently selected form."""
        selected_form = self.get_selected_form()
        if selected_form:
            self.form_duplication_requested.emit(selected_form)
    
    def delete_selected_form(self) -> None:
        """Delete the currently selected form."""
        if not PYSIDE6_AVAILABLE:
            return
        
        selected_form = self.get_selected_form()
        if selected_form:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Delete Form",
                f"Are you sure you want to delete this form?\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.form_deletion_requested.emit(selected_form)
    
    def show_form_properties(self) -> None:
        """Show properties dialog for the selected form."""
        if not PYSIDE6_AVAILABLE:
            return
        
        selected_form = self.get_selected_form()
        if selected_form:
            # Create properties dialog
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Form Properties")
            dialog.setIcon(QMessageBox.Icon.Information)
            
            # Build properties text
            props = []
            props.append(f"Form Type: {selected_form.get_form_type().value}")
            props.append(f"Form ID: {selected_form.get_form_id()}")
            props.append(f"Status: {selected_form.get_status().value}")
            props.append(f"Created: {selected_form.get_created_date()}")
            props.append(f"Modified: {selected_form.get_modified_date()}")
            
            tags = selected_form.get_tags()
            if tags:
                props.append(f"Tags: {', '.join(sorted(tags))}")
            
            dialog.setText("\n".join(props))
            dialog.exec()
    
    def refresh(self) -> None:
        """Refresh the form list display."""
        self.update_display()


# Utility functions

def create_form_list_widget(parent: Optional[QWidget] = None) -> FormListWidget:
    """Factory function for creating form list widgets.
    
    Args:
        parent: Parent widget for the form list.
        
    Returns:
        FormListWidget: New form list widget instance.
    """
    return FormListWidget(parent)


def format_form_metadata(form: BaseForm) -> Dict[str, str]:
    """Utility function for formatting form metadata for display.
    
    Args:
        form: Form to extract and format metadata from.
        
    Returns:
        Dict[str, str]: Dictionary of formatted metadata fields.
    """
    metadata = {}
    
    try:
        metadata['form_type'] = form.get_form_type().value
        metadata['form_id'] = form.get_form_id()
        metadata['status'] = form.get_status().value
        metadata['created'] = form.get_created_date().strftime("%Y-%m-%d %H:%M")
        metadata['modified'] = form.get_modified_date().strftime("%Y-%m-%d %H:%M")
        
        tags = form.get_tags()
        metadata['tags'] = ', '.join(sorted(tags)) if tags else 'None'
        
    except Exception as e:
        metadata['error'] = f"Error formatting metadata: {e}"
    
    return metadata


# Example usage and testing
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        app = QApplication(sys.argv)
        
        # Create form list widget
        form_list = FormListWidget()
        form_list.setWindowTitle("RadioForms - Form List")
        form_list.resize(400, 600)
        form_list.show()
        
        # Handle form events
        def handle_form_activated(form):
            print(f"Form activated: {form.get_form_type().value}")
        
        def handle_form_creation(form_type):
            print(f"Form creation requested: {form_type.value}")
        
        def handle_form_deletion(form):
            print(f"Form deletion requested: {form.get_form_type().value}")
            form_list.remove_form(form)
        
        form_list.form_activated.connect(handle_form_activated)
        form_list.form_creation_requested.connect(handle_form_creation)
        form_list.form_deletion_requested.connect(handle_form_deletion)
        
        # Add some sample forms for testing
        try:
            from ...models.base_form import create_form_from_type, FormType
            
            for i in range(5):
                form_213 = create_form_from_type(FormType.ICS_213)
                form_214 = create_form_from_type(FormType.ICS_214)
                
                if form_213:
                    form_list.add_form(form_213)
                if form_214:
                    form_list.add_form(form_214)
                    
        except ImportError:
            print("Sample forms not available - form factories not imported")
        
        sys.exit(app.exec())
    else:
        print("PySide6 not available - form list widget available for testing")
        
        # Test widget functionality without UI
        form_list = FormListWidget()
        print("Form list widget created successfully")
        print(f"Initial form count: {len(form_list.forms)}")
        
        # Test search and filter functionality
        search_widget = FormSearchWidget()
        print("Search widget created successfully")
        print(f"Default filter: {search_widget.get_current_filter()}")
        print(f"Default sort: {search_widget.get_current_sort()}")