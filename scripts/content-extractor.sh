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
    
    # Set defaults (relative to repo) - simplified single source of truth
    DOWNLOADS_BASE="$REPO_DIR/downloads"
    YOUTUBE_SCRIPT="$REPO_DIR/scripts/youtube-transcript.sh"
    SPOTIFY_SCRIPT="$REPO_DIR/scripts/spotify-transcript.sh"
    # Content organization within downloads
    DOWNLOADS_TEXT="$DOWNLOADS_BASE/text"     # All transcripts
    DOWNLOADS_AUDIO="$DOWNLOADS_BASE/audio"   # Audio files
    DOWNLOADS_VIDEO="$DOWNLOADS_BASE/video"   # Video files  
    # OnTheSpot defaults (will be determined by hybrid detection)
    ONTHESPOT_DIR=""  # Will be detected
    
    # Try to load from YAML config if yq is available
    if command -v yq >/dev/null 2>&1 && [[ -f "$CONFIG_FILE" ]]; then
        echo "📄 Loading AgentOS config from $CONFIG_FILE"
        
        # Get downloads base path
        local downloads_base
        downloads_base=$(yq eval '.base.downloads_base // "downloads"' "$CONFIG_FILE")
        DOWNLOADS_BASE="$REPO_DIR/$downloads_base"
        
        # Build content organization paths
        local text_dir audio_dir video_dir
        text_dir=$(yq eval '.content.text // "text"' "$CONFIG_FILE") 
        audio_dir=$(yq eval '.content.audio // "audio"' "$CONFIG_FILE")
        video_dir=$(yq eval '.content.video // "video"' "$CONFIG_FILE")
        
        DOWNLOADS_TEXT="$DOWNLOADS_BASE/$text_dir"
        DOWNLOADS_AUDIO="$DOWNLOADS_BASE/$audio_dir" 
        DOWNLOADS_VIDEO="$DOWNLOADS_BASE/$video_dir"
        
        # Script paths (relative to repo)
        local yt_script spotify_script
        yt_script=$(yq eval '.scripts.youtube_transcript // "scripts/youtube-transcript.sh"' "$CONFIG_FILE")
        spotify_script=$(yq eval '.scripts.spotify_transcript // "scripts/spotify-transcript.sh"' "$CONFIG_FILE")
        
        YOUTUBE_SCRIPT="$REPO_DIR/$yt_script"
        SPOTIFY_SCRIPT="$REPO_DIR/$spotify_script"
        
        # OnTheSpot hybrid installation detection
        local install_method brew_formula local_path manual_path download_path
        install_method=$(yq eval '.tools.spotify.install_method // "auto"' "$CONFIG_FILE")
        brew_formula=$(yq eval '.tools.spotify.brew_formula // "casual-snek/onthespot"' "$CONFIG_FILE")
        local_path=$(yq eval '.tools.spotify.local_path // "apps/onthespot"' "$CONFIG_FILE")
                 manual_path=$(yq eval '.tools.spotify.manual_path // "~/Applications/onthespot"' "$CONFIG_FILE" | sed "s|^~|$HOME|")
        
        # Determine OnTheSpot directory using hybrid pattern
        if [[ "$install_method" == "auto" ]]; then
            # Try brew first
            if command -v brew >/dev/null 2>&1 && brew list "$brew_formula" >/dev/null 2>&1; then
                ONTHESPOT_DIR="$(brew --prefix)/bin"
                echo "🍺 Using brew-installed OnTheSpot"
            # Try local path
            elif [[ -d "$REPO_DIR/$local_path" ]]; then
                ONTHESPOT_DIR="$REPO_DIR/$local_path"
                echo "📁 Using local OnTheSpot: $ONTHESPOT_DIR"
            # Fallback to manual path
            elif [[ -d "$manual_path" ]]; then
                ONTHESPOT_DIR="$manual_path"
                echo "⚠️  Using manual OnTheSpot install: $ONTHESPOT_DIR"
            else
                echo "❌ OnTheSpot not found. Will attempt auto-install when needed."
                ONTHESPOT_DIR=""
            fi
        elif [[ "$install_method" == "brew" ]]; then
            ONTHESPOT_DIR="$(brew --prefix)/bin"
        elif [[ "$install_method" == "local" ]]; then
            ONTHESPOT_DIR="$REPO_DIR/$local_path"
        elif [[ "$install_method" == "manual" ]]; then
            ONTHESPOT_DIR="$manual_path"
        fi
        
        
        
        echo "🏠 Repo: $REPO_DIR"
        echo "📁 Downloads: $DOWNLOADS_BASE"
    else
        if [[ ! -f "$CONFIG_FILE" ]]; then
            echo "⚠️  No config file found at $CONFIG_FILE, using defaults"
        elif ! command -v yq >/dev/null 2>&1; then
            echo "⚠️  yq not found. Install with: brew install yq"
            echo "   Using default settings for now"
        fi
        echo "🏠 Repo: $REPO_DIR (auto-detected)"
        echo "📁 Downloads: $DOWNLOADS_BASE (default)"
    fi
    
    # Ensure download directories exist
    mkdir -p "$DOWNLOADS_TEXT" "$DOWNLOADS_AUDIO" "$DOWNLOADS_VIDEO"
}

function main() {
    load_config
    
    local url="$1"
    local output_dir="${2:-$DOWNLOADS_TEXT}"
    
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
    
    local cache_file="$DOWNLOADS_TEXT/youtube-$video_id.txt"
    
    # Check cache
    if [[ -f "$cache_file" ]]; then
        echo "✅ Found cached transcript: $cache_file"
        echo "$cache_file"
        return 0
    fi
    
    echo "📺 Downloading and transcribing YouTube video..."
    
    # Use configured script - it will save directly to downloads with smart filename
    "$YOUTUBE_SCRIPT" "$url" "$DOWNLOADS_TEXT" "$video_id"
    
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
    local cache_file="$DOWNLOADS_TEXT/spotify-$url_hash.txt"
    
    # Check cache
    if [[ -f "$cache_file" ]]; then
        echo "✅ Found cached transcript: $cache_file"
        echo "$cache_file"
        return 0
    fi
    
    echo "🎵 Downloading and transcribing Spotify content..."
    
    # Use configured script - it will save directly to downloads with smart filename
    "$SPOTIFY_SCRIPT" "$url" "$DOWNLOADS_TEXT" "$DOWNLOADS_AUDIO" "$ONTHESPOT_DIR" "$url_hash"
    
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
    local cache_file="$DOWNLOADS_TEXT/web-$url_hash.txt"
    
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