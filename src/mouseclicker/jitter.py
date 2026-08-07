"""Position and timing jitter for human-like clicking."""

from __future__ import annotations

import random


class Jitter:
    """Applies random perturbation to make clicks appear human-like.

    Attributes:
        position: Max pixel offset for position jitter (±N pixels).
        timing: Max millisecond offset for timing jitter (±N ms).
    """

    def __init__(self, position: int = 3, timing: int = 20) -> None:
        if position < 0:
            raise ValueError(f"Position jitter must be non-negative, got {position}")
        if timing < 0:
            raise ValueError(f"Timing jitter must be non-negative, got {timing}")
        self.position = position
        self.timing = timing

    def position_offset(self) -> int:
        """Return a random offset between -position and +position."""
        return random.randint(-self.position, self.position)

    def timing_offset(self) -> int:
        """Return a random offset between -timing and +timing."""
        return random.randint(-self.timing, self.timing)

    def apply_position_jitter(self, x: int | None, y: int | None) -> tuple[int | None, int | None]:
        """Apply position jitter to coordinates.

        Args:
            x: Target X coordinate, or None to skip.
            y: Target Y coordinate, or None to skip.

        Returns:
            Tuple of (adjusted_x, adjusted_y).
        """
        if x is None and y is None:
            return None, None
        return (
            (x + self.position_offset()) if x is not None else x,
            (y + self.position_offset()) if y is not None else y,
        )

    def apply_timing_jitter(self, interval_ms: int) -> int:
        """Apply timing jitter to interval.

        Args:
            interval_ms: Original interval in milliseconds.

        Returns:
            Adjusted interval (minimum 0).
        """
        offset = self.timing_offset()
        return max(0, interval_ms + offset)
