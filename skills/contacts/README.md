# Contacts Skill

## Intention: Read and search contacts from macOS Contacts app

**✅ PRIMARY METHOD: SQLite Direct Access** (fast, milliseconds)

Query the Contacts SQLite database directly for maximum speed.

## Quick Reference

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

## Notes

- Multiple contact sources may exist (iCloud, Google, Exchange, local)
- Each source has its own database in `Sources/UUID/`
- Use wildcard `*` to query all sources simultaneously
- Phone numbers are stored in various formats - normalize when comparing
- The `ZLASTFOURDIGITS` field provides fast indexed phone lookups

