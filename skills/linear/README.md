# Linear Skill

## Intention: Create tasks, manage issues, or work with Linear

When the user mentions adding a task, creating a task, getting tasks, or anything related to team management, projects, or issues, use the Linear GraphQL API directly.

## Quick Reference: Find and Update Issue

**Find issue by identifier (most reliable method):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 100) { nodes { id identifier title description } } }"}' | \
jq '.data.issues.nodes[] | select(.identifier == "DEV-264")'
```

**Update issue description (use heredoc for complex JSON):**
```bash
ISSUE_ID="bbc2eeb4-0c85-4cd8-8a2b-e22c84fc28a3" && \
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @- << EOF
{
  "query": "mutation(\$id: String!, \$input: IssueUpdateInput!) { issueUpdate(id: \$id, input: \$input) { success issue { identifier url } } }",
  "variables": {
    "id": "$ISSUE_ID",
    "input": {
      "description": "Your description here"
    }
  }
}
EOF
```

### Linear API Integration

Use the Linear GraphQL API endpoint: `https://api.linear.app/graphql`

**Authentication:** Use personal API key from `.env` file. **CRITICAL:** For personal API keys, use `Authorization: <API_KEY>` (without "Bearer"). For OAuth tokens, use `Authorization: Bearer <TOKEN>`.

**Basic Query Pattern:**
```bash
# Always use pagination (first: 100) to avoid missing issues
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 100) { nodes { id identifier title } pageInfo { hasNextPage endCursor } } }"}' | jq .
```

**Troubleshooting Auth Errors:**
- If you get `AUTHENTICATION_ERROR`, verify the key exists: `grep LINEAR_API_KEY "$PROJECT_ROOT/.env"`
- **Never use "Bearer" prefix** for personal API keys - Linear personal keys are used directly
- If auth still fails, try unconditional sourcing pattern above (more reliable than conditional)

**Common Queries:**

**CRITICAL: Always use pagination when querying issues**

Linear's default limit is 50 issues. Always use `first: 100` (or higher) to avoid missing issues. For large workspaces, check `hasNextPage` and use cursor-based pagination.

- **Get all issues (with pagination):** `{ issues(first: 100) { nodes { id identifier title description } pageInfo { hasNextPage endCursor } } }`
- **Get specific issue by identifier:** Use filter with pagination: `{ issues(first: 100, filter: { identifier: { eq: "DEV-320" } }) { nodes { id identifier title } } }`
- **Get specific issue by ID:** `{ issue(id: "ISSUE-ID") { id identifier title description } }`
- **Get user's assigned issues:** `{ viewer { assignedIssues(first: 100) { nodes { id title } pageInfo { hasNextPage } } } }`
- **Get user's assigned issues due this week:** `{ viewer { assignedIssues(first: 100, filter: { dueDate: { gte: "YYYY-MM-DD", lte: "YYYY-MM-DD" } }) { nodes { id identifier title description url priority state { name } dueDate assignee { name } team { name } } } } }`
- **Get team issues:** `{ team(id: "TEAM-ID") { issues(first: 100) { nodes { id title } pageInfo { hasNextPage } } } }`

**Finding issues by identifier:**

**RECOMMENDED: Query all issues and filter with jq (more reliable than GraphQL filters):**
```bash
# Get all issues with full details, then filter with jq
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 100) { nodes { id identifier title description } } }"}' | \
jq '.data.issues.nodes[] | select(.identifier == "DEV-264")'
```

**Alternative: Use GraphQL filter (may be less reliable):**
```bash
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ issues(first: 100, filter: { identifier: { eq: \"DEV-320\" } }) { nodes { id identifier title } } }"
  }' | jq '.data.issues.nodes[0]'
```

**Date Filtering:** Use ISO format (YYYY-MM-DD) for date filters.

**Pagination Best Practices:**

**ALWAYS use `first: 100` (or higher) when querying issues.** Linear's default limit is 50 issues, so queries without pagination will miss issues beyond the first 50.

