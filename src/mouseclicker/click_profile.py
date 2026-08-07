"""ClickProfile data model."""

from __future__ import annotations

from dataclasses import dataclass, field

from .click_type import ClickType


@dataclass
class ClickProfile:
    """A named set of click settings.

    Attributes:
        name: Human-readable name for this profile.
        click_type: The kind of mouse action to perform.
        interval: Time between clicks in milliseconds (must be > 0).
        coordinates: Target (x, y) coordinates, or None for current position.
        long_press_duration: Hold duration in seconds for LONG_PRESS type.
        enabled: Whether this profile is active.
    """

    name: str
    click_type: ClickType = ClickType.LEFT_CLICK
    interval: int = 100
    coordinates: tuple[int, int] | None = None
    long_press_duration: float = 0.0
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate profile settings."""
        if self.click_type not in ClickType:
            raise ValueError(
                f"Invalid click_type: {self.click_type!r}. "
                f"Must be one of: {[e.value for e in ClickType]}"
            )
        if self.interval <= 0:
            raise ValueError(f"Interval must be positive, got {self.interval}")
        if self.long_press_duration < 0:
            raise ValueError(
                f"long_press_duration must be non-negative, got {self.long_press_duration}"
            )

    def to_dict(self) -> dict:
        """Serialize profile to dictionary for config storage."""
        return {
            "name": self.name,
            "click_type": self.click_type.value,
            "interval": self.interval,
            "coordinates": list(self.coordinates) if self.coordinates else None,
            "long_press_duration": self.long_press_duration,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ClickProfile:
        """Deserialize profile from dictionary."""
        click_type = ClickType(data.get("click_type", "left_click"))
        coordinates = tuple(data["coordinates"]) if data.get("coordinates") else None
        return cls(
            name=data["name"],
            click_type=click_type,
            interval=data.get("interval", 100),
            coordinates=coordinates,
            long_press_duration=data.get("long_press_duration", 0.0),
            enabled=data.get("enabled", True),
        )
