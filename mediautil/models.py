"""Data models for mediautil."""

from dataclasses import dataclass

@dataclass
class CommandArguments:
    files: list[str]
    
    verbose: bool
    debug: bool
    confirm: bool
    dry_run: bool

    cleanup: bool
    create_dir: bool
    
    list_streams: bool

    output_container: str|None

    set_title: str|None
    set_stream_language: tuple[int, str]|None
    
    extract_streams: list[int]|None
    extract_subtitle_streams: bool
    
    delete_streams: list[int]|None
    delete_audio_streams_except: int|None
    delete_data_streams: bool
    delete_image_streams: bool
    delete_subtitle_streams: bool

    convert_stream: tuple[int, str]|None

    hardware_acceleration_enabled: bool
    multi_threaded: bool
    
    custom_ffmpeg_args: list[str]|None
