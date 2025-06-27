#!/bin/bash
set -e

# Install required Python packages
if ! python3 -m pip install -r requirements.txt; then
    echo "Failed to install runtime requirements" >&2
    exit 1
fi

if [ "$1" = "--dev" ]; then
    # Install development tools as well
    if ! python3 -m pip install -r requirements-dev.txt; then
        echo "Failed to install development requirements" >&2
        exit 1
    fi
fi
