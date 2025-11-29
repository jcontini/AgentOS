#!/usr/bin/env swift
// Contacts management using Contacts framework (same API as Contacts.app)
// Usage: swift contacts.swift <command> [arguments...]
//
// Commands:
//   add    - Add a new contact
//   update - Update an existing contact
//   search - Search for contacts (returns JSON)
//
// All write operations sync with iCloud/other contact sources automatically

import Contacts
import Foundation

let contactStore = CNContactStore()

// Request access
let semaphore = DispatchSemaphore(value: 0)
var accessGranted = false

contactStore.requestAccess(for: .contacts) { granted, error in
    accessGranted = granted
    if let error = error {
        fputs("Error requesting access: \(error)\n", stderr)
    }
    semaphore.signal()
}

semaphore.wait()

guard accessGranted else {
    fputs("Contacts access denied. Grant access in System Settings > Privacy & Security > Contacts\n", stderr)
    exit(1)
}

// Helper to output JSON
func outputJSON(_ dict: [String: Any]) {
    if let data = try? JSONSerialization.data(withJSONObject: dict, options: .prettyPrinted),
       let str = String(data: data, encoding: .utf8) {
        print(str)
    }
}

// Common keys to fetch for all operations
let keysToFetch: [CNKeyDescriptor] = [
    CNContactIdentifierKey as CNKeyDescriptor,
    CNContactGivenNameKey as CNKeyDescriptor,
    CNContactFamilyNameKey as CNKeyDescriptor,
    CNContactMiddleNameKey as CNKeyDescriptor,
    CNContactNicknameKey as CNKeyDescriptor,
    CNContactOrganizationNameKey as CNKeyDescriptor,
    CNContactJobTitleKey as CNKeyDescriptor,
    CNContactDepartmentNameKey as CNKeyDescriptor,
    CNContactPhoneNumbersKey as CNKeyDescriptor,
    CNContactEmailAddressesKey as CNKeyDescriptor,
    CNContactPostalAddressesKey as CNKeyDescriptor,
    CNContactNoteKey as CNKeyDescriptor,
    CNContactBirthdayKey as CNKeyDescriptor
]

// Helper to find contacts by name or phone
func findContacts(query: String, byPhone: Bool = false) -> [CNContact] {
    
    var results: [CNContact] = []
    
    if byPhone {
        // Search by phone - normalize and search
        let normalizedQuery = query.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
        let predicate = CNContact.predicateForContacts(matching: CNPhoneNumber(stringValue: query))
        if let contacts = try? contactStore.unifiedContacts(matching: predicate, keysToFetch: keysToFetch) {
            results.append(contentsOf: contacts)
        }
        
        // Also try partial match via enumeration if exact match fails
        if results.isEmpty && normalizedQuery.count >= 4 {
            let lastFour = String(normalizedQuery.suffix(4))
            let request = CNContactFetchRequest(keysToFetch: keysToFetch)
            try? contactStore.enumerateContacts(with: request) { contact, _ in
                for phone in contact.phoneNumbers {
                    let phoneDigits = phone.value.stringValue.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
                    if phoneDigits.hasSuffix(lastFour) || phoneDigits.contains(normalizedQuery) {
                        results.append(contact)
                        break
                    }
                }
            }
        }
    } else {
        // Search by name - use enumeration to ensure all keys are fetched
        let queryLower = query.lowercased()
        let request = CNContactFetchRequest(keysToFetch: keysToFetch)
        try? contactStore.enumerateContacts(with: request) { contact, stop in
            let fullName = "\(contact.givenName) \(contact.familyName)".lowercased()
            let org = contact.organizationName.lowercased()
            if fullName.contains(queryLower) || contact.givenName.lowercased().contains(queryLower) || 
               contact.familyName.lowercased().contains(queryLower) || org.contains(queryLower) {
                results.append(contact)
            }
            // Limit results for performance
            if results.count >= 50 { stop.pointee = true }
        }
    }
    
    return results
}

