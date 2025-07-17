# AI Context System

*A structured approach to AI-human collaboration that transforms AI from chatbot to teammate*

**Written by Claude (Sonnet 4)** - I'm the AI who actually uses this system

## What This Does

Turn your AI assistant from an isolated chatbot into an integrated part of your workflow:

```
You: "Add 'follow up with Sarah' to my ai-tasks list"
AI: ✅ Actually adds it to your Todoist

You: "My network seems slow, can you check?"  
AI: *Reads your actual network config and diagnoses the issue*

You: "Create a Linear issue for refactoring auth"
AI: ✅ Creates the issue with proper labeling and assignment
```

**Key insight**: MCPs + persistent context = AI that takes action in your actual systems, not just gives advice.

→ **[See real examples of how this works](blog/why-mcps.md)**

## Prerequisites

- **[Claude Desktop](https://claude.ai/)** or **[Cursor](https://cursor.sh/)** (for MCP support - web versions can't do this)
- macOS/Linux/Windows with terminal access
- Basic familiarity with configuration files
- The productivity apps you want to integrate (Todoist, Linear, etc.)

## Quick Setup

1. **Clone this repository**: 
   ```bash
   git clone https://github.com/your-username/ai-context
   cd ai-context
   ```

2. **Customize your context**: 
   - Open `context/ai.md` in Claude Desktop, Cursor, or similar AI-powered editor
   - Ask your AI: "Help me customize this file with my own preferences, environment, and workflow details"
   - 💡 **Pro tip**: Use voice-to-text tools like [SuperWhisper](https://superwhisper.com/) to talk through your preferences instead of typing

3. **Configure MCPs**: 
   - Follow `context/mcp.md` for step-by-step MCP setup
   - Install the specific MCPs for tools you use

4. **Start collaborating**: 
   - In your AI sessions, reference: "First, read `/path/to/your/context/ai.md` for context"
   - Watch your AI become an integrated teammate instead of isolated chatbot

## Repository Structure

```
AI-Context/
├── context/        # AI context files (customize with AI help!)
│   ├── ai.md       # Main AI collaboration instructions
│   ├── tech.md     # Technical preferences  
│   ├── mcp.md      # MCP setup & troubleshooting
│   ├── tools.md    # Tool discovery patterns
│   └── calendar.md # Event formatting standards
├── blog/           # Deep dives and explanations
│   └── why-mcps.md # Why MCPs are actually useful
├── LICENSE         # MIT License
└── README.md       # This file
```

## Key Components

**Context Files**: Persistent AI memory of your preferences, workflows, and environment

**MCP Integration**: Let AI actually take actions (add tasks, create calendar events, read files, run commands)

**Discovery-First**: Always check current configs and search for latest info rather than relying on static docs

## Learn More

- **[Why MCPs Are Actually Useful](blog/why-mcps.md)** - The productivity superpowers you're missing
- **[MCP Documentation](https://modelcontextprotocol.io)** - Official Model Context Protocol docs

## Contributing

This system improves through real-world usage! If you develop new patterns, MCP integrations, or context strategies that work well, please share them via issues or PRs.

**Particularly valuable contributions**:
- New MCP configurations for popular tools
- Context file templates for specific workflows
- Troubleshooting guides for common setup issues

## License

MIT License - feel free to adapt this system to your needs.

---

*This system was developed through months of iteration between Joe and me (Claude). The goal: push the boundaries of AI-human collaboration.* 