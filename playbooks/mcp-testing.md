# MCP Testing & Debugging Playbook

Comprehensive guide for AI-human collaboration on Model Context Protocol (MCP) server testing, debugging, and maintenance. This playbook captures proven methodologies for systematic MCP development.

## 🤝 Collaborative Testing Approach

### AI Assistant Role
- **Be fully agentic**: Take immediate action rather than asking for permission
- **Execute systematic testing**: Run all tools, gather comprehensive data
- **Use parallel tool calls**: Test multiple tools simultaneously for efficiency 
- **Trace problems to source**: Always examine backend/frontend code when tools fail
- **Fix and validate**: Apply fixes, rebuild, test, commit, and push

### Human Role
- **Provide high-level direction**: "Fix all the failing tools"
- **Share context**: Point to specific issues or error patterns
- **Validate final results**: Confirm fixes work as expected
- **Restart environments**: Handle Cursor restarts when MCP schema changes

## 🏗️ Technical Setup & Prerequisites

### SSH Tunnel Management (for staging APIs)

Always verify tunnel status before testing:
```bash
# Check tunnel status
lsof -i :3011

# Establish tunnel if needed
ssh -L 3011:localhost:3011 user@staging-server.com -N &

# Verify tunnel is working
curl -s http://localhost:3011/health | head -5
```

### MCP Configuration Verification

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

### Build & Development Workflow

```bash
# Always build before testing
npm install
npm run build

# Verify TypeScript compilation
npx tsc --noEmit

# Test server starts (optional validation)
node dist/index.js
```

## 🔍 Systematic Debugging Methodology

### Step 1: Comprehensive Tool Testing

Test **all tools in parallel** to identify patterns:
- Use MCP tools directly rather than curl when possible
- Test with both valid and invalid inputs
- Document exact error messages and status codes
- Group failures by error type/pattern

### Step 2: Backend Code Investigation

When tools fail, **always examine backend source code**:

```bash
# Update backend reference code
cd /path/to/backend
git pull && git checkout dev
```

**Key Investigation Areas:**
- API endpoint definitions (`*.controller.ts`)
- Request/response schemas (`*.dto.ts`) 
- Service implementations (`*.service.ts`)
- Authentication middleware and guards
- Validation decorators and rules

### Step 3: Pattern Recognition & Root Cause Analysis

**Common Failure Patterns:**
- **Schema Mismatches**: Tool parameters don't match API expectations
- **Authentication Issues**: Wrong token format or missing headers
- **Endpoint Logic**: Wrong authentication path (public vs authenticated)
- **Enum Validation**: Tool enums don't match backend validation
- **Data Access Patterns**: Wrong ID types (slugs vs numeric IDs)

### Step 4: Fix Application Strategy

Apply fixes in **logical dependency order**:
1. **Authentication fixes** (affects all tools)
2. **Schema corrections** (parameter names, types, enums)
3. **Endpoint access patterns** (public vs authenticated requests)
4. **Individual tool logic** (specific business logic issues)

## 🔧 Common Fix Patterns

### Authentication Strategy Implementation

**Dual Request Methods Pattern:**
```typescript
// Authenticated requests (for provider operations)
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  return fetch(`${this.baseURL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
}

