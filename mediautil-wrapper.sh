#!/bin/bash
# Wrapper script for mediautil
# This script is installed to /usr/local/bin/mediautil by deploy.sh

PYTHONPATH="/opt/mediautil:$PYTHONPATH"
export PYTHONPATH

exec /usr/bin/python3 -m mediautil "$@"
