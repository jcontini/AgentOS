#!/bin/bash

# content-extractor.sh
# Simple URL router for getting content into LLM context
# Usage: ./content-extractor.sh "https://any-url"

set -e  # Exit on error

# Configuration loading
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"

function load_config() {
    # Auto-detect repo directory (parent of scripts dir)
    REPO_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Set defaults - scripts auto-detect repo location
    YOUTUBE_SCRIPT="$REPO_DIR/scripts/youtube-transcript.sh"
    SPOTIFY_SCRIPT="$REPO_DIR/scripts/spotify-transcript.sh"
    # Default content locations
    CONTENT_TEXT="$REPO_DIR/content/text"     # All transcripts
    CONTENT_AUDIO="$REPO_DIR/content/audio"   # Audio files
    CONTENT_VIDEO="$REPO_DIR/content/video"   # Video files  
    CONTENT_APPS="$REPO_DIR/content/apps"     # Local installations
    # OnTheSpot location (hardcoded)
    ONTHESPOT_DIR="$CONTENT_APPS/onthespot"
    
    # Try to load from YAML config if yq is available
    if command -v yq >/dev/null 2>&1 && [[ -f "$CONFIG_FILE" ]]; then
        echo "📄 Loading AgentOS config from $CONFIG_FILE"
        
        # Get content paths (support both relative and absolute)
        local text_path audio_path video_path apps_path
        text_path=$(yq eval '.content.text // "content/text"' "$CONFIG_FILE")
        audio_path=$(yq eval '.content.audio // "content/audio"' "$CONFIG_FILE")
        video_path=$(yq eval '.content.video // "content/video"' "$CONFIG_FILE")
        apps_path=$(yq eval '.content.apps // "content/apps"' "$CONFIG_FILE")
        
        # Convert relative paths to absolute (starting with repo root)
        if [[ "$text_path" != /* ]]; then
            CONTENT_TEXT="$REPO_DIR/$text_path"
        else
            CONTENT_TEXT="$text_path"
        fi
        
        if [[ "$audio_path" != /* ]]; then
            CONTENT_AUDIO="$REPO_DIR/$audio_path"
        else
            CONTENT_AUDIO="$audio_path"
        fi
        
        if [[ "$video_path" != /* ]]; then
            CONTENT_VIDEO="$REPO_DIR/$video_path"
        else
            CONTENT_VIDEO="$video_path"
        fi
        
        if [[ "$apps_path" != /* ]]; then
            CONTENT_APPS="$REPO_DIR/$apps_path"
        else
            CONTENT_APPS="$apps_path"
        fi
        
        # OnTheSpot location (always in apps folder)
        ONTHESPOT_DIR="$CONTENT_APPS/onthespot"
        
        echo "🏠 Repo: $REPO_DIR"
        echo "📁 Content: Custom paths from config"
    else
        if [[ ! -f "$CONFIG_FILE" ]]; then
            echo "⚠️  No config file found at $CONFIG_FILE, using defaults"
        elif ! command -v yq >/dev/null 2>&1; then
            echo "⚠️  yq not found, using default paths"
            echo "   Edit config.yaml to customize content locations"
        fi
        echo "🏠 Repo: $REPO_DIR (auto-detected)"
        echo "📁 Content: $REPO_DIR/content/* (default)"
    fi
    
    # Ensure content directories exist
    mkdir -p "$CONTENT_TEXT" "$CONTENT_AUDIO" "$CONTENT_VIDEO" "$CONTENT_APPS"
}

function main() {
    load_config
    
    local url="$1"
    local output_dir="${2:-$CONTENT_TEXT}"
    
    if [[ -z "$url" ]]; then
        echo "Usage: $0 <url>"
        echo "Examples:"
        echo "  $0 'https://youtube.com/watch?v=xyz'"
        echo "  $0 'https://open.spotify.com/episode/abc'"
        echo "  $0 'https://docs.google.com/document/d/xyz'"
        exit 1
    fi
    
    echo "Extracting content from: $url"
    
    if [[ "$url" =~ youtube\.com|youtu\.be ]]; then
        extract_youtube "$url"
    elif [[ "$url" =~ spotify\.com ]]; then
        extract_spotify "$url"
    else
        extract_web "$url"
    fi
}

function extract_youtube() {
    local url="$1"
    local video_id
    
    # Extract video ID for caching
    video_id=$(echo "$url" | sed -n 's/.*[?&]v=\([^&]*\).*/\1/p')
    if [[ -z "$video_id" ]]; then
        video_id=$(echo "$url" | sed -n 's/.*youtu\.be\/\([^?]*\).*/\1/p')
    fi
    
    local cache_file="$CONTENT_TEXT/youtube-$video_id.txt"
    
    # Check cache
    if [[ -f "$cache_file" ]]; then
        echo "✅ Found cached transcript: $cache_file"
        echo "$cache_file"
        return 0
    fi
    
    echo "📺 Downloading and transcribing YouTube video..."
    
    # Use configured script - it will save directly to content with smart filename
    "$YOUTUBE_SCRIPT" "$url" "$CONTENT_TEXT" "$video_id"
    
    if [[ -f "$cache_file" ]]; then
        echo "✅ YouTube transcript saved: $cache_file"
        echo "$cache_file"
    else
        echo "❌ Failed to create YouTube transcript"
        exit 1
    fi
}

function extract_spotify() {
    local url="$1"
    
    # Simple cache key based on URL hash
    local url_hash
    url_hash=$(echo "$url" | shasum -a 256 | cut -d' ' -f1 | cut -c1-12)
    local cache_file="$CONTENT_TEXT/spotify-$url_hash.txt"
    
    # Check cache
    if [[ -f "$cache_file" ]]; then
        echo "✅ Found cached transcript: $cache_file"
        echo "$cache_file"
        return 0
    fi
    
    echo "🎵 Downloading and transcribing Spotify content..."
    
    # Use configured script - it will save directly to content with smart filename
    "$SPOTIFY_SCRIPT" "$url" "$CONTENT_TEXT" "$CONTENT_AUDIO" "$ONTHESPOT_DIR" "$url_hash"
    
    if [[ -f "$cache_file" ]]; then
        echo "✅ Spotify transcript saved: $cache_file"
        echo "$cache_file"
    else
        echo "❌ Failed to create Spotify transcript"
        exit 1
    fi
}

function extract_web() {
    local url="$1"
    
    # Simple cache key based on URL hash
    local url_hash
    url_hash=$(echo "$url" | shasum -a 256 | cut -d' ' -f1 | cut -c1-12)
    local cache_file="$CONTENT_TEXT/web-$url_hash.txt"
    
    # Check cache
    if [[ -f "$cache_file" ]]; then
        echo "✅ Found cached content: $cache_file"
        echo "$cache_file"
        return 0
    fi
    
    echo "🌐 Extracting web content..."
    echo "Note: This will use Exa MCP when called from an AI agent"
    echo "For manual use, you could add curl/lynx extraction here"
    
    # Placeholder - this will be called by LLM with Exa MCP
    echo "To implement: Use Exa MCP to scrape content and save to $cache_file"
    echo "$cache_file"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 