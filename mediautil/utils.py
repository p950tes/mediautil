
from typing import Union

from .environment import print_error

def format_bytes(bytes: int) -> str:
    """Format bytes into a human-readable string."""
    modified_size = bytes
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    last_unit = units[-1]
    for unit in units:
        if modified_size < 1024.0 or unit == last_unit:
            return f"{modified_size:.{__resolve_num_decimals(unit)}f} {unit}"
        modified_size /= 1024.0
    unit = last_unit
    return f"{modified_size:.{__resolve_num_decimals(unit)}f} {last_unit}"

def format_bitrate(bits_per_second: int) -> str:
    """Format bytes into a human-readable string."""
    modified_size = bits_per_second
    units = ['b/s', 'kb/s', 'Mb/s']
    last_unit = units[-1]
    for unit in units:
        if modified_size < 1000.0 or unit == last_unit:
            return f"{modified_size:.{__resolve_num_decimals(unit)}f} {unit}"
        modified_size /= 1000.0
    unit = last_unit
    return f"{modified_size:.{__resolve_num_decimals(unit)}f} {unit}"

def __resolve_num_decimals(unit: str) -> int:
    major_unit = unit[0].upper()

    if major_unit == "B":
        return 0
    if major_unit == "K":
        return 1
    else:
        return 2

def format_seconds(seconds: Union[float, str, None]) -> str|None:
    """Convert seconds (float or string) to a formatted HH:MM:SS.mmm string."""
    if seconds is None:
        return None
    if seconds == "" or seconds is False:
        return str(seconds)
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        remaining = seconds % 3600
        minutes = int(remaining // 60)
        secs = int(remaining % 60)
        milliseconds = int(round((remaining % 60 - secs) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    except (ValueError, TypeError):
        print_error(f"Failed to parse duration: '{seconds}'")
        return str(seconds)
