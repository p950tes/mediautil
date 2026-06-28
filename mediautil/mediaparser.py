import json
from pathlib import Path
from typing import Any

from .ffmpeg import execute_ffprobe
from .environment import *
from .utils import format_bytes, format_seconds, format_bitrate

class Stream:
    """Represents a media stream (video, audio, subtitle)."""

    type: str
    codec_name: str
    index: int
    raw: dict
    tags: dict
    language: str | None
    title: str | None
    filename: str | None
    mimetype: str | None
    bitrate: str | None
    frames: list[dict]
    closed_captions_type: str | None

    def __init__(self, raw: dict):
        """Initialize a Stream from raw ffprobe data."""
        self.type = raw.get("codec_type", "")
        self.codec_name = raw.get("codec_name", "")
        self.index = raw["index"]
        self.raw = raw
        self.frames = []
        self.language = None
        self.title = None
        self.filename = None
        self.mimetype = None
        self.bitrate = None
        self.closed_captions_type = None
        if 'tags' in raw:
            self.__parse_tags(raw['tags'])

    def __has_disposition(self, disposition: str) -> bool:
        """Check if stream has a specific disposition."""
        if 'disposition' not in self.raw or disposition not in self.raw['disposition']:
            return False
        value = int(self.raw['disposition'][disposition])
        return value > 0

    def __parse_tags(self, tags: dict) -> None:
        """Parse tags from ffprobe data."""
        self.tags = tags
        if 'language' in tags:
            self.language = tags['language']
        if 'title' in tags:
            self.title = tags['title']
        if 'filename' in tags:
            self.filename = tags['filename']
        if 'mimetype' in tags:
            self.mimetype = tags['mimetype']

    def digest_frame(self, frame: dict) -> None:
        """Process frame data to extract additional information."""
        self.frames.append(frame)
        if not 'side_data_list' in frame:
            return
        side_data_list = frame['side_data_list']
        for side_data in side_data_list:
            if not 'side_data_type' in side_data:
                continue
            side_data_type = side_data['side_data_type']
            if 'Closed Captions' in side_data_type or side_data_type == 'CC':
                self.closed_captions_type = side_data_type

    def get_size_in_bytes(self) -> int | None:
        """Get the size of the stream in bytes from tags."""
        if 'tags' not in self.raw:
            return None
        tags = self.raw['tags']
        numbytes_tags = [tag for tag in tags if tag.startswith('NUMBER_OF_BYTES')]
        if len(numbytes_tags) > 0:
            return int(tags.get(numbytes_tags[0]))
        else:
            return None

    def is_video(self) -> bool:
        """Check if this is a video stream."""
        return self.type == 'video'

    def is_audio(self) -> bool:
        """Check if this is an audio stream."""
        return self.type == 'audio'

    def is_subtitle(self) -> bool:
        """Check if this is a subtitle stream."""
        return self.type == 'subtitle'

    def is_unknown_type(self) -> bool:
        """Check if this is an unknown stream type."""
        return self.type not in ['video', 'audio', 'subtitle']

    def is_image(self) -> bool:
        """Check if this is an image-based stream."""
        return self.codec_name in ['mjpeg', 'png']

    def is_default(self) -> bool:
        """Check if this is the default stream."""
        return self.__has_disposition('default')

    def is_forced(self) -> bool:
        """Check if this stream is forced."""
        if self.__has_disposition('forced'):
            return True
        if self.title and "FORCED" in self.title.upper():
            return True
        return False

    def is_hearing_impaired(self) -> bool:
        """Check if this stream is for hearing impaired."""
        if self.__has_disposition('hearing_impaired'):
            return True
        if self.title and "SDH" in self.title.upper():
            return True
        return False

    def is_image_based_subtitle(self) -> bool:
        """Check if this is an image-based subtitle."""
        return self.is_subtitle() and self.raw.get('codec_name') in [
            'dvd_subtitle', 'dvb_subtitle', 'pgs_subtitle', 'hdmv_pgs_subtitle'
        ]

    def has_embedded_subtitles(self) -> bool:
        """Check if this stream has embedded subtitles."""
        return self.closed_captions_type is not None

    def print_details(self, prefix: str = "") -> None:
        print(f"{prefix}{self}")

    def __str__(self) -> str:
        """String representation of the stream."""
        result = list()
        result.append(f"Stream #{self.index}")
        result.append(self.type)
        if self.language and (self.is_audio() or self.is_subtitle()):
            result.append(f"({self.language})")

        if self.codec_name:
            result.append(self.codec_name)

        if self.raw.get('profile'):
            result.append(f"({self.raw.get('profile')})")

        if 'width' in self.raw:
            result.append(f"{self.raw.get('width')}x{self.raw.get('height')}")

        if self.bitrate:
            result.append(f"({self.bitrate})")

        if self.raw.get('channel_layout'):
            result.append(f"{self.raw.get('channel_layout')}")

        num_bytes = self.get_size_in_bytes()
        if num_bytes:
            result.append(format_bytes(num_bytes))

        if self.title:
            result.append(f"'{self.title}'")
        if self.filename:
            result.append(f"'{self.filename}'")
        if self.mimetype:
            result.append(f"({self.mimetype})")

        if self.is_default():
            result.append("(default)")
        if self.is_forced():
            result.append("(forced)")
        if self.is_hearing_impaired():
            result.append("(hi)")
        if self.closed_captions_type:
            result.append(f"(Embedded subtitle bitstream: {self.closed_captions_type})")

        return ' '.join(result)