- **Default behavior:** `{ issues { nodes { ... } } }` returns only 50 issues
- **With pagination:** `{ issues(first: 100) { nodes { ... } pageInfo { hasNextPage endCursor } } }` returns up to 100 issues
- **Check for more:** If `hasNextPage` is true, use `after: endCursor` to fetch the next page
- **When searching:** Always combine filters with pagination: `{ issues(first: 100, filter: { ... }) { ... } }`

**Example with pagination check:**
```bash
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ issues(first: 100) { nodes { id identifier title } pageInfo { hasNextPage endCursor } } }"
  }' | jq '{issues: .data.issues.nodes, hasMore: .data.issues.pageInfo.hasNextPage}'
```

**Calculate "This Week" Range (Cross-platform):**
```bash
TODAY=$(date +%Y-%m-%d) && \
DOW=$(date +%w) && \
if [ "$DOW" = "0" ]; then 
  # Today is Sunday, get next Sunday (+7 days)
  END_WEEK=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d)
else 
  # Get next Sunday (cross-platform: try macOS BSD date, fallback to Linux GNU date)
  END_WEEK=$(date -v+Sun +%Y-%m-%d 2>/dev/null || date -d "next Sunday" +%Y-%m-%d)
fi
```
**Why:** On Sunday, we want next Sunday (+7 days). Otherwise, get the upcoming Sunday. The command tries macOS BSD date syntax first, then falls back to Linux GNU date syntax.

**Complete "This Week" Query Example (Single Command):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TODAY=$(date +%Y-%m-%d) && \
DOW=$(date +%w) && \
if [ "$DOW" = "0" ]; then END_WEEK=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d); else END_WEEK=$(date -v+Sun +%Y-%m-%d 2>/dev/null || date -d "next Sunday" +%Y-%m-%d); fi && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ viewer { assignedIssues(filter: { dueDate: { gte: \\\"$TODAY\\\", lte: \\\"$END_WEEK\\\" } }) { nodes { id identifier title description url priority state { name } dueDate assignee { name } team { name } } } } }\"}" | \
jq -r '.data.viewer.assignedIssues.nodes[] | "\(.identifier) | \(.title) | Due: \(.dueDate) | Status: \(.state.name) | Priority: \(.priority // "None") | Team: \(.team.name) | \(.url)"'
```

**Note:** For detailed API documentation, use web search (see `skills/search/README.md`) to find Linear API docs or visit https://linear.app/developers/graphql

### Issue Creation Best Practices

When creating Linear issues via the Linear API:
- If an issue has a due date specified, automatically set its status to "Todo" unless explicitly specified otherwise
- This ensures issues with deadlines are immediately actionable
- After creating or updating an issue, automatically open it in the web browser using a cross-platform command:
  ```bash
  # Cross-platform: macOS uses 'open', Linux uses 'xdg-open', Windows uses 'start'
  open "https://linear.app/{workspace}/issue/{identifier}" 2>/dev/null || \
  xdg-open "https://linear.app/{workspace}/issue/{identifier}" 2>/dev/null || \
  start "https://linear.app/{workspace}/issue/{identifier}" 2>/dev/null || true
  ```

**Note:** Project-specific reference IDs (user IDs, team IDs, label IDs, workspace name) should be stored in project-specific rule files, not in this general skill file.

### Updating Issues Efficiently

**CRITICAL: Use heredoc for complex JSON to avoid escaping issues**

**Pattern: Find issue, then update in one flow:**
```bash
# Step 1: Find issue ID (query once, get full details)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ISSUE_DATA=$(curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 100) { nodes { id identifier title description } } }"}' | \
jq -r '.data.issues.nodes[] | select(.identifier == "DEV-264")') && \
ISSUE_ID=$(echo "$ISSUE_DATA" | jq -r '.id') && \

# Step 2: Update issue using heredoc (avoids JSON escaping problems)
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @- << EOF
{
  "query": "mutation(\$id: String!, \$input: IssueUpdateInput!) { issueUpdate(id: \$id, input: \$input) { success issue { identifier url description } } }",
  "variables": {
    "id": "$ISSUE_ID",
    "input": {
      "description": "Updated description here"
    }
  }
}
EOF
```

**Key points:**
- **Mutation format**: `mutation($id: String!, $input: IssueUpdateInput!)` - `id` and `input` are separate parameters
- **Use heredoc**: `--data-binary @- << 'EOF'` avoids JSON escaping issues with newlines, quotes, etc.
- **Query once**: Get all issues with full fields (id, identifier, title, description) in one call
- **Filter with jq**: More reliable than GraphQL filters for finding specific issues
- **Include url in response**: Always request `url` in mutation response to get the issue URL for opening

### Issue Relations (Blocking Relationships)

**CRITICAL: Understanding blocking relationships**

When setting up blocking relationships, remember:
- **"Issue A is blocked by Issue B"** means **Issue B blocks Issue A**
- The relation is created from the blocker's perspective: `issueId` = the blocker, `relatedIssueId` = the blocked issue

**Pattern:**
- User says: "Issue DEV-391 is blocked by DEV-366"
- Translation: DEV-366 blocks DEV-391
- Create relation: `issueId` = DEV-366, `relatedIssueId` = DEV-391, `type` = "blocks"

**Create blocking relationship:**
```bash
# Example: DEV-391 is blocked by DEV-366
# First, get both issue IDs
ISSUE_A_ID="73e9cf66-491a-4b7f-a4dc-2faf83ca50e5"  # DEV-391 (blocked issue)
ISSUE_B_ID="9a5c4f6e-e078-4520-85f9-1c57187ee6fd"  # DEV-366 (blocker)

# Create relation: Issue B blocks Issue A
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"mutation(\$input: IssueRelationCreateInput!) { issueRelationCreate(input: \$input) { success issueRelation { id } } }\",
    \"variables\": {
      \"input\": {
        \"issueId\": \"$ISSUE_B_ID\",
        \"relatedIssueId\": \"$ISSUE_A_ID\",
        \"type\": \"blocks\"
      }
    }
  }"
