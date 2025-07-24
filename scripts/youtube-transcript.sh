#!/bin/bash

# YouTube Transcription Script (Consolidated Version)
# Usage: ./youtube-transcript-consolidated.sh "https://youtube.com/watch?v=..."

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Error: Please provide a YouTube URL"
    echo "Usage: $0 'https://youtube.com/watch?v=...'"
    exit 1
fi

# Store URL in variable
VIDEO_URL="$1"

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

# Create output directory if it doesn't exist
mkdir -p "/Users/joe/Documents/Reports/YT-transcripts"

# Change to output directory
cd "/Users/joe/Documents/Reports/YT-transcripts"

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

echo "✅ Transcript saved to: /Users/joe/Documents/Reports/YT-transcripts/${TITLE}.txt" 