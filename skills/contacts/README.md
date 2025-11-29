# Contacts Skill

## Intention: Read, search, add, and edit contacts from macOS Contacts app

**Methods:**
- **Reading:** Swift script (uses AppleScript for notes/social profiles due to framework bugs)
- **Writing:** Swift script with Contacts framework + AppleScript for notes/social profiles (syncs with iCloud)

## Note Format Convention

When adding notes to contacts, use this format:
```
YYYY-MM-DD Met @ [place] via [person/context].

[Social media URLs on separate lines]
```

**Example:**
```
2025-11-28 Met @ Friendsgiving via friends.

Instagram: https://www.instagram.com/username
LinkedIn: https://linkedin.com/in/username
```

## Quick Reference

### Reading (SQLite - Fast)

**Search contacts by name:**
```bash
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "SELECT r.ZFIRSTNAME, r.ZLASTNAME, r.ZORGANIZATION, p.ZFULLNUMBER, e.ZADDRESS FROM ZABCDRECORD r LEFT JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK LEFT JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK WHERE r.ZFIRSTNAME LIKE '%John%' OR r.ZLASTNAME LIKE '%Smith%' LIMIT 20;" 2>/dev/null
done
```

**Find contact by phone number (last 4 digits):**
```bash
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "SELECT r.ZFIRSTNAME, r.ZLASTNAME, r.ZORGANIZATION, p.ZFULLNUMBER FROM ZABCDRECORD r JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK WHERE p.ZLASTFOURDIGITS = '1234' LIMIT 10;" 2>/dev/null
done
```

### Writing (Swift Script)

**Add a new contact:**
```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" add \
  --first "John" --last "Doe" \
  --phone "+15125551234" --phone-label "mobile" \
  --email "john@example.com" --email-label "work" \
  --organization "Acme Corp" --job-title "Engineer"
```

**Update an existing contact:**
```bash
# First search to get the contact ID
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" search --name "John Doe"

# Then update using the ID
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --job-title "Senior Engineer" \
  --department "Engineering"

# Update with a note (use the standard format)
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --note "2025-11-28 Met @ conference via mutual friend."
```

**Add social profiles:**
```bash
# Add Instagram profile
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --social "instagram:username"

# Add LinkedIn profile  
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --social "linkedin:johndoe"

# Add when creating a new contact
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" add \
  --first "Jane" --last "Smith" \
  --social "instagram:janesmith"
```

**Remove social profiles:**
```bash
# Remove a corrupted or unwanted social profile by service name
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --remove-social "INSTAGRAM"

# Works with any case (instagram, INSTAGRAM, Instagram all match)
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update \
  --id "CONTACT_ID_HERE" \
  --remove-social "linkedin"
```

**Search contacts (returns JSON):**
```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" search --name "John"
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" search --phone "5551234"
```

---

## Database Location

**Important:** Contacts are stored in source-specific databases:
```
~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb
```

Multiple source databases may exist (iCloud, Google, local, etc.). Use a bash loop to query all sources.

**Note:** The main database at `~/Library/Application Support/AddressBook/AddressBook-v22.abcddb` is typically empty - use the Sources subdirectories.

**Query pattern (bash loop):**
```bash
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "YOUR_SQL_QUERY" 2>/dev/null
done
```

## Schema: Key Tables

### ZABCDRECORD (Main contacts table)
- `Z_PK` - Primary key
- `ZFIRSTNAME` - First name
- `ZLASTNAME` - Last name
- `ZMIDDLENAME` - Middle name
- `ZNICKNAME` - Nickname
- `ZORGANIZATION` - Company/organization
- `ZJOBTITLE` - Job title
- `ZDEPARTMENT` - Department
- `ZNOTE` - Notes (foreign key to ZABCDNOTE)
- `ZBIRTHDAY` - Birthday timestamp
- `ZUNIQUEID` - Unique identifier

### ZABCDPHONENUMBER (Phone numbers)
- `Z_PK` - Primary key
- `ZOWNER` - Foreign key to ZABCDRECORD.Z_PK
- `ZFULLNUMBER` - Full phone number (various formats)
- `ZLASTFOURDIGITS` - Last 4 digits (indexed for fast lookup)
- `ZLABEL` - Label (Mobile, Home, Work, etc.)
- `ZCOUNTRYCODE` - Country code
- `ZAREACODE` - Area code

### ZABCDEMAILADDRESS (Email addresses)
- `Z_PK` - Primary key
- `ZOWNER` - Foreign key to ZABCDRECORD.Z_PK
- `ZADDRESS` - Email address
- `ZLABEL` - Label (Home, Work, etc.)

