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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    argparser = argparse.ArgumentParser(prog='Mediautil', description='Multi-purpose media editing tool')

    argparser.add_argument(
        'files',
        metavar='FILE',
        type=lambda x: is_valid_file(argparser, x),
        nargs='+',
        help='Input file'
    )

    argparser.add_argument('--list', action='store_true', help='Prints information about the specified file')
    argparser.add_argument(
        '--set-stream-language',
        nargs=2,
        metavar=('STREAM', 'LANGUAGE'),
        help='Sets stream language to the specified language'
    )
    argparser.add_argument('--output-container', dest='output_container', help='Specify a new output container')
    argparser.add_argument('--delete-stream', metavar='stream', help='Deletes the specified stream')
    argparser.add_argument('--extract-stream', metavar='stream', help='Deletes the specified stream')
    argparser.add_argument(
        '--delete-audio-streams-except',
        metavar='stream',
        help='Deletes all audio streams except the one specified',
        type=int
    )
    argparser.add_argument(
        '--delete-data-streams',
        help='Deletes all data streams',
        action='store_true'
    )
    argparser.add_argument(
        '--delete-image-streams',
        help='Deletes all image streams',
        action='store_true'
    )
    argparser.add_argument(
        '--delete-subs',
        dest='delete_subs',
        help='Deletes all subtitle streams',
        action='store_true'
    )
    argparser.add_argument(
        '--extract-subs',
        dest='extract_subs',
        help='Extract all subtitle streams',
        action='store_true'
    )
    argparser.add_argument(
        '-eds', '--extract-and-delete-subs',
        dest='extract_and_delete_subs',
        help='Extract and delete all subtitle streams',
        action='store_true'
    )

    argparser.add_argument('-d', '--create-dir', action='store_true', help='Store the output in a directory with the same name as the input file')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    argparser.add_argument('--debug', action='store_true', help='Debug mode')
    argparser.add_argument('--dry-run', '--nono', action='store_true', help='Make no changes')
    argparser.add_argument('--no-confirm', dest='confirm', action='store_false', help='Disables confirmation dialog before executing')
    argparser.add_argument('--no-cleanup', dest='cleanup', action='store_false', help='Disables cleanup of old file')

    args = argparser.parse_args()

    # Process related options
    if args.extract_and_delete_subs:
        args.extract_subs = True
        args.delete_subs = True

    if args.dry_run:
        args.confirm = False
    if args.debug:
        args.verbose = True

    # Parse stream indexes
    if args.delete_stream:
        if "," in args.delete_stream:
            args.delete_stream = list(map(int, args.delete_stream.split(",")))
        else:
            args.delete_stream = [int(args.delete_stream)]
    if args.extract_stream:
        if "," in args.extract_stream:
            args.extract_stream = list(map(int, args.extract_stream.split(",")))
        else:
            args.extract_stream = [int(args.extract_stream)]

    # Set global ARGS
    set_args(args)

    return args
