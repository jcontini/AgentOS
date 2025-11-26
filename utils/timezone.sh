#!/bin/bash
# UTC to Local Timezone Conversion Utility
# 
# This utility converts UTC ISO timestamps to the user's local timezone.
# Used by AI assistants when displaying timestamps to users.
#
# Usage (standalone):
#   ./utc-to-local.sh "2025-11-25T03:30:00.925000Z"
#
# Usage (sourced in scripts):
#   source utc-to-local.sh
#   utc_to_local "2025-11-25T03:30:00.925000Z"

# Function to convert UTC ISO timestamp to local timezone
# Usage: utc_to_local "2025-11-25T03:30:00.925000Z"
# Returns: "2025-11-24 21:30:00 CST" (or appropriate local timezone)
utc_to_local() {
    local utc_timestamp="$1"
    if [ -z "$utc_timestamp" ] || [ "$utc_timestamp" = "N/A" ] || [ "$utc_timestamp" = "null" ]; then
        echo "N/A"
        return
    fi
    
    # Remove microseconds and 'Z' if present, keep ISO format
    local clean_timestamp=$(echo "$utc_timestamp" | sed 's/\.[0-9]*Z\?$//' | sed 's/Z$//')
    
    # Convert UTC to local timezone using epoch seconds as intermediary
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - parse UTC time, get epoch seconds, then format in local timezone
        local epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" -u "$clean_timestamp" "+%s" 2>/dev/null)
        if [ -n "$epoch" ]; then
            date -r "$epoch" "+%Y-%m-%d %H:%M:%S %Z" 2>/dev/null || echo "$utc_timestamp"
        else
            # Fallback: use gdate if available (GNU date)
            (command -v gdate >/dev/null && gdate -d "$clean_timestamp" "+%Y-%m-%d %H:%M:%S %Z" 2>/dev/null) || \
            echo "$utc_timestamp"
        fi
    else
        # Linux - parse as UTC, output in local timezone
        TZ=UTC date -d "$clean_timestamp" "+%Y-%m-%d %H:%M:%S %Z" 2>/dev/null || echo "$utc_timestamp"
    fi
}

# Function to convert UTC ISO timestamp to local date only (YYYY-MM-DD)
# Usage: utc_to_local_date "2025-11-25T03:30:00.925000Z"
# Returns: "2025-11-24" (date in local timezone)
utc_to_local_date() {
    local utc_timestamp="$1"
    if [ -z "$utc_timestamp" ] || [ "$utc_timestamp" = "N/A" ] || [ "$utc_timestamp" = "null" ]; then
        echo "N/A"
        return
    fi
    
    local clean_timestamp=$(echo "$utc_timestamp" | sed 's/\.[0-9]*Z\?$//' | sed 's/Z$//')
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - parse UTC time, get epoch seconds, then format date in local timezone
        local epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" -u "$clean_timestamp" "+%s" 2>/dev/null)
        if [ -n "$epoch" ]; then
            date -r "$epoch" "+%Y-%m-%d" 2>/dev/null || echo "$utc_timestamp" | cut -d'T' -f1
        else
            # Fallback: use gdate if available
            (command -v gdate >/dev/null && gdate -d "$clean_timestamp" "+%Y-%m-%d" 2>/dev/null) || \
            echo "$utc_timestamp" | cut -d'T' -f1
        fi
    else
        # Linux - parse UTC timestamp, output date in local timezone
        TZ=UTC date -d "$clean_timestamp" "+%Y-%m-%d" 2>/dev/null || echo "$utc_timestamp" | cut -d'T' -f1
    fi
}

# Function to convert UTC ISO timestamp to local time only (HH:MM:SS)
# Usage: utc_to_local_time "2025-11-25T03:30:00.925000Z"
# Returns: "21:30:00" (time in local timezone)
utc_to_local_time() {
    local utc_timestamp="$1"
    if [ -z "$utc_timestamp" ] || [ "$utc_timestamp" = "N/A" ] || [ "$utc_timestamp" = "null" ]; then
        echo "N/A"
        return
    fi
    
    local clean_timestamp=$(echo "$utc_timestamp" | sed 's/\.[0-9]*Z\?$//' | sed 's/Z$//')
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" -u "$clean_timestamp" "+%s" 2>/dev/null)
        if [ -n "$epoch" ]; then
            date -r "$epoch" "+%H:%M:%S" 2>/dev/null || echo "$utc_timestamp" | cut -d'T' -f2 | cut -d'.' -f1
        else
            (command -v gdate >/dev/null && gdate -d "$clean_timestamp" "+%H:%M:%S" 2>/dev/null) || \
            echo "$utc_timestamp" | cut -d'T' -f2 | cut -d'.' -f1
        fi
    else
        TZ=UTC date -d "$clean_timestamp" "+%H:%M:%S" 2>/dev/null || echo "$utc_timestamp" | cut -d'T' -f2 | cut -d'.' -f1
    fi
}

# If run directly (not sourced), convert the first argument
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <UTC_TIMESTAMP>"
        echo "Example: $0 '2025-11-25T03:30:00.925000Z'"
        exit 1
    fi
    utc_to_local "$1"
fi

