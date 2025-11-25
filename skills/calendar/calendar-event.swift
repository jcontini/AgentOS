#!/usr/bin/env swift
// Unified calendar event management using EventKit (same API as Calendar.app)
// Usage: swift calendar-event.swift <command> [arguments...]
//
// Commands:
//   add    - Add a new event
//   delete - Delete an event
//   update - Update an existing event
//
// Environment variables (optional, can be set in .env):
//   CALENDAR_NAME - Preferred calendar name to match (defaults to system default calendar)
//
// Timezone: Automatically uses system timezone (no configuration needed - works when traveling)

import EventKit
import Foundation

let eventStore = EKEventStore()

// Get user preferences from environment
let preferredCalendarName = ProcessInfo.processInfo.environment["CALENDAR_NAME"] ?? ""
let timezoneIdentifier = TimeZone.current.identifier

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

// Helper function to find calendar
func findCalendar() -> EKCalendar? {
    if !preferredCalendarName.isEmpty,
       let calendar = eventStore.calendars(for: .event).first(where: { $0.title.contains(preferredCalendarName) }) {
        return calendar
    } else if let defaultCalendar = eventStore.defaultCalendarForNewEvents {
        return defaultCalendar
    }
    return nil
}

// Helper function to parse date
func parseDate(_ dateString: String) -> Date? {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm"
    formatter.timeZone = TimeZone(identifier: timezoneIdentifier) ?? TimeZone.current
    return formatter.date(from: dateString)
}

// Helper function to format date for output
func formatDate(_ date: Date) -> String {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .short
    formatter.timeZone = TimeZone(identifier: timezoneIdentifier) ?? TimeZone.current
    return formatter.string(from: date)
}

