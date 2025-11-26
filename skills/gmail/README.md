# Gmail Skill

## Intention: Read emails and create drafts from Gmail

When the user mentions reading emails, checking messages, searching emails, or creating draft emails, use the Gmail API via the Python script.

**Important:** This skill uses service account authentication with domain-wide delegation, allowing it to access any Google Workspace account in your domain without OAuth flows.

### Prerequisites

- Google Workspace account with admin access
- Python 3.6+ installed

### Setup

This skill uses service account authentication with domain-wide delegation, allowing access to any Google Workspace account in your domain without OAuth flows.

#### Phase 1: Google Cloud Console Setup

**Step 1.1: Create/Select Project**
- Navigate to: `https://console.cloud.google.com/projectcreate`
- **If creating new:** Name it `gmail-api-access` (or similar)
- **If using existing:** Select from project dropdown
- **Verification:** Project is selected/created and visible in top bar

**Step 1.2: Enable Gmail API**
- Navigate to: `https://console.cloud.google.com/apis/library/gmail.googleapis.com`
- Ensure project is selected
- Click **"Enable"** button
- Wait for enablement to complete
- **Verification:** API shows as "Enabled" with green checkmark

**Step 1.3: Create Service Account**
- Navigate to: `https://console.cloud.google.com/iam-admin/serviceaccounts`
- Ensure project is selected
- Click **"Create Service Account"**
- **Service account name:** `gmail-api-service`
- **Service account ID:** Auto-generated (or customize)
- **Description:** "Service account for Gmail API access via local scripts"
- Click **"Create and Continue"**
- **Grant roles:** Skip (click "Continue" - no IAM roles needed)
- Click **"Done"**
- **Verification:** Service account appears in list with email like `gmail-api-service@PROJECT-ID.iam.gserviceaccount.com`

**Step 1.4: Create Service Account Key (JSON)**

**⚠️ Browser Automation Notes for Google Cloud Console**

When automating Google Cloud Console setup with browser automation tools (see `skills/browser/README.md` for general browser automation patterns), be aware of these GCP-specific patterns:

**Multi-step wizards:**
- Google Cloud Console uses multi-step wizards (e.g., "step 1 of 3")
- Each step may have async validation/processing
- Wait for step completion indicators before proceeding
- Some steps are optional - can skip by clicking "Continue" or "Done" without filling fields

**Service account creation flow:**
1. Fill in name and description
2. Click "Create and continue" → wait for processing
3. Skip permissions (optional) → click "Continue"
4. Skip principals (optional) → click "Done"
5. May need to navigate away and back to see created account

**Navigation patterns:**
- Some features may not be accessible via direct URL
- Organization-scoped features may require organization to be selected first
- Use navigation menu/sidebar instead of direct URLs when needed
- Look for features in navigation menus, sidebar, or search

**⚠️ Common Issue: Organization Policy Blocking Key Creation**

If you see an error dialog "Service account key creation is disabled", an organization policy is blocking key creation:
- **Policy ID:** `iam.disableServiceAccountKeyCreation` (legacy constraint)
- **Root Cause:** Your Google Cloud organization has a policy that prevents service account key creation for security reasons
- **Solution:** As organization admin, you need to:
  1. **Grant yourself Organization Policy Administrator role** (if not already granted):
     - Navigate to: `https://console.cloud.google.com/iam-admin/iam?organizationId=YOUR-ORG-ID`
     - Find your user account (e.g., `user@domain.com`)
     - Click "Edit principal" (pencil icon)
     - Click "Add another role"
     - Search for and select: **"Organization Policy Administrator"** (`roles/orgpolicy.policyAdmin`)
     - Click "Save"
     - Wait a few minutes for role to propagate
  
  2. **Disable the organization policy:**
     - Navigate to: `https://console.cloud.google.com/iam-admin/orgpolicies/list?organizationId=YOUR-ORG-ID`
     - Search for "Disable service account key creation" or filter by `disableServiceAccountKeyCreation`
     - **Important:** There may be TWO policies:
       - `iam.managed.disableServiceAccountKeyCreation` (managed constraint - newer)
       - `iam.disableServiceAccountKeyCreation` (legacy constraint - older)
     - **You need to disable the LEGACY constraint** (`iam.disableServiceAccountKeyCreation`)
     - Click on the legacy policy (it will say "Legacy" in the name)
     - Click "Manage policy"
     - In the edit dialog:
       - Change "Policy source" from **"Override parent's policy"** to **"Inherit parent's policy"**
       - This removes the enforcement rule
     - Click "Set policy"
     - **Verification:** Policy status changes to "Not enforced"
     - Wait a few minutes for policy to propagate
  
  3. **Retry key creation** (go back to Step 1.4 and continue)

