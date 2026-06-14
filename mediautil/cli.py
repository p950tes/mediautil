"""Command-line interface for mediautil."""

import argparse
from pathlib import Path
import signal
import sys

from .actions import process_file
from .logging import *
from .utils import set_args

# Set up signal handling
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(1))


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    LoggingOptions.VERBOSE = args.verbose
    LoggingOptions.DEBUG = args.debug

    # Debug output
    debug('Arguments:\n  ' + '\n  '.join(f'{k}={v}' for k, v in vars(args).items() if v is not None) + "\n")

    if len(args.files) > 1:
        print("Input files:")
        print('  ' + '\n  '.join(args.files))

    for file in args.files:
        process_file(file)
        if len(args.files) > 1:
            print("---")

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

def is_valid_file(parser: argparse.ArgumentParser, arg: str) -> str:
    """Validate that a file exists."""
    if Path(arg).is_file():
        return arg
    parser.error(f"The file {arg} does not exist!")

if __name__ == '__main__':
    main()
