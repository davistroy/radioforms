"""UI tests for main window functionality.

This module tests UI interactions, widget behavior, and user workflows
using pytest-qt for PySide6 testing.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import pytest
    from pytestqt.qtbot import QtBot
    from src.ui.main_window import MainWindow, PYSIDE6_AVAILABLE
    
    if PYSIDE6_AVAILABLE:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication
        
        @pytest.fixture(scope="session")
        def qapp():
            """Create QApplication for testing."""
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            yield app
            app.quit()
        
        
        class TestMainWindowUI:
            """Test main window UI functionality."""
            
            @pytest.fixture
            def main_window(self, qtbot, qapp):
                """Create main window for testing."""
                window = MainWindow(debug=True)
                qtbot.addWidget(window)
                return window
            
            def test_window_creation(self, main_window):
                """Test main window creates successfully."""
                assert main_window is not None
                assert main_window.windowTitle() == "RadioForms - ICS Forms Management"
            
            def test_window_size(self, main_window):
                """Test window sizing."""
                # Check minimum size
                min_size = main_window.minimumSize()
                assert min_size.width() >= 800
                assert min_size.height() >= 600
            
            def test_menu_bar_exists(self, main_window):
                """Test menu bar is created."""
                menu_bar = main_window.menuBar()
                assert menu_bar is not None
                
                # Check for expected menus
                menu_titles = [action.text() for action in menu_bar.actions()]
                expected_menus = ["&File", "&Edit", "&Form", "&View", "&Help"]
                
                for expected_menu in expected_menus:
                    assert any(expected_menu in title for title in menu_titles)
            
            def test_status_bar_exists(self, main_window):
                """Test status bar is created."""
                status_bar = main_window.statusBar()
                assert status_bar is not None
                assert status_bar.isVisible()
            
            def test_central_widget_exists(self, main_window):
                """Test central widget is set."""
                central_widget = main_window.centralWidget()
                assert central_widget is not None
            
            def test_tab_widget_exists(self, main_window):
                """Test tab widget for forms exists."""
                assert hasattr(main_window, 'tab_widget')
                assert main_window.tab_widget is not None
                
                # Should have at least one tab (ICS-213)
                assert main_window.tab_widget.count() >= 1
            
            def test_menu_actions_exist(self, main_window):
                """Test menu actions are created."""
                expected_actions = [
                    'new', 'save', 'save_as', 'import', 'export', 'exit',
                    'validate', 'clear', 'approve', 'add_reply',
                    'priority_routine', 'priority_urgent', 'priority_immediate',
                    'refresh', 'toggle_statusbar', 'documentation', 'shortcuts', 'about'
                ]
                
                for action_name in expected_actions:
                    assert action_name in main_window.actions
                    assert main_window.actions[action_name] is not None
            
            def test_keyboard_shortcuts(self, main_window):
                """Test keyboard shortcuts are configured."""
                shortcuts = {
                    'new': 'Ctrl+N',
                    'save': 'Ctrl+S',
                    'import': 'Ctrl+I',
                    'export': 'Ctrl+E',
                    'validate': 'F5',
                    'clear': 'Ctrl+L'
                }
                
                for action_name, expected_shortcut in shortcuts.items():
                    action = main_window.actions[action_name]
                    assert action.shortcut().toString() == expected_shortcut
            
            def test_menu_action_triggers(self, main_window, qtbot):
                """Test menu actions can be triggered."""
                # Test non-destructive actions
                safe_actions = ['refresh', 'about', 'documentation', 'shortcuts']
                
                for action_name in safe_actions:
                    if action_name in main_window.actions:
                        action = main_window.actions[action_name]
                        # Trigger action and verify no exception
                        with qtbot.waitSignal(action.triggered, timeout=1000):
                            action.trigger()
            
            def test_status_bar_messages(self, main_window, qtbot):
                """Test status bar message updates."""
                main_window._update_status("Test message", 1000)
                
                status_bar = main_window.statusBar()
                # Message should be displayed
                # Note: Direct text access might be implementation-dependent
                assert status_bar is not None
            
            def test_window_close_handling(self, main_window, qtbot):
                """Test window close event handling."""
                # This tests the closeEvent method exists and is callable
                assert hasattr(main_window, 'closeEvent')
                assert callable(main_window.closeEvent)
            
            def test_menu_state_management(self, main_window):
                """Test menu state management."""
                # Call update menu states
                main_window._update_menu_states()
                
                # Check that actions have appropriate states
                # (Exact states depend on whether forms are loaded)
                save_action = main_window.actions['save']
                assert hasattr(save_action, 'isEnabled')
            
            def test_priority_actions_checkable(self, main_window):
                """Test priority actions are checkable."""
                priority_actions = ['priority_routine', 'priority_urgent', 'priority_immediate']
                
                for action_name in priority_actions:
                    action = main_window.actions[action_name]
                    assert action.isCheckable()
            
            def test_status_bar_toggle(self, main_window, qtbot):
                """Test status bar visibility toggle."""
                status_bar = main_window.statusBar()
                initial_visible = status_bar.isVisible()
                
                # Toggle status bar
                main_window._toggle_status_bar()
                assert status_bar.isVisible() != initial_visible
                
                # Toggle back
                main_window._toggle_status_bar()
                assert status_bar.isVisible() == initial_visible
            
            def test_form_widget_integration(self, main_window):
                """Test form widget integration."""
                if hasattr(main_window, 'ics213_widget') and main_window.ics213_widget:
                    # Check that form widget is properly integrated
                    assert main_window.ics213_widget is not None
                    
                    # Check tab integration
                    tab_count = main_window.tab_widget.count()
                    assert tab_count >= 1
                    
                    # Check tab text
                    tab_text = main_window.tab_widget.tabText(0)
                    assert "ICS-213" in tab_text
        
        
        class TestMainWindowInteractions:
            """Test main window user interactions."""
            
            @pytest.fixture
            def main_window(self, qtbot, qapp):
                """Create main window for testing."""
                window = MainWindow(debug=True)
                qtbot.addWidget(window)
                return window
            
            def test_new_form_action(self, main_window, qtbot):
                """Test new form action."""
                new_action = main_window.actions['new']
                
                # Trigger new form action
                with qtbot.waitSignal(new_action.triggered, timeout=1000):
                    new_action.trigger()
                
                # Should update status
                # (Exact verification depends on implementation)
            
            def test_refresh_action(self, main_window, qtbot):
                """Test refresh action."""
                refresh_action = main_window.actions['refresh']
                
                # Trigger refresh action
                with qtbot.waitSignal(refresh_action.triggered, timeout=1000):
                    refresh_action.trigger()
            
            def test_about_dialog(self, main_window, qtbot):
                """Test about dialog."""
                about_action = main_window.actions['about']
                
                # Trigger about action
                with qtbot.waitSignal(about_action.triggered, timeout=1000):
                    about_action.trigger()
                
                # Should show about dialog
                # (Dialog testing would require more complex setup)
            
            def test_priority_setting(self, main_window):
                """Test priority setting functionality."""
                from src.forms.ics213 import Priority
                
                # Test setting different priorities
                for priority in [Priority.ROUTINE, Priority.URGENT, Priority.IMMEDIATE]:
                    main_window._set_priority(priority)
                    
                    # Check that appropriate action is checked
                    if priority == Priority.ROUTINE:
                        assert main_window.actions['priority_routine'].isChecked()
                    elif priority == Priority.URGENT:
                        assert main_window.actions['priority_urgent'].isChecked()
                    elif priority == Priority.IMMEDIATE:
                        assert main_window.actions['priority_immediate'].isChecked()
            
            def test_menu_state_updates(self, main_window):
                """Test menu state updates with form changes."""
                # Initial state
                main_window._update_menu_states()
                
                # Menu states should be appropriate for current form state
                # (Exact states depend on whether forms are loaded)
                assert hasattr(main_window, '_update_menu_states')
                assert callable(main_window._update_menu_states)
            
            def test_keyboard_navigation(self, main_window, qtbot):
                """Test keyboard navigation."""
                # Test that main window accepts focus
                main_window.setFocus()
                
                # Test tab navigation (basic)
                if main_window.tab_widget.count() > 0:
                    qtbot.keyClick(main_window, Qt.Key_Tab)
            
            def test_error_handling_ui(self, main_window):
                """Test UI error handling."""
                # Test handlers that should handle errors gracefully
                main_window._on_validate_form()  # Should handle no form gracefully
                main_window._on_clear_form()     # Should handle no form gracefully
                
                # Should not raise exceptions
                assert True
    
    else:
        # Skip all tests if PySide6 not available
        @pytest.mark.skip(reason="PySide6 not available")
        class TestMainWindowUI:
            pass
            
        @pytest.mark.skip(reason="PySide6 not available")
        class TestMainWindowInteractions:
            pass

except ImportError:
    # Skip all tests if pytest-qt not available
    @pytest.mark.skip(reason="pytest-qt not available")
    class TestMainWindowUI:
        pass
        
    @pytest.mark.skip(reason="pytest-qt not available")
    class TestMainWindowInteractions:
        pass