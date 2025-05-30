# PySide6 GUI Application Coding Rules: Best Practices for AI-Assisted Development

## Core Philosophy

**The #1 Rule**: Keep the UI thread responsive. Separate business logic from presentation.

### PySide6 Fundamental Principles

1. **Never Block the Main Thread**: Long operations must run in separate threads
2. **Model-View Separation**: Business logic should never depend on UI
3. **Signal-Slot Architecture**: Use Qt's event system for loose coupling
4. **Resource Management**: Properly parent widgets and clean up resources
5. **Platform Awareness**: Test on all target platforms

## 🔧 Essential Setup & Configuration

### Always Use Context7 MCP

**CRITICAL**: Before implementing ANY PySide6 feature:
```python
# Always check latest documentation with context7
# Use: context7 /pyside/pyside-setup for official PySide6 docs
# This ensures you're using the most current APIs and best practices
```

### Project Initialization Checklist

1. **Virtual Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install PySide6
pip install PySide6
```

2. **Project Structure**
```
project-name/
├── src/
│   ├── main.py              # Application entry point
│   ├── app/
│   │   ├── __init__.py
│   │   └── application.py   # QApplication setup
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main window class
│   │   ├── dialogs/         # Dialog classes
│   │   ├── widgets/         # Custom widgets
│   │   └── resources/       # Icons, images
│   ├── models/              # Data models
│   │   └── __init__.py
│   ├── controllers/         # Business logic
│   │   └── __init__.py
│   ├── utils/               # Utilities
│   │   └── __init__.py
│   └── resources/
│       ├── icons/
│       ├── styles/
│       │   └── style.qss    # Qt stylesheets
│       └── ui/              # .ui files from Qt Designer
├── tests/
├── docs/
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

3. **Main Application Template**
```python
# main.py
import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from app.application import Application

# Configure logging before Qt
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Application entry point."""
    # High DPI support
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setOrganizationName("YourCompany")
    app.setOrganizationDomain("yourcompany.com")
    app.setApplicationName("YourApp")
    
    # Create and show main application
    main_app = Application()
    main_app.show()
    
    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## 🚨 PySide6 Specific Anti-Patterns

### 1. Blocking the Main Thread
```python
# ❌ AVOID: Long operations in UI thread
class MainWindow(QMainWindow):
    def on_button_clicked(self):
        # This freezes the UI!
        result = requests.get("https://api.example.com/large-data")
        self.display_result(result.json())

# ✅ DO: Use QThread or QThreadPool
from PySide6.QtCore import QThread, Signal, QThreadPool, QRunnable

class DataFetcher(QThread):
    data_received = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.data_received.emit(response.json())
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def on_button_clicked(self):
        self.fetcher = DataFetcher("https://api.example.com/large-data")
        self.fetcher.data_received.connect(self.display_result)
        self.fetcher.error_occurred.connect(self.show_error)
        self.fetcher.start()
```

### 2. Memory Leaks from Improper Parenting
```python
# ❌ AVOID: Widgets without parents
def create_dialog():
    dialog = QDialog()  # No parent - won't be cleaned up!
    dialog.show()
    return dialog

# ✅ DO: Always provide parent widgets
def create_dialog(parent):
    dialog = QDialog(parent)  # Will be cleaned up with parent
    dialog.show()
    return dialog
```

### 3. Direct UI Updates from Threads
```python
# ❌ AVOID: Updating UI from worker thread
class Worker(QThread):
    def run(self):
        for i in range(100):
            # This will crash!
            self.label.setText(f"Progress: {i}%")

# ✅ DO: Use signals for thread communication
class Worker(QThread):
    progress_updated = Signal(int)
    
    def run(self):
        for i in range(100):
            self.progress_updated.emit(i)
            self.msleep(10)

# In main window
worker.progress_updated.connect(
    lambda val: self.label.setText(f"Progress: {val}%")
)
```

### 4. Hardcoded Sizes and Positions
```python
# ❌ AVOID: Fixed sizes
button = QPushButton("Click me")
button.resize(100, 30)  # Won't scale properly!
button.move(50, 50)     # Fixed position!

