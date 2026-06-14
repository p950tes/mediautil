"""Constants for mediautil."""

# Specify how many microseconds are analyzed to probe the input.
# A higher value will enable detecting more accurate information, but will increase latency.
# It defaults to 5,000,000 microseconds = 5 seconds.
FFMPEG_ANALYZEDURATION = str(100_000_000)

# Set probing size in bytes, i.e. the size of the data to analyze to get stream information.
# A higher value will enable detecting more information in case it is dispersed into the stream,
# but will increase latency. Must be an integer not lesser than 32. It is 5000000 by default.
FFMPEG_PROBESIZE = str(100_000_000)
