"""Tests for utility functions."""

import pytest
from mediautil.utils import format_bytes


class TestFormatBytes:
    """Test the format_bytes function."""

    def test_bytes(self):
        """Test formatting of bytes."""
        assert format_bytes(0) == "0.00 B"
        assert format_bytes(500) == "500.00 B"
        assert format_bytes(1023) == "1023.00 B"

    def test_kilobytes(self):
        """Test formatting of kilobytes."""
        assert format_bytes(1024) == "1.00 KiB"
        assert format_bytes(1536) == "1.50 KiB"
        assert format_bytes(1024 * 1023) == "1023.00 KiB"

    def test_megabytes(self):
        """Test formatting of megabytes."""
        assert format_bytes(1024 * 1024) == "1.00 MiB"
        assert format_bytes(1024 * 1024 * 1.5) == "1.50 MiB"

    def test_gigabytes(self):
        """Test formatting of gigabytes."""
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GiB"
        assert format_bytes(1024 * 1024 * 1024 * 2.5) == "2.50 GiB"

    def test_terabytes(self):
        """Test formatting of terabytes."""
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.00 TiB"

    def test_decimal_places(self):
        """Test custom decimal places."""
        assert format_bytes(1024, decimal_places=0) == "1 KiB"
        assert format_bytes(1024, decimal_places=1) == "1.0 KiB"
        assert format_bytes(1024, decimal_places=3) == "1.000 KiB"
