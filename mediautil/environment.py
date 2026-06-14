"""Logger for mediautil."""

import sys

from dataclasses import dataclass

@dataclass
class GlobalSettings:
    VERBOSE: bool = False
    DEBUG: bool = False
    CONFIRM: bool = True
    DRY_RUN: bool = False

def print_error(*args, **kwargs) -> None:
    """Print an error message to stderr."""
    print("ERROR:", *args, file=sys.stderr, **kwargs)

def fatal(*args, **kwargs) -> None:
    """Print an error message and exit."""
    print_error(*args, **kwargs)
    sys.exit(1)

def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return GlobalSettings.VERBOSE

def verbose(*args, **kwargs) -> None:
    """Print a message if verbose mode is enabled."""
    if is_verbose():
        print(*args, file=sys.stderr, **kwargs)

def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return GlobalSettings.DEBUG

def debug(*args, **kwargs) -> None:
    """Print a debug message if debug mode is enabled."""
    if is_debug():
        print(*args, file=sys.stderr, **kwargs)
