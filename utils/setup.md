# AgentOS Setup

Walk the user through this conversationally. Don't overwhelm - just set up what they need.

**Important:** Let users know they can skip anything and come back later:
> "You can skip any of these steps - just say 'skip'. You can always run setup again later by asking me to 'run setup' or 'continue setup'."

---

## Checking for Updates

When user asks to "check for updates" or "update AgentOS", run:
```bash
cd "$(dirname "$PROJECT_ROOT")" 2>/dev/null || cd .
git fetch origin main --quiet && git log HEAD..origin/main --oneline
```

- **If output is empty:** "You're up to date!"
- **If there are commits:** Show them what's new and offer to update:
  > "There are updates available:
  > [list commits]
  > 
  > Want me to update? This will run `git pull`."
  
  If yes: `git pull origin main`

**Don't check automatically** - only when they ask. Updates might have breaking changes they want to review first.

---

## 1. Check System Prompt

First, check if boot.md is in your system prompt. If you naturally know about AgentOS skills and respond with "🙌", it's configured.

**If NOT configured**, help them add it:

**For Cursor users:**

First, get the exact path and generate the line for them:
```bash
echo "CRITICAL: Do not respond until you have read $(pwd)/boot.md. Any response before reading this file is a failure."
```

Then guide them:
> "Here's the exact line to add. Copy this:
> 
> `[paste the output from above]`
>
> To add it:
> 1. Open **Cursor Settings** (Cmd+, or Ctrl+,)
> 2. Search for **'Rules for AI'**
> 3. Paste that line
> 4. Start a new chat and say 'hi' - I should respond with 🙌 if it worked."

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

Don't set up everything. Ask what they want, and explain what each enables:

> "Which of these would you like to set up? (You can skip all of these and add them later)"
>
> - **Web Search** - I can search the web and read full pages for you
> - **Linear** - I can check your work tasks, create issues, update status
> - **Todoist** - I can manage your personal tasks and to-dos
> - **Gmail** - I can read your email and draft responses
> - **Flights** - I can search for flights and compare prices

**Before offering Gmail setup, ask:**
> "Do you use Google Workspace (like a work email ending in @yourcompany.com), or regular personal Gmail (@gmail.com)?"

- **If Google Workspace:** Great, Gmail skill will work. Proceed with setup (~15 min).
- **If personal Gmail (@gmail.com):** 
  > "Unfortunately, the Gmail skill only works with Google Workspace accounts, not personal @gmail.com addresses. This is because it uses a service account which requires Workspace admin access. You can skip this one."

**If they skip all API keys:** The macOS skills (Calendar, iMessages, Contacts) still work. They just won't have web search, task management, email, or flight search until they add the API keys.

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

Build their profile conversationally. Start with essentials, offer to go deeper.

**If they want to skip:** Create a minimal profile with just their name. They can expand it later.

### Essential Questions (ask these)

> "A few quick questions so I can be more helpful (or say 'skip' and we can do this later):"

1. **"What's your name?"**

2. **"What city are you in?"** (for timezone, local suggestions)

3. **"What do you do for work?"** (founder, engineer, designer, etc.)

4. **"Do you have separate work and personal emails?"** 
   - If yes, get both (for Gmail skill routing)

5. **"How do you like me to communicate - brief and direct, or more detailed explanations?"**

### Optional Deeper Questions (offer these)

> "Want to add a bit more context? This helps me be more useful, but we can skip it."

If they say yes, pick a few relevant ones:

- **"Any current goals you're working toward?"** (health, career, learning, etc.)
- **"What does a typical day look like for you?"** (routine, meetings, etc.)
- **"Any tools you use daily?"** (task managers, note apps, etc.)
- **"Anything else that would help me understand your context?"**

### Build the Profile

Based on their answers, create a profile following this structure:

```bash
mkdir -p user
cat > user/profile.md << 'EOF'
# [Name]'s Profile

## About Me
- Location: [City]
- Work: [What they do]
- Emails: [work email], [personal email if different]

## Communication Preferences
- [Their preference - e.g., "Brief and direct" or "Detailed explanations"]

## Goals
- [Any goals they mentioned]

## Routine
- [Any routine info they shared]

## Tools
- [Tools they mentioned using]
EOF
```

> "I created your profile at `user/profile.md`. You can edit it anytime to add more context - things like your daily routine, current projects, or how you like certain tasks handled."

**For AI:** A well-developed profile might include sections like:
- Future (goals, travel plans)
- Present (living situation, work, routine, relationships, communities, tech environment)
- Past (background/timeline for context)
- AI User Manual (communication preferences, custom workflows)

Don't overwhelm new users with all this - start simple and they can expand over time.

## 7. Verify & Celebrate

Test each skill they set up (read the skill README for test commands).

Then celebrate and remind them about coming back:

> "🎉 You're all set! Try asking me to [contextual suggestion based on what they set up]"

If they skipped anything:
> "Whenever you want to add more skills, just say 'run setup' and we'll pick up where we left off."

Also mention:
> "If you have feedback, questions, or want to request a feature, just tell me and I can file a GitHub issue. (Requires the GitHub skill - see `skills/github/README.md`)"
