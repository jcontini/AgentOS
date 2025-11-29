# Google Workspace Skill

## Intention: Access Gmail and Google Drive via Google Workspace APIs

This skill provides access to Gmail (read emails, create drafts) and Google Drive (list, search, read files) using service account authentication with domain-wide delegation.

**Included APIs:**
- **Gmail** - Read emails, search messages, create drafts
- **Drive** - List files, search files, read file content (including Google Docs as plain text)

**Important:** This skill uses service account authentication with domain-wide delegation, allowing it to access any Google Workspace account in your domain without OAuth flows.

### Prerequisites

- Google Workspace account with admin access
- Python 3.6+ installed

### Dependencies

Install required Python packages:
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## Setup

This skill uses service account authentication with domain-wide delegation. This is a one-time setup that enables access to both Gmail and Drive APIs.

### Phase 1: Google Cloud Console Setup

**Step 1.1: Create/Select Project**
- Navigate to: `https://console.cloud.google.com/projectcreate`
- **If creating new:** Name it `google-workspace-api` (or similar)
- **If using existing:** Select from project dropdown
- **Verification:** Project is selected/created and visible in top bar

**Step 1.2: Enable APIs**

Enable the Gmail, Drive, and Docs APIs:

- **Gmail API:** Navigate to `https://console.cloud.google.com/apis/library/gmail.googleapis.com`
  - Ensure project is selected → Click **"Enable"**
- **Drive API:** Navigate to `https://console.cloud.google.com/apis/library/drive.googleapis.com`
  - Ensure project is selected → Click **"Enable"**
- **Docs API:** Navigate to `https://console.cloud.google.com/apis/library/docs.googleapis.com`
  - Ensure project is selected → Click **"Enable"**
- **Verification:** All APIs show as "Enabled" with green checkmark

**Step 1.3: Create Service Account**
- Navigate to: `https://console.cloud.google.com/iam-admin/serviceaccounts`
- Ensure project is selected
- Click **"Create Service Account"**
- **Service account name:** `workspace-api-service`
- **Service account ID:** Auto-generated (or customize)
- **Description:** "Service account for Google Workspace API access"
- Click **"Create and Continue"**
- **Grant roles:** Skip (click "Continue" - no IAM roles needed)
- Click **"Done"**
- **Verification:** Service account appears in list with email like `workspace-api-service@PROJECT-ID.iam.gserviceaccount.com`

**Step 1.4: Create Service Account Key (JSON)**

⚠️ **Browser Automation Notes for Google Cloud Console**

When automating Google Cloud Console setup with browser automation tools:

**Multi-step wizards:**
- Google Cloud Console uses multi-step wizards (e.g., "step 1 of 3")
- Each step may have async validation/processing
- Wait for step completion indicators before proceeding

**Service account creation flow:**
1. Fill in name and description
2. Click "Create and continue" → wait for processing
3. Skip permissions (optional) → click "Continue"
4. Skip principals (optional) → click "Done"
5. May need to navigate away and back to see created account

**Navigation patterns:**
- Some features may not be accessible via direct URL
- Use navigation menu/sidebar instead of direct URLs when needed

⚠️ **Common Issue: Organization Policy Blocking Key Creation**

If you see an error dialog "Service account key creation is disabled", an organization policy is blocking key creation:

- **Policy ID:** `iam.disableServiceAccountKeyCreation` (legacy constraint)
- **Solution:** As organization admin:
  1. **Grant yourself Organization Policy Administrator role:**
     - Navigate to: `https://console.cloud.google.com/iam-admin/iam?organizationId=YOUR-ORG-ID`
     - Find your user account, click "Edit principal"
     - Add role: **"Organization Policy Administrator"**
     - Save and wait a few minutes
  
  2. **Disable the organization policy:**
     - Navigate to: `https://console.cloud.google.com/iam-admin/orgpolicies/list?organizationId=YOUR-ORG-ID`
     - Search for "Disable service account key creation"
     - **Important:** Disable the LEGACY constraint (`iam.disableServiceAccountKeyCreation`)
     - Click "Manage policy" → Change "Policy source" to **"Inherit parent's policy"**
     - Click "Set policy"
  
  3. **Retry key creation**

