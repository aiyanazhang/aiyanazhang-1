#!/bin/bash

# Java Environment Checker Launch Script
# This script provides a convenient way to run the Java Environment Checker

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# JAR file location
JAR_FILE="$SCRIPT_DIR/java-env-checker.jar"

# Check if JAR file exists
if [ ! -f "$JAR_FILE" ]; then
    echo "Error: JAR file not found at $JAR_FILE"
    echo "Please ensure the application is properly built and packaged."
    exit 1
fi

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH"
    echo "Please install Java and ensure it's available in your PATH"
    exit 1
fi

# Run the application
java -jar "$JAR_FILE" "$@"