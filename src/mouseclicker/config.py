"""YAML config loader/saver."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .click_profile import ClickProfile
from .click_type import ClickType


class Config:
    """Manages persistent settings stored as YAML."""

    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "mouseclicker" / "config.yaml"

    def __init__(
        self,
        default_profile: str = "default",
        hotkey_toggle: str = "Ctrl+Alt+A",
        position_jitter: int = 3,
        timing_jitter: int = 20,
        schedule_mode: str = "delay",
        cron_expression: str = "0 9 * * *",
        delay_seconds: int = 0,
        profiles: dict[str, ClickProfile] | None = None,
    ):
        self.default_profile = default_profile
        self.hotkey_toggle = hotkey_toggle
        self.position_jitter = position_jitter
        self.timing_jitter = timing_jitter
        self.schedule_mode = schedule_mode
        self.cron_expression = cron_expression
        self.delay_seconds = delay_seconds
        self.profiles: dict[str, ClickProfile] = profiles or {}

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> Config:
        """Load config from YAML file, returning defaults if file missing."""
        path = Path(config_path or cls.DEFAULT_CONFIG_PATH)
        if not path.exists():
            return cls()

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
            return cls.from_dict(data)
        except (yaml.YAMLError, KeyError, ValueError):
            return cls()

    def save(self, config_path: str | Path | None = None) -> None:
        """Save config to YAML file."""
        path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    def add_profile(self, profile: ClickProfile) -> None:
        """Add or update a profile."""
        self.profiles[profile.name] = profile

    def remove_profile(self, name: str) -> None:
        """Remove a profile by name."""
        self.profiles.pop(name, None)

    def get_profile(self, name: str) -> ClickProfile | None:
        """Get a profile by name, or None if not found."""
        return self.profiles.get(name)

    def to_dict(self) -> dict[str, Any]:
        """Serialize config to dictionary."""
        profiles_dict = {}
        for name, profile in self.profiles.items():
            profiles_dict[name] = profile.to_dict()

        return {
            "default_profile": self.default_profile,
            "hotkey": {"toggle": self.hotkey_toggle},
            "jitter": {
                "position": self.position_jitter,
                "timing": self.timing_jitter,
            },
            "schedule": {
                "mode": self.schedule_mode,
                "cron": self.cron_expression,
                "delay": self.delay_seconds,
            },
            "profiles": profiles_dict,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Deserialize config from dictionary."""
        hotkey = data.get("hotkey") or {}
        jitter = data.get("jitter") or {}
        schedule = data.get("schedule") or {}

        profiles: dict[str, ClickProfile] = {}
        for name, profile_data in data.get("profiles", {}).items():
            try:
                profiles[name] = ClickProfile.from_dict(profile_data)
            except (ValueError, KeyError):
                continue

        return cls(
            default_profile=data.get("default_profile", "default"),
            hotkey_toggle=hotkey.get("toggle", "Ctrl+Alt+A"),
            position_jitter=jitter.get("position", 3),
            timing_jitter=jitter.get("timing", 20),
            schedule_mode=schedule.get("mode", "delay"),
            cron_expression=schedule.get("cron", "0 9 * * *"),
            delay_seconds=schedule.get("delay", 0),
            profiles=profiles,
        )
