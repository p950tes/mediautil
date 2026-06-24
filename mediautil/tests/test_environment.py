"""Tests for environment module."""

import pytest
from mediautil.environment import GlobalSettings, print_error, is_verbose, is_debug, verbose, debug


class TestGlobalSettings:
    """Test GlobalSettings dataclass."""

    def test_default_values(self):
        """Test default values of GlobalSettings."""
        assert GlobalSettings.VERBOSE is False
        assert GlobalSettings.DEBUG is False
        assert GlobalSettings.CONFIRM is True
        assert GlobalSettings.DRY_RUN is False

    def test_modify_settings(self):
        """Test modifying GlobalSettings."""
        original_verbose = GlobalSettings.VERBOSE
        GlobalSettings.VERBOSE = True
        assert GlobalSettings.VERBOSE is True
        GlobalSettings.VERBOSE = original_verbose


class TestLoggingFunctions:
    """Test logging utility functions."""

    def test_is_verbose_false(self):
        """Test is_verbose when VERBOSE is False."""
        GlobalSettings.VERBOSE = False
        assert is_verbose() is False

    def test_is_verbose_true(self):
        """Test is_verbose when VERBOSE is True."""
        GlobalSettings.VERBOSE = True
        assert is_verbose() is True
        GlobalSettings.VERBOSE = False

    def test_is_debug_false(self):
        """Test is_debug when DEBUG is False."""
        GlobalSettings.DEBUG = False
        assert is_debug() is False

    def test_is_debug_true(self):
        """Test is_debug when DEBUG is True."""
        GlobalSettings.DEBUG = True
        assert is_debug() is True
        GlobalSettings.DEBUG = False

    def test_verbose_does_not_print_when_disabled(self, capsys):
        """Test that verbose does not print when VERBOSE is False."""
        GlobalSettings.VERBOSE = False
        verbose("This should not appear")
        captured = capsys.readouterr()
        assert "This should not appear" not in captured.err

    def test_verbose_prints_when_enabled(self, capsys):
        """Test that verbose prints when VERBOSE is True."""
        GlobalSettings.VERBOSE = True
        verbose("This should appear")
        captured = capsys.readouterr()
        assert "This should appear" in captured.err
        GlobalSettings.VERBOSE = False

    def test_debug_does_not_print_when_disabled(self, capsys):
        """Test that debug does not print when DEBUG is False."""
        GlobalSettings.DEBUG = False
        debug("Debug message should not appear")
        captured = capsys.readouterr()
        assert "Debug message should not appear" not in captured.err

    def test_debug_prints_when_enabled(self, capsys):
        """Test that debug prints when DEBUG is True."""
        GlobalSettings.DEBUG = True
        debug("Debug message should appear")
        captured = capsys.readouterr()
        assert "Debug message should appear" in captured.err
        GlobalSettings.DEBUG = False
