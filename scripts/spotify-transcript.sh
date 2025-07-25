#!/bin/bash

# Spotify Transcription Script - Pure Function
# Usage: ./spotify-transcript.sh "URL" "TEXT_DIR" "AUDIO_DIR" "ONTHESPOT_DIR" 
# Called by content-extractor.sh with proper paths
# 
# Requirements:
# - OnTheSpot (for downloading Spotify content)
# - Whisper (for transcription)
# - FFmpeg (for audio conversion)

# Check arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 'SPOTIFY_URL' 'TEXT_DIR' 'AUDIO_DIR' 'ONTHESPOT_DIR' 'URL_HASH'"
    echo "Note: This script is typically called by content-extractor.sh"
    exit 1
fi

# Get arguments (no config loading needed)
SPOTIFY_URL="$1"
TEXT_DIR="$2"
AUDIO_DIR="$3"
ONTHESPOT_DIR="$4"
URL_HASH="$5"

# OnTheSpot downloads to its own location, we'll copy from there
DEFAULT_DOWNLOAD_PATH="$HOME/Music/OnTheSpot"

# Final output file (cache-friendly filename)  
FINAL_OUTPUT="$TEXT_DIR/spotify-$URL_HASH.txt"

# Ensure output directories exist
mkdir -p "$TEXT_DIR" "$AUDIO_DIR"

# Auto-install OnTheSpot if not found and directory is empty
if [ -z "$ONTHESPOT_DIR" ]; then
    echo "🔧 OnTheSpot not found. Attempting auto-installation..."
    
    # Try brew first
    if command -v brew >/dev/null 2>&1; then
        echo "📦 Trying brew install..."
        if brew tap casual-snek/onthespot && brew install onthespot; then
            echo "✅ OnTheSpot installed via brew"
            # Update directory for this session
            ONTHESPOT_DIR="$(brew --prefix)/bin"
        else
            echo "⚠️  Brew install failed, trying local install..."
        fi
    fi
    
    # If brew failed or unavailable, try local install
    if [ -z "$ONTHESPOT_DIR" ] || [ ! -d "$ONTHESPOT_DIR" ]; then
        echo "📁 Installing OnTheSpot locally..."
        REPO_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
        LOCAL_ONTHESPOT="$REPO_DIR/content/apps/onthespot"
        
        mkdir -p "$REPO_DIR/content/apps"
        cd "$REPO_DIR/content/apps"
        
        if git clone https://github.com/casualsnek/onthespot; then
            cd onthespot
            python3 -m venv onthespot_env
            source onthespot_env/bin/activate
            pip install -r requirements.txt
            echo "✅ OnTheSpot installed locally to content/apps/onthespot"
            ONTHESPOT_DIR="$LOCAL_ONTHESPOT"
        else
            echo "❌ Failed to install OnTheSpot automatically"
            echo "📋 Manual installation options:"
            echo "1. Brew (if available): brew tap casual-snek/onthespot && brew install onthespot"
            echo "2. Local: cd content/apps && git clone https://github.com/casualsnek/onthespot"
            echo "3. Manual: Install to ~/Applications/onthespot"
            exit 1
        fi
    fi
fi

# Check if OnTheSpot is actually working
if ! command -v onthespot-cli &> /dev/null; then
    if [ ! -d "$ONTHESPOT_DIR" ]; then
        echo "❌ OnTheSpot directory not found: $ONTHESPOT_DIR"
        exit 1
    fi
fi

# Check if Whisper is installed
if ! command -v whisper &> /dev/null; then
    echo "❌ Whisper not found. To install:"
    echo "   pip install openai-whisper"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. To install:"
    echo "   brew install ffmpeg"
    exit 1
fi

# Determine if we're using installed OnTheSpot or source build
if [ -f "$ONTHESPOT_DIR/onthespot_env/bin/activate" ]; then
    echo "Using OnTheSpot source build..."
    cd "$ONTHESPOT_DIR"
    source onthespot_env/bin/activate
    # CRITICAL: Set FFMPEG_PATH environment variable (OnTheSpot has which() commented out)
    export FFMPEG_PATH="/opt/homebrew/bin/ffmpeg"
    ONTHESPOT_CMD="onthespot-cli"
elif command -v onthespot-cli &> /dev/null; then
    export FFMPEG_PATH="/opt/homebrew/bin/ffmpeg"
    ONTHESPOT_CMD="onthespot-cli"
else
    echo "❌ OnTheSpot environment not found. Please run setup first."
    exit 1
