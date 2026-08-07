"""Core click loop engine."""

from __future__ import annotations

import os
import threading
import time

from .click_profile import ClickProfile
from .click_type import ClickType


class AutoClicker:
    """Core engine that simulates mouse clicks at configurable intervals.

    Runs in a background thread. Uses evdev to inject events.

    Attributes:
        profile: The ClickProfile defining click settings.
        is_running: Whether the auto-clicker is currently active.
    """

    def __init__(self, profile: ClickProfile) -> None:
        self.profile = profile
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._device_path: str = "/dev/input/event0"

    @property
    def is_running(self) -> bool:
        """Whether the auto-clicker is currently running."""
        return self._running

    def _inject_click(self, device_path: str, current_x: int | None = None, current_y: int | None = None) -> None:
        """Inject a single click event."""
        x, y = self.profile.coordinates if self.profile.coordinates else (None, None)
        self.profile.click_type.inject(
            device_path=device_path,
            x=x,
            y=y,
            current_x=current_x,
            current_y=current_y,
            long_press_duration=self.profile.long_press_duration,
        )

    def _find_device(self) -> str:
        """Find a suitable input device for mouse event injection.

        Returns:
            Path to the first available mouse device.
        """
        try:
            import evdev
            for path in evdev.list_devices():
                try:
                    device = evdev.InputDevice(path)
                    if device.info.evbit is not None and evdev.ecodes.EV_REL in device.info.evbit:
                        device.close()
                        return path
                    device.close()
                except Exception:
                    continue
        except Exception:
            pass
        
        for path in ["/dev/input/event3", "/dev/input/event7", "/dev/input/event0"]:
            if os.path.exists(path):
                return path
        
        return "/dev/input/event0"

    def start(self, duration: float | None = None, device_path: str | None = None) -> None:
        """Start the auto-clicker loop.

        Args:
            duration: How long to run in seconds. None = run indefinitely.
            device_path: evdev device path for injection. Auto-detected if None.

        Raises:
            FileNotFoundError: If no suitable device found.
            PermissionError: If insufficient permissions to write to device.
            ValueError: If profile is disabled.
        """
        if self._running:
            return

        if device_path is None:
            device_path = self._find_device()
        
        if not os.path.exists(device_path):
            raise FileNotFoundError(f"Device not found: {device_path}")

        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        interval_sec = self.profile.interval / 1000.0
        self._device_path = device_path

        def _loop() -> None:
            try:
                start_time = time.monotonic()
                while not self._stop_event.is_set():
                    if duration is not None:
                        elapsed = time.monotonic() - start_time
                        if elapsed >= duration:
                            break
                    if self.profile.enabled:
                        self._inject_click(self._device_path)
                    self._stop_event.wait(interval_sec)
            except PermissionError:
                self._running = False
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    self._running = False
                else:
                    self._running = False
            finally:
                if not self._stop_event.is_set():
                    self._running = False

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the auto-clicker."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._running = False

    def restart(
        self,
        new_profile: ClickProfile,
        device_path: str = "/dev/input/event0",
    ) -> "AutoClicker":
        """Stop current and start with a new profile.

        Returns:
            New AutoClicker instance with the new profile.
        """
        self.stop()
        return AutoClicker(new_profile)
