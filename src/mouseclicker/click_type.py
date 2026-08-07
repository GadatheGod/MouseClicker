"""ClickType enum and evdev mouse event injection."""

from __future__ import annotations

import enum
import os
import time

import evdev


class ClickType(str, enum.Enum):
    """Types of mouse actions supported by MouseClicker."""

    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    LONG_PRESS = "long_press"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"

    def inject(
        self,
        device_path: str,
        x: int | None,
        y: int | None,
        current_x: int | None,
        current_y: int | None,
        long_press_duration: float = 0.0,
    ) -> None:
        """Inject a mouse click event via evdev.

        Args:
            device_path: Path to the evdev input device (e.g. /dev/input/event0).
            x: Target X coordinate, or None to use current position.
            y: Target Y coordinate, or None to use current position.
            current_x: Current mouse X position (used when x is None).
            current_y: Current mouse Y position (used when y is None).
            long_press_duration: Duration in seconds for LONG_PRESS type.

        Raises:
            FileNotFoundError: If device_path doesn't exist.
            PermissionError: If insufficient permissions to write to device.
        """
        if not os.path.exists(device_path):
            raise FileNotFoundError(f"Device not found: {device_path}")

        try:
            device = evdev.InputDevice(device_path)
        except PermissionError:
            raise

        # Move to target coordinates if specified
        target_x = x if x is not None else (current_x or 0)
        target_y = y if y is not None else (current_y or 0)

        if target_x != 0 or target_y != 0:
            device.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_X, target_x)
            device.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_Y, target_y)
            device.syn()

        if self == ClickType.LEFT_CLICK:
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 1)
            device.syn()
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 0)
            device.syn()

        elif self == ClickType.RIGHT_CLICK:
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_RIGHT, 1)
            device.syn()
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_RIGHT, 0)
            device.syn()

        elif self == ClickType.LONG_PRESS:
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 1)
            device.syn()
            if long_press_duration > 0:
                time.sleep(long_press_duration)
            device.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 0)
            device.syn()

        elif self == ClickType.SCROLL_UP:
            device.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_WHEEL, 1)
            device.syn()

        elif self == ClickType.SCROLL_DOWN:
            device.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_WHEEL, -1)
            device.syn()

        device.close()
