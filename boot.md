# Instructions for AI Assistants
You are operating within AgentOS at `/Users/joe/dev/ai/` - always start here.
To confirm you read this file, prefix first response with "🙌".

## Using Tools & MCPs
You may need tools to to execute the playbooks. Instead of saying that you are unable to do something, try to use MCPs. 
If you don't have access to one, do some web research, and propose installing one.
   - [Context7 MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/context7) // API & library documentation lookup
   - [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp) // Adding events 
   - [Tavily MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/tavily) // Web search, crawling, content extraction
   - [Todoist MCP](https://github.com/Doist/todoist-mcp) // Task management
   - [Contacts MCP](https://github.com/jcontini/macos-contacts-mcp) // Contacts management

When using a tool to create or find any external resource (task, event, webpage, etc), show the url in the response so I can click it easily.

## Using the web
- When I ask you for information about anything:
  - Always search the web to get latest context. Do not rely on your training data.
  - If I ask you to find something on a specific site (eg YouTube, Github), use the site:filter in the query

- When I give you a specific URL to read:
  - First, use the web search MCP (eg Tavily) with settings:
    - `extract_depth`: "advanced" 
    - `format`: "markdown"
  - If the MCP doesn't work:
    - Try `curl -s [URL]` to get raw HTML
    - Pipe through `grep` or other text processing tools
    - Useful for: footer content, embedded links, metadata, social media links

## Using the terminal
- **NEVER use `grep` or `find` to locate files.** Always use `tree -L 3` instead. It is much faster and more reliable.

## Writing & Editing code
When using an IDE like Cursor or VSCode:
- When working in a repo
  - Never commit unless I ask you to
  - Check the README to get context
  - When committing
    - If the commit is rejected due to convention, try again with the proper convention

- If you run into even 1 issue using a library/api,
  - Use Context7 MCP to find & read the latest docs for the challenging lib
  - If you can't find it there, use web search to try and find the lib/api documentation

- Always
  - Seek to minimize duplicate code. 
  - Prioritize simple solutions over complex ones
  - Think twice before creating extra files. Practice DRY, YAGNI principles.

## Writing reports
When I ask you to create a report:

1. Read my profile to get more context on me
2. Run `date +%Y-%m-%d` to get current date for filename
3. Create markdown report in `user/reports/` folder
4. Use lowercase filename with underscores (e.g., `YYYY-MM-DD_report-topic.md`)
5. Follow structure: Summary → Key Findings → Detailed Sections → Sources

## Installing Anything (Plugins, Extensions, Libraries, MCPs)

1. **Find the Source**
   - Use the official repo (e.g., GitHub). Avoid unverified intermediaries.
   - Abort if anything looks suspicious (name mismatch, publisher, abandoned repo, etc.).

2. **Check Install Methods**
   - Prefer official install scripts or modern package managers (UV for Python, NPM/Yarn for Node, etc.).
   - Review scripts for safety before running.

3. **Install**
   - Use user-level, reproducible installs. Pin versions when possible.
   - Example: `uv pip install --user <package>==<version>` or `npm install --global <package>@<version>`.

4. **Verify & Configure**
   - Confirm install and version (`<cmd> --version`).
   - Ensure the binary is in your `$PATH` and update config files with the full path if needed.

5. **Cleanup & Rollback**
   - Remove old installs to avoid conflicts. Uninstall with the same tool if needed.

## Scripts
Commands run from `/Users/joe/dev/ai/`. Do not run `cd`, `pwd`, or any command to inspect or change directories unless I explicitly tell you to. 

**Script locations:**
- General scripts: `/Users/joe/dev/ai/scripts/` - always use full absolute paths like `/Users/joe/dev/ai/scripts/script-name.sh`
- User-specific scripts: `/Users/joe/dev/ai/user/scripts/` - for personal scripts like backups, local schedules, etc.

### Handling YouTube links
- **When to use:** I provide a YouTube link and ask for transcript or video download
- **Actions:**
  - **Transcript only:** `/Users/joe/dev/ai/scripts/youtube-transcript.sh "[YOUTUBE_URL]"`
  - **Video + transcript:** `/Users/joe/dev/ai/scripts/youtube-transcript.sh "[YOUTUBE_URL]" --video`
- **Output locations:** `/Users/joe/dev/ai/user/youtube/transcripts/` and `/Users/joe/dev/ai/user/youtube/videos/`

### Enrich person or company information
- **When to use:** Need to lookup contact details, company info, or validate emails/domains/LinkedIn profiles
- **Actions:**
  - **Email to profile:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com"` (default)
  - **Email to phone:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com" --type phone`
  - **Check disposable email:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com" --type disposable`
  - **Domain to company:** `/Users/joe/dev/ai/scripts/enrich.sh --domain "company.com"` (default)
  - **Domain to logo:** `/Users/joe/dev/ai/scripts/enrich.sh --domain "company.com" --type logo`
  - **IP to company:** `/Users/joe/dev/ai/scripts/enrich.sh --ip "1.2.3.4"`
  - **LinkedIn person profile:** `/Users/joe/dev/ai/scripts/enrich.sh --linkedin "linkedin.com/in/username"` (default: person)
  - **LinkedIn company profile:** `/Users/joe/dev/ai/scripts/enrich.sh --linkedin "linkedin.com/company/companyname" --type company`
- **Output:** JSON data to stdout (parse for structured information)
- **Requirements:** ENRICH_SO_API_KEY set in .env file
