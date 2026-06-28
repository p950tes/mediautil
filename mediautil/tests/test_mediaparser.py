"""Tests for media parser module."""

import pytest
from mediautil.mediaparser import Stream, MediaFile, MediaParser


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
        media_file = MediaFile(path="/test.mp4", streams=streams)
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
        media_file = MediaFile(path="/test.mp4", streams=streams)
        
        assert len(media_file.get_video_streams()) == 1
        assert len(media_file.get_audio_streams()) == 1
        assert len(media_file.get_subtitle_streams()) == 1
        assert len(media_file.get_other_streams()) == 1

    def test_container_from_path(self):
        """Test container extraction from path."""
        media_file = MediaFile(path="/test.mp4", streams=[])
        assert media_file.container == "mp4"
        
        media_file = MediaFile(path="/test.mkv", streams=[])
        assert media_file.container == "mkv"
