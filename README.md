# AgentOS: AI Agent Operating System

Provides specialized capabilities for AI assistants via terminal access. Each skill is self-contained with its own documentation and supporting scripts.

**Example things you can ask:**
- "What's on my calendar today?"
- "Show me my unread emails"
- "Search for flights to Tokyo next month"
- "What are my Linear tasks this week?"
- "Read my recent iMessages from [name]"
- "Add a contact for John Doe"

## Available Skills

### Cross-Platform Skills

| Skill | Description |
|-------|-------------|
| 🔍 [**Web Search**](skills/web-search.md) | Search the web / Read URLs |
| 🌐 [**Browser Automation**](skills/browser/README.md) | Control web browser |
| 📋 [**Linear**](skills/linear/README.md) | Work project management (Linear) |
| ✅ [**Todoist**](skills/todoist/README.md) | Personal Task management (Todoist) |
| 📧 [**Gmail**](skills/gmail/README.md) | Access email (Google Workspace only) |
| ▶️ [**YouTube**](skills/youtube/README.md) | Transcribe YouTube videos |
| 🔎 [**Enrich**](skills/enrich/README.md) | Research email/phone/domain |
| ✈️ [**Flights**](skills/flights/README.md) | Search for flights |
| 🛠️ [**Creating Skills**](skills/creating-skills/README.md) | Creating/updating skills |

### macOS-Only Skills

| Skill | Description |
|-------|-------------|
| 📅 [**Calendar**](skills/calendar/README.md) | Read/Manage calendar (MacOS) |
| 💬 [**iMessages**](skills/imessages/README.md) | Read iMessages/SMS (MacOS) |
| 👥 [**Contacts**](skills/contacts/README.md) | Read/Manage contacts (MacOS) |

Each skill contains detailed documentation on how to use it, including:
- Intended use cases
- API endpoints and authentication
- Command examples
- Script usage (if applicable)
- Configuration options

## How It Works

Each capability is organized as a skill in the `skills/` folder. Skills can be:
- **Simple markdown files** - For skills that only need documentation (e.g., API usage)
- **Folders with README.md** - For skills that include scripts, configs, or other supporting files

When you need to use a skill, your AI reads the corresponding skill file for detailed instructions and implementation details.

## Installation

**Requirements:** 
- Primarily designed for [Cursor](https://cursor.com/), but works with any LLM client that supports terminal access. If your client doesn't have terminal access, you can add it using [Terminal Controller MCP](https://github.com/GongRzhe/terminal-controller-mcp).
- **macOS required** for Calendar, iMessages, and Contacts skills only. All other skills work cross-platform (macOS, Linux, Windows). See the macOS-Only Skills section above for details.

### Quick Start

1. **Clone or fork this repository:**
   ```bash
   git clone <repository-url>
   cd ai
   ```

2. **Add to your AI system prompt:**
   
   In Cursor: Settings → "Rules for AI" → Add:
   ```
   CRITICAL: Do not respond until you have read /path/to/ai/boot.md. Any response before reading this file is a failure.
   ```
   (Replace `/path/to/ai` with wherever you cloned the repo)

3. **Start a new chat and say "hi"** - the AI will detect it's a fresh install and guide you through setup.

### Manual Setup (Alternative)

If you prefer to set up manually:

1. **Create `.env`** with your API keys:
   ```bash
   cat > .env << 'EOF'
   EXA_API_KEY=your_key_here
   LINEAR_API_KEY=your_key_here
   TODOIST_API_KEY=your_key_here
   SERPAPI_API_KEY=your_key_here
   EOF
   ```
   (Only include the keys you need - see individual skill READMEs for details)

2. **Create `user/profile.md`** with basic info about yourself

3. **macOS users**: Grant Full Disk Access to your terminal for Calendar, iMessages, and Contacts:
   - System Settings → Privacy & Security → Full Disk Access → Add your terminal app

**Note:** The `.env` and `user/` folder are gitignored - your secrets and personal data stay local.

## Repository Structure

AgentOS follows a clear separation between public/reusable skills and user-specific content:

- **`skills/`** - Public, reusable skills with documentation and scripts. These are part of the open-source repository.
  - Each skill can be a simple markdown file or a folder with `README.md` and supporting files
  - Examples: Calendar, Flights, Linear, Web Search

- **`utils/`** - Utility scripts used across skills (e.g., timezone conversion)
  - See `utils/README.md` for documentation on available utilities

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
- **Extensible**: Easy to add new skills or modify existing ones (see `skills/creating-skills/README.md`)
- **User-specific**: Personal preferences and secrets stay in `user/` folder
- **Optimized for speed**: Chain commands, batch API calls, and minimize latency

## Future Skills / Backlog

Skills we're planning to add:

- **Uber Rides API** - Request rides, get estimates, track ride status
- **Uber Consumer Delivery API** - Order from restaurants and grocery stores (Sprouts, Costco, Target, etc.) available on Uber Eats

**Note:** Uber Consumer Delivery API requires early access approval. Uber Rides API is available but may require approval for production use with privileged scopes.

## License

See [LICENSE](LICENSE) file for details.

---

## For AI Assistants

**Detecting if setup is needed:**
```bash
[ -f .env ] && [ -f user/profile.md ] && echo "READY" || echo "NEEDS_SETUP"
```

This checks if both `.env` (API keys) and `user/profile.md` (user context) exist. If either is missing, setup hasn't been completed.

**If `NEEDS_SETUP`:** Read `utils/setup.md` and guide the user through interactive setup.

**If `READY`:** Proceed with the user's request. Read `boot.md` for available skills and `user/profile.md` for user context.