// Helper to get note via AppleScript (Contacts framework has bugs with notes)
func getNoteViaAppleScript(firstName: String, lastName: String) -> String {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            return note of thePerson
        on error
            return ""
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    
    let pipe = Pipe()
    task.standardOutput = pipe
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) {
            return output == "missing value" ? "" : output
        }
    } catch {}
    return ""
}

// Helper to set note via AppleScript (Contacts framework has bugs with notes)
func setNoteViaAppleScript(firstName: String, lastName: String, note: String) -> Bool {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedNote = note.replacingOccurrences(of: "\"", with: "\\\"")
    
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            set the note of thePerson to "\(escapedNote)"
            save
            return "success"
        on error errMsg
            return errMsg
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    
    let pipe = Pipe()
    task.standardOutput = pipe
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
        return task.terminationStatus == 0
    } catch {}
    return false
}

// Social services: (normalizedName, domain) - single source of truth
let socialServices: [(name: String, domain: String)] = [
    ("Instagram", "instagram.com"),
    ("LinkedIn", "linkedin.com"),
    ("Twitter", "twitter.com"),
    ("Facebook", "facebook.com"),
    ("TikTok", "tiktok.com"),
    ("YouTube", "youtube.com"),
    ("Snapchat", "snapchat.com"),
    ("Pinterest", "pinterest.com"),
    ("Reddit", "reddit.com"),
    ("WhatsApp", "whatsapp.com"),
    ("Telegram", "telegram.org"),
    ("Signal", "signal.org"),
    ("Discord", "discord.com"),
    ("Slack", "slack.com"),
    ("GitHub", "github.com"),
    ("Mastodon", "mastodon.social"),
    ("Bluesky", "bsky.app"),
    ("Threads", "threads.net"),
]

// Normalize service name to proper case (macOS Contacts displays ALL CAPS as garbage)
func normalizeServiceName(_ service: String) -> String {
    let lower = service.lowercased()
    // Handle X -> Twitter alias
    if lower == "x" { return "Twitter" }
    // Look up in socialServices
    if let match = socialServices.first(where: { $0.name.lowercased() == lower }) {
        return match.name
    }
    // Default: capitalize first letter
    return service.prefix(1).uppercased() + service.dropFirst().lowercased()
}

// Get domain for a service (for garbage detection)
func getDomainForService(_ service: String) -> String? {
    let lower = service.lowercased()
    if lower == "x" { return "twitter.com" }
    return socialServices.first(where: { $0.name.lowercased() == lower })?.domain
}

// Helper to get social profiles via AppleScript (Contacts framework has bugs)
func getSocialProfilesViaAppleScript(firstName: String, lastName: String) -> [[String: String]] {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    
    // Use ||| as delimiter to avoid conflicts with usernames containing commas or colons
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            set profileList to ""
            repeat with sp in social profiles of thePerson
                set serviceName to service name of sp
                set userName to user name of sp
                if userName is not missing value then
                    if profileList is not "" then
                        set profileList to profileList & "|||"
                    end if
                    set profileList to profileList & serviceName & ":::" & userName
                end if
            end repeat
            return profileList
        on error
            return ""
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    
    let pipe = Pipe()
    task.standardOutput = pipe
    task.standardError = FileHandle.nullDevice
    
    var profiles: [[String: String]] = []
    do {
        try task.run()
        task.waitUntilExit()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines),
           !output.isEmpty && output != "missing value" {
            // Parse "service:::username|||service:::username" format
            let items = output.components(separatedBy: "|||")
            for item in items {
                let parts = item.components(separatedBy: ":::")
                if parts.count >= 2 {
                    let service = parts[0].trimmingCharacters(in: .whitespaces)
                    let username = parts.dropFirst().joined(separator: ":::").trimmingCharacters(in: .whitespaces)
                    if !service.isEmpty && !username.isEmpty {
                        profiles.append(["service": service, "username": username])
                    }
                }
            }
        }
    } catch {}
    return profiles
}

