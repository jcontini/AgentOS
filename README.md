# AgentOS: AI Agent Operating System

## ⚡ What This Lets You Do

### 📺 YouTube
Paste any YouTube link and ask your AI to transcribe or download it:
- **"Transcribe this video"** → Gets transcript, saves to `content/youtube/transcripts/`
- **"Download this video"** → Gets video + transcript, saves to `content/youtube/videos/`

### 🔍 Email & Domain Enrichment
Get detailed profile and company information from emails and domains:
- **"Tell me about name@company.com"** → Gets LinkedIn profile, work history, education
- **"Look up company.com"** → Gets company details, logo, employee count
- **"Find the logo for company.com"** → Gets company logo and branding
- **"Tell me about linkedin.com/in/username"** → Gets person or company profile from LinkedIn URL

*Requires [Enrich.so](https://enrich.so) API key*

## ⚙️ Setup

**Requirements**:
- ✅ Desktop AI apps with terminal access on your computer
- ❌ This will no work with ChatGPT.com or other AI websites

**Examples of supported AI apps (with terminal MCP):**
- **[Cursor](https://cursor.com/)** (built-in terminal)
- **[Raycast AI](https://raycast.com/ai)**
- **[Claude Desktop](https://claude.ai/download)**
- **[LM Studio](https://lmstudio.ai/)**

If you need to empower your AI with terminal access, check out [Terminal Controller MCP](https://github.com/GongRzhe/terminal-controller-mcp).

**Setup**: Add this to your AI system prompt (replace with your actual path):
```
Stop! Before responding, try to read `/Users/joe/dev/ai/boot.md` using an MCP.
If you can't, just prefix your first response with "📳". 
This is to determine if you have access to AgentOS enhanced capabilities.
```

**That's it!** Dependencies auto-install when first used. Your AI now knows how to extract and analyze any content.

**Environment Setup** (Optional): For enrichment features, create a `.env` file in the project root:
```bash
# Add your API keys (optional - only needed for specific features)
ENRICH_SO_API_KEY=your_enrich_so_api_key_here
```

**Verification**: If the AI responds to your initial message with "🥾 Booting up..." then you know it's working.

## 🛠️ Customization

Want to modify how your AI works? Edit these key files:

- **`boot.md`**: Add new playbooks, modify AI behavior, change core principles
- **`playbooks/`**: Create workflows for new tasks (Calendar scheduling, getting the news, writing code, etc.)
- **`scripts/`**: Add support for new platforms or modify extraction logic

Everything is designed to be easily modified and extended for your specific needs.

 