# ✅ DO: Use layouts
layout = QVBoxLayout()
button = QPushButton("Click me")
button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
layout.addWidget(button)
```

## 📋 UI Development Best Practices

### 1. Main Window Structure
```python
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, 
    QStatusBar, QToolBar, QDockWidget
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon

class MainWindow(QMainWindow):
    """Application main window."""
    
    # Define signals at class level
    file_opened = Signal(str)
    status_message = Signal(str, int)  # message, timeout_ms
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Application Title")
        self.setMinimumSize(800, 600)
        
        # Setup UI components
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_dock_widgets()
        self._setup_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load settings
        self._load_settings()
    
    def _setup_ui(self):
        """Setup central widget and main layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add main content widget
        from .widgets.content_widget import ContentWidget
        self.content_widget = ContentWidget()
        self.main_layout.addWidget(self.content_widget)
    
    def _setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Open action
        self.open_action = QAction(
            QIcon(":/icons/open.png"), 
            "&Open...", 
            self
        )
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Open a file")
        self.open_action.triggered.connect(self._on_open)
        file_menu.addAction(self.open_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    @Slot()
    def _on_open(self):
        """Handle open action."""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*)"
        )
        
        if filename:
            self.file_opened.emit(filename)
            self.status_message.emit(f"Opened: {filename}", 5000)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._save_settings()
        event.accept()
    
    def _save_settings(self):
        """Save window geometry and state."""
        from PySide6.QtCore import QSettings
        
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def _load_settings(self):
        """Restore window geometry and state."""
        from PySide6.QtCore import QSettings
        
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
```

### 2. Custom Widgets
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation
from PySide6.QtGui import QPainter, QColor, QPaintEvent

class CustomWidget(QWidget):
    """Custom widget with animation support."""
    
    # Custom signals
    value_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Private attributes
        self._value = 0
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(250)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        self.setMinimumSize(200, 100)
        
    # Qt Property for animation
    def get_value(self):
        return self._value
    
    def set_value(self, value):
        if self._value != value:
            self._value = value
            self.value_changed.emit(value)
            self.update()  # Trigger repaint
    
    value = Property(int, get_value, set_value)
    
    def animate_to(self, target_value):
        """Animate value change."""
        self._animation.setStartValue(self._value)
        self._animation.setEndValue(target_value)
        self._animation.start()
    
    def paintEvent(self, event: QPaintEvent):
        """Custom painting."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Draw value bar
        bar_width = int(self.width() * (self._value / 100.0))
        painter.fillRect(0, 0, bar_width, self.height(), QColor(52, 152, 219))
        
        # Draw text
        painter.drawText(
            self.rect(), 
            Qt.AlignCenter, 
            f"{self._value}%"
        )
```

### 3. Dialogs and Forms
```python
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from typing import Optional, Dict

