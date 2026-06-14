# Mediautil

A multi-purpose media editing tool built on top of ffmpeg and ffprobe.

## Requirements

- Python 3.7 or higher
- ffmpeg (must be in PATH)

## Installation

### Manual Deployment (Recommended for Production)

This project uses manual deployment to `/opt`. On your production server:

```bash
./deploy.sh
```

The deployment script will:
- Verify Python 3.7+ and ffmpeg are installed
- Clean up any previous installation
- Copy all files to `/opt/mediautil/`

**To uninstall:**
```bash
rm -rf /opt/mediautil
```

## Usage

```bash
# List information about media files
mediautil --list video.mp4

# Extract subtitles
mediautil --extract-subs video.mp4

# Delete all subtitle streams
mediautil --delete-subs video.mp4

# Change container format
mediautil --output-container mkv video.mp4

# Set stream language
mediautil --set-stream-language 1 eng video.mp4

# Delete specific streams
mediautil --delete-stream 2,3 video.mp4

# Run in dry-run mode (no changes)
mediautil --dry-run --list video.mp4

# Enable verbose output
mediautil -v --list video.mp4

# Enable debug mode
mediautil --debug --list video.mp4
```

## Running Tests

```bash
pytest mediautil/tests/
```

## Features

- List media file information (streams, codecs, languages, etc.)
- Extract subtitle streams to SRT files
- Delete specific streams or all streams of a type
- Change container format
- Set stream language
- Remove embedded closed captions (EIA-608)
- Dry-run mode for testing commands without making changes
- Verbose and debug output modes
- Support for multiple input files
