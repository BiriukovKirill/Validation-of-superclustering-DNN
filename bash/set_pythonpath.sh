#!/bin/bash

# Get the directory where this script lives (e.g., my_repo/bash)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go one level up to reach the repo root (my_repo/)
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set PYTHONPATH to include the 'python' directory in the repo
export PYTHONPATH="$REPO_ROOT/python:$PYTHONPATH"

echo "PYTHONPATH set to: $PYTHONPATH"