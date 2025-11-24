# Flights Search Skill

## Intention: Search for flights / Find flight prices

Use SerpApi Google Flights API to search for flights. API key stored in `.env` as `SERPAPI_API_KEY`. Use curl to call SerpApi directly.

**Note:** Generated flight data is saved to `$PROJECT_ROOT/skills-data/flights/` (gitignored, like application data).

**Basic Flight Search (Round Trip):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&departure_id=LAX&arrival_id=AUS&outbound_date=2025-10-14&return_date=2025-10-21&api_key=$SERPAPI_API_KEY" | jq .
```

**One-Way Flight Search:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=LAX&arrival_id=AUS&outbound_date=2025-10-14&api_key=$SERPAPI_API_KEY" | jq .
```

**Common Parameters:**
- `departure_id` (required) - Airport IATA code (e.g., "LAX", "AUS") or comma-separated list for multiple airports
- `arrival_id` (required) - Airport IATA code or comma-separated list
- `outbound_date` (required) - Date in YYYY-MM-DD format
- `return_date` (optional) - Date in YYYY-MM-DD format (required for round trips)
- `type` (optional) - `1` (Round trip, default), `2` (One way), `3` (Multi-city)
- `currency` (optional) - Currency code (e.g., "USD", defaults to USD)
- `travel_class` (optional) - `1` (Economy, default), `2` (Premium economy), `3` (Business), `4` (First)
- `stops` (optional) - Maximum number of stops (e.g., "0" for nonstop, "1", "2")
- `adults` (optional) - Number of adults (default: 1)
- `children` (optional) - Number of children (default: 0)
- `exclude_basic` (optional) - `true` to exclude basic economy fares (US domestic flights only)
- `sort_by` (optional) - `1` (Top flights, default), `2` (Price), `3` (Departure time), `4` (Arrival time), `5` (Duration), `6` (Emissions)
- `gl` (optional) - Country code (e.g., "us", "uk", "fr")
- `hl` (optional) - Language code (e.g., "en", "es", "fr")

**Example with Filters:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&departure_id=LAX&arrival_id=AUS&outbound_date=2025-10-14&return_date=2025-10-21&currency=USD&travel_class=1&stops=0&exclude_basic=true&sort_by=2&api_key=$SERPAPI_API_KEY" | jq .
```

**Response Structure:**
- `other_flights` - **Primary data source** - Array of flight options (may be empty if `best_flights` exists)
- `best_flights` - Top recommended flights (may be null/empty - check `other_flights` if empty)
- `price_insights` - Price trend information
- `search_metadata` - Search execution metadata
- `airports` - Airport information
- `search_parameters` - Parameters used for search

**Flight Object Structure:**
```json
{
  "flights": [{
    "departure_airport": {"id": "AUS", "time": "2025-12-23 09:03"},
    "arrival_airport": {"id": "MCO", "time": "2025-12-23 12:40"},
    "duration": 157,
    "airline": "Frontier",
    "flight_number": "F9 4524"
  }],
  "total_duration": 157,
  "price": 130,
  "type": "One way"
}
```

**Extracting Flight Data:**
```bash
# Check for errors first
jq 'if .error then "Error: \(.error)" else empty end'

# Extract top 5 cheapest flights (always use other_flights, not best_flights)
jq '[.other_flights[]? | {
  price: .price,
  airline: (.flights[0].airline // "Multiple"),
  departure: .flights[0].departure_airport.time,
  arrival: .flights[-1].arrival_airport.time,
  duration_min: .total_duration,
  duration_hrs: "\(.total_duration / 60)h \(.total_duration % 60)m",
  stops: (.flights | length - 1)
}] | sort_by(.price) | .[0:5]'

# Complete example: Search and extract in one call
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=2025-12-23&currency=USD&sort_by=2&api_key=$SERPAPI_API_KEY" | \
jq 'if .error then "Error: \(.error)" elif (.other_flights | length) == 0 then "No flights found" else [.other_flights[]? | {price: .price, airline: .flights[0].airline, departure: .flights[0].departure_airport.time, arrival: .flights[-1].arrival_airport.time, duration: .total_duration, stops: (.flights | length - 1)}] | sort_by(.price) | .[0:5] end'
```

**Date Calculation (Cross-platform):**
```bash
# Always calculate dates dynamically - never hardcode years
CURRENT_YEAR=$(date +%Y)

# Specific date: December 23rd
DATE="2025-12-23"  # Use current year: $(date +%Y)-12-23

# "Around December 23rd" - calculate range (22nd, 23rd, 24th)
# Cross-platform: works on both macOS (BSD date) and Linux (GNU date)
DATE1=$(date +%Y)-12-22
DATE2=$(date +%Y)-12-23
DATE3=$(date +%Y)-12-24

