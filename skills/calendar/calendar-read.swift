#!/usr/bin/env swift
// Read calendar events using EventKit (sees ALL calendars including subscriptions)
// Usage: swift calendar-read.swift [days] [calendar_filter]
//
// Arguments:
//   days            - Number of days to fetch (default: 1 for today only)
//   calendar_filter - Optional calendar name to filter (e.g., "Extras", "Adavia")
//
// Examples:
//   swift calendar-read.swift              # Today's events from all calendars
//   swift calendar-read.swift 7            # Next 7 days from all calendars
//   swift calendar-read.swift 1 Extras     # Today's events from Extras calendar only
//   swift calendar-read.swift 7 Adavia     # Next 7 days from Adavia calendar only

import EventKit
import Foundation

let eventStore = EKEventStore()

// Parse arguments
let args = CommandLine.arguments
let daysToFetch = args.count > 1 ? Int(args[1]) ?? 1 : 1
let calendarFilter = args.count > 2 ? args[2] : nil

// Request access
let semaphore = DispatchSemaphore(value: 0)
var accessGranted = false

if #available(macOS 14.0, *) {
    eventStore.requestFullAccessToEvents { granted, error in
        accessGranted = granted
        if let error = error {
            fputs("Error requesting access: \(error)\n", stderr)
        }
        semaphore.signal()
    }
} else {
    eventStore.requestAccess(to: .event) { granted, error in
        accessGranted = granted
        if let error = error {
            fputs("Error requesting access: \(error)\n", stderr)
        }
        semaphore.signal()
    }
}
semaphore.wait()

guard accessGranted else {
    fputs("Calendar access denied. Grant access in System Settings > Privacy & Security > Calendars\n", stderr)
    exit(1)
}

// Get date range
let calendar = Calendar.current
let startOfDay = calendar.startOfDay(for: Date())
let endDate = calendar.date(byAdding: .day, value: daysToFetch, to: startOfDay)!

// Filter calendars if specified
var calendarsToSearch: [EKCalendar]? = nil
if let filter = calendarFilter {
    calendarsToSearch = eventStore.calendars(for: .event).filter { 
        $0.title.lowercased().contains(filter.lowercased()) 
    }
    if calendarsToSearch?.isEmpty == true {
        fputs("No calendars found matching '\(filter)'\n", stderr)
        exit(1)
    }
}

// Query events
let predicate = eventStore.predicateForEvents(withStart: startOfDay, end: endDate, calendars: calendarsToSearch)
let events = eventStore.events(matching: predicate)

// Format output as JSON
let dateFormatter = DateFormatter()
dateFormatter.dateFormat = "yyyy-MM-dd HH:mm"

let timeFormatter = DateFormatter()
timeFormatter.dateFormat = "HH:mm"

let dayFormatter = DateFormatter()
dayFormatter.dateFormat = "yyyy-MM-dd"

var output: [[String: Any]] = []

for event in events.sorted(by: { $0.startDate < $1.startDate }) {
    var eventDict: [String: Any] = [
        "title": event.title ?? "",
        "start": dateFormatter.string(from: event.startDate),
        "end": dateFormatter.string(from: event.endDate),
        "start_time": timeFormatter.string(from: event.startDate),
        "end_time": timeFormatter.string(from: event.endDate),
        "date": dayFormatter.string(from: event.startDate),
        "calendar": event.calendar.title,
        "all_day": event.isAllDay
    ]
    
    if let location = event.location, !location.isEmpty {
        eventDict["location"] = location
    }
    
    if let notes = event.notes, !notes.isEmpty {
        eventDict["notes"] = notes
    }
    
    if let url = event.url {
        eventDict["url"] = url.absoluteString
    }
    
    output.append(eventDict)
}

// Output JSON
if let jsonData = try? JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys]),
   let jsonString = String(data: jsonData, encoding: .utf8) {
    print(jsonString)
} else {
    print("[]")
}

