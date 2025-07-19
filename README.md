# AI BIOS

*Universal framework for AI-Human collaboration that works across any platform*

## What is this?

A universal framework that transforms any AI from isolated chatbot into persistent, cross-platform teammate.

| Problem | Solution |
|---------|----------|
| **🔒 Platform lock-in**<br/>Cursor memory ≠ Claude memory ≠ ChatGPT memory | **🌐 Interface-Agnostic Design**<br/>Markdown-based context that works identically everywhere |
| **🤷 AI doesn't have relevant context**<br/>Every conversation starts without knowledge of your environment, preferences, or workflow | **🗺️ Routing Tables**<br/>Persistent markdown files that build context over time |
| **🎲 AI does things unpredictably**<br/>Same tasks executed differently each time, missed steps, inconsistent outcomes | **📋 BIOS Instructions**<br/>Explicit workflows with decision points and status indicators |
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
2. **Customize `user.md`** with your preferences and tools  
3. **Add this line to your AI system prompt** in a supported platform:

**Note**: Replace `/path/to/your/ai/bios.md` with your actual path!
```
First, read my AI configuration at /path/to/your/ai/bios.md - this contains all context, preferences, and routing for how we collaborate.
```

Once configured, every AI session will automatically load your collaboration framework!

## Verification

**How to know it's working**: When you start a new AI session, if the framework is properly configured, the AI will begin its first response with the hands emoji: 🙌

If you don't see the hands emoji in the AI's first response, this indicates the framework isn't loading. Common troubleshooting steps:
- Verify the file path in your system prompt is correct and absolute (not relative)
- Ensure the AI platform has proper file system access permissions
- Check that `bios.md` exists at the specified path

## How It Works

The framework transforms AI interaction through structured context files designed for persistent, cross-platform collaboration:

| Component | Purpose & Design Philosophy |
|-----------|----------------------------|
| **`bios.md`** | Universal routing table and collaboration principles - **scales with AI capabilities** and works across current and future models |
| **`tools.md`** | Tool discovery and MCP troubleshooting - **universal approach** to maintaining cross-platform compatibility |
| **`user.md`** | Your specific preferences and environment - **enables real productivity** with persistent context |
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
- **[User Profile](user.md)** - Your collaboration profile and preferences (note: this is Joe's sample file - customize for your own use)
- **[Ideas](ideas/)** - Experimental collaboration concepts

---

*This README was written collaboratively by human and AI using the framework itself* 