"""Command-line interface for mediautil."""

import signal
import sys

from .parsers import parse_args
from .actions import process_file
from .utils import debug, get_args

# Set up signal handling
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(1))


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    # Debug output
    debug('Arguments:\n  ' + '\n  '.join(f'{k}={v}' for k, v in vars(args).items() if v is not None) + "\n")

    if len(args.files) > 1:
        print("Input files:")
        print('  ' + '\n  '.join(args.files))

    for file in args.files:
        process_file(file)
        if len(args.files) > 1:
            print("---")


if __name__ == '__main__':
    main()