# Relative dates (cross-platform)
TODAY=$(date +%Y-%m-%d)
# Try macOS BSD date first, fallback to Linux GNU date
NEXT_WEEK=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d)
NEXT_MONTH=$(date -v+1m +%Y-%m-%d 2>/dev/null || date -d "+1 month" +%Y-%m-%d)
```

**Important:** Always use current year or future. API rejects past dates with error: `"outbound_date cannot be in the past"`

**Common Errors & Handling:**
- `"outbound_date cannot be in the past"` - Always calculate dates dynamically, never hardcode past years
- Empty `best_flights` - **Always use `other_flights`** - it's the primary data source
- No results - Verify airport codes (IATA format) and dates are valid
- Check `.error` field first before extracting flight data

**Workflow for Comparing Multiple Dates:**
1. Calculate dates dynamically (never hardcode years)
2. Make separate API calls for each date (API doesn't support batching)
3. Extract flight data using `other_flights` array
4. Sort by price and compare results

**Example: Compare flights on Dec 22, 23, 24:**
```bash
# Calculate dates
DATE1="2025-12-22"
DATE2="2025-12-23"
DATE3="2025-12-24"

# Search each date (can chain with &&)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE1&sort_by=2&api_key=$SERPAPI_API_KEY" | jq '{date: "'$DATE1'", flights: [.other_flights[]? | {price: .price, airline: .flights[0].airline, departure: .flights[0].departure_airport.time, duration: .total_duration, stops: (.flights | length - 1)}] | sort_by(.price) | .[0:5]}' && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE2&sort_by=2&api_key=$SERPAPI_API_KEY" | jq '{date: "'$DATE2'", flights: [.other_flights[]? | {price: .price, airline: .flights[0].airline, departure: .flights[0].departure_airport.time, duration: .total_duration, stops: (.flights | length - 1)}] | sort_by(.price) | .[0:5]}' && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE3&sort_by=2&api_key=$SERPAPI_API_KEY" | jq '{date: "'$DATE3'", flights: [.other_flights[]? | {price: .price, airline: .flights[0].airline, departure: .flights[0].departure_airport.time, duration: .total_duration, stops: (.flights | length - 1)}] | sort_by(.price) | .[0:5]}'
```

**Notes:**
- Airport codes must be IATA format (e.g., LAX, AUS, JFK, MCO)
- Dates must be in YYYY-MM-DD format and cannot be in the past
- **Always use `other_flights` array** - `best_flights` is often empty/null
- **Always check for `.error` field** before extracting flight data
- For multi-city trips, use `type=3` with `multi_city_json` parameter
- Use `departure_token` from response to fetch booking options for specific flights
- API does not support batching multiple dates - make separate calls for each date

---

## Interactive Flight Viewer

For a visual, filterable interface to view flight search results, use the HTML viewer at `skills/flights/viewer.html`.

### Generating JSON for Viewer

To generate the JSON file that the viewer loads (saved to `$PROJECT_ROOT/skills-data/flights/flights-results.json`), use this pattern:

```bash
# Example: Search multiple dates and generate viewer JSON
DATE1="2025-12-22"
DATE2="2025-12-23"
DATE3="2025-12-24"

set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE1&sort_by=2&api_key=$SERPAPI_API_KEY" > /tmp/flights_$DATE1.json && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE2&sort_by=2&api_key=$SERPAPI_API_KEY" > /tmp/flights_$DATE2.json && \
curl -s "https://serpapi.com/search.json?engine=google_flights&type=2&departure_id=AUS&arrival_id=MCO&outbound_date=$DATE3&sort_by=2&api_key=$SERPAPI_API_KEY" > /tmp/flights_$DATE3.json && \
jq -s '
def format_time(time):
  (time | split(" ")[1]) as $t |
  ($t | split(":")[0] | tonumber) as $h |
  ($t | split(":")[1]) as $m |
  (if $h > 12 then ($h - 12) else (if $h == 0 then 12 else $h end) end) as $hour |
  (if $h >= 12 then "PM" else "AM" end) as $ampm |
  "\($hour):\($m) \($ampm)";

def format_duration(minutes):
  (minutes / 60 | floor) as $hours |
  (minutes % 60) as $mins |
  "\($hours)h \($mins)m";

def get_flight_info(flights):
  if (flights | length) == 1 then
    "\(flights[0].airline) \(flights[0].flight_number)"
  else
    "\(flights[0].airline) \(flights[0].flight_number) + \(flights | length - 1) more"
  end;

