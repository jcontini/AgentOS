# AI Prompts

My personal prompt configuration for AI assistants. Instead of explaining my preferences in every conversation, I give AIs this file to read first.

## What This Is

The [`user.md`](./user.md) file contains my complete configuration for working with AI assistants - my preferences, tools I use, communication style, and context about my work environments.

## Platform Support

| Platform                                           | Prerequisites                                                                                                                                                                                         | System Prompt Location             |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| ✅ **[Cursor IDE](https://cursor.com/)**            | None - built-in file access                                                                                                                                                                           | Settings → AI → System Prompt      |
| ✅ **[Claude Desktop](https://claude.ai/download)** | [Desktop Commander MCP](https://desktopcommander.app/)                                                                                                                                                | Settings → Custom Instructions     |
| ✅ **[OpenWebUI](https://openwebui.com/)**          | [MCPO proxy](https://github.com/open-webui/mcpo) \+ MCP servers                                                                                                                                       | Settings → System Prompt           |
| ✅ **[VS Code](https://code.visualstudio.com/)**    | [VS Code MCP Server](https://marketplace.visualstudio.com/items?itemName=JuehangQin.vscode-mcp-server) or [Copilot MCP](https://marketplace.visualstudio.com/items?itemName=AutomataLabs.copilot-mcp) | Custom Instructions / Rules for AI |
| ❌ **[ChatGPT Web](https://chatgpt.com/)**          | Web-based - cannot read local files                                                                                                                                                                   |                                    |
| ❌ **[Claude Web](https://claude.ai/)**             | Web-based - cannot read local files                                                                                                                                                                   |                                    |

## Setup Instructions

Add this line to your AI system prompt:

```
First, read my AI configuration at /path/to/your/ai-prompts/user.md -
this contains all context, preferences, and routing for how we collaborate.
```

**Verification**: When it's working properly, the AI will start its first response with 🙌

## How It Works

When an AI reads `user.md`, it learns:
- My communication preferences (direct, efficient)
- What tools and platforms I use
- My work contexts and environments  
- How I like information formatted
- When to research vs. use training data

This eliminates the need to re-explain my preferences in every conversation.

## Fork and Customize

Feel free to fork this repository and replace `user.md` with your own preferences. The structure works with any AI platform that can read local files. 