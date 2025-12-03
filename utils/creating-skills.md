# Creating Skills

## Intention: Guide for creating new skills in this repository

When creating new skills in `skills/`, follow these patterns and best practices.

## TLDR: Which Approach?

```mermaid
flowchart LR
    A{Complex logic?<br/>validation, normalization,<br/>multiple backends} -->|Yes| B[CLI Wrapper]
    A -->|No| C{Writes with<br/>specific formatting?}
    C -->|Yes| B
    C -->|No| D[Pure Docs]
    
    B --> E["README + script<br/>e.g. contacts, calendar"]
    D --> F["README only<br/>e.g. todoist, linear, copilot"]
    
    style D fill:#2d5a27
    style B fill:#8b4513
    style F fill:#2d5a27
    style E fill:#8b4513
```

See [Skill Architecture](#skill-architecture) for details, [Context Optimization](#context-optimization) for README guidelines.

## Skill Architecture

Choose the right approach based on complexity:

| Approach | When to Use | Examples |
|----------|-------------|----------|
| **Pure docs** | Straightforward APIs/queries, read-only, AI can compose | Todoist, Linear, Copilot |
| **CLI wrapper** | Complex logic, validation, writes, multiple backends | Contacts |

### Pure Docs (Preferred)

README only — no wrapper script. AI reads docs and composes commands directly.

**Use when:**
- API/database queries are straightforward
- No complex validation or normalization needed
- Read-only or simple writes
- AI can compose queries from schema + patterns

**README includes:**
- Schema/API reference (fields, types, not full specs)
- 3-5 essential query patterns
- Notes on conventions (date formats, field meanings)

**README omits:**
- Exhaustive examples (AI can compose variations)
- Full API specs (AI can look up if needed)
- Verbose explanations

### CLI Wrapper

README + script. Script encapsulates complex logic.

**Use when:**
- Complex validation/normalization (e.g., phone number formatting)
- Multiple backends (e.g., SQLite reads + AppleScript writes)
- State management or caching
- Error-prone operations that need guardrails

**README documents:**
- CLI commands and options
- Output format
- Technical details (for debugging)

## Context Optimization

**Target: ~100-150 lines per README.** The AI reads these files, so optimize for:

- **Density over verbosity** — One good example beats five similar ones
- **Schema + patterns** — Give structure, let AI compose specifics
- **Tables over prose** — Faster to scan, less context
- **Omit the obvious** — AI knows curl, jq, SQL basics

## File Structure

- **Minimal files** — README + implementation file(s). No unnecessary abstraction.
- **Choose the right tool:**
  - **Swift** — macOS system APIs (EventKit, Contacts framework)
  - **Bash** — Simple API calls with curl
  - **Python** — Complex APIs, data processing, when libraries help
  - **Direct tools** — SQLite, jq — use directly in README examples
- **No user-specific content** — Use generic examples (`user@example.com`). User data belongs in `user/` or `.env`.

## Output Format

- **JSON for AI consumption** — Output JSON to stdout. AI parses; user doesn't need formatted output.
- **Technical error messages** — Include details for debugging. AI handles errors.

## Environment Variables & Secrets

- **API keys → `.env`** — Store in `$PROJECT_ROOT/.env`, never hardcode
- **Skill-specific files → `user/skills-data/`** — Service account keys, certs, cached data go in `user/skills-data/SKILL_NAME/` (folder name matches skill folder)
- **Document required vars** — List env vars needed in README
- **Bash pattern:** `set -a && source "$PROJECT_ROOT/.env" && set +a && command`
- **Never commit secrets** — `.env` and `user/` are gitignored

## Examples by Pattern

| Pattern | Skill | Structure |
|---------|-------|-----------|
| Pure docs (REST API) | `skills/todoist/` | README with curl examples |
| Pure docs (GraphQL) | `skills/linear/` | README with query patterns |
| Pure docs (SQLite) | `skills/copilot/` | README with sqlite3 examples |
| CLI wrapper (Python) | `skills/contacts/` | README + `contacts.py` |
| CLI wrapper (Swift) | `skills/calendar/` | README + `.swift` files |
| CLI wrapper (Bash) | `skills/enrich/` | README + `enrich.sh` |

## See Also

- **Terminal Usage** — See `boot.md` for command patterns
- **Creating Reports** — See `boot.md` for `user/reports/` patterns
