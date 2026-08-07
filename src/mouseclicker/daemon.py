"""Background process manager (Daemon)."""

from __future__ import annotations

import threading

from .auto_clicker import AutoClicker
from .click_profile import ClickProfile
from .hotkey import HotkeyListener
from .ipc import IPCServer
from .schedule import Schedule


class Daemon:
    """Orchestrates the auto-clicker daemon.

    Manages the AutoClicker instance, Schedule triggers, Hotkey events,
    IPC commands, and provides status information.

    Attributes:
        is_running: Whether the daemon is currently running.
    """

    def __init__(self, socket_path: str | None = None) -> None:
        self._profile: ClickProfile | None = None
        self._clicker: AutoClicker | None = None
        self._schedule: Schedule | None = None
        self._hotkey_listener: HotkeyListener | None = None
        self._ipc_server = IPCServer(socket_path)
        self._running = False
        self._hotkey_thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        """Whether the daemon is currently running."""
        return self._running

    @property
    def profile(self) -> ClickProfile | None:
        """The current click profile."""
        return self._profile

    def set_schedule(self, schedule: Schedule) -> None:
        """Set the schedule for the daemon.

        Args:
            schedule: The Schedule to use.
        """
        self._schedule = schedule

    def set_hotkey_listener(self, hotkey_listener: HotkeyListener) -> None:
        """Set the hotkey listener for the daemon.

        Args:
            hotkey_listener: The HotkeyListener to use.
        """
        self._hotkey_listener = hotkey_listener

    def start(self, profile: ClickProfile | None = None) -> None:
        """Start the daemon with a click profile.

        Args:
            profile: The ClickProfile to use. Defaults to existing profile.

        Returns:
            True if started successfully, False otherwise.
        """
        if self._running:
            return False

        if profile:
            self._profile = profile
        if not self._profile:
            raise ValueError("No profile configured")

        self._clicker = AutoClicker(self._profile)
        try:
            self._clicker.start()
        except PermissionError as e:
            self._clicker = None
            self._running = False
            raise RuntimeError(
                f"Permission denied: {e}. Try running with sudo or add your user to 'input' group:\n"
                f"  sudo usermod -aG input $USER\n"
                f"Then log out and log back in."
            )
        except Exception as e:
            self._clicker = None
            self._running = False
            raise RuntimeError(f"Failed to start auto-clicker: {e}")

        self._running = True

        # Start hotkey listener thread if configured
        if self._hotkey_listener:
            self._hotkey_thread = threading.Thread(target=self._hotkey_loop, daemon=True)
            self._hotkey_thread.start()
        
        return True

    def stop(self) -> None:
        """Stop the daemon."""
        if self._clicker:
            old_clicker = self._clicker
            old_clicker.stop()
        self._running = False
        self._clicker = None

    def switch_profile(self, profile: ClickProfile) -> None:
        """Switch to a new click profile.

        Args:
            profile: The new ClickProfile to use.
        """
        self._profile = profile
        if self._clicker:
            self._clicker.stop()
        self._clicker = AutoClicker(profile)
        self._clicker.start()

    def _hotkey_loop(self) -> None:
        """Loop that listens for hotkey events."""
        if not self._hotkey_listener:
            return

        active_modifiers: dict[str, bool] = {}
        modifiers, key = self._hotkey_listener._parse_hotkey(self._hotkey_listener.hotkey)
        key_code = self._hotkey_listener._get_key_code(key)
        device_handles: list = []

        try:
            devices = self._hotkey_listener.get_available_devices()
            if not devices:
                return

            # Open keyboard devices for hotkey listening
            for dev_path in devices:
                try:
                    dev = __import__("evdev", fromlist=["InputDevice"])
                    device = dev.InputDevice(dev_path)
                    caps = device.capabilities()
                    if 1 in caps:  # EV_KEY
                        device_handles.append(device)
                    else:
                        device.close()
                except (PermissionError, OSError):
                    continue

            if not device_handles:
                return

            import sys
            while self._running:
                for device in device_handles:
                    try:
                        for event in device.read():
                            # EV_KEY (type 1) events
                            if event.type == 1:
                                key_name = self._hotkey_listener._get_key_name(event.code)
                                if key_name in self._hotkey_listener.MODIFIER_KEYS:
                                    active_modifiers[key_name] = event.value == 1
                                elif event.code == key_code and event.value == 1:
                                    if self._hotkey_listener.is_hotkey_pressed(modifiers, key, active_modifiers):
                                        print(f"Hotkey pressed! modifiers={active_modifiers}", file=sys.stderr, flush=True)
                                        self._on_hotkey_toggle()
                    except (BlockingIOError, OSError):
                        continue
        finally:
            for device in device_handles:
                try:
                    device.close()
                except OSError:
                    pass

    def _on_hotkey_toggle(self) -> None:
        """Handle hotkey toggle event."""
        if self._running:
            self.stop()
        else:
            if self._profile:
                self.start(self._profile)

    def get_status(self) -> dict:
        """Get daemon status information.

        Returns:
            Dictionary with status information.
        """
        return {
            "running": self._running,
            "profile": self._profile.name if self._profile else None,
            "clicker_running": self._clicker.is_running if self._clicker else False,
            "schedule_mode": self._schedule.mode if self._schedule else None,
        }

    def get_ipc_server(self) -> IPCServer:
        """Get the IPC server instance."""
        return self._ipc_server