### ZABCDPOSTALADDRESS (Physical addresses)
- `Z_PK` - Primary key
- `ZOWNER` - Foreign key to ZABCDRECORD.Z_PK
- `ZSTREET` - Street address
- `ZCITY` - City
- `ZSTATE` - State/province
- `ZZIPCODE` - Postal/ZIP code
- `ZCOUNTRY` - Country
- `ZLABEL` - Label (Home, Work, etc.)

### ZABCDNOTE (Notes)
- `Z_PK` - Primary key
- `ZTEXT` - Note text content

## Common Queries

### Search Contacts by Name
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZORGANIZATION as organization,
    r.ZJOBTITLE as job_title,
    p.ZFULLNUMBER as phone,
    p.ZLABEL as phone_label,
    e.ZADDRESS as email,
    e.ZLABEL as email_label
FROM ZABCDRECORD r
LEFT JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
LEFT JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK
WHERE r.ZFIRSTNAME LIKE '%search%' 
   OR r.ZLASTNAME LIKE '%search%'
   OR r.ZORGANIZATION LIKE '%search%'
LIMIT 20;
```

### Find Contact by Phone Number
```sql
-- Use last 4 digits for fast indexed lookup, then verify full number
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZORGANIZATION as organization,
    p.ZFULLNUMBER as phone
FROM ZABCDRECORD r
JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
WHERE p.ZLASTFOURDIGITS = '1234'  -- Last 4 digits of phone number
LIMIT 10;

-- Or search by partial number (slower but more flexible)
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    p.ZFULLNUMBER as phone
FROM ZABCDRECORD r
JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
WHERE REPLACE(REPLACE(REPLACE(p.ZFULLNUMBER, ' ', ''), '-', ''), '(', '') LIKE '%5125551234%'
LIMIT 10;
```

### Find Contact by Email
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZORGANIZATION as organization,
    e.ZADDRESS as email
FROM ZABCDRECORD r
JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK
WHERE e.ZADDRESS LIKE '%@example.com%'
LIMIT 10;
```

### Get All Info for a Contact
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZMIDDLENAME as middle_name,
    r.ZNICKNAME as nickname,
    r.ZORGANIZATION as organization,
    r.ZJOBTITLE as job_title,
    r.ZDEPARTMENT as department,
    datetime(r.ZBIRTHDAY + 978307200, 'unixepoch', 'localtime') as birthday,
    p.ZFULLNUMBER as phone,
    p.ZLABEL as phone_label,
    e.ZADDRESS as email,
    e.ZLABEL as email_label,
    a.ZSTREET as street,
    a.ZCITY as city,
    a.ZSTATE as state,
    a.ZZIPCODE as zip,
    a.ZCOUNTRY as country
FROM ZABCDRECORD r
LEFT JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
LEFT JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK
LEFT JOIN ZABCDPOSTALADDRESS a ON a.ZOWNER = r.Z_PK
WHERE r.ZFIRSTNAME = 'John' AND r.ZLASTNAME = 'Smith';
```

### List All Contacts (Basic Info)
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZORGANIZATION as organization
FROM ZABCDRECORD r
WHERE r.ZFIRSTNAME IS NOT NULL OR r.ZLASTNAME IS NOT NULL OR r.ZORGANIZATION IS NOT NULL
ORDER BY r.ZSORTINGLASTNAME, r.ZSORTINGFIRSTNAME
LIMIT 100;
```

### Search by Organization/Company
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    r.ZORGANIZATION as organization,
    r.ZJOBTITLE as job_title,
    p.ZFULLNUMBER as phone,
    e.ZADDRESS as email
FROM ZABCDRECORD r
LEFT JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
LEFT JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK
WHERE r.ZORGANIZATION LIKE '%Company Name%'
LIMIT 20;
```

### Get Contacts with Notes
```sql
SELECT 
    r.ZFIRSTNAME as first_name,
    r.ZLASTNAME as last_name,
    n.ZTEXT as note
FROM ZABCDRECORD r
JOIN ZABCDNOTE n ON r.ZNOTE = n.Z_PK
WHERE n.ZTEXT IS NOT NULL AND n.ZTEXT != ''
LIMIT 20;
```

## Resolving Phone Numbers from iMessages

Use this to map iMessage phone numbers to contact names:

```bash
# Replace '1234' with the last 4 digits of the phone number from iMessages
# Phone numbers in iMessages are E.164 format: +1XXXXXXXXXX
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "SELECT r.ZFIRSTNAME, r.ZLASTNAME, r.ZORGANIZATION, p.ZFULLNUMBER FROM ZABCDRECORD r JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK WHERE p.ZLASTFOURDIGITS = '1234' LIMIT 5;" 2>/dev/null
done

