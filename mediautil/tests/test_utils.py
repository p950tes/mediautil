"""Tests for utility functions."""

import pytest
from mediautil.utils import format_bytes, format_bitrate, format_seconds


class TestFormatBytes:
    """Test the format_bytes function."""

    def test_zero_bytes(self):
        """Test formatting of zero bytes."""
        assert format_bytes(0) == "0 B"

    def test_bytes(self):
        """Test formatting of bytes."""
        assert format_bytes(500) == "500 B"
        assert format_bytes(1023) == "1023 B"

    def test_kilobytes(self):
        """Test formatting of kilobytes."""
        assert format_bytes(1024) == "1.0 KiB"
        assert format_bytes(1536) == "1.5 KiB"

    def test_megabytes(self):
        """Test formatting of megabytes."""
        assert format_bytes(1024 * 1024) == "1.00 MiB"

    def test_gigabytes(self):
        """Test formatting of gigabytes."""
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GiB"


class TestFormatBitrate:
    """Test the format_bitrate function."""

    def test_bits_per_second(self):
        """Test formatting of bitrates."""
        assert format_bitrate(100) == "100 b/s"
        assert format_bitrate(1000) == "1.0 kb/s"
        assert format_bitrate(1500) == "1.5 kb/s"
        assert format_bitrate(1000000) == "1.00 Mb/s"


class TestFormatSeconds:
    """Test the format_seconds function."""

    def test_zero_seconds(self):
        """Test formatting of zero seconds."""
        assert format_seconds(0) == "00:00:00.000"
        assert format_seconds(0.0) == "00:00:00.000"

    def test_seconds_only(self):
        """Test formatting of seconds under 1 minute."""
        assert format_seconds(5.5) == "00:00:05.500"
        assert format_seconds(59.999) == "00:00:59.999"

    def test_minutes_and_seconds(self):
        """Test formatting of durations over 1 minute."""
        assert format_seconds(65.5) == "00:01:05.500"
        assert format_seconds(3661.5) == "01:01:01.500"

    def test_hours_minutes_seconds(self):
        """Test formatting of durations over 1 hour."""
        assert format_seconds(3600) == "01:00:00.000"
        assert format_seconds(7323.123) == "02:02:03.123"

    def test_none_input(self):
        """Test handling of None input."""
        assert format_seconds(None) is None

    def test_string_input(self):
        """Test handling of string input."""
        assert format_seconds("120.5") == "00:02:00.500"