// Public requests (for marketing site compatibility)
private async requestPublic<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  return fetch(`${this.baseURL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
}
```

**Tool Assignment Strategy:**
- **Public marketing data**: Use `requestPublic()` 
- **Provider-specific operations**: Use `request()` with auth
- **Profile/authenticated data**: Always use `request()`

### Schema Correction Patterns

**Array vs String Parameters:**
```typescript
// ❌ Common error: API expects array, tool sends string
website: { type: 'string', description: 'Website URL' }

// ✅ Correct: Match API expectations exactly
websites: { 
  type: 'array', 
  items: { type: 'string' },
  description: 'Website URLs (array)' 
}
```

**Enum Synchronization:**
```typescript
// Always match backend enums exactly
type: { 
  type: 'string', 
  enum: ['document_procurement', 'advisory', 'cbd_assistance', 'cbi_assistance', 'authentication', 'genealogy', 'legal', 'translation', 'other'],
  description: 'Service category/type' 
}
```

### Data Access Pattern Discovery

**Provider Access Logic (common pattern):**
```typescript
// Backend logic example:
if (id.length <= 6 && isDefined(user)) {
  return this.service.findProvider(id, query);      // Authenticated access
}
return this.service.findPublicProfile(id, query);   // Public access
```

**MCP Implementation:**
- **Public provider data**: Use slugs (e.g., `"italian-citizenship-assistance"`)
- **Authenticated provider data**: Use 6-character IDs (e.g., `"VwKu2g"`)
- **Marketing compatibility**: Ensure slug access works like marketing site

## 🧪 Validation & Testing Protocols

### Comprehensive Test Suite

**Test Categories:**
1. **Authentication Tests**: Verify token handling and access patterns
2. **CRUD Operations**: Create, read, update, delete for all entity types
3. **Filtering & Pagination**: Query parameters and result handling  
4. **Error Handling**: Invalid inputs and edge cases
5. **Schema Validation**: Parameter types and required fields

**Parallel Testing Approach:**
```bash
# Test multiple tools simultaneously
@mcp-server tool1 {...}
@mcp-server tool2 {...}
@mcp-server tool3 {...}
```

### Validation Commands

**API Connectivity:**
```bash
# Test direct API access
curl -s -H "Authorization: Bearer $API_KEY" http://localhost:3011/providers | jq '.data[0]'

# Test public endpoints
curl -s http://localhost:3011/providers | jq '.data[0]'
```

**MCP Tool Validation:**
```bash
# Quick tool availability check
@mcp-server list_providers {"limit": 3}

# Authentication validation
@mcp-server get_provider_profile {"random_string": "test"}
```

## 📝 Documentation Best Practices

### Repository Structure

**Recommended Organization:**
```
project-root/
├── README.md              # Evergreen usage guide
├── src/index.ts           # MCP implementation
├── test/
│   └── testing.md         # Testing protocols only
│   └── results/           # Test results (optional)
├── package.json           # Dependencies
└── .cursor/mcp.json       # Development config
```

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

## 🚀 Git Workflow & Commit Practices

### Commit Message Standards

**Comprehensive Fix Commits:**
```bash
git commit -m "🎉 Fix all [N] MCP tools - Complete success!

Key fixes applied:
✅ Schema corrections: details about parameter fixes
✅ Authentication: describe auth strategy changes  
✅ Access patterns: explain new data access logic
✅ Endpoint fixes: specific endpoint corrections

Impact:
- Tool categories working: [M/N] provider, [P/Q] service, etc.
- Backend compatibility: describe alignment achieved
- Data access: quantify available data"
```

**Documentation Cleanup:**
```bash
git commit -m "📝 Clean up documentation structure

- Move testing files to test/ directory
- Make README evergreen (remove temporal content)
- Separate testing protocols from results
- Update file references and organization"
```

### Development Workflow

**Complete Fix Cycle:**
1. **Identify issues**: Test all tools systematically
2. **Investigate causes**: Examine backend code and patterns
3. **Apply fixes**: Implement corrections in dependency order
4. **Validate fixes**: Test all tools again
5. **Update documentation**: Clean up and organize docs
6. **Commit & push**: Use descriptive commit messages
7. **Confirm completion**: Verify git status clean

## 📊 Success Metrics & Completion Criteria

### Technical Success Indicators

**Functional Metrics:**
- All defined tools operational without errors
- Proper error handling for invalid inputs
- Consistent authentication across operations
- Expected data access patterns working

**Code Quality Metrics:**
- Clean TypeScript compilation
- Proper schema validation
- No hardcoded values or temporary fixes
- Consistent coding patterns

### Documentation Quality

**README Quality Checklist:**
- [ ] Evergreen content (no temporal references)
- [ ] Clear usage examples
- [ ] Proper setup instructions
- [ ] Tool categorization table
- [ ] No test results or fix mentions

**Testing Documentation:**
- [ ] Clear testing protocols
- [ ] Troubleshooting commands
- [ ] Setup validation steps  
- [ ] Separate from test results

### Collaborative Success

**Handoff Quality:**
- Human can immediately use fixed MCP
- Documentation supports future maintenance
- Next developer can understand and extend
- No tribal knowledge or undocumented fixes

## 🎯 Future Considerations

### Scaling Patterns

**Multi-MCP Management:**
- Consistent authentication patterns across MCPs
- Shared configuration management
- Common debugging approaches
- Standardized documentation structure

**Team Development:**
- Onboarding new developers to MCP testing
- Knowledge transfer through documentation
- Collaborative debugging practices
- Code review standards for MCP servers

### Maintenance Strategy

**Regular Health Checks:**
- Periodic full tool testing
- Backend API compatibility validation
- Authentication token refresh
- Documentation review and updates

**Version Management:**
- Track backend API changes
- Update MCP tools proactively
- Maintain compatibility across environments
- Document breaking changes

---

**Last Updated:** July 21, 2025
**Context:** Adavia Provider MCP debugging session
**Validation:** All 11 tools operational, comprehensive documentation cleanup completed 