# Task Management Skill

## Intention: Create tasks, manage issues, or work with Linear

When the user mentions adding a task, creating a task, getting tasks, or anything related to team management, projects, or issues, use the Linear GraphQL API directly.

### Linear API Integration

Use the Linear GraphQL API endpoint: `https://api.linear.app/graphql`

**Authentication:** Use personal API key from `.env` file. **CRITICAL:** For personal API keys, use `Authorization: <API_KEY>` (without "Bearer"). For OAuth tokens, use `Authorization: Bearer <TOKEN>`.

**Basic Query Pattern:**
```bash
# Unconditional sourcing (simpler and more reliable - see boot.md)
set -a && source /Users/joe/dev/ai/.env && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues { nodes { id title } } }"}' | jq .
```

**Troubleshooting Auth Errors:**
- If you get `AUTHENTICATION_ERROR`, verify the key exists: `grep LINEAR_API_KEY /Users/joe/dev/ai/.env`
- **Never use "Bearer" prefix** for personal API keys - Linear personal keys are used directly
- If auth still fails, try unconditional sourcing pattern above (more reliable than conditional)

**Common Queries:**

- **Get all issues:** `{ issues { nodes { id title description } } }`
- **Get user's assigned issues:** `{ viewer { assignedIssues { nodes { id title } } } }`
- **Get user's assigned issues due this week:** `{ viewer { assignedIssues(filter: { dueDate: { gte: "YYYY-MM-DD", lte: "YYYY-MM-DD" } }) { nodes { id identifier title description url priority state { name } dueDate assignee { name } team { name } } } } }`
- **Get specific issue:** `{ issue(id: "ISSUE-ID") { id title description } }`
- **Get team issues:** `{ team(id: "TEAM-ID") { issues { nodes { id title } } } }`

**Date Filtering:** Use ISO format (YYYY-MM-DD) for date filters.

**Calculate "This Week" Range (macOS):**
```bash
TODAY=$(date +%Y-%m-%d) && \
DOW=$(date +%w) && \
if [ "$DOW" = "0" ]; then END_WEEK=$(date -v+7d +%Y-%m-%d); else END_WEEK=$(date -v+Sun +%Y-%m-%d); fi
```
**Why:** `date -v+Sun` returns today if today is Sunday. For "this week" queries, if today is Sunday, use next Sunday (+7 days). Otherwise, use `date -v+Sun` to get the upcoming Sunday.

**Complete "This Week" Query Example (Single Command):**
```bash
set -a && source /Users/joe/dev/ai/.env && set +a && \
TODAY=$(date +%Y-%m-%d) && \
DOW=$(date +%w) && \
if [ "$DOW" = "0" ]; then END_WEEK=$(date -v+7d +%Y-%m-%d); else END_WEEK=$(date -v+Sun +%Y-%m-%d); fi && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ viewer { assignedIssues(filter: { dueDate: { gte: \\\"$TODAY\\\", lte: \\\"$END_WEEK\\\" } }) { nodes { id identifier title description url priority state { name } dueDate assignee { name } team { name } } } } }\"}" | \
jq -r '.data.viewer.assignedIssues.nodes[] | "\(.identifier) | \(.title) | Due: \(.dueDate) | Status: \(.state.name) | Priority: \(.priority // "None") | Team: \(.team.name) | \(.url)"'
```

**Note:** For detailed API documentation, search for Linear API docs using `skills/get-docs.md` or visit https://linear.app/developers/graphql

### Issue Creation Best Practices

When creating Linear issues via the Linear API:
- If an issue has a due date specified, automatically set its status to "Todo" unless explicitly specified otherwise
- This ensures issues with deadlines are immediately actionable
- After creating or updating an issue, automatically open it in the web browser using `open "https://linear.app/{workspace}/issue/{identifier}"`

**Note:** Project-specific reference IDs (user IDs, team IDs, label IDs) should be stored in project-specific rule files, not in this general skill file.

