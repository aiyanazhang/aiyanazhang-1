#!/bin/bash

set -e

OUTPUT_DIR="${1:-$HOME/Downloads/qoder_logs_$(date +%Y%m%d_%H%M%S)}"

echo "Creating output directory: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "Collecting Qoder logs..."

ACP_DIR="$OUTPUT_DIR/acp_logs"
mkdir -p "$ACP_DIR"
if [ -f "$TMPDIR/acp.log" ]; then
    echo "Copying acp.log..."
    cp "$TMPDIR/acp.log" "$ACP_DIR/"
else
    echo "Warning: $TMPDIR/acp.log not found"
fi

CLI_CACHE_DIR="$HOME/Library/Application Support/Qoder/SharedClientCache/cli"
CLI_OUTPUT_DIR="$OUTPUT_DIR/cli_cache"
mkdir -p "$CLI_OUTPUT_DIR"
if [ -d "$CLI_CACHE_DIR" ]; then
    echo "Archiving cli cache..."
    tar -czf "$CLI_OUTPUT_DIR/cli_cache.tar.gz" -C "$HOME/Library/Application Support/Qoder/SharedClientCache" "cli"
else
    echo "Warning: $CLI_CACHE_DIR not found"
fi

DIAGNOSIS_FILE="$HOME/Library/Application Support/Qoder/SharedClientCache/cache/diagnosis.bin"
DIAGNOSIS_DIR="$OUTPUT_DIR/diagnosis"
mkdir -p "$DIAGNOSIS_DIR"
if [ -f "$DIAGNOSIS_FILE" ]; then
    echo "Copying diagnosis.bin..."
    cp "$DIAGNOSIS_FILE" "$DIAGNOSIS_DIR/"
else
    echo "Warning: $DIAGNOSIS_FILE not found"
fi

QODER_LOGS_SOURCE="$HOME/Library/Application Support/Qoder/logs"
QODER_LOGS_DIR="$OUTPUT_DIR/qoder_logs"
if [ -d "$QODER_LOGS_SOURCE" ]; then
    echo "Archiving Qoder logs..."
    tar -czf "$QODER_LOGS_DIR.tar.gz" -C "$HOME/Library/Application Support/Qoder" "logs"
else
    echo "Warning: $QODER_LOGS_SOURCE not found"
fi

TEMP_DIR="$OUTPUT_DIR"
FINAL_DIR=$(dirname "$OUTPUT_DIR")
ARCHIVE_NAME="qoder_logs_$(date +%Y%m%d_%H%M%S).tar.gz"
ARCHIVE_PATH="$FINAL_DIR/$ARCHIVE_NAME"

echo "Creating archive..."
tar -czf "$ARCHIVE_PATH" -C "$FINAL_DIR" "$(basename "$TEMP_DIR")"

echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"

echo "Log collection complete!"
echo "Archive saved to: $ARCHIVE_PATH"
ls -lh "$ARCHIVE_PATH"
