# Google Drive

> List files, search files, read file content via Drive API

## Skills Provided

- **files** (connection) — List, search, read cloud files

## Auth

Uses service account authentication with domain-wide delegation.

**Required files:**
- `user/skills-data/google-workspace/service-account-key.json`

**Required scopes (configured in Google Admin Console):**
```
https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/documents.readonly
```

### Setup

See the full setup guide for Google Workspace service account configuration:

1. **Google Cloud Console:** Create project, enable Drive API + Docs API, create service account, download JSON key
2. **Google Admin Console:** Configure domain-wide delegation with Client ID and scopes
3. **Local:** Place JSON key at `user/skills-data/google-workspace/service-account-key.json`

### Dependencies

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## Usage

Use the Python script: `apps/google-drive/drive.py`

**⚠️ IMPORTANT:** The `--user` flag MUST come BEFORE the subcommand.

### List Files

```bash
# List recent files (default 20, sorted by modified time)
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com list

# List files in a specific folder
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com list --folder-id "FOLDER_ID"

# List more results
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com list --max-results 50
```

### Search Files

```bash
# Search by name
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com search --query "meeting notes"

# Search for specific file type
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com search --query "budget" --type doc
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com search --query "report" --type sheet
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com search --query "project" --type folder
```

**File type filters:** `doc`, `sheet`, `slide`, `folder`, `pdf`

### Get File Metadata

```bash
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com metadata --file-id "FILE_ID"
```

### Read File Content

**Two commands available:**
- `read` - Downloads entire file first, then truncates (works for all file types)
- `read-doc` - Uses Docs API for efficient partial reads of large Google Docs

```bash
# Read entire file (Google Docs exported as plain text)
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com read --file-id "FILE_ID"

# Read first 5000 characters
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com read --file-id "FILE_ID" --max-chars 5000

# Read with offset (for pagination)
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com read --file-id "FILE_ID" --max-chars 5000 --offset 5000
```

### Read Large Google Docs (Efficient)

For very large Google Docs (100+ pages), use `read-doc`:

```bash
# Read first 5000 characters efficiently
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com read-doc --file-id "DOC_ID" --max-chars 5000

# Read starting from character 10000
python3 "$PROJECT_ROOT/apps/google-drive/drive.py" --user user@example.com read-doc --file-id "DOC_ID" --max-chars 5000 --start 10000
```

**When to use which:**
- `read` - Small/medium files, non-Google-Doc files
- `read-doc` - Large Google Docs where you only need a portion

**Supported file types for `read`:**
- **Google Docs** → Exported as plain text
- **Google Sheets** → Exported as CSV
- **Google Slides** → Exported as plain text
- **Text files** → Read directly
- **Binary files** → Returns metadata only

---

## Error Handling

**Common errors:**

1. **Service account key file not found:**
   **Solution:** Ensure JSON key file is at `user/skills-data/google-workspace/service-account-key.json`

2. **Domain-wide delegation not configured (403 Access denied):**
   **Solution:** Verify domain-wide delegation in Admin Console with correct Client ID and scopes

3. **API not enabled (403):**
   **Solution:** Enable Drive API and Docs API in Google Cloud Console

4. **Invalid user email (403 User not found):**
   **Solution:** Ensure email address exists in your Google Workspace domain

---

## Rate Limits

- Drive: ~10,000 queries/100 seconds
- If you receive 429 errors, wait before retrying
