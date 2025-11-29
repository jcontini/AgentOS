#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contacts CLI - CRUD interface for macOS Contacts.app

Usage:
    contacts.py search <query>
    contacts.py search --phone <digits>
    contacts.py get <id>
    contacts.py create --first <name> [--last <name>] [--org <name>] ...
    contacts.py update <id> --field <value> ...
    contacts.py fix [<id> | --all]
    
    contacts.py phone add <id> <number> [<label>]
    contacts.py phone remove <id> <number>
    contacts.py email add <id> <address> [<label>]
    contacts.py email remove <id> <address>
    contacts.py url add <id> <url> [<label>]
    contacts.py url remove <id> <url>
    contacts.py social add <id> <service> <username>
    contacts.py social remove <id> <service>

Reads use SQLite (fast). Writes use AppleScript (reliable, syncs with iCloud).
"""

import argparse
import glob
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

# =============================================================================
# Dataclasses (Schema)
# =============================================================================

@dataclass
class Phone:
    number: str
    label: str = "mobile"

@dataclass
class Email:
    address: str
    label: str = "home"

@dataclass
class Social:
    service: str
    username: str

@dataclass
class URL:
    url: str
    label: str = "homepage"

@dataclass
class Contact:
    id: str = ""
    firstName: str = ""
    lastName: str = ""
    middleName: str = ""
    nickname: str = ""
    organization: str = ""
    jobTitle: str = ""
    department: str = ""
    note: str = ""
    phones: list[Phone] = field(default_factory=list)
    emails: list[Email] = field(default_factory=list)
    urls: list[URL] = field(default_factory=list)
    socials: list[Social] = field(default_factory=list)

# =============================================================================
# Social Service Normalization
# =============================================================================

# Apple-official social services - these get native "View Profile" actions in Contacts.app
# See: /System/Library/Frameworks/Contacts.framework/.../CNSocialProfile.h
# For everything else (GitHub, Instagram, etc.), use URLs instead - they're clickable!
SOCIAL_SERVICES = {
    "facebook": {"name": "Facebook", "url": "https://www.facebook.com/"},
    "flickr": {"name": "Flickr", "url": "https://www.flickr.com/people/"},
    "linkedin": {"name": "LinkedIn", "url": "https://www.linkedin.com/in/"},
    "myspace": {"name": "MySpace", "url": "https://myspace.com/"},
    "sinaweibo": {"name": "SinaWeibo", "url": "https://weibo.com/"},
    "tencentweibo": {"name": "TencentWeibo", "url": ""},
    "twitter": {"name": "Twitter", "url": "https://twitter.com/"},
    "x": {"name": "Twitter", "url": "https://twitter.com/"},  # Alias
    "yelp": {"name": "Yelp", "url": "https://www.yelp.com/user_details?userid="},
    "gamecenter": {"name": "GameCenter", "url": ""},
}

# URL templates for non-Apple services - use `url add` command with these
URL_TEMPLATES = {
    "github": "https://github.com/",
    "gitlab": "https://gitlab.com/",
    "instagram": "https://www.instagram.com/",
    "tiktok": "https://www.tiktok.com/@",
    "youtube": "https://www.youtube.com/@",
    "threads": "https://www.threads.net/@",
    "bluesky": "https://bsky.app/profile/",
    "mastodon": "https://mastodon.social/@",
    "keybase": "https://keybase.io/",
    "angellist": "https://angel.co/u/",
    "producthunt": "https://www.producthunt.com/@",
    "pinterest": "https://www.pinterest.com/",
    "quora": "https://www.quora.com/profile/",
    "medium": "https://medium.com/@",
    "reddit": "https://www.reddit.com/user/",
    "snapchat": "https://www.snapchat.com/add/",
    "twitch": "https://www.twitch.tv/",
    "telegram": "https://t.me/",
}

def get_service_info(service: str) -> dict:
    """Get service info by name (case-insensitive)."""
    return SOCIAL_SERVICES.get(service.lower(), {})

def normalize_service(service: str) -> str:
    """Normalize service name to proper case (instagram -> Instagram)."""
    info = get_service_info(service)
    return info.get("name", service.capitalize())

def get_service_url_template(service: str) -> str:
    """Get URL template for a service."""
    info = get_service_info(service)
    return info.get("url", "")

def get_service_domain(service: str) -> str:
    """Extract domain from URL template."""
    url = get_service_url_template(service)
    if not url:
        return ""
    # Extract domain from URL like "https://www.instagram.com/" -> "instagram.com"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

# =============================================================================
# SQLite Queries (READ)
# =============================================================================

def get_contact_databases() -> list[str]:
    """Find all AddressBook databases across contact sources."""
    pattern = os.path.expanduser(
        "~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb"
    )
    return glob.glob(pattern)

def query_contacts(sql: str, params: tuple = ()) -> list[dict]:
    """Query all contact databases and aggregate results."""
    results = []
    for db_path in get_contact_databases():
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            for row in cursor:
                results.append(dict(row))
            conn.close()
        except sqlite3.Error:
            continue
    return results

def search_by_name(query: str) -> list[dict]:
    """Search contacts by name or organization."""
    sql = """
        SELECT DISTINCT
            r.ZUNIQUEID as id,
            r.ZFIRSTNAME as firstName,
            r.ZLASTNAME as lastName,
            r.ZORGANIZATION as organization,
            r.ZJOBTITLE as jobTitle
        FROM ZABCDRECORD r
        WHERE r.ZFIRSTNAME LIKE ? 
           OR r.ZLASTNAME LIKE ?
           OR r.ZORGANIZATION LIKE ?
           OR (r.ZFIRSTNAME || ' ' || r.ZLASTNAME) LIKE ?
        LIMIT 50
    """
    pattern = f"%{query}%"
    return query_contacts(sql, (pattern, pattern, pattern, pattern))

def search_by_phone(digits: str) -> list[dict]:
    """Search contacts by phone number (last 4+ digits)."""
    # Use last 4 digits for indexed lookup
    last_four = digits[-4:] if len(digits) >= 4 else digits
    sql = """
        SELECT DISTINCT
            r.ZUNIQUEID as id,
            r.ZFIRSTNAME as firstName,
            r.ZLASTNAME as lastName,
            r.ZORGANIZATION as organization,
            p.ZFULLNUMBER as phone
        FROM ZABCDRECORD r
        JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
        WHERE p.ZLASTFOURDIGITS = ?
        LIMIT 20
    """
    return query_contacts(sql, (last_four,))

def get_contact_details(contact_id: str) -> Optional[dict]:
    """Get full contact details by ID using AppleScript (ensures consistency after writes)."""
    # First get name from SQLite (fast lookup to find the contact)
    sql = """
        SELECT r.ZFIRSTNAME as firstName, r.ZLASTNAME as lastName
        FROM ZABCDRECORD r WHERE r.ZUNIQUEID = ?
    """
    results = query_contacts(sql, (contact_id,))
    if not results:
        return None
    
    first = results[0].get("firstName") or ""
    last = results[0].get("lastName") or ""
    
    # Get all details via single AppleScript call (consistent, ~2s)
    # Use ||| as field delimiter, ::: as key-value delimiter
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(first)}" and last name is "{escape_applescript(last)}"
                
                set output to "firstName:::" & first name of thePerson
                set output to output & "|||lastName:::" & last name of thePerson
                
                set v to middle name of thePerson
                if v is not missing value then set output to output & "|||middleName:::" & v
                
                set v to nickname of thePerson
                if v is not missing value then set output to output & "|||nickname:::" & v
                
                set v to organization of thePerson
                if v is not missing value then set output to output & "|||organization:::" & v
                
                set v to job title of thePerson
                if v is not missing value then set output to output & "|||jobTitle:::" & v
                
                set v to department of thePerson
                if v is not missing value then set output to output & "|||department:::" & v
                
                set v to note of thePerson
                if v is not missing value then set output to output & "|||note:::" & v
                
                -- Phones: number,label;number,label;...
                set phoneList to ""
                repeat with p in phones of thePerson
                    if phoneList is not "" then set phoneList to phoneList & ";"
                    set phoneList to phoneList & value of p & "," & label of p
                end repeat
                set output to output & "|||phones:::" & phoneList
                
                -- Emails: address,label;address,label;...
                set emailList to ""
                repeat with e in emails of thePerson
                    if emailList is not "" then set emailList to emailList & ";"
                    set emailList to emailList & value of e & "," & label of e
                end repeat
                set output to output & "|||emails:::" & emailList
                
                -- URLs: url,label;url,label;...
                set urlList to ""
                repeat with u in urls of thePerson
                    if urlList is not "" then set urlList to urlList & ";"
                    set urlList to urlList & value of u & "," & label of u
                end repeat
                set output to output & "|||urls:::" & urlList
                
                -- Socials: service,username;service,username;...
                set socialList to ""
                repeat with sp in social profiles of thePerson
                    set userName to user name of sp
                    if userName is not missing value and userName is not "" then
                        if socialList is not "" then set socialList to socialList & ";"
                        set socialList to socialList & service name of sp & "," & userName
                    end if
                end repeat
                set output to output & "|||socials:::" & socialList
                
                return output
            on error errMsg
                return "error:::" & errMsg
            end try
        end tell
    '''
    
    success, output = run_applescript(script)
    if not success or not output:
        return None
    
    # Parse delimiter-based output
    contact = {"id": contact_id}
    
    if output.startswith("error:::"):
        return {"id": contact_id, "error": output[8:]}
    
    for field in output.split("|||"):
        if ":::" not in field:
            continue
        key, value = field.split(":::", 1)
        
        if key == "phones":
            contact["phones"] = []
            if value:
                for item in value.split(";"):
                    if "," in item:
                        number, label = item.rsplit(",", 1)
                        contact["phones"].append({"number": number, "label": label})
        elif key == "emails":
            contact["emails"] = []
            if value:
                for item in value.split(";"):
                    if "," in item:
                        address, label = item.rsplit(",", 1)
                        contact["emails"].append({"address": address, "label": label})
        elif key == "urls":
            contact["urls"] = []
            if value:
                for item in value.split(";"):
                    if "," in item:
                        url, label = item.rsplit(",", 1)
                        contact["urls"].append({"url": url, "label": label})
        elif key == "socials":
            contact["socials"] = []
            if value:
                for item in value.split(";"):
                    if "," in item:
                        service, username = item.split(",", 1)
                        contact["socials"].append({"service": service, "username": username})
        else:
            contact[key] = value
    
    return contact

# =============================================================================
# AppleScript Helpers
# =============================================================================

def run_applescript(script: str) -> tuple[bool, str]:
    """Run AppleScript and return (success, output)."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout.strip()

