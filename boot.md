# AgentOS

> **First run?** Check: `[ -f .env ] && [ -f user/profile.md ] || echo "NEEDS_SETUP"`
> If needs setup, read `utils/setup.md` and guide the user through it.

## Available Skills

- <img src="https://www.google.com/s2/favicons?domain=exa.ai&sz=64" width="16" height="16" style="vertical-align:text-bottom"> [**ExaSearch**](skills/search/README.md) - Semantic web search, discover URLs (Exa)
- <img src="https://www.google.com/s2/favicons?domain=firecrawl.dev&sz=64" width="16" height="16" style="vertical-align:text-bottom"> [**Firecrawl Extract**](skills/extract/README.md) - Extract content from URLs (Exa → Firecrawl fallback)
- <img src="https://cdn.simpleicons.org/linear" width="16" height="16" style="vertical-align:text-bottom"> [**Linear**](skills/linear/README.md) - Work project management
- <img src="https://cdn.simpleicons.org/todoist" width="16" height="16" style="vertical-align:text-bottom"> [**Todoist**](skills/todoist/README.md) - Personal task management
- <img src="https://www.google.com/s2/favicons?domain=copilot.money&sz=64" width="16" height="16" style="vertical-align:text-bottom"> [**Copilot Money**](skills/copilot/README.md) - Personal finance, balances, transactions (macOS)
- <img src="https://img.icons8.com/fluency/48/gmail.png" width="16" height="16" style="vertical-align:text-bottom"> [**Gmail**](skills/google-workspace/README.md) - Read emails, search messages, create drafts
- <img src="https://img.icons8.com/fluency/48/google-drive.png" width="16" height="16" style="vertical-align:text-bottom"> [**Google Drive**](skills/google-workspace/README.md) - List files, search files, read file content
- <img src="https://upload.wikimedia.org/wikipedia/commons/1/1c/MacOSCalendar.png" width="16" height="16" style="vertical-align:text-bottom"> [**Calendar**](skills/calendar/README.md) - Read/manage calendar (macOS Native)
- <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IMessage_logo.svg/1200px-IMessage_logo.svg.png" width="16" height="16" style="vertical-align:text-bottom"> [**iMessages**](skills/imessages/README.md) - Read iMessages/SMS (macOS Native)
- <img src="https://www.google.com/s2/favicons?domain=whatsapp.com&sz=64" width="16" height="16" style="vertical-align:text-bottom"> [**WhatsApp**](skills/whatsapp/README.md) - Read WhatsApp messages (macOS Native)
- <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Contacts_%28iOS%29.png" width="16" height="16" style="vertical-align:text-bottom"> [**Contacts**](skills/contacts/README.md) - Read/manage contacts (macOS Native)
- <img src="https://cdn.simpleicons.org/youtube" width="16" height="16" style="vertical-align:text-bottom"> [**YouTube**](skills/youtube/README.md) - Transcribe videos
- <img src="https://images.g2crowd.com/uploads/product/image/b0a53bb6a5db8829772a32d63c3d41b7/enrich-labs-enrich-so.png" width="16" height="16" style="vertical-align:text-bottom"> [**Enrich**](skills/enrich/README.md) - Research email/phone/domain
- ✈️ [**Flights**](skills/flights/README.md) - Search for flights
- <img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" width="16" height="16" style="vertical-align:text-bottom"> [**GitHub**](skills/github/README.md) - Manage issues, PRs, repos
- <img src="https://raindrop.io/favicon.ico" width="16" height="16" style="vertical-align:text-bottom"> [**Raindrop**](skills/raindrop/README.md) - Manage bookmarks and collections
- <img src="https://www.google.com/s2/favicons?domain=apollo.io&sz=64" width="16" height="16" style="vertical-align:text-bottom"> [**Apollo CRM**](skills/apollo/README.md) - Read accounts, contacts, deals, sequences, tasks, calls

**Utilities:**
- [**Timezone**](utils/README.md) - Timezone conversion
- [**Creating Skills**](utils/creating-skills.md) - Guide to adding new skills

When you need to perform any of these tasks, read the corresponding file for instructions.

**Understanding SDKs/libraries/APIs:** Use [ExaSearch](skills/search/README.md) to find documentation.

## Search vs Extract

**Decision tree for web tasks:**

```
Need to FIND information or discover URLs?
  → Use search/ (Exa semantic search)

Have specific URLs to read/extract content from?
  → Use extract/ (Exa first, Firecrawl fallback)
     Firecrawl when: Exa fails, JS-heavy site, need more content
```

| Task | Skill | API |
|------|-------|-----|
| Research a topic | `search/` | Exa |
| Find documentation | `search/` | Exa |
| Discover niche content | `search/` | Exa (neural) |
| Read a specific URL | `extract/` | Exa → Firecrawl |
| Scrape JS-heavy site (Notion, React) | `extract/` | Firecrawl |

**⚠️ Always surface API errors to the user** - credit exhaustion (402), rate limits (429), auth failures (401). Don't silently fail.

**When an API fails due to credits/limits:** Tell the user and ask if you should try an alternative. Many skills have fallbacks (e.g., Exa → Firecrawl for search). Don't assume - ask.

## Browser Tool Usage

**⚠️ CRITICAL: Do NOT use the browser tool unless the user explicitly asks you to.**

