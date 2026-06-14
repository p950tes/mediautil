"""Utility functions for mediautil."""

import argparse
import sys
from pathlib import Path

# Global ARGS will be set by CLI
ARGS = None

def set_args(args: argparse.Namespace) -> None:
    """Set the global ARGS variable."""
    global ARGS
    ARGS = args


def get_args() -> argparse.Namespace:
    """Get the global ARGS variable."""
    return ARGS


def print_error(*args, **kwargs) -> None:
    """Print an error message to stderr."""
    print("ERROR:", *args, file=sys.stderr, **kwargs)


def fatal(*args, **kwargs) -> None:
    """Print an error message and exit."""
    print_error(*args, **kwargs)
    exit(1)


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return ARGS.verbose if ARGS else False


def verbose(*args, **kwargs) -> None:
    """Print a message if verbose mode is enabled."""
    if is_verbose():
        print(*args, file=sys.stderr, **kwargs)


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return ARGS.debug if ARGS else False


def debug(*args, **kwargs) -> None:
    """Print a debug message if debug mode is enabled."""
    if is_debug():
        print(*args, file=sys.stderr, **kwargs)


def confirm() -> None:
    """Prompt for confirmation if confirm mode is enabled."""
    print()
    if ARGS and ARGS.confirm:
        input('Press ENTER to continue or CTRL-C to abort\n')


def format_bytes(size: int, decimal_places: int = 2) -> str:
    """Format bytes into a human-readable string."""
    modified_size = size
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if modified_size < 1024.0 or unit == 'TiB':
            return f"{modified_size:.{decimal_places}f} {unit}"
        modified_size /= 1024.0
    return f"{modified_size:.{decimal_places}f} TiB"
