#!/bin/bash

echo "Starting Legal Document AI Assistant..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Python is not installed or not in PATH"
        echo "Please install Python 3.8 or higher"
        exit 1
    else
        python start.py
    fi
else
    python3 start.py
fi
