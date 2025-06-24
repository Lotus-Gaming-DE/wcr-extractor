#!/bin/bash
# Install required Python packages
pip install -r requirements.txt

if [ "$1" = "--dev" ]; then
    # Install development tools as well
    pip install -r requirements-dev.txt
fi
