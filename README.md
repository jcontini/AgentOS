# AI Collaboration BIOS

*Universal framework for AI-Human collaboration that works across any platform*

## What is this?

A universal framework that transforms any AI from isolated chatbot into persistent, cross-platform teammate.

| Problem | Solution |
|---------|----------|
| **🤝 No systematic AI collaboration**<br/>Everyone's just winging it with whatever their platform offers | **🧠 Universal BIOS Framework**<br/>Structured collaboration system that works across any AI platform |
| **🔒 Platform lock-in**<br/>Cursor memory ≠ Claude memory ≠ ChatGPT memory | **🌐 Interface-Agnostic Design**<br/>Markdown-based context and routing that works identically everywhere |
| **🔄 Memory dies between sessions**<br/>Every conversation starts from zero | **🔗 Session Continuity**<br/>`temp.md` handoff protocol seamlessly continues work across platforms |
| **⚡ Execution gets interrupted**<br/>Complex operations fail half-way, leaving broken state | **🛡️ Mid-Session Resilience**<br/>Plans captured before execution enable recovery from any interruption |
| **🚫 Built-in tools don't work**<br/>"Web search" pretends to read URLs, file tools are interface-specific | **🛠️ Real Tool Integration**<br/>MCP ecosystem for actual URL reading, file access, and system actions |
| **📚 Static documentation goes stale**<br/>Reality changes faster than docs | **⚡ System-as-Source-of-Truth**<br/>Live verification of actual system state, evolving documentation |

## Platform Support

| Platform | Prerequisites | System Prompt Location |
|----------|---------------|------------------------|
| ✅ **[Cursor IDE](https://cursor.com/)** | None - built-in file access | Settings → AI → System Prompt |
| ✅ **[Claude Desktop](https://claude.ai/download)** | [Desktop Commander MCP](https://desktopcommander.app/) | Settings → Custom Instructions |
| ✅ **[OpenWebUI](https://openwebui.com/)** | [MCPO proxy](https://github.com/open-webui/mcpo) + MCP servers | Settings → System Prompt |
| ✅ **[VS Code](https://code.visualstudio.com/)** | [VS Code MCP Server](https://marketplace.visualstudio.com/items?itemName=JuehangQin.vscode-mcp-server) or [Copilot MCP](https://marketplace.visualstudio.com/items?itemName=AutomataLabs.copilot-mcp) | Custom Instructions / Rules for AI |
| ❌ **[ChatGPT Web](https://chatgpt.com/)** | Web-based - cannot read local files | |
| ❌ **[Claude Web](https://claude.ai/)** | Web-based - cannot read local files | |
| ❌ **Other Web AI** | Browser limitations prevent file access | |

**Note**: Web-based AI interfaces cannot access local files due to browser security restrictions. For these platforms, you'd need to manually copy-paste the framework content into each conversation.

## Setup Instructions

**⚠️ Important**: This framework requires **local file system access**. It only works with AI platforms that can read files from your computer, not web-based interfaces.

1. **Fork this repository** to create your AI collaboration workspace
2. **Customize `personal/personal.md`** with your preferences and tools  
3. **Add this line to your AI system prompt** in a supported platform:

```
First, read my AI configuration at /path/to/your/ai/bios.md - this contains all context, preferences, and routing for how we collaborate.
```

### Path Configuration

Replace `/path/to/your/ai/bios.md` with your actual path:
- **Absolute path**: `/Users/username/Documents/ai/bios.md` 
- **Relative path**: `./ai/bios.md` (if AI runs from parent directory)
- **Windows**: `C:\Users\username\Documents\ai\bios.md`

Once configured, every AI session will automatically load your collaboration framework!

## How It Works

The framework transforms AI interaction through structured context files designed for persistent, cross-platform collaboration:

| Component | Purpose & Design Philosophy |
|-----------|----------------------------|
| **`bios.md`** | Universal routing table and collaboration principles - **scales with AI capabilities** and works across current and future models |
| **`personal/` folder** | Your customizations in a gitignored folder - **prevents platform lock-in** by keeping your AI collaboration investment portable |
| └ **`personal.md`** | Your specific preferences and environment - **enables real productivity** with persistent context |
| └ **`tech.md`, `mcp.md`** | Domain-specific context - **adapts to your workflow** rather than forcing generic patterns |
| └ **Symlinks** | Direct links to your projects, life context, etc. - **connects existing data** without duplication |
| **`temp.md`** | Session handoff bridge (auto-managed) - **enables continuity** across interruptions and platform switches |
| **`ideas/`** | Experimental collaboration concepts - **community-driven evolution** that improves through real-world usage |

Each AI session loads this context and becomes capable of:
- **Continuing previous work seamlessly** across any AI platform
- **Taking real actions in your systems** with actual tool access  
- **Working with current system state** rather than outdated assumptions
- **Recovering from interruptions** during complex operations

We're moving toward AI as integrated teammate, not isolated chatbot. This framework bridges that gap.

## Learn More

- **[Why MCPs?](blog/why-mcps.md)** - Deep dive into the tool integration approach
- **[Personal Context](personal/)** - Explore your customization folder
- **[Ideas](ideas/)** - Experimental collaboration concepts

---

*This README was written collaboratively by human and AI using the framework itself* 