[
  {date: "'$DATE1'", flights: [.[0].other_flights[]? | {
    date: "'$DATE1'",
    price: .price,
    airline: (.flights[0].airline // "Multiple"),
    flight_info: get_flight_info(.flights),
    booking_token: .booking_token,
    booking_url: ("https://www.google.com/travel/flights/search?hl=en&gl=us&curr=USD&adults=1&departure_id=" + (.flights[0].departure_airport.id // "") + "&arrival_id=" + (.flights[-1].arrival_airport.id // "") + "&outbound_date=" + "'$DATE1'" + (if .booking_token then "&tfu=" + .booking_token else "" end)),
    departure_airport: .flights[0].departure_airport.id,
    arrival_airport: .flights[-1].arrival_airport.id,
    departure: format_time(.flights[0].departure_airport.time),
    arrival: format_time(.flights[-1].arrival_airport.time),
    duration: format_duration(.total_duration),
    stops: (.flights | length - 1)
  }]},
  {date: "'$DATE2'", flights: [.[1].other_flights[]? | {
    date: "'$DATE2'",
    price: .price,
    airline: (.flights[0].airline // "Multiple"),
    flight_info: get_flight_info(.flights),
    booking_token: .booking_token,
    booking_url: ("https://www.google.com/travel/flights/search?hl=en&gl=us&curr=USD&adults=1&departure_id=" + (.flights[0].departure_airport.id // "") + "&arrival_id=" + (.flights[-1].arrival_airport.id // "") + "&outbound_date=" + "'$DATE2'" + (if .booking_token then "&tfu=" + .booking_token else "" end)),
    departure_airport: .flights[0].departure_airport.id,
    arrival_airport: .flights[-1].arrival_airport.id,
    departure: format_time(.flights[0].departure_airport.time),
    arrival: format_time(.flights[-1].arrival_airport.time),
    duration: format_duration(.total_duration),
    stops: (.flights | length - 1)
  }]},
  {date: "'$DATE3'", flights: [.[2].other_flights[]? | {
    date: "'$DATE3'",
    price: .price,
    airline: (.flights[0].airline // "Multiple"),
    flight_info: get_flight_info(.flights),
    booking_token: .booking_token,
    booking_url: ("https://www.google.com/travel/flights/search?hl=en&gl=us&curr=USD&adults=1&departure_id=" + (.flights[0].departure_airport.id // "") + "&arrival_id=" + (.flights[-1].arrival_airport.id // "") + "&outbound_date=" + "'$DATE3'" + (if .booking_token then "&tfu=" + .booking_token else "" end)),
    departure_airport: .flights[0].departure_airport.id,
    arrival_airport: .flights[-1].arrival_airport.id,
    departure: format_time(.flights[0].departure_airport.time),
    arrival: format_time(.flights[-1].arrival_airport.time),
    duration: format_duration(.total_duration),
    stops: (.flights | length - 1)
  }]}
] | [.[].flights[]]
' /tmp/flights_$DATE1.json /tmp/flights_$DATE2.json /tmp/flights_$DATE3.json > /tmp/flights-results.json && \
mkdir -p "$PROJECT_ROOT/skills-data/flights" && \
cp /tmp/flights-results.json "$PROJECT_ROOT/skills-data/flights/flights-results.json"
```

**Alternative: Serve from /tmp directory**
If you prefer to keep JSON in /tmp, serve from there instead:
```bash
bunx serve /tmp --port 8000
open http://localhost:8000/flights-results.json  # Test JSON loads
open http://localhost:8000/../skills/flights/viewer.html  # Or copy viewer to /tmp
```

**JSON Structure:**
The generated JSON is an array of flight objects, each containing:
- `date`: Date string (YYYY-MM-DD format)
- `price`: Number (price in USD)
- `airline`: String (airline name)
- `flight_info`: String (airline + flight number, e.g., "Spirit NK 1415")
- `booking_token`: String (base64 encoded token for booking URL)
- `booking_url`: String (Google Flights URL with booking token)
- `departure`: String (formatted time, e.g., "6:00 AM")
- `arrival`: String (formatted time, e.g., "9:39 AM")
- `duration`: String (formatted duration, e.g., "2h 39m")
- `stops`: Number (0 for nonstop, 1+ for stops)

### Serving the Viewer

1. **Start Bun HTTP server:**
   ```bash
   cd "$PROJECT_ROOT/skills/flights"
   bun server.js
   ```
   The server will start on port 8000 and display the URL.

2. **Open the viewer in browser:**
   ```bash
   open http://localhost:8000/viewer.html
   ```
   
   Or visit http://localhost:8000/viewer.html directly in your browser.

The viewer will automatically load `/tmp/flights-results.json` and display flights with filtering capabilities:
- Filter by price range
- Filter by departure/arrival time
- Filter by duration
- Filter by airline (checkboxes)
- Results grouped by date and stops
- Click "Book" buttons to open Google Flights booking pages

**Note:** The viewer looks for `flights-results.json` in `skills-data/flights/` (or falls back to same directory as `viewer.html`, then `/tmp/flights-results.json`). The generation script above saves the JSON to `skills-data/flights/` automatically. Make sure to generate this file before opening the viewer.

