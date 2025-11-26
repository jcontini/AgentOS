# Utils

Utility scripts for common operations used across skills.

## Timezone Management

Convert UTC timestamps to the user's local timezone. **Always convert UTC timestamps to local timezone when displaying to users.**

### Script Location

`utils/timezone.sh`

### Usage

The script provides three functions that can be sourced and used in your commands:

#### 1. `utc_to_local()` - Full timestamp conversion

Converts a UTC ISO timestamp to local timezone with date, time, and timezone.

**Usage:**
```bash
source "$PROJECT_ROOT/utils/timezone.sh"
utc_to_local "2025-11-25T03:30:00.925000Z"
# Returns: "2025-11-24 21:30:00 CST" (or appropriate local timezone)
```

**Example in command:**
```bash
source "$PROJECT_ROOT/utils/timezone.sh" && \
utc_to_local "2025-11-25T03:30:00.925000Z"
```

#### 2. `utc_to_local_date()` - Date only

Converts a UTC ISO timestamp to local date (YYYY-MM-DD).

**Usage:**
```bash
source "$PROJECT_ROOT/utils/timezone.sh"
utc_to_local_date "2025-11-25T03:30:00.925000Z"
# Returns: "2025-11-24" (date in local timezone)
```

#### 3. `utc_to_local_time()` - Time only

Converts a UTC ISO timestamp to local time (HH:MM:SS).

**Usage:**
```bash
source "$PROJECT_ROOT/utils/timezone.sh"
utc_to_local_time "2025-11-25T03:30:00.925000Z"
# Returns: "21:30:00" (time in local timezone)
```

### Standalone Usage

You can also run the script directly:

```bash
"$PROJECT_ROOT/utils/timezone.sh" "2025-11-25T03:30:00.925000Z"
```

### Important Notes

- Automatically detects system timezone
- Handles null, empty, or "N/A" values gracefully (returns "N/A")
- Works on both macOS and Linux
- Accepts ISO 8601 format timestamps with or without microseconds and 'Z' suffix
- Always use `$PROJECT_ROOT` variable for paths (never hardcode paths)

### Example: Converting API Response Timestamps

When displaying data from APIs that return UTC timestamps:

```bash
# Get data from API
curl -H "Authorization: Bearer $API_KEY" https://api.example.com/events > /tmp/events.json

# Convert timestamps in the response
source "$PROJECT_ROOT/utils/timezone.sh" && \
jq -r '.events[] | "\(.title): \(utc_to_local(.created_at))"' /tmp/events.json
```

### When to Use

**Always use timezone conversion when:**
- Displaying timestamps from APIs to users
- Showing calendar event times
- Displaying email timestamps
- Showing any date/time information from external services

**Don't use when:**
- Working with timestamps internally (keep UTC)
- Storing data (always store UTC)
- API calls (APIs expect UTC)

