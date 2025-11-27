# AgentOS

> **First run?** Check: `[ -f .env ] && [ -f user/profile.md ] || echo "NEEDS_SETUP"`
> If needs setup, read `utils/setup.md` and guide the user through it.

## Available Skills

- [**Web Search**](skills/web-search/README.md) - Search the web, read URLs
- [**Browser**](skills/browser/README.md) - Control web browser
- [**Linear**](skills/linear/README.md) - Work project management
- [**Todoist**](skills/todoist/README.md) - Personal task management
- [**Gmail**](skills/gmail/README.md) - Email (Google Workspace only)
- [**Calendar**](skills/calendar/README.md) - Read/manage calendar (macOS)
- [**iMessages**](skills/imessages/README.md) - Read iMessages/SMS (macOS)
- [**Contacts**](skills/contacts/README.md) - Read/manage contacts (macOS)
- [**YouTube**](skills/youtube/README.md) - Transcribe videos
- [**Enrich**](skills/enrich/README.md) - Research email/phone/domain
- [**Flights**](skills/flights/README.md) - Search for flights
- [**GitHub**](skills/github/README.md) - Manage issues, PRs, repos

**Utilities:**
- [**Timezone**](utils/README.md) - Timezone conversion
- [**Creating Skills**](utils/creating-skills/README.md) - Guide to adding new skills

When you need to perform any of these tasks, read the corresponding file for instructions.

**Understanding SDKs/libraries/APIs:** Use [Web Search](skills/web-search/README.md) to find documentation.

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

