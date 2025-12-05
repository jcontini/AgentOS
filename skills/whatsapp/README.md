# WhatsApp Skill

## Intention: Read WhatsApp messages from macOS WhatsApp app

**Required Skills:**
- [Contacts](skills/apple-contacts/README.md) - For resolving phone numbers to contact names

**✅ PRIMARY METHOD: SQLite Direct Access** (fast, milliseconds)

Similar to the iMessages skill, we query the WhatsApp SQLite database directly for maximum speed.

## Quick Reference

**Get recent messages:**
```bash
sqlite3 ~/Library/Group\ Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite << 'SQL'
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    SUBSTR(m.ZTEXT, 1, 200) as text
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 20;
SQL
```

**Search messages by contact (JID or phone number):**
```bash
sqlite3 ~/Library/Group\ Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite << 'SQL'
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZFROMJID LIKE '%13129182275%'  -- partial JID match
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 20;
SQL
```

**Get messages from today:**
```bash
sqlite3 ~/Library/Group\ Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite << 'SQL'
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZMESSAGEDATE + 978307200 >= CAST(strftime('%s', 'now', 'start of day', 'localtime') AS INTEGER)
  AND m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC;
SQL
```

---

## Database Location

**Full path:** `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite`

**Important:** Database is read-only for queries. WhatsApp.app manages writes.

## Date Format: Seconds Since macOS Epoch

**Critical:** Message dates are stored as **seconds** since **macOS epoch (2001-01-01 00:00:00 UTC)**.

**Conversion pattern:**
```sql
-- Convert to readable date
datetime(ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime')

-- Convert readable date to query format (for filtering)
CAST(strftime('%s', '2025-01-01') AS INTEGER) - 978307200
```

**⚠️ IMPORTANT:** When using `strftime()` in WHERE clauses for date comparisons, you MUST use `CAST(strftime(...) AS INTEGER)`. SQLite's `strftime()` returns TEXT, causing integer comparisons to fail silently.

```sql
-- ✅ CORRECT: CAST to INTEGER
WHERE m.ZMESSAGEDATE + 978307200 >= CAST(strftime('%s', 'now', '-3 days') AS INTEGER)

-- ❌ WRONG: Returns empty results (TEXT vs INTEGER comparison)
WHERE m.ZMESSAGEDATE + 978307200 >= strftime('%s', 'now', '-3 days')
```

## Schema: Key Tables

### ZWAMESSAGE (Main messages table)
- `Z_PK` - Primary key
- `ZSTANZAID` - Unique message identifier
- `ZTEXT` - Message content (may be NULL for attachments/media)
- `ZMESSAGEDATE` - Send/receive time (seconds, macOS epoch)
- `ZSENTDATE` - When message was sent
- `ZISFROMME` - 1 if sent by user, 0 if received
- `ZMESSAGESTATUS` - Message status (0=sent, 1=delivered, 2=read, etc.)
- `ZMESSAGETYPE` - Message type (0=text, 1=image, 2=audio, 3=video, etc.)
- `ZCHATSESSION` - Foreign key to ZWACHATSESSION table
- `ZFROMJID` - Sender JID (format: `PHONENUMBER@s.whatsapp.net`)
- `ZTOJID` - Recipient JID
- `ZPUSHNAME` - Display name of sender
- `ZSTARRED` - 1 if starred/favorited
- `ZMEDIAITEM` - Foreign key to ZWAMEDIAITEM table

### ZWACHATSESSION (Conversations)
- `Z_PK` - Primary key
- `ZCONTACTJID` - Contact JID (format: `PHONENUMBER@s.whatsapp.net`)
- `ZPARTNERNAME` - Display name of contact/group
- `ZLASTMESSAGEDATE` - Date of last message
- `ZLASTMESSAGETEXT` - Preview of last message
- `ZUNREADCOUNT` - Number of unread messages
- `ZARCHIVED` - 1 if archived
- `ZHIDDEN` - 1 if hidden
- `ZSESSIONTYPE` - Session type (0=individual, 1=group)
- `ZGROUPINFO` - Foreign key to ZWAGROUPINFO for group chats

### ZWAGROUPINFO (Group chat information)
- `Z_PK` - Primary key
- `ZCHATSESSION` - Foreign key to ZWACHATSESSION
- `ZSUBJECTOWNERJID` - JID of person who set group subject
- `ZCREATORJID` - JID of group creator
- `ZOWNERJID` - JID of group owner
- `ZCREATIONDATE` - When group was created
- `ZSUBJECTTIMESTAMP` - When subject was last changed

### ZWAGROUPMEMBER (Group members)
- `Z_PK` - Primary key
- `ZCHATSESSION` - Foreign key to ZWACHATSESSION
- `ZMEMBERJID` - JID of group member
- `ZCONTACTNAME` - Display name of member
- `ZFIRSTNAME` - First name of member
- `ZISADMIN` - 1 if admin
- `ZISACTIVE` - 1 if active member

