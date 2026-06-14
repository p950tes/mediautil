"""Parsing functions for mediautil."""

import argparse
import json

from .models import MediaFile, Stream
from .executors import CommandExecutor
from .constants import FFMPEG_ANALYZEDURATION, FFMPEG_PROBESIZE
from .utils import print_error, fatal, is_valid_file, set_args, get_args


def parse_mediafile(filepath: str) -> MediaFile:
    """Parse a media file using ffprobe and return a MediaFile object."""
    ffprobe_result = CommandExecutor().execute([
        'ffprobe', '-hide_banner', '-of', 'json',
        '-analyzeduration', FFMPEG_ANALYZEDURATION,
        '-probesize', FFMPEG_PROBESIZE,
        '-show_streams', '-show_format',
        # Display frame details but from the first frame only
        '-show_frames', '-read_intervals', '%+#1',
        filepath
    ])

    if ffprobe_result.returncode != 0:
        print_error(ffprobe_result.stderr)
        fatal(f"Failed to parse file info from {filepath}")

    ffprobe = json.loads(ffprobe_result.stdout)

    streams = [Stream(stream_metadata) for stream_metadata in ffprobe['streams']]

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

    return MediaFile(filepath, ffprobe['format'], streams)

