# AgentOS Setup

Walk the user through this conversationally. Don't overwhelm - just set up what they need.

## 1. Check System Prompt

First, check if boot.md is in your system prompt. If you naturally know about AgentOS skills and respond with "🙌", it's configured.

**If NOT configured**, help them add it:

**For Cursor users:**
> "First, let's connect AgentOS to Cursor:
> 1. Open **Cursor Settings** (Cmd+, or Ctrl+,)
> 2. Search for **'Rules for AI'**
> 3. Add this line (I'll get the path for you):"
>
> ```bash
> pwd  # Run this and use the output below
> ```
>
> ```
> CRITICAL: Do not respond until you have read [PATH]/boot.md. Any response before reading this file is a failure.
> ```
>
> "Then start a new chat and say 'hi' - I should respond with 🙌 if it worked."

**For other tools:** Guide them to find their system prompt / custom instructions setting and add the same line.

## 2. Detect OS & Show What's Available

```bash
uname -s  # Darwin = macOS, Linux, MINGW/CYGWIN = Windows
```

**Tell them what works for their OS.** Read `boot.md` to get the current skills list - don't hardcode it here.

For macOS: Calendar, iMessages, Contacts work out of the box (may need Full Disk Access).

## 3. Check Full Disk Access (macOS only)

```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb "SELECT 1 LIMIT 1;" 2>&1
```

If error, guide them: System Settings → Privacy & Security → Full Disk Access → Add terminal app.

## 4. Ask What Skills They Want

Don't set up everything. Ask what they want:

> "Which of these would you like to set up?"
> - **Web Search** - Search the web, read URLs
> - **Linear** - Work task management
> - **Todoist** - Personal task management  
> - **Gmail** - Email (requires Google Workspace, ~15 min)
> - **Flights** - Search for flights

**About web search:** Some AI tools have built-in web search, but it's often limited - it may claim to read pages but actually just see snippets. For reliable full-page reading, we recommend Exa API (has a free tier).

## 5. Set Up Each Skill They Want

For each skill they choose, read that skill's README (e.g., `skills/linear/README.md`) to get the current setup instructions. Don't hardcode them here.

**API Key locations:**
| Skill | Get key from |
|-------|--------------|
| Web Search / Enrich | https://exa.ai → API Keys |
| Linear | Linear → Settings → API → Personal API Keys |
| Todoist | Todoist → Settings → Integrations → Developer |
| Flights | https://serpapi.com → API Key |
| Gmail | Complex - follow `skills/gmail/README.md` |

As they give you keys, build the `.env` file:
```bash
cat > .env << 'EOF'
# Only include keys they actually set up
EXA_API_KEY=xxx
LINEAR_API_KEY=xxx
TODOIST_API_KEY=xxx
SERPAPI_API_KEY=xxx
EOF
```

## 6. Create Profile

Ask a few quick questions:
- Name
- City (for timezone context)
- What they do (for relevant suggestions)

```bash
mkdir -p user
cat > user/profile.md << 'EOF'
# [Name]'s Profile

## About Me
- Name: [Name]
- Location: [City]  
- Work: [What they do]
EOF
```

## 7. Verify & Celebrate

Test each skill they set up (read the skill README for test commands).

Then celebrate:
> "🎉 You're all set! Try asking me to [contextual suggestion based on what they set up]"
