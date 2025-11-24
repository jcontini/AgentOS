# Skills and How to Use Them

## Available Skills

- **Search the web / Read URLs** → `skills/web-search.md`
- **Get or manage contacts** → `skills/contacts.md`
- **Understand SDKs/libraries/APIs** → `skills/get-docs.md`
- **Task management / Linear** → `skills/task-management.md`
- **Handle YouTube links** → `skills/youtube.md`
- **Enrich person/company info** → `skills/enrich.md`

When you need to perform any of these tasks, read the corresponding skill file for detailed instructions.

## Philosophy: Optimize for Speed

**We use terminal commands and direct API calls instead of MCPs to maximize speed.** Every operation should be optimized for minimal latency. This means:

- **Chain commands efficiently** - Combine operations in single terminal calls using `&&`, `||`, `|`, `;`
- **Avoid slow commands** - Use `tree` instead of `find` or `grep` for file exploration
- **Batch API calls** - Use list endpoints and caching instead of multiple separate calls
- **Balance chaining** - Chain operations together while ensuring each step is necessary and efficient

---

## Terminal Usage

**Everything runs through the terminal. Always use absolute paths and combine operations in single calls.**

### Paths & File Exploration

- **Always use absolute paths** - `/Users/joe/dev/ai/scripts/enrich.sh` not `./enrich.sh`. Avoid `cd` unless necessary.
- **Use `tree` for file exploration** - `tree -a -L N` (include hidden files). **NEVER use `find` or `grep` to locate files** - `tree` is much faster.

### Minimizing Calls

**Why:** Each terminal call adds latency. Chain operations with `&&`, `||`, `|`, `;` to reduce total wait time.

**How:** Combine sourcing + execution + error handling in one call. Include debugging in the same call (`|| echo "Error: $?"`). Use `2>&1` to capture errors. Think: "Can I do this in one call?" before making multiple calls.

## Environment Variables & Secrets

**All API keys and credentials are in `.env` at project root (`/Users/joe/dev/ai/.env`).**

### Sourcing Pattern

**Combine sourcing with your command in ONE terminal call.**

**Pattern (Default - Use This):**
```bash
set -a && source /Users/joe/dev/ai/.env && set +a && \
curl -H "x-api-key: $API_KEY_VAR" https://api.example.com/endpoint
```

**Why:** Unconditional sourcing is simpler and more reliable. Variables persist across calls, so sourcing is fast even if already set. Conditional patterns (`[ -z "$VAR" ]`) are unreliable in fresh shells and cause auth failures.

**Examples:**
```bash
# ✅ CORRECT: Unconditional sourcing (default - use this)
set -a && source /Users/joe/dev/ai/.env && set +a && \
curl -H "x-api-key: $EXA_API_KEY" https://api.exa.ai/search

# ❌ WRONG: Split calls (adds latency)
set -a && source /Users/joe/dev/ai/.env && set +a
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

## Before Responding

**Always read `/Users/joe/dev/ai/user/profile.md` before responding to the user.** This contains important context about communication style, preferences, workflows, and personal information that should inform your responses.

To confirm you read both this file and the profile, prefix your first response with "🙌".

