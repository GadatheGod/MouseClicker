import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.mouseclicker.schedule import Schedule


class TestSchedule:
    """Tests for schedule module."""

    def test_schedule_default(self):
        """Should have sensible defaults."""
        schedule = Schedule()
        assert schedule.mode == "delay"
        assert schedule.delay_seconds == 0
        assert schedule.cron_expression == "0 9 * * *"

    def test_schedule_invalid_mode_raises(self):
        """Should raise ValueError for invalid mode."""
        with pytest.raises(ValueError):
            Schedule(mode="invalid")

    def test_delay_mode_next_run(self):
        """Delay mode should return next_run in the future."""
        schedule = Schedule(mode="delay", delay_seconds=60)
        next_run = schedule.next_run()
        assert next_run is not None
        assert next_run > datetime.now()

    def test_delay_mode_zero_returns_none(self):
        """Delay mode with 0 seconds should return None."""
        schedule = Schedule(mode="delay", delay_seconds=0)
        next_run = schedule.next_run()
        assert next_run is None

    def test_cron_mode_next_run(self):
        """Cron mode should return next run time."""
        schedule = Schedule(mode="cron", cron_expression="0 9 * * *")
        next_run = schedule.next_run()
        assert next_run is not None
        assert next_run > datetime.now()

    def test_is_due_delay_zero(self):
        """Delay mode with 0 should be due."""
        schedule = Schedule(mode="delay", delay_seconds=0)
        assert schedule.is_due() is True

    def test_is_due_delay_positive(self):
        """Delay mode with positive seconds should not be due."""
        schedule = Schedule(mode="delay", delay_seconds=60)
        assert schedule.is_due() is False

    def test_wait_until_delay_zero(self):
        """Wait until with delay 0 should return True immediately."""
        schedule = Schedule(mode="delay", delay_seconds=0)
        assert schedule.wait_until() is True

    def test_to_dict_serializes(self):
        """Should serialize to dictionary."""
        schedule = Schedule(mode="cron", delay_seconds=30, cron_expression="0 12 * * *")
        data = schedule.to_dict()
        assert data["mode"] == "cron"
        assert data["delay"] == 30
        assert data["cron"] == "0 12 * * *"

    def test_from_dict_deserializes(self):
        """Should deserialize from dictionary."""
        data = {
            "mode": "cron",
            "delay": 30,
            "cron": "0 12 * * *",
        }
        schedule = Schedule.from_dict(data)
        assert schedule.mode == "cron"
        assert schedule.delay_seconds == 30
        assert schedule.cron_expression == "0 12 * * *"
