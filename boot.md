# Instructions for AI Assistants

Study the playbooks below, and prepare to use them when appropriate.
To confirm you read this file, prefix first response with "🙌".

# Playbooks

## Getting user context / profile

**When to use:** User asks you to read specific context (personal, work, profile, etc)

**Actions:** Read profile.md in the same directory

---

## Writing reports

**When to use:** User asks for a report, analysis, or research summary

**Actions:**
1. Create markdown report in `content/reports/` folder
2. Use lowercase filename with underscores (e.g., `YYYY-MM-DD_report-topic.md`)
3. Follow structure: Summary → Key Findings → Detailed Sections → Sources


## Creating events
After creating calendar events, present them using this structured format:

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

## Searching the web

When user mentions specific platforms, optimize search strategy:
- **Domain focus:** Restrict to target site (youtube.com, github.com, docs.site.com, etc.)
- **Search quality:** Use advanced/deep search options when available
- **Result limits:** 3-5 results for specific searches, more for research
- **Score analysis:** Higher relevance scores usually indicate target content

---

## Getting the news

Use a web search tool to get news on these topics:

**Core:** Tech/AI breakthroughs, major investments, geopolitics
**Citizenship/Residency:** Policy changes, golden visas, digital nomad programs, permanent residency laws
**Exclude:** Student/work visas, routine immigration processing

Lead with significant developments, organize by category, use inline linking to sources.

```
## Technology
- [Article](link)
## Geopolitics
- [Article](link)
``` 

---

## Handling YouTube links
- **When to use:** User provides a YouTube link and asks for transcript or video download. 
- **Working directory:** Ensure you're in the working directory (where boot.md is located)
- **Actions:**
  - **Transcript only:** `./scripts/youtube-transcript.sh "[YOUTUBE_URL]"`
  - **Video + transcript:** `./scripts/youtube-transcript.sh "[YOUTUBE_URL]" --video`
- **Output locations:** `content/youtube/transcripts/` and `content/youtube/videos/`

---

## Installing anything from the internet (plugins, extensions, libraries, MCPs)

- **Rule 0**: No `curl | bash`. Present a plan before executing.
- **Verify identity**: Exact name matches official docs; maintainer/org match; healthy activity.
- **Plan**: name, ecosystem, official URL, version (pin), exact commands, install scope.
- **Execute**: Use non-interactive flags; pin versions (npm/pnpm/yarn exact, pip `==`, brew formula).
- **Untrusted/new**: Clone to temp and scan for postinstall/eval/network/fs/obfuscation/native bins.
- **MCP locations**: Cursor global `~/.cursor/mcp.json`; workspace `.cursor/mcp.json`; Claude `~/Library/Application Support/Claude/claude_desktop_config.json`.
- **MCP edit**: Propose minimal JSON diff first; then apply; restart client.
- **Verify**: `npm ls <pkg>` / `uv pip show <pkg>` / `brew info <formula>` / `<cmd> --version`.
- **Rollback**: `npm uninstall` / `uv pip uninstall` / `brew uninstall` / revert JSON edits.
- **Auto-fail**: name mismatch, suspicious postinstall, publisher mismatch, abandoned repo.

## Using Tools
You may need tools to to execute the playbooks. Instead of saying that you are unable to do something:

1. Try to use MCPs. If you don't have access to one, propose installing one to the user.
   - [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) // Adding events 
   - [Tavily MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/tavily) // Web search, crawling, content extraction
   - [Desktop Commander MCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) // Terminal & file access
   - [Todoist MCP](https://github.com/Doist/todoist-mcp) // Task management
   - [Contacts MCP](https://github.com/jcontini/macos-contacts-mcp) // Contacts management
2. Try to use the script in {WORKING_DIR} as instructed, eg `cd {WORKING_DIR} && ./scripts/{script w params}`

When using a tool to create an external resource (task, calendar event, etc), give user a link to the created resource, eg [Task Name](link-to/task-id).
