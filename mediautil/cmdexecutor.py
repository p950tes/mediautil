"""Command executors for mediautil."""

import io
import subprocess
import sys
import threading
from dataclasses import dataclass
from typing import IO

from .environment import *

@dataclass
class CommandExecutionResult:
    """Result of a command execution."""
    
    args: list[str]
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None

    def get_command_as_string(self) -> str:
        """Get the command as a space-separated string."""
        return ' '.join(self.args)

    def is_success(self) -> bool:
        """Check if the command executed successfully."""
        return self.returncode == 0

    def is_failed(self) -> bool:
        """Check if the command failed."""
        return not self.is_success()

class CommandExecutor:
    """Executes shell commands and captures output."""

    print_output: bool

    def __init__(self, print_output: bool = False) -> None:
        """Initialize the executor."""
        if is_debug():
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
            print_error(f"Failed to process output stream: {e}")
        finally:
            output_stream.close()
