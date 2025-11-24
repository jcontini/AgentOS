#!/bin/bash

# YouTube Content Extraction Script
# Usage: ./youtube-transcript.sh "YOUTUBE_URL" [--video]
# Default: transcript only
# --video: download both video and transcript

# Check arguments
if [ -z "$1" ]; then
    echo "Error: Missing YouTube URL"
    echo "Usage: $0 'https://youtube.com/watch?v=...' [--video]"
    echo "  Default: Download transcript only"
    echo "  --video: Download both video and transcript"
    exit 1
fi

# Parse arguments
VIDEO_URL="$1"
DOWNLOAD_VIDEO=false

if [ "$2" = "--video" ]; then
    DOWNLOAD_VIDEO=true
fi

# Extract video ID
VIDEO_ID=$(echo "$VIDEO_URL" | sed -n 's/.*[?&]v=\([^&]*\).*/\1/p')

if [ -z "$VIDEO_ID" ]; then
    echo "Error: Could not extract video ID from URL"
    exit 1
fi

# Set up directories relative to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TEXT_DIR="$PROJECT_ROOT/user/youtube/transcripts"
VIDEO_DIR="$PROJECT_ROOT/user/youtube/videos"

# Ensure output directories exist
mkdir -p "$TEXT_DIR"
if [ "$DOWNLOAD_VIDEO" = true ]; then
    mkdir -p "$VIDEO_DIR"
fi

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

# Get current date in YYYY-MM-DD format
CURRENT_DATE=$(date +%Y-%m-%d)

# Set final output filenames with date prefix
TRANSCRIPT_OUTPUT="$TEXT_DIR/${CURRENT_DATE}_$TITLE.txt"
VIDEO_OUTPUT="$VIDEO_DIR/${CURRENT_DATE}_$TITLE.%(ext)s"

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

# Move transcript to final location
mv "${TITLE}.txt" "$TRANSCRIPT_OUTPUT"

# Output transcript content to stdout
echo ""
echo "==================== TRANSCRIPT CONTENT ===================="
cat "$TRANSCRIPT_OUTPUT"
echo "============================================================"
echo ""

# Download video if requested
if [ "$DOWNLOAD_VIDEO" = true ]; then
    echo "Downloading video..."
    cd "$VIDEO_DIR"
    yt-dlp -f "best[height<=1080]" -o "${CURRENT_DATE}_$TITLE.%(ext)s" "$VIDEO_URL"
    
    if [ $? -eq 0 ]; then
        echo "✅ Video saved to: $VIDEO_DIR/${CURRENT_DATE}_$TITLE.*"
    else
        echo "❌ Video download failed"
    fi
fi

# Clean up temp directory
cd /
rm -rf "$TEMP_DIR"

echo "✅ Transcript saved to: $TRANSCRIPT_OUTPUT" 