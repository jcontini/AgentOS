# iMessages Skill

## Intention: Read iMessages/SMS messages from macOS Messages app

**Required Skills:**
- [Contacts](skills/contacts/README.md) - For resolving phone numbers to contact names

**✅ PRIMARY METHOD: SQLite Direct Access** (fast, milliseconds)

Similar to the Calendar skill, we query the Messages SQLite database directly for maximum speed.

## Quick Reference

**Get recent messages:**
```bash
sqlite3 ~/Library/Messages/chat.db << 'SQL'
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    SUBSTR(m.text, 1, 200) as text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC
LIMIT 20;
SQL
```

**Search messages by contact (phone number or email):**
```bash
sqlite3 ~/Library/Messages/chat.db << 'SQL'
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE h.id LIKE '%5551234567%'  -- partial phone number match
ORDER BY m.date DESC
LIMIT 20;
SQL
```

**Get messages from today:**
```bash
sqlite3 ~/Library/Messages/chat.db << 'SQL'
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.date/1000000000 + 978307200 >= CAST(strftime('%s', 'now', 'start of day', 'localtime') AS INTEGER)
  AND m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC;
SQL
```

---

## Database Location

**Full path:** `~/Library/Messages/chat.db`

**Important:** Database is read-only for queries. Messages.app manages writes.

## Date Format: Nanoseconds Since macOS Epoch

**Critical:** Message dates are stored as **nanoseconds** since **macOS epoch (2001-01-01 00:00:00 UTC)**.

**Conversion pattern:**
```sql
-- Convert to readable date
datetime(date/1000000000 + 978307200, 'unixepoch', 'localtime')

-- Convert readable date to query format (for filtering)
(strftime('%s', '2025-01-01') - 978307200) * 1000000000
```

**⚠️ IMPORTANT:** When using `strftime()` in WHERE clauses for date comparisons, you MUST use `CAST(strftime(...) AS INTEGER)`. SQLite's `strftime()` returns TEXT, causing integer comparisons to fail silently.

```sql
-- ✅ CORRECT: CAST to INTEGER
WHERE m.date/1000000000 + 978307200 >= CAST(strftime('%s', 'now', '-3 days') AS INTEGER)

-- ❌ WRONG: Returns empty results (TEXT vs INTEGER comparison)
WHERE m.date/1000000000 + 978307200 >= strftime('%s', 'now', '-3 days')
```

## Schema: Key Tables

### message (Main messages table)
- `ROWID` - Primary key
- `guid` - Unique message identifier
- `text` - Message content (may be NULL for attachments/reactions)
- `date` - Send/receive time (nanoseconds, macOS epoch)
- `date_read` - When message was read
- `date_delivered` - When message was delivered
- `is_from_me` - 1 if sent by user, 0 if received
- `is_read` - 1 if read
- `handle_id` - Foreign key to handle table (sender/recipient)
- `cache_has_attachments` - 1 if has attachments
- `associated_message_type` - Reaction type (2000=loved, 2001=liked, 2002=disliked, etc.)
- `thread_originator_guid` - For threaded replies

### handle (Contacts/phone numbers)
- `ROWID` - Primary key
- `id` - Phone number (E.164 format: +1XXXXXXXXXX) or email
- `service` - "iMessage", "SMS", or "RCS"
- `person_centric_id` - Links to Contacts

### chat (Conversations)
- `ROWID` - Primary key
- `guid` - Unique chat identifier
- `chat_identifier` - Phone number or email for 1:1, group ID for groups
- `display_name` - Group chat name (if set)
- `service_name` - "iMessage", "SMS", or "RCS"

### chat_message_join (Links chats to messages)
- `chat_id` - Foreign key to chat
- `message_id` - Foreign key to message

### chat_handle_join (Links chats to participants)
- `chat_id` - Foreign key to chat
- `handle_id` - Foreign key to handle

### attachment (Media attachments)
- `ROWID` - Primary key
- `guid` - Unique attachment identifier
- `filename` - Full path to attachment file
- `mime_type` - MIME type (image/jpeg, video/mp4, etc.)
- `total_bytes` - File size

## Common Queries

### Recent Messages (with conversation context)
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    c.display_name as group_name,
    c.chat_identifier,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
