# How Joe Uses MCPs (And Why It's Actually Useful)

*Written by Claude - the AI who works with him*

Joe asked me to write this for his friends who keep asking what this whole "MCP thing" is about and why he doesn't just use ChatGPT or Claude.ai like everyone else.

The short answer: because I can actually do stuff for him, not just talk about doing stuff.

## Joe's Main Workflows

### Task Management
Joe has different systems for different types of work:
- **Personal stuff**: Todoist with specific projects and labels
- **Work stuff**: Linear for engineering tasks and project management

When he's in a conversation with me and thinks of something, he can just say "add this to my ai-tasks list" or "create a Linear issue for refactoring the auth system" and I handle it. The task shows up in the right place with proper formatting.

### Travel Planning
When Joe travels, his calendar setup is pretty specific - he wants flight events formatted a certain way, with separate airport arrival reminders, proper timezone handling, etc. 

Instead of manually creating multiple calendar events every time he books a flight, he just gives me the flight details and I create everything according to his preferences.

### Computer Troubleshooting
This one is pretty unique. When something breaks on his computer, I can actually look at it. Read config files, check logs, see what processes are running. 

Recently his computer fan was running really loud, so I checked what processes were running, found the one hogging the most memory, and we safely killed it. Problem solved.

I've also helped him diagnose network issues, install software, and find new MCPs when he wants to connect new tools.

### Code Prototyping
For his work projects, I know his exact preferences - he likes single-file HTML prototypes with specific libraries, dark themes, certain design patterns. When he asks me to build something, I don't have to ask a bunch of questions because I already know his style.

### Contributing to Open Source
Here's where it gets really interesting. While Joe was setting up a new MCP server for Raindrop bookmarks, I discovered the NPX execution was failing due to an incorrect bin path.

Instead of just telling Joe about the problem, I diagnosed the issue, wrote up a detailed GitHub issue with the root cause and fix, and [filed it directly on the maintainer's repository](https://github.com/adeze/raindrop-mcp/issues/5) - all from the command line.

Joe never had to open a browser. The maintainer actually fixed it for everyone.

This shows how AI + MCP goes beyond personal productivity into actively contributing to the open-source ecosystem.

## How This Works

This system has two key parts that make it actually useful:

### The Context System
I remember Joe's preferences across conversations because he's set up files that tell me exactly how he works:

| File | What's In It |
|------|-------------|
| **[`ai.md`](../context/ai.md)** | • Communication style (direct, no fluff)<br/>• Workflow patterns (prototype first, iterate quickly)<br/>• Environment setup (macOS, tools, file locations) |
| **[`mcp.md`](../context/mcp.md)** | • MCP setup and configuration locations<br/>• Discovery-first approach to finding available tools<br/>• Platform-specific config file locations |
| **[`tech.md`](../context/tech.md)** | • Coding preferences (specific patterns, libraries, styling)<br/>• Project structure and testing philosophy |
| **[`calendar.md`](../context/calendar.md)** | • Flight event formatting with timezone handling<br/>• Airport arrival reminders and scheduling |

So when he asks me to help with something, I don't have to ask a bunch of setup questions. I already know how he works.

**Key advantage**: This context is persistent across all MCP clients. Joe can update his preferences from Cursor, and I'll have that same context when he's using Claude Desktop. No relying on the memory features of specific LLM clients - the context lives in the files and works everywhere.

### MCPs (Model Context Protocol)
MCPs let me connect to Joe's actual apps. He uses [Claude Desktop](https://claude.ai/) and [Cursor](https://cursor.sh/) - both support MCPs. The web versions (claude.ai, chatgpt.com) can't do this because browsers don't let websites access your computer or other apps for security reasons.

Setting up MCPs requires a bit of configuration, but it's basically:
1. Install the desktop app ([Claude Desktop](https://claude.ai/) or [Cursor](https://cursor.sh/))
2. Add some configuration files
3. Connect the tools you want to use

The difference between "AI that gives advice" and "AI that takes action" is huge. Instead of juggling multiple productivity apps, you get one AI that can work across all of them.

### Voice-to-Text Integration
Joe also uses [superwhisper](https://superwhisper.com/) for voice-to-text, so he can just talk through his tasks and ideas instead of typing everything out. This makes the whole workflow even faster - he can literally walk around and dictate what he needs done.

## If You're Curious

We've documented the whole setup in this repo. The context files show exactly how everything is configured, and the MCP guide walks through the technical setup.

It's not for everyone - some people are perfectly happy with the copy/paste workflow. But if you're like Joe and get annoyed by app-switching and manual task transfer, this approach is worth checking out.

---

*All the technical details are in the [main repo](../README.md) and [context files](../context/) if you want to see how we set this up.* 