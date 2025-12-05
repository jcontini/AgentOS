# Gmail

> Read emails, search messages, create drafts via Gmail API

## Skills Provided

- **email** (connection) — Read, search, draft emails

## Auth

Uses service account authentication with domain-wide delegation.

**Required files:**
- `user/skills-data/google-workspace/service-account-key.json`

**Required scopes (configured in Google Admin Console):**
```
https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.compose
```

### Setup

See the full setup guide for Google Workspace service account configuration:

1. **Google Cloud Console:** Create project, enable Gmail API, create service account, download JSON key
2. **Google Admin Console:** Configure domain-wide delegation with Client ID and scopes
3. **Local:** Place JSON key at `user/skills-data/google-workspace/service-account-key.json`

### Dependencies

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## Usage

Use the Python script: `skills/gmail/gmail.py`

**⚠️ IMPORTANT:** The `--user` flag MUST come BEFORE the subcommand.

### List Messages

```bash
# List recent emails (default 10)
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com list

# List with search query
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com list --query "from:sender@domain.com"

# List unread emails
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com list --query "is:unread"

# List more results
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com list --max-results 50
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
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com get --message-id "MESSAGE_ID"
```

### Create Draft Email

```bash
python3 "$PROJECT_ROOT/skills/gmail/gmail.py" --user user@example.com draft \
  --to "recipient@example.com" \
  --subject "Email Subject" \
  --body "Email body text here"
```

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
   **Solution:** Enable Gmail API in Google Cloud Console

4. **Invalid user email (403 User not found):**
   ```
   API error: 403 - User not found
   ```
   **Solution:** Ensure email address exists in your Google Workspace domain

---

## Rate Limits

- Gmail: ~1,000,000 quota units/day
- If you receive 429 errors, wait before retrying
