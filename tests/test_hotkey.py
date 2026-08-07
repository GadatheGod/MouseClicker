import pytest
from unittest.mock import patch, MagicMock
from src.mouseclicker.hotkey import HotkeyListener


class TestHotkeyListener:
    """Tests for evdev hotkey listener."""

    def test_hotkey_listener_init(self):
        """Should initialize with default hotkey."""
        listener = HotkeyListener()
        assert listener.hotkey == "Ctrl+Alt+A"
        assert listener.is_pressed is False

    def test_hotkey_listener_with_custom_hotkey(self):
        """Should initialize with custom hotkey."""
        listener = HotkeyListener(hotkey="Alt+X")
        assert listener.hotkey == "Alt+X"

    def test_parse_hotkey_splits_modifiers(self):
        """Should parse hotkey string into modifiers and key."""
        listener = HotkeyListener()
        modifiers, key = listener._parse_hotkey("Ctrl+Alt+A")
        assert modifiers == {"ctrl", "alt"}
        assert key == "a"

    def test_parse_hotkey_single_key(self):
        """Should handle single key without modifiers."""
        listener = HotkeyListener()
        modifiers, key = listener._parse_hotkey("F1")
        assert modifiers == set()
        assert key == "f1"

    def test_parse_hotkey_invalid_raises(self):
        """Should raise ValueError for invalid hotkey."""
        listener = HotkeyListener()
        with pytest.raises(ValueError):
            listener._parse_hotkey("Invalid+Hotkey")

    @patch("src.mouseclicker.hotkey.evdev.InputDevice")
    def test_listen_detects_key_press(self, mock_device):
        """Should detect key press event."""
        mock_instance = MagicMock()
        mock_device.return_value = mock_instance

        # Simulate EV_KEY event for 'a' with value 1 (press)
        event = MagicMock()
        event.type = 1  # EV_KEY
        event.code = 30  # KEY_A
        event.value = 1  # press

        mock_instance.read_once.return_value = event

        listener = HotkeyListener()
        modifiers, key = listener._parse_hotkey("Ctrl+Alt+A")
        # Mock ecodes to simulate modifier state
        with patch("src.mouseclicker.hotkey.evdev.ecodes") as mock_ecodes:
            mock_ecodes.KEY_LEFTCTRL = 29
            mock_ecodes.KEY_LEFTALT = 56
            mock_instance.read_once.return_value = event
            result = listener.is_hotkey_pressed(modifiers, key, {"ctrl": True, "alt": True})
            assert result is True

    @patch("src.mouseclicker.hotkey.evdev.InputDevice")
    def test_listen_ignores_non_hotkey(self, mock_device):
        """Should ignore events that don't match hotkey."""
        mock_instance = MagicMock()
        mock_device.return_value = mock_instance

        listener = HotkeyListener()
        # Key "f99" is not in KEY_NAMES
        result = listener.is_hotkey_pressed(set(), "f99", {})
        assert result is False

    def test_get_available_devices_returns_list(self):
        """Should return list of available input devices."""
        listener = HotkeyListener()
        devices = listener.get_available_devices()
        assert isinstance(devices, list)

    def test_key_name_mapping(self):
        """Should map key codes to names."""
        listener = HotkeyListener()
        # KEY_A = 30
        assert listener._get_key_name(30) == "a"
        # KEY_F1 = 59
        assert listener._get_key_name(59) == "f1"