def escape_applescript(s: str) -> str:
    """Escape string for AppleScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

def get_note_applescript(first: str, last: str) -> str:
    """Get contact note via AppleScript."""
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(first)}" and last name is "{escape_applescript(last)}"
                return note of thePerson
            on error
                return ""
            end try
        end tell
    '''
    success, output = run_applescript(script)
    return "" if output == "missing value" else output

def get_socials_applescript(first: str, last: str) -> list[dict]:
    """Get social profiles via AppleScript."""
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(first)}" and last name is "{escape_applescript(last)}"
                set profileList to ""
                repeat with sp in social profiles of thePerson
                    set serviceName to service name of sp
                    set userName to user name of sp
                    if userName is not missing value and userName is not "" then
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
    '''
    success, output = run_applescript(script)
    if not output:
        return []
    
    socials = []
    for item in output.split("|||"):
        if ":::" in item:
            service, username = item.split(":::", 1)
            socials.append({"service": service.strip(), "username": username.strip()})
    return socials

# =============================================================================
# AppleScript Commands (WRITE)
# =============================================================================

def create_contact_applescript(contact: Contact) -> tuple[bool, str]:
    """Create a new contact via AppleScript."""
    props = []
    if contact.firstName:
        props.append(f'first name:"{escape_applescript(contact.firstName)}"')
    if contact.lastName:
        props.append(f'last name:"{escape_applescript(contact.lastName)}"')
    if contact.middleName:
        props.append(f'middle name:"{escape_applescript(contact.middleName)}"')
    if contact.nickname:
        props.append(f'nickname:"{escape_applescript(contact.nickname)}"')
    if contact.organization:
        props.append(f'organization:"{escape_applescript(contact.organization)}"')
    if contact.jobTitle:
        props.append(f'job title:"{escape_applescript(contact.jobTitle)}"')
    if contact.department:
        props.append(f'department:"{escape_applescript(contact.department)}"')
    if contact.note:
        props.append(f'note:"{escape_applescript(contact.note)}"')
    
    props_str = ", ".join(props)
    
    # Build phone additions
    phone_cmds = ""
    for phone in contact.phones:
        label = phone.label if isinstance(phone, Phone) else phone.get("label", "mobile")
        number = phone.number if isinstance(phone, Phone) else phone.get("number", "")
        phone_cmds += f'''
            make new phone at end of phones of newPerson with properties {{label:"{label}", value:"{escape_applescript(number)}"}}
        '''
    
    # Build email additions
    email_cmds = ""
    for email in contact.emails:
        label = email.label if isinstance(email, Email) else email.get("label", "home")
        address = email.address if isinstance(email, Email) else email.get("address", "")
        email_cmds += f'''
            make new email at end of emails of newPerson with properties {{label:"{label}", value:"{escape_applescript(address)}"}}
        '''
    
    # Build social profile additions
    social_cmds = ""
    for social in contact.socials:
        service = social.service if isinstance(social, Social) else social.get("service", "")
        username = social.username if isinstance(social, Social) else social.get("username", "")
        service = normalize_service(service)
        social_cmds += f'''
            make new social profile at end of social profiles of newPerson with properties {{service name:"{service}", user name:"{escape_applescript(username)}"}}
        '''
    
    script = f'''
        tell application "Contacts"
            set newPerson to make new person with properties {{{props_str}}}
            {phone_cmds}
            {email_cmds}
            {social_cmds}
            save
            return id of newPerson
        end tell
    '''
    return run_applescript(script)

def update_contact_applescript(contact_id: str, updates: dict) -> tuple[bool, str]:
    """Update contact fields via AppleScript."""
    # First get current name for lookup
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    first = contact.get("firstName", "")
    last = contact.get("lastName", "")
    
    set_cmds = []
    if "firstName" in updates:
        set_cmds.append(f'set first name of thePerson to "{escape_applescript(updates["firstName"])}"')
    if "lastName" in updates:
        set_cmds.append(f'set last name of thePerson to "{escape_applescript(updates["lastName"])}"')
    if "middleName" in updates:
        set_cmds.append(f'set middle name of thePerson to "{escape_applescript(updates["middleName"])}"')
    if "nickname" in updates:
        set_cmds.append(f'set nickname of thePerson to "{escape_applescript(updates["nickname"])}"')
    if "organization" in updates:
        set_cmds.append(f'set organization of thePerson to "{escape_applescript(updates["organization"])}"')
    if "jobTitle" in updates:
        set_cmds.append(f'set job title of thePerson to "{escape_applescript(updates["jobTitle"])}"')
    if "department" in updates:
        set_cmds.append(f'set department of thePerson to "{escape_applescript(updates["department"])}"')
    if "note" in updates:
        set_cmds.append(f'set note of thePerson to "{escape_applescript(updates["note"])}"')
    
    if not set_cmds:
        return True, "Nothing to update"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(first)}" and last name is "{escape_applescript(last)}"
                {chr(10).join(set_cmds)}
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def add_phone_applescript(contact_id: str, phone: Phone) -> tuple[bool, str]:
    """Add phone to contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                make new phone at end of phones of thePerson with properties {{label:"{phone.label}", value:"{escape_applescript(phone.number)}"}}
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def remove_phone_applescript(contact_id: str, number: str) -> tuple[bool, str]:
    """Remove phone from contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    # Normalize number for comparison (remove non-digits)
    normalized = ''.join(c for c in number if c.isdigit())
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set phoneCount to count of phones of thePerson
                repeat with i from phoneCount to 1 by -1
                    set p to phone i of thePerson
                    set phoneVal to value of p
                    set phoneDigits to do shell script "echo " & quoted form of phoneVal & " | tr -cd '0-9'"
                    if phoneDigits contains "{normalized}" or "{normalized}" contains phoneDigits then
                        delete phone i of thePerson
                        exit repeat
                    end if
                end repeat
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def add_email_applescript(contact_id: str, email: Email) -> tuple[bool, str]:
    """Add email to contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                make new email at end of emails of thePerson with properties {{label:"{email.label}", value:"{escape_applescript(email.address)}"}}
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def remove_email_applescript(contact_id: str, address: str) -> tuple[bool, str]:
    """Remove email from contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set emailCount to count of emails of thePerson
                repeat with i from emailCount to 1 by -1
                    set e to email i of thePerson
                    if value of e is "{escape_applescript(address)}" then
                        delete email i of thePerson
                        exit repeat
                    end if
                end repeat
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def add_url_applescript(contact_id: str, url_obj: URL) -> tuple[bool, str]:
    """Add URL to contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                make new url at end of urls of thePerson with properties {{label:"{escape_applescript(url_obj.label)}", value:"{escape_applescript(url_obj.url)}"}}
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def remove_url_applescript(contact_id: str, url: str) -> tuple[bool, str]:
    """Remove URL from contact via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set urlCount to count of urls of thePerson
                repeat with i from urlCount to 1 by -1
                    set u to url i of thePerson
                    if value of u contains "{escape_applescript(url)}" then
                        delete url i of thePerson
                        exit repeat
                    end if
                end repeat
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def add_social_applescript(contact_id: str, social: Social) -> tuple[bool, str]:
    """Add or update social profile via AppleScript."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    service = normalize_service(social.service)
    
    # Upsert: update if exists, add if not
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set didUpdate to false
                repeat with sp in social profiles of thePerson
                    if service name of sp is "{service}" then
                        set user name of sp to "{escape_applescript(social.username)}"
                        set didUpdate to true
                        exit repeat
                    end if
                end repeat
                if not didUpdate then
                    make new social profile at end of social profiles of thePerson with properties {{service name:"{service}", user name:"{escape_applescript(social.username)}"}}
                end if
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def remove_social_applescript(contact_id: str, service: str) -> tuple[bool, str]:
    """Remove social profile via AppleScript (nullifies since delete not supported)."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    service = normalize_service(service)
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                repeat with sp in social profiles of thePerson
                    if service name of sp is "{service}" then
                        set service name of sp to ""
                        set user name of sp to ""
                        set url of sp to ""
                    end if
                end repeat
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

# =============================================================================
# Fix Command (Social Profile Cleanup)
# =============================================================================

def fix_contact_socials(contact_id: str) -> tuple[bool, str]:
    """Fix corrupted social profiles for a contact."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    first = contact.get("firstName", "")
    last = contact.get("lastName", "")
    
    # Build AppleScript checks from unified SOCIAL_SERVICES
    service_checks = "\n".join([
        f'if svcLower is "{key}" then\nset normalizedName to "{info["name"]}"\nset expectedDomain to "{get_service_domain(key)}"\nset urlTemplate to "{info["url"]}"\nend if'
        for key, info in SOCIAL_SERVICES.items()
    ])
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(first)}" and last name is "{escape_applescript(last)}"
                
                repeat with sp in social profiles of thePerson
                    set svc to service name of sp
                    set usr to user name of sp
                    set theUrl to url of sp
                    
                    -- Normalize service name and get domain/URL template
                    set svcLower to ""
                    set normalizedName to ""
                    set expectedDomain to ""
                    set urlTemplate to ""
                    
                    if svc is not missing value then
                        set svcLower to do shell script "echo " & quoted form of svc & " | tr '[:upper:]' '[:lower:]'"
                    end if
                    
                    {service_checks}
                    
                    -- CASE 0: Remove defunct services (Google+)
                    if svcLower contains "plus.goo" or svcLower contains "google+" or svcLower is "googleplus" then
                        set service name of sp to ""
                        set user name of sp to ""
                        set url of sp to ""
                    else
                    
                    -- CASE 1: Check if username has URL pasted into it (like "WWW.FACEBOOK.COM/PROFILE.PHP?ID=123")
                    set urlPastedAsUsername to false
                    set extractedProfileId to ""
                    if usr is not missing value and usr is not "" then
                        if usr contains "profile.php" or usr contains "facebook.com" or usr contains "http" then
                            set urlPastedAsUsername to true
                            -- Try to extract profile ID
                            if usr contains "id=" then
                                set AppleScript's text item delimiters to "id="
                                set idParts to text items of usr
                                if (count of idParts) > 1 then
                                    set extractedProfileId to item 2 of idParts
                                    -- Clean up any trailing garbage
                                    set AppleScript's text item delimiters to "&"
                                    set extractedProfileId to text item 1 of extractedProfileId
                                end if
                                set AppleScript's text item delimiters to ""
                            end if
                        end if
                    end if
                    
                    if urlPastedAsUsername then
                        -- Fix the pasted URL: clear username, set proper URL
                        if extractedProfileId is not "" then
                            set user name of sp to ""
                            set url of sp to "https://www.facebook.com/profile.php?id=" & extractedProfileId
                            if normalizedName is not "" then
                                set service name of sp to normalizedName
                            end if
                        else
                            -- Can't recover, nullify
                            set service name of sp to ""
                            set user name of sp to ""
                            set url of sp to ""
                        end if
                    else
                        -- CASE 2: Normal processing
                        -- Check if username is garbage
                        set hasValidUsername to false
                        if usr is not missing value and usr is not "" and usr is not "TYPE=PREF" then
                            -- Username is garbage if:
                            -- 1. It's a substring of the expected domain (like "facebook" in "facebook.com")
                            -- 2. It looks like a domain itself (contains www, .com, .org, etc)
                            set usrLower to do shell script "echo " & quoted form of usr & " | tr '[:upper:]' '[:lower:]'"
                            set looksLikeDomain to false
                            if usrLower contains "www." or usrLower contains ".com" or usrLower contains ".org" or usrLower contains "facebook.com" or usrLower contains "twitter.com" or usrLower contains "linkedin.com" or usrLower contains "instagram.com" then
                                set looksLikeDomain to true
                            end if
                            
                            if not looksLikeDomain then
                                if expectedDomain is "" or expectedDomain does not contain usrLower then
                                    set hasValidUsername to true
                                end if
                            end if
                        end if
                        
                        -- Try to extract username from URL if needed
                        if not hasValidUsername and theUrl is not missing value and theUrl is not "" then
                            set AppleScript's text item delimiters to "/"
                            set urlParts to text items of theUrl
                            set extractedUser to last item of urlParts
                            set AppleScript's text item delimiters to ""
                            if extractedUser is "" and (count of urlParts) > 1 then
                                set extractedUser to item -2 of urlParts
                            end if
                            -- Validate extracted username is not garbage
                            set extractedIsValid to false
                            if (count of extractedUser) > 2 then
                                -- Must not be domain-like (www, com, facebook, etc)
                                set extractedLower to do shell script "echo " & quoted form of extractedUser & " | tr '[:upper:]' '[:lower:]'"
                                if extractedLower is not "www" and extractedLower does not contain ".com" and extractedLower does not contain ".org" and extractedLower does not contain "facebook" and extractedLower does not contain "twitter" and extractedLower does not contain "linkedin" and extractedLower does not contain "instagram" and extractedLower does not contain "flickr" and extractedLower is not "people" and extractedLower is not "in" then
                                    set extractedIsValid to true
                                end if
                            end if
                            if extractedIsValid then
                                set usr to extractedUser
                                set hasValidUsername to true
                            end if
                        end if
                        
                        -- CASE 3: Check if URL is a profile.php URL (preserve these!)
                        set isProfilePhpUrl to false
                        if theUrl is not missing value and theUrl contains "profile.php?id=" then
                            set isProfilePhpUrl to true
                        end if
                        
                        -- Apply fix or nullify
                        if not hasValidUsername and not isProfilePhpUrl then
                            -- No valid username and no profile.php URL - nullify
                            set service name of sp to ""
                            set user name of sp to ""
                            set url of sp to ""
                        else if isProfilePhpUrl then
                            -- Preserve profile.php URLs, just normalize service name
                            if normalizedName is not "" then
                                set service name of sp to normalizedName
                            end if
                        else
                            -- Has valid username - normalize to lowercase
                            set usr to do shell script "echo " & quoted form of usr & " | tr '[:upper:]' '[:lower:]'"
                            
                            if normalizedName is not "" then
                                set service name of sp to normalizedName
                            end if
                            set user name of sp to usr
                            
                            -- Check if URL needs to be constructed
                            -- (missing, corrupted, doesn't contain username, or has wrong case)
                            set needsUrl to false
                            if theUrl is missing value or theUrl is "" then
                                set needsUrl to true
                            else if expectedDomain is not "" and theUrl does not contain expectedDomain then
                                set needsUrl to true
                            else
                                -- Check if URL contains lowercase username (case-sensitive check)
                                considering case
                                    if theUrl does not contain usr then
                                        set needsUrl to true
                                    end if
                                end considering
                            end if
                            
                            if needsUrl and urlTemplate is not "" then
                                -- Construct URL from template + lowercase username
                                set url of sp to urlTemplate & usr
                            end if
                        end if
                    end if
                    end if -- end Google+ check
                end repeat
                
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)


