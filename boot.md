# AgentOS

> **First run?** Check: `[ -f .env ] && [ -f user/profile.md ] || echo "NEEDS_SETUP"`
> If needs setup, read `utils/setup.md` and guide the user through it.

## Concepts

| Term | What it is |
|------|-----------|
| **Skill** | A service you connect to (Exa, Gmail, Linear, Apollo) |
| **Action** | A type of skill — stateless verbs (search, extract, transcribe) |
| **Connection** | A type of skill — your data (email, crm, calendar) |

**Paths are predictable:** `skills/{skill-name}/README.md`

## Skills

See `skills.yaml` for the full routing table.

### Actions (stateless verbs)

| Action | Skills | Description |
|--------|--------|-------------|
| search | exa | Semantic web search, discover URLs |
| extract | exa, firecrawl | Extract content from URLs |
| transcribe | youtube | Video transcripts |
| enrich | enrich-so | Research email, phone, domain, company |
| check-domain | whoapi | Check domain availability |
| search-flights | google-flights | Search for flights |

### Connections (your data)

| Connection | Skills | Description |
|------------|--------|-------------|
| crm | apollo | Deals, contacts, companies |
| email | gmail | Read, search, draft emails |
| files | google-drive | Cloud file storage |
| work-tasks | linear | Issues, projects |
| personal-tasks | todoist | Personal todos |
| calendar | apple-calendar | Events |
| contacts | apple-contacts | People |
| messages | imessages, whatsapp | Conversations |
| bookmarks | raindrop | Collections |
| code | github | Repos, PRs, issues |
| finance | copilot | Accounts, transactions |

## Using Skills

1. Identify the skill needed (action or connection)
2. Look up skills in `skills.yaml`
3. Read skill docs: `skills/{skill-name}/README.md`
4. If skill fails (402/429), try next skill in list

## Search vs Extract

```
Need to FIND information or discover URLs?
  → Use search (Exa)

Have specific URLs to read/extract content from?
  → Use extract (Exa first, Firecrawl fallback)
     Firecrawl when: Exa fails, JS-heavy site, need more content
```

**⚠️ Always surface API errors to the user** - credit exhaustion (402), rate limits (429), auth failures (401). Don't silently fail.

## Browser Tool Usage

**⚠️ CRITICAL: Do NOT use the browser tool unless the user explicitly asks you to.**

**Preferred approach for web research:**
1. **First:** Use search (Exa) for semantic web search
2. **Second:** Use extract (Exa/Firecrawl) for specific URLs
3. **Last resort:** Browser tool - only if explicitly requested or APIs fail

## Terminal Usage & Best Practices

**We use terminal commands and direct API calls instead of MCPs to maximize speed.**

### Core Principles

- **Chain commands** - Combine operations using `&&`, `||`, `|`, `;`
- **Use absolute paths** - Always use `$PROJECT_ROOT` variable
- **Source env in same call** - Combine `.env` sourcing with command execution
- **Batch API calls** - Use list endpoints and caching instead of loops

### Project Root

```bash
PROJECT_ROOT="/path/to/your/project"
```

### Environment Variables

All API keys in `.env` at `$PROJECT_ROOT/.env`. Always source in the same call:

```bash
# ✅ CORRECT: Source + execute in one call
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -H "x-api-key: $EXA_API_KEY" https://api.exa.ai/search
```

### Data Storage

- **Skills data**: Store generated data in `$PROJECT_ROOT/user/skills-data/`

### Timezone Conversion

**Always convert UTC timestamps to local timezone when displaying to user.** See `utils/README.md`.

---

## Repository Structure

- **`skills/`**: Skill documentation and scripts. Each skill has its own folder with `README.md`.
- **`skills.yaml`**: Routing table mapping actions/connections to skills.
- **`utils/`**: Utility scripts (timezone, setup guides).
- **`user/`**: User-specific content (profile, reports, skills-data). Gitignored.

### Creating Reports

Use shell command substitution for date-stamped filenames:

```bash
cat > "$PROJECT_ROOT/user/reports/$(date +"%Y-%m-%d")-report-name.md" << 'EOF'
# Report Title
Content here...
EOF
```

## Before Responding

**Read `user/profile.md`** for user context, preferences, and workflows.

**Prefix your first response with "🙌"** to confirm you read this file.
