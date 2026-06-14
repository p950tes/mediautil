"""Tests for data models."""

import pytest
from mediautil.models import Stream, MediaFile, CommandExecutionResult


class TestCommandExecutionResult:
    """Test CommandExecutionResult dataclass."""

    def test_is_success(self):
        """Test successful execution."""
        result = CommandExecutionResult(args=["test"], returncode=0)
        assert result.is_success()
        assert not result.is_failed()

    def test_is_failed(self):
        """Test failed execution."""
        result = CommandExecutionResult(args=["test"], returncode=1)
        assert result.is_failed()
        assert not result.is_success()

    def test_get_command_as_string(self):
        """Test command string conversion."""
        result = CommandExecutionResult(args=["ffmpeg", "-i", "input.mp4"])
        assert result.get_command_as_string() == "ffmpeg -i input.mp4"


class TestStream:
    """Test Stream class."""

    def test_video_stream(self):
        """Test video stream identification."""
        raw = {"codec_type": "video", "codec_name": "h264", "index": 0}
        stream = Stream(raw)
        assert stream.is_video()
        assert not stream.is_audio()
        assert not stream.is_subtitle()

    def test_audio_stream(self):
        """Test audio stream identification."""
        raw = {"codec_type": "audio", "codec_name": "aac", "index": 1}
        stream = Stream(raw)
        assert stream.is_audio()
        assert not stream.is_video()

    def test_subtitle_stream(self):
        """Test subtitle stream identification."""
        raw = {"codec_type": "subtitle", "codec_name": "srt", "index": 2}
        stream = Stream(raw)
        assert stream.is_subtitle()
        assert not stream.is_video()

    def test_stream_with_tags(self):
        """Test stream with tags."""
        raw = {
            "codec_type": "audio",
            "codec_name": "aac",
            "index": 1,
            "tags": {"language": "eng", "title": "English"}
        }
        stream = Stream(raw)
        assert stream.language == "eng"
        assert stream.title == "English"

    def test_stream_is_default(self):
        """Test default stream detection."""
        raw = {
            "codec_type": "video",
            "codec_name": "h264",
            "index": 0,
            "disposition": {"default": "1"}
        }
        stream = Stream(raw)
        assert stream.is_default()

    def test_stream_is_forced(self):
        """Test forced stream detection."""
        raw = {
            "codec_type": "subtitle",
            "codec_name": "srt",
            "index": 0,
            "disposition": {"forced": "1"}
        }
        stream = Stream(raw)
        assert stream.is_forced()

    def test_stream_is_hearing_impaired(self):
        """Test hearing impaired stream detection."""
        raw = {
            "codec_type": "subtitle",
            "codec_name": "srt",
            "index": 0,
            "disposition": {"hearing_impaired": "1"}
        }
        stream = Stream(raw)
        assert stream.is_hearing_impaired()

    def test_image_based_subtitle(self):
        """Test image-based subtitle detection."""
        for codec in ['dvd_subtitle', 'dvb_subtitle', 'pgs_subtitle', 'hdmv_pgs_subtitle']:
            raw = {"codec_type": "subtitle", "codec_name": codec, "index": 0}
            stream = Stream(raw)
            assert stream.is_image_based_subtitle()

    def test_digest_frame_with_closed_captions(self):
        """Test frame digestion for closed captions."""
        raw = {"codec_type": "video", "codec_name": "h264", "index": 0}
        stream = Stream(raw)
        
        frame = {
            "stream_index": 0,
            "side_data_list": [
                {"side_data_type": "Closed Captions (EIA-608)"}
            ]
        }
        stream.digest_frame(frame)
        assert stream.has_embedded_subtitles()
        assert stream.closed_captions_type == "Closed Captions (EIA-608)"


class TestMediaFile:
    """Test MediaFile class."""

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
