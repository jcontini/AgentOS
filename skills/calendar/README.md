# Calendar Skill

## Intention: Read calendar events, search calendar, find upcoming events, add calendar events

**✅ PRIMARY METHODS:**
- **Reading Events:** Use SQLite directly (fast, milliseconds)
- **Adding Events:** Use EventKit framework (same API as Calendar.app, syncs immediately)

## Quick Reference

**Add an event:**
```bash
swift "$PROJECT_ROOT/skills/calendar/add-event.swift" "Event Title" "2025-11-24 14:00" "2025-11-24 15:00" "Location" "Description"
```

**Delete an event:**
```bash
swift "$PROJECT_ROOT/skills/calendar/delete-event.swift" "Event Title" ["2025-11-24 14:00"]
```

**Search for events:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT summary, datetime(start_date + 978307200, 'unixepoch', 'localtime') as start_time
FROM CalendarItem 
WHERE hidden = 0 AND summary LIKE '%search term%'
ORDER BY start_date ASC;
SQL
```

---

## Reading Events (SQLite)

### Database Location

**Full path:** `~/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb`

**SQLite Version:** 3.43.2 (macOS 15.6.1 Sequoia)

**Important:** Database is read-only for queries. Calendar.app manages it via CoreData.

### Date Format: macOS Epoch Offset

**Critical:** Calendar dates are stored as seconds since **macOS epoch (2001-01-01 00:00:00 UTC)**, NOT UNIX epoch (1970-01-01).

**Offset constant:** `978307200` seconds

**Conversion pattern:**
```bash
# Convert macOS epoch to readable date
datetime(start_date + 978307200, 'unixepoch', 'localtime')

# Convert readable date to macOS epoch for queries
strftime('%s', '2026-01-01') - 978307200
```

### Schema: Key Tables

**CalendarItem (Events)** - Primary table for all calendar events
- `ROWID` - Primary key
- `summary` - Event title/text
- `start_date` - Start time (macOS epoch seconds)
- `end_date` - End time (macOS epoch seconds)
- `all_day` - 1 if all-day event, 0 otherwise
- `calendar_id` - Foreign key to Calendar table
- `location_id` - Foreign key to Location table
- `hidden` - 1 if deleted/hidden, 0 if visible
- `description` - Event description/notes

**Calendar** - Calendar accounts/lists
- `ROWID` - Primary key
- `title` - Calendar name (e.g., "user@example.com", "Work Calendar")

**Location** - Event locations
- `ROWID` - Primary key
- `title` - Location name
- `address` - Full address

### Query Patterns

**Basic Event Search:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.ROWID,
    Calendar.title as calendar_name,
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time,
    datetime(CalendarItem.end_date + 978307200, 'unixepoch', 'localtime') as end_time,
    Location.title as location
FROM CalendarItem
INNER JOIN Calendar ON Calendar.ROWID = CalendarItem.calendar_id
LEFT JOIN Location ON Location.ROWID = CalendarItem.location_id
WHERE CalendarItem.hidden = 0 
  AND CalendarItem.summary LIKE '%search term%'
ORDER BY CalendarItem.start_date ASC;
SQL
```

**Upcoming Events:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time,
    Location.title as location
FROM CalendarItem
LEFT JOIN Location ON Location.ROWID = CalendarItem.location_id
WHERE CalendarItem.hidden = 0 
  AND CalendarItem.start_date > (strftime('%s', 'now') - 978307200)
ORDER BY CalendarItem.start_date ASC
LIMIT 20;
SQL
```

**Date Range Query:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time,
    datetime(CalendarItem.end_date + 978307200, 'unixepoch', 'localtime') as end_time
FROM CalendarItem
WHERE CalendarItem.hidden = 0 
  AND CalendarItem.start_date >= (strftime('%s', '2026-01-01') - 978307200)
  AND CalendarItem.start_date < (strftime('%s', '2026-12-31') - 978307200)
ORDER BY CalendarItem.start_date ASC;
SQL
```

**Filter by Calendar:**
```bash
# Replace 'Your Calendar Name' with your actual calendar name
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time
FROM CalendarItem
INNER JOIN Calendar ON Calendar.ROWID = CalendarItem.calendar_id
WHERE CalendarItem.hidden = 0 
  AND Calendar.title = 'Your Calendar Name'
ORDER BY CalendarItem.start_date ASC;
SQL
```

**Find Events by Person Name:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time,
    Location.title as location
FROM CalendarItem
LEFT JOIN Location ON Location.ROWID = CalendarItem.location_id
WHERE CalendarItem.hidden = 0 
  AND CalendarItem.summary LIKE '%PersonName%'
ORDER BY CalendarItem.start_date DESC;
SQL
```

**Get Event Details:**
```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    CalendarItem.description,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_time,
    datetime(CalendarItem.end_date + 978307200, 'unixepoch', 'localtime') as end_time,
    CalendarItem.all_day,
    Location.title as location,
    Location.address as location_address,
    Calendar.title as calendar_name
