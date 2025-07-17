# Tool Usage Guide

This file contains information about discovering and using tools available in your current environment.

## What are MCPs?

**Model Context Protocol (MCP)** is a standardized way for AI applications to connect to external tools and data sources. Think of it as "USB-C for AI" - a universal plug-and-play system that lets LLMs securely access databases, APIs, files, and services.

*For MCP setup, configuration, and troubleshooting, see `/Users/joe/Documents/Admin/Context/mcp.md`*

## Discovery-First Approach 🔍

**Important**: Tool availability is dynamic and context-dependent. Rather than maintaining static lists, **always check the actual configuration** for your current environment.

### How to Discover Your Current Tools

1. **Identify your client** from system prompts:
   - "You operate in Cursor" → Cursor
   - Desktop Commander available → Claude Desktop
   - Other indicators in your system prompt

2. **Check the actual config file**:
   ```bash
   # Cursor (check both global and project-specific)
   cat ~/.cursor/mcp.json
   cat .cursor/mcp.json  # Project-specific supplements
   
   # Claude Desktop
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # OpenWebUI
   cat ~/.local/openwebui/mcp-config.json
   ```

3. **Explore tool capabilities**:
   - Try calling tools to understand their actual capabilities
   - Use `--help` flags where available
   - Check web documentation for the latest features

### Config File Locations

| Client | Global Config | Project Config |
|--------|--------------|----------------|
| **Cursor** | `~/.cursor/mcp.json` | `.cursor/mcp.json` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | N/A |
| **OpenWebUI** | `~/.local/openwebui/mcp-config.json` | N/A |

## Living in Fast-Moving Times 🚀

We're in an era where AI capabilities evolve faster than documentation. Embrace this by:

1. **Using web search** for the latest information on tools, APIs, and best practices
2. **Experimenting freely** - try first, adjust based on results (Adam Grant style 😜)
3. **Reading actual configs** over static documentation
4. **Checking tool versions** and updating as needed

## Key Tool Usage Patterns

While specific tools vary, common patterns include:

- **Web Search (Exa)**: Use whenever current information would help
- **Task Management**: Work tasks → Linear | Personal → Todoist (when configured)
- **Documentation (Context7)**: Latest library docs for development
- **Database Access**: Check for postgres or other DB tools in your config

## Troubleshooting Approach

If I ask you to do something that seems impossible:

1. **Check available tools** in your current environment
2. **Read the actual config** to see what's configured
3. **Try calling the tool** to test capabilities
4. **Search the web** for latest documentation
5. **Experiment** with different approaches

Remember: Your training data might be outdated - the tools and their capabilities have likely evolved!

## For MCP Setup/Issues
**For MCP installation, configuration, and troubleshooting, see `/Users/joe/Documents/Admin/Context/mcp.md`**