# =============================================================================
# CLI
# =============================================================================

def output_json(data):
    """Output data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(
        description="Contacts CLI - CRUD interface for macOS Contacts.app",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # search
    search_parser = subparsers.add_parser("search", help="Search contacts")
    search_parser.add_argument("query", nargs="?", help="Name to search for")
    search_parser.add_argument("--phone", help="Search by phone number")
    
    # get
    get_parser = subparsers.add_parser("get", help="Get contact by ID")
    get_parser.add_argument("id", help="Contact ID")
    
    # create
    create_parser = subparsers.add_parser("create", help="Create a new contact")
    create_parser.add_argument("--first", help="First name")
    create_parser.add_argument("--last", help="Last name")
    create_parser.add_argument("--middle", help="Middle name")
    create_parser.add_argument("--nickname", help="Nickname")
    create_parser.add_argument("--org", help="Organization")
    create_parser.add_argument("--job-title", help="Job title")
    create_parser.add_argument("--department", help="Department")
    create_parser.add_argument("--note", help="Note")
    create_parser.add_argument("--phone", help="Phone number")
    create_parser.add_argument("--phone-label", default="mobile", help="Phone label")
    create_parser.add_argument("--email", help="Email address")
    create_parser.add_argument("--email-label", default="home", help="Email label")
    create_parser.add_argument("--social", help="Social profile (service:username)")
    
    # update
    update_parser = subparsers.add_parser("update", help="Update contact fields")
    update_parser.add_argument("id", help="Contact ID")
    update_parser.add_argument("--first", help="First name")
    update_parser.add_argument("--last", help="Last name")
    update_parser.add_argument("--middle", help="Middle name")
    update_parser.add_argument("--nickname", help="Nickname")
    update_parser.add_argument("--org", help="Organization")
    update_parser.add_argument("--job-title", help="Job title")
    update_parser.add_argument("--department", help="Department")
    update_parser.add_argument("--note", help="Note")
    
    # fix
    fix_parser = subparsers.add_parser("fix", help="Fix corrupted social profiles")
    fix_parser.add_argument("id", help="Contact ID")
    
    # phone subcommands
    phone_parser = subparsers.add_parser("phone", help="Phone operations")
    phone_sub = phone_parser.add_subparsers(dest="action", required=True)
    
    phone_add = phone_sub.add_parser("add", help="Add phone")
    phone_add.add_argument("id", help="Contact ID")
    phone_add.add_argument("number", help="Phone number")
    phone_add.add_argument("label", nargs="?", default="mobile", help="Label (mobile, home, work)")
    
    phone_remove = phone_sub.add_parser("remove", help="Remove phone")
    phone_remove.add_argument("id", help="Contact ID")
    phone_remove.add_argument("number", help="Phone number")
    
    # email subcommands
    email_parser = subparsers.add_parser("email", help="Email operations")
    email_sub = email_parser.add_subparsers(dest="action", required=True)
    
    email_add = email_sub.add_parser("add", help="Add email")
    email_add.add_argument("id", help="Contact ID")
    email_add.add_argument("address", help="Email address")
    email_add.add_argument("label", nargs="?", default="home", help="Label (home, work)")
    
    email_remove = email_sub.add_parser("remove", help="Remove email")
    email_remove.add_argument("id", help="Contact ID")
    email_remove.add_argument("address", help="Email address")
    
    # url subcommands
    url_parser = subparsers.add_parser("url", help="URL operations")
    url_sub = url_parser.add_subparsers(dest="action", required=True)
    
    url_add = url_sub.add_parser("add", help="Add URL")
    url_add.add_argument("id", help="Contact ID")
    url_add.add_argument("url", help="URL")
    url_add.add_argument("label", nargs="?", default="homepage", help="Label (GitHub, Instagram, homepage, etc.)")
    
    url_remove = url_sub.add_parser("remove", help="Remove URL")
    url_remove.add_argument("id", help="Contact ID")
    url_remove.add_argument("url", help="URL (or partial match)")
    
    # social subcommands
    social_parser = subparsers.add_parser("social", help="Social profile operations")
    social_sub = social_parser.add_subparsers(dest="action", required=True)
    
    social_add = social_sub.add_parser("add", help="Add social profile (Apple-official only: twitter, linkedin, facebook, flickr, yelp)")
    social_add.add_argument("id", help="Contact ID")
    social_add.add_argument("service", help="Service name (twitter, linkedin, facebook, flickr, yelp)")
    social_add.add_argument("username", help="Username")
    
    social_remove = social_sub.add_parser("remove", help="Remove social profile")
    social_remove.add_argument("id", help="Contact ID")
    social_remove.add_argument("service", help="Service name")
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == "search":
        if args.phone:
            results = search_by_phone(args.phone)
        elif args.query:
            results = search_by_name(args.query)
        else:
            parser.error("Provide a query or --phone")
        output_json({"count": len(results), "contacts": results})
    
    elif args.command == "get":
        contact = get_contact_details(args.id)
        if contact:
            output_json(contact)
        else:
            output_json({"error": "Contact not found"})
            sys.exit(1)
    
    elif args.command == "create":
        if not (args.first or args.last or args.org):
            parser.error("At least --first, --last, or --org is required")
        
        contact = Contact(
            firstName=args.first or "",
            lastName=args.last or "",
            middleName=args.middle or "",
            nickname=args.nickname or "",
            organization=args.org or "",
            jobTitle=args.job_title or "",
            department=args.department or "",
            note=args.note or "",
        )
        
        if args.phone:
            contact.phones.append(Phone(number=args.phone, label=args.phone_label))
        if args.email:
            contact.emails.append(Email(address=args.email, label=args.email_label))
        if args.social and ":" in args.social:
            service, username = args.social.split(":", 1)
            contact.socials.append(Social(service=service, username=username))
        
        success, result = create_contact_applescript(contact)
        if success:
            name = f"{contact.firstName} {contact.lastName}".strip() or contact.organization
            output_json({"success": True, "message": f"Created '{name}'", "id": result})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "update":
        updates = {}
        if args.first: updates["firstName"] = args.first
        if args.last: updates["lastName"] = args.last
        if args.middle: updates["middleName"] = args.middle
        if args.nickname: updates["nickname"] = args.nickname
        if args.org: updates["organization"] = args.org
        if args.job_title: updates["jobTitle"] = args.job_title
        if args.department: updates["department"] = args.department
        if args.note: updates["note"] = args.note
        
        if not updates:
            parser.error("No fields to update")
        
        success, result = update_contact_applescript(args.id, updates)
        if success:
            output_json({"success": True, "message": "Contact updated"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "fix":
        success, result = fix_contact_socials(args.id)
        if success:
            output_json({"success": True, "message": "Social profiles fixed"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "phone":
        if args.action == "add":
            phone = Phone(number=args.number, label=args.label)
            success, result = add_phone_applescript(args.id, phone)
        elif args.action == "remove":
            success, result = remove_phone_applescript(args.id, args.number)
        
        if success:
            output_json({"success": True, "message": f"Phone {'removed' if args.action == 'remove' else 'added'}"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "email":
        if args.action == "add":
            email = Email(address=args.address, label=args.label)
            success, result = add_email_applescript(args.id, email)
        elif args.action == "remove":
            success, result = remove_email_applescript(args.id, args.address)
        
        if success:
            output_json({"success": True, "message": f"Email {'removed' if args.action == 'remove' else 'added'}"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "url":
        if args.action == "add":
            url_obj = URL(url=args.url, label=args.label)
            success, result = add_url_applescript(args.id, url_obj)
        elif args.action == "remove":
            success, result = remove_url_applescript(args.id, args.url)
        
        if success:
            output_json({"success": True, "message": f"URL {'removed' if args.action == 'remove' else 'added'}"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)
    
    elif args.command == "social":
        if args.action == "add":
            social = Social(service=args.service, username=args.username)
            success, result = add_social_applescript(args.id, social)
        elif args.action == "remove":
            success, result = remove_social_applescript(args.id, args.service)
        
        if success:
            output_json({"success": True, "message": f"Social profile {'removed' if args.action == 'remove' else 'added'}"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)

if __name__ == "__main__":
    main()