@dataclass
class MediaFile:
    """Represents a media file with its streams."""

    path: str
    container: str
    streams: list[Stream]
    metadata: dict[str, Any]
    title: str|None
    comment: str|None
    encoder: str|None
    duration: str|None
    format: str|None
    creation_time: str|None
    size: int|None

    def __init__(self, path: str, streams: list[Stream]):
        """Initialize a MediaFile with path, format info, and streams."""
        self.path = path
        self.container = Path(path).suffix[1:]
        self.streams = streams

    def get_video_streams(self) -> list[Stream]:
        """Get all video streams."""
        return [stream for stream in self.streams if stream.is_video()]

    def get_audio_streams(self) -> list[Stream]:
        """Get all audio streams."""
        return [stream for stream in self.streams if stream.is_audio()]

    def get_subtitle_streams(self) -> list[Stream]:
        """Get all subtitle streams."""
        return [stream for stream in self.streams if stream.is_subtitle()]

    def get_other_streams(self) -> list[Stream]:
        """Get all other (non-video, non-audio, non-subtitle) streams."""
        return [stream for stream in self.streams if stream.is_unknown_type()]

    def print_details(self) -> None:
        prefix = "   "
        print("Metadata:")
        if self.title:         print(  f"{prefix}Title:    {self.title}")
        if self.duration:      print(  f"{prefix}Duration: {self.duration}")
        if self.format:        print(  f"{prefix}Format:   {self.format}")
        if self.size:          print(  f"{prefix}Size:     {format_bytes(self.size)}")
        if self.comment:       verbose(f"{prefix}Comment:  {self.comment}")
        
        video_streams = self.get_video_streams()
        audio_streams = self.get_audio_streams()
        subtitle_streams = self.get_subtitle_streams()
        other_streams = self.get_other_streams()

        if video_streams:
            print("Video streams:")
            for stream in video_streams:
                stream.print_details(prefix)
        if audio_streams:
            print("Audio streams:")
            for stream in audio_streams:
                stream.print_details(prefix)
        if subtitle_streams:
            print("Subtitle streams:")
            for stream in subtitle_streams:
                stream.print_details(prefix)
        if other_streams:
            print("Other streams:")
            for stream in other_streams:
                stream.print_details(prefix)
    
class MediaParser:

    def parse(self, filepath: str) -> MediaFile:
        """Parse a media file using ffprobe and return a MediaFile object."""
        ffprobe_result = execute_ffprobe(filepath)

        if ffprobe_result.returncode != 0:
            print_error(ffprobe_result.stderr)
            fatal(f"Failed to parse file info from {filepath}")

        ffprobe = json.loads(ffprobe_result.stdout)

        streams = [self.parse_stream(stream_metadata) for stream_metadata in ffprobe['streams']]

        if 'frames' in ffprobe:
            for frame in ffprobe['frames']:
                if not 'stream_index' in frame:
                    continue
                for stream in streams:
                    if stream.index == frame['stream_index']:
                        stream.digest_frame(frame)

        # Validate indexes
        for i in range(len(streams)):
            if i != streams[i].index:
                fatal(f"The array index {i} does not match the stream index {streams[i].index}")

        mediafile = MediaFile(filepath, streams)

        metadata = ffprobe.get("format", {})
        mediafile.metadata = metadata
        mediafile.duration = format_seconds(metadata.get("duration", None))
        mediafile.format = metadata.get("format_long_name", None) or metadata.get("format_name", None)
        if "size" in metadata:
            mediafile.size = int(metadata['size'])
        
        tags = metadata.get("tags", {})
        mediafile.title = tags.get("title", None)
        mediafile.encoder = tags.get("encoder", None)
        mediafile.creation_time = tags.get("creation_time", None)
        mediafile.comment = tags.get("comment", None)

        return mediafile

    def parse_stream(self, metadata: dict[str, Any]) -> Stream:
        stream = Stream(metadata)

        bitrate = self._resolve_stream_bitrate(metadata)
        if bitrate:
            stream.bitrate = format_bitrate(bitrate)

        return stream
    
    def _resolve_stream_bitrate(self, stream: dict[str, Any]) -> int|None:
        try:
            if "bit_rate" in stream and stream["bit_rate"]:
                return int(stream["bit_rate"])
            
            tags = stream.get("tags", {})
            if "BPS" in tags:
                return int(tags["BPS"])
            
            for key, value in tags.items():
                if key.startswith("BPS"):
                    return int(value)
            return None
        except Exception as e:
            print_error(f"Failed to resolve bitrate: {e}")
            return None
