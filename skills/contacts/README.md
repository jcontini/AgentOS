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

# URL operations (for GitHub, Instagram, etc.)
python3 contacts.py url add <id> "https://github.com/johndoe" GitHub
python3 contacts.py url remove <id> github.com

# Social profile operations (Apple-official only)
python3 contacts.py social add <id> twitter johndoe
python3 contacts.py social remove <id> twitter

# Fix corrupted social profiles
python3 contacts.py fix <id>
```

## Social Profiles vs URLs

**Use Social Profiles for Apple-official services only:**
- Twitter, LinkedIn, Facebook, Flickr, Yelp, MySpace, SinaWeibo, TencentWeibo, GameCenter

These get **native "View Profile" / "View Tweets" click actions** in Contacts.app.

**Use URLs for everything else:**
- GitHub, Instagram, TikTok, YouTube, Keybase, AngelList, Quora, Pinterest, Threads, Bluesky, Mastodon, etc.

URLs are **clickable in Contacts.app** and more universal. Custom social profiles (like "GitHub") display text but have no click action.

> **Why?** Apple's social service list hasn't been updated since 2015. See `/System/Library/Frameworks/Contacts.framework/.../CNSocialProfile.h`

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

Returns JSON with all fields including phones, emails, urls, note, and social profiles.

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
  --social "twitter:johndoe" \
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
| `--social` | Social profile as `service:username` (Apple-official only) |

### update

Update contact fields. Use resource subcommands (`phone`, `email`, `url`, `social`) for multi-value fields.

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

### url

Add or remove URLs. Use this for non-Apple social profiles (GitHub, Instagram, etc.) - they'll be clickable in Contacts.app.

```bash
# Add URL with label
python3 contacts.py url add <id> "https://github.com/johndoe" GitHub
python3 contacts.py url add <id> "https://instagram.com/johndoe" Instagram
python3 contacts.py url add <id> "https://keybase.io/johndoe" Keybase

# Remove URL (partial match works)
python3 contacts.py url remove <id> github.com
```

Common URL templates:
| Service | URL Format |
|---------|------------|
| GitHub | `https://github.com/{username}` |
| Instagram | `https://instagram.com/{username}` |
| YouTube | `https://youtube.com/@{username}` |
| TikTok | `https://tiktok.com/@{username}` |
| Keybase | `https://keybase.io/{username}` |
| AngelList | `https://angel.co/u/{username}` |
| Quora | `https://quora.com/profile/{username}` |
| Pinterest | `https://pinterest.com/{username}` |
| Threads | `https://threads.net/@{username}` |
| Bluesky | `https://bsky.app/profile/{handle}` |
| Mastodon | `https://mastodon.social/@{username}` |

### social

Add or remove social profiles. **Only use for Apple-official services** (these get native click actions).

```bash
# Add/update social profile
python3 contacts.py social add <id> twitter johndoe
python3 contacts.py social add <id> linkedin john-doe
python3 contacts.py social add <id> facebook johnd

# Remove social profile
python3 contacts.py social remove <id> twitter
```

**Apple-official services:** Twitter, LinkedIn, Facebook, Flickr, Yelp, MySpace, SinaWeibo, TencentWeibo, GameCenter

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
- `ZABCDURLADDRESS` - URLs with labels
- `ZABCDSOCIALPROFILE` - Social profiles
- `ZABCDPOSTALADDRESS` - Physical addresses
- `ZABCDNOTE` - Notes