**Note:** Both legacy and managed constraints can exist simultaneously. The legacy constraint (`iam.disableServiceAccountKeyCreation`) takes precedence, so you must disable it even if the managed constraint shows "Not enforced".

**Error dialog handling:**
- When organization policies block actions, error dialogs appear
- Error dialogs may appear on top of underlying dialogs (stacked dialogs)
- If error dialog appears, cancel the underlying dialog first
- Error dialog should auto-dismiss when underlying action is canceled
- Read error messages for policy ID and explanation

**Creating the Key:**
- Click on the service account email (from Step 1.3)
- Go to **"Keys"** tab
- Click **"Add Key"** → **"Create new key"**
- Select **"JSON"** format
- Click **"Create"**
- **File downloads automatically** - note the location (usually Downloads folder)
- **Verification:** JSON file downloaded (e.g., `PROJECT-ID-gmail-api-service-xxxxx.json`)
- **Important:** Save this file securely - it contains the private key!

**⚠️ File Download Handling:**
- Browser automation cannot access downloaded files directly
- After clicking "Create", check Downloads folder: `~/Downloads/*.json` (macOS) or `~/Downloads/*.json` (Linux)
- Use file system commands to locate and move the file:
  ```bash
  # Find the downloaded JSON file
  ls -lt ~/Downloads/*.json | head -1
  
  # Move to project location
  mv ~/Downloads/gmail-api-access-*-*.json "$PROJECT_ROOT/user/gmail-service-account-key.json"
  ```

**Step 1.5: Get Service Account Client ID**
- Still on service account details page
- Look for **"Client ID"** (long numeric string)
- **Copy this Client ID** - you'll need it for Phase 2
- **Alternative location:** The Client ID is also in the JSON file under `client_id` field
- **Verification:** Client ID copied (format: `123456789012345678901`)

#### Phase 2: Google Workspace Admin Console Setup

**Step 2.1: Navigate to Domain-Wide Delegation**
- Navigate to: `https://admin.google.com`
- Go to: **Security** → **Access and data control** → **API controls** → **Manage Domain Wide Delegation**
- Or direct URL: `https://admin.google.com/ac/owl/domainwidedelegation`
- **Verification:** Page shows list of existing delegations (may be empty)

**Step 2.2: Add Service Account Delegation**
- Click **"Add new"**
- **Client ID:** Paste the Client ID from Step 1.5
- **OAuth Scopes (comma-delimited):** Enter:
  ```
  https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.compose
  ```
- Click **"Authorize"**
- **Verification:** Service account appears in delegation list with the scopes shown
- **Note:** Changes can take up to 24 hours but typically happen within minutes

#### Phase 3: Local Setup

**Step 3.1: Move Service Account Key to Project**
- Move the downloaded JSON key file to: `$PROJECT_ROOT/user/gmail-service-account-key.json`
- Set permissions to `600` (owner read/write only):
  ```bash
  chmod 600 "$PROJECT_ROOT/user/gmail-service-account-key.json"
  ```
- **Verification:** File exists at destination with correct permissions

**Step 3.2: Verify .gitignore**
- Ensure `user/` directory is in `.gitignore` (it should be by default)
- The service account key file should not be committed to git
- **Verification:** Check with `git status` that the file is not tracked

### Dependencies

Install required Python packages:
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Gmail API Integration

Use the Python script: `skills/gmail/gmail.py`

**Authentication:** Uses service account JSON key file located at `user/gmail-service-account-key.json`. The script automatically handles service account authentication and user impersonation via domain-wide delegation.

**Basic Usage Pattern:**
```bash
# List recent emails
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com

# List emails with search query
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "from:sender@domain.com"

# Get full message content
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" get --user user@example.com --message-id "MESSAGE_ID"

# Create draft email
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" draft --user user@example.com --to "recipient@example.com" --subject "Subject" --body "Email body text"
```