**Creating the Key:**
- Click on the service account email (from Step 1.3)
- Go to **"Keys"** tab
- Click **"Add Key"** → **"Create new key"**
- Select **"JSON"** format
- Click **"Create"**
- **File downloads automatically**
- **Verification:** JSON file downloaded

**Step 1.5: Get Service Account Client ID**
- Still on service account details page
- Look for **"Client ID"** (long numeric string like `123456789012345678901`)
- **Copy this Client ID** - needed for Phase 2
- **Alternative:** The Client ID is also in the JSON file under `client_id` field

### Phase 2: Google Workspace Admin Console Setup

**Step 2.1: Navigate to Domain-Wide Delegation**
- Navigate to: `https://admin.google.com/ac/owl/domainwidedelegation`
- Or: **Admin Console** → **Security** → **Access and data control** → **API controls** → **Manage Domain Wide Delegation**

**Step 2.2: Add Service Account Delegation**
- Click **"Add new"**
- **Client ID:** Paste the Client ID from Step 1.5
- **OAuth Scopes (comma-delimited):**
  ```
  https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/documents.readonly
  ```
- Click **"Authorize"**
- **Verification:** Service account appears in delegation list with all scopes shown

**Note:** If you already have some scopes configured, you can edit the existing entry to add new scopes.

### Phase 3: Local Setup

**Step 3.1: Move Service Account Key to Project**
```bash
# Create the google-workspace skills-data directory
mkdir -p "$PROJECT_ROOT/user/skills-data/google-workspace"

# Move the downloaded JSON key file
mv ~/Downloads/*-*.json "$PROJECT_ROOT/user/skills-data/google-workspace/service-account-key.json"

# Set permissions (owner read/write only)
chmod 600 "$PROJECT_ROOT/user/skills-data/google-workspace/service-account-key.json"
```

**Verification:** File exists at `user/skills-data/google-workspace/service-account-key.json`

**Step 3.2: Verify .gitignore**
- Ensure `user/` directory is in `.gitignore` (it should be by default)
- **Verification:** `git status` shows the file is not tracked

---

## Gmail API

Use the Python script: `skills/google-workspace/gmail.py`

**⚠️ IMPORTANT:** The `--user` flag MUST come BEFORE the subcommand.

### List Messages

```bash
# List recent emails (default 10)
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com list

# List with search query
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com list --query "from:sender@domain.com"

# List unread emails
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com list --query "is:unread"

# List more results
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com list --max-results 50
```

**Gmail Search Query Syntax:**
- `from:email@domain.com` - Messages from sender
- `to:email@domain.com` - Messages to recipient
- `subject:keyword` - Messages with keyword in subject
- `has:attachment` - Messages with attachments
- `is:unread` / `is:read` / `is:starred` - Message state
- `after:YYYY/MM/DD` / `before:YYYY/MM/DD` - Date filters
- `newer_than:7d` / `older_than:30d` - Relative date filters

### Get Full Message Content

```bash
# Get message by ID
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com get --message-id "MESSAGE_ID"
```

### Create Draft Email

```bash
python3 "$PROJECT_ROOT/skills/google-workspace/gmail.py" --user user@example.com draft \
  --to "recipient@example.com" \
  --subject "Email Subject" \
  --body "Email body text here"
```

---

## Drive API

Use the Python script: `skills/google-workspace/drive.py`

**⚠️ IMPORTANT:** The `--user` flag MUST come BEFORE the subcommand.

### List Files

```bash
# List recent files (default 20, sorted by modified time)
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com list

# List files in a specific folder
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com list --folder-id "FOLDER_ID"

# List more results
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com list --max-results 50
```

### Search Files

```bash
# Search by name
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com search --query "meeting notes"

# Search for specific file type
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com search --query "budget" --type doc
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com search --query "report" --type sheet
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com search --query "project" --type folder
```

**File type filters:** `doc`, `sheet`, `slide`, `folder`, `pdf`

### Get File Metadata

```bash
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com metadata --file-id "FILE_ID"
```

