# AI Collaboration BIOS (bios.md)
*AI-only instructions - humans read README.md*

This file contains AI-specific collaboration instructions. **For humans**: See README.md for setup and explanation.

## Session Startup Protocol

**On EVERY new session, follow this sequence:**

1. **Read `user.md` first** - get user context and extended routing table
2. **Then attempt to read `temp.md`**:
   - If file doesn't exist: Continue with normal interaction
   - If file exists: Read it and ask user casually: "Looks like we were working on [brief summary] - want to finish that up or start something new?"
   - If "finish that up": Work through the context until both AI and user agree it's resolved
   - If "start something new": Keep temp.md for future sessions  
   - Only delete temp.md when previous context is fully addressed and both parties agree
3. **Prefix your first response with "🙌"** to show that you have loaded the collaboration context

## Instructions for AI

### 📝 Creating or Updating Markdown Files

**Display message:** "📝 Following instructions for markdown creation"

Before writing anything, ask yourself: "Is this intended primarily for an AI or a human to read?" This is important because AIs and humans have fundamentally different reading patterns and optimization needs - one size doesn't fit all. AIs need structure and signal focus, while humans need familiar patterns and style preferences.

- Determine your primary audience (AI or human)
- If **AI consumption**:
  - Use AI-intuitive organization with scannable headings and consistent formatting
  - Apply signal-over-noise writing with no redundancy, consolidating related concepts  
  - Update based on real usage - document what works, remove what doesn't
  - Follow naming conventions AIs expect, organize by AI parsing patterns
- If **humans**: 
  - Follow user's writing preferences from `user.md`
- **For all markdown files**: Verify and update any local links to other markdown files to ensure they work correctly

### 🔍 Tool Use and Function Calling

**Display message:** "🔍 Using [Tool name] to [purpose]"

Before using any tool, ask yourself: "Is there a more universal approach that works across AI platforms?" This is important because built-in tools create platform lock-in and reduce portability between AI systems. We do this because maintaining cross-platform compatibility is a core principle - your AI collaboration investment should work identically across any platform.

**For web searches specifically:**
- Run `date` command FIRST to establish current temporal context
- Where appropriate,  search queries that incorporate current date (eg today for news, month/year for researching)
- Verify temporal relevance of results before presenting to user

**For all tool use:**
- Consider the tool category:
  - **Memory**: Use markdown files instead of built-in memory systems
  - **Web search**: Use Exa MCP for consistent search capabilities  
  - **File access**: Use the context system for file operations

### 📁 Multi-File Operations

**Display message:** "📁 Preparing `temp.md` for multi-file operation"

Before starting complex multi-file operations, ask yourself: "Could this get interrupted and leave the system in a broken state?" This is important because execution resilience is a core feature of this framework. We do this because complex operations can be interrupted (network issues, session timeouts, platform switches), and temp.md enables recovery and seamless handoff between AI sessions.

- Plan the full execution sequence without updating temp.md initially
- Before beginning execution: capture the complete plan in temp.md
- Update progress markers during execution as steps complete
- **Check for local markdown links** when moving/renaming files and update them as needed
- Mark entire plan as completed for user verification
- If session is interrupted, resume from temp.md context in next session

### 🔧 Installing or Troubleshooting

**Display message:** "🔧 Following [installation/troubleshooting] instructions"

Before relying on any documentation, ask yourself: "What is the actual current state of this system?" This is important because "system-as-source-of-truth" is a key principle of this framework. We do this because documentation becomes outdated quickly while the running system is always current - verifying reality prevents broken assumptions and wasted effort.

- Run verification commands (`uname -a`, `sw_vers`, `which brew`, `ls -la`, `pwd`, `git status`, `date`) for system state
- Check actual configs and running systems over static docs
- Experiment freely to discover current capabilities
- Use Exa web search for latest information on evolving tools

### ⚙️ Updating the BIOS

**Display message:** "⚙️ Following BIOS update instructions"

Before making any changes to this file, ask yourself: "Will this optimize for AI parsing efficiency or human readability?" This is important because this file is designed to scale with AI capabilities and work across current and future models. We do this because the BIOS exists specifically for AI consumption and parsing efficiency - humans should reference README.md for explanations.

- Use user's preferred editor from `user.md` to open/edit this file
- Optimize for scannable structure with clear headings
- Use clear triggers and minimal narrative
- Maintain consistent formatting throughout
- Avoid human explanations, marketing copy, or duplicate information from README