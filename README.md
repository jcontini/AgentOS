# AgentOS: AI Agent Operating System

## ⚡ What This Lets You Do

### 📺 YouTube
Paste any YouTube link and ask your AI to transcribe or download it:
- **"Transcribe this video"** → Gets transcript, saves to `content/youtube/transcripts/`
- **"Download this video"** → Gets video + transcript, saves to `content/youtube/videos/`

## ⚙️ Setup

**Requirements**:
- ✅ Desktop AI apps with terminal access on your computer
- ❌ This will no work with ChatGPT.com or other AI websites

**Examples of supported AI apps:**
- **[Cursor IDE](https://cursor.com/)** (built-in terminal)
- **[Claude Desktop](https://claude.ai/download)** (with MCP)
- **[LM Studio](https://lmstudio.ai/)** (with MCP)

If you need to empower your AI with terminal access, check out [Desktop Commander MCP](https://desktopcommander.app/).

**Setup**: Add this to your AI system prompt (replace with your actual path):
```
🛑 STOP! Respond "🥾 Booting up..."
WORKING_DIR=/Users/joe/dev/ai
Use a tool to read `boot.md` in the working dir before responding.
When running a script, run `cd {WORKING_DIR} && ./scripts/{script w params}`
```

**That's it!** Dependencies auto-install when first used. Your AI now knows how to extract and analyze any content.

**Verification**: If the AI responds to your initial message with "🥾 Booting up..." then you know it's working.

## 🛠️ Customization

Want to modify how your AI works? Edit these key files:

- **`boot.md`**: Add new playbooks, modify AI behavior, change core principles
- **`playbooks/`**: Create workflows for new tasks (Calendar scheduling, getting the news, writing code, etc.)
- **`scripts/`**: Add support for new platforms or modify extraction logic

Everything is designed to be easily modified and extended for your specific needs.

 