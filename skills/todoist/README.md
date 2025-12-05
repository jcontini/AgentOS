# Todoist Skill

## Intention: See and manage Todoist tasks (create, update, complete, delete, list)

When the user mentions adding a task, creating a task, getting tasks, completing tasks, or anything related to personal task management in Todoist, use the Todoist REST API directly.

**Important:** When retrieving a task, always check for and display its subtasks. Subtasks are tasks with a `parent_id` matching the parent task's ID. Use the `parent_id` query parameter to fetch subtasks.

### AI Task Creation Defaults

When creating tasks on behalf of the user:
1. **Default due date:** If user doesn't specify a date, set `"due_string": "today"`
2. **AI label:** Always include `"labels": ["AI"]` so user knows the task was created by AI
3. **Project assignment:** If user specifies a project, include `"project_id"` at creation time since it cannot be updated later (must delete/recreate to change)

**Example (AI-created task):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Task content here",
    "due_string": "today",
    "labels": ["AI"]
  }' | jq .
```

**Example (AI-created task with project and priority):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PROJECT_ID="YOUR_PROJECT_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Task content here\",
    \"project_id\": $PROJECT_ID,
    \"priority\": 4,
    \"due_string\": \"today\",
    \"labels\": [\"AI\"]
  }" | jq .
```

### Todoist API Integration

Use the Todoist REST API endpoint: `https://api.todoist.com/rest/v2`

**Authentication:** Use API token from `.env` file. The API token is obtained from Todoist Settings > Integrations > Developer section.

**Basic Query Pattern:**
```bash
# Unconditional sourcing (simpler and more reliable - see boot.md)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq .
```

**Troubleshooting Auth Errors:**
- If you get authentication errors, verify the token exists: `grep TODOIST_API_TOKEN "$PROJECT_ROOT/.env"`
- Ensure token is prefixed with `Bearer` in Authorization header
- If auth still fails, try unconditional sourcing pattern above (more reliable than conditional)

### Common Operations

#### Get All Tasks

**Get active tasks (parent tasks only, no subtasks):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | select(.parent_id == null) | "\(.id) | \(.content) | Due: \(.due.date // "None") | Priority: \(.priority) | Project: \(.project_id)"'
```

**Get active tasks with subtasks:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ALL_TASKS=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
echo "$ALL_TASKS" | jq -r '.[] | select(.parent_id == null) | "\(.id) | \(.content) | Due: \(.due.date // "None") | Priority: \(.priority)"' | while read -r line; do
  TASK_ID=$(echo "$line" | cut -d'|' -f1 | xargs)
  echo "$line"
  echo "$ALL_TASKS" | jq -r ".[] | select(.parent_id == $TASK_ID) | \"  └─ \(.id) | \(.content) | Due: \(.due.date // \"None\")\""
done
```

**Get completed tasks (requires Sync API, see below):**
- Use Sync API for completed tasks: `https://api.todoist.com/sync/v9/sync`

#### Get Tasks by Project

**First, get project ID:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.name)"'
```

**Then get tasks for specific project:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PROJECT_ID="YOUR_PROJECT_ID" && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.content) | Due: \(.due.date // "None")"'
```

#### Get Tasks Due Today/This Week

**Due today:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TODAY=$(date +%Y-%m-%d) && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?filter=today" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.content) | Due: \(.due.date // "None") | Priority: \(.priority)"'
```

**Due this week:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?filter=7 days" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.content) | Due: \(.due.date // "None") | Priority: \(.priority)"'
```

**Note:** Todoist supports filter strings like `today`, `overdue`, `7 days`, `no date`, etc. See Todoist API docs for full filter syntax.

#### Create a Task

**Basic task:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Task content here",
    "due_string": "today"
  }' | jq .
```

**Task with due date:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Task content here",
    "due_string": "2025-01-15",
    "priority": 4
  }' | jq .
```

**Task in specific project:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PROJECT_ID="YOUR_PROJECT_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Task content here\",
    \"project_id\": $PROJECT_ID,
    \"due_string\": \"today\"
  }" | jq .
```

**Task with description:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Task content here",
    "description": "Additional notes or description",
    "due_string": "today"
  }' | jq .
```

**Create subtask (child task):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PARENT_TASK_ID="YOUR_PARENT_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Subtask content here\",
    \"parent_id\": $PARENT_TASK_ID,
    \"due_string\": \"today\"
  }" | jq .
```

**Priority levels:** 1 (normal), 2, 3, 4 (urgent)

#### Update a Task

**Update task content:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated task content"
  }' | jq .
```

**Update due date:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "due_string": "tomorrow"
  }' | jq .
```

**Update priority:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": 4
  }' | jq .
```

**Move task to different project (workaround):**
**⚠️ Important:** The Todoist REST API v2 does NOT support updating `project_id` via POST. This has been confirmed through testing - attempting to update `project_id` returns the task unchanged. To move a task to a different project, you must delete and recreate it.

**Step 1: Get task details:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq .
```

**Step 2: Delete old task and recreate in new project:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
OLD_TASK_ID="YOUR_TASK_ID" && \
NEW_PROJECT_ID="TARGET_PROJECT_ID" && \
# Get task details first
TASK_DATA=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks/$OLD_TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
# Extract due date (prefer due.string, fallback to due.date)
DUE_STRING=$(echo "$TASK_DATA" | jq -r 'if .due then (.due.string // .due.date) else null end') && \
# Delete old task
curl -s -X DELETE "https://api.todoist.com/rest/v2/tasks/$OLD_TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" && \
# Recreate with new project_id, preserving all other fields
PAYLOAD=$(echo "$TASK_DATA" | jq --arg proj "$NEW_PROJECT_ID" --arg due "$DUE_STRING" '{
  content: .content,
  description: (.description // ""),
  project_id: ($proj | tonumber),
  priority: .priority,
  label_ids: (.labels | map(.id))
} + (if $due != "null" and $due != "" then {due_string: $due} else {} end)') && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq .
```