class SettingsDialog(QDialog):
    """Application settings dialog."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, current_settings: Dict, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 300)
        
        # Store current settings
        self._settings = current_settings.copy()
        
        # Setup UI
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Create dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Server settings
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("example.com")
        form_layout.addRow("Server:", self.server_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8080)
        form_layout.addRow("Port:", self.port_input)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        form_layout.addRow("Theme:", self.theme_combo)
        
        # Options
        self.auto_save_check = QCheckBox("Enable auto-save")
        form_layout.addRow(self.auto_save_check)
        
        self.debug_check = QCheckBox("Enable debug mode")
        form_layout.addRow(self.debug_check)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_settings(self):
        """Load current settings into UI."""
        self.server_input.setText(self._settings.get("server", ""))
        self.port_input.setValue(self._settings.get("port", 8080))
        self.theme_combo.setCurrentText(self._settings.get("theme", "Light"))
        self.auto_save_check.setChecked(self._settings.get("auto_save", False))
        self.debug_check.setChecked(self._settings.get("debug", False))
    
    def get_settings(self) -> Dict:
        """Get current settings from UI."""
        return {
            "server": self.server_input.text(),
            "port": self.port_input.value(),
            "theme": self.theme_combo.currentText(),
            "auto_save": self.auto_save_check.isChecked(),
            "debug": self.debug_check.isChecked()
        }
    
    def accept(self):
        """Handle dialog acceptance."""
        new_settings = self.get_settings()
        if new_settings != self._settings:
            self.settings_changed.emit(new_settings)
        super().accept()
```

### 4. Model-View Architecture
```python
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QHeaderView
from typing import List, Any

class DataModel(QAbstractTableModel):
    """Custom table model for data display."""
    
    def __init__(self, headers: List[str], parent=None):
        super().__init__(parent)
        self._headers = headers
        self._data: List[List[Any]] = []
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """Return data for given index and role."""
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if role == Qt.DisplayRole:
            return str(self._data[row][col])
        elif role == Qt.TextAlignmentRole:
            if isinstance(self._data[row][col], (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.BackgroundRole:
            # Alternate row colors
            if row % 2 == 0:
                return QColor(240, 240, 240)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        """Return header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
    
    def add_data(self, row_data: List[Any]):
        """Add a new row of data."""
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(row_data)
        self.endInsertRows()
    
    def clear_data(self):
        """Clear all data."""
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

# Usage
class DataView(QTableView):
    """Custom table view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create model
        self.model = DataModel(["ID", "Name", "Value"])
        self.setModel(self.model)
        
        # Configure view
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        
        # Add sample data
        self.model.add_data([1, "Item 1", 100.5])
        self.model.add_data([2, "Item 2", 200.0])
```

## 🧵 Threading and Concurrency

### 1. QThread Pattern
```python
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
import time

class WorkerThread(QThread):
    """Worker thread for background operations."""
    
    # Signals
    progress = Signal(int)
    result_ready = Signal(object)
    error = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        self._tasks = []
    
    def add_task(self, task):
        """Add task to queue."""
        self._mutex.lock()
        self._tasks.append(task)
        self._condition.wakeOne()
        self._mutex.unlock()
    
    def stop(self):
        """Stop the thread gracefully."""
        self._is_running = False
        self._condition.wakeOne()
        self.wait()  # Wait for thread to finish
    
    def run(self):
        """Thread main loop."""
        while self._is_running:
            self._mutex.lock()
            
            if not self._tasks:
                self._condition.wait(self._mutex)
            
            if self._tasks and self._is_running:
                task = self._tasks.pop(0)
                self._mutex.unlock()
                
                try:
                    # Process task
                    result = self._process_task(task)
                    self.result_ready.emit(result)
                except Exception as e:
                    self.error.emit(str(e))
            else:
                self._mutex.unlock()
    
    def _process_task(self, task):
        """Process a single task."""
        total_steps = 100
        for i in range(total_steps):
            if not self._is_running:
                break
            
            # Simulate work
            time.sleep(0.01)
            self.progress.emit(int((i + 1) / total_steps * 100))
        
        return f"Completed: {task}"
```

### 2. QThreadPool and QRunnable
```python
from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject
import traceback

class WorkerSignals(QObject):
    """Signals for worker communication."""
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    """Worker for thread pool execution."""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        """Execute the function."""
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

# Usage
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        
    def execute_task(self):
        """Execute task in thread pool."""
        def long_running_task(progress_callback):
            """Task that reports progress."""
            for i in range(100):
                time.sleep(0.01)
                progress_callback.emit(i + 1)
            return "Task completed!"
        
        # Create worker
        worker = Worker(long_running_task, self.update_progress)
        worker.signals.result.connect(self.on_result)
        worker.signals.error.connect(self.on_error)
        
        # Execute
        self.threadpool.start(worker)
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
```

## 🎨 Styling and Theming

### 1. Qt Style Sheets (QSS)
```python
# style_manager.py
from PySide6.QtCore import QFile, QTextStream
from pathlib import Path

class StyleManager:
    """Manage application styling."""
    
    THEMES = {
        "light": "light.qss",
        "dark": "dark.qss",
        "custom": "custom.qss"
    }
    
    @staticmethod
    def load_stylesheet(theme: str = "light") -> str:
        """Load stylesheet from file."""
        if theme not in StyleManager.THEMES:
            theme = "light"
        
        style_path = Path(__file__).parent / "styles" / StyleManager.THEMES[theme]
        
        if not style_path.exists():
            return ""
        
        file = QFile(str(style_path))
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            file.close()
            return stylesheet
        
        return ""
    
    @staticmethod
    def apply_theme(app: QApplication, theme: str = "light"):
        """Apply theme to application."""
        stylesheet = StyleManager.load_stylesheet(theme)
        app.setStyleSheet(stylesheet)
```

Example dark.qss:
```css
/* Dark theme stylesheet */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #484848;
    border-color: #777777;
}

QPushButton:pressed {
    background-color: #222222;
}

QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    color: #ffffff;
    padding: 4px;
    border-radius: 4px;
}

QTableView {
    background-color: #2b2b2b;
    alternate-background-color: #3c3c3c;
    selection-background-color: #4a90e2;
    gridline-color: #555555;
}

QHeaderView::section {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 4px;
    border: 1px solid #555555;
}
```

## 📦 Resource Management

### 1. Qt Resource System
```python
# Create resources.qrc file
"""
<RCC>
    <qresource prefix="/icons">
        <file>open.png</file>
        <file>save.png</file>
        <file>exit.png</file>
    </qresource>
    <qresource prefix="/styles">
        <file>dark.qss</file>
        <file>light.qss</file>
    </qresource>
