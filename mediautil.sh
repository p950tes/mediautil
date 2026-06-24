#!/bin/bash
# Wrapper script for mediautil

PYTHONPATH="/opt/mediautil:$PYTHONPATH"
export PYTHONPATH

exec /usr/bin/python3 -m mediautil "$@"
