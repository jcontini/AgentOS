# Spotify Transcription Playbook

## Overview
This playbook provides automated transcription of Spotify content (tracks, albums, playlists, podcasts) using OnTheSpot for downloading and OpenAI Whisper for speech-to-text conversion.

## Prerequisites
- **Spotify Premium Account** (required for OnTheSpot)
- **OnTheSpot** (Spotify downloader)
- **OpenAI Whisper** (speech-to-text)
- **FFmpeg** (audio processing)

## Installation & Setup

### OnTheSpot Installation (Build from Source - Recommended)
```bash
# Navigate to applications directory
cd /Users/joe/Applications

# Clone repository
git clone https://github.com/casualsnek/onthespot
cd onthespot

# Create isolated environment
python3 -m venv onthespot_env
source onthespot_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
cd src
python3 -m onthespot
```

### Quick Dependencies Install
```bash
# Install Whisper
pip install openai-whisper

# Install FFmpeg (if not already installed)
brew install ffmpeg
```

### OnTheSpot Configuration
1. Launch OnTheSpot: `python3 -m onthespot` (from source directory)
2. Go to **Configuration** tab
3. Add your Spotify Premium account credentials
4. Set download location and format preferences
5. Save settings

## Usage

### Automated Script
```bash
# Single track
/Users/joe/Documents/Admin/ai/scripts/spotify-transcript.sh "https://open.spotify.com/track/1TTxd0ZtQyTZ3e97xsPShH"

# Playlist (like Thomas Schramm Bible audiobook)
/Users/joe/Documents/Admin/ai/scripts/spotify-transcript.sh "https://open.spotify.com/playlist/37i9dQZF1E8UXBoz02kGID"

# Album
/Users/joe/Documents/Admin/ai/scripts/spotify-transcript.sh "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
```

### Manual Process
1. **Download Audio:**
   ```bash
   # Using OnTheSpot CLI
   onthespot-cli download "SPOTIFY_URL" --format mp3 --output-dir "./audio"
   
   # Or using source build
   cd /Users/joe/Applications/onthespot
   source onthespot_env/bin/activate
   python3 src/onthespot/cli.py download "SPOTIFY_URL"
   ```

2. **Transcribe with Whisper:**
   ```bash
   # Single file
   whisper "audio_file.mp3" --model medium --output_format txt --language en
   
   # Batch processing
   for file in *.mp3; do
       whisper "$file" --model medium --output_format txt --language en
   done
   ```

## Output Structure
```
/Users/joe/Documents/Reports/Spotify-transcripts/
├── audio/          # Downloaded MP3 files
└── text/           # Generated transcripts (.txt files)
```

## Whisper Model Options
- **tiny**: Fastest, lowest quality
- **base**: Good speed/quality balance
- **small**: Better quality, slower
- **medium**: Recommended balance ⭐
- **large**: Best quality, slowest

## Troubleshooting

### OnTheSpot Issues
- **Login Failed**: Ensure Premium account and correct credentials
- **Download Stuck at 99%**: Missing FFmpeg, install with `brew install ffmpeg`
- **Account Restricted**: Wait or try different account

### Whisper Issues
- **Out of Memory**: Use smaller model (`--model small`)
- **Wrong Language**: Specify language (`--language en`)
- **Poor Quality**: Try larger model (`--model large`)

### Script Issues
- **OnTheSpot Not Found**: Run the installation steps in script comments
- **Permission Denied**: Run `chmod +x spotify-transcript.sh`
- **No Audio Files**: Check OnTheSpot output directory

## Legal Considerations
- OnTheSpot accesses streams from your legitimate Premium account
- Intended for personal use and content you have legal access to
- Respect Spotify's Terms of Service
- Support artists by maintaining your Premium subscription

## Integration with AI Workflows

### For Bible Study (Thomas Schramm Example)
```bash
# Download entire Bible audiobook
./spotify-transcript.sh "https://open.spotify.com/playlist/PLAYLIST_ID"

# Result: 932 individual chapter transcripts for study and analysis
```

### For Podcast Analysis
```bash
# Download podcast episode
./spotify-transcript.sh "https://open.spotify.com/episode/EPISODE_ID"

# Use transcript for AI analysis, note-taking, etc.
```

## Performance Tips
- **Batch Processing**: Download full playlists rather than individual tracks
- **Quality Settings**: Use `medium` model for good speed/accuracy balance
- **Storage**: Monitor disk space for large playlists (Bible = ~24GB audio)
- **Parallel Processing**: OnTheSpot supports multiple download workers

## Security Notes
- Build from source for maximum security and transparency
- Inspect code before running: `cat src/onthespot/__main__.py`
- Use isolated Python environment for dependencies
- Verify Git repository authenticity before cloning

## Future Enhancements
- [ ] Add support for determining Bible translation from metadata
- [ ] Implement chapter-by-chapter analysis
- [ ] Add progress indicators for large playlists
- [ ] Create summary reports of transcribed content
