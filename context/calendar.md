# Calendar Management

This file contains procedures and formats for managing calendar events.

## Flight Events

When creating calendar events for flights, use this specific format:

### Title Format
**Pattern:** `✈️ [DEPARTURE]-[ARRIVAL] ([FLIGHT_NUMBER])` 

**Example:** `✈️ AUS-ATL (DL2976)`

### Location
Use full airport name for Google Maps compatibility (e.g., "Austin-Bergstrom International Airport" for departure airport)

### Times
- **Start time:** Departure time in departure airport's local timezone
- **End time:** Arrival time in arrival airport's local timezone
- **Year:** Default to current year unless it seems like it might be next year, then ask to confirm
- **Timezone considerations:** Joe travels frequently, so if discussing travel-related events, confirm timezone/location if not clear from context

### Description Format
```
Confirmation: [6-character airline confirmation code]

Duration: [flight duration]
Aircraft: [aircraft type if available]
[Other relevant flight details]
```

### Airport Arrival Events
When creating flight events, **ALWAYS** create a second event for airport arrival:

**Title:** `@[DEPARTURE_AIRPORT_CODE]`  
**Example:** `@MSY`

**Location:** Full departure airport name (same as flight event location)

**Duration:** Exactly 1 hour, ending exactly when flight departure begins  
**Example:** If flight departs at 7:20 PM, airport event runs 6:20-7:20 PM

**Purpose:** To know when to be at the airport

### Important Notes
- **Do NOT include flight status** in the event since it can change frequently
- **Skip terminal information** if it shows as "TBD" - only include actual terminal numbers/letters
