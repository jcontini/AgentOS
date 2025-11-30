# Contacts Skill

CRUD interface for macOS Contacts.app.

**Implementation:** Python script using SQLite for reads (fast) and AppleScript for writes (reliable, syncs with iCloud).

## Quick Reference

```bash
# Search
python3 contacts.py search "John Smith"
python3 contacts.py search --phone 5551234
python3 contacts.py search --where "no_photo = true"
python3 contacts.py search --where "no_photo = true AND url LIKE '%instagram%'"

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

# URL operations (for all social profiles)
python3 contacts.py url add <id> "https://twitter.com/johndoe"       # auto-detects label: "Twitter"
python3 contacts.py url add <id> "https://github.com/johndoe"        # auto-detects label: "GitHub"
python3 contacts.py url add <id> "https://example.com" "My Website"  # explicit label
python3 contacts.py url remove <id> github.com

# Migrate social profiles to URLs
python3 contacts.py fix <id>

# Photo operations
python3 contacts.py photo set <id> "https://github.com/johndoe.png"
python3 contacts.py photo set <id> /path/to/photo.jpg
python3 contacts.py photo clear <id>
```

## Why URLs Instead of Social Profiles?

**URLs are used for ALL social profiles** (Twitter, LinkedIn, GitHub, Instagram, etc.) because:

1. **Better sync compatibility** — Apple's `X-SOCIALPROFILE` vCard property is non-standard and gets lost or corrupted when syncing with Google Contacts, Outlook, and other services
2. **Universal** — URLs work everywhere and sync reliably via CardDAV
3. **Still clickable** — URLs are clickable in Contacts.app
4. **Auto-labeled** — Service names are auto-detected from URLs (e.g., `https://twitter.com/johndoe` → label "Twitter")

The `fix` command migrates existing Apple social profiles to URLs for better cross-platform compatibility.

## Commands

### search

Search contacts by name, phone number, or custom query.

```bash
python3 contacts.py search "John"
python3 contacts.py search "Acme Corp"
python3 contacts.py search --phone 5551234
python3 contacts.py search --where "no_photo = true"
python3 contacts.py search --where "organization IS NOT NULL"
python3 contacts.py search --where "url LIKE '%twitter%'"
```

**Virtual fields for `--where`:**
| Field | Description |
|-------|-------------|
| `no_photo = true` | Contacts with no photo at all |
| `has_photo = true` | Contacts with any photo (embedded or reference) |

**Standard fields:** `firstName`, `lastName`, `organization`, `jobTitle`, `photo`, `thumbnail`, `url`, `number`

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

Returns JSON with all fields including phones, emails, urls, socials, and photos array:

```json
{
  "photos": [
    {"type": "thumbnail", "storage": "embedded", "size": 12128}
  ]
}
```

Photo storage types:
- `embedded` - Actual image data stored in Contacts
- `reference` - iCloud/linked photo pointer (38 bytes, still displays in Contacts.app)

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
  --url "https://twitter.com/johndoe" \
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
| `--url` | URL (auto-detects label from known services) |
| `--url-label` | URL label (Twitter, LinkedIn, homepage, etc.) |

### update

Update contact fields. Use resource subcommands (`phone`, `email`, `url`) for multi-value fields.

```bash
python3 contacts.py update ABC123 --org "New Company" --job-title "Senior Engineer"
```

### phone

Add or remove phone numbers. **Numbers are automatically normalized to include country code.**

```bash
# Add phone (label is optional, defaults to "mobile")
python3 contacts.py phone add <id> 5125551234       # → +15125551234
python3 contacts.py phone add <id> (512) 555-1234   # → +15125551234
python3 contacts.py phone add <id> +15125551234     # → +15125551234 (kept as-is)
python3 contacts.py phone add <id> +44 7911 123456  # → +44 7911 123456 (kept as-is)

# Remove phone
python3 contacts.py phone remove <id> +15125551234
```

