"""Command executors for mediautil."""

import io
import subprocess
import sys
import threading
from typing import IO

from .models import CommandExecutionResult
from .utils import debug, is_debug, verbose, get_args
from .constants import FFMPEG_ANALYZEDURATION, FFMPEG_PROBESIZE


class CommandExecutor:
    """Executes shell commands and captures output."""

    print_output: bool

    def __init__(self, print_output: bool = False) -> None:
        """Initialize the executor."""
        args = get_args()
        if args and is_debug():
            print_output = True
        self.print_output = print_output

    def execute(self, args: list[str]) -> CommandExecutionResult:
        """Execute a command and return the result."""
        verbose(' '.join(args))
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            encoding='utf-8',
            errors='replace',
            text=True
        )

        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        stdout_reader = threading.Thread(
            target=self.__process_output_stream,
            args=(process.stdout, stdout_buffer, sys.stdout),
            daemon=True
        )
        stderr_reader = threading.Thread(
            target=self.__process_output_stream,
            args=(process.stderr, stderr_buffer, sys.stderr),
            daemon=True
        )
        stdout_reader.start()
        stderr_reader.start()
        try:
            process.wait()
        finally:
            stdout_reader.join(timeout=1.0)
            stderr_reader.join(timeout=1.0)

        verbose(f"Return code: {process.returncode}")

        return CommandExecutionResult(
            args=args,
            stdout=stdout_buffer.getvalue(),
            stderr=stderr_buffer.getvalue(),
            returncode=process.returncode
        )

    def __process_output_stream(
        self, output_stream: IO[str], output_buffer: io.StringIO, print_stream: IO[str]
    ) -> None:
        """Process an output stream, optionally printing to console."""
        try:
            for line in iter(output_stream.readline, ''):
                if self.print_output:
                    print_stream.write(line)
                    print_stream.flush()
                output_buffer.write(line)
                output_buffer.flush()
        except Exception as e:
            from .utils import print_error
            print_error(f"Failed to process output stream: {e}")
        finally:
            output_stream.close()


class FfmpegExecutor:
    """Builder for ffmpeg commands."""

    args: list[str]

    def __init__(self, input_file_path: str) -> None:
        """Initialize with input file path."""
        self.args = ['ffmpeg']
        args = get_args()
        if args and not args.verbose:
            self.args.extend(['-loglevel', 'warning'])
        self.args.extend(['-nostdin', '-hide_banner'])
        self.args.extend(['-analyzeduration', FFMPEG_ANALYZEDURATION])
        self.args.extend(['-probesize', FFMPEG_PROBESIZE])
        self.args.extend(['-i', input_file_path])

    def add_arg(self, argument: str) -> None:
        """Add a single argument."""
        self.args.append(argument)

    def add_args(self, arguments: list[str]) -> None:
        """Add multiple arguments."""
        self.args.extend(arguments)

    def execute(self) -> CommandExecutionResult:
        """Execute the ffmpeg command."""
        print(' '.join(self.args))
        args = get_args()
        if args and args.dry_run:
            print("(dry-run, not actually executing)")
            return CommandExecutionResult([], returncode=0)
        executor = CommandExecutor(print_output=True)
        return executor.execute(self.args)