### Read File Content

**Two commands available:**
- `read` - Downloads entire file first, then truncates (works for all file types)
- `read-doc` - Uses Docs API for efficient partial reads of large Google Docs (recommended for large docs)

```bash
# Read entire file (Google Docs exported as plain text)
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com read --file-id "FILE_ID"

# Read first 5000 characters (downloads entire file first)
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com read --file-id "FILE_ID" --max-chars 5000

# Read with offset (for pagination through large files)
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com read --file-id "FILE_ID" --max-chars 5000 --offset 5000
```

### Read Large Google Docs (Efficient)

For very large Google Docs (100+ pages), use `read-doc` which uses the Docs API to efficiently read portions without downloading the entire document:

```bash
# Read first 5000 characters of a large Google Doc (efficient - doesn't download whole doc)
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com read-doc --file-id "DOC_ID" --max-chars 5000

# Read starting from character 10000
python3 "$PROJECT_ROOT/skills/google-workspace/drive.py" --user user@example.com read-doc --file-id "DOC_ID" --max-chars 5000 --start 10000
```

**When to use which:**
- `read` - For small/medium files, non-Google-Doc files (sheets, text files, etc.)
- `read-doc` - For large Google Docs where you only need a portion

**Supported file types for `read`:**
- **Google Docs** → Exported as plain text
- **Google Sheets** → Exported as CSV
- **Google Slides** → Exported as plain text
- **Text files** → Read directly (txt, json, xml, etc.)
- **Binary files** → Returns metadata only

**Response includes:** `totalChars`, `returnedChars`, and `truncated` fields

---

## Error Handling

**Common errors:**

1. **Service account key file not found:**
   ```
   FileNotFoundError: Service account key file not found
   ```
   **Solution:** Ensure JSON key file is at `user/skills-data/google-workspace/service-account-key.json`

2. **Domain-wide delegation not configured (403 Access denied):**
   ```
   API error: 403 - Access denied
   ```
   **Solution:** Verify domain-wide delegation in Admin Console with correct Client ID and all scopes

3. **API not enabled (403):**
   ```
   API error: 403 - API has not been used
   ```
   **Solution:** Enable both Gmail and Drive APIs in Google Cloud Console

4. **Invalid user email (403 User not found):**
   ```
   API error: 403 - User not found
   ```
   **Solution:** Ensure email address exists in your Google Workspace domain

---

## Required Scopes

The following OAuth scopes must be configured in domain-wide delegation:

| Scope | Purpose |
|-------|---------|
| `https://www.googleapis.com/auth/gmail.readonly` | Read emails |
| `https://www.googleapis.com/auth/gmail.compose` | Create drafts |
| `https://www.googleapis.com/auth/drive.readonly` | Read Drive files |
| `https://www.googleapis.com/auth/documents.readonly` | Read Google Docs (efficient for large docs) |

**Full scopes string for Admin Console:**
```
https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/documents.readonly
```

---

## Troubleshooting

**Authentication issues:**
- Verify service account JSON key file exists and is readable
- Check domain-wide delegation has correct Client ID
- Ensure all scopes are listed (Gmail + Drive)
- Domain-wide delegation changes can take up to 24 hours (usually minutes)

**File not readable:**
- Binary files (images, PDFs, etc.) cannot be read as text
- Use `--max-chars` for very large documents to avoid timeout

**Rate limits:**
- Gmail: ~1,000,000 quota units/day
- Drive: ~10,000 queries/100 seconds
- If you receive 429 errors, wait before retrying

---

## Migration from Old Gmail Skill

If you previously used `skills/gmail/`, migrate your service account key:

```bash
# Create new directory
mkdir -p "$PROJECT_ROOT/user/skills-data/google-workspace"

# Move the key file
mv "$PROJECT_ROOT/user/skills-data/gmail/gmail-service-account-key.json" \
   "$PROJECT_ROOT/user/skills-data/google-workspace/service-account-key.json"

# Update domain-wide delegation scopes in Admin Console to add Drive scope
```

Then update your scripts to use `skills/google-workspace/gmail.py` instead of `skills/gmail/gmail.py`.

