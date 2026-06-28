"""Tests for CLI module."""

import pytest
from unittest.mock import patch
from mediautil.cli import parse_args
from mediautil.models import CommandArguments


def mock_is_valid_file(parser, x):
    """Mock is_valid_file to always return the input."""
    return x


class TestParseArgs:
    """Test argument parsing."""

    def test_basic_file_argument(self):
        """Test basic file argument parsing."""
        with patch('sys.argv', ['mediautil', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.files == ['test.mp4']

    def test_multiple_files(self):
        """Test parsing multiple file arguments."""
        with patch('sys.argv', ['mediautil', 'file1.mp4', 'file2.mkv']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.files == ['file1.mp4', 'file2.mkv']

    def test_list_option(self):
        """Test --list option."""
        with patch('sys.argv', ['mediautil', '--list', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.list_streams is True
            assert args.files == ['test.mp4']

    def test_verbose_option(self):
        """Test -v/--verbose option."""
        with patch('sys.argv', ['mediautil', '-v', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.verbose is True

    def test_debug_option_sets_verbose(self):
        """Test that --debug also sets verbose."""
        with patch('sys.argv', ['mediautil', '--debug', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.debug is True
            assert args.verbose is True

    def test_dry_run_option(self):
        """Test --dry-run option."""
        with patch('sys.argv', ['mediautil', '--dry-run', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.dry_run is True
            assert args.confirm is False

    def test_no_confirm_option(self):
        """Test --no-confirm option."""
        with patch('sys.argv', ['mediautil', '--no-confirm', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.confirm is False

    def test_extract_subs_option(self):
        """Test --extract-subs option."""
        with patch('sys.argv', ['mediautil', '--extract-subs', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.extract_subtitle_streams is True

    def test_delete_subs_option(self):
        """Test --delete-subs option."""
        with patch('sys.argv', ['mediautil', '--delete-subs', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.delete_subtitle_streams is True

    def test_extract_and_delete_subs_sets_both(self):
        """Test that -eds sets both extract and delete."""
        with patch('sys.argv', ['mediautil', '-eds', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.extract_subtitle_streams is True
            assert args.delete_subtitle_streams is True

    def test_delete_stream_single(self):
        """Test --delete-stream with single index."""
        with patch('sys.argv', ['mediautil', '--delete-stream', '1', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.delete_streams == [1]

    def test_delete_stream_multiple(self):
        """Test --delete-stream with multiple indexes."""
        with patch('sys.argv', ['mediautil', '--delete-stream', '0,2,3', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.delete_streams == [0, 2, 3]

    def test_set_stream_language(self):
        """Test --set-stream-language option."""
        with patch('sys.argv', ['mediautil', '--set-stream-language', '0', 'eng', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.set_stream_language == (0, 'eng')

    def test_output_container(self):
        """Test --output-container option."""
        with patch('sys.argv', ['mediautil', '--output-container', 'mkv', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.output_container == 'mkv'

    def test_create_dir_option(self):
        """Test -d/--create-dir option."""
        with patch('sys.argv', ['mediautil', '-d', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.create_dir is True

    def test_convert_stream(self):
        """Test --convert-stream option."""
        with patch('sys.argv', ['mediautil', '--convert-stream', '0', 'libx264', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.convert_stream == (0, 'libx264')

    def test_hardware_acceleration_enabled(self):
        """Test --hwaccel option."""
        with patch('sys.argv', ['mediautil', '--hwaccel', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.hardware_acceleration_enabled is True

    def test_multi_threaded(self):
        """Test --multi-threaded option."""
        with patch('sys.argv', ['mediautil', '--multi-threaded', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.multi_threaded is True

    def test_custom_args(self):
        """Test --custom-args option."""
        with patch('sys.argv', ['mediautil', '--custom-args', '-b:v 2M -preset fast', 'test.mp4']), \
             patch('mediautil.cli.is_valid_file', mock_is_valid_file):
            args = parse_args()
            assert args.custom_ffmpeg_args == ['-b:v', '2M', '-preset', 'fast']


class TestCommandArguments:
    """Test CommandArguments dataclass."""

    def test_default_values(self):
        """Test default values of CommandArguments."""
        args = CommandArguments(
            verbose=False,
            debug=False,
            confirm=True,
            dry_run=False,
            cleanup=True,
            create_dir=False,
            list_streams=False,
            files=[],
            output_container=None,
            extract_streams=None,
            delete_streams=None,
            set_stream_language=None,
            set_title=None,
            convert_stream=None,
            delete_audio_streams_except=None,
            delete_data_streams=False,
            delete_image_streams=False,
            delete_subtitle_streams=False,
            extract_subtitle_streams=False,
            hardware_acceleration_enabled=False,
            multi_threaded=False,
            custom_ffmpeg_args=None,
        )
        assert args.verbose is False
        assert args.debug is False
        assert args.confirm is True
        assert args.dry_run is False
        assert args.hardware_acceleration_enabled is False
        assert args.multi_threaded is False
