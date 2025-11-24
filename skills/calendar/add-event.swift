#!/usr/bin/env swift
// Add calendar event using EventKit (same API as Calendar.app)
// Usage: swift add-calendar-event-eventkit.swift "Event Title" "2025-11-24 14:00"
//
// Environment variables (optional, can be set in .env):
//   CALENDAR_NAME - Preferred calendar name to match (defaults to system default calendar)
//
// Timezone: Automatically uses system timezone (no configuration needed)
//
// To use with .env file:
//   set -a && source "$PROJECT_ROOT/.env" && set +a && \
//   swift "$PROJECT_ROOT/skills/calendar/add-event.swift" "Event Title" "2025-11-24 14:00"

import EventKit
import Foundation

let eventStore = EKEventStore()

// Get user preferences from environment (for open-source compatibility)
// Calendar name can be set in .env file, timezone always uses system timezone (adapts when traveling)
let preferredCalendarName = ProcessInfo.processInfo.environment["CALENDAR_NAME"] ?? ""
let timezoneIdentifier = TimeZone.current.identifier  // Always use system timezone - no configuration needed

// Request access using macOS 14+ API
let semaphore = DispatchSemaphore(value: 0)
var accessGranted = false

if #available(macOS 14.0, *) {
    eventStore.requestFullAccessToEvents { granted, error in
        accessGranted = granted
        if let error = error {
            print("Error requesting access: \(error)")
        }
        semaphore.signal()
    }
} else {
    eventStore.requestAccess(to: .event) { granted, error in
        accessGranted = granted
        if let error = error {
            print("Error requesting access: \(error)")
        }
        semaphore.signal()
    }
}

semaphore.wait()

guard accessGranted else {
    print("Calendar access denied. Grant access in System Settings > Privacy & Security > Calendars")
    exit(1)
}

// Create event
let event = EKEvent(eventStore: eventStore)
event.title = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "EventKit Event"

// Parse date from arguments or use now + 1 hour
if CommandLine.arguments.count > 2 {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm"
    formatter.timeZone = TimeZone(identifier: timezoneIdentifier) ?? TimeZone.current
    if let date = formatter.date(from: CommandLine.arguments[2]) {
        event.startDate = date
        // End time from arg 3, or default to 1 hour later
        if CommandLine.arguments.count > 3 {
            if let endDate = formatter.date(from: CommandLine.arguments[3]) {
                event.endDate = endDate
            } else {
                event.endDate = date.addingTimeInterval(3600)
            }
        } else {
            event.endDate = date.addingTimeInterval(3600)
        }
    } else {
        event.startDate = Date()
        event.endDate = Date().addingTimeInterval(3600)
    }
} else {
    event.startDate = Date()
    event.endDate = Date().addingTimeInterval(3600)
}

// Location and description from args
if CommandLine.arguments.count > 4 {
    event.location = CommandLine.arguments[4]
}
if CommandLine.arguments.count > 5 {
    event.notes = CommandLine.arguments[5]
}

// Find calendar (prefer CALENDAR_NAME from env if set, else use system default)
if !preferredCalendarName.isEmpty,
   let calendar = eventStore.calendars(for: .event).first(where: { $0.title.contains(preferredCalendarName) }) {
    event.calendar = calendar
} else if let defaultCalendar = eventStore.defaultCalendarForNewEvents {
    event.calendar = defaultCalendar
} else {
    print("Error: No calendar found")
    exit(1)
}

// Save event
do {
    try eventStore.save(event, span: .thisEvent)
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .short
    formatter.timeZone = TimeZone(identifier: timezoneIdentifier) ?? TimeZone.current
    
    print("✓ Event '\(event.title ?? "Untitled")' added to calendar '\(event.calendar?.title ?? "Unknown")'")
    print("  Start: \(formatter.string(from: event.startDate))")
    print("  End: \(formatter.string(from: event.endDate))")
} catch {
    print("Error saving event: \(error)")
    exit(1)
}
