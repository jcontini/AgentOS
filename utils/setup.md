# AgentOS Setup Guide

**This is an AI-guided setup.** Walk the user through this conversationally. Be friendly and helpful.

## Opening

Start with:
> "🙌 Welcome to AgentOS! I'm going to help you get set up. This will only take a few minutes.
>
> Let me check your system first..."

## Step 1: Detect Environment

```bash
uname -s
```

- `Darwin` = macOS → "Great, you're on macOS! You get access to all the cool native integrations."
- `Linux` = Linux → "You're on Linux - most skills will work great for you."
- `MINGW`/`CYGWIN` = Windows → "You're on Windows - I'll show you what works for you."

## Step 2: Show What's Available

Based on their OS, give them a quick overview:

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

## Step 3: Check Prerequisites (macOS)

For macOS users, silently test if Full Disk Access is needed:
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb "SELECT COUNT(*) FROM CalendarItem LIMIT 1;" 2>&1
```

If this returns an error, tell them:
> "Quick thing - to use Calendar, iMessages, and Contacts, your terminal needs Full Disk Access:
> 1. Open **System Settings → Privacy & Security → Full Disk Access**
> 2. Click **+** and add your terminal app (Terminal, iTerm, Warp, etc.)
> 3. Restart your terminal and come back
>
> Let me know when you're ready!"

## Step 4: Ask What They Want to Set Up

> "Now let's set up the skills you want to use. Which of these interest you?
>
> **Quick setup (just need an API key):**
> - 🔍 **Web Search** - Search the web, read any URL (Exa API - free tier available)
> - 📋 **Linear** - Work project management 
> - ✅ **Todoist** - Personal task management
> - ✈️ **Flights** - Search for flights (SerpAPI)
>
> **More involved setup:**
> - 📧 **Gmail** - Email access (needs Google Workspace, ~15 min setup)
>
> Which would you like to set up? (You can always add more later)"

Based on their answer, guide them through just those. Don't overwhelm with everything.

### API Key Quick Reference

| Skill | Steps |
|-------|-------|
| **Web Search** | Go to https://exa.ai → Sign up → Copy API key |
| **Linear** | Linear app → Settings → API → Create personal API key |
| **Todoist** | Todoist → Settings → Integrations → Developer → Copy API token |
| **Flights** | Go to https://serpapi.com → Sign up → Copy API key |

For each one they want, guide them:
> "Let's set up [Skill]. 
> 1. Go to [URL]
> 2. [Sign up / log in]
> 3. Copy your API key and paste it here"

### Gmail (If They Want It)

> "Gmail setup is a bit more involved - it needs Google Workspace (not regular Gmail) and takes about 15 minutes. Want to do this now, or save it for later?"

If yes, read and follow `skills/gmail/README.md` setup steps with them.

## Step 5: Save Their Keys

As they give you each key, build the `.env` file:

```bash
cat > "$PROJECT_ROOT/.env" << 'EOF'
# AgentOS Environment Variables

# Exa API (Web Search, Enrich)
EXA_API_KEY=their_key_here

# Linear API  
LINEAR_API_KEY=their_key_here

# Todoist API
TODOIST_API_KEY=their_key_here

# SerpAPI (Flights)
SERPAPI_API_KEY=their_key_here

# Gmail user email (Google Workspace)
GMAIL_USER_EMAIL=their_email_here
EOF
```

Only include the keys they actually set up. Remove the others.

## Step 6: Quick Test

For each skill they set up, run a quick test and show them it works:

**Web Search:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "numResults": 1}' | head -c 200
```
> "✅ Web Search is working!"

**Linear:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}' | head -c 200
```
> "✅ Linear is connected!"

**Todoist:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_KEY" | head -c 200
```
> "✅ Todoist is working!"

If any fail, help them troubleshoot (usually a typo in the key).

## Step 7: Create Their Profile

> "Last step! Let me create a profile so I can personalize things for you. What's your name?"

After they answer, ask a couple more optional questions:
- "What city are you in?" (for timezone/local context)
- "What kind of work do you do?" (for relevant suggestions)

Then create their profile:

```bash
mkdir -p "$PROJECT_ROOT/user"
cat > "$PROJECT_ROOT/user/profile.md" << 'EOF'
# [Name]'s Profile

## About Me
- Name: [Name]
- Location: [City]
- Work: [What they do]

## Preferences
- [Can add more later]
EOF
```

> "You can always add more to this file later - things like your daily routine, goals, or how you like me to communicate."

## Step 8: Celebrate & Suggest First Task

End on a high note with a summary and suggestion:

> "🎉 **You're all set up!**
>
> **Ready to use:**
> - [List their working skills with emoji]
>
> **Try asking me to:**
> - [Contextual suggestion based on what they set up]"

### Example Endings

**macOS user with Todoist:**
> "🎉 You're all set up!
>
> **Ready to use:** 📅 Calendar, 💬 iMessages, 👥 Contacts, ✅ Todoist
>
> Try asking me: *'What's on my calendar today?'* or *'Show me my Todoist tasks'*"

**User with Linear + Web Search:**
> "🎉 You're all set up!
>
> **Ready to use:** 🔍 Web Search, 📋 Linear
>
> Try asking me: *'What are my Linear tasks this week?'* or *'Search for the latest news on [topic]'*"

**Minimal setup (no API keys):**
> "🎉 You're all set up with the basics!
>
> **Ready to use:** 📅 Calendar, 💬 iMessages, 👥 Contacts
>
> Try asking me: *'What's on my calendar today?'* or *'Show me recent messages from [name]'*
>
> When you want to add more skills like web search or task management, just ask!"

---

## Tips for Good Setup Experience

1. **Don't overwhelm** - Only set up what they want now. They can add more later.
2. **Test as you go** - Verify each skill works before moving on.
3. **Be encouraging** - Celebrate small wins ("✅ That's working!")
4. **Offer escape hatches** - Let them skip things and come back later.
5. **End with action** - Give them something to try immediately.

