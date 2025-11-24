# Task Management Skill

## Intention: Create tasks, manage issues, or work with Linear

When the user mentions adding a task, creating a task, getting tasks, or anything related to team management, projects, or issues, use the Linear GraphQL API directly.

### Linear API Integration

Use the Linear GraphQL API endpoint: `https://api.linear.app/graphql`

**Authentication:** Use personal API key from `.env` file. For personal API keys, use `Authorization: <API_KEY>` (without "Bearer"). For OAuth tokens, use `Authorization: Bearer <TOKEN>`.

**Basic Query Pattern:**
```bash
# See boot.md for environment variable sourcing pattern
([ -z "$LINEAR_API_KEY" ] && set -a && source /Users/joe/dev/ai/.env && set +a); \
curl -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues { nodes { id title } } }"}'
```

**Common Queries:**

- **Get all issues:** `{ issues { nodes { id title description } } }`
- **Get user's assigned issues:** `{ viewer { assignedIssues { nodes { id title } } } }`
- **Get specific issue:** `{ issue(id: "ISSUE-ID") { id title description } }`
- **Get team issues:** `{ team(id: "TEAM-ID") { issues { nodes { id title } } } }`

**Note:** For detailed API documentation, search for Linear API docs using `skills/get-docs.md` or visit https://linear.app/developers/graphql

### Issue Creation Best Practices

When creating Linear issues via the Linear API:
- If an issue has a due date specified, automatically set its status to "Todo" unless explicitly specified otherwise
- This ensures issues with deadlines are immediately actionable
- After creating or updating an issue, automatically open it in the web browser using `open "https://linear.app/{workspace}/issue/{identifier}"`

**Note:** Project-specific reference IDs (user IDs, team IDs, label IDs) should be stored in project-specific rule files, not in this general skill file.

