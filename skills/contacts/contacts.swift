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
    // Note field requires explicit key fetch - check if available
    if contact.isKeyAvailable(CNContactNoteKey), !contact.note.isEmpty { 
        dict["note"] = contact.note 
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
      swift contacts.swift update --id "ABC123" --organization "New Company"
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
    
    guard let existingContact = try? contactStore.unifiedContact(withIdentifier: contactId, keysToFetch: keysToFetch) else {
        outputJSON(["success": false, "error": "Contact not found with ID: \(contactId)"])
        exit(1)
    }
    
    let contact = existingContact.mutableCopy() as! CNMutableContact
    
    if let first = argDict["first"] { contact.givenName = first }
    if let last = argDict["last"] { contact.familyName = last }
    if let middle = argDict["middle"] { contact.middleName = middle }
    if let nickname = argDict["nickname"] { contact.nickname = nickname }
    if let org = argDict["organization"] { contact.organizationName = org }
    if let jobTitle = argDict["job-title"] { contact.jobTitle = jobTitle }
    if let dept = argDict["department"] { contact.departmentName = dept }
    if let note = argDict["note"] { contact.note = note }
    
    // For phone/email updates, we add to existing (use --replace-phones or --replace-emails to replace)
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

