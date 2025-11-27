# AgentOS Setup Guide

**This is an AI-guided setup.** Read this file and walk the user through setup interactively.

## Setup Flow

### Step 1: Detect Environment

Run this to detect the user's OS:
```bash
uname -s
```

**Results:**
- `Darwin` = macOS
- `Linux` = Linux
- Contains `MINGW` or `CYGWIN` = Windows

### Step 2: Show Available Skills

Based on OS, tell the user what's available:

#### macOS Users
**Works out of the box (no setup needed):**
- 📅 Calendar - Read/manage calendar events
- 💬 iMessages - Read iMessages/SMS
- 👥 Contacts - Read/search/add/edit contacts
- ▶️ YouTube - Transcribe videos (needs `yt-dlp` - will prompt to install)

**Requires API keys:**
- 🔍 Web Search - Search the web, read URLs (Exa API)
- 📋 Linear - Work project management
- ✅ Todoist - Personal task management
- 📧 Gmail - Email access (Google Workspace + service account)
- 🔎 Enrich - Research email/phone/domain (Exa API)
- ✈️ Flights - Search for flights (SerpAPI)

**Requires browser MCP:**
- 🌐 Browser Automation - Control web browser

#### Linux/Windows Users
**Works out of the box:**
- ▶️ YouTube - Transcribe videos (needs `yt-dlp`)

**Requires API keys:**
- 🔍 Web Search - Search the web, read URLs (Exa API)
- 📋 Linear - Work project management
- ✅ Todoist - Personal task management
- 📧 Gmail - Email access (Google Workspace + service account)
- 🔎 Enrich - Research email/phone/domain (Exa API)
- ✈️ Flights - Search for flights (SerpAPI)

**Requires browser MCP:**
- 🌐 Browser Automation - Control web browser

**Not available (macOS only):**
- ❌ Calendar, iMessages, Contacts - These use macOS-specific databases

### Step 3: Check Prerequisites

#### For macOS users, check Full Disk Access:
Some skills need Full Disk Access for the terminal. Check if it's needed:
```bash
# Test calendar access
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb "SELECT COUNT(*) FROM CalendarItem LIMIT 1;" 2>&1
```

If this returns an error about permissions, tell the user:
> "To use Calendar, iMessages, and Contacts, you need to grant Full Disk Access to your terminal app:
> 1. Open System Settings → Privacy & Security → Full Disk Access
> 2. Click the + button and add Terminal.app (or your terminal emulator like iTerm, Warp, etc.)
> 3. Restart your terminal"

#### Check for yt-dlp (YouTube skill):
```bash
which yt-dlp
```
If not found, offer to install:
```bash
brew install yt-dlp  # macOS
# or: pip install yt-dlp
```

### Step 4: Set Up API Keys

Create or update the `.env` file. Guide the user through each one they want:

```bash
# Check if .env exists
cat "$PROJECT_ROOT/.env" 2>/dev/null || echo "No .env file yet"
```

#### API Key Reference

| Skill | Env Variable | How to Get |
|-------|--------------|------------|
| Web Search | `EXA_API_KEY` | https://exa.ai → Sign up → API Keys |
| Linear | `LINEAR_API_KEY` | Linear → Settings → API → Personal API Keys |
| Todoist | `TODOIST_API_KEY` | Todoist → Settings → Integrations → Developer → API token |
| Enrich | `EXA_API_KEY` | Same as Web Search (uses Exa) |
| Flights | `SERPAPI_API_KEY` | https://serpapi.com → Sign up → API Key |

#### Gmail Setup (More Complex)

Gmail requires Google Workspace with a service account. Ask if they want to set this up:

> "Gmail setup requires:
> 1. A Google Workspace account (not regular Gmail)
> 2. Admin access to create a service account
> 3. Domain-wide delegation configuration
> 
> This takes about 10-15 minutes. Want to set it up now?"

If yes, guide them through `skills/gmail/README.md` setup steps.

### Step 5: Create .env File

Help them create the `.env` file with their keys:

```bash
cat > "$PROJECT_ROOT/.env" << 'EOF'
# AgentOS Environment Variables
# Add your API keys below

# Exa API (for Web Search and Enrich skills)
EXA_API_KEY=

# Linear API (for work project management)
LINEAR_API_KEY=

# Todoist API (for personal task management)  
TODOIST_API_KEY=

# SerpAPI (for flight search)
SERPAPI_API_KEY=

# User email for Gmail (Google Workspace)
GMAIL_USER_EMAIL=
EOF
```

Then have them fill in each key they obtained.

### Step 6: Verify Setup

Test each configured skill:

**Web Search:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "numResults": 1}' | head -c 200
```

**Linear:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}' | head -c 200
```

**Todoist:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_KEY" | head -c 200
```

**Gmail:**
```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user "$GMAIL_USER_EMAIL" list --max-results 1
```

### Step 7: Create User Profile

Help them create their profile for personalization:

```bash
mkdir -p "$PROJECT_ROOT/user"
cat > "$PROJECT_ROOT/user/profile.md" << 'EOF'
# My Profile

## About Me
- Name: [Your name]
- Location: [City, timezone]
- Work: [What you do]

## Preferences
- [Add your preferences here]

## Workflows
- [Add custom workflows here]
EOF
```

Tell them they can customize this file to help the AI understand their context better.

### Step 8: Summary

At the end, summarize what's set up:

```
✅ Setup Complete!

Working skills:
- [List skills that are ready]

Skills needing setup:
- [List skills still needing API keys]

Next steps:
- Read boot.md to understand how to use skills
- Customize user/profile.md with your preferences
- Try asking me to help with tasks!
```

## Interactive Prompts

Use these conversation patterns:

**Starting setup:**
> "Let me help you set up AgentOS. First, let me check your system..."

**After OS detection:**
> "You're on [macOS/Linux/Windows]. Here's what works for you:
> - These skills work out of the box: [list]
> - These need API keys: [list]
> 
> Want me to help you set up the API keys now?"

**For each API key:**
> "[Skill name] needs an API key from [service].
> 1. Go to [URL]
> 2. [Steps to get key]
> 3. Copy the key and paste it here
> 
> (Or type 'skip' to set this up later)"

**When skipping:**
> "No problem! You can set this up later by adding [ENV_VAR] to your .env file."

**Completion:**
> "All done! You now have [X] skills ready to use. Try asking me to [example task]!"

