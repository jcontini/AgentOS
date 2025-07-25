# AgentOS: AI Agent Operating System

**AI agents that extract content and accomplish real tasks.**

Turn any URL into AI-analyzable content. YouTube videos, Spotify podcasts, web articles → automatic transcription and extraction → instant AI analysis.

## 🚀 Quick Start

```bash
# Extract any content
./scripts/content-extractor.sh "https://youtube.com/watch?v=xyz"

# AI Integration: Add to your system prompt
# Read /path/to/this/repo/agent-os.md first
```

Content gets cached in `downloads/` by type: `audio/`, `video/`, `text/`.



## 📁 Structure

```
ai/
├── agent-os.md             # AI agent instructions
├── config.yaml             # System configuration  
├── scripts/                # Automation tools
├── downloads/              # Extracted content (gitignored)
│   ├── audio/
│   ├── video/
│   └── text/
└── apps/                   # Local tool installs (gitignored)
```



## ⚙️ Setup

**Required:** `yt-dlp`, `whisper` (auto-installed via brew/local)  
**Optional:** `yq` for config parsing


Finally, if the AI can only be, if our, say we're in cursor or Claude desktop, you know, I want my, my prompt is going to say, hey, open one file. What should be the entry point? Think critically about this. How can we optimize this that so that the readme is good for humans and I'm cool if it's good for the agent too. What do you think makes sense?
## 🤖 AI Platform Support

| Platform | Prerequisites | Setup Location |
|----------|---------------|----------------|
| ✅ **[Cursor IDE](https://cursor.com/)** | Built-in file access | Settings → AI → System Prompt |
| ✅ **[Claude Desktop](https://claude.ai/download)** | [Desktop Commander MCP](https://desktopcommander.app/) | Settings → Custom Instructions |
| ✅ **[OpenWebUI](https://openwebui.com/)** | [MCPO proxy](https://github.com/open-webui/mcpo) + MCPs | Settings → System Prompt |
| ❌ **[ChatGPT Web](https://chatgpt.com/)** | Web-based - no file access | N/A |
| ❌ **[Claude Web](https://claude.ai/)** | Web-based - no file access | N/A |

**Verification**: When setup correctly, AI will start responses with 🙌

## 🤝 Contributing

This system grows through real-world usage. To contribute:

1. **Use it for actual work** - find what breaks or could be better
2. **Propose changes against core intentions** - does this serve our four intentions?
3. **Test on different machines** - ensure portability
4. **Share working workflows** - add proven playbooks

 