```

**Delete blocking relationship:**
```bash
# Get relation ID first, then delete
RELATION_ID="5a43f570-e3db-491c-aa86-09c6829ac98c"
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"mutation(\$id: String!) { issueRelationDelete(id: \$id) { success } }\",
    \"variables\": {\"id\": \"$RELATION_ID\"}
  }"
```

**Query issue relations:**
```bash
# Check what blocks an issue (or what it blocks)
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ issue(id: \"ISSUE-ID\") { identifier title relations { nodes { type relatedIssue { identifier title } } } } }"
  }'
```

**Common relation types:**
- `blocks` - One issue blocks another
- `duplicate` - One issue is a duplicate of another
- `related` - Issues are related (general)

### Project Management

#### Get All Projects
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { nodes { id name lead { id name } } } }"}' | \
jq -r '.data.projects.nodes[] | "\(.id) | \(.name) | Lead: \(.lead.name // "None")"'
```

#### Create a Project
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TEAM_ID="your-team-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { projectCreate(input: { name: \\\"Project Name\\\", teamIds: [\\\"$TEAM_ID\\\"] }) { success project { id name } } }\"}" | jq .
```

#### Update Project Title
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PROJECT_ID="project-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { projectUpdate(id: \\\"$PROJECT_ID\\\", input: { name: \\\"New Project Name\\\" }) { success project { id name } } }\"}" | jq .
```

