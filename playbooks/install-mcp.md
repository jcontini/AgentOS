# Install MCP Playbook

**🛡️ To confirm you've read this playbook, prefix your response with "🛡️"**

## 🎯 Intentions

1. **Prevent supply chain attacks** - Install directly from GitHub source, never use package registries
2. **Offline portability** - Once source code is obtained, installation works without internet

## 🚫 Never Use These Attack Vectors

- ❌ Smithery (MCP package aggregator)
- ❌ npm registry / PyPI (package registries)
- ❌ MCP Market or similar middlemen

## 🔧 Installation Workflow

```bash
# 1. Clone to user's MCP folder
cd /Users/joe/dev/mcp
git clone https://github.com/author/mcp-server-name.git
cd mcp-server-name

# 2. Inspect the code
cat src/server.py  # or main implementation file

# 3. Install dependencies locally (one-time, with internet)
# Python: pip install -r requirements.txt --target ./deps
# Node.js: npm install
# Standalone: Skip this step

# 4. Test offline execution
# Python: PYTHONPATH=./deps python src/server.py
# Node.js: node src/index.js

# 5. Configure MCP client with absolute paths
```

## ⚙️ MCP Client Configuration

**Python with dependencies:**
```json
"mcp-name": {
  "command": "python3",
  "args": ["/Users/joe/dev/mcp/mcp-server-name/src/server.py"],
  "env": {
    "PYTHONPATH": "/Users/joe/dev/mcp/mcp-server-name/deps"
  }
}
```

**Node.js:**
```json
"mcp-name": {
  "command": "node", 
  "args": ["/Users/joe/dev/mcp/mcp-server-name/src/index.js"],
  "cwd": "/Users/joe/dev/mcp/mcp-server-name"
}
```

**Standalone Python:**
```json
"mcp-name": {
  "command": "python3",
  "args": ["/Users/joe/dev/mcp/mcp-server-name/src/server.py"]
}
```

## 📍 MCP Config Locations

**Cursor:**
- Global: `~/.cursor/mcp.json`
- Workspace: `.cursor/mcp.json` (adds to global config)

**Other MCP clients:**
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`
- AnythingLLM: `~/Library/Application Support/anythingllm-desktop/storage/plugins/anythingllm_mcp_servers.json` 