### ZWAMEDIAITEM (Media attachments)
- `Z_PK` - Primary key
- `ZMESSAGE` - Foreign key to ZWAMESSAGE
- `ZMEDIALOCALPATH` - Local file path
- `ZMEDIAURL` - Remote URL (if applicable)
- `ZFILESIZE` - File size in bytes
- `ZMOVIEDURATION` - Duration for video/audio
- `ZLATITUDE` / `ZLONGITUDE` - Location coordinates
- `ZMEDIAORIGIN` - Origin type
- `ZCLOUDSTATUS` - Cloud sync status

## Common Queries

### Recent Messages (with contact name)
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 20;
```

### Messages from Specific Contact
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE 'Them' END as sender,
    m.ZTEXT
FROM ZWAMESSAGE m
JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE cs.ZCONTACTJID LIKE '%13129182275%'  -- Use partial JID
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 30;
```

### Unread Messages
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    cs.ZPARTNERNAME as contact_name,
    m.ZFROMJID as sender,
    m.ZTEXT
FROM ZWAMESSAGE m
JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE cs.ZUNREADCOUNT > 0
  AND m.ZISFROMME = 0
  AND m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC;
```

### Messages from Today
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZMESSAGEDATE + 978307200 >= CAST(strftime('%s', 'now', 'start of day', 'localtime') AS INTEGER)
  AND m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC;
```

### Messages from Last N Days
```sql
-- Last 7 days (CAST required: strftime returns TEXT, not INTEGER)
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZMESSAGEDATE + 978307200 >= CAST(strftime('%s', 'now', '-7 days') AS INTEGER)
  AND m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC;
```

### Search Messages by Text Content
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZTEXT LIKE '%search term%'
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 20;
```

### Group Chat Messages
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as group_name,
    m.ZPUSHNAME as sender_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
LEFT JOIN ZWAGROUPINFO gi ON cs.ZGROUPINFO = gi.Z_PK
WHERE gi.Z_PK IS NOT NULL  -- Only group chats
  AND m.ZTEXT IS NOT NULL AND m.ZTEXT != ''
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 30;
```

### List All Conversations (Most Recent First)
```sql
SELECT 
    cs.Z_PK,
    cs.ZPARTNERNAME as contact_name,
    cs.ZCONTACTJID,
    cs.ZSESSIONTYPE,
    datetime(cs.ZLASTMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as last_message_date,
    cs.ZLASTMESSAGETEXT,
    cs.ZUNREADCOUNT
FROM ZWACHATSESSION cs
WHERE cs.ZREMOVED = 0
ORDER BY cs.ZLASTMESSAGEDATE DESC
LIMIT 20;
```

### Messages with Media/Attachments
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    mi.ZMEDIALOCALPATH,
    mi.ZFILESIZE,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
JOIN ZWAMEDIAITEM mi ON m.ZMEDIAITEM = mi.Z_PK
ORDER BY m.ZMESSAGEDATE DESC
LIMIT 20;
```

### Starred Messages
```sql
SELECT 
    datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') as date,
    CASE m.ZISFROMME WHEN 1 THEN 'Me' ELSE m.ZFROMJID END as sender,
    cs.ZPARTNERNAME as contact_name,
    m.ZTEXT
FROM ZWAMESSAGE m
LEFT JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
WHERE m.ZSTARRED = 1
ORDER BY m.ZMESSAGEDATE DESC;
```

## Message Types

Common `ZMESSAGETYPE` values:
- 0 = Text message
- 1 = Image
- 2 = Audio
- 3 = Video
- 4 = Contact (vCard)
- 5 = Location
- 6 = Document
- 7 = URL/Link preview
- 8 = GIF
- 9 = Sticker
- 10 = Live location
- 11 = Voice note
- 12 = System message

## Message Status

Common `ZMESSAGESTATUS` values:
- 0 = Sent
- 1 = Delivered
- 2 = Read
- 3 = Failed
- 4 = Pending

## Performance Notes

- SQLite queries run in ~5ms (extremely fast)
- The database can be large but queries are indexed
- Use `LIMIT` to control result size
- Filter by date for recent messages to improve performance
- JID format: `PHONENUMBER@s.whatsapp.net` (e.g., `13129182275@s.whatsapp.net`)

## Permissions

**Full Disk Access** may be required for terminal apps to read the WhatsApp database:
- System Settings → Privacy & Security → Full Disk Access
- Add Terminal.app or your terminal emulator

## Notes

- JIDs are stored in format: `PHONENUMBER@s.whatsapp.net`
- Phone numbers in JIDs are typically without country code prefix (e.g., `13129182275` not `+13129182275`)
- Group chats have `ZSESSIONTYPE = 1`
- Individual chats have `ZSESSIONTYPE = 0`
- Empty `ZTEXT` field often indicates attachments, media, or system messages
- Use `skills/apple-contacts/README.md` to resolve phone numbers to contact names
- WhatsApp uses seconds (not nanoseconds) since macOS epoch, unlike iMessage

