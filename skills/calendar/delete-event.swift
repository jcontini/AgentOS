#!/usr/bin/env swift
// Delete calendar event using EventKit (same API as Calendar.app)
// Usage: swift delete-calendar-event-eventkit.swift "Event Title" "2025-11-24 14:00"
//
// This properly deletes events through CoreData so they sync to Google Calendar/iCloud

import EventKit
import Foundation

let eventStore = EKEventStore()

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

// Get search criteria from arguments
let searchTitle = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ""
let searchDate = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : ""

guard !searchTitle.isEmpty else {
    print("Usage: swift delete-calendar-event-eventkit.swift \"Event Title\" [\"YYYY-MM-DD HH:MM\"]")
    print("Example: swift delete-calendar-event-eventkit.swift \"Test Event\" \"2025-11-24 14:00\"")
    exit(1)
}

// Parse date if provided
var startDate: Date? = nil
if !searchDate.isEmpty {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm"
    formatter.timeZone = TimeZone.current
    startDate = formatter.date(from: searchDate)
}

// Find events matching criteria
// Search today with wider time window to catch events created via SQLite
let calendars = eventStore.calendars(for: .event)
var foundEvents: [EKEvent] = []

// Search entire day
let today = Calendar.current.startOfDay(for: Date())
let tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: today)!

for calendar in calendars {
    let predicate = eventStore.predicateForEvents(withStart: today, end: tomorrow, calendars: [calendar])
    let events = eventStore.events(matching: predicate)
    
    for event in events {
        if let title = event.title, title.localizedCaseInsensitiveContains(searchTitle) {
            // If date specified, check if it matches (within 2 hour window)
            if let start = startDate {
                let timeDiff = abs(event.startDate.timeIntervalSince(start))
                if timeDiff <= 7200 {  // 2 hour window
                    foundEvents.append(event)
                }
            } else {
                foundEvents.append(event)
            }
        }
    }
}

guard !foundEvents.isEmpty else {
    print("No events found matching '\(searchTitle)'")
    exit(0)
}

// Delete events
var deletedCount = 0
for event in foundEvents {
    do {
        try eventStore.remove(event, span: .thisEvent, commit: false)
        deletedCount += 1
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        print("✓ Deleted: '\(event.title ?? "Untitled")' on \(formatter.string(from: event.startDate))")
    } catch {
        print("Error deleting event '\(event.title ?? "Untitled")': \(error)")
    }
}

// Commit all deletions
do {
    try eventStore.commit()
    print("\n✓ Successfully deleted \(deletedCount) event(s)")
} catch {
    print("Error committing deletions: \(error)")
    exit(1)
}

