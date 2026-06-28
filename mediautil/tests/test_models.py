"""Tests for data models."""

import pytest
from mediautil.models import Stream, MediaFile, CommandArguments, format_bytes


class TestFormatBytes:
    """Test the format_bytes function."""

    def test_zero_bytes(self):
        """Test formatting of zero bytes."""
        assert format_bytes(0) == "0.00 B"

    def test_bytes(self):
        """Test formatting of bytes."""
        assert format_bytes(500) == "500.00 B"
        assert format_bytes(1023) == "1023.00 B"

    def test_kilobytes(self):
        """Test formatting of kilobytes."""
        assert format_bytes(1024) == "1.00 KiB"
        assert format_bytes(1536) == "1.50 KiB"

    def test_megabytes(self):
        """Test formatting of megabytes."""
        assert format_bytes(1024 * 1024) == "1.00 MiB"

    def test_gigabytes(self):
        """Test formatting of gigabytes."""
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GiB"


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
            delete_audio_streams_except=None,
            delete_data_streams=False,
            delete_image_streams=False,
            delete_subtitle_streams=False,
            extract_subtitle_streams=False,
            convert_stream=None,
            hardware_acceleration_enabled=False,
            custom_ffmpeg_args=None
        )
        assert args.verbose is False
        assert args.debug is False
        assert args.confirm is True
        assert args.dry_run is False


class TestStream:
    """Test Stream class."""

    def test_video_stream_creation(self):
        """Test video stream creation and identification."""
        raw = {"codec_type": "video", "codec_name": "h264", "index": 0}
        stream = Stream(raw)
        assert stream.type == "video"
        assert stream.codec_name == "h264"
        assert stream.index == 0
        assert stream.is_video() is True
        assert stream.is_audio() is False
        assert stream.is_subtitle() is False

    def test_audio_stream_creation(self):
        """Test audio stream creation and identification."""
        raw = {"codec_type": "audio", "codec_name": "aac", "index": 1}
        stream = Stream(raw)
        assert stream.type == "audio"
        assert stream.is_audio() is True
        assert stream.is_video() is False

    def test_subtitle_stream_creation(self):
        """Test subtitle stream creation and identification."""
        raw = {"codec_type": "subtitle", "codec_name": "srt", "index": 2}
        stream = Stream(raw)
        assert stream.type == "subtitle"
        assert stream.is_subtitle() is True

    def test_stream_with_tags(self):
        """Test stream with language and title tags."""
        raw = {
            "codec_type": "audio",
            "codec_name": "aac",
            "index": 1,
            "tags": {"language": "eng", "title": "English"}
        }
        stream = Stream(raw)
        assert stream.language == "eng"
        assert stream.title == "English"

    def test_stream_with_disposition(self):
        """Test stream with disposition tags."""
        raw = {
            "codec_type": "video",
            "codec_name": "h264",
            "index": 0,
            "disposition": {"default": "1"}
        }
        stream = Stream(raw)
        assert stream.is_default() is True

    def test_image_based_subtitle(self):
        """Test image-based subtitle detection."""
        for codec in ['dvd_subtitle', 'dvb_subtitle', 'pgs_subtitle']:
            raw = {"codec_type": "subtitle", "codec_name": codec, "index": 0}
            stream = Stream(raw)
            assert stream.is_image_based_subtitle() is True

    def test_stream_str_representation(self):
        """Test stream string representation."""
        raw = {
            "codec_type": "video",
            "codec_name": "h264",
            "index": 0,
            "tags": {"language": "und"}
        }
        stream = Stream(raw)
        str_repr = str(stream)
        assert "Stream #0" in str_repr
        assert "video" in str_repr


class TestMediaFile:
    """Test MediaFile class."""

    def test_media_file_creation(self):
        """Test MediaFile creation."""
        streams = [
            Stream({"codec_type": "video", "codec_name": "h264", "index": 0}),
            Stream({"codec_type": "audio", "codec_name": "aac", "index": 1}),
            Stream({"codec_type": "subtitle", "codec_name": "srt", "index": 2}),
        ]
        media_file = MediaFile(path="/test.mp4", format={"format_name": "mp4"}, streams=streams)
        assert media_file.path == "/test.mp4"
        assert media_file.container == "mp4"
        assert len(media_file.streams) == 3

    def test_get_streams_by_type(self):
        """Test stream filtering by type."""
        streams = [
            Stream({"codec_type": "video", "codec_name": "h264", "index": 0}),
            Stream({"codec_type": "audio", "codec_name": "aac", "index": 1}),
            Stream({"codec_type": "subtitle", "codec_name": "srt", "index": 2}),
            Stream({"codec_type": "data", "codec_name": "unknown", "index": 3}),
        ]
        media_file = MediaFile(path="/test.mp4", format={}, streams=streams)
        
        assert len(media_file.get_video_streams()) == 1
        assert len(media_file.get_audio_streams()) == 1
        assert len(media_file.get_subtitle_streams()) == 1
        assert len(media_file.get_other_streams()) == 1

    def test_container_from_path(self):
        """Test container extraction from path."""
        media_file = MediaFile(path="/test.mp4", format={}, streams=[])
        assert media_file.container == "mp4"
        
        media_file = MediaFile(path="/test.mkv", format={}, streams=[])
        assert media_file.container == "mkv"
