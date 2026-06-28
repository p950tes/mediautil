"""Mediautil - A multi-purpose media editing tool."""

from .models import CommandArguments
from .mediaparser import Stream, MediaFile, MediaParser
from .utils import format_bytes, format_bitrate, format_seconds
from .cmdexecutor import CommandExecutionResult, CommandExecutor
from .ffmpeg import FfmpegExecutor, execute_ffprobe, FFMPEG_ANALYZEDURATION, FFMPEG_PROBESIZE
from .environment import (
    GlobalSettings,
    print_error,
    fatal,
    is_verbose,
    verbose,
    is_debug,
    debug,
)
from .actions import (
    process_file,
    extract_subtitles,
    cleanup,
    confirm,
    resolve_new_subtitle_file_path,
)

__version__ = "1.0.0"
