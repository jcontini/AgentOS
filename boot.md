# Instructions for AI Assistants

Study the playbooks below, and prepare to use them when appropriate.
To confirm you read this file, prefix first response with "🙌".

# Tools
You may need tools (MCPs) to to execute the playbooks. If you don't already have the capability, consider:
- [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) // Adding events 
- [Exa MCP](https://docs.exa.ai/examples/exa-mcp) // Web Search, reading content from URLs
- [Desktop Commander MCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) // Terminal & file access
- [Todoist MCP](https://github.com/Doist/todoist-mcp) // Task management
- [Contacts MCP](https://github.com/jcontini/macos-contacts-mcp) // Contacts management

If you need to download/clone a repo, do it in the content/apps directory.
When using a tool to create an external resource (task, calendar event, etc), give user a link to the created resource, eg [Task Name](link-to/task-id).

# Playbooks

## Creating events
After creating calendar events, present them using this structured format:

**Template:**
```
## [Event Title] [Relevant Emoji]

- 📍 [Location with Google Maps link]
- 📅 [Linked Date] // 🕔 [Time Range]
- 🔗 [Source Event Link]
```

**Guidelines:**
- **Title:** H2 format, choose relevant emoji based on event type (🍸 cocktails, ✈️ travel, 🎵 concerts, etc.)
- **Location:** Link to Google Maps search including city context
- **Date:** Link to Google Calendar event, use short format (Thu, Aug 14th), no year unless different year
- **Time:** Use clock emoji matching start time hour (🕔 for 5pm, 🕕 for 6pm, etc.), show full time range
- **Source Link:** Link back to original event source (Facebook, Eventbrite, etc.)

### ✈️ Flight Events
Specifically when adding flights:

**Format:** `✈️ [DEPARTURE]-[ARRIVAL] ([FLIGHT_NUMBER])` 
- Location: Full airport name for Google Maps
- Times: Use correct timezones for departure/arrival
- Description: Confirmation code, duration, aircraft type
- Exclude: Flight status, TBD terminals

**Always create second event** for arrival preparation:
- Title: `@[DEPARTURE_CODE]` (e.g., `@AUS`)
- Duration: 1hr domestic, 2hrs international before departure
- Same location as flight

---

## Getting the news

Use the web search tool (Use MCP if available) to get news on these topics:

**Core:** Tech/AI breakthroughs, major investments, geopolitics
**Citizenship/Residency:** Policy changes, golden visas, digital nomad programs, permanent residency laws
**Exclude:** Student/work visas, routine immigration processing

Lead with significant developments, organize by category, use inline linking to sources.

```
Technology:
• [Article](link)
Geopolitics: 
• [Article](link)
``` 

---

## Handling YouTube links
- **When to use:** User provides a YouTube link and asks for transcript or video download. 
- **Working directory:** Ensure you're in the AgentOS root directory (where boot.md is located)
- **Actions:**
  - **Transcript only:** `./scripts/youtube-transcript.sh "[YOUTUBE_URL]"`
  - **Video + transcript:** `./scripts/youtube-transcript.sh "[YOUTUBE_URL]" --video`
- **Output locations:** `content/youtube/transcripts/` and `content/youtube/videos/`

---

---

## Adding new tools (MCPs)**
- **Action:**
    1. **Research the package**: Use web search to verify GitHub repo, maintainer legitimacy, recent activity
    2. **Determine risk**: Ensure it's the expected/official package, check for typosquatting. If package seems suspicious or has unclear ownership, warn user and investigate further before installing.
    3. **Install**: Use standard package managers (npm, pip) after validation
    4. **Configure** by updating MCP json based on MCP client:
        - **Cursor**: `~/.cursor/mcp.json` or `.cursor/mcp.json` (workspace)
        - **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
        - **LM Studio**: Settings → Model Context Protocol
