"""Tests for command executor module."""

import pytest
from mediautil.cmdexecutor import CommandExecutionResult


class TestCommandExecutionResult:
    """Test CommandExecutionResult dataclass."""

    def test_is_success_zero_returncode(self):
        """Test successful execution with returncode 0."""
        result = CommandExecutionResult(args=["test"], returncode=0)
        assert result.is_success() is True
        assert result.is_failed() is False

    def test_is_success_none_returncode(self):
        """Test successful execution with None returncode."""
        result = CommandExecutionResult(args=["test"], returncode=None)
        assert result.is_success() is False
        assert result.is_failed() is True

    def test_is_failed_nonzero_returncode(self):
        """Test failed execution with non-zero returncode."""
        result = CommandExecutionResult(args=["test"], returncode=1)
        assert result.is_failed() is True
        assert result.is_success() is False

    def test_get_command_as_string_empty(self):
        """Test command string conversion with empty args."""
        result = CommandExecutionResult(args=[])
        assert result.get_command_as_string() == ""

    def test_get_command_as_string(self):
        """Test command string conversion."""
        result = CommandExecutionResult(args=["ffmpeg", "-i", "input.mp4", "-c", "copy"])
        assert result.get_command_as_string() == "ffmpeg -i input.mp4 -c copy"

    def test_result_with_output(self):
        """Test result with stdout and stderr."""
        result = CommandExecutionResult(
            args=["echo", "hello"],
            stdout="hello\n",
            stderr="",
            returncode=0
        )
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.is_success() is True
