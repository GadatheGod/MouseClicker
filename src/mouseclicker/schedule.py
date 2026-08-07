"""Schedule module for simple delay and cron-based triggers."""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta

from croniter import croniter


class Schedule:
    """Manages schedule triggers for the auto-clicker.

    Supports two modes:
    - Simple delay: Start after N seconds
    - Cron expression: Recurring schedule

    Attributes:
        mode: Either 'delay' or 'cron'.
        delay_seconds: Seconds to wait for delay mode.
        cron_expression: Cron expression for cron mode.
    """

    def __init__(
        self,
        mode: str = "delay",
        delay_seconds: int = 0,
        cron_expression: str = "0 9 * * *",
    ) -> None:
        if mode not in ("delay", "cron"):
            raise ValueError(f"Invalid schedule mode: {mode}")
        self.mode = mode
        self.delay_seconds = delay_seconds
        self.cron_expression = cron_expression

    def next_run(self) -> datetime | None:
        """Get the next run time.

        Returns:
            datetime for next run, or None for immediate.
        """
        if self.mode == "delay":
            if self.delay_seconds <= 0:
                return None
            return datetime.now() + timedelta(seconds=self.delay_seconds)

        if self.mode == "cron":
            now = datetime.now()
            cron = croniter(self.cron_expression, now)
            next_time = cron.get_next(datetime)
            return next_time

        return None

    def wait_until(self, cancel_event: threading.Event | None = None) -> bool:
        """Wait until the next run time.

        Args:
            cancel_event: Optional threading.Event to cancel the wait.

        Returns:
            True if waited successfully, False if cancelled.
        """
        next_run = self.next_run()
        if next_run is None:
            return True  # Immediate

        now = datetime.now()
        wait_seconds = (next_run - now).total_seconds()

        if wait_seconds > 0:
            # Sleep in 60s increments, checking for cancel each time
            remaining = wait_seconds
            while remaining > 0:
                sleep_time = min(remaining, 60)
                if cancel_event and cancel_event.wait(timeout=sleep_time):
                    return False
                remaining -= sleep_time

        return True  # Time to run

    def is_due(self) -> bool:
        """Check if the schedule is due to run."""
        if self.mode == "delay":
            return self.delay_seconds <= 0
        if self.mode == "cron":
            now = datetime.now()
            cron = croniter(self.cron_expression, now)
            try:
                prev_time = cron.get_prev(datetime)
                return prev_time <= now
            except (ValueError, OverflowError):
                return True
        return False

    def to_dict(self) -> dict:
        """Serialize schedule to dictionary."""
        return {
            "mode": self.mode,
            "delay": self.delay_seconds,
            "cron": self.cron_expression,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        """Deserialize schedule from dictionary."""
        return cls(
            mode=data.get("mode", "delay"),
            delay_seconds=data.get("delay", 0),
            cron_expression=data.get("cron", "0 9 * * *"),
        )