// Helper to upsert social profile via AppleScript (finds existing by service name, updates or adds)
func upsertSocialProfileViaAppleScript(firstName: String, lastName: String, service: String, username: String) -> Bool {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    let normalizedService = normalizeServiceName(service)
    let escapedUsername = username.replacingOccurrences(of: "\"", with: "\\\"")
    
    // AppleScript is case-insensitive by default, so "Instagram" matches "INSTAGRAM"
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            set didUpdate to false
            repeat with sp in social profiles of thePerson
                if service name of sp is "\(normalizedService)" then
                    set service name of sp to "\(normalizedService)"
                    set user name of sp to "\(escapedUsername)"
                    set didUpdate to true
                    exit repeat
                end if
            end repeat
            if not didUpdate then
                make new social profile at end of social profiles of thePerson with properties {service name:"\(normalizedService)", user name:"\(escapedUsername)"}
            end if
            save
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    task.standardOutput = FileHandle.nullDevice
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
        return task.terminationStatus == 0
    } catch {}
    return false
}

// Helper to auto-fix ALL corrupted social profiles for a contact (runs after any update)
func autoFixAllSocialProfilesViaAppleScript(firstName: String, lastName: String) {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    
    // Build service mappings for AppleScript: {lowercase: {name, domain}}
    var serviceMappings = ""
    for svc in socialServices {
        let lower = svc.name.lowercased()
        serviceMappings += "if svcLower is \"\(lower)\" then\n"
        serviceMappings += "    set normalizedName to \"\(svc.name)\"\n"
        serviceMappings += "    set expectedDomain to \"www.\(svc.domain)\"\n"
        serviceMappings += "end if\n"
    }
    
    // Scan all profiles: normalize service names, fix usernames, nullify garbage
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            repeat with sp in social profiles of thePerson
                set svc to service name of sp
                set usr to user name of sp
                set theUrl to url of sp
                
                -- Get lowercase service name for lookups
                set svcLower to ""
                if svc is not missing value then
                    set svcLower to do shell script "echo " & quoted form of svc & " | tr '[:upper:]' '[:lower:]'"
                end if
                
                -- Look up normalized name and expected domain
                set normalizedName to ""
                set expectedDomain to ""
                \(serviceMappings)
                
                -- Step 1: Check if username is garbage (missing, TYPE=PREF, or substring of domain)
                set hasValidUsername to false
                if usr is not missing value and usr is not "" and usr is not "TYPE=PREF" then
                    -- Check if username is a substring of expected domain (garbage like "www.facebook")
                    if expectedDomain is not "" and expectedDomain contains usr then
                        set hasValidUsername to false
                    else
                        set hasValidUsername to true
                    end if
                end if
                
                -- Step 2: If no valid username, try to extract from URL (after last /)
                if not hasValidUsername and theUrl is not missing value and theUrl is not "" then
                    set AppleScript's text item delimiters to "/"
                    set urlParts to text items of theUrl
                    set extractedUser to last item of urlParts
                    set AppleScript's text item delimiters to ""
                    if extractedUser is "" and (count of urlParts) > 1 then
                        set extractedUser to item -2 of urlParts
                    end if
                    -- Check extracted value is not domain garbage
                    if (count of extractedUser) > 0 then
                        if expectedDomain is "" or expectedDomain does not contain extractedUser then
                            set usr to extractedUser
                            set hasValidUsername to true
                        end if
                    end if
                end if
                
                -- Step 3: Apply fix or nullify
                if not hasValidUsername then
                    -- No valid username anywhere, nullify the profile
                    set service name of sp to ""
                    set user name of sp to ""
                    set url of sp to ""
                else
                    -- Valid username found, normalize service name
                    if normalizedName is not "" then
                        set service name of sp to normalizedName
                    end if
                    set user name of sp to usr
                end if
            end repeat
            save
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    task.standardOutput = FileHandle.nullDevice
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
    } catch {}
}

