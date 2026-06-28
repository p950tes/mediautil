"""Command-line interface for mediautil."""

import argparse
from pathlib import Path
import signal
import sys

from .actions import process_file
from .environment import *
from .models import CommandArguments

# Set up signal handling
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(1))


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    GlobalSettings.VERBOSE = args.verbose
    GlobalSettings.DEBUG = args.debug
    GlobalSettings.CONFIRM = args.confirm
    GlobalSettings.DRY_RUN = args.dry_run
    
    if len(args.files) > 1:
        print("Input files:")
        print('  ' + '\n  '.join(args.files))

    for file in args.files:
        process_file(file, args)
        if len(args.files) > 1:
            print("---")


def parse_args() -> CommandArguments:
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

    argparser.add_argument(
        '--set-title', 
        dest='set_title', 
        help='Updates the title metadata attribute')

    argparser.add_argument(
        '--convert-stream',
        nargs=2,
        metavar=('STREAM', 'CODEC'),
        help='Converts the specified stream to the specified codec'
    )
    argparser.add_argument('--output-container', dest='output_container', help='Specify a new output container')
    argparser.add_argument('--delete-stream', metavar='stream', help='Deletes the specified stream')
    argparser.add_argument('--extract-stream', metavar='stream', help='Extracts the specified stream')
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
    argparser.add_argument(
        '--hwaccel',
        dest='hardware_acceleration_enabled',
        help='Enable hardware acceleration',
        action='store_true'
    )
    argparser.add_argument(
        '--multi-threaded',
        dest='multi_threaded',
        help='Enable use of all available CPU cores',
        action='store_true'
    )
    argparser.add_argument(
        '--custom-args',
        dest='custom_args',
        help='Specify custom arguments to ffmpeg. Multiple space-separated arguments possible',
        action='store'
    )

    argparser.add_argument('-d', '--create-dir', action='store_true', help='Store the output in a directory with the same name as the input file')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    argparser.add_argument('--debug', action='store_true', help='Debug mode')
    argparser.add_argument('--dry-run', '--nono', action='store_true', help='Make no changes')
    argparser.add_argument('--no-confirm', dest='confirm', action='store_false', help='Disables confirmation dialog before executing')
    argparser.add_argument('--no-cleanup', dest='cleanup', action='store_false', help='Disables cleanup of old file')

    args = argparser.parse_args()

    debug('Arguments:\n  ' + '\n  '.join(f'{k}={v}' for k, v in vars(args).items() if v is not None) + "\n")

    # Process related options
    if args.extract_and_delete_subs:
        args.extract_subs = True
        args.delete_subs = True

    if args.debug:
        args.verbose = True
    
    if args.dry_run:
        args.confirm = False

    # Parse stream indexes

    delete_streams = None
    if args.delete_stream:
        if "," in args.delete_stream:
            delete_streams = list(map(int, args.delete_stream.split(",")))
        else:
            delete_streams = [int(args.delete_stream)]
    
    extract_streams = None
    if args.extract_stream:
        if "," in args.extract_stream:
            extract_streams = list(map(int, args.extract_stream.split(",")))
        else:
            extract_streams = [int(args.extract_stream)]

    set_stream_language = None
    if args.set_stream_language is not None:
        stream_index = int(args.set_stream_language[0])
        new_language = args.set_stream_language[1]
        set_stream_language = (stream_index, new_language)

    set_title = None
    if args.set_title:
        set_title = args.set_title.strip()

    convert_stream = None
    if args.convert_stream is not None:
        stream_index = int(args.convert_stream[0])
        target_codec = args.convert_stream[1]
        convert_stream = (stream_index, target_codec)

    custom_ffmpeg_args = None
    if args.custom_args:
        custom_ffmpeg_args = args.custom_args.strip().split(" ")

    return CommandArguments(
        files = args.files,
        
        verbose = args.verbose,
        debug = args.debug,
        confirm = args.confirm,
        dry_run = args.dry_run,

        cleanup = args.cleanup,
        create_dir = args.create_dir,

        list_streams = args.list,
        
        output_container = args.output_container,

        set_title = set_title,
        set_stream_language = set_stream_language,
        
        extract_streams = extract_streams,
        extract_subtitle_streams = args.extract_subs,

        delete_streams = delete_streams,
        delete_audio_streams_except = args.delete_audio_streams_except,
        delete_data_streams = args.delete_data_streams,
        delete_image_streams = args.delete_image_streams,
        delete_subtitle_streams = args.delete_subs,

        convert_stream = convert_stream,

        hardware_acceleration_enabled = args.hardware_acceleration_enabled,
        multi_threaded = args.multi_threaded,

        custom_ffmpeg_args = custom_ffmpeg_args,
    )


def is_valid_file(parser: argparse.ArgumentParser, arg: str) -> str:
    """Validate that a file exists."""
    if Path(arg).is_file():
        return arg
    parser.error(f"The file {arg} does not exist!")


if __name__ == '__main__':
    main()