fi

# Create timestamp for tracking new downloads
touch /tmp/spotify_download_start

# Download from Spotify using OnTheSpot
echo "📥 Downloading from Spotify to default OnTheSpot directory..."
echo "URL: $SPOTIFY_URL"

# OnTheSpot downloads to its configured directory, not current directory
# The default is /Users/joe/Music/OnTheSpot based on config
$ONTHESPOT_CMD --download "$SPOTIFY_URL"

if [ $? -ne 0 ]; then
    echo "❌ Failed to download from Spotify"
    echo "💡 Make sure you're logged into your Premium account in OnTheSpot"
    echo "💡 Some tracks may not be available due to regional restrictions or DRM"
    exit 1
fi

# Find downloaded files in OnTheSpot's default directory
# Check both the default location and common subdirectories
echo "🔍 Looking for downloaded files in $DEFAULT_DOWNLOAD_PATH..."

# Find MP3 files newer than our start timestamp
AUDIO_FILES=$(find "$DEFAULT_DOWNLOAD_PATH" -name "*.mp3" -type f -newer /tmp/spotify_download_start 2>/dev/null)

if [ -z "$AUDIO_FILES" ]; then
    echo "⚠️  No new files found. Checking for any existing MP3 files..."
    # Fallback: show any MP3 files that exist
    EXISTING_FILES=$(find "$DEFAULT_DOWNLOAD_PATH" -name "*.mp3" -type f -maxdepth 3 2>/dev/null | head -5)
    if [ ! -z "$EXISTING_FILES" ]; then
        echo "📁 Found existing MP3 files:"
        echo "$EXISTING_FILES"
        echo ""
        echo "💡 If you want to transcribe existing files, you can run:"
        echo "   whisper 'path/to/file.mp3' --model medium --output_format txt --output_dir '/Users/joe/Documents/Reports/Spotify-transcripts/text'"
    else
        echo "❌ No MP3 files found in OnTheSpot directory"
        echo "💡 The track may not be available for download, or there may be authentication issues"
    fi
    exit 1
fi

# Copy downloaded files to our working directory for processing
echo "📋 Copying downloaded files to working directory..."
for audio_file in $AUDIO_FILES; do
    cp "$audio_file" "$AUDIO_DIR/"
    echo "Copied: $(basename "$audio_file")"
done

# Transcribe each audio file
echo "🎤 Starting transcription with Whisper..."

for audio_file in "$AUDIO_DIR"/*.mp3; do
    if [ -f "$audio_file" ]; then
        # Get just the filename without path and extension
        base_name=$(basename "$audio_file" .mp3)
        
        echo "Transcribing: $base_name"
        
        # Use Whisper to transcribe
        # --model medium for good quality/speed balance
        # --output_format txt for plain text
        # --output_dir to specify where transcripts go
        # Create temp directory for this transcription
        TEMP_TRANSCRIPT_DIR=$(mktemp -d)
        
        whisper "$audio_file" \
            --model medium \
            --output_format txt \
            --output_dir "$TEMP_TRANSCRIPT_DIR" \
            --language en \
            --task transcribe
        
        if [ $? -eq 0 ]; then
            # Find the generated transcript and append to final output
            temp_transcript=$(find "$TEMP_TRANSCRIPT_DIR" -name "*.txt" | head -1)
            if [ -f "$temp_transcript" ]; then
                echo "=== $base_name ===" >> "$FINAL_OUTPUT"
                cat "$temp_transcript" >> "$FINAL_OUTPUT"
                echo "" >> "$FINAL_OUTPUT"
                echo "✅ Transcribed: $base_name"
            else
                echo "❌ Failed to find transcript for: $base_name"
            fi
            # Clean up temp transcript
            rm -rf "$TEMP_TRANSCRIPT_DIR"
        else
            echo "❌ Failed to transcribe: $base_name"
            rm -rf "$TEMP_TRANSCRIPT_DIR"
        fi
    fi
done

# Summary
echo ""
echo "🎯 Transcription Complete!"
echo "📁 Audio files: $AUDIO_DIR/"
echo "📄 Transcripts: $TEXT_DIR/"
echo ""

# Show final consolidated transcript
if [ -f "$FINAL_OUTPUT" ]; then
    echo "✅ Consolidated transcript created: $FINAL_OUTPUT"
    echo "📊 Size: $(wc -l < "$FINAL_OUTPUT") lines"
else
    echo "❌ No transcript was created"
fi