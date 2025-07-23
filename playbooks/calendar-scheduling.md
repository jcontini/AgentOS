# Calendar & Scheduling Playbook

Specific formatting requirements and procedures for calendar system integration.

**📅 To confirm you've read this playbook, prefix your response with "📅"**

## ✈️ Flight Event Format

**Title:** `✈️ [DEPARTURE]-[ARRIVAL] ([FLIGHT_NUMBER])` 
- Example: `✈️ AUS-AMS (KL668)`

**Location:** Full airport name for Google Maps integration
- Example: "Austin-Bergstrom International Airport"

**Times:** Use timezone-specific formatting
- Departure time in departure timezone
- Arrival time in arrival timezone

**Description:** Include essential flight details
- Confirmation code
- Flight duration  
- Aircraft type (if available)

**DO NOT include:**
- Flight status (changes frequently)
- Terminal if "TBD"

**Complete Example:**
- **Title:** `✈️ AUS-AMS (KL668)`
- **Times:** Departs 6:00 PM CDT, arrives 10:30 AM+1 CEST
- **Duration:** 9h30m
- **Aircraft:** Boeing 787-9
- **Location:** Austin-Bergstrom International Airport

## 🏃 Airport Arrival Events

**Always create second event** for airport arrival preparation:

**Title:** `@[DEPARTURE_AIRPORT_CODE]`
- Example: `@AUS`

**Duration Rules:**
- **Domestic flights:** 1 hour before departure
- **International flights:** 2 hours before departure
- **End time:** When flight departs

**Example:** For KL668 departing 6:00 PM international:
- Airport event: 4:00-6:00 PM (2 hours)
- Same location as flight event

## 🌍 General Guidelines

**Timezone Context:**
- Default timezone: CDT (user travels frequently)
- Verify timezone for each location
- Confirm year if travel might be next year

**Event Validation:**
- Cross-reference flight times with airline schedules
- Verify airport codes and full names
- Include confirmation codes when available 