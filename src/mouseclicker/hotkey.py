"""Hotkey listener using evdev for global keyboard shortcuts."""

from __future__ import annotations

import evdev
from evdev import ecodes


class HotkeyListener:
    """Listens for global keyboard shortcuts via evdev.

    Attributes:
        hotkey: The configured hotkey string (e.g. 'Ctrl+Alt+A').
        is_pressed: Whether the hotkey is currently pressed.
    """

    # Modifier key mappings
    MODIFIER_KEYS = {
        "ctrl": [ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL],
        "alt": [ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT],
        "shift": [ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT],
        "meta": [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
    }

    # Key code to name mapping (common keys)
    KEY_NAMES = {
        30: "a", 31: "b", 32: "c", 33: "d", 34: "e", 35: "f", 36: "g",
        37: "h", 38: "i", 39: "j", 40: "k", 41: "l", 42: "m", 43: "n",
        44: "o", 45: "p", 46: "q", 47: "r", 48: "s", 49: "t", 50: "u",
        51: "v", 52: "w", 53: "x", 54: "y", 55: "z",
        59: "f1", 60: "f2", 61: "f3", 62: "f4", 63: "f5", 64: "f6",
        65: "f7", 66: "f8", 67: "f9", 68: "f10", 69: "f11", 70: "f12",
    }

    def __init__(self, hotkey: str = "Ctrl+Alt+A") -> None:
        self.hotkey = hotkey
        self.is_pressed = False
        self._modifiers, self._key = self._parse_hotkey(hotkey)

    def _parse_hotkey(self, hotkey: str) -> tuple[set[str], str]:
        """Parse hotkey string into modifiers and key."""
        parts = hotkey.lower().split("+")
        valid_modifiers = set(self.MODIFIER_KEYS.keys())
        modifiers = set()
        key = parts[-1]

        for part in parts[:-1]:
            part = part.strip()
            if part not in valid_modifiers:
                raise ValueError(f"Invalid modifier: {part}")
            modifiers.add(part)

        return modifiers, key

    def _get_key_name(self, code: int) -> str:
        """Get key name from code."""
        return self.KEY_NAMES.get(code, str(code))

    def is_hotkey_pressed(
        self,
        modifiers: set[str] | None = None,
        key: str | None = None,
        active_modifiers: dict[str, bool] | None = None,
    ) -> bool:
        """Check if the hotkey is currently pressed.

        Args:
            modifiers: Expected modifiers (defaults to parsed hotkey).
            key: Expected key (defaults to parsed hotkey).
            active_modifiers: Currently active modifier states.

        Returns:
            True if the hotkey is pressed.
        """
        if modifiers is None:
            modifiers = self._modifiers
        if key is None:
            key = self._key
        if active_modifiers is None:
            active_modifiers = {}

        # Check if all modifiers are active
        for mod in modifiers:
            if not active_modifiers.get(mod, False):
                return False

        return self._get_key_name(self._get_key_code(key)) == key.lower()

    def _get_key_code(self, key_name: str) -> int:
        """Get key code from key name."""
        for code, name in self.KEY_NAMES.items():
            if name == key_name.lower():
                return code
        return 0

    def get_available_devices(self) -> list[str]:
        """Get list of available evdev input devices."""
        try:
            return [dev.path for dev in evdev.list_devices()]
        except PermissionError:
            return []
