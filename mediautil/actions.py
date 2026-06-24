"""Action functions for mediautil."""

import json
import os
from pathlib import Path

from .models import MediaFile, Stream, CommandArguments
from .ffmpeg import FfmpegExecutor, execute_ffprobe
from .environment import *

def resolve_new_subtitle_file_path(subtitle: Stream, name: str, destination_dir: str) -> str:
    """Resolve the output path for a subtitle file."""
    language_str = subtitle.language
    if not language_str:
        language_str = "unknown"
    if subtitle.is_hearing_impaired():
        language_str += ".sdh"
    if subtitle.is_forced():
        language_str += ".forced"

    output_base = f"{destination_dir}/{name}.{language_str}"
    output_file = f"{output_base}.srt"
    i = 0
    while Path(output_file).exists():
        i += 1
        output_file = f"{output_base}.{i}.srt"
    return output_file

def extract_subtitles(
    input_file: MediaFile,
    destination_dir: str,
    subtitle_streams: list[Stream] = []
) -> None:
    """Extract subtitle streams from a media file."""
    if not subtitle_streams:
        subtitle_streams = input_file.get_subtitle_streams()
    if not subtitle_streams:
        print("WARNING: No subtitle streams present")
        return

    subtitle_streams = [stream for stream in subtitle_streams if not stream.is_image_based_subtitle()]
    if not subtitle_streams:
        print("WARNING: Only image based subtitle streams present, will not extract any subtitles")
        return

    inputfilename_without_extension = Path(input_file.path).stem

    for subtitle in subtitle_streams:
        output_file = resolve_new_subtitle_file_path(subtitle, inputfilename_without_extension, destination_dir)

        print(f"Extracting subtitle: {subtitle}")
        executor = FfmpegExecutor(input_file.path)
        executor.add_args(['-map', f'0:{subtitle.index}'])
        executor.add_args(['-c', 'srt'])
        executor.add_arg(output_file)
        result = executor.execute()
        if result.is_failed():
            print_error(
                f"Failed to extract subtitle: {subtitle}. \n"
                f"Command: {result.get_command_as_string()}\n"
                f"Response code: {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
            raise RuntimeError(f"Failed to extract subtitle: {subtitle}")


def process_file(input_file_path: str, args: CommandArguments) -> None:
    """Process a single media file according to command line arguments."""

    print(f"\nProcessing '{input_file_path}'")
    input_file = parse_mediafile(input_file_path)

    print(f"\n{input_file}\n")
    if args.list_streams:
        return

    output_container = args.output_container if args.output_container else input_file.container
    container_change = input_file.container != output_container

    num_actions = 0
    action_list = list()

    executor = FfmpegExecutor(input_file.path)
    executor.add_args(['-c', 'copy'])
    executor.add_args(['-map', '0'])

    # Container change
    if container_change:
        num_actions += 1
        action_list.append(f" * Will change container from {input_file.container} to {output_container}")

    # Extract subtitles
    if args.extract_subtitle_streams:
        action_list.append(" * Will extract all subtitles")
        image_based_subs = [stream for stream in input_file.get_subtitle_streams() if stream.is_image_based_subtitle()]
        if image_based_subs:
            action_list.append("   WARNING: The following subtitles are image based and will not be extracted:")
            for sub in image_based_subs:
                action_list.append(f"    - {sub}")

    # Set stream language
    if args.set_stream_language:
        stream_index = args.set_stream_language[0]
        new_language = args.set_stream_language[1]
        if stream_index >= len(input_file.streams):
            fatal(f"Stream index not found: {stream_index}")
        stream_to_modify = input_file.streams[stream_index]
        if stream_to_modify.language == new_language:
            print(f"WARNING: The specified stream already has '{new_language}' set as language: \n{stream_to_modify}")
        else:
            num_actions += 1
            action_list.append(f" * Will update the following stream language to '{new_language}': {stream_to_modify}")
            executor.add_args([f"-metadata:s:{stream_index}", f"language={new_language}"])

    # Convert stream
    if args.convert_stream:
        stream_index = args.convert_stream[0]
        target_codec = args.convert_stream[1]
        if stream_index >= len(input_file.streams):
            fatal(f"Stream index not found: {stream_index}")
        stream_to_modify = input_file.streams[stream_index]
        if stream_to_modify.codec_name == target_codec:
            print(f"WARNING: The specified stream is already encoded with '{target_codec}': \n{stream_to_modify}")
        else:
            num_actions += 1
            action_list.append(f" * Will re-encode the following stream with codec '{target_codec}': {stream_to_modify}")
            executor.add_args([f"-c:{stream_index}", f"{target_codec}"])

    # Extract specific stream
    if args.extract_streams:
        for index in args.extract_streams:
            if index >= len(input_file.streams):
                fatal(f"Stream index not found: {index}")
            stream_to_extract = input_file.streams[index]
            if not stream_to_extract.is_subtitle:
                fatal("Only subtitle streams are currently supported for extractions.")
            action_list.append(f" * Will extract the following stream: {stream_to_extract}")

    # Delete specific stream
    if args.delete_streams:
        for index in args.delete_streams:
            if index >= len(input_file.streams):
                fatal(f"Stream index not found: {index}")
            num_actions += 1
            stream_to_delete = input_file.streams[index]
            executor.add_args(['-map', f'-0:{stream_to_delete.index}'])
            action_list.append(f" * Will delete the following stream: {stream_to_delete}")

    # Delete audio streams except one
    if args.delete_audio_streams_except is not None:
        if args.delete_audio_streams_except > len(input_file.get_audio_streams()):
            fatal(f"Audio stream index not found: {args.delete_audio_streams_except}")

        audio_streams_to_delete = [
            stream for stream in input_file.get_audio_streams()
            if stream.index != args.delete_audio_streams_except
        ]
        if audio_streams_to_delete:
            num_actions += 1
            action_list.append(" * Will delete the following audio streams:")
            for stream in audio_streams_to_delete:
                action_list.append(f"    - {stream}")
                executor.add_args(['-map', f'-0:{stream.index}'])

    # Delete image streams
    if args.delete_image_streams:
        image_streams_to_delete = [stream for stream in input_file.get_video_streams() if stream.is_image()]
        if image_streams_to_delete:
            num_actions += 1
            action_list.append(" * Will delete the following image video streams:")
            for stream in image_streams_to_delete:
                action_list.append(f"    - {stream}")
                executor.add_args(['-map', f'-0:{stream.index}'])

    # Delete data streams
    if args.delete_data_streams:
        num_actions += 1
        action_list.append(" * Will delete data streams")
        executor.add_args(['-dn'])
        executor.add_args(['-map_chapters', '-1'])
        if input_file.get_other_streams():
            action_list.append(" * Will delete the following other streams:")
            for stream in input_file.get_other_streams():
                action_list.append(f"    - {stream}")
                executor.add_args(['-map', f'-0:{stream.index}'])

    # Delete subtitles
    if args.delete_subtitle_streams:
        subtitles_detected = False

        if len(input_file.get_subtitle_streams()) > 0:
            num_actions += 1
            subtitles_detected = True
            action_list.append(" * Will delete all subtitle streams")
            executor.add_arg('-sn')

        if any(s.has_embedded_subtitles() for s in input_file.get_video_streams()):
            for stream in input_file.get_video_streams():
                if stream.has_embedded_subtitles():
                    if stream.codec_name == 'h264':
                        executor.add_args(['-bsf:v', 'filter_units=remove_types=6'])
                    elif stream.codec_name == 'hevc':
                        executor.add_args(['-bsf:v', 'filter_units=remove_types=39'])
                    else:
                        print_error(f"Embedded subtitle removal from {stream.codec_name} not implemented")
                        break
                    num_actions += 1
                    subtitles_detected = True
                    action_list.append(" * Will delete embedded EIA608 closed captions from video using bitstream filter")

        if not subtitles_detected:
            action_list.append(" * Requested deletion of all subtitle streams but none exists")

    if not action_list:
        verbose("No actions specified")
        return

    print("\nACTIONS:")
    for action in action_list:
        print(action)

    option_list = []
    if args.dry_run:
        option_list.append(" * Dry-run mode, will not perform any actions")
    if args.create_dir:
        option_list.append(" * Will create a new directory with the same name as the video file")
    if not args.cleanup:
        option_list.append(" * Cleanup disabled, will leave the source file behind, unmodified")

    if option_list:
        print("\nOPTIONS:")
        [print(option) for option in option_list]

    confirm()

    inputfilename_without_extension = Path(input_file.path).stem

    working_dir = os.path.dirname(os.path.abspath(input_file.path))
    if args.create_dir:
        working_dir = f"{working_dir}/{inputfilename_without_extension}"

    working_file = f"{working_dir}/{inputfilename_without_extension}.new.{output_container}"
    verbose(f"Working file    : {working_file}")
    if Path(working_file).exists():
        fatal(f"Working file already exists: {working_file}")

    output_file = f"{working_dir}/{inputfilename_without_extension}.{output_container}"
    verbose(f"Destination file: {output_file}")

    if container_change and Path(output_file).exists():
        fatal(f"Output file already exists: {output_file}")

    if not Path(working_dir).exists() and not GlobalSettings.DRY_RUN:
        verbose(f"Creating working dir: {working_dir}")
        os.makedirs(working_dir)

    # Extract streams if requested
    if args.extract_streams:
        streams_to_extract = [input_file.streams[index] for index in args.extract_streams]
        extract_subtitles(input_file, working_dir, streams_to_extract)
    if args.extract_subtitle_streams:
        extract_subtitles(input_file, working_dir)

    if num_actions == 0:
        # the only action was to extract subs
        return

    print("Performing selected actions on source file")
    executor.add_arg(working_file)
    result = executor.execute()

    if result.returncode != 0:
        fatal(f"ffmpeg execution failed with exit code {result.returncode}")

    print("\nffmpeg execution successful")

    cleanup(inputfile=input_file.path, workingfile=working_file, outputfile=output_file, args=args)

def parse_mediafile(filepath: str) -> MediaFile:
    """Parse a media file using ffprobe and return a MediaFile object."""
    print_error(filepath)
    ffprobe_result = execute_ffprobe(filepath)

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

def cleanup(inputfile: str, workingfile: str, outputfile: str, args: CommandArguments) -> None:
    """Clean up temporary files after processing."""
    
    if args.dry_run:
        return
    
    if not args.cleanup:
        print("Cleanup disabled, leaving old file behind.")
        print(f"Original file: {inputfile}")
        print(f"Modified file: {workingfile}")
        return

    if not Path(workingfile).exists():
        fatal(f"{workingfile} does not exist. Aborting cleanup")

    verbose(f"Deleting {inputfile}")
    os.unlink(inputfile)

    verbose(f"Moving {workingfile} -> {outputfile}")
    os.replace(workingfile, outputfile)

def confirm() -> None:
    """Prompt for confirmation if confirm mode is enabled."""
    print()
    if GlobalSettings.CONFIRM:
        input('Press ENTER to continue or CTRL-C to abort\n')
