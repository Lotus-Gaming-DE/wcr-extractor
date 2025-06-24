#!/bin/bash
# Install required Python packages
python3 -m pip install -r requirements.txt

if [ "$1" = "--dev" ]; then
    # Install development tools as well
    python3 -m pip install -r requirements-dev.txt
fi
