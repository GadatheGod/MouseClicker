"""System-tray GUI application for MouseClicker."""

from __future__ import annotations

import sys
from pathlib import Path

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
    QMainWindow,
    QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap

from src.mouseclicker.config import Config
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType
from src.mouseclicker.daemon import Daemon
from src.mouseclicker.jitter import Jitter
from src.mouseclicker.hotkey import HotkeyListener


def _create_icon(color: str, size: int = 64) -> QIcon:
    """Create a colored icon."""
    safe_color = color.replace("#", "hex_")
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color}"/>
      <stop offset="100%" style="stop-color:{color}"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="12" fill="url(#bg)"/>
  <circle cx="32" cy="32" r="18" fill="none" stroke="white" stroke-width="3"/>
  <circle cx="32" cy="32" r="6" fill="white"/>
  <line x1="32" y1="14" x2="32" y2="20" stroke="white" stroke-width="3" stroke-linecap="round"/>
  <line x1="32" y1="44" x2="32" y2="50" stroke="white" stroke-width="3" stroke-linecap="round"/>
  <line x1="14" y1="32" x2="20" y2="32" stroke="white" stroke-width="3" stroke-linecap="round"/>
  <line x1="44" y1="32" x2="50" y2="32" stroke="white" stroke-width="3" stroke-linecap="round"/>
</svg>'''
    temp_path = Path(f"/tmp/mouseclicker_icon_{safe_color}.svg")
    temp_path.write_text(svg_content)
    return QIcon(str(temp_path))


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


class MainWindow(QMainWindow):
    """Main window as fallback when tray icon doesn't show."""

    def __init__(self, tray_app: "TrayApp") -> None:
        super().__init__()
        self.tray_app = tray_app
        self.setWindowTitle("MouseClicker")
        self.setFixedSize(300, 250)
        icon_path = Path(__file__).parent / "icons" / "icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("MouseClicker"))

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(tray_app._start)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(tray_app._stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        for name in tray_app.config.profiles:
            self.profile_combo.addItem(name)
        self.profile_combo.currentTextChanged.connect(tray_app._switch_profile)
        layout.addWidget(self.profile_combo)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(tray_app._open_settings)
        layout.addWidget(settings_btn)

    def update_profile_combo(self, profiles: dict) -> None:
        """Update the profile dropdown."""
        self.profile_combo.clear()
        for name in profiles:
            self.profile_combo.addItem(name)


class TrayApp:
    """System-tray GUI application for MouseClicker."""

    def __init__(self) -> None:
        self.config = Config.load()
        self.daemon: Daemon | None = None
        self.trayIcon: QSystemTrayIcon | None = None
        self._main_window: MainWindow | None = None
        self._hotkey_listener: HotkeyListener | None = None
        self._is_running = False
        self._update_icon_timer: QTimer | None = None

    def _setup_tray(self) -> None:
        """Set up the system tray icon and menu."""
        self.trayIcon = QSystemTrayIcon(_create_icon("#4CAF50"))

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

        # Setup hotkey listener (daemon may not exist yet)
        self._hotkey_listener = HotkeyListener(hotkey=self.config.hotkey_toggle)

        # Setup icon update timer
        self._update_icon_timer = QTimer()
        self._update_icon_timer.timeout.connect(self._update_icon)
        self._update_icon_timer.start(500)

    def _update_icon(self) -> None:
        """Update tray icon color based on running state."""
        if self._is_running:
            self.trayIcon.setIcon(_create_icon("#4CAF50"))  # Green
            self.trayIcon.setToolTip("MouseClicker: Running")
        else:
            self.trayIcon.setIcon(_create_icon("#F44336"))  # Red
            self.trayIcon.setToolTip("MouseClicker: Stopped")

    def _start(self) -> None:
        """Start the auto-clicker."""
        profile_name = self.config.default_profile
        profile = self.config.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(None, "Error", f"Profile '{profile_name}' not found")
            return

        self.daemon = Daemon()
        self.daemon.set_hotkey_listener(self._hotkey_listener)
        try:
            self.daemon.start(profile)
        except RuntimeError as e:
            QMessageBox.critical(None, "Error", str(e))
            self.daemon = None
            return
        self._is_running = True
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        if self._main_window:
            self._main_window.start_btn.setEnabled(False)
            self._main_window.stop_btn.setEnabled(True)

    def _stop(self) -> None:
        """Stop the auto-clicker."""
        if self.daemon:
            try:
                self.daemon.stop()
            except Exception:
                pass
            self.daemon = None
        self._is_running = False
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        if self._main_window:
            self._main_window.start_btn.setEnabled(True)
            self._main_window.stop_btn.setEnabled(False)

    def _switch_profile(self, name: str) -> None:
        """Switch to a different profile."""
        self.config.default_profile = name
        self.config.save()
        if self.daemon and self._is_running:
            profile = self.config.get_profile(name)
            if profile:
                self.daemon.switch_profile(profile)

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
        app.setStyle("Fusion")
        self._setup_tray()

        # Show main window as fallback
        self._main_window = MainWindow(self)
        self._main_window.show()
        self._main_window.raise_()
        self._main_window.activateWindow()
        print("MainWindow shown", flush=True)

        self.trayIcon.showMessage(
            "MouseClicker",
            "MouseClicker is running. Right-click the tray icon or use the main window to control.",
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )
        sys.exit(app.exec())


def main() -> None:
    """Main entry point for the GUI application."""
    app = TrayApp()
    app.run()


if __name__ == "__main__":
    import sys
    print(f"__main__ block entered, argv={sys.argv}", flush=True)
    main()