**Note:** When recreating, preserve all fields: `content`, `description`, `priority`, `due_string`/`due`, `label_ids`, `parent_id` (if subtask), etc. The script above handles due dates by preferring `due.string` (natural language like "tomorrow") and falling back to `due.date` (YYYY-MM-DD format).

#### Complete a Task

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID/close" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq .
```

#### Reopen a Task

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID/reopen" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq .
```

#### Delete a Task

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X DELETE "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

### Projects

#### List All Projects

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.name) | Order: \(.order)"'
```

#### Create a Project

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.todoist.com/rest/v2/projects" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Name"
  }' | jq .
```

### Labels

#### List All Labels

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.todoist.com/rest/v2/labels" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.name)"'
```

#### Add Label to Task

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
LABEL_ID="YOUR_LABEL_ID" && \
curl -s -X POST "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"label_ids\": [$LABEL_ID]
  }" | jq .
```

### Task Links

**Get task link (opens in native Todoist app):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
TASK_LINK="https://app.todoist.com/app/task/$TASK_ID" && \
echo "$TASK_LINK"
```

**Example: Get task with link:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
TASK=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
CONTENT=$(echo "$TASK" | jq -r '.content') && \
LINK=$(echo "$TASK" | jq -r '.url') && \
echo "Task: $CONTENT" && \
echo "Link: $LINK"
```

**Note:** The API `url` field returns `https://app.todoist.com/app/task/{id}` format. While Todoist shows a deprecation warning, this format currently works and opens in the native app. Todoist's "Copy link" feature generates slug-based URLs (`task-name-hash`), but the numeric ID format from the API works for programmatic linking.

### Subtasks

**Important:** When retrieving a task, always check for subtasks by querying tasks with `parent_id` matching the task ID.

**Get subtasks for a task:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
PARENT_TASK_ID="YOUR_TASK_ID" && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks?parent_id=$PARENT_TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r '.[] | "\(.id) | \(.content) | Due: \(.due.date // "None") | Priority: \(.priority)"'
```

**Get all tasks with their subtasks (hierarchical view):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
ALL_TASKS=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
echo "$ALL_TASKS" | jq -r '.[] | select(.parent_id == null) | "\(.id) | \(.content)"' | while read -r line; do
  TASK_ID=$(echo "$line" | cut -d'|' -f1 | xargs)
  TASK_CONTENT=$(echo "$line" | cut -d'|' -f2- | xargs)
  echo "$TASK_CONTENT"
  echo "$ALL_TASKS" | jq -r ".[] | select(.parent_id == $TASK_ID) | \"  └─ \(.content)\""
done
```

### Finding Tasks

**Search tasks by content:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
SEARCH_TERM="keyword" && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | \
jq -r ".[] | select(.content | contains(\"$SEARCH_TERM\")) | \"\(.id) | \(.content) | Due: \(.due.date // \"None\")\""
```

**Get task by ID (with subtasks):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
TASK=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
SUBTASKS=$(curl -s -X GET "https://api.todoist.com/rest/v2/tasks?parent_id=$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN") && \
echo "$TASK" | jq . && \
echo "Subtasks:" && \
echo "$SUBTASKS" | jq -r '.[] | "  - \(.id) | \(.content) | Due: \(.due.date // "None")"'
```

**Get task by ID (simple, no subtasks):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
TASK_ID="YOUR_TASK_ID" && \
curl -s -X GET "https://api.todoist.com/rest/v2/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" | jq .
```

### Date Format

**Due date formats supported:**
- `today`, `tomorrow`, `next week`, `next monday`, etc. (natural language)
- `2025-01-15` (YYYY-MM-DD)
- `2025-01-15T14:00` (with time)

### Best Practices

1. **Always check for subtasks:** When retrieving a task, also query for subtasks using `parent_id` parameter
2. **Batch operations:** Use filters and project_id parameters to reduce API calls
3. **Cache project/label IDs:** Store frequently used IDs to avoid repeated lookups
4. **Error handling:** Check HTTP status codes and handle rate limits (429)
5. **Task IDs:** Store task IDs when creating tasks for future updates/deletes
6. **Parent vs subtask:** Filter by `parent_id == null` to get only parent tasks, or use `parent_id=TASK_ID` to get subtasks
7. **Project assignment:** Always specify `project_id` when creating tasks if you know the target project. The API does NOT support updating `project_id` after creation - you must delete and recreate the task to move it.
8. **Moving tasks:** When moving a task to a different project, fetch all task fields first, then delete and recreate with the new `project_id` to preserve all metadata (description, priority, due date, labels, etc.)
9. **Task links:** The API `url` field returns `https://app.todoist.com/app/task/{id}` format. While Todoist shows a warning that this format will be deprecated, it currently still works and opens in the native app. Use the API's `url` field directly, or construct as: `https://app.todoist.com/app/task/${TASK_ID}`. Note: Todoist's "Copy link" feature generates a slug-based URL (`book-fl-dc-flight-6fQhp2xCJHwmvMMg`), but the numeric ID format from the API still works for native app deep linking.

### Rate Limits

Todoist API has rate limits. If you receive 429 errors, wait before retrying. The REST API typically allows 450 requests per 15 minutes.

### Note

For detailed API documentation, use search (see `skills/exa/README.md`) to find Todoist API docs or visit https://developer.todoist.com/rest/v2/

