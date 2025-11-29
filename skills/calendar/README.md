# Calendar Skill

## Intention: Manage calendar events (read, add, update, delete), search calendar, find upcoming events

**Related Skills:**
- [Extract](skills/extract/README.md) - For verifying event URLs (cancellations, venue changes)

**✅ Uses EventKit framework** - Same API as Calendar.app, sees ALL calendars including subscriptions, syncs immediately.

## Quick Reference

**Read today's events:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift"
```

**Read next 7 days:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 7
```

**Read from specific calendar:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 1 Extras
```

**Add an event:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" add "Event Title" "2025-11-24 14:00" "2025-11-24 15:00" "Location" "Description"
```

**Delete an event:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" delete "Event Title" "2025-11-24 14:00"
```

**Update an event:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" update "Old Title" "2025-11-24 14:00" "New Title"
```

---

## Reading Events

### Script: `calendar-read.swift`

Reads events from ALL calendars including subscribed calendars (ICS feeds).

**Usage:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" [days] [calendar_filter]
```

**Arguments:**
- `days` - Number of days to fetch (default: 1 for today only)
- `calendar_filter` - Optional calendar name filter (case-insensitive, partial match)

**Examples:**
```bash
# Today's events from all calendars
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift"

# Next 7 days from all calendars
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 7

# Today's events from Extras calendar only
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 1 Extras

# Next 7 days from Adavia calendar only
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 7 Adavia
```

**Output format (JSON):**
```json
[
  {
    "title": "Dev Sync",
    "start": "2025-11-27 10:00",
    "end": "2025-11-27 11:00",
    "start_time": "10:00",
    "end_time": "11:00",
    "date": "2025-11-27",
    "calendar": "Adavia",
    "all_day": false,
    "location": "Zoom",
    "notes": "Weekly sync meeting",
    "url": "https://example.com/event"
  }
]
```

**Note:** Events may include a `url` field if a URL was added to the event. URLs may also appear in the `notes` field.

**Filter with jq:**
```bash
# List events in simple format
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" | jq -r '.[] | "\(.start_time) | \(.title) | \(.calendar)"'

# Get only non-all-day events
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" | jq '[.[] | select(.all_day == false)]'

# Get events from a specific calendar
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" 7 | jq '[.[] | select(.calendar == "Extras")]'

# Get events with URLs
swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" | jq '[.[] | select(.url != null)]'
```

---

## Researching Events

**When users ask about events, always:**

1. **Check for URLs** - Events may have URLs in:
   - `url` field (direct event URL)
   - `notes` field (may contain URLs as text)
   - Extract URLs from notes using regex or text parsing

2. **Follow URLs to research** - Use the [Extract skill](skills/extract/README.md) to fetch fresh content from event URLs.

3. **Verify event status** - Always check:
   - **Cancellations** - Look for "cancelled", "postponed", "rescheduled" notices
   - **Date/time changes** - Compare calendar date with event page date
   - **Venue changes** - Check if location matches calendar entry
   - **Event status** - Look for "sold out", "postponed", "moved" indicators

**Example workflow:**
```bash
# Get event with URL
EVENT=$(swift "$PROJECT_ROOT/skills/calendar/calendar-read.swift" | jq '.[] | select(.title | contains("Event Name"))')

# Extract URL (check both url field and notes)
EVENT_URL=$(echo "$EVENT" | jq -r '.url // empty')
if [ -z "$EVENT_URL" ]; then
  # Try extracting from notes
  EVENT_URL=$(echo "$EVENT" | jq -r '.notes // ""' | grep -oE 'https?://[^[:space:]]+' | head -1)
fi

# Research event using Extract skill (see skills/extract/README.md)
# The Web Search skill handles fetching fresh content with livecrawl
```

**Key checks when researching:**
- Compare event date on website with calendar date
- Look for cancellation notices or status updates
- Check for rescheduling announcements
- Verify venue/location matches calendar entry
- Look for event details (topics, speakers, schedule) if user asks "what's this about?"

---

## Managing Events

### Script: `calendar-event.swift`

Unified script for add/delete/update operations.

**Commands:**
- `add` - Add a new event
- `delete` - Delete an event
- `update` - Update an existing event

**Environment Variables (optional, add to `.env`):**
- `CALENDAR_NAME` - Preferred calendar name for new events (defaults to system default)

**Note:** Timezone automatically uses system timezone (works when traveling).

### Adding Events

**Usage:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" add "Event Title" "2025-11-24 14:00" "2025-11-24 15:00" "Location" "Description" "URL"
```

**Arguments:**
1. Command: `add` (required)
2. Event title (required)
3. Start date/time: `"YYYY-MM-DD HH:MM"` (required)
4. End date/time: `"YYYY-MM-DD HH:MM"` (optional, defaults to 1 hour after start)
5. Location (optional)
6. Description (optional)
7. URL (optional) - Appended to description as "Reserve: <url>"

**Example:**
```bash
TODAY=$(date +%Y-%m-%d)
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" add \
  "Meeting with Team" \
  "$TODAY 14:00" \
  "$TODAY 15:00" \
  "Conference Room A" \
  "Discuss project updates"
```

### Deleting Events

**Usage:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" delete "Event Title" "2025-11-24 14:00"
```

**Arguments:**
1. Command: `delete` (required)
2. Event title (required)
3. Start date/time (optional, but recommended for precision)

### Updating Events

**Usage:**
```bash
swift "$PROJECT_ROOT/skills/calendar/calendar-event.swift" update "Old Title" "2025-11-24 14:00" "New Title" "2025-11-24 15:00" "2025-11-24 16:00" "New Location" "New Description"
```

**Arguments:**
1. Command: `update` (required)
2. Old event title (required)
3. Old start date/time (optional, recommended for precision)
4. New title (optional, defaults to old title)
5. New start date/time (optional)
6. New end date/time (optional)
7. New location (optional)
8. New description (optional)

---

## Permissions

First-time setup requires calendar access:
1. System Settings > Privacy & Security > Calendars
2. Find Cursor (or Terminal) and grant **"Full Access"**
3. Restart Cursor/Terminal after granting

---

## Why EventKit over SQLite?

| Feature | EventKit | SQLite |
|---------|----------|--------|
| Sees subscribed calendars (ICS feeds) | ✅ Yes | ❌ No |
| Sees all calendar sources | ✅ Yes | ⚠️ Partial |
| Speed | ~100ms | ~5ms |
| Can write events | ✅ Yes | ❌ No |
| Syncs to iCloud/Google | ✅ Yes | N/A |

**Verdict:** EventKit is the way to go. The 100ms tradeoff is worth seeing ALL your calendars.