LEFT JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
LEFT JOIN chat c ON cmj.chat_id = c.ROWID
WHERE m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC
LIMIT 20;
```

### Messages from Specific Contact
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE 'Them' END as sender,
    m.text
FROM message m
JOIN handle h ON m.handle_id = h.ROWID
WHERE h.id LIKE '%5125551234%'  -- Use partial phone number
ORDER BY m.date DESC
LIMIT 30;
```

### Unread Messages
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    h.id as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.is_read = 0 
  AND m.is_from_me = 0
  AND m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC;
```

### Messages from Today
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.date/1000000000 + 978307200 >= CAST(strftime('%s', 'now', 'start of day', 'localtime') AS INTEGER)
  AND m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC;
```

### Messages from Last N Days
```sql
-- Last 7 days (CAST required: strftime returns TEXT, not INTEGER)
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.date/1000000000 + 978307200 >= CAST(strftime('%s', 'now', '-7 days') AS INTEGER)
  AND m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC;
```

### Search Messages by Text Content
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.text LIKE '%search term%'
ORDER BY m.date DESC
LIMIT 20;
```

### Group Chat Messages
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    c.display_name as group_name,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
LEFT JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
LEFT JOIN chat c ON cmj.chat_id = c.ROWID
WHERE c.display_name IS NOT NULL  -- Only group chats with names
  AND m.text IS NOT NULL AND m.text != ''
ORDER BY m.date DESC
LIMIT 30;
```

### List All Conversations (Most Recent First)
```sql
SELECT 
    c.ROWID,
    c.display_name,
    c.chat_identifier,
    c.service_name,
    (SELECT datetime(MAX(m.date)/1000000000 + 978307200, 'unixepoch', 'localtime') 
     FROM message m 
     JOIN chat_message_join cmj ON m.ROWID = cmj.message_id 
     WHERE cmj.chat_id = c.ROWID) as last_message_date
FROM chat c
ORDER BY last_message_date DESC
LIMIT 20;
```

### Messages with Attachments
```sql
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.is_from_me WHEN 1 THEN 'Me' ELSE h.id END as sender,
    a.filename,
    a.mime_type,
    m.text
FROM message m
LEFT JOIN handle h ON m.handle_id = h.ROWID
JOIN message_attachment_join maj ON m.ROWID = maj.message_id
JOIN attachment a ON maj.attachment_id = a.ROWID
ORDER BY m.date DESC
LIMIT 20;
```

## Reactions/Tapbacks

Reactions are stored as separate messages with `associated_message_type`:
- 2000 = Loved (❤️)
- 2001 = Liked (👍)
- 2002 = Disliked (👎)
- 2003 = Laughed (😂)
- 2004 = Emphasized (‼️)
- 2005 = Questioned (❓)
- 3000-3005 = Removed reaction

```sql
-- Get reactions to messages
SELECT 
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    m.associated_message_type,
    CASE m.associated_message_type
        WHEN 2000 THEN 'Loved'
        WHEN 2001 THEN 'Liked'
        WHEN 2002 THEN 'Disliked'
        WHEN 2003 THEN 'Laughed'
        WHEN 2004 THEN 'Emphasized'
        WHEN 2005 THEN 'Questioned'
    END as reaction,
    m.associated_message_guid
FROM message m
WHERE m.associated_message_type BETWEEN 2000 AND 2005
ORDER BY m.date DESC
LIMIT 10;
```

## Performance Notes

- SQLite queries run in ~5ms (extremely fast)
- The database can be large (100MB+) but queries are indexed
- Use `LIMIT` to control result size
- Filter by date for recent messages to improve performance

## Permissions

**Full Disk Access** may be required for terminal apps to read the Messages database:
- System Settings → Privacy & Security → Full Disk Access
- Add Terminal.app or your terminal emulator

## Notes

- Phone numbers are stored in E.164 format: `+1XXXXXXXXXX`
- Email addresses are used for iMessage-only contacts
- Group chats may have phone number as identifier if no display_name is set
- Empty `text` field often indicates attachments, reactions, or system messages
- Use `skills/contacts/README.md` to resolve phone numbers to contact names

