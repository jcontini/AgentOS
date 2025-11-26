# Creating Skills Skill

## Intention: Guide for creating new skills in this repository

When creating new skills in `skills/`, follow these patterns and best practices.

## File Structure

- **Minimal files** - Prefer README + implementation file(s). Avoid unnecessary wrappers or abstraction layers.
- **Choose the right tool** - Use the language/framework that fits the task:
  - **Swift** - For macOS system APIs (e.g., EventKit for calendar, Contacts framework)
  - **Bash** - For simple API calls with curl (e.g., REST APIs that don't need complex logic)
  - **Python** - For complex APIs, data processing, or when libraries simplify the work
  - **Direct tools** - For database queries (e.g., SQLite), use the tool directly
- **No wrappers unless needed** - If you need Python anyway, use Python directly (no bash wrapper). If bash is doing the work, use bash directly.
- **No user-specific content** - Never include user-specific information (email addresses, names, file paths, account details, etc.) in `skills/` files. Use generic examples (e.g., `user@example.com`, `example@domain.com`). User-specific content belongs in `user/` folder or `.env` file.

## Output Format

- **JSON for AI consumption** - Output JSON to stdout for AI to parse. The user doesn't need to see formatted output.
- **Technical error messages** - Include detailed technical error information for debugging. The AI will be doing the debugging.

## Dependencies

- **Document in README** - List required packages, tools, and installation commands in the README. No separate dependency files needed unless the skill is complex.

## Environment Variables & Secrets

- **API keys/tokens go in `.env`** - Simple API keys, tokens, and credentials should be stored in `$PROJECT_ROOT/.env` (never hardcoded)
- **Skill-specific data/secrets go in `user/skills-data/`** - Files like service account keys, certificates, or other skill-specific data should be stored in `$PROJECT_ROOT/user/skills-data/SKILL_NAME/` where `SKILL_NAME` matches the skill folder name exactly
  - **Important:** The folder name in `user/skills-data/` must match the skill folder name (whether in `skills/` or `user/skills/`) to avoid collisions
  - Example: Skill `skills/gmail/` → Data in `user/skills-data/gmail/`
  - Example: User skill `user/skills/abp/` → Data in `user/skills-data/abp/`
- **Document required vars** - In the README, clearly list which environment variables the skill needs (e.g., `LINEAR_API_KEY`, `TODOIST_API_TOKEN`)
- **Document data files** - If the skill requires files (like service account keys), document the expected path in `user/skills-data/SKILL_NAME/` where `SKILL_NAME` matches the skill folder name
- **Use env vars in code** - Reference environment variables in scripts (e.g., `$API_KEY` in bash, `os.getenv('API_KEY')` in Python)
- **Bash sourcing pattern** - For bash scripts, use unconditional sourcing: `set -a && source "$PROJECT_ROOT/.env" && set +a && command`
- **Python env loading** - For Python scripts, load from `.env` using `python-dotenv` or parse manually
- **Never commit secrets** - Both `.env` and `user/` are gitignored. Never commit API keys, credentials, or user-specific data to the repository

## Pattern Examples

- **Swift skill:** `skills/calendar/` → `README.md` + `calendar-event.swift` (macOS EventKit API)
- **Bash skill:** `skills/enrich/` → `README.md` + `enrich.sh` (Bash calls curl directly)
- **Python skill:** `skills/gmail/` → `README.md` + `gmail.py` (Python handles CLI, API client)
- **SQLite skill:** `skills/calendar/` → Uses SQLite directly in README examples (no wrapper needed)

## Repository Structure Context

**This is an open-source repository.** The structure is organized as follows:

- **`user/` folder**: Contains user-specific content (personal files, preferences, skills, reports). This folder is for individual user customization and should not be shared publicly.
  - **`user/skills/`**: User-specific skills with their own folders and READMEs (mirrors `skills/` structure)
  - **`user/skills-data/`**: Skill-specific data files (service account keys, certificates, cached data, etc.). Each skill should have its own subdirectory matching the skill folder name exactly (e.g., `skills/gmail/` → `user/skills-data/gmail/`, `user/skills/abp/` → `user/skills-data/abp/`). This ensures no naming collisions between system and user skills.
  - **`user/reports/`**: User-generated reports and analysis
- **`skills/` folder**: Contains skill documentation and scripts. Each skill has its own folder with `README.md` and supporting files (scripts, configs, etc.). This is system/public content that should be part of the open-source repository.

When creating or referencing user-specific files, always place them in the `user/` folder or its subdirectories.

## See Also

- **Creating Reports** - See `boot.md` for patterns on creating reports in `user/reports/`
- **Terminal Usage** - See `boot.md` for terminal usage patterns and best practices
- **Environment Variables** - See `boot.md` for environment variable sourcing patterns