</RCC>
"""

# Compile resources
# pyside6-rcc resources.qrc -o resources_rc.py

# Usage in code
from . import resources_rc  # Import compiled resources

icon = QIcon(":/icons/open.png")
```

### 2. Settings Management
```python
from PySide6.QtCore import QSettings
from typing import Any, Optional

class SettingsManager:
    """Centralized settings management."""
    
    def __init__(self):
        self.settings = QSettings()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value."""
        return self.settings.value(key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value."""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry."""
        return self.get("window/geometry")
    
    def set_window_geometry(self, geometry: bytes):
        """Save window geometry."""
        self.set("window/geometry", geometry)
    
    def get_recent_files(self, max_files: int = 10) -> List[str]:
        """Get recent files list."""
        recent = self.get("files/recent", [])
        return recent[:max_files] if isinstance(recent, list) else []
    
    def add_recent_file(self, filepath: str):
        """Add file to recent files."""
        recent = self.get_recent_files()
        
        # Remove if already exists
        if filepath in recent:
            recent.remove(filepath)
        
        # Add to front
        recent.insert(0, filepath)
        
        # Limit size
        recent = recent[:10]
        
        self.set("files/recent", recent)
```

## 🧪 Testing PySide6 Applications

### 1. Unit Testing Widgets
```python
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import sys

# Fixture for QApplication
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

class TestCustomWidget:
    """Test custom widget functionality."""
    
    def test_widget_creation(self, qapp):
        """Test widget can be created."""
        from src.ui.widgets.custom_widget import CustomWidget
        
        widget = CustomWidget()
        assert widget is not None
        assert widget.value == 0
    
    def test_value_change_signal(self, qapp, qtbot):
        """Test value change emits signal."""
        from src.ui.widgets.custom_widget import CustomWidget
        
        widget = CustomWidget()
        qtbot.addWidget(widget)
        
        # Watch for signal
        with qtbot.waitSignal(widget.value_changed, timeout=1000) as blocker:
            widget.set_value(50)
        
        assert blocker.args == [50]
        assert widget.value == 50
    
    def test_button_click(self, qapp, qtbot):
        """Test button click handling."""
        from src.ui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Simulate button click
        button = window.findChild(QPushButton, "actionButton")
        qtbot.mouseClick(button, Qt.LeftButton)
        
        # Verify result
        assert window.action_performed
```

### 2. Integration Testing
```python
class TestApplication:
    """Integration tests for application."""
    
    def test_file_open_dialog(self, qapp, qtbot, monkeypatch):
        """Test file open functionality."""
        from src.ui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitForWindowShown(window)
        
        # Mock file dialog
        test_file = "/path/to/test.txt"
        monkeypatch.setattr(
            QFileDialog, 
            "getOpenFileName",
            lambda *args: (test_file, "")
        )
        
        # Trigger open action
        window.open_action.trigger()
        
        # Verify file was opened
        assert window.current_file == test_file
```

## 🔍 Debugging and Profiling

### 1. Debug Helpers
```python
from PySide6.QtCore import QObject, qDebug
import logging

class DebugHelper:
    """Debugging utilities for PySide6."""
    
    @staticmethod
    def print_widget_tree(widget, indent=0):
        """Print widget hierarchy."""
        print("  " * indent + f"{widget.__class__.__name__} - {widget.objectName()}")
        for child in widget.children():
            if isinstance(child, QWidget):
                DebugHelper.print_widget_tree(child, indent + 1)
    
    @staticmethod
    def connect_to_logger(obj: QObject):
        """Connect all signals to logger."""
        meta_obj = obj.metaObject()
        
        for i in range(meta_obj.methodCount()):
            method = meta_obj.method(i)
            if method.methodType() == QMetaMethod.Signal:
                signal_name = method.name().data().decode()
                signal = getattr(obj, signal_name)
                signal.connect(
                    lambda *args, name=signal_name: 
                    logging.debug(f"Signal {name} emitted: {args}")
                )
```

## 🚀 Deployment

### 1. PyInstaller Configuration
```python
# pyinstaller_config.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/resources', 'resources'),
        ('src/ui/styles', 'ui/styles'),
    ],
    hiddenimports=['PySide6.QtXml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.ico'
)
```

## 🏁 Pre-Production Checklist

Before considering any PySide6 application production-ready:

- [ ] All long operations run in separate threads
- [ ] No UI updates from worker threads
- [ ] Proper parent-child relationships for all widgets
- [ ] Memory leaks checked (objects properly deleted)
- [ ] Settings persistence implemented
- [ ] Keyboard shortcuts for common actions
- [ ] Tab order configured correctly
- [ ] Accessibility features implemented
- [ ] High DPI support tested
- [ ] Platform-specific features handled
- [ ] Error dialogs for user-facing errors
- [ ] Progress indication for long operations
- [ ] Proper application metadata set
- [ ] Resources compiled and included
- [ ] Translations implemented (if needed)
- [ ] Cross-platform testing completed
- [ ] Deployment packages created and tested

## 💡 PySide6-Specific Tips

### Always Remember:

1. **Main Thread is Sacred**: Never block it
2. **Signals for Communication**: Use signals between threads
3. **Parent Everything**: Widgets need parents for cleanup
4. **Layouts Over Positioning**: Use layouts for responsive UI
5. **Model-View Separation**: Keep logic out of widgets
6. **Test on Target Platforms**: Behavior varies across OS
7. **Use Qt's Classes**: Prefer QFile over Python's open()
8. **Handle Events Properly**: Don't block event handlers
9. **Resource Management**: Clean up timers, threads, connections

### Common Gotchas:

- Forgetting to call `super().__init__()`
- Not keeping references to threads (gets garbage collected)
- Modifying UI from worker threads
- Memory leaks from circular references
- Not disconnecting signals when needed
- Blocking event loop with sleep()
- Platform-specific path separators
- Different behavior between Qt Designer and code
- Signal parameter type mismatches

Remember: Always check the latest documentation using context7 MCP before implementing any feature!
        