import pytest
from unittest.mock import patch, MagicMock
import argparse
from src.mouseclicker.cli import (
    cmd_start,
    cmd_stop,
    cmd_status,
    cmd_profiles,
    cmd_script,
    cmd_schedule,
)
from src.mouseclicker.config import Config
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType


class TestCmdStart:
    """Tests for start command."""

    def test_start_with_valid_profile(self, tmp_path):
        """Should start with valid profile."""
        config = Config()
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK, interval=100)
        config.add_profile(profile)

        args = argparse.Namespace(profile="test", interval=None, type=None)

        with patch("src.mouseclicker.cli.Daemon") as mock_daemon:
            mock_instance = MagicMock()
            mock_daemon.return_value = mock_instance
            cmd_start(args, config)
            mock_daemon.assert_called_once()
            mock_instance.start.assert_called_once()

    def test_start_with_cli_overrides(self, tmp_path):
        """Should apply CLI overrides."""
        config = Config()
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK, interval=100)
        config.add_profile(profile)

        args = argparse.Namespace(profile="test", interval=200, type="right_click")

        with patch("src.mouseclicker.cli.Daemon") as mock_daemon:
            mock_instance = MagicMock()
            mock_daemon.return_value = mock_instance
            cmd_start(args, config)
            assert profile.interval == 200
            assert profile.click_type == ClickType.RIGHT_CLICK


class TestCmdStop:
    """Tests for stop command."""

    def test_stop(self):
        """Should stop the daemon."""
        with patch("src.mouseclicker.cli.Daemon") as mock_daemon:
            mock_instance = MagicMock()
            mock_daemon.return_value = mock_instance
            cmd_stop()
            mock_instance.stop.assert_called_once()


class TestCmdStatus:
    """Tests for status command."""

    def test_status_running(self):
        """Should show running status."""
        with patch("src.mouseclicker.cli.Daemon") as mock_daemon:
            mock_instance = MagicMock()
            mock_daemon.return_value = mock_instance
            mock_instance.get_status.return_value = {"running": True, "profile": "test"}
            cmd_status()

    def test_status_stopped(self):
        """Should show stopped status."""
        with patch("src.mouseclicker.cli.Daemon") as mock_daemon:
            mock_instance = MagicMock()
            mock_daemon.return_value = mock_instance
            mock_instance.get_status.return_value = {"running": False, "profile": None}
            cmd_status()


class TestCmdProfiles:
    """Tests for profiles command."""

    def test_list_profiles(self):
        """Should list profiles."""
        config = Config()
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        config.add_profile(profile)

        args = argparse.Namespace(action="list")
        cmd_profiles(args, config)

    def test_set_default_profile(self):
        """Should set default profile."""
        config = Config()

        args = argparse.Namespace(action="set", name="gaming")
        with patch.object(config, "save"):
            cmd_profiles(args, config)
            assert config.default_profile == "gaming"

    def test_add_profile(self):
        """Should add a new profile."""
        config = Config()

        args = argparse.Namespace(action="add", name="new", type="left_click", interval=50)
        with patch.object(config, "save"):
            cmd_profiles(args, config)
            assert "new" in config.profiles


class TestCmdScript:
    """Tests for script command."""

    def test_run_script(self, tmp_path):
        """Should run a script file."""
        script_file = tmp_path / "test.msck"
        script_file.write_text("delay(100)\nleft_click(100, 200)\n")

        args = argparse.Namespace(action="run", file=str(script_file))
        with patch("src.mouseclicker.cli.ScriptEngine") as mock_engine:
            mock_instance = MagicMock()
            mock_engine.return_value = mock_instance
            mock_instance.run.return_value = "completed"
            cmd_script(args)


class TestCmdSchedule:
    """Tests for schedule command."""

    def test_set_schedule(self):
        """Should set schedule."""
        config = Config()

        args = argparse.Namespace(action="set", mode="cron", cron="0 9 * * *", delay=None)
        with patch.object(config, "save"):
            cmd_schedule(args, config)
            assert config.schedule_mode == "cron"
            assert config.cron_expression == "0 9 * * *"
