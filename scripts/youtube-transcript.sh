#!/bin/bash

# YouTube Transcription Script - Pure Function
# Usage: ./youtube-transcript.sh "URL" "TEXT_DIR" "VIDEO_ID"
# Called by content-extractor.sh with proper paths

# Check arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 'https://youtube.com/watch?v=...' '/path/to/text/dir' 'video_id'"
    echo "Note: This script is typically called by content-extractor.sh"
    exit 1
fi

# Get arguments (no config loading needed)
VIDEO_URL="$1"
TEXT_DIR="$2"
VIDEO_ID="$3"

# Ensure output directory exists
mkdir -p "$TEXT_DIR"

# Final output file (cache-friendly filename)
FINAL_OUTPUT="$TEXT_DIR/youtube-$VIDEO_ID.txt"



# Check if yt-dlp is installed
if ! command -v yt-dlp &> /dev/null; then
    echo "Error: yt-dlp is not installed. Please install it first:"
    echo "pip install yt-dlp"
    exit 1
fi

# Get the video title and sanitize it for filesystem
echo "Getting video title..."
TITLE=$(yt-dlp --get-title "$VIDEO_URL" 2>/dev/null | tr -d '/:?"*<>|' | tr ' ' '_')

if [ -z "$TITLE" ]; then
    echo "Error: Could not retrieve video title. Please check the URL."
    exit 1
fi

echo "Processing video: $TITLE"

# Create temp directory for processing
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download subtitles
echo "Downloading subtitles..."
yt-dlp --skip-download --write-auto-sub --sub-lang "en" --convert-subs "srt" -o "${TITLE}.%(ext)s" "$VIDEO_URL"

# Check if subtitles were downloaded
if [ ! -f "${TITLE}.en.srt" ]; then
    echo "Error: Could not download subtitles. Auto-generated subtitles may not be available for this video."
    exit 1
fi

# Process the subtitles directly in bash (replaces the Python script)
echo "Cleaning transcript..."

# Use awk to process the SRT file and clean it up
awk '
BEGIN { 
    previous_line = "" 
}
{
    # Skip timestamp lines (contain -->)
    if ($0 ~ /-->/) next
    
    # Skip line numbers (lines that are only digits)
    if ($0 ~ /^[0-9]+$/) next
    
    # Skip empty lines
    if ($0 ~ /^[[:space:]]*$/) next
    
    # Skip bracketed content like [Music], [Applause], etc.
    # Handle both full-line bracketed content and mixed content
    if ($0 ~ /^[[:space:]]*\[.*\][[:space:]]*$/) next
    
    # Remove leading/trailing whitespace
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
    
    # Only print if different from previous line (remove duplicates)
    if ($0 != previous_line && $0 != "") {
        print $0
        previous_line = $0
    }
}' "${TITLE}.en.srt" > "${TITLE}.txt"

# Clean up the SRT file
rm "${TITLE}.en.srt"

# Move to final location with cache-friendly filename
mv "${TITLE}.txt" "$FINAL_OUTPUT"

# Clean up temp directory
cd /
rm -rf "$TEMP_DIR"

echo "✅ Transcript saved to: $FINAL_OUTPUT" 