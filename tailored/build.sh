#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="resume-builder"
TEX_FILE="${1:-output/resume.tex}"

# Check Docker is available
if ! command -v docker &>/dev/null; then
    echo "Error: Docker is not installed or not in PATH." >&2
    exit 1
fi

# Build image if it doesn't exist
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Building Docker image '$IMAGE_NAME'..."
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
fi

# Ensure output directory exists
mkdir -p "$SCRIPT_DIR/output"

# Run pdflatex inside the container
echo "Compiling $TEX_FILE..."
docker run --rm \
    -v "$SCRIPT_DIR":/resume \
    "$IMAGE_NAME" \
    -output-directory=output \
    -interaction=nonstopmode \
    "$TEX_FILE"

echo "Done. Output in $SCRIPT_DIR/output/"