**Preferred approach for web research:**
1. **First:** Use [ExaSearch](skills/search/README.md) for semantic web search and finding information
2. **Second:** Use [Firecrawl Extract](skills/extract/README.md) for extracting content from specific URLs (Exa first, Firecrawl as fallback)
3. **Last resort only:** Browser tool - only if user explicitly requests it or if Exa/Firecrawl both fail and user needs interactive browsing

**Why:** Exa and Firecrawl are faster, more reliable, and don't require interactive browser sessions. The browser tool should only be used when absolutely necessary (e.g., user explicitly asks to browse a site, or interactive actions are required that APIs cannot handle).

## Terminal Usage & Best Practices

**We use terminal commands and direct API calls instead of MCPs to maximize speed.** Everything runs through the terminal. Optimize for minimal latency by combining operations.

### Core Principles

- **Chain commands** - Combine operations in single calls using `&&`, `||`, `|`, `;`
- **Use absolute paths** - Always use `$PROJECT_ROOT` variable (e.g., `$PROJECT_ROOT/skills/enrich/enrich.sh`). Avoid `cd` unless necessary.
- **Source env in same call** - Combine `.env` sourcing with command execution
- **Batch API calls** - Use list endpoints and caching instead of loops
- **Use `tree` for file exploration** - `tree -a -L N` (include hidden files). **NEVER use `find` or `grep` to locate files** - `tree` is much faster.

### Project Root

**Define once at session start:**
```bash
PROJECT_ROOT="/path/to/your/project"  # Or: PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
```

### Environment Variables

**All API keys/credentials in `.env` at `$PROJECT_ROOT/.env`.** Always source in the same call as your command:

```bash
# ✅ CORRECT: Source + execute in one call
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -H "x-api-key: $EXA_API_KEY" https://api.exa.ai/search

# ❌ WRONG: Split calls add latency
set -a && source "$PROJECT_ROOT/.env" && set +a
curl ...  # Separate call!
```

**Note:** Use variable references (`$LINEAR_API_KEY`), never hardcode secrets.

### API Querying Patterns

**Minimize calls by batching, caching, and combining:**

- **Batch queries** - `GET /items?ids=1,2,3` instead of loops
- **Cache results** - `curl ... > /tmp/data.json && jq ... /tmp/data.json` (one call)
- **Combine operations** - Source + curl + parse in one terminal call
- **Reuse data** - Don't re-query what you already have

**Example:** Instead of `for id in 1 2 3; do curl .../items/${id}; done` (3+ calls), use `curl .../items?limit=10 > /tmp/items.json && jq ... /tmp/items.json` (1 call).

### Data Storage

- **Skills data**: Store generated data in `$PROJECT_ROOT/user/skills-data/` (gitignored)

### Timezone Conversion

**Always convert UTC timestamps to local timezone when displaying to user.** See `utils/README.md` for detailed usage instructions. The timezone utility provides functions: `utc_to_local()`, `utc_to_local_date()`, `utc_to_local_time()`. Automatically detects system timezone.

---

## Repository Structure

**This is an open-source repository.** The structure is organized as follows:

- **`user/` folder**: Contains user-specific content (personal files, preferences, skills, reports). This folder is for individual user customization and should not be shared publicly.
  - **`user/skills/`**: User-specific skills with their own folders and READMEs (mirrors `skills/` structure)
  - **`user/reports/`**: User-generated reports and analysis
- **`skills/` folder**: Contains skill documentation and scripts. Each skill has its own folder with `README.md` and supporting files (scripts, configs, etc.). This is system/public content that should be part of the open-source repository.
- **`utils/` folder**: Utility scripts used across skills (e.g., timezone conversion). These are supporting infrastructure, not user-facing skills. See `utils/README.md` for documentation.

When creating or referencing user-specific files, always place them in the `user/` folder or its subdirectories.

### Creating Reports

**When creating reports in `user/reports/`, use shell command substitution to generate the date automatically in the filename:**

**⚠️ CRITICAL: The `write` tool does NOT evaluate shell command substitution.** You must use shell commands (`run_terminal_cmd` with `cat >` or heredoc) to create date-stamped filenames.

**⚠️ IMPORTANT:**
- **DO NOT manually type dates** - LLMs often don't have accurate date context
- **DO NOT include dates in the file content** - The filename date is the source of truth
- **Always use shell date command** - `$(date +"%Y-%m-%d")` evaluated in shell ensures accuracy
- **Use `run_terminal_cmd` with shell commands** - The `write` tool treats `$(date ...)` as literal text

**Example:**
```bash
# ✅ CORRECT: Use shell command with date substitution
cat > "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-report-name.md" << 'EOF'
# Report Title

Content here without dates...
EOF

# ✅ CORRECT: Alternative using echo (for shorter content)
echo "# Report Title

Content here" > "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-report-name.md"

# ❌ WRONG: Using write tool (date substitution won't work)
write "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-report.md" "Content"
# This creates a file literally named: $(date +"%Y-%m-%d")-report.md

# ❌ WRONG: Manual date (LLM may get it wrong)
write "$PROJECT_ROOT/user/reports/2025-01-30-report.md" "# Report Title

Date: January 30, 2025  ← Don't include dates in content!"
```

## Before Responding

**Read `user/profile.md`** for user context, preferences, and workflows.

**Prefix your first response with "🙌"** to confirm you read this file.

