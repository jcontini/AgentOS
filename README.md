# AgentOS: AI Agent Operating System

## ⚡ What This Lets You Do

### 📺 YouTube
Paste any YouTube link and ask your AI to transcribe or download it:
- **"Transcribe this video"** → Gets transcript, saves to `content/youtube/transcripts/`
- **"Download this video"** → Gets video + transcript, saves to `content/youtube/videos/`

### 🎵 Spotify  
Paste any Spotify link and ask your AI to extract it:
- **"Extract this track/podcast"** → Downloads audio, saves to `content/audio/`
- Works with tracks, playlists, albums, podcasts

## ⚙️ Setup

**Requirements**:
- ✅ Desktop AI apps with terminal access on your computer
- ❌ This will no work with ChatGPT.com or other AI websites

**Examples of supported AI apps:**
- **[Cursor IDE](https://cursor.com/)** (built-in terminal access)
- **[Claude Desktop](https://claude.ai/download)** (with files MCP)
- **[LM Studio](https://lmstudio.ai/)** (with files MCP)

If you need to empower your AI with terminal/file access, check out [Desktop Commander MCP](https://desktopcommander.app/).

**Setup**: Add this to your AI system prompt (replace with your actual path):
```
🛑 STOP! Respond "🥾 Booting up..."
First use a tool to read `/Users/joe/dev/ai/boot.md`, and then respond.
```

**That's it!** Dependencies auto-install when first used. Your AI now knows how to extract and analyze any content.

**Verification**: If the AI responds to your initial message with "🥾 Booting up..." then you know it's working.

## 🛠️ Customization

Want to modify how your AI works? Edit these key files:

- **`boot.md`**: Add new playbooks, modify AI behavior, change core principles
- **`playbooks/`**: Create workflows for new tasks (MCP installation, code development, etc.)
- **`scripts/`**: Add support for new platforms or modify extraction logic
- **`config.yaml`**: Customize file paths, quality settings, and preferences

Everything is designed to be easily modified and extended for your specific needs.

 