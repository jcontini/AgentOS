# AgentOS: AI Agent Operating System

A skills-based system that extends AI assistants with terminal access and specialized capabilities. Each skill is self-contained with its own documentation and supporting scripts.

## How It Works

AgentOS uses a **skills-based architecture** where each capability is organized as a skill in the `skills/` folder. Skills can be:
- **Simple markdown files** - For skills that only need documentation (e.g., API usage)
- **Folders with README.md** - For skills that include scripts, configs, or other supporting files

When you need to use a skill, your AI reads the corresponding skill file for detailed instructions and implementation details.

## Available Skills

| Skill | Description | Platform | README |
|-------|-------------|----------|--------|
| **Calendar** | Manage calendar events (read, add, update, delete), search calendar | macOS | [`calendar/README.md`](skills/calendar/README.md) |
| **Contacts** | Get or manage contacts | macOS | [`contacts.md`](skills/contacts.md) |
| **Enrich** | Enrich person or company information from emails, domains, LinkedIn | Cross-platform | [`enrich/README.md`](skills/enrich/README.md) |
| **Flights** | Search for flights and compare prices | Cross-platform | [`flights/README.md`](skills/flights/README.md) |
| **Linear** | Create tasks, manage issues, work with Linear | Cross-platform | [`linear/README.md`](skills/linear/README.md) |
| **Todoist** | Manage personal tasks (create, update, complete, delete, list) | Cross-platform | [`todoist/README.md`](skills/todoist/README.md) |
| **Web Search** | Search the web and read URLs | Cross-platform | [`web-search.md`](skills/web-search.md) |
| **YouTube** | Handle YouTube links (transcript or video download) | Cross-platform | [`youtube/README.md`](skills/youtube/README.md) |

Each skill contains detailed documentation on how to use it, including:
- Intended use cases
- API endpoints and authentication
- Command examples
- Script usage (if applicable)
- Configuration options

## Installation

**Requirements:** 
- Primarily designed for [Cursor](https://cursor.com/), but works with any LLM client that supports terminal access. If your client doesn't have terminal access, you can add it using [Terminal Controller MCP](https://github.com/GongRzhe/terminal-controller-mcp).
- **macOS required** for Calendar and Contacts skills only. All other skills work cross-platform (macOS, Linux, Windows). See Platform column in the skills table above for details.

1. **Clone or fork this repository:**
   ```bash
   git clone <repository-url>
   cd ai
   ```

2. **Add to your AI system prompt** (replace `YOUR_PROJECT_PATH` with your actual path):
   ```
   Stop! Before responding, try to read `YOUR_PROJECT_PATH/boot.md` using an MCP.
   If you can't, just prefix your first response with "📳". 
   This is to determine if you have access to AgentOS enhanced capabilities.
   ```

3. **Configure environment variables** (optional): Create a `.env` file in the project root for API keys and user preferences:
   ```bash
   # API keys (only needed for specific skills)
   EXA_API_KEY=your_exa_api_key
   SERPAPI_API_KEY=your_serpapi_key
   ENRICH_SO_API_KEY=your_enrich_so_api_key
   LINEAR_API_KEY=your_linear_api_key
   TODOIST_API_TOKEN=your_todoist_api_token
   
   # User preferences (optional)
   CALENDAR_NAME=your-calendar-name@example.com
   ```

   **Note:** The `.env` file is gitignored and contains user-specific secrets/preferences. Never commit it to the repository.

4. **Verify installation:** If the AI responds to your initial message with "🙌" then you know it's working.

## Repository Structure

AgentOS follows a clear separation between public/reusable skills and user-specific content:

- **`skills/`** - Public, reusable skills with documentation and scripts. These are part of the open-source repository.
  - Each skill can be a simple markdown file or a folder with `README.md` and supporting files
  - Examples: Calendar, Flights, Linear, Web Search

- **`user/`** - User-specific content (gitignored, not shared publicly)
  - **`user/skills/`** - User-specific skills that mirror the `skills/` structure (e.g., personal automation scripts)
  - **`user/skills-data/`** - Generated data from skills (e.g., flight search results, cached API responses)
  - **`user/profile.md`** - User preferences, workflows, and context for the AI
  - **`user/reports/`** - User-generated reports and analysis

- **`.env`** - API keys and user preferences (gitignored)

## Philosophy

AgentOS is designed with speed and simplicity in mind:
- **Terminal-first**: All operations use terminal commands and direct API calls (no MCP overhead)
- **Self-contained**: Each skill includes everything needed to use it
- **Extensible**: Easy to add new skills or modify existing ones
- **User-specific**: Personal preferences and secrets stay in `user/` folder

## License

See [LICENSE](LICENSE) file for details.
