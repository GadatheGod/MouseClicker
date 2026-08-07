import pytest
import tempfile
import os
from pathlib import Path
from src.mouseclicker.config import Config
from src.mouseclicker.click_type import ClickType


class TestConfig:
    """Tests for YAML config loader/saver."""

    def test_default_config_values(self):
        """Config should have sensible defaults."""
        config = Config()
        assert config.default_profile == "default"
        assert config.hotkey_toggle == "Ctrl+Alt+A"
        assert config.position_jitter == 3
        assert config.timing_jitter == 20
        assert config.schedule_mode == "delay"
        assert config.cron_expression == "0 9 * * *"
        assert config.delay_seconds == 0
        assert config.profiles == {}

    def test_load_config_from_file(self):
        """Should load config from YAML file."""
        yaml_content = """
default_profile: gaming
hotkey:
  toggle: "Alt+X"
jitter:
  position: 5
  timing: 30
schedule:
  mode: cron
  cron: "0 12 * * *"
  delay: 0
profiles:
  gaming:
    name: gaming
    click_type: left_click
    interval: 50
    enabled: true
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            try:
                config = Config.load(f.name)
                assert config.default_profile == "gaming"
                assert config.hotkey_toggle == "Alt+X"
                assert config.position_jitter == 5
                assert config.timing_jitter == 30
                assert config.schedule_mode == "cron"
                assert config.cron_expression == "0 12 * * *"
                assert config.delay_seconds == 0
                assert "gaming" in config.profiles
                assert config.profiles["gaming"].click_type == ClickType.LEFT_CLICK
            finally:
                os.unlink(f.name)

    def test_load_config_missing_file(self):
        """Should return default config for missing file."""
        config = Config.load("/nonexistent/path/config.yaml")
        assert config.default_profile == "default"
        assert config.profiles == {}

    def test_save_config_to_file(self):
        """Should save config to YAML file."""
        config = Config()
        config.default_profile = "test"
        config.position_jitter = 10
        config.timing_jitter = 50

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = f.name

        try:
            config.save(config_path)
            loaded = Config.load(config_path)
            assert loaded.default_profile == "test"
            assert loaded.position_jitter == 10
            assert loaded.timing_jitter == 50
        finally:
            os.unlink(config_path)

    def test_add_profile(self):
        """Should add a profile to config."""
        config = Config()
        from src.mouseclicker.click_profile import ClickProfile
        profile = ClickProfile(name="test", click_type=ClickType.RIGHT_CLICK, interval=200)
        config.add_profile(profile)
        assert "test" in config.profiles
        assert config.profiles["test"].click_type == ClickType.RIGHT_CLICK

    def test_remove_profile(self):
        """Should remove a profile from config."""
        config = Config()
        from src.mouseclicker.click_profile import ClickProfile
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        config.add_profile(profile)
        config.remove_profile("test")
        assert "test" not in config.profiles

    def test_get_profile_returns_none_for_missing(self):
        """Should return None for non-existent profile."""
        config = Config()
        assert config.get_profile("nonexistent") is None

    def test_get_profile_returns_existing(self):
        """Should return existing profile."""
        config = Config()
        from src.mouseclicker.click_profile import ClickProfile
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        config.add_profile(profile)
        assert config.get_profile("test") is profile

    def test_to_dict_serializes_profiles(self):
        """Should serialize profiles to dict."""
        config = Config()
        from src.mouseclicker.click_profile import ClickProfile
        profile = ClickProfile(name="test", click_type=ClickType.LEFT_CLICK)
        config.add_profile(profile)
        data = config.to_dict()
        assert "profiles" in data
        assert "test" in data["profiles"]

    def test_from_dict_deserializes_profiles(self):
        """Should deserialize profiles from dict."""
        data = {
            "default_profile": "custom",
            "hotkey": {"toggle": "Ctrl+Z"},
            "jitter": {"position": 1, "timing": 5},
            "schedule": {"mode": "delay", "cron": "", "delay": 10},
            "profiles": {
                "custom": {
                    "name": "custom",
                    "click_type": "right_click",
                    "interval": 150,
                    "enabled": True,
                }
            },
        }
        config = Config.from_dict(data)
        assert config.default_profile == "custom"
        assert config.hotkey_toggle == "Ctrl+Z"
        assert config.position_jitter == 1
        assert config.timing_jitter == 5
        assert config.delay_seconds == 10
        assert "custom" in config.profiles
        assert config.profiles["custom"].click_type == ClickType.RIGHT_CLICK