// Helper to fix corrupted social profile via AppleScript (extracts username from URL, normalizes service name)
func fixSocialProfileViaAppleScript(firstName: String, lastName: String, service: String) -> Bool {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    let normalizedService = normalizeServiceName(service)
    let expectedDomain = getDomainForService(service).map { "www.\($0)" } ?? ""
    
    // Find profile, fix it using same logic as auto-fix
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            set expectedDomain to "\(expectedDomain)"
            repeat with sp in social profiles of thePerson
                if service name of sp is "\(normalizedService)" then
                    set usr to user name of sp
                    set theUrl to url of sp
                    
                    -- Check if existing username is valid (not garbage)
                    set hasValidUsername to false
                    if usr is not missing value and usr is not "" and usr is not "TYPE=PREF" then
                        if expectedDomain is "" or expectedDomain does not contain usr then
                            set hasValidUsername to true
                        end if
                    end if
                    
                    -- If no valid username, try to extract from URL
                    if not hasValidUsername and theUrl is not missing value and theUrl is not "" then
                        set AppleScript's text item delimiters to "/"
                        set urlParts to text items of theUrl
                        set extractedUser to last item of urlParts
                        set AppleScript's text item delimiters to ""
                        if extractedUser is "" and (count of urlParts) > 1 then
                            set extractedUser to item -2 of urlParts
                        end if
                        if (count of extractedUser) > 0 and (expectedDomain is "" or expectedDomain does not contain extractedUser) then
                            set usr to extractedUser
                            set hasValidUsername to true
                        end if
                    end if
                    
                    -- Apply fix or nullify
                    if hasValidUsername then
                        set service name of sp to "\(normalizedService)"
                        set user name of sp to usr
                    else
                        set service name of sp to ""
                        set user name of sp to ""
                        set url of sp to ""
                    end if
                    exit repeat
                end if
            end repeat
            save
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    task.standardOutput = FileHandle.nullDevice
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
        return task.terminationStatus == 0
    } catch {}
    return false
}

// Helper to remove social profile via AppleScript (nullifies fields since delete isn't supported)
func removeSocialProfileViaAppleScript(firstName: String, lastName: String, service: String) -> Bool {
    let escapedFirst = firstName.replacingOccurrences(of: "\"", with: "\\\"")
    let escapedLast = lastName.replacingOccurrences(of: "\"", with: "\\\"")
    let normalizedService = normalizeServiceName(service)
    
    let script = """
    tell application "Contacts"
        try
            set thePerson to first person whose first name is "\(escapedFirst)" and last name is "\(escapedLast)"
            repeat with sp in social profiles of thePerson
                if service name of sp is "\(normalizedService)" then
                    set service name of sp to ""
                    set user name of sp to ""
                    set url of sp to ""
                end if
            end repeat
            save
        end try
    end tell
    """
    
    let task = Process()
    task.launchPath = "/usr/bin/osascript"
    task.arguments = ["-e", script]
    task.standardOutput = FileHandle.nullDevice
    task.standardError = FileHandle.nullDevice
    
    do {
        try task.run()
        task.waitUntilExit()
        return task.terminationStatus == 0
    } catch {}
    return false
}

// Helper to convert contact to dictionary
func contactToDict(_ contact: CNContact) -> [String: Any] {
    var dict: [String: Any] = [
        "id": contact.identifier,
        "firstName": contact.givenName,
        "lastName": contact.familyName
    ]
    
    if !contact.middleName.isEmpty { dict["middleName"] = contact.middleName }
    if !contact.nickname.isEmpty { dict["nickname"] = contact.nickname }
    if !contact.organizationName.isEmpty { dict["organization"] = contact.organizationName }
    if !contact.jobTitle.isEmpty { dict["jobTitle"] = contact.jobTitle }
    if !contact.departmentName.isEmpty { dict["department"] = contact.departmentName }
    
    // Note field - use AppleScript since Contacts framework is buggy with notes
    let note = getNoteViaAppleScript(firstName: contact.givenName, lastName: contact.familyName)
    dict["note"] = note
    
    // Social profiles - use AppleScript since Contacts framework is buggy
    let socialProfiles = getSocialProfilesViaAppleScript(firstName: contact.givenName, lastName: contact.familyName)
    if !socialProfiles.isEmpty {
        dict["socialProfiles"] = socialProfiles
    }
    
    if !contact.phoneNumbers.isEmpty {
        dict["phones"] = contact.phoneNumbers.map { phone in
            [
                "label": CNLabeledValue<NSString>.localizedString(forLabel: phone.label ?? ""),
                "number": phone.value.stringValue
            ]
        }
    }
    
    if !contact.emailAddresses.isEmpty {
        dict["emails"] = contact.emailAddresses.map { email in
            [
                "label": CNLabeledValue<NSString>.localizedString(forLabel: email.label ?? ""),
                "address": email.value as String
            ]
        }
    }
    
    // Birthday field requires explicit key fetch - check if available
    if contact.isKeyAvailable(CNContactBirthdayKey), let birthday = contact.birthday {
        var bday: [String: Int] = [:]
        if let year = birthday.year { bday["year"] = year }
        if let month = birthday.month { bday["month"] = month }
        if let day = birthday.day { bday["day"] = day }
        dict["birthday"] = bday
    }
    
    return dict
}