// Helper function to find events by title and optional date
func findEvents(title: String, startDate: Date? = nil) -> [EKEvent] {
    let calendars = eventStore.calendars(for: .event)
    var foundEvents: [EKEvent] = []
    
    // Search wider range: if date provided, search that day ±1 day, otherwise search next 7 days
    let searchStart: Date
    let searchEnd: Date
    
    if let providedDate = startDate {
        // Search around the provided date (±1 day)
        let providedDay = Calendar.current.startOfDay(for: providedDate)
        searchStart = Calendar.current.date(byAdding: .day, value: -1, to: providedDay)!
        searchEnd = Calendar.current.date(byAdding: .day, value: 2, to: providedDay)!
    } else {
        // Search next 7 days
        let today = Calendar.current.startOfDay(for: Date())
        searchStart = today
        searchEnd = Calendar.current.date(byAdding: .day, value: 7, to: today)!
    }
    
    for calendar in calendars {
        let predicate = eventStore.predicateForEvents(withStart: searchStart, end: searchEnd, calendars: [calendar])
        let events = eventStore.events(matching: predicate)
        
        for event in events {
            if let eventTitle = event.title, eventTitle.localizedCaseInsensitiveContains(title) {
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
    
    return foundEvents
}

// Get command from arguments
guard CommandLine.arguments.count > 1 else {
    print("Usage: swift calendar-event.swift <command> [arguments...]")
    print("\nCommands:")
    print("  add    - Add a new event")
    print("  delete - Delete an event")
    print("  update - Update an existing event")
    print("\nSee README.md for detailed usage examples")
    exit(1)
}

let command = CommandLine.arguments[1]
let args = Array(CommandLine.arguments.dropFirst(2))

switch command {
case "add":
    // Usage: add "Title" "YYYY-MM-DD HH:MM" ["YYYY-MM-DD HH:MM"] ["Location"] ["Description"] ["ReservationURL"]
    guard args.count >= 2 else {
        print("Usage: swift calendar-event.swift add \"Event Title\" \"YYYY-MM-DD HH:MM\" [\"YYYY-MM-DD HH:MM\"] [\"Location\"] [\"Description\"] [\"ReservationURL\"]")
        print("Example: swift calendar-event.swift add \"Meeting\" \"2025-11-25 14:00\" \"2025-11-25 15:00\" \"Conference Room\" \"Team sync\"")
        exit(1)
    }
    
    let title = args[0]
    guard let startDate = parseDate(args[1]) else {
        print("Error: Invalid start date format. Use YYYY-MM-DD HH:MM")
        exit(1)
    }
    
    let endDate = args.count > 2 ? parseDate(args[2]) : startDate.addingTimeInterval(3600)
    let location = args.count > 3 ? args[3] : nil
    var description = args.count > 4 ? args[4] : nil
    let reservationURL = args.count > 5 ? args[5] : nil
    
    // Append reservation URL to description if provided
    if let url = reservationURL {
        if let existingDesc = description, !existingDesc.isEmpty {
            description = "\(existingDesc)\n\nReserve: \(url)"
        } else {
            description = "Reserve: \(url)"
        }
    }
    
    guard let calendar = findCalendar() else {
        print("Error: No calendar found")
        exit(1)
    }
    
    let event = EKEvent(eventStore: eventStore)
    event.title = title
    event.startDate = startDate
    event.endDate = endDate ?? startDate.addingTimeInterval(3600)
    event.location = location
    event.notes = description
    event.calendar = calendar
    
    do {
        try eventStore.save(event, span: .thisEvent)
        print("✓ Event '\(title)' added to calendar '\(calendar.title)'")
        print("  Start: \(formatDate(event.startDate))")
        print("  End: \(formatDate(event.endDate))")
        if let url = reservationURL {
            print("RESERVATION_URL:\(url)")
        }
    } catch {
        print("Error saving event: \(error)")
        exit(1)
    }
    
case "delete":
    // Usage: delete "Title" ["YYYY-MM-DD HH:MM"]
    guard args.count >= 1 else {
        print("Usage: swift calendar-event.swift delete \"Event Title\" [\"YYYY-MM-DD HH:MM\"]")
        print("Example: swift calendar-event.swift delete \"Test Event\" \"2025-11-25 14:00\"")
        exit(1)
    }
    
    let searchTitle = args[0]
    let searchDate = args.count > 1 ? parseDate(args[1]) : nil
    
    let foundEvents = findEvents(title: searchTitle, startDate: searchDate)
    
    guard !foundEvents.isEmpty else {
        print("No events found matching '\(searchTitle)'")
        exit(0)
    }
    
    var deletedCount = 0
    for event in foundEvents {
        do {
            try eventStore.remove(event, span: .thisEvent, commit: false)
            deletedCount += 1
            print("✓ Deleted: '\(event.title ?? "Untitled")' on \(formatDate(event.startDate))")
        } catch {
            print("Error deleting event '\(event.title ?? "Untitled")': \(error)")
        }
    }
    
    do {
        try eventStore.commit()
        print("\n✓ Successfully deleted \(deletedCount) event(s)")
    } catch {
        print("Error committing deletions: \(error)")
        exit(1)
    }
    
case "update":
    // Usage: update "Old Title" ["YYYY-MM-DD HH:MM"] ["New Title"] ["YYYY-MM-DD HH:MM"] ["YYYY-MM-DD HH:MM"] ["Location"] ["Description"]
    guard args.count >= 1 else {
        print("Usage: swift calendar-event.swift update \"Old Title\" [\"YYYY-MM-DD HH:MM\"] [\"New Title\"] [\"YYYY-MM-DD HH:MM\"] [\"YYYY-MM-DD HH:MM\"] [\"Location\"] [\"Description\"]")
        print("Example: swift calendar-event.swift update \"Old Event\" \"2025-11-25 14:00\" \"New Event\" \"2025-11-25 15:00\" \"2025-11-25 16:00\" \"New Location\" \"New Description\"")
        exit(1)
    }
    
    let searchTitle = args[0]
    let searchDate = args.count > 1 ? parseDate(args[1]) : nil
    let newTitle = args.count > 2 ? args[2] : searchTitle
    let newStartDate = args.count > 3 ? parseDate(args[3]) : nil
    let newEndDate = args.count > 4 ? parseDate(args[4]) : nil
    let newLocation = args.count > 5 ? args[5] : nil
    let newDescription = args.count > 6 ? args[6] : nil
    
    let foundEvents = findEvents(title: searchTitle, startDate: searchDate)
    
    guard !foundEvents.isEmpty else {
        print("No events found matching '\(searchTitle)'")
        exit(0)
    }
    
    var updatedCount = 0
    for event in foundEvents {
        event.title = newTitle
        
        if let newStart = newStartDate {
            event.startDate = newStart
        }
        
        if let newEnd = newEndDate {
            event.endDate = newEnd
        } else if newStartDate != nil && newEndDate == nil {
            // If only start date provided, keep original duration
            let duration = event.endDate.timeIntervalSince(event.startDate)
            event.endDate = event.startDate.addingTimeInterval(duration)
        }
        
        if let location = newLocation {
            event.location = location
        }
        
        if let description = newDescription {
            event.notes = description
        }
        
        do {
            try eventStore.save(event, span: .thisEvent, commit: false)
            updatedCount += 1
            print("✓ Updated: '\(event.title ?? "Untitled")' on \(formatDate(event.startDate))")
        } catch {
            print("Error updating event '\(event.title ?? "Untitled")': \(error)")
        }
    }
    
    do {
        try eventStore.commit()
        print("\n✓ Successfully updated \(updatedCount) event(s)")
    } catch {
        print("Error committing updates: \(error)")
        exit(1)
    }
    
default:
    print("Unknown command: \(command)")
    print("Available commands: add, delete, update")
    exit(1)
}

