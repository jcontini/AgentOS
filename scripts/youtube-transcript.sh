#!/bin/bash

# YouTube Transcription Script - Simplified
# Usage: ./youtube-transcript.sh "YOUTUBE_URL"

# Check arguments
if [ -z "$1" ]; then
    echo "Error: Missing YouTube URL"
    echo "Usage: $0 'https://youtube.com/watch?v=...'"
    exit 1
fi

# Get URL and extract video ID
VIDEO_URL="$1"
VIDEO_ID=$(echo "$VIDEO_URL" | sed -n 's/.*[?&]v=\([^&]*\).*/\1/p')

if [ -z "$VIDEO_ID" ]; then
    echo "Error: Could not extract video ID from URL"
    exit 1
fi

# Set up directories relative to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEXT_DIR="$SCRIPT_DIR/../content/youtube/transcripts"

# Ensure output directory exists
mkdir -p "$TEXT_DIR"

# Final output file (will be set after getting title)



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

# Set final output filename using title (no prefix needed in dedicated directory)
FINAL_OUTPUT="$TEXT_DIR/$TITLE.txt"

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