// Parse phone label
func parsePhoneLabel(_ label: String) -> String {
    switch label.lowercased() {
    case "mobile", "cell": return CNLabelPhoneNumberMobile
    case "home": return CNLabelHome
    case "work": return CNLabelWork
    case "main": return CNLabelPhoneNumberMain
    case "iphone": return CNLabelPhoneNumberiPhone
    default: return CNLabelOther
    }
}

// Parse email label
func parseEmailLabel(_ label: String) -> String {
    switch label.lowercased() {
    case "home": return CNLabelHome
    case "work": return CNLabelWork
    case "icloud": return CNLabelEmailiCloud
    default: return CNLabelOther
    }
}

// Get command from arguments
guard CommandLine.arguments.count > 1 else {
    print("""
    Usage: swift contacts.swift <command> [arguments...]
    
    Commands:
      add     - Add a new contact
      update  - Update an existing contact
      search  - Search for contacts (returns JSON)
    
    Examples:
      swift contacts.swift add --first "John" --last "Doe" --phone "+15125551234" --phone-label "mobile"
      swift contacts.swift add --first "Jane" --last "Smith" --social "instagram:janesmith"
      swift contacts.swift update --id "ABC123" --organization "New Company"
      swift contacts.swift update --id "ABC123" --social "linkedin:johndoe"
      swift contacts.swift update --id "ABC123" --remove-social "INSTAGRAM"
      swift contacts.swift update --id "ABC123" --fix-social "instagram"
      swift contacts.swift search --name "John"
      swift contacts.swift search --phone "5551234"
    """)
    exit(1)
}

let command = CommandLine.arguments[1]
let args = Array(CommandLine.arguments.dropFirst(2))

// Parse key-value arguments
var argDict: [String: String] = [:]
var i = 0
while i < args.count {
    if args[i].hasPrefix("--") {
        let key = String(args[i].dropFirst(2))
        if i + 1 < args.count && !args[i + 1].hasPrefix("--") {
            argDict[key] = args[i + 1]
            i += 2
        } else {
            argDict[key] = "true"
            i += 1
        }
    } else {
        i += 1
    }
}

