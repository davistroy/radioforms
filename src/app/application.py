"""Application core module.

This module contains the main Application class that manages the
PySide6 QApplication lifecycle and coordinates the overall application state.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Conditional import for PySide6 to allow graceful failure
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt, QCoreApplication
    from PySide6.QtGui import QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # Dummy classes for development without PySide6
    class QApplication:
        def __init__(self, *args): pass
        def exec(self): return 0
        def setOrganizationName(self, name): pass
        def setOrganizationDomain(self, domain): pass  
        def setApplicationName(self, name): pass
        def setApplicationVersion(self, version): pass
    
    class QCoreApplication:
        @staticmethod
        def setAttribute(attr, value): pass
    
    class Qt:
        AA_EnableHighDpiScaling = None
        AA_UseHighDpiPixmaps = None


class Application:
    """Main application class managing the Qt application lifecycle.
    
    This class is responsible for:
    - Setting up the QApplication instance
    - Managing application metadata
    - Coordinating startup and shutdown
    - Handling application-level error conditions
    
    Example:
        app = Application(debug=True)
        exit_code = app.run()
    """
    
    def __init__(
        self, 
        database_path: Optional[Path] = None,
        debug: bool = False
    ) -> None:
        """Initialize the application.
        
        Args:
            database_path: Optional path to database file
            debug: Enable debug mode
        """
        self.logger = logging.getLogger(__name__)
        self.database_path = database_path or Path("radioforms.db")
        self.debug = debug
        self.qt_app: Optional[QApplication] = None
        self.main_window = None
        
        self.logger.info(f"Application initialized with database: {self.database_path}")
        
    def _setup_qt_application(self) -> QApplication:
        """Set up the Qt application with proper configuration.
        
        Returns:
            Configured QApplication instance
            
        Raises:
            RuntimeError: If PySide6 is not available
        """
        if not PYSIDE6_AVAILABLE:
            raise RuntimeError(
                "PySide6 is not available. Please install with: pip install PySide6"
            )
        
        # High DPI support
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create QApplication
        qt_app = QApplication(sys.argv)
        
        # Set application metadata
        qt_app.setOrganizationName("RadioForms")
        qt_app.setOrganizationDomain("radioforms.local")
        qt_app.setApplicationName("RadioForms")
        qt_app.setApplicationVersion("0.1.0")
        
        self.logger.info("Qt application configured successfully")
        return qt_app
        
    def _create_main_window(self):
        """Create and configure the main application window.
        
        Returns:
            Main window instance
        """
        try:
            from ..ui.main_window import MainWindow
            
            main_window = MainWindow(
                database_path=self.database_path,
                debug=self.debug
            )
            
            self.logger.info("Main window created successfully")
            return main_window
            
        except ImportError as e:
            self.logger.error(f"Could not import main window: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating main window: {e}")
            raise
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show error dialog to user if Qt is available.
        
        Args:
            title: Dialog title
            message: Error message to display
        """
        if PYSIDE6_AVAILABLE and self.qt_app:
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, title, message)
            except Exception as e:
                self.logger.error(f"Could not show error dialog: {e}")
        
        # Always log the error
        self.logger.error(f"{title}: {message}")
    
    def run(self) -> int:
        """Run the application main loop.
        
        Returns:
            Application exit code (0 for success, non-zero for error)
        """
        try:
            # Check if PySide6 is available
            if not PYSIDE6_AVAILABLE:
                self.logger.error("PySide6 not available - running in test mode")
                self.logger.info("Application would start main window here")
                self.logger.info("Database path: %s", self.database_path)
                self.logger.info("Debug mode: %s", self.debug)
                return 0
            
            # Set up Qt application
            self.qt_app = self._setup_qt_application()
            
            # Create main window
            self.main_window = self._create_main_window()
            self.main_window.show()
            
            self.logger.info("Application ready - entering main loop")
            
            # Run Qt event loop
            return self.qt_app.exec()
            
        except Exception as e:
            error_msg = f"Failed to start application: {e}"
            self._show_error_dialog("Startup Error", error_msg)
            return 1
    
    def shutdown(self) -> None:
        """Perform application shutdown cleanup.
        
        This method is called during application shutdown to perform
        necessary cleanup operations.
        """
        self.logger.info("Application shutdown initiated")
        
        try:
            if self.main_window:
                self.logger.info("Closing main window")
                # Main window will handle its own cleanup
                
            if self.qt_app:
                self.logger.info("Qt application cleanup")
                # Qt handles most cleanup automatically
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        
        self.logger.info("Application shutdown complete")