**Phone Normalization Rules:**
- 10-digit US numbers → `+1` prefix added
- 11-digit numbers starting with 1 → `+` prefix added
- Numbers with `+` prefix → kept as-is (international)
- Short numbers (extensions) → kept as-is

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

Add or remove URLs. **Labels are auto-detected from known services.**

```bash
# Add URL (label auto-detected from URL)
python3 contacts.py url add <id> "https://twitter.com/johndoe"      # → label: "Twitter"
python3 contacts.py url add <id> "https://github.com/johndoe"       # → label: "GitHub"
python3 contacts.py url add <id> "https://linkedin.com/in/johndoe"  # → label: "LinkedIn"

# Add URL with explicit label
python3 contacts.py url add <id> "https://example.com" "My Website"

# Remove URL (partial match works)
python3 contacts.py url remove <id> github.com
```

**Supported services for auto-detection:**
| Service | URL Pattern |
|---------|-------------|
| Twitter | `twitter.com/{username}` |
| LinkedIn | `linkedin.com/in/{username}` |
| Facebook | `facebook.com/{username}` |
| GitHub | `github.com/{username}` |
| Instagram | `instagram.com/{username}` |
| YouTube | `youtube.com/@{username}` |
| TikTok | `tiktok.com/@{username}` |
| Bluesky | `bsky.app/profile/{handle}` |
| Mastodon | `mastodon.social/@{username}` |
| Threads | `threads.net/@{username}` |
| Keybase | `keybase.io/{username}` |
| Pinterest | `pinterest.com/{username}` |
| And more... |

### fix

Migrate social profiles to URLs for better cross-platform sync compatibility.

```bash
python3 contacts.py fix <id>
```

This command:
- Converts Apple social profiles (Twitter, LinkedIn, Facebook, etc.) to clickable URLs
- Preserves the service name as the URL label
- Clears the original social profile entries

Returns which services were migrated:
```json
{"success": true, "message": "Contact fixed. Migrated socials to URLs: Twitter, LinkedIn", "migrated": ["Twitter", "LinkedIn"]}
```

### photo

Set or clear contact photos.

```bash
# Set photo from URL
python3 contacts.py photo set <id> "https://github.com/johndoe.png"
python3 contacts.py photo set <id> "https://avatars.githubusercontent.com/u/12345"

# Set photo from local file
python3 contacts.py photo set <id> /path/to/photo.jpg

# Clear photo
python3 contacts.py photo clear <id>
```

**Photo Sources by Service:**

Services with direct photo URLs (no auth required):
| Service | Photo URL Pattern |
|---------|------------------|
| GitHub | `https://github.com/{username}.png` |
| Facebook | `https://graph.facebook.com/{username}/picture?type=large` |
| Keybase | `https://keybase.io/{username}/photo.png` |
| Gravatar | `https://gravatar.com/avatar/{md5_email}?s=400` |
| Snapchat | `https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=PNG` |

Services with API endpoints (returns JSON with avatar_url):
| Service | API Endpoint |
|---------|-------------|
| GitHub | `https://api.github.com/users/{username}` |
| GitLab | `https://gitlab.com/api/v4/users?username={username}` |
| Bluesky | `https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={username}` |

Services requiring authentication (no easy photo extraction):
- LinkedIn, Twitter/X, Instagram, TikTok, YouTube

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
- `ZABCDRECORD` - Main contacts table (names, org, job title, photos)
  - `ZIMAGEDATA` - Full image BLOB
  - `ZTHUMBNAILIMAGEDATA` - Thumbnail BLOB (main storage for API-set photos)
- `ZABCDPHONENUMBER` - Phone numbers (ZLASTFOURDIGITS is indexed)
- `ZABCDEMAILADDRESS` - Email addresses
- `ZABCDURLADDRESS` - URLs with labels
- `ZABCDSOCIALPROFILE` - Social profiles (legacy, migrated to URLs)
- `ZABCDPOSTALADDRESS` - Physical addresses
- `ZABCDNOTE` - Notes
