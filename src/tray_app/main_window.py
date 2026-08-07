"""System-tray GUI application for MouseClicker."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

from src.mouseclicker.config import Config
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType
from src.mouseclicker.daemon import Daemon
from src.mouseclicker.jitter import Jitter


class SettingsDialog(QDialog):
    """Settings dialog for configuring click profiles."""

    def __init__(self, config: Config, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Profile selection
        layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        for name in config.profiles:
            self.profile_combo.addItem(name)
        layout.addWidget(self.profile_combo)

        # Interval
        layout.addWidget(QLabel("Interval (ms):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10000)
        self.interval_spin.setValue(100)
        layout.addWidget(self.interval_spin)

        # Jitter position
        layout.addWidget(QLabel("Position Jitter (px):"))
        self.jitter_pos_spin = QSpinBox()
        self.jitter_pos_spin.setRange(0, 20)
        self.jitter_pos_spin.setValue(config.position_jitter)
        layout.addWidget(self.jitter_pos_spin)

        # Jitter timing
        layout.addWidget(QLabel("Timing Jitter (ms):"))
        self.jitter_time_spin = QSpinBox()
        self.jitter_time_spin.setRange(0, 100)
        self.jitter_time_spin.setValue(config.timing_jitter)
        layout.addWidget(self.jitter_time_spin)

        # Hotkey
        layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(config.hotkey_toggle)
        layout.addWidget(self.hotkey_input)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self) -> None:
        """Save settings to config."""
        self.config.position_jitter = self.jitter_pos_spin.value()
        self.config.timing_jitter = self.jitter_time_spin.value()
        self.config.hotkey_toggle = self.hotkey_input.text()
        self.config.save()
        self.accept()


class TrayApp:
    """System-tray GUI application for MouseClicker."""

    def __init__(self) -> None:
        self.config = Config.load()
        self.daemon: Daemon | None = None
        self.trayIcon: QSystemTrayIcon | None = None
        self._setup_tray()

    def _setup_tray(self) -> None:
        """Set up the system tray icon and menu."""
        self.trayIcon = QSystemTrayIcon()

        # Create menu
        menu = QMenu()

        # Start/Stop actions
        self.start_action = QAction("Start", menu)
        self.start_action.triggered.connect(self._start)
        menu.addAction(self.start_action)

        self.stop_action = QAction("Stop", menu)
        self.stop_action.triggered.connect(self._stop)
        self.stop_action.setEnabled(False)
        menu.addAction(self.stop_action)

        menu.addSeparator()

        # Profile submenu
        profile_menu = QMenu("Profiles", menu)
        for name in self.config.profiles:
            action = QAction(name, profile_menu)
            action.triggered.connect(lambda checked, n=name: self._switch_profile(n))
            profile_menu.addAction(action)
        menu.addMenu(profile_menu)

        menu.addSeparator()

        # Settings
        settings_action = QAction("Settings", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        # Quit
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.trayIcon.setContextMenu(menu)
        self.trayIcon.setToolTip("MouseClicker")
        self.trayIcon.setVisible(True)

    def _start(self) -> None:
        """Start the auto-clicker."""
        profile_name = self.config.default_profile
        profile = self.config.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(None, "Error", f"Profile '{profile_name}' not found")
            return

        self.daemon = Daemon()
        self.daemon.start(profile)
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.trayIcon.setToolTip(f"MouseClicker: Running ({profile_name})")

    def _stop(self) -> None:
        """Stop the auto-clicker."""
        if self.daemon:
            self.daemon.stop()
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.trayIcon.setToolTip("MouseClicker: Stopped")

    def _switch_profile(self, name: str) -> None:
        """Switch to a different profile."""
        self.config.default_profile = name
        self.config.save()
        if self.daemon:
            profile = self.config.get_profile(name)
            if profile:
                self.daemon.switch_profile(profile)
                self.trayIcon.setToolTip(f"MouseClicker: Running ({name})")

    def _open_settings(self) -> None:
        """Open settings dialog."""
        dialog = SettingsDialog(self.config)
        dialog.exec()

    def _quit(self) -> None:
        """Quit the application."""
        if self.daemon:
            self.daemon.stop()
        QApplication.quit()

    def run(self) -> None:
        """Run the tray application."""
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")  # Cross-platform consistent look
        self.trayIcon.showMessage(
            "MouseClicker",
            "MouseClicker is running. Right-click the tray icon to control.",
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )
        sys.exit(app.exec())


def main() -> None:
    """Main entry point for the GUI application."""
    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()
