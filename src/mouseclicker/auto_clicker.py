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

    def start(self, duration: float | None = None, device_path: str = "/dev/input/event0") -> None:
        """Start the auto-clicker loop.

        Args:
            duration: How long to run in seconds. None = run indefinitely.
            device_path: evdev device path for injection.

        Raises:
            FileNotFoundError: If device_path doesn't exist.
            ValueError: If profile is disabled.
        """
        if not os.path.exists(device_path):
            raise FileNotFoundError(f"Device not found: {device_path}")

        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        interval_sec = self.profile.interval / 1000.0

        def _loop() -> None:
            try:
                start_time = time.monotonic()
                while not self._stop_event.is_set():
                    if duration is not None:
                        elapsed = time.monotonic() - start_time
                        if elapsed >= duration:
                            break
                    if self.profile.enabled:
                        self._inject_click(device_path)
                    self._stop_event.wait(interval_sec)
            finally:
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
