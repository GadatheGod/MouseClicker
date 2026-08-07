import pytest
from unittest.mock import patch, MagicMock
from src.mouseclicker.daemon import Daemon
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType
from src.mouseclicker.schedule import Schedule


class TestDaemon:
    """Tests for background process manager."""

    def test_daemon_init(self):
        """Should initialize with default settings."""
        daemon = Daemon()
        assert daemon.is_running is False
        assert daemon._schedule is None
        assert daemon._hotkey_listener is None

    @patch("src.mouseclicker.daemon.AutoClicker")
    def test_start_starts_clicker(self, mock_clicker_class):
        """Should start AutoClicker with profile."""
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        daemon = Daemon()
        daemon._profile = profile

        mock_clicker = MagicMock()
        mock_clicker_class.return_value = mock_clicker

        daemon.start()
        mock_clicker_class.assert_called_once_with(profile)
        mock_clicker.start.assert_called_once()
        assert daemon.is_running is True

    @patch("src.mouseclicker.daemon.AutoClicker")
    def test_stop_stops_clicker(self, mock_clicker_class):
        """Should stop AutoClicker."""
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        daemon = Daemon()
        daemon._profile = profile
        old_clicker = MagicMock()
        daemon._clicker = old_clicker
        daemon._running = True

        daemon.stop()
        old_clicker.stop.assert_called_once()
        assert daemon.is_running is False

    @patch("src.mouseclicker.daemon.AutoClicker")
    def test_switch_profile(self, mock_clicker_class):
        """Should switch to a new profile."""
        old_profile = ClickProfile(name="old", click_type=ClickType.LEFT_CLICK)
        new_profile = ClickProfile(name="new", click_type=ClickType.RIGHT_CLICK)

        daemon = Daemon()
        daemon._profile = old_profile
        old_clicker = MagicMock()
        daemon._clicker = old_clicker
        daemon._running = True

        mock_clicker = MagicMock()
        mock_clicker_class.return_value = mock_clicker

        daemon.switch_profile(new_profile)
        old_clicker.stop.assert_called_once()
        mock_clicker_class.assert_called_once_with(new_profile)
        mock_clicker.start.assert_called_once()
        assert daemon._profile == new_profile

    def test_set_schedule(self):
        """Should set schedule."""
        daemon = Daemon()
        schedule = Schedule(mode="cron", cron_expression="0 9 * * *")
        daemon.set_schedule(schedule)
        assert daemon._schedule == schedule

    def test_set_hotkey_listener(self):
        """Should set hotkey listener."""
        daemon = Daemon()
        from src.mouseclicker.hotkey import HotkeyListener
        hotkey = HotkeyListener(hotkey="Ctrl+Alt+A")
        daemon.set_hotkey_listener(hotkey)
        assert daemon._hotkey_listener == hotkey

    def test_get_status_with_schedule(self):
        """Should return status with schedule info."""
        daemon = Daemon()
        daemon._profile = ClickProfile(name="test")
        daemon._schedule = Schedule(mode="cron", cron_expression="0 9 * * *")
        daemon._running = True
        status = daemon.get_status()
        assert status["running"] is True
        assert status["profile"] == "test"
        assert status["schedule_mode"] == "cron"

    def test_get_status_not_running(self):
        """Should return not running status."""
        daemon = Daemon()
        status = daemon.get_status()
        assert status["running"] is False
