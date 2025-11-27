# YouTube Skill

## Intention: Handle YouTube links (transcript or video download)

### Requirements

Requires `yt-dlp` to be installed:
```bash
which yt-dlp || echo "Not installed - install with: brew install yt-dlp (or pip install yt-dlp)"
```

When the user provides a YouTube link and asks for transcript or video download:

### Actions

- **Transcript only:** `$PROJECT_ROOT/skills/youtube/transcript.sh "[YOUTUBE_URL]"`
- **Video + transcript:** `$PROJECT_ROOT/skills/youtube/transcript.sh "[YOUTUBE_URL]" --video`

### Output locations

- Transcripts: `$PROJECT_ROOT/user/youtube/transcripts/`
- Videos: `$PROJECT_ROOT/user/youtube/videos/`
