# Linear Skill

## Intention: Create tasks, manage issues, or work with Linear

When the user mentions adding a task, creating a task, getting tasks, or anything related to team management, projects, or issues, use the Linear GraphQL API directly.

### Linear API Integration

Use the Linear GraphQL API endpoint: `https://api.linear.app/graphql`

**Authentication:** Use personal API key from `.env` file. **CRITICAL:** For personal API keys, use `Authorization: <API_KEY>` (without "Bearer"). For OAuth tokens, use `Authorization: Bearer <TOKEN>`.

**Basic Query Pattern:**
```bash
# Unconditional sourcing (simpler and more reliable - see boot.md)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues { nodes { id title } } }"}' | jq .
```

**Troubleshooting Auth Errors:**
- If you get `AUTHENTICATION_ERROR`, verify the key exists: `grep LINEAR_API_KEY "$PROJECT_ROOT/.env"`
- **Never use "Bearer" prefix** for personal API keys - Linear personal keys are used directly
- If auth still fails, try unconditional sourcing pattern above (more reliable than conditional)

**Common Queries:**

- **Get all issues:** `{ issues { nodes { id title description } } }`
- **Get user's assigned issues:** `{ viewer { assignedIssues { nodes { id title } } } }`
- **Get user's assigned issues due this week:** `{ viewer { assignedIssues(filter: { dueDate: { gte: "YYYY-MM-DD", lte: "YYYY-MM-DD" } }) { nodes { id identifier title description url priority state { name } dueDate assignee { name } team { name } } } } }`
- **Get specific issue:** `{ issue(id: "ISSUE-ID") { id title description } }`
- **Get team issues:** `{ team(id: "TEAM-ID") { issues { nodes { id title } } } }`

**Date Filtering:** Use ISO format (YYYY-MM-DD) for date filters.

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

**Note:** For detailed API documentation, use search (see `skills/search/README.md`) to find Linear API docs or visit https://linear.app/developers/graphql

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

**Note:** Project-specific reference IDs (user IDs, team IDs, label IDs) should be stored in project-specific rule files, not in this general skill file.

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