FROM CalendarItem
INNER JOIN Calendar ON Calendar.ROWID = CalendarItem.calendar_id
LEFT JOIN Location ON Location.ROWID = CalendarItem.location_id
WHERE CalendarItem.ROWID = YOUR_EVENT_ROWID;
SQL
```

### Performance Tips

1. **Always filter by `hidden = 0`** - Excludes deleted/hidden events
2. **Use date range filters** - Leverages `EventHiddenEndDateStartDate` index
3. **Limit results** - Use `LIMIT` for large result sets
4. **Single query** - Combine joins and filters in one query instead of multiple queries

---

## Managing Events (EventKit)

### EventKit Framework (Recommended)

**✅ USE THIS METHOD** - EventKit is the official API that Calendar.app uses internally. It uses CoreData under the hood and syncs properly to Google Calendar/iCloud.

**Scripts:**
- `$PROJECT_ROOT/skills/calendar/add-event.swift` - Add events
- `$PROJECT_ROOT/skills/calendar/delete-event.swift` - Delete events

### Adding Events

**Usage:**
```bash
# Basic usage (uses system default calendar and timezone)
swift "$PROJECT_ROOT/skills/calendar/add-event.swift" "Event Title" "2025-11-24 14:00" "2025-11-24 15:00" "Location" "Description"

# With .env file (for user-specific calendar)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
swift "$PROJECT_ROOT/skills/calendar/add-event.swift" "Event Title" "2025-11-24 14:00" "2025-11-24 15:00" "Location" "Description"
```

**Environment Variables (optional, add to `.env` for user-specific preferences):**
- `CALENDAR_NAME` - Preferred calendar name to match (e.g., "user@example.com")

**Note:** 
- Calendar name is user-specific and should be in `.env` (not committed to git)
- If `CALENDAR_NAME` is not set, script uses system default calendar
- **Timezone:** Automatically uses system timezone (no configuration needed - works when traveling)

**Arguments:**
1. Event title (required)
2. Start date/time: `"YYYY-MM-DD HH:MM"` (required)
3. End date/time: `"YYYY-MM-DD HH:MM"` (optional, defaults to 1 hour after start)
4. Location (optional)
5. Description (optional)

**Example:**
```bash
TODAY=$(date +%Y-%m-%d)
swift "$PROJECT_ROOT/skills/calendar/add-event.swift" \
  "Meeting with Team" \
  "$TODAY 14:00" \
  "$TODAY 15:00" \
  "Conference Room A" \
  "Discuss project updates"
```

### Deleting Events

**Usage:**
```bash
# Delete by title (searches today)
swift "$PROJECT_ROOT/skills/calendar/delete-event.swift" "Event Title"

# Delete by title and specific time (more precise)
swift "$PROJECT_ROOT/skills/calendar/delete-event.swift" "Event Title" "2025-11-24 14:00"
```

**Example:**
```bash
# Delete a test event from today
swift "$PROJECT_ROOT/skills/calendar/delete-event.swift" "Test Event"

# Delete specific event by time
swift "$PROJECT_ROOT/skills/calendar/delete-event.swift" "Meeting" "2025-11-24 14:00"
```

**Note:** EventKit deletions sync properly to Google Calendar/iCloud, just like additions. Events must have been created via EventKit (not SQLite) to be deletable via EventKit.

**Advantages:**
- ✅ Uses same API as Calendar.app (EventKit/CoreData)
- ✅ Syncs immediately to Google Calendar/iCloud
- ✅ Appears instantly in Calendar.app
- ✅ No Calendar.app needed to be open
- ✅ Fast (milliseconds)
- ✅ Proper CoreData integration with all sync metadata
- ✅ Creates events with `external_id` for cloud sync

**Permissions:** First-time setup requires calendar access grant:
- System Settings > Privacy & Security > Calendars > Cursor (or Terminal)
- Grant "Full Access" (not "Add Only")
- Restart Cursor/Terminal after granting

### ICS File Import (Fallback)

**Use when:** EventKit permissions aren't available or you need a quick one-off event.

**Template:**
```bash
# Get timezone from system (automatically adapts when traveling)
# macOS: Get timezone identifier from system
TZONE=$(readlink /etc/localtime | sed 's#.*zoneinfo/##' || echo "America/Chicago")
TODAY=$(date +%Y%m%d)
START_TIME="1400"  # 2:00 PM
END_TIME="1500"    # 3:00 PM
EVENT_UID=$(uuidgen | tr '[:lower:]' '[:upper:]')

cat > /tmp/event.ics << ICS
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Calendar//Event//EN
BEGIN:VEVENT
UID:${EVENT_UID}
DTSTART;TZID=${TZONE}:${TODAY}T${START_TIME}00
DTEND;TZID=${TZONE}:${TODAY}T${END_TIME}00
SUMMARY:Event Title
DESCRIPTION:Event description
LOCATION:Event location
END:VEVENT
END:VCALENDAR
ICS

open /tmp/event.ics
```

**Note:** Timezone is automatically detected from system (adapts when traveling). No configuration needed.

**Advantages:**
- ✅ Syncs to Google Calendar/iCloud automatically
- ✅ Calendar.app handles import properly
- ✅ No permissions needed
- ✅ Works even if Calendar.app is closed

---

## Example: Finding Events by Multiple Criteria

```bash
sqlite3 ~/Library/Group\ Containers/group.com.apple.calendar/Calendar.sqlitedb << 'SQL'
SELECT 
    CalendarItem.summary,
    datetime(CalendarItem.start_date + 978307200, 'unixepoch', 'localtime') as start_date,
    datetime(CalendarItem.end_date + 978307200, 'unixepoch', 'localtime') as end_date,
    Location.title as location
FROM CalendarItem
LEFT JOIN Location ON Location.ROWID = CalendarItem.location_id
WHERE CalendarItem.hidden = 0 
  AND CalendarItem.summary LIKE '%PersonName%'
  AND (CalendarItem.summary LIKE '%event type%' OR CalendarItem.summary LIKE '%keyword%')
ORDER BY CalendarItem.start_date DESC;
SQL
```

**Note:** Replace `PersonName` and `event type`/`keyword` with your search terms. This query demonstrates combining multiple search criteria.
