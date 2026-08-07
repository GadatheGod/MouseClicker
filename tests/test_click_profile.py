import pytest
from src.mouseclicker.click_profile import ClickProfile
from src.mouseclicker.click_type import ClickType


class TestClickProfile:
    """Tests for ClickProfile data model."""

    def test_create_default_profile(self):
        """Should create a profile with sensible defaults."""
        profile = ClickProfile(name="test")
        assert profile.name == "test"
        assert profile.click_type == ClickType.LEFT_CLICK
        assert profile.interval == 100
        assert profile.coordinates is None
        assert profile.long_press_duration == 0.0
        assert profile.enabled is True

    def test_create_profile_with_custom_values(self):
        """Should allow overriding all profile settings."""
        profile = ClickProfile(
            name="custom",
            click_type=ClickType.RIGHT_CLICK,
            interval=500,
            coordinates=(300, 400),
            long_press_duration=1.5,
            enabled=True,
        )
        assert profile.name == "custom"
        assert profile.click_type == ClickType.RIGHT_CLICK
        assert profile.interval == 500
        assert profile.coordinates == (300, 400)
        assert profile.long_press_duration == 1.5
        assert profile.enabled is True

    def test_disable_profile(self):
        """Should allow disabling a profile."""
        profile = ClickProfile(name="disabled", enabled=False)
        assert profile.enabled is False

    def test_invalid_click_type_raises(self):
        """Should raise ValueError for invalid click type."""
        with pytest.raises(ValueError):
            ClickProfile(name="bad", click_type="invalid_type")  # type: ignore

    def test_invalid_interval_raises(self):
        """Should raise ValueError for non-positive interval."""
        with pytest.raises(ValueError):
            ClickProfile(name="bad", interval=0)
        with pytest.raises(ValueError):
            ClickProfile(name="bad", interval=-100)

    def test_invalid_long_press_duration_raises(self):
        """Should raise ValueError for negative long_press_duration."""
        with pytest.raises(ValueError):
            ClickProfile(name="bad", long_press_duration=-1.0)

    def test_profile_to_dict(self):
        """Should serialize profile to dictionary."""
        profile = ClickProfile(
            name="test",
            click_type=ClickType.LEFT_CLICK,
            interval=200,
            coordinates=(100, 200),
        )
        data = profile.to_dict()
        assert data["name"] == "test"
        assert data["click_type"] == "left_click"
        assert data["interval"] == 200
        assert data["coordinates"] == [100, 200]
        assert data["enabled"] is True

    def test_profile_from_dict(self):
        """Should deserialize profile from dictionary."""
        data = {
            "name": "test",
            "click_type": "right_click",
            "interval": 300,
            "coordinates": [150, 250],
            "long_press_duration": 1.0,
            "enabled": True,
        }
        profile = ClickProfile.from_dict(data)
        assert profile.name == "test"
        assert profile.click_type == ClickType.RIGHT_CLICK
        assert profile.interval == 300
        assert profile.coordinates == (150, 250)
        assert profile.long_press_duration == 1.0
        assert profile.enabled is True

    def test_profile_from_dict_defaults(self):
        """Should use defaults for missing dict keys."""
        data = {"name": "minimal"}
        profile = ClickProfile.from_dict(data)
        assert profile.name == "minimal"
        assert profile.click_type == ClickType.LEFT_CLICK
        assert profile.interval == 100
        assert profile.coordinates is None
        assert profile.long_press_duration == 0.0
        assert profile.enabled is True

    def test_profile_from_dict_invalid_click_type(self):
        """Should raise ValueError for invalid click type string."""
        data = {"name": "bad", "click_type": "invalid"}
        with pytest.raises(ValueError):
            ClickProfile.from_dict(data)

    def test_profile_from_dict_invalid_interval(self):
        """Should raise ValueError for invalid interval."""
        data = {"name": "bad", "interval": 0}
        with pytest.raises(ValueError):
            ClickProfile.from_dict(data)
