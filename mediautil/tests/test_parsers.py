"""Tests for parsing functions."""

import pytest
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock
from mediautil.parsers import parse_args
from mediautil.utils import set_args


class TestParseArgs:
    """Test argument parsing."""

    def test_list_option(self):
        """Test --list option."""
        with patch('sys.argv', ['mediautil', '--list', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.list is True
                assert args.files == ['test.mp4']

    def test_verbose_option(self):
        """Test -v/--verbose option."""
        with patch('sys.argv', ['mediautil', '-v', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.verbose is True

    def test_debug_option_sets_verbose(self):
        """Test that --debug also sets verbose."""
        with patch('sys.argv', ['mediautil', '--debug', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.debug is True
                assert args.verbose is True

    def test_dry_run_disables_confirm(self):
        """Test that --dry-run disables confirmation."""
        with patch('sys.argv', ['mediautil', '--dry-run', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.dry_run is True
                assert args.confirm is False

    def test_extract_and_delete_subs_sets_both(self):
        """Test that -eds sets both extract and delete."""
        with patch('sys.argv', ['mediautil', '-eds', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.extract_subs is True
                assert args.delete_subs is True

    def test_multiple_stream_indexes(self):
        """Test parsing multiple stream indexes."""
        with patch('sys.argv', ['mediautil', '--delete-stream', '0,2,3', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.delete_stream == [0, 2, 3]

    def test_single_stream_index(self):
        """Test parsing single stream index."""
        with patch('sys.argv', ['mediautil', '--delete-stream', '1', 'test.mp4']):
            with patch('mediautil.utils.Path') as mock_path:
                mock_path.return_value.is_file.return_value = True
                args = parse_args()
                assert args.delete_stream == [1]