#### Assign Project Lead
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
# First, get viewer (current user) ID
VIEWER_ID=$(curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}' | jq -r '.data.viewer.id') && \
# Then assign as lead to project
PROJECT_ID="project-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { projectUpdate(id: \\\"$PROJECT_ID\\\", input: { leadId: \\\"$VIEWER_ID\\\" }) { success project { id name lead { name } } } }\"}" | jq .
```

#### Assign Lead to All Projects
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
VIEWER_ID=$(curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}' | jq -r '.data.viewer.id') && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects { nodes { id name } } }"}' | \
jq -r '.data.projects.nodes[].id' | \
while read project_id; do
  curl -s -X POST "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"mutation { projectUpdate(id: \\\"$project_id\\\", input: { leadId: \\\"$VIEWER_ID\\\" }) { success project { name } } }\"}" | \
  jq -r '.data.projectUpdate | if .success then "✅ \(.project.name)" else "❌ Failed" end'
done
```

#### Move Issue to Different Project
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ISSUE_ID="issue-id-here" && \
PROJECT_ID="project-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { projectId: \\\"$PROJECT_ID\\\" }) { success issue { identifier title project { name } } } }\"}" | jq .
```

### Initiatives

**Note:** Projects can be assigned to initiatives via the API using `initiativeToProjectCreate`. To remove projects from initiatives, you need to query for the relationship ID first using `initiativeToProjects`, then delete it with `initiativeToProjectDelete`.

#### List All Initiatives
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ initiatives { nodes { id name projects { nodes { id name } } } } }"}' | \
jq -r '.data.initiatives.nodes[] | "\(.id) | \(.name) | Projects: \(.projects.nodes | length)"'
```

