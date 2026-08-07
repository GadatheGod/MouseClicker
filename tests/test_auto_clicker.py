import pytest
import time
from unittest.mock import patch, MagicMock
from src.mouseclicker.auto_clicker import AutoClicker
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType


class TestAutoClicker:
    """Tests for core click loop engine."""

    @patch("src.mouseclicker.auto_clicker.os.path.exists")
    def test_start_clicks_at_interval(self, mock_exists):
        """AutoClicker should click at configured interval."""
        mock_exists.return_value = True
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=100,
        )
        clicker = AutoClicker(profile)

        with patch.object(clicker, "_inject_click") as mock_inject:
            # Run for 250ms — should get ~2 clicks at 100ms interval
            clicker.start(duration=0.25)
            assert mock_inject.call_count >= 1

    @patch("src.mouseclicker.auto_clicker.os.path.exists")
    def test_stop_stops_clicking(self, mock_exists):
        """AutoClicker should stop when stop() is called."""
        mock_exists.return_value = True
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=50,
        )
        clicker = AutoClicker(profile)

        with patch.object(clicker, "_inject_click") as mock_inject:
            clicker.start(duration=1.0)
            time.sleep(0.1)
            clicker.stop()
            call_count = mock_inject.call_count
            time.sleep(0.2)
            # Should not increment after stop
            assert mock_inject.call_count == call_count

    @patch("src.mouseclicker.auto_clicker.os.path.exists")
    def test_is_running_flag(self, mock_exists):
        """is_running should reflect actual state."""
        mock_exists.return_value = True
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=100,
        )
        clicker = AutoClicker(profile)
        assert clicker.is_running is False

        with patch.object(clicker, "_inject_click"):
            clicker.start(duration=0.1)
            assert clicker.is_running is True

    @patch("src.mouseclicker.auto_clicker.os.path.exists")
    def test_invalid_device_raises(self, mock_exists):
        """Should raise error if device doesn't exist."""
        mock_exists.return_value = False
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=100,
        )
        clicker = AutoClicker(profile)
        with pytest.raises(FileNotFoundError):
            clicker.start(duration=0.1)

    @patch("src.mouseclicker.auto_clicker.os.path.exists")
    def test_disabled_profile_does_not_click(self, mock_exists):
        """Disabled profile should not produce clicks."""
        mock_exists.return_value = True
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=50,
            enabled=False,
        )
        clicker = AutoClicker(profile)

        with patch.object(clicker, "_inject_click") as mock_inject:
            clicker.start(duration=0.2)
            assert mock_inject.call_count == 0

    def test_getter_properties(self):
        """AutoClicker should expose profile and is_running."""
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        clicker = AutoClicker(profile)
        assert clicker.profile is profile
        assert clicker.is_running is False
