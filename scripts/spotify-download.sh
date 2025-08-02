#!/bin/bash

# Spotify Download Script using OnTheSpot
# Downloads Spotify tracks/playlists and stores them in configured audio directory

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if URL is provided
if [ $# -eq 0 ]; then
    print_error "No Spotify URL provided"
    echo "Usage: $0 <spotify-url>"
    echo "Example: $0 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'"
    exit 1
fi

SPOTIFY_URL="$1"

# Validate Spotify URL
if [[ ! "$SPOTIFY_URL" =~ ^https://open\.spotify\.com/(track|album|playlist|artist)/ ]]; then
    print_error "Invalid Spotify URL. Must be a Spotify track, album, playlist, or artist URL."
    exit 1
fi

print_status "Processing Spotify URL: $SPOTIFY_URL"

# Get script directory and navigate to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

# Read audio storage path from config.yaml
if [ ! -f "config.yaml" ]; then
    print_error "config.yaml not found in repo root"
    exit 1
fi

# Extract audio path from config.yaml (assuming standard YAML structure)
AUDIO_PATH=$(grep -A 10 "content:" config.yaml | grep "audio:" | sed 's/.*audio:[[:space:]]*//' | sed 's/[[:space:]]*#.*//' | tr -d '"' | tr -d "'")

if [ -z "$AUDIO_PATH" ]; then
    print_error "Could not find audio path in config.yaml"
    exit 1
fi

print_status "Audio storage path: $AUDIO_PATH"

# Create audio directory if it doesn't exist
mkdir -p "$AUDIO_PATH"

# Function to check if OnTheSpot is installed
check_onthespot_installed() {
    # Check if virtual environment exists and has OnTheSpot
    local venv_path="content/apps/onthespot-env"
    if [ -f "$venv_path/bin/activate" ]; then
        source "$venv_path/bin/activate"
        if python -c "import onthespot" &> /dev/null; then
            return 0
        fi
    fi
    
    # Check system-wide installation as fallback
    if command -v onthespot &> /dev/null; then
        return 0
    elif python3 -c "import onthespot" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to install OnTheSpot
install_onthespot() {
    print_status "OnTheSpot not found. Installing in virtual environment..."
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python first."
        exit 1
    fi
    
    # Create virtual environment in content/apps
    local venv_path="content/apps/onthespot-env"
    
    print_status "Creating virtual environment at $venv_path..."
    mkdir -p "content/apps"
    python3 -m venv "$venv_path"
    
    # Install OnTheSpot in virtual environment
    print_status "Installing OnTheSpot from GitHub..."
    source "$venv_path/bin/activate"
    pip install git+https://github.com/justin025/onthespot
    
    if [ $? -eq 0 ]; then
        print_success "OnTheSpot installed successfully in virtual environment"
    else
        print_error "Failed to install OnTheSpot"
        exit 1
    fi
}

# Function to check if ffmpeg is available
check_ffmpeg() {
    if command -v ffmpeg &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to open OnTheSpot for configuration
configure_onthespot() {
    print_warning "OnTheSpot needs to be configured with your Spotify credentials."
    print_status "Opening OnTheSpot GUI for initial setup..."
    
    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│                    SETUP REQUIRED                      │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ OnTheSpot will open automatically. Please:             │"
    echo "│                                                         │"
    echo "│ 1. Connect your Spotify account                        │"
    echo "│ 2. Follow the setup instructions                       │"
    echo "│ 3. Close OnTheSpot when setup is complete              │"
    echo "│ 4. Run this script again to download                   │"
    echo "│                                                         │"
    echo "│ Opening OnTheSpot GUI now...                           │"
    echo "└─────────────────────────────────────────────────────────┘"
    echo ""
    
    # Activate virtual environment if it exists
    local venv_path="content/apps/onthespot-env"
    if [ -f "$venv_path/bin/activate" ]; then
        source "$venv_path/bin/activate"
    fi
    
    # Try to open OnTheSpot GUI
    local abs_gui="$REPO_ROOT/content/apps/onthespot-env/bin/onthespot-gui"
    if [ -f "$abs_gui" ]; then
        "$abs_gui" &
    elif command -v onthespot-gui &> /dev/null; then
        onthespot-gui &
    else
        print_error "OnTheSpot GUI not found after install attempt"
        exit 1
    fi
    
    OTS_PID=$!
    
    echo ""
    print_status "OnTheSpot is running (PID: $OTS_PID)"
    print_status "Please complete Spotify setup in the GUI, then run this script again."
    print_status "Script will exit now to allow GUI setup..."
    
    # Exit to let user configure, they can run script again after setup
    exit 0
}

# Function to download using OnTheSpot CLI
download_spotify_content() {
    local url="$1"
    local output_dir="$2"
    
    print_status "Starting download from Spotify..."
    
    # Check ffmpeg availability (optional for post-processing)
    local has_ffmpeg=false
    if check_ffmpeg; then
        print_success "ffmpeg available for audio processing"
        has_ffmpeg=true
    else
        print_warning "ffmpeg not available - will download in original format"
    fi
    
    # Activate virtual environment if it exists
    local venv_path="content/apps/onthespot-env"
    if [ -f "$venv_path/bin/activate" ]; then
        source "$venv_path/bin/activate"
    fi
    
    # Use OnTheSpot CLI with absolute path
    local cmd=""
    local abs_cli="$REPO_ROOT/content/apps/onthespot-env/bin/onthespot-cli"
    if [ -f "$abs_cli" ]; then
        cmd="$abs_cli"
    elif command -v onthespot-cli &> /dev/null; then
        cmd="onthespot-cli"
    else
        print_error "OnTheSpot CLI not accessible"
        return 1
    fi
    
    # Change to output directory and run download
    print_status "Executing: $cmd --download '$url'"
    cd "$output_dir"
    
    if $cmd --download "$url"; then
        print_success "Download completed successfully"
        cd - > /dev/null
        return 0
    else
        print_error "Download failed"
        cd - > /dev/null
        return 1
    fi
}

# Main execution flow
main() {
    print_status "Starting Spotify download process..."
    
    # Check if OnTheSpot is installed
    if ! check_onthespot_installed; then
        install_onthespot
    else
        print_success "OnTheSpot is already installed"
    fi
    
    # Try to download directly - if it fails due to config, we'll handle it
    if download_spotify_content "$SPOTIFY_URL" "$AUDIO_PATH"; then
        print_success "Spotify content downloaded to: $AUDIO_PATH"
        
        # List downloaded files
        print_status "Downloaded files:"
        find "$AUDIO_PATH" -type f \( -name "*.mp3" -o -name "*.ogg" -o -name "*.m4a" -o -name "*.flac" -o -name "*.wav" \) 2>/dev/null | tail -10 || {
            print_status "Checking for any audio files..."
            find "$AUDIO_PATH" -type f 2>/dev/null | head -10
        }
    else
        print_error "Failed to download Spotify content"
        print_status "This might be due to missing Spotify credentials."
        print_status "Opening OnTheSpot GUI for setup..."
        configure_onthespot
    fi
}

# Run main function
main

print_success "Spotify download script completed"