#### Create Initiative
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { initiativeCreate(input: { name: \"Initiative Name\" }) { success initiative { id name } } }"}' | jq .
```

#### Delete Initiative
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_ID="initiative-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { initiativeDelete(id: \\\"$INITIATIVE_ID\\\") { success } }\"}" | jq .
```

**Note:** Deleting an initiative will remove it, but projects will remain (they'll just no longer be associated with that initiative).

#### Get Initiative Projects
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_ID="initiative-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ initiative(id: \\\"$INITIATIVE_ID\\\") { id name projects { nodes { id name } } } }\"}" | jq .
```

#### Update Initiative Name
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_ID="initiative-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { initiativeUpdate(id: \\\"$INITIATIVE_ID\\\", input: { name: \\\"New Initiative Name\\\" }) { success initiative { id name } } }\"}" | jq .
```

#### Query Initiative-Project Relationships
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
# Get all initiative-project relationships (useful for finding relationship IDs)
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ initiativeToProjects { nodes { id initiative { name } project { name } } } }"}' | \
jq -r '.data.initiativeToProjects.nodes[] | "\(.id) | \(.initiative.name) → \(.project.name)"'
```

**Use this to find relationship IDs** when you need to delete initiative-project relationships. The `id` field is what you need for `initiativeToProjectDelete`.

#### Assign Project to Initiative
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_ID="initiative-id-here" && \
PROJECT_ID="project-id-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { initiativeToProjectCreate(input: { initiativeId: \\\"$INITIATIVE_ID\\\", projectId: \\\"$PROJECT_ID\\\" }) { success initiativeToProject { id initiative { name } project { name } } } }\"}" | jq .
```

**Note:** If a project is already in an initiative, you'll get an error "Project already related to a parent or child initiative." Projects can be in multiple initiatives, but there may be restrictions. Use `initiativeToProjectDelete` to remove a project from an initiative first if needed.

#### Remove Project from Initiative
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_ID="initiative-id-here" && \
PROJECT_ID="project-id-here" && \
# Query initiativeToProjects to get the relationship ID
RELATION_ID=$(curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ initiativeToProjects { nodes { id initiative { id name } project { id name } } } }\"}" | \
jq -r ".data.initiativeToProjects.nodes[] | select(.initiative.id == \"$INITIATIVE_ID\" and .project.id == \"$PROJECT_ID\") | .id") && \
# Delete the relationship using the relationship ID
if [ -n "$RELATION_ID" ]; then
  curl -s -X POST "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"mutation { initiativeToProjectDelete(id: \\\"$RELATION_ID\\\") { success } }\"}" | jq .
else
  echo "Relationship not found"
fi
```

**Alternative: Query by initiative name and project name pattern:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
INITIATIVE_NAME="Core Systems" && \
PROJECT_NAME_PATTERN="Launch" && \
# Get all relationship IDs matching the criteria
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ initiativeToProjects { nodes { id initiative { name } project { name } } } }\"}" | \
jq -r ".data.initiativeToProjects.nodes[] | select(.initiative.name == \"$INITIATIVE_NAME\" and (.project.name | contains(\"$PROJECT_NAME_PATTERN\"))) | .id" | \
while read relation_id; do
  PROJECT_NAME=$(curl -s -X POST "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"{ initiativeToProject(id: \\\"$relation_id\\\") { project { name } } }\"}" | \
  jq -r '.data.initiativeToProject.project.name') && \
  curl -s -X POST "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"mutation { initiativeToProjectDelete(id: \\\"$relation_id\\\") { success } }\"}" | \
  jq -r ".data.initiativeToProjectDelete | if .success then \"✅ Removed $PROJECT_NAME\" else \"❌ Failed\" end"
done
```

**Key Points:**
- `initiativeToProjectDelete` requires the **relationship ID** (not project ID or initiative ID)
- Query `initiativeToProjects` to get relationship IDs
- The relationship ID is the `id` field on the `InitiativeToProject` node
- Projects can be in multiple initiatives, so you may need to filter by both initiative and project

### Cycles

**Cycles are time-based iterations** (like sprints) that group work by time periods. Issues can be assigned to cycles to organize work by iteration.

#### List All Cycles
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ cycles { nodes { id number name startsAt endsAt } } }"}' | \
jq -r '.data.cycles.nodes[] | "Cycle \(.number): \(.startsAt) to \(.endsAt) | ID: \(.id)"'
```

#### Get Issue's Current Cycle
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ISSUE_ID="DEV-123" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ issue(id: \\\"$ISSUE_ID\\\") { identifier title cycle { id number startsAt endsAt } } }\"}" | jq .
```

#### Assign Issue to Cycle
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ISSUE_ID="DEV-123" && \
CYCLE_ID="cycle-uuid-here" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { cycleId: \\\"$CYCLE_ID\\\" }) { success issue { identifier cycle { number } } } }\"}" | jq .
```

#### Move Issues Between Cycles
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
# Get Cycle 37 ID
CYCLE37_ID=$(curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ cycles { nodes { id number } } }"}' | \
jq -r '.data.cycles.nodes[] | select(.number == 37) | .id') && \
# Move issues to Cycle 37
for issue_id in DEV-309 DEV-324 DEV-325 DEV-310; do
  curl -s -X POST "https://api.linear.app/graphql" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"mutation { issueUpdate(id: \\\"$issue_id\\\", input: { cycleId: \\\"$CYCLE37_ID\\\" }) { success issue { identifier cycle { number } } } }\"}" | \
  jq -r ".data.issueUpdate | if .success then \"✅ \(.issue.identifier) → Cycle \(.issue.cycle.number)\" else \"❌ $issue_id\" end"
done
```

#### Remove Issue from Cycle
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ISSUE_ID="DEV-123" && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { cycleId: null }) { success issue { identifier cycle { number } } } }\"}" | jq .
```

**Key Points:**
- Cycles are numbered iterations (Cycle 36, Cycle 37, etc.)
- Each cycle has a start and end date
- Issues can be assigned to cycles via `cycleId` in `issueUpdate`
- Use `cycleId: null` to remove an issue from a cycle
- Cycles help organize work by time periods (like sprints)

### Getting User/Viewer Information

#### Get Current User (Viewer)
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | jq .
```

#### Get User ID (for assigning leads, etc.)
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}' | jq -r '.data.viewer.id'
```