# To resolve multiple phone numbers at once:
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "SELECT r.ZFIRSTNAME, r.ZLASTNAME, p.ZFULLNUMBER FROM ZABCDRECORD r JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK WHERE p.ZLASTFOURDIGITS IN ('1234', '5678', '9012') LIMIT 20;" 2>/dev/null
done
```

## Performance Notes

- SQLite queries run in ~5-10ms per database
- Use `ZLASTFOURDIGITS` for fast phone lookups (indexed)
- The bash loop queries all contact sources sequentially
- Use `LIMIT` to control result size
- Combine multiple lookups in a single query with `IN ('val1', 'val2', ...)`

## Permissions

**Full Disk Access** may be required for terminal apps to read the Contacts database:
- System Settings → Privacy & Security → Full Disk Access
- Add Terminal.app or your terminal emulator

## Date Format

Birthday and other dates use macOS epoch (2001-01-01):
```sql
datetime(ZBIRTHDAY + 978307200, 'unixepoch', 'localtime')
```

## Writing Contacts (Swift Script)

The Swift script `contacts.swift` uses the native Contacts framework to add and update contacts. Changes sync automatically with iCloud and other configured contact sources.

### Add Contact

```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" add [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--first <name>` | First name |
| `--last <name>` | Last name |
| `--middle <name>` | Middle name |
| `--nickname <name>` | Nickname |
| `--organization <name>` | Company/organization |
| `--job-title <title>` | Job title |
| `--department <name>` | Department |
| `--phone <number>` | Phone number |
| `--phone-label <label>` | Phone label (mobile, home, work, main, iphone) |
| `--email <address>` | Email address |
| `--email-label <label>` | Email label (home, work, icloud) |
| `--note <text>` | Notes |
| `--social <svc:user>` | Social profile (e.g., `instagram:username`, `linkedin:johndoe`) |

**Minimum required:** At least one of `--first`, `--last`, or `--organization`

### Update Contact

```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update --id "CONTACT_ID" [options]
```

Uses the same options as `add`. The contact ID can be obtained from the `search` command.

**Additional options:**
| Option | Description |
|--------|-------------|
| `--replace-phones` | Replace all phone numbers (default: append) |
| `--replace-emails` | Replace all email addresses (default: append) |
| `--append-note` | Append to existing note instead of replacing |
| `--remove-social <svc>` | Remove social profile by service name (e.g., `INSTAGRAM`) |

### Search Contact

```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" search --name "query"
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" search --phone "5551234"
```

Returns JSON with contact details including the `id` field needed for updates.

## Technical Notes

- Multiple contact sources may exist (iCloud, Google, Exchange, local)
- Each source has its own database in `Sources/UUID/`
- Phone numbers are stored in various formats - normalize when comparing
- The `ZLASTFOURDIGITS` field provides fast indexed phone lookups
- Write operations via Swift automatically sync with iCloud

### Notes Field Workaround

The macOS Contacts framework has a bug where `mutableCopy()` doesn't preserve `CNContactNoteKey`, causing `CNPropertyNotFetchedException` when trying to set notes. 

**Solution:** The Swift script uses AppleScript (`osascript`) under the hood for all note operations:
- Reading notes: AppleScript queries the Contacts app directly
- Writing notes: AppleScript sets the note via the Contacts app

This is transparent to users - just use `--note` flag as normal.

### Social Profiles

The macOS Contacts framework has the same `mutableCopy()` bug for social profiles.

**Solution:** The Swift script uses AppleScript for social profile operations:
- Reading: Returns `socialProfiles` array in search results
- Writing: Use `--social service:username` format

**Supported services:** Instagram, LinkedIn, Twitter, Facebook, TikTok, YouTube, Snapchat, Pinterest, Reddit, WhatsApp, Telegram, Signal, Discord, Slack, GitHub, Mastodon, Bluesky, Threads (and any custom service).

**Important:** Service names are automatically normalized to proper case (e.g., `instagram` → `Instagram`). Using ALL CAPS service names directly in macOS Contacts displays garbage (raw vCard metadata).

**Removal workaround:** AppleScript doesn't support `delete` for social profiles, but we can nullify them by clearing `service name`, `user name`, and `url`. Use `--remove-social` flag:
```bash
swift "$PROJECT_ROOT/skills/contacts/contacts.swift" update --id "ID" --remove-social "INSTAGRAM"
```

This matches case-insensitively (`instagram`, `INSTAGRAM`, `Instagram` all work). The ghost entry remains in the database but is invisible/empty.