**Output:** All commands output JSON to stdout for AI consumption.

### Common Operations

#### List Messages

**List recent emails (default 10):**
```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com
```

**List emails with search query:**
```bash
# Search by sender
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "from:sender@domain.com"

# Search by subject
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "subject:meeting"

# Search by date
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "after:2025/1/1"

# Search unread
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "is:unread"

# Combined search
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --query "from:sender@domain.com is:unread"
```

**List more results:**
```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com --max-results 50
```

**Gmail Search Query Syntax:**
- `from:email@domain.com` - Messages from sender
- `to:email@domain.com` - Messages to recipient
- `subject:keyword` - Messages with keyword in subject
- `has:attachment` - Messages with attachments
- `is:unread` - Unread messages
- `is:read` - Read messages
- `is:starred` - Starred messages
- `after:YYYY/MM/DD` - Messages after date
- `before:YYYY/MM/DD` - Messages before date
- `newer_than:7d` - Messages newer than 7 days
- `older_than:30d` - Messages older than 30 days

#### Get Full Message Content

**Get message by ID:**
```bash
# First, list messages to get message IDs
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" list --user user@example.com

# Then get full content
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" get --user user@example.com --message-id "MESSAGE_ID_HERE"
```

**Response includes:**
- Full email headers (From, To, Cc, Bcc, Subject, Date)
- Email body (plain text)
- Message ID and thread ID
- Labels
- Snippet

#### Create Draft Email

**Create a draft:**
```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" draft \
  --user user@example.com \
  --to "recipient@example.com" \
  --subject "Email Subject" \
  --body "Email body text here"
```

**Create draft with multiple recipients:**
```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" draft \
  --user user@example.com \
  --to "recipient1@example.com,recipient2@example.com" \
  --subject "Email Subject" \
  --body "Email body text here"
```

**Note:** Drafts are created but not sent. The user can review and send them from Gmail. Replace `user@example.com` with your actual Google Workspace email address.

### Error Handling

**Common errors:**

1. **Service account key file not found:**
   ```
   FileNotFoundError: Service account key file not found: /path/to/user/gmail-service-account-key.json
   ```
   **Solution:** Ensure the JSON key file is located at `user/gmail-service-account-key.json`

2. **Domain-wide delegation not configured:**
   ```
   Gmail API error: 403 - Access denied
   ```
   **Solution:** Verify domain-wide delegation is configured in Google Workspace Admin Console with correct Client ID and scopes

3. **Invalid user email:**
   ```
   Gmail API error: 403 - User not found
   ```
   **Solution:** Ensure the email address exists in your Google Workspace domain

4. **API not enabled:**
   ```
   Gmail API error: 403 - Gmail API has not been used
   ```
   **Solution:** Enable Gmail API in Google Cloud Console

### Troubleshooting

**Authentication issues:**
- Verify service account JSON key file exists and is readable
- Check that domain-wide delegation is configured with correct Client ID
- Ensure scopes are correct: `https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.compose`
- Domain-wide delegation changes can take up to 24 hours (usually minutes)

**API errors:**
- Check that Gmail API is enabled in Google Cloud Console
- Verify service account has correct permissions
- Ensure user email is in the same Google Workspace domain

**Message not found:**
- Verify message ID is correct (get from list command)
- Check that the message exists in the specified user's mailbox

### Best Practices

1. **Use search queries:** Filter messages with Gmail search syntax to reduce results
2. **Limit results:** Use `--max-results` to control response size
3. **Cache message IDs:** Store message IDs when listing to avoid re-querying
4. **Error handling:** Check for HTTP errors and handle rate limits (429)
5. **Account selection:** Always specify `--user` parameter with correct email address

### Rate Limits

Gmail API has rate limits. If you receive 429 errors, wait before retrying. The API typically allows:
- 1,000,000 quota units per day
- Most operations consume 5 quota units
- Rate limits reset daily

### Scopes

Required scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.compose` - Create drafts

**Note:** These scopes allow reading emails and creating drafts. Sending emails requires additional scope (not implemented).

### Note

For detailed Gmail API documentation, use web search (see `skills/web-search.md`) to find Gmail API docs or visit https://developers.google.com/gmail/api

