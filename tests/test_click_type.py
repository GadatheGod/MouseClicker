import pytest
from unittest.mock import patch, MagicMock
from src.mouseclicker.click_type import ClickType


class TestClickType:
    """Tests for ClickType enum and evdev injection."""

    def test_click_type_enum_values(self):
        """ClickType should have all five members."""
        assert ClickType.LEFT_CLICK == "left_click"
        assert ClickType.RIGHT_CLICK == "right_click"
        assert ClickType.LONG_PRESS == "long_press"
        assert ClickType.SCROLL_UP == "scroll_up"
        assert ClickType.SCROLL_DOWN == "scroll_down"

    @patch("src.mouseclicker.click_type.evdev")
    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_left_click_injects_events(self, mock_exists, mock_evdev):
        """left_click should inject BTN_LEFT press and release."""
        mock_exists.return_value = True
        mock_device = MagicMock()
        mock_evdev.InputDevice.return_value = mock_device

        click_type = ClickType.LEFT_CLICK
        click_type.inject("/dev/input/event0", 100, 200, None, None)

        mock_device.write.assert_any_call(
            mock_evdev.ecodes.EV_KEY, mock_evdev.ecodes.BTN_LEFT, 1
        )
        mock_device.write.assert_any_call(
            mock_evdev.ecodes.EV_KEY, mock_evdev.ecodes.BTN_LEFT, 0
        )
        mock_device.syn.assert_called()

    @patch("src.mouseclicker.click_type.evdev")
    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_right_click_injects_events(self, mock_exists, mock_evdev):
        """right_click should inject BTN_RIGHT press and release."""
        mock_exists.return_value = True
        mock_device = MagicMock()
        mock_evdev.InputDevice.return_value = mock_device

        click_type = ClickType.RIGHT_CLICK
        click_type.inject("/dev/input/event0", 100, 200, None, None)

        mock_device.write.assert_any_call(
            mock_evdev.ecodes.EV_KEY, mock_evdev.ecodes.BTN_RIGHT, 1
        )
        mock_device.write.assert_any_call(
            mock_evdev.ecodes.EV_KEY, mock_evdev.ecodes.BTN_RIGHT, 0
        )
        mock_device.syn.assert_called()

    @patch("src.mouseclicker.click_type.evdev.InputDevice")
    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_long_press_injects_press_release(self, mock_exists, mock_input_device):
        """long_press should inject press, then release after duration."""
        mock_exists.return_value = True
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        click_type = ClickType.LONG_PRESS
        click_type.inject("/dev/input/event0", 100, 200, None, 2.0)

        # Check press
        calls = mock_device.write.call_args_list
        press_calls = [c for c in calls if c[0][2] == 1]
        release_calls = [c for c in calls if c[0][2] == 0]
        assert len(press_calls) >= 1
        assert len(release_calls) >= 1

    @patch("src.mouseclicker.click_type.evdev.InputDevice")
    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_scroll_up_injects_wheel(self, mock_exists, mock_input_device):
        """scroll_up should inject wheel up event."""
        mock_exists.return_value = True
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        click_type = ClickType.SCROLL_UP
        click_type.inject("/dev/input/event0", 100, 200, None, None)

        mock_device.write.assert_any_call(2, 8, 1)  # EV_REL, REL_WHEEL, positive
        mock_device.syn.assert_called()

    @patch("src.mouseclicker.click_type.evdev.InputDevice")
    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_scroll_down_injects_wheel(self, mock_exists, mock_input_device):
        """scroll_down should inject wheel down event."""
        mock_exists.return_value = True
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        click_type = ClickType.SCROLL_DOWN
        click_type.inject("/dev/input/event0", 100, 200, None, None)

        mock_device.write.assert_any_call(2, 8, -1)  # EV_REL, REL_WHEEL, negative
        mock_device.syn.assert_called()

    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_inject_raises_on_missing_device(self, mock_exists):
        """inject should raise FileNotFoundError if device doesn't exist."""
        mock_exists.return_value = False
        click_type = ClickType.LEFT_CLICK
        with pytest.raises(FileNotFoundError):
            click_type.inject("/dev/input/event999", 100, 200, None, None)

    @patch("src.mouseclicker.click_type.os.path.exists")
    def test_inject_raises_on_permission_error(self, mock_exists):
        """inject should raise PermissionError on permission denied."""
        mock_exists.return_value = True
        with patch("src.mouseclicker.click_type.evdev.InputDevice") as mock_device:
            mock_device.side_effect = PermissionError("Permission denied")
            click_type = ClickType.LEFT_CLICK
            with pytest.raises(PermissionError):
                click_type.inject("/dev/input/event0", 100, 200, None, None)
