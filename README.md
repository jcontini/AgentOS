# AgentOS: AI Agent Operating System

**AI agents that extract content and accomplish real tasks.**

Transform any content into AI-analyzable format. YouTube videos, Spotify podcasts, web articles → automatic transcription and extraction → instant AI analysis. Plus a complete framework for AI agent behavior, principles, and workflows.

## 🔄 How It Works

### **AI Agent Workflow**
1. **Boot Sequence**: AI reads `boot.md` to understand core intentions, principles, and available playbooks
2. **Task Recognition**: AI matches user requests to role-specific playbooks 
3. **Content Processing**: When content analysis is needed, AI calls `./scripts/content-extractor.sh "URL"`
4. **Analysis**: AI reads extracted content from `content/` and provides analysis

### **Folder Structure & Purpose**
- **`playbooks/`**: Proven workflows for common tasks (MCP installation, code development, etc.)
- **`scripts/`**: Automation tools that handle technical complexity (content extraction, transcription)
- **`content/`**: All user-generated content (`audio/`, `video/`, `text/`, `apps/`) - yours to keep or manage as needed
- **`boot.md`**: Complete AI agent operating instructions - the single entry point for understanding the system

### **The Key Insight**
Instead of explaining your preferences every conversation, AI agents read `boot.md` once and understand how to work with your system. Content extraction happens automatically when needed. Everything stays portable and under your control.

## ⚙️ Setup

**No manual setup required!** Scripts auto-install dependencies when first run:
- **OnTheSpot**: Auto-installs via brew or local git clone
- **Whisper**: Provides install instructions if missing (`pip install openai-whisper`)
- **yt-dlp**: Provides install instructions if missing (`pip install yt-dlp`)
- **FFmpeg**: Provides install instructions if missing (`brew install ffmpeg`)

**Optional customization**: Edit `config.yaml` to customize paths, quality settings, etc. Scripts work with sensible defaults without any changes.

## 🤖 AI Platform Support

| Platform | Prerequisites | Setup Location |
|----------|---------------|----------------|
| ✅ **[Cursor IDE](https://cursor.com/)** | Built-in file access | Settings → AI → System Prompt |
| ✅ **[Claude Desktop](https://claude.ai/download)** | [Desktop Commander MCP](https://desktopcommander.app/) | Settings → Custom Instructions |
| ✅ **[OpenWebUI](https://openwebui.com/)** | [MCPO proxy](https://github.com/open-webui/mcpo) + MCPs | Settings → System Prompt |
| ❌ **[ChatGPT Web](https://chatgpt.com/)** | Web-based - no file access | N/A |
| ❌ **[Claude Web](https://claude.ai/)** | Web-based - no file access | N/A |

**Setup Instructions**: Add this to your AI system prompt:
```
🛑 STOP! Tell user: "🥾 Booting up..."
Read `/Users/joe/Documents/ai/boot.md` before responding to their query.
```

**Verification**: When setup correctly, AI will start responses with 🥾

## 🎭 Core Philosophy

AgentOS follows four core intentions:

1. **Agent Empowerment**: AI agents should accomplish real tasks, not just provide information
2. **User Sovereignty**: Users should own and control their AI infrastructure  
3. **Practical Implementation**: Working solutions over theoretical frameworks
4. **Content Liberation**: Any content should be analyzable by AI immediately

Every feature, principle, and workflow serves these intentions.

## 🤝 Contributing

This system grows through real-world usage. To contribute:

1. **Use it for actual work** - find what breaks or could be better
2. **Propose changes against core intentions** - does this serve our four intentions?
3. **Test on different machines** - ensure portability
4. **Share working workflows** - add proven playbooks

## 📋 License

MIT License - Use freely, modify as needed, make it your own.

 