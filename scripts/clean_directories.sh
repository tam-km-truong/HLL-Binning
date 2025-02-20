#!/bin/bash

# Delete all files in the output and tmp directories
rm -rf output/* tmp/*

# Create necessary directories if they don't exist
mkdir -p output tmp tmp/sketches tmp/completion tmp/bins

echo "All files in output and tmp have been removed, and necessary directories are recreated."
