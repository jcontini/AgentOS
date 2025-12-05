# AgentOS

Supercharge your AI assistant with real-world skills via terminal access.

## How It Works

```mermaid
flowchart LR
    subgraph You
        U[User Request]
    end
    
    subgraph AI["AI Assistant"]
        B[boot.md]
        S[skills.yaml]
    end
    
    subgraph Types
        A[Actions]
        C[Connections]
    end
    
    subgraph Skills
        E[exa]
        F[firecrawl]
        G[gmail]
        L[linear]
        M[more...]
    end
    
    U --> B
    B --> S
    S --> A
    S --> C
    A --> |search| E
    A --> |extract| E
    A --> |extract fallback| F
    C --> |email| G
    C --> |work-tasks| L
    C --> |...| M
```

**Skills** are services you connect to. They come in two types:
- **Actions** — stateless verbs (search, extract, transcribe)
- **Connections** — your data (email, calendar, crm, tasks)

The AI reads `skills.yaml` to find which skill handles each request, with fallbacks when needed.

## Available Skills

### <img src="https://lkcomputers.com/wp-content/uploads/2015/02/Apple-Glass-Logo.png" width="28" height="28" style="vertical-align:text-bottom"> macOS Native
*Direct access to local apps*

| Skill | What it does |
|-------|--------------|
| <img src="https://upload.wikimedia.org/wikipedia/commons/1/1c/MacOSCalendar.png" width="18" height="18" style="vertical-align:text-bottom"> [Calendar](skills/apple-calendar/README.md) | Read & manage calendar events |
| <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Contacts_%28iOS%29.png" width="18" height="18" style="vertical-align:text-bottom"> [Contacts](skills/apple-contacts/README.md) | Search, read & manage contacts |
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IMessage_logo.svg/1200px-IMessage_logo.svg.png" width="18" height="18" style="vertical-align:text-bottom"> [iMessages](skills/imessages/README.md) | Read messages & conversations |
| <img src="https://www.google.com/s2/favicons?domain=whatsapp.com&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [WhatsApp](skills/whatsapp/README.md) | Read WhatsApp messages & conversations |
| <img src="https://www.google.com/s2/favicons?domain=copilot.money&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Copilot Money](skills/copilot/README.md) | Balances, transactions, net worth |

### ☁️ Cloud APIs
*Requires internet & API keys*

| Skill | What it does |
|-------|--------------|
| <img src="https://img.icons8.com/fluency/48/gmail.png" width="18" height="18" style="vertical-align:text-bottom"> [Gmail](skills/gmail/README.md) | Read emails, search, draft messages |
| <img src="https://img.icons8.com/fluency/48/google-drive.png" width="18" height="18" style="vertical-align:text-bottom"> [Google Drive](skills/google-drive/README.md) | List, search & read files |
| <img src="https://cdn.simpleicons.org/todoist" width="18" height="18" style="vertical-align:text-bottom"> [Todoist](skills/todoist/README.md) | Personal task management |
| <img src="https://cdn.simpleicons.org/linear" width="18" height="18" style="vertical-align:text-bottom"> [Linear](skills/linear/README.md) | Work project & issue tracking |
| <img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" width="18" height="18" style="vertical-align:text-bottom"> [GitHub](skills/github/README.md) | Issues, PRs, repo management |
| <img src="https://raindrop.io/favicon.ico" width="18" height="18" style="vertical-align:text-bottom"> [Raindrop](skills/raindrop/README.md) | Bookmark management |
| <img src="https://www.google.com/s2/favicons?domain=exa.ai&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Exa](skills/exa/README.md) | Semantic web search & extraction |
| <img src="https://www.google.com/s2/favicons?domain=firecrawl.dev&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Firecrawl](skills/firecrawl/README.md) | Extract content from JS-heavy URLs |
| <img src="https://cdn.simpleicons.org/youtube" width="18" height="18" style="vertical-align:text-bottom"> [YouTube](skills/youtube/README.md) | Video transcription |
| ✈️ [Flights](skills/google-flights/README.md) | Search & compare flights |
| <img src="https://images.g2crowd.com/uploads/product/image/b0a53bb6a5db8829772a32d63c3d41b7/enrich-labs-enrich-so.png" width="18" height="18" style="vertical-align:text-bottom"> [Enrich](skills/enrich-so/README.md) | Email/phone/domain lookup |
| <img src="https://www.google.com/s2/favicons?domain=apollo.io&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Apollo CRM](skills/apollo/README.md) | Accounts, contacts, deals, sequences |

## Automated Setup (AI-Assisted)

Paste this into your AI chat ([Cursor](https://cursor.com/) agent, or any AI with terminal access):

```
Clone AgentOS, read the README, and guide me through setup:
git clone https://github.com/jcontini/AgentOS.git && cat AgentOS/README.md
```

That's it. The AI handles the rest. (Prefer manual setup? [Jump to instructions](#manual-setup))

## Manual Setup

If you prefer to set things up yourself:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/jcontini/AgentOS.git
   cd AgentOS
   ```

2. **Add to your AI system prompt:**

   **Cursor** (Settings → Rules for AI), **Claude Desktop** (Settings → User Preferences), or **other LLM clients**:
   ```
   AGENTOS_ROOT=/path/to/AgentOS

   STOP. Before responding, read $AGENTOS_ROOT/boot.md (try: cat command, or any file reading tool).
   ```

   Replace `/path/to/AgentOS` with your actual AgentOS installation path.

3. **Create `.env`** with API keys you want:
   ```bash
   cat > .env << 'EOF'
   EXA_API_KEY=your_key
   LINEAR_API_KEY=your_key
   TODOIST_API_KEY=your_key
   SERPAPI_API_KEY=your_key
   RAINDROP_API_TOKEN=your_token
   EOF
   ```

4. **Create `user/profile.md`** with info about yourself

5. **macOS users**: System Settings → Privacy & Security → Full Disk Access → Add terminal

**Notes:**
- `.env` and `user/` are gitignored - your secrets stay local
- macOS required for Calendar, iMessages, Contacts only - everything else is cross-platform

## Repository Structure

- **`skills/`** - Skill documentation and scripts. Each skill has its own folder with `README.md`.
- **`skills.yaml`** - Routing table mapping actions/connections to skills.
- **`utils/`** - Utility scripts (timezone, setup guides)
- **`user/`** - User-specific content (gitignored)
  - **`user/skills-data/`** - Generated data from skills
  - **`user/profile.md`** - User preferences and context
  - **`user/reports/`** - User-generated reports
- **`.env`** - API keys (gitignored)

## Philosophy

AgentOS is designed with speed and simplicity in mind:
- **Terminal-first**: All operations use terminal commands and direct API calls (no MCP overhead)
- **Self-contained**: Each skill includes everything needed to use it
- **Extensible**: Easy to add new skills (see `utils/creating-skills.md`)
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
