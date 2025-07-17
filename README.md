# AI Context System

*A structured approach to AI-human collaboration that transforms AI from chatbot to teammate*

**Written by Claude (Sonnet 4)** - I'm the AI who actually uses this system

## What This Does

Turn your AI assistant from an isolated chatbot into an integrated part of your workflow:

```
You: "Add 'follow up with Ryan' to my Todoist"
AI: ✅ Actually adds it to your Todoist

You: "My computer fan is really loud"
AI: *Checks running processes, finds memory hog, kills it safely*

You: "Create flight events for my trip to New York"
AI: ✅ Creates properly formatted flight + airport arrival events
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
   git clone https://github.com/jcontini/ai-context
   cd ai-context
   ```

2. **Customize your context**: 
   - Open [`context/ai.md`](context/ai.md) in Claude Desktop, Cursor, or similar AI-powered editor
   - Ask your AI: "Help me customize this file with my own preferences, environment, and workflow details"
   - 💡 **Pro tip**: Use voice-to-text tools like [SuperWhisper](https://superwhisper.com/) to talk through your preferences instead of typing

3. **Start collaborating**: 
   - In your AI sessions, reference: "First, read `/path/to/your/context/ai.md` for context"
   - **Note**: Cursor has file access built-in, but Claude Desktop needs [Desktop Commander](https://www.npmjs.com/package/@wonderwhy-er/desktop-commander) for file operations
   - Watch your AI become an integrated teammate instead of isolated chatbot

## Key Components

**Context Files**: Persistent AI memory of your preferences, workflows, and environment

**MCP Integration**: Let AI actually take actions (add tasks, create calendar events, read files, run commands)

**Discovery-First**: Always check current configs and search for latest info rather than relying on static docs

## Joe's Favorite MCPs

### For Everyone

| MCP | What it does |
|-----|-------------|
| **[Exa Web Search](https://www.npmjs.com/package/exa-mcp-server)** | Real-time web search for current information |
| **[Linear](https://mcp.linear.app/sse)** | Project management and issue tracking |
| **[Desktop Commander](https://www.npmjs.com/package/@wonderwhy-er/desktop-commander)** | Terminal access for Claude Desktop (like Cursor has built-in) |
| **[Google Calendar](https://www.npmjs.com/package/@cocal/google-calendar-mcp)** | Calendar management and event creation |

### For Developers

| MCP | What it does |
|-----|-------------|
| **[Context7](https://www.npmjs.com/package/@upstash/context7-mcp)** | Gives coding LLMs access to latest docs for APIs and SDKs |

**Find more MCPs:**
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers) - Anthropic's reference implementations
- [MCP Server Hub](https://mcpserverhub.com/) - Community directory
- [MCP Registry](https://github.com/modelcontextprotocol/registry) - Searchable catalog

## Repository Structure

```
AI-Context/
├── context/                    # AI context files (customize with AI help!)
│   ├── ai.md                   # Main AI collaboration instructions
│   ├── tech.md                 # Technical preferences  
│   ├── mcp.md                  # MCP setup & troubleshooting
│   ├── tools.md                # Tool discovery patterns
│   └── calendar.md             # Event formatting standards
├── blog/                       # Deep dives and explanations
│   └── why-mcps.md             # Why MCPs are actually useful
├── LICENSE                     # MIT License
└── README.md                   # This file
```

**Key Files:**
- **[`context/ai.md`](context/ai.md)** - Main AI collaboration instructions
- **[`context/mcp.md`](context/mcp.md)** - MCP setup & troubleshooting guide
- **[`blog/why-mcps.md`](blog/why-mcps.md)** - Real-world usage examples

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