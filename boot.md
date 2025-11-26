# Skills and How to Use Them

## Available Skills

- **Search the web / Read URLs** → `skills/web-search.md`
- **Manage calendar events** → `skills/calendar/README.md`
- **Task management / Linear** → `skills/linear/README.md`
- **Personal task management / Todoist** → `skills/todoist/README.md`
- **Get or manage contacts** → `skills/contacts.md`
- **Handle YouTube links** → `skills/youtube/README.md`
- **Enrich person/company info** → `skills/enrich/README.md`
- **Search for flights** → `skills/flights/README.md`

When you need to perform any of these tasks, read the corresponding skill file for detailed instructions.

**Understanding SDKs/libraries/APIs:** Use web search (see `skills/web-search.md`) to research and find documentation for any library or API you need to understand.

## Philosophy: Optimize for Speed

**We use terminal commands and direct API calls instead of MCPs to maximize speed.** Every operation should be optimized for minimal latency. This means:

- **Chain commands efficiently** - Combine operations in single terminal calls using `&&`, `||`, `|`, `;`
- **Avoid slow commands** - Use `tree` instead of `find` or `grep` for file exploration
- **Batch API calls** - Use list endpoints and caching instead of multiple separate calls
- **Balance chaining** - Chain operations together while ensuring each step is necessary and efficient

---

## Terminal Usage

**Everything runs through the terminal. Always use absolute paths and combine operations in single calls.**

### Project Root

**Define project root once at the start of your session or in your shell:**
```bash
PROJECT_ROOT="/path/to/your/project"  # Replace with your actual path
```

**Or detect it automatically from script location:**
```bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
```

### Paths & File Exploration

- **Always use absolute paths** - Use `$PROJECT_ROOT` variable: `$PROJECT_ROOT/skills/enrich/enrich.sh` not `./enrich.sh`. Avoid `cd` unless necessary.
- **Skills data**: Store generated data in `$PROJECT_ROOT/user/skills-data/` (gitignored, like application data)
- **Use `tree` for file exploration** - `tree -a -L N` (include hidden files). **NEVER use `find` or `grep` to locate files** - `tree` is much faster.

### Minimizing Calls

**Why:** Each terminal call adds latency. Chain operations with `&&`, `||`, `|`, `;` to reduce total wait time.

**How:** Combine sourcing + execution + error handling in one call. Include debugging in the same call (`|| echo "Error: $?"`). Use `2>&1` to capture errors. Think: "Can I do this in one call?" before making multiple calls.

## Environment Variables & Secrets

**All API keys and credentials are in `.env` at project root (`$PROJECT_ROOT/.env`).**

### Sourcing Pattern

**Combine sourcing with your command in ONE terminal call.**

**Pattern (Default - Use This):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -H "x-api-key: $API_KEY_VAR" https://api.example.com/endpoint
```

**Why:** Unconditional sourcing is simpler and more reliable. Variables persist across calls, so sourcing is fast even if already set. Conditional patterns (`[ -z "$VAR" ]`) are unreliable in fresh shells and cause auth failures.

**Examples:**
```bash
# ✅ CORRECT: Unconditional sourcing (default - use this)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -H "x-api-key: $EXA_API_KEY" https://api.exa.ai/search

# ❌ WRONG: Split calls (adds latency)
set -a && source "$PROJECT_ROOT/.env" && set +a
curl ...  # Separate call!
```

**Note:** Use variable references (`$LINEAR_API_KEY`), never hardcode secrets in commands.

## API Querying

**Minimize API calls by batching, caching, and combining operations.**

**Why:** Each API call adds latency. Batch queries, cache results, and reuse data to reduce total wait time.

**How:**
- **Batch queries** - Use list endpoints (`GET /items?ids=1,2,3`) instead of loops
- **Cache results** - `curl ... > /tmp/data.json && jq ... /tmp/data.json` (combine in one call)
- **Extract efficiently** - Get all needed fields in one `jq` pass
- **Don't re-query** - Reuse data you already have
- **Combine operations** - Source + curl + parse in one terminal call

**Example:** Instead of `for id in 1 2 3; do curl .../items/${id}; done` (3+ calls), use `curl .../items?limit=10 > /tmp/items.json && jq ... /tmp/items.json` (1 call).

---

## Repository Structure

**This is an open-source repository.** The structure is organized as follows:

- **`user/` folder**: Contains user-specific content (personal files, preferences, skills, reports). This folder is for individual user customization and should not be shared publicly.
  - **`user/skills/`**: User-specific skills with their own folders and READMEs (mirrors `skills/` structure)
  - **`user/reports/`**: User-generated reports and analysis
- **`skills/` folder**: Contains skill documentation and scripts. Each skill has its own folder with `README.md` and supporting files (scripts, configs, etc.). This is system/public content that should be part of the open-source repository.

When creating or referencing user-specific files, always place them in the `user/` folder or its subdirectories.

### Creating Reports

**When creating reports in `user/reports/`, use shell command substitution to generate the date automatically in the filename:**

```bash
# Generate date-stamped filename automatically (date evaluated inline)
write "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-report-name.md" "Report content here"
```

**⚠️ IMPORTANT:**
- **DO NOT manually type dates** - LLMs often don't have accurate date context
- **DO NOT include dates in the file content** - The filename date is the source of truth
- **Always use shell date command** - `$(date +"%Y-%m-%d")` evaluated inline ensures accuracy

**Example:**
```bash
# ✅ CORRECT: Use shell date command substitution inline
write "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-mac-llm-clients-comparison.md" "# Report Title

Content here without dates..."

# ❌ WRONG: Manual date (LLM may get it wrong)
write "$PROJECT_ROOT/user/reports/2025-01-30-report.md" "# Report Title

Date: January 30, 2025  ← Don't include dates in content!"
```

## Before Responding

**ALWAYS read `$PROJECT_ROOT/user/profile.md` first** to understand the user's context, preferences, goals, and background. This is essential for providing relevant, personalized responses.

To confirm you read this file, prefix your first response with "🙌".

