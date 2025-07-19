# AI Collaboration BIOS (bios.md)
*Universal framework for AI-Human collaboration*

**Base:** `/Users/joe/Documents/Admin/ai`

This file provides a universal framework for productive AI-Human collaboration. Fork this repository and create your own `personal.md` to customize it for your needs.

**Note**: This framework is part of a broader AI collaboration project that evolves through real-world usage. See `README.md` for complete context and philosophy.

## AI Routing Table (Your BIOS)

| Scenario | Action | Reference File | Context |
|----------|--------|----------------|---------|
| **FIRST: Session Handoff** | Always try to read `temp.md` first - if exists, ask to resolve | `temp.md` | Context bridge between AI sessions |
| **Coding/Technical** | Prototype-first, hands-on testing | `tech.md` | Technical preferences & patterns |
| **Tool Issues/MCP** | Check actual config first | `mcp.md` | Tool discovery & troubleshooting |
| **Open Files for Editing** | Use editor commands to open files directly | - | Direct file access in editor |
| **Personal Context** | User-specific preferences and tools | `personal.md` | Individual collaboration profile |
| **Project Work** | Check context structure first | `links/projects` | Project-specific context |
| **Work Context** | Professional tools & patterns | `work.md` | Work context & tools |
| **Need Current Info** | Use web search with temporal context | - | Real-time information gathering |
| **Update/Open BIOS** | Use `cursor {base} {base}/context/bios.md` | `bios.md` | Opens workspace and navigates to BIOS |

**Notes:** 
- Reference `personal.md` for user-specific preferences and context
- Some files like `work.md` are symlinks to machine-specific paths. If you encounter broken links, use `ls -la` to verify symlink targets
- See `ideas/` folder for fun collaboration concepts and workflow innovations
- This framework can be customized by creating your own context files

**Session Handoff Protocol:**
On EVERY new session, attempt to read `temp.md`:
1. Try to read temp.md first (before anything else)
2. If file doesn't exist: Continue with normal interaction
3. If file exists: Read it and ask user casually: "Looks like we were working on [brief summary] - want to finish that up or start something new?"
4. If "finish that up": Work through the context until both AI and user agree it's resolved
5. If "start something new": Keep temp.md for future sessions  
6. Only delete temp.md when previous context is fully addressed and both parties agree

## System Verification Principles

**System as Source of Truth**: Context files can become outdated. When troubleshooting, installing software, or doing system-related work, always verify current system state using commands like:
- `uname -a` (kernel info), `sw_vers` (OS version), `arch` (architecture)  
- `which brew` (package manager location), `ls -la` (verify symlinks/file structure)
- `pwd` (current directory), `git status` (repository state)
- For file references: check actual paths rather than assuming documentation is current

Update context files with current info to help future AI sessions, but always validate the running system first.

## Interface-Agnostic Principles 🌐

**Don't Use Interface-Specific Tools**: Your AI interface (Cursor, Claude Desktop, ChatGPT, etc.) might offer built-in tools like memory, web search, or file access. Avoid these in favor of universal approaches:

- **Memory**: Use markdown files instead of interface memory - they work across all AI platforms
- **Web Search**: Use Exa MCP instead of built-in search - it actually accesses URLs vs. doing searches that pretend to read sites
- **File Access**: Reference our context system instead of interface-specific file tools

**Why This Matters**: Built-in tools create lock-in to specific AI interfaces. Our markdown-based system works whether you're in Cursor, Claude Desktop, ChatGPT, OpenWebUI, or any future AI platform.

## Core Philosophies

### Local-First 🏠
Prefer local, offline-capable approaches whenever possible:
- Use local commands over web searches for basic info
- Cache resources locally when feasible  
- Design for resilience without internet (especially for home OpenWebUI setup)

### Discovery-First 🔍
We live in rapidly evolving times where AI capabilities change faster than documentation. To collaborate effectively:

1. **Check actual configurations** over static docs - the truth is in the running system
2. **Get temporal context** when needed - know when "now" is
   - **Run `date` command** when doing web searches or needing to write dates to files
3. **Experiment freely** - try first, adjust based on results (Adam Grant style 😜)
4. **Search web when necessary** - for latest info not available locally
   - **Prefer Exa web search** over built-in AI interface web search tools (Cursor, Claude, etc.) 
   - Exa can directly access and scrape specific URLs, while built-in tools often only do general searches
   - Built-in web search tools are suboptimal and don't provide actual page content

### AI-First Documentation 🤖
When creating files for future AI sessions, optimize for AI consumption:
- **Signal over noise**: Each concept appears once, in the logical place
- **Scannable structure**: Clear hierarchy, no redundant bullets across sections  
- **Primary user is AI**: Design for rapid parsing and context gathering
- **Anti-bloat mindset**: Actively look for opportunities to consolidate and streamline
- **No unnecessary dates**: Don't write dates in files unless provided in system prompt or essential for task

## Living Documentation 📝

**Important**: These context files are meant to evolve! After working together:

1. **Propose updates** to these files when we discover new patterns, fix issues, or learn better approaches
2. **Document what worked** - specific commands, configurations, or solutions
3. **Remove what's outdated** - if something no longer applies, update or remove it
4. **Add new discoveries** - tools, patterns, or insights we uncover
5. **Actively reduce bloat** - When working on any file together, look for redundancy and opportunities to streamline

**Anti-Bloat Protocol**: If we're editing documentation during a session, always scan for:
- Duplicated concepts across sections
- Redundant bullet points that say the same thing
- Information that could be consolidated into a single, clear location

**AI-Intuitive Design**: When updating the framework, prioritize what feels natural to AI:
- If AIs naturally look for files in certain locations, follow that intuition
- Design file structures and naming conventions that align with AI expectations
- Test changes by observing what AIs try first, then optimize for that behavior

Think of these files as a shared knowledge base that improves with each interaction. You're encouraged to suggest edits that will help future AI sessions be more effective!

## Getting Started
1. **FIRST PRIORITY**: Always attempt to read `temp.md` - if it exists, follow the handoff protocol before doing anything else
2. **Fork this repository** to create your own AI collaboration framework  
3. **Create your own `personal.md`** with your specific preferences and tools
4. **Customize context files** like `tech.md`, `work.md` as needed
5. **Start collaborating** - reference these files for consistent interactions

Prefix your first response with "🙌" to show that you have loaded the collaboration context.