# Contacts Skill

CRUD interface for macOS Contacts.app.

**Implementation:** Python script using SQLite for reads (fast) and AppleScript for writes (reliable, syncs with iCloud).

## Quick Reference

```bash
# Search
python3 contacts.py search "John Smith"
python3 contacts.py search --phone 5551234

# Get full details
python3 contacts.py get <contact-id>

# Create
python3 contacts.py create --first "John" --last "Doe" --phone "+15125551234"

# Update
python3 contacts.py update <id> --org "Acme Corp" --job-title "Engineer"

# Phone operations
python3 contacts.py phone add <id> +15125551234 mobile
python3 contacts.py phone remove <id> +15125551234

# Email operations
python3 contacts.py email add <id> john@example.com work
python3 contacts.py email remove <id> john@example.com

# Social profile operations
python3 contacts.py social add <id> instagram johndoe
python3 contacts.py social remove <id> instagram

# Fix corrupted social profiles
python3 contacts.py fix <id>
```

## Commands

### search

Search contacts by name or phone number.

```bash
python3 contacts.py search "John"
python3 contacts.py search "Acme Corp"
python3 contacts.py search --phone 5551234
```

Returns JSON:
```json
{
  "count": 2,
  "contacts": [
    {"id": "ABC123", "firstName": "John", "lastName": "Doe", "organization": "Acme Corp"},
    {"id": "DEF456", "firstName": "Johnny", "lastName": "Smith", "organization": null}
  ]
}
```

### get

Get full contact details by ID.

```bash
python3 contacts.py get ABC123-DEF456-GHI789
```

Returns JSON with all fields including phones, emails, note, and social profiles.

### create

Create a new contact. Requires at least `--first`, `--last`, or `--org`.

```bash
python3 contacts.py create \
  --first "John" \
  --last "Doe" \
  --org "Acme Corp" \
  --job-title "Engineer" \
  --phone "+15125551234" \
  --phone-label mobile \
  --email "john@example.com" \
  --email-label work \
  --social "instagram:johndoe" \
  --note "Met at conference 2025"
```

Options:
| Flag | Description |
|------|-------------|
| `--first` | First name |
| `--last` | Last name |
| `--middle` | Middle name |
| `--nickname` | Nickname |
| `--org` | Organization/company |
| `--job-title` | Job title |
| `--department` | Department |
| `--note` | Note text |
| `--phone` | Phone number |
| `--phone-label` | Phone label (mobile, home, work) |
| `--email` | Email address |
| `--email-label` | Email label (home, work) |
| `--social` | Social profile as `service:username` |

### update

Update contact fields. Use resource subcommands (`phone`, `email`, `social`) for multi-value fields.

```bash
python3 contacts.py update ABC123 --org "New Company" --job-title "Senior Engineer"
```

### phone

Add or remove phone numbers.

```bash
# Add phone (label is optional, defaults to "mobile")
python3 contacts.py phone add <id> +15125551234
python3 contacts.py phone add <id> +15125551234 work

# Remove phone
python3 contacts.py phone remove <id> +15125551234
```

### email

Add or remove email addresses.

```bash
# Add email (label is optional, defaults to "home")
python3 contacts.py email add <id> john@example.com
python3 contacts.py email add <id> john@work.com work

# Remove email
python3 contacts.py email remove <id> john@example.com
```

### social

Add or remove social profiles. Service names are automatically normalized (instagram → Instagram).

```bash
# Add/update social profile
python3 contacts.py social add <id> instagram johndoe
python3 contacts.py social add <id> linkedin john-doe
python3 contacts.py social add <id> twitter johnd

# Remove social profile
python3 contacts.py social remove <id> instagram
```

Supported services: Instagram, LinkedIn, Twitter/X, Facebook, TikTok, YouTube, Snapchat, Pinterest, Reddit, WhatsApp, Telegram, Signal, Discord, Slack, GitHub, Mastodon, Bluesky, Threads.

### fix

Fix corrupted social profiles for a contact (extracts usernames from URLs, normalizes service names, removes garbage entries).

```bash
python3 contacts.py fix <id>
```

## Note Format Convention

When adding notes to contacts, use this format:

```
YYYY-MM-DD Met @ [place] via [person/context].
```

Example:
```bash
python3 contacts.py update ABC123 --note "2025-11-28 Met @ Friendsgiving via friends."
```

## Technical Details

### Data Access

- **Reads (search, get):** SQLite queries against `~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb`
- **Writes (create, update, add/remove):** AppleScript via `osascript`

### Why AppleScript for Writes?

The macOS Contacts framework (`CNContact`) has known bugs:
- `mutableCopy()` doesn't preserve notes
- Social profiles get corrupted with garbage data

AppleScript is the canonical, reliable interface that Apple maintains. Changes sync automatically with iCloud.

### Permissions

Full Disk Access may be required for SQLite reads:
- System Settings → Privacy & Security → Full Disk Access
- Add Terminal.app or your terminal emulator

Contacts access is required for AppleScript operations:
- System Settings → Privacy & Security → Contacts

### Database Schema

Key tables in AddressBook SQLite:
- `ZABCDRECORD` - Main contacts table (names, org, job title)
- `ZABCDPHONENUMBER` - Phone numbers (ZLASTFOURDIGITS is indexed)
- `ZABCDEMAILADDRESS` - Email addresses
- `ZABCDPOSTALADDRESS` - Physical addresses
- `ZABCDNOTE` - Notes
