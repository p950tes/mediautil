"""Data models for mediautil."""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class CommandArguments:
    verbose: bool
    debug: bool
    confirm: bool
    dry_run: bool

    cleanup: bool
    create_dir: bool
    
    list_streams: bool

    files: list[str]
    output_container: str|None
    extract_streams: list[int]|None
    delete_streams: list[int]|None
    set_stream_language: tuple[int, str]|None
    delete_audio_streams_except: int|None
    
    delete_data_streams: bool
    delete_image_streams: bool
    delete_subtitle_streams: bool
    extract_subtitle_streams: bool

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


class MediaFile:
    """Represents a media file with its streams."""

    path: str
    container: str
    format: dict
    streams: list[Stream]

    def __init__(self, path: str, format: dict, streams: list[Stream]):
        """Initialize a MediaFile with path, format info, and streams."""
        self.path = path
        self.format = format
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

    def __str__(self) -> str:
        """String representation of the media file."""
        video_streams = self.get_video_streams()
        audio_streams = self.get_audio_streams()
        subtitle_streams = self.get_subtitle_streams()
        other_streams = self.get_other_streams()
        result = list()
        if video_streams:
            result.append("Video streams: \n" + '\n'.join(['   ' + str(s) for s in video_streams]))
        if audio_streams:
            result.append("Audio streams: \n" + '\n'.join(['   ' + str(s) for s in audio_streams]))
        if subtitle_streams:
            result.append("Subtitle streams: \n" + '\n'.join(['   ' + str(s) for s in subtitle_streams]))
        if other_streams:
            result.append("Other streams: \n" + '\n'.join(['   ' + str(s) for s in other_streams]))

        return '\n'.join(result)

def format_bytes(size: int, decimal_places: int = 2) -> str:
    """Format bytes into a human-readable string."""
    modified_size = size
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if modified_size < 1024.0 or unit == 'TiB':
            return f"{modified_size:.{decimal_places}f} {unit}"
        modified_size /= 1024.0
    return f"{modified_size:.{decimal_places}f} TiB"
