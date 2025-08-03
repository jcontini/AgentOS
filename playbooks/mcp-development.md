# MCP Development, Testing & Debugging Playbook

Comprehensive guide for developing, testing, and debugging Model Context Protocol (MCP) servers based on proven patterns and user preferences.

**📚 To confirm you've read this playbook, prefix your response with "📚"**

## 🎯 Core Philosophy

**Simplicity First**: Default to minimal, single-file approaches until complexity genuinely demands modularization. The people MCP (`hobbies/ppl-mcp/src/index.ts`) is the gold standard - everything in one clean file.

**Tool-Centric Design**: Prefer tools over resources. Current MCP clients (Cursor, Claude Desktop, LM Studio) have poor resource support, and tools provide better discoverability and functionality.

**Modern Stack**: Always use latest versions and modern best practices.

**Iterative Development**: Build → Test → Debug → Fix → Repeat - integrate testing and debugging as core parts of development workflow.

## 📁 Project Structure (Preferred)

```
project-name-mcp/
├── src/
│   └── index.ts          # Everything goes here
├── test/
│   └── testing.md        # Testing protocols only
│   └── results/          # Test results (optional)
├── package.json
├── tsconfig.json
├── .gitignore            # Comprehensive AI tool + development ignores
├── README.md
└── .cursor/mcp.json      # Development config
```

**Anti-pattern**: Avoid complex folder structures with separate `/tools`, `/resources`, `/api` folders unless absolutely necessary.

## 🛠️ Technical Standards

### Dependencies
- **MCP SDK**: `@modelcontextprotocol/sdk` (latest)
- **TypeScript**: Modern configuration (strict mode optional)
- **Testing**: Include tests with real MCP client validation

### Code Structure (Single File Pattern)
```typescript
#!/usr/bin/env node

// 1. Imports
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
// ... other imports

// 2. Main Server Class
class YourMCPServer {
  private server: Server;
  // Initialize everything in constructor
  
  // 3. Tool Handlers (private methods)
  private async handleToolOne(args: any): Promise<any> { }
  private async handleToolTwo(args: any): Promise<any> { }
  
  // 4. Setup & Run
  private setupToolHandlers(): void { }
  async run(): Promise<void> { }
}

// 5. Startup
const server = new YourMCPServer();
server.run().catch(console.error);
```

### Tool Design Principles
- **Descriptive names**: `create_provider`, `search_people` not `create`, `search`
- **Rich schemas**: Include helpful descriptions and examples
- **Proper validation**: Check required parameters early
- **Meaningful errors**: Return helpful error messages
- **Consistent responses**: Use standard success/error format

## 🔧 Development Environment Setup

### 1. Research Latest Docs
Before starting, use Context7 MCP to get latest documentation for any libraries/frameworks used.

### 2. AI Coding Tool Configuration

Different AI coding tools use different permission/approval systems. Configure based on your tool:

#### Claude Code - Self-Bootstrapping Permissions Strategy

**Preferred Approach**: Start by asking user for minimal bootstrap permissions, then self-configure:

1. **Initial Ask**: Request only `Edit(.claude/settings.local.json)` and `Write(.claude/settings.local.json)`
2. **Self-Bootstrap**: Use those permissions to grant yourself full development permissions
3. **Full Development**: Continue with complete autonomy

**Full Permissions Template** (`.claude/settings.local.json`):
```json
{
  "permissions": {
    "allow": [
      "Edit(*)",
      "Write(*)",
      "WebFetch(domain:*)",
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(git:*)",
      "Bash(mkdir:*)",
      "Bash(rm:*)",
      "Bash(curl:*)",
      "Bash(tree:*)",
      "Bash(find:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(pwd:*)"
    ],
    "deny": []
  }
}
```

### 3. MCP Configuration

**Configuration Location Priority:**
1. **Workspace-level**: `.cursor/mcp.json` (preferred for development)
2. **Global**: `~/.cursor/mcp.json` (for production tools)

**Required Configuration Structure:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/absolute/path/to/dist/index.js"],
      "env": {
        "API_KEY": "your-staging-api-key",
        "BACKEND_URL": "http://localhost:3011"
      }
    }
  }
}
```

### 4. Package Management
- Always use latest versions in `package.json`
- Include proper scripts: `build`, `test`, `dev`
- Use TypeScript with strict configuration

### 5. Git Configuration
Create comprehensive `.gitignore` for MCP development

## 🧪 Iterative Development Workflow

### Build & Development Cycle

```bash
# Always build before testing
npm install
npm run build

# Verify TypeScript compilation
npx tsc --noEmit

# Test server starts (optional validation)
node dist/index.js
```

**Core Workflow**: Build → Test in Cursor → Debug → Fix → Repeat

## 🚀 Deployment & Integration

### Local Development
```bash
npm run build
node dist/index.js
```

### MCP Client Integration

**Cursor/Claude Desktop** (`~/.cursor/mcp.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "your-mcp": {
      "command": "node",
      "args": ["/path/to/your-mcp/dist/index.js"]
    }
  }
}
```

**LM Studio** (Settings → Model Context Protocol):
- Add server with command: `node /path/to/your-mcp/dist/index.js`

## 📝 Documentation Best Practices

### README.md Standards

**Evergreen Content Principles:**
- ❌ **Avoid**: Status badges, version numbers, recent updates
- ❌ **Avoid**: Test results, fix histories, temporal references
- ❌ **Avoid**: "All tools working!" or implementation details
- ✅ **Include**: What it does, how to use it, setup instructions
- ✅ **Include**: Tool categories and purposes
- ✅ **Include**: Example workflows and usage patterns

**README Template Structure:**
```markdown
# Project Name

Brief description of what it does.

## What It Does
Usage-focused explanation with examples.

## Setup
1. Install dependencies
2. Configure MCP client  
3. Start using

## Available Tools
| Category | Tools | What They Do |
|----------|-------|-------------|

## Key Features
- Capability descriptions (not implementation details)
```

### Testing Documentation

**test/testing.md Purpose:**
- Testing protocols and procedures
- Setup and validation steps
- Troubleshooting commands
- Expected behaviors and error conditions
- **NOT for**: Test results, status updates, fix histories

**Separate Test Results:**
- Keep test results in `test/results/` or similar
- Use timestamped files for historical tracking
- Don't mix protocols with results


---
