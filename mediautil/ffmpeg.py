"""Command executors for mediautil."""

from .environment import *
from .cmdexecutor import CommandExecutor, CommandExecutionResult

# Specify how many microseconds are analyzed to probe the input.
# A higher value will enable detecting more accurate information, but will increase latency.
# It defaults to 5,000,000 microseconds = 5 seconds.
FFMPEG_ANALYZEDURATION = str(100_000_000)

# Set probing size in bytes, i.e. the size of the data to analyze to get stream information.
# A higher value will enable detecting more information in case it is dispersed into the stream,
# but will increase latency. Must be an integer not lesser than 32.
# It defaults to 5,000,000 microseconds = 5 seconds.
FFMPEG_PROBESIZE = str(100_000_000)

class FfmpegExecutor:
    """Builder for ffmpeg commands."""

    cmdline_args: list[str]

    def __init__(self, input_file_path: str) -> None:
        """Initialize with input file path."""
        self.cmdline_args = ['ffmpeg']
        if not is_verbose():
            self.cmdline_args.extend(['-loglevel', 'warning'])
        self.cmdline_args.extend(['-nostdin', '-hide_banner'])
        self.cmdline_args.extend(['-analyzeduration', FFMPEG_ANALYZEDURATION])
        self.cmdline_args.extend(['-probesize', FFMPEG_PROBESIZE])
        self.cmdline_args.extend(['-i', input_file_path])

    def add_arg(self, argument: str) -> None:
        """Add a single argument."""
        self.cmdline_args.append(argument)

    def add_args(self, arguments: list[str]) -> None:
        """Add multiple arguments."""
        self.cmdline_args.extend(arguments)

    def execute(self) -> CommandExecutionResult:
        """Execute the ffmpeg command."""
        print(' '.join(self.cmdline_args))
        if GlobalSettings.DRY_RUN:
            print("(dry-run, not actually executing)")
            return CommandExecutionResult([], returncode=0)
        executor = CommandExecutor(print_output=True)
        return executor.execute(self.cmdline_args)

def execute_ffprobe(filepath: str) -> CommandExecutionResult:
    ffprobe_result = CommandExecutor().execute([
        'ffprobe', '-hide_banner', '-of', 'json',
        '-analyzeduration', FFMPEG_ANALYZEDURATION,
        '-probesize', FFMPEG_PROBESIZE,
        '-show_streams', '-show_format',
        # Display frame details but from the first frame only
        '-show_frames', '-read_intervals', '%+#1',
        filepath
    ])
    return ffprobe_result
