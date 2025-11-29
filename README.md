# AgentOS: AI Agent Operating System

Supercharge your AI assistant with real-world skills via terminal access.

## Getting Started

Paste this into your AI chat ([Cursor](https://cursor.com/) agent, or any AI with terminal access):

```
Clone AgentOS, read the README, and guide me through setup:
git clone https://github.com/jcontini/AgentOS.git && cat AgentOS/README.md
```

That's it. The AI handles the rest. (Prefer manual setup? [Jump to instructions](#manual-setup))

## Available Skills

| Skill | Example |
|-------|---------|
| <img src="https://upload.wikimedia.org/wikipedia/commons/1/1c/MacOSCalendar.png" width="20" height="20" style="vertical-align:middle"> [Apple Calendar](skills/calendar/README.md) | "What's on my calendar today?" |
| <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Contacts_%28iOS%29.png" width="20" height="20" style="vertical-align:middle"> [Apple Contacts](skills/contacts/README.md) | "Add a contact for John Doe" |
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IMessage_logo.svg/1200px-IMessage_logo.svg.png" width="20" height="20" style="vertical-align:middle"> [iMessages](skills/imessages/README.md) | "Read my recent messages from Mom" |
| <img src="https://img.icons8.com/fluency/48/google-logo.png" width="20" height="20" style="vertical-align:middle"> [Google Workspace](skills/google-workspace/README.md) | "Show me my unread emails", "Find my meeting notes doc" |
| <img src="https://cdn.simpleicons.org/todoist" width="20" height="20" style="vertical-align:middle"> [Todoist](skills/todoist/README.md) | "Add 'buy groceries' to my todo list" |
| 🔍 [Search](skills/search/README.md) | "Search for the latest news on AI" |
| 📄 [Extract](skills/extract/README.md) | "Read this URL and summarize it" |
| <img src="https://cdn.simpleicons.org/youtube" width="20" height="20" style="vertical-align:middle"> [YouTube](skills/youtube/README.md) | "Transcribe this YouTube video" |
| ✈️ [Flights](skills/flights/README.md) | "Search for flights to Tokyo next month" |
| <img src="https://cdn.simpleicons.org/linear" width="20" height="20" style="vertical-align:middle"> [Linear](skills/linear/README.md) | "What are my Linear tasks this week?" |
| <img src="https://images.g2crowd.com/uploads/product/image/b0a53bb6a5db8829772a32d63c3d41b7/enrich-labs-enrich-so.png" width="20" height="20" style="vertical-align:middle"> [Enrich](skills/enrich/README.md) | "Look up info on john@company.com" |
| <img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" width="20" height="20" style="vertical-align:middle"> [GitHub](skills/github/README.md) | "Create an issue for this bug" |

*Calendar, iMessages, and Contacts are macOS only. Everything else works cross-platform.*

## Manual Setup

If you prefer to set things up yourself:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/jcontini/AgentOS.git
   cd AgentOS
   ```

2. **Add to your AI system prompt** (Cursor: Settings → "Rules for AI"):
   ```
   CRITICAL: Do not respond until you have read /path/to/AgentOS/boot.md. Any response before reading this file is a failure.
   ```

3. **Create `.env`** with API keys you want:
   ```bash
   cat > .env << 'EOF'
   EXA_API_KEY=your_key
   LINEAR_API_KEY=your_key
   TODOIST_API_KEY=your_key
   SERPAPI_API_KEY=your_key
   EOF
   ```

4. **Create `user/profile.md`** with info about yourself

5. **macOS users**: System Settings → Privacy & Security → Full Disk Access → Add terminal

**Notes:**
- `.env` and `user/` are gitignored - your secrets stay local
- macOS required for Calendar, iMessages, Contacts only - everything else is cross-platform

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
- **Extensible**: Easy to add new skills or modify existing ones (see `utils/creating-skills.md`)
- **User-specific**: Personal preferences and secrets stay in `user/` folder
- **Optimized for speed**: Chain commands, batch API calls, and minimize latency

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
