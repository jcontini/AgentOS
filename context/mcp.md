# MCP (Model Context Protocol) Setup & Troubleshooting Guide

## Universal Quick Reference

**Core Debugging Commands (All Platforms):**
```bash
node --version              # Check Node.js version
which npx                   # Check npx location
tail -f ~/Library/Logs/Claude/mcp*.log  # View logs
npx @modelcontextprotocol/inspector [server-path-or-url]  # Test server
```

**Platform Config Locations:**
| Platform | Config File | Extensions/Additional |
|----------|-------------|----------------------|
| **Cursor** | `~/.cursor/mcp.json` (global)<br/>`.cursor/mcp.json` (project) | - |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | `~/Library/Application Support/Claude/extensions-installations.json`<br/>`~/Library/Application Support/Claude/Claude Extensions/` |
| **OpenWebUI** | `~/.local/openwebui/mcp-config.json` | - |

## Debugging Workflow (Universal)

1. **Check current state**:
   ```bash
   cat [relevant config file from table above]
   node --version
   tail ~/Library/Logs/Claude/mcp.log
   ```

2. **Search for latest info**: Use web search for current solutions

3. **Test incrementally**: Disable all MCPs except one, add back gradually

4. **Experiment**: Try variations based on error messages

## Common Issues & Quick Fixes

| Issue | Symptoms | First Try | Then Search For |
|-------|----------|-----------|-----------------|
| **Node.js compatibility** | "symbol to string" errors | Check `node --version` | "MCP node version requirements [current year]" |
| **PATH problems** | "spawn ENOENT" | Add full PATH to env | "MCP PATH configuration" |
| **Auth failures** | HTTP 401 | Add `--debug` flag | "[MCP name] authentication setup" |
| **Server disconnects** | Process exits | Check logs, restart client | "MCP server timeout issues" |

## Config Patterns (Verify with Latest Docs!)

**Universal Environment Setup:**
- Store API keys in `env` section
- Use absolute paths for Node/NPX when possible
- Include comprehensive PATH in env variables

**Common Command Patterns:**
- **Remote SSE**: `["npx", "-y", "mcp-remote", "https://endpoint/sse", "--debug"]`
- **Local scripts**: `["node", "/absolute/path/to/script.js"]`
- **NPX packages**: `["npx", "-y", "package-name"]`

## Platform-Specific Commands

### Claude Desktop
```bash
# List traditional MCP servers
jq '.mcpServers | keys' ~/Library/Application\ Support/Claude/claude_desktop_config.json

# List DXT extensions
jq '.extensions | keys' ~/Library/Application\ Support/Claude/extensions-installations.json
jq -r '.extensions[] | "\(.id // "N/A") - v\(.version // "N/A")"' ~/Library/Application\ Support/Claude/extensions-installations.json

# Extension directories
ls ~/Library/Application\ Support/Claude/Claude\ Extensions/
```

### DXT Extensions Overview
**What**: One-click packaged MCP servers (.dxt files) with bundled dependencies
**vs Traditional**: No manual JSON config or Node.js setup required
**Coexistence**: Both DXT and traditional MCP servers can run simultaneously

## Recovery Procedure

**When MCPs break:**
1. **Check what changed** - OS update? Node version? Config edit?
2. **Read actual error** - Often contains the fix
3. **Search for solution** - Use web search + error message + "MCP" + current year
4. **Test one MCP** - Isolate the problem
5. **Try alternatives** - Different Node version, different approach

## Living Documentation 🚀

**Important**: This guide contains patterns that worked at time of writing. Always:
1. **Search the web** for latest MCP documentation and best practices
2. **Check actual versions** - Requirements change frequently
3. **Read error messages carefully** - They often contain the solution
4. **Experiment with solutions** - The ecosystem evolves rapidly

## Resources

- **Search terms**: "MCP setup latest", "MCP debugging current", "[specific MCP] configuration [current year]"
- **Official docs**: https://modelcontextprotocol.io
- **DXT Documentation**: https://github.com/anthropics/dxt
- **Node.js management**: `nvm` for version switching

**Best troubleshooting resource**: Web search for your specific error message + "MCP" + current year!