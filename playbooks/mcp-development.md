# MCP Development Playbook

This playbook defines the preferred approach for developing Model Context Protocol (MCP) servers based on proven patterns and user preferences.

**📖 To confirm you've read this playbook, prefix your response with "📚"**

## 🎯 Core Philosophy

**Simplicity First**: Default to minimal, single-file approaches until complexity genuinely demands modularization. The people MCP (`hobbies/ppl-mcp/src/index.ts`) is the gold standard - everything in one clean file.

**Tool-Centric Design**: Prefer tools over resources. Current MCP clients (Cursor, Claude Desktop, LM Studio) have poor resource support, and tools provide better discoverability and functionality.

**Modern Stack**: Always use latest versions and modern best practices.

## 📁 Project Structure (Preferred)

```
project-name-mcp/
├── src/
│   └── index.ts          # Everything goes here
├── package.json
├── tsconfig.json
├── .gitignore            # Comprehensive AI tool + development ignores
├── README.md
└── [tool-specific config]   # See Development Environment Setup below
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

## 🧪 Testing Requirements

Create `testing.md` file with instructions for real MCP client testing in Cursor:
1. **Schema validation**: Verify tool definitions load correctly
2. **Functionality tests**: Step-by-step tool calls with expected outputs
3. **Error conditions**: Test auth failures, invalid inputs, edge cases
4. **Build/restart cycle**: Instructions for rebuilding and restarting MCP process

**Testing Workflow**: Build → Test in Cursor → Iterate → Repeat

## 🔧 Development Workflow

### 1. Research Latest Docs
Before starting, use Context7 MCP to get latest documentation for any libraries/frameworks used.

### 2. Development Environment Setup

Different AI coding tools use different permission/approval systems. Configure based on your tool:

#### Claude Code
Create `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:*)",
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(git:*)",
      "Bash(mkdir:*)",
      "Bash(rm:*)",
      "Bash(curl:*)",
      "Bash(tree:*)"
    ],
    "deny": []
  }
}
```
**Note**: Permissions are session-bound and may not persist between sessions.

#### General Principle
Always configure your AI coding tool for maximum autonomy while maintaining safety. Most tools support some form of pre-approval for common development commands.

### 3. Package Management
- Always use latest versions in `package.json`
- Include proper scripts: `build`, `test`, `dev`
- Use TypeScript with strict configuration

### 4. Git Configuration
Create comprehensive `.gitignore` for MCP development:
```gitignore
# Node.js
node_modules/
dist/
build/
*.log

# AI Coding Tool Configs
.claude/
.codex/
.gemini/
.cursor/
.vscode/
.idea/

# Database Files
*.db
*.kz

# Environment & Secrets
.env
.env.local
.env.*.local

# OS Generated
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

### 5. Documentation
- **README**: Follow user's README principles (no code duplication, show don't tell)
- **Tool descriptions**: Rich, helpful schemas with examples
- **Error messages**: Clear and actionable

## 🚀 Deployment Patterns

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

**Testing with AI Coding Tools**: Most CLI-based AI tools (Claude Code, Codex CLI, Gemini CLI) can interact with MCP servers when properly configured in their respective clients.

## ❌ Anti-Patterns to Avoid

- **Over-engineering**: Multiple files/folders for simple MCPs
- **Resource-heavy**: Prefer tools over resources 
- **Enterprise patterns**: Avoid abstractions for simple projects
- **Complex build processes**: Keep it simple
- **Outdated dependencies**: Always use latest versions

## ✅ Success Patterns

- **Single file with everything**: Like people MCP
- **Clear tool naming**: Descriptive and unambiguous  
- **Rich error handling**: Helpful messages
- **Modern TypeScript**: Latest features and strict mode
- **Comprehensive permissions**: Pre-approve everything
- **Real-world testing**: Test with actual MCP clients

## 🔍 Troubleshooting

1. **Use Exa search** for recent issues/discussions
2. **Check GitHub issues** for MCP SDK problems
3. **Validate schemas** with actual MCP client
4. **Test incrementally** - build tools one at a time

## 💡 Code Writing Philosophy

### Be Solution-Oriented
- Never say "I can't" - research web for solutions first
- Use web search (preferably Exa) for rapidly changing topics like MCP SDK updates
- Move beyond static responses to actively take actions

### Simplicity Principles  
- Default to minimal approaches until complexity demands modularization
- Avoid enterprise patterns and abstractions for simple projects
- Focus on functionality to test hypotheses, not production robustness

### Non-Interactive Development
- Always use non-interactive flags (`--yes`, `--no-edit`, `--force`) 
- AI assistants cannot handle interactive prompts
- Research command documentation for automation options

### Testing for Prototypes
- No unit/integration tests for quick prototypes
- Focus on CLI testing (cURL, debug logs, functionality validation)
- Real MCP client testing (Cursor, Claude Desktop, LM Studio) over simulated testing
- Build → Test → Iterate workflow using actual MCP clients

This playbook prioritizes developer velocity and maintainability over enterprise patterns.

---

**📚 Additional Context**: Also read `../user.md` for comprehensive user preferences and development context. 