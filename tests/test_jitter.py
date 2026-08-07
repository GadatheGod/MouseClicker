import pytest
from src.mouseclicker.jitter import Jitter


class TestJitter:
    """Tests for position and timing jitter."""

    def test_position_jitter_returns_offset(self):
        """position_jitter should return a random offset within range."""
        jitter = Jitter(position=5, timing=0)
        offset = jitter.position_offset()
        assert -5 <= offset <= 5

    def test_position_jitter_zero_range(self):
        """position_jitter with range 0 should return 0."""
        jitter = Jitter(position=0, timing=0)
        offset = jitter.position_offset()
        assert offset == 0

    def test_timing_jitter_returns_offset(self):
        """timing_jitter should return a random offset within range."""
        jitter = Jitter(position=0, timing=20)
        offset = jitter.timing_offset()
        assert -20 <= offset <= 20

    def test_timing_jitter_zero_range(self):
        """timing_jitter with range 0 should return 0."""
        jitter = Jitter(position=0, timing=0)
        offset = jitter.timing_offset()
        assert offset == 0

    def test_apply_position_jitter(self):
        """apply_position_jitter should return adjusted coordinates."""
        jitter = Jitter(position=3, timing=0)
        x, y = jitter.apply_position_jitter(100, 200)
        assert 97 <= x <= 103
        assert 197 <= y <= 203

    def test_apply_position_jitter_none_coords(self):
        """apply_position_jitter should return None for None coordinates."""
        jitter = Jitter(position=3, timing=0)
        x, y = jitter.apply_position_jitter(None, None)
        assert x is None
        assert y is None

    def test_apply_timing_jitter(self):
        """apply_timing_jitter should return adjusted interval."""
        jitter = Jitter(position=0, timing=10)
        adjusted = jitter.apply_timing_jitter(100)
        assert 90 <= adjusted <= 110

    def test_apply_timing_jitter_zero_interval(self):
        """apply_timing_jitter should not go below 0."""
        jitter = Jitter(position=0, timing=50)
        adjusted = jitter.apply_timing_jitter(10)
        assert adjusted >= 0

    def test_negative_jitter_raises(self):
        """Should raise ValueError for negative jitter ranges."""
        with pytest.raises(ValueError):
            Jitter(position=-5, timing=-10)

    def test_invalid_position_raises(self):
        """Should raise ValueError for negative position range."""
        with pytest.raises(ValueError):
            Jitter(position=-1, timing=0)

    def test_invalid_timing_raises(self):
        """Should raise ValueError for negative timing range."""
        with pytest.raises(ValueError):
            Jitter(position=0, timing=-1)