switch command {
case "add":
    // Required: at least first name, last name, or organization
    guard argDict["first"] != nil || argDict["last"] != nil || argDict["organization"] != nil else {
        fputs("Error: At least --first, --last, or --organization is required\n", stderr)
        fputs("Usage: swift contacts.swift add --first \"John\" --last \"Doe\" [options]\n", stderr)
        fputs("\nOptions:\n", stderr)
        fputs("  --first <name>         First name\n", stderr)
        fputs("  --last <name>          Last name\n", stderr)
        fputs("  --middle <name>        Middle name\n", stderr)
        fputs("  --nickname <name>      Nickname\n", stderr)
        fputs("  --organization <name>  Company/organization\n", stderr)
        fputs("  --job-title <title>    Job title\n", stderr)
        fputs("  --department <name>    Department\n", stderr)
        fputs("  --phone <number>       Phone number\n", stderr)
        fputs("  --phone-label <label>  Phone label (mobile, home, work, main, iphone)\n", stderr)
        fputs("  --email <address>      Email address\n", stderr)
        fputs("  --email-label <label>  Email label (home, work, icloud)\n", stderr)
        fputs("  --note <text>          Notes\n", stderr)
        fputs("  --social <svc:user>    Social profile (e.g., instagram:username, linkedin:johndoe)\n", stderr)
        exit(1)
    }
    
    let contact = CNMutableContact()
    
    if let first = argDict["first"] { contact.givenName = first }
    if let last = argDict["last"] { contact.familyName = last }
    if let middle = argDict["middle"] { contact.middleName = middle }
    if let nickname = argDict["nickname"] { contact.nickname = nickname }
    if let org = argDict["organization"] { contact.organizationName = org }
    if let jobTitle = argDict["job-title"] { contact.jobTitle = jobTitle }
    if let dept = argDict["department"] { contact.departmentName = dept }
    if let note = argDict["note"] { contact.note = note }
    
    if let phone = argDict["phone"] {
        let label = argDict["phone-label"] ?? "mobile"
        contact.phoneNumbers = [CNLabeledValue(label: parsePhoneLabel(label), value: CNPhoneNumber(stringValue: phone))]
    }
    
    if let email = argDict["email"] {
        let label = argDict["email-label"] ?? "home"
        contact.emailAddresses = [CNLabeledValue(label: parseEmailLabel(label), value: email as NSString)]
    }
    
    let saveRequest = CNSaveRequest()
    saveRequest.add(contact, toContainerWithIdentifier: nil)
    
    do {
        try contactStore.execute(saveRequest)
        
        // Add social profile after contact is saved (AppleScript needs contact to exist)
        if let social = argDict["social"] {
            let parts = social.components(separatedBy: ":")
            if parts.count >= 2 {
                let service = parts[0]
                let username = parts.dropFirst().joined(separator: ":")
                _ = upsertSocialProfileViaAppleScript(firstName: contact.givenName, lastName: contact.familyName, service: service, username: username)
            }
        }
        
        let name = [contact.givenName, contact.familyName].filter { !$0.isEmpty }.joined(separator: " ")
        let displayName = name.isEmpty ? contact.organizationName : name
        outputJSON([
            "success": true,
            "message": "Contact '\(displayName)' created",
            "id": contact.identifier,
            "contact": contactToDict(contact)
        ])
    } catch {
        outputJSON(["success": false, "error": error.localizedDescription])
        exit(1)
    }
    
case "update":
    // Required: contact ID
    guard let contactId = argDict["id"] else {
        fputs("Error: --id is required for update\n", stderr)
        fputs("Usage: swift contacts.swift update --id \"CONTACT_ID\" [options]\n", stderr)
        fputs("Use 'search' command to find contact IDs\n", stderr)
        exit(1)
    }
    
    // Fetch contact with all necessary keys including URLs and notes
    let keysToFetch: [CNKeyDescriptor] = [
        CNContactIdentifierKey as CNKeyDescriptor,
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactMiddleNameKey as CNKeyDescriptor,
        CNContactNicknameKey as CNKeyDescriptor,
        CNContactOrganizationNameKey as CNKeyDescriptor,
        CNContactJobTitleKey as CNKeyDescriptor,
        CNContactDepartmentNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor,
        CNContactEmailAddressesKey as CNKeyDescriptor,
        CNContactNoteKey as CNKeyDescriptor
    ]
    
    // Handle social profile update via AppleScript (Contacts framework has bugs)
    if let social = argDict["social"] {
        // First get the contact to find its name
        guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
            outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
            exit(1)
        }
        
        let firstName = existingContact.givenName
        let lastName = existingContact.familyName
        
        let parts = social.components(separatedBy: ":")
        if parts.count >= 2 {
            let service = parts[0]
            let username = parts.dropFirst().joined(separator: ":")
            
            if upsertSocialProfileViaAppleScript(firstName: firstName, lastName: lastName, service: service, username: username) {
                // Continue to handle other updates if present
                if argDict["note"] == nil && argDict["first"] == nil && argDict["last"] == nil &&
                   argDict["organization"] == nil && argDict["phone"] == nil && argDict["email"] == nil {
                    let name = [firstName, lastName].filter { !$0.isEmpty }.joined(separator: " ")
                    let displayName = name.isEmpty ? existingContact.organizationName : name
                    outputJSON([
                        "success": true,
                        "message": "Social profile updated for '\(displayName)'",
                        "contact": contactToDict(existingContact)
                    ])
                    exit(0)
                }
            } else {
                outputJSON(["success": false, "error": "Failed to add social profile via AppleScript"])
                exit(1)
            }
        } else {
            outputJSON(["success": false, "error": "Invalid --social format. Use: service:username (e.g., instagram:johndoe)"])
            exit(1)
        }
    }
    
    // Handle social profile removal via AppleScript (nullifies fields since delete isn't supported)
    if let removeService = argDict["remove-social"] {
        guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
            outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
            exit(1)
        }
        
        let firstName = existingContact.givenName
        let lastName = existingContact.familyName
        
        if removeSocialProfileViaAppleScript(firstName: firstName, lastName: lastName, service: removeService) {
            // If no other updates, return success
            if argDict["note"] == nil && argDict["first"] == nil && argDict["last"] == nil &&
               argDict["organization"] == nil && argDict["phone"] == nil && argDict["email"] == nil && argDict["social"] == nil {
                let name = [firstName, lastName].filter { !$0.isEmpty }.joined(separator: " ")
                let displayName = name.isEmpty ? existingContact.organizationName : name
                outputJSON([
                    "success": true,
                    "message": "Social profile '\(removeService)' removed from '\(displayName)'",
                    "contact": contactToDict(existingContact)
                ])
                exit(0)
            }
        } else {
            outputJSON(["success": false, "error": "Failed to remove social profile '\(removeService)' - may not exist or AppleScript error"])
            exit(1)
        }
    }
    
    // Handle social profile fix via AppleScript (auto-extracts username from URL, normalizes service name)
    if let fixService = argDict["fix-social"] {
        guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
            outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
            exit(1)
        }
        
        let firstName = existingContact.givenName
        let lastName = existingContact.familyName
        
        if fixSocialProfileViaAppleScript(firstName: firstName, lastName: lastName, service: fixService) {
            let name = [firstName, lastName].filter { !$0.isEmpty }.joined(separator: " ")
            let displayName = name.isEmpty ? existingContact.organizationName : name
            outputJSON([
                "success": true,
                "message": "Social profile '\(fixService)' fixed for '\(displayName)'",
                "contact": contactToDict(existingContact)
            ])
            exit(0)
        } else {
            outputJSON(["success": false, "error": "Failed to fix social profile '\(fixService)'"])
            exit(1)
        }
    }
    
    // Handle note update via AppleScript (Contacts framework has bugs with notes)
    if let noteText = argDict["note"] {
        // First get the contact to find its name
        guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
            outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
            exit(1)
        }
        
        let firstName = argDict["first"] ?? existingContact.givenName
        let lastName = argDict["last"] ?? existingContact.familyName
        
        // Build the final note (handle append)
        var finalNote = noteText
        if argDict["append-note"] != nil {
            let existingNote = getNoteViaAppleScript(firstName: firstName, lastName: lastName)
            if !existingNote.isEmpty {
                finalNote = existingNote + "\n\n" + noteText
            }
        }
        
        // Update note via AppleScript
        if setNoteViaAppleScript(firstName: firstName, lastName: lastName, note: finalNote) {
            // Now update other fields if needed via Swift
            let contact = existingContact.mutableCopy() as! CNMutableContact
            
            if let first = argDict["first"] { contact.givenName = first }
            if let last = argDict["last"] { contact.familyName = last }
            if let middle = argDict["middle"] { contact.middleName = middle }
            if let nickname = argDict["nickname"] { contact.nickname = nickname }
            if let org = argDict["organization"] { contact.organizationName = org }
            if let jobTitle = argDict["job-title"] { contact.jobTitle = jobTitle }
            if let dept = argDict["department"] { contact.departmentName = dept }
            
            if let phone = argDict["phone"] {
                let label = argDict["phone-label"] ?? "mobile"
                let newPhone = CNLabeledValue(label: parsePhoneLabel(label), value: CNPhoneNumber(stringValue: phone))
                if argDict["replace-phones"] != nil {
                    contact.phoneNumbers = [newPhone]
                } else {
                    contact.phoneNumbers.append(newPhone)
                }
            }
            
            if let email = argDict["email"] {
                let label = argDict["email-label"] ?? "home"
                let newEmail = CNLabeledValue(label: parseEmailLabel(label), value: email as NSString)
                if argDict["replace-emails"] != nil {
                    contact.emailAddresses = [newEmail]
                } else {
                    contact.emailAddresses.append(newEmail)
                }
            }
            
            // Save other fields via Swift
            let saveRequest = CNSaveRequest()
            saveRequest.update(contact)
            do {
                try contactStore.execute(saveRequest)
            } catch {
                // Note was saved, other fields might have failed
            }
            
            // Auto-fix any corrupted social profiles
            autoFixAllSocialProfilesViaAppleScript(firstName: contact.givenName, lastName: contact.familyName)
            let name = [contact.givenName, contact.familyName].filter { !$0.isEmpty }.joined(separator: " ")
            let displayName = name.isEmpty ? contact.organizationName : name
            outputJSON([
                "success": true,
                "message": "Contact '\(displayName)' updated",
                "contact": contactToDict(contact)
            ])
            exit(0)
        } else {
            outputJSON(["success": false, "error": "Failed to update note via AppleScript"])
            exit(1)
        }
    }
    
    // No note update - use standard path
    guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
        outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
        exit(1)
    }
    
    let contact = existingContact.mutableCopy() as! CNMutableContact
    
    // Update basic fields
    if let first = argDict["first"] { contact.givenName = first }
    if let last = argDict["last"] { contact.familyName = last }
    if let middle = argDict["middle"] { contact.middleName = middle }
    if let nickname = argDict["nickname"] { contact.nickname = nickname }
    if let org = argDict["organization"] { contact.organizationName = org }
    if let jobTitle = argDict["job-title"] { contact.jobTitle = jobTitle }
    if let dept = argDict["department"] { contact.departmentName = dept }
    
    // For phone/email/URL updates, we add to existing (use --replace-phones, --replace-emails, --replace-urls to replace)
    if let phone = argDict["phone"] {
        let label = argDict["phone-label"] ?? "mobile"
        let newPhone = CNLabeledValue(label: parsePhoneLabel(label), value: CNPhoneNumber(stringValue: phone))
        if argDict["replace-phones"] != nil {
            contact.phoneNumbers = [newPhone]
        } else {
            contact.phoneNumbers.append(newPhone)
        }
    }
    
    if let email = argDict["email"] {
        let label = argDict["email-label"] ?? "home"
        let newEmail = CNLabeledValue(label: parseEmailLabel(label), value: email as NSString)
        if argDict["replace-emails"] != nil {
            contact.emailAddresses = [newEmail]
        } else {
            contact.emailAddresses.append(newEmail)
        }
    }
    
    let saveRequest = CNSaveRequest()
    saveRequest.update(contact)
    
    do {
        try contactStore.execute(saveRequest)
        // Auto-fix any corrupted social profiles
        autoFixAllSocialProfilesViaAppleScript(firstName: contact.givenName, lastName: contact.familyName)
        let name = [contact.givenName, contact.familyName].filter { !$0.isEmpty }.joined(separator: " ")
        let displayName = name.isEmpty ? contact.organizationName : name
        outputJSON([
            "success": true,
            "message": "Contact '\(displayName)' updated",
            "contact": contactToDict(contact)
        ])
    } catch {
        outputJSON(["success": false, "error": error.localizedDescription])
        exit(1)
    }
    
case "search":
    guard argDict["name"] != nil || argDict["phone"] != nil else {
        fputs("Error: --name or --phone is required for search\n", stderr)
        fputs("Usage: swift contacts.swift search --name \"John\" OR --phone \"5551234\"\n", stderr)
        exit(1)
    }
    
    var contacts: [CNContact] = []
    
    if let name = argDict["name"] {
        contacts = findContacts(query: name, byPhone: false)
    } else if let phone = argDict["phone"] {
        contacts = findContacts(query: phone, byPhone: true)
    }
    
    let results = contacts.map { contactToDict($0) }
    outputJSON(["count": results.count, "contacts": results])
    
default:
    fputs("Unknown command: \(command)\n", stderr)
    fputs("Available commands: add, update, search\n", stderr)
    exit(1)
}
