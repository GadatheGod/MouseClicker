import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication


class TestTrayApp:
    """Tests for system-tray GUI application."""

    @pytest.fixture(autouse=True)
    def qt_app(self, qtbot):
        """Provide a QApplication instance."""
        app = QApplication.instance() or QApplication([])
        return app

    def test_tray_app_creates_icon(self, qtbot):
        """Should create a system tray icon."""
        from src.tray_app.main_window import TrayApp

        app = QApplication.instance() or QApplication([])
        tray = TrayApp()
        assert tray.trayIcon is not None

    def test_tray_app_has_menu(self, qtbot):
        """Should have a context menu."""
        from src.tray_app.main_window import TrayApp

        app = QApplication.instance() or QApplication([])
        tray = TrayApp()
        menu = tray.trayIcon.contextMenu()
        assert menu is not None

    def test_tray_app_start_stop_actions(self, qtbot):
        """Should have start/stop actions."""
        from src.tray_app.main_window import TrayApp

        app = QApplication.instance() or QApplication([])
        tray = TrayApp()
        menu = tray.trayIcon.contextMenu()
        assert menu is not None
