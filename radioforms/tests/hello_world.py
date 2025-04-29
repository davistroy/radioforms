#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple PySide6 'Hello World' application to test the environment setup.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer


class HelloWorldWindow(QMainWindow):
    """
    A simple window displaying 'Hello World' message.
    """
    
    def __init__(self):
        """Initialize the window."""
        super().__init__()
        
        # Set up the window
        self.setWindowTitle("RadioForms - Hello World")
        self.resize(400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a hello world label
        hello_label = QLabel("Hello World!")
        hello_label.setAlignment(Qt.AlignCenter)
        hello_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(hello_label)
        
        # Add application description
        description_label = QLabel(
            "RadioForms environment is successfully set up!"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(description_label)
        
        # Auto-close timer for automated testing
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close)
        
    def start_close_timer(self, timeout_ms=3000):
        """
        Start a timer to auto-close the window.
        
        Args:
            timeout_ms: Timeout in milliseconds (default: 3000)
        """
        self.close_timer.start(timeout_ms)


def main():
    """Main entry point."""
    # Check if application instance exists
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Create and show the window
    window = HelloWorldWindow()
    window.show()
    
    # Start auto-close timer if run with --test argument
    if "--test" in sys.argv:
        window.start_close_timer()
    
    # Run the application
    return app.exec() if hasattr(app, 'exec') else app.exec_()


if __name__ == "__main__":
    sys.exit(main())
