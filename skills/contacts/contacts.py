#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contacts CLI - CRUD interface for macOS Contacts.app

Usage:
    contacts.py search <query>
    contacts.py search --phone <digits>
    contacts.py search --where "no_photo = true AND url LIKE '%instagram%'"
    contacts.py get <id>
    contacts.py create --first <name> [--last <name>] [--org <name>] ...
    contacts.py update <id> --field <value> ...
    contacts.py fix <id>
    
    contacts.py phone add <id> <number> [<label>]
    contacts.py phone remove <id> <number>
    contacts.py email add <id> <address> [<label>]
    contacts.py email remove <id> <address>
    contacts.py url add <id> <url> [<label>]
    contacts.py url remove <id> <url>
    contacts.py social add <id> <service> <username>
    contacts.py social remove <id> <service>
    contacts.py photo set <id> <url_or_path>
    contacts.py photo clear <id>

Field names for --where queries: id, firstName, lastName, middleName, nickname,
organization, jobTitle, department, photo, thumbnail, url, number, address
Virtual fields: has_photo=true/false, no_photo=true (checks both photo and thumbnail)
Phone numbers are auto-normalized to include country code (+1 for US by default).
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

def normalize_phone(number: str, default_country: str = "+1") -> str:
    """
    Normalize phone number to include country code.
    - If starts with +, keep as-is (already has country code)
    - Otherwise, strip non-digits and prepend default country code
    """
    number = number.strip()
    if number.startswith("+"):
        return number
    
    # Strip everything except digits
    digits = ''.join(c for c in number if c.isdigit())
    
    # US numbers: if 10 digits, add +1
    # If 11 digits starting with 1, add +
    if len(digits) == 10:
        return f"{default_country}{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    elif len(digits) > 10:
        # Assume already has country code, just add +
        return f"+{digits}"
    else:
        # Short number (local/extension), return as-is
        return number

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
# Schema Mapping (SQLite ↔ Our API ↔ AppleScript)
# =============================================================================
# Single source of truth for field name translations.
# Our field names are camelCase, SQLite uses Z-prefixed UPPERCASE, AppleScript uses spaces.

SCHEMA = {
    # Main contact fields (ZABCDRECORD table)
    "id":           {"sql": "ZUNIQUEID", "applescript": "id"},
    "firstName":    {"sql": "ZFIRSTNAME", "applescript": "first name"},
    "lastName":     {"sql": "ZLASTNAME", "applescript": "last name"},
    "middleName":   {"sql": "ZMIDDLENAME", "applescript": "middle name"},
    "nickname":     {"sql": "ZNICKNAME", "applescript": "nickname"},
    "organization": {"sql": "ZORGANIZATION", "applescript": "organization"},
    "jobTitle":     {"sql": "ZJOBTITLE", "applescript": "job title"},
    "department":   {"sql": "ZDEPARTMENT", "applescript": "department"},
    "photo":        {"sql": "ZIMAGEDATA", "applescript": "image"},           # Full image BLOB
    "thumbnail":    {"sql": "ZTHUMBNAILIMAGEDATA", "applescript": None},     # Thumbnail BLOB (main storage for API-set photos)
}

# Related tables (one-to-many, joined via ZOWNER → Z_PK)
SCHEMA_RELATIONS = {
    "phones": {
        "table": "ZABCDPHONENUMBER",
        "fields": {"number": "ZFULLNUMBER", "label": "ZLABEL"},
    },
    "emails": {
        "table": "ZABCDEMAILADDRESS",
        "fields": {"address": "ZADDRESS", "label": "ZLABEL"},
    },
    "urls": {
        "table": "ZABCDURLADDRESS",
        "fields": {"url": "ZURL", "label": "ZLABEL"},
    },
    "socials": {
        "table": "ZABCDSOCIALPROFILE",
        "fields": {"service": "ZSERVICENAME", "username": "ZUSERNAME"},
    },
}

def sql_column(field: str) -> str:
    """Convert our field name to SQLite column name."""
    if field in SCHEMA:
        return SCHEMA[field]["sql"]
    return field  # Pass through unknown fields

def sql_select(fields: list[str], table_alias: str = "r") -> str:
    """Generate SELECT clause: 'ZFIRSTNAME as firstName, ZLASTNAME as lastName'"""
    parts = []
    for f in fields:
        if f in SCHEMA:
            parts.append(f'{table_alias}.{SCHEMA[f]["sql"]} as {f}')
    return ", ".join(parts)

def applescript_prop(field: str) -> str:
    """Convert our field name to AppleScript property name."""
    if field in SCHEMA:
        return SCHEMA[field]["applescript"]
    return field

# =============================================================================
# Unified Social Services Registry
# =============================================================================
# 
# All social services in one place. Fields:
#   - name: Display name (required)
#   - profile_url: Profile URL template with {username} placeholder (required)
#   - photo_url: Direct avatar URL template (optional, omit if auth required)
#   - photo_api: API endpoint returning JSON with avatar (optional)
#   - apple_native: True if Apple-official social service (optional, defaults False)

SERVICES = {
    # Apple-native services (use `social add`)
    "twitter":     {"name": "Twitter", "profile_url": "https://twitter.com/{username}", "apple_native": True},
    "x":           {"name": "Twitter", "profile_url": "https://twitter.com/{username}", "apple_native": True},
    "linkedin":    {"name": "LinkedIn", "profile_url": "https://www.linkedin.com/in/{username}", "apple_native": True},
    "facebook":    {"name": "Facebook", "profile_url": "https://www.facebook.com/{username}", "photo_url": "https://graph.facebook.com/{username}/picture?type=large", "apple_native": True},
    "flickr":      {"name": "Flickr", "profile_url": "https://www.flickr.com/people/{username}", "apple_native": True},
    "myspace":     {"name": "MySpace", "profile_url": "https://myspace.com/{username}", "apple_native": True},
    "sinaweibo":   {"name": "SinaWeibo", "profile_url": "https://weibo.com/{username}", "apple_native": True},
    "tencentweibo": {"name": "TencentWeibo", "profile_url": "", "apple_native": True},
    "yelp":        {"name": "Yelp", "profile_url": "https://www.yelp.com/user_details?userid={username}", "apple_native": True},
    "gamecenter":  {"name": "GameCenter", "profile_url": "", "apple_native": True},
    
    # Non-Apple services (use `url add`)
    "github":      {"name": "GitHub", "profile_url": "https://github.com/{username}", "photo_url": "https://github.com/{username}.png", "photo_api": "https://api.github.com/users/{username}"},
    "gitlab":      {"name": "GitLab", "profile_url": "https://gitlab.com/{username}", "photo_api": "https://gitlab.com/api/v4/users?username={username}"},
    "instagram":   {"name": "Instagram", "profile_url": "https://www.instagram.com/{username}"},
    "tiktok":      {"name": "TikTok", "profile_url": "https://www.tiktok.com/@{username}"},
    "youtube":     {"name": "YouTube", "profile_url": "https://www.youtube.com/@{username}"},
    "threads":     {"name": "Threads", "profile_url": "https://www.threads.net/@{username}"},
    "bluesky":     {"name": "Bluesky", "profile_url": "https://bsky.app/profile/{username}", "photo_api": "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={username}"},
    "mastodon":    {"name": "Mastodon", "profile_url": "https://mastodon.social/@{username}"},
    "keybase":     {"name": "Keybase", "profile_url": "https://keybase.io/{username}", "photo_url": "https://keybase.io/{username}/photo.png"},
    "angellist":   {"name": "AngelList", "profile_url": "https://angel.co/u/{username}"},
    "producthunt": {"name": "ProductHunt", "profile_url": "https://www.producthunt.com/@{username}"},
    "pinterest":   {"name": "Pinterest", "profile_url": "https://www.pinterest.com/{username}"},
    "quora":       {"name": "Quora", "profile_url": "https://www.quora.com/profile/{username}"},
    "medium":      {"name": "Medium", "profile_url": "https://medium.com/@{username}"},
    "reddit":      {"name": "Reddit", "profile_url": "https://www.reddit.com/user/{username}"},
    "snapchat":    {"name": "Snapchat", "profile_url": "https://www.snapchat.com/add/{username}", "photo_url": "https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=PNG"},
    "twitch":      {"name": "Twitch", "profile_url": "https://www.twitch.tv/{username}"},
    "telegram":    {"name": "Telegram", "profile_url": "https://t.me/{username}"},
    "gravatar":    {"name": "Gravatar", "profile_url": "https://gravatar.com/{username}", "photo_url": "https://gravatar.com/avatar/{username}?s=400&d=404"},
    "goodreads":   {"name": "Goodreads", "profile_url": "https://www.goodreads.com/{username}"},
    "spotify":     {"name": "Spotify", "profile_url": "https://open.spotify.com/user/{username}"},
    "soundcloud":  {"name": "SoundCloud", "profile_url": "https://soundcloud.com/{username}"},
    "dribbble":    {"name": "Dribbble", "profile_url": "https://dribbble.com/{username}"},
    "behance":     {"name": "Behance", "profile_url": "https://www.behance.net/{username}"},
    "devto":       {"name": "DEV", "profile_url": "https://dev.to/{username}"},
    "stackoverflow": {"name": "StackOverflow", "profile_url": "https://stackoverflow.com/users/{username}"},
    "hackernews":  {"name": "HackerNews", "profile_url": "https://news.ycombinator.com/user?id={username}"},
    "discord":     {"name": "Discord", "profile_url": ""},
    "slack":       {"name": "Slack", "profile_url": ""},
    "whatsapp":    {"name": "WhatsApp", "profile_url": "https://wa.me/{username}"},
    "signal":      {"name": "Signal", "profile_url": ""},
}

# Legacy compatibility: map old SOCIAL_SERVICES lookups
SOCIAL_SERVICES = {k: {"name": v["name"], "url": v["profile_url"].replace("{username}", "")} 
                   for k, v in SERVICES.items() if v.get("apple_native")}

# Legacy compatibility: URL_TEMPLATES for non-Apple services
URL_TEMPLATES = {k: v["profile_url"].replace("{username}", "") 
                 for k, v in SERVICES.items() if not v.get("apple_native")}

# =============================================================================
# Service Helper Functions
# =============================================================================

def get_service(name: str) -> Optional[dict]:
    """Get service info by name (case-insensitive)."""
    return SERVICES.get(name.lower())

def get_service_from_url(url: str) -> Optional[tuple[str, str]]:
    """
    Extract service name and username from a profile URL.
    Returns (service_key, username) or None if not recognized.
    """
    url_lower = url.lower()
    
    for key, service in SERVICES.items():
        profile_template = service.get("profile_url", "")
        if not profile_template:
            continue
        
        # Extract domain from template
        # e.g., "https://github.com/{username}" -> "github.com"
        try:
            from urllib.parse import urlparse
            template_domain = urlparse(profile_template).netloc.replace("www.", "")
            url_domain = urlparse(url).netloc.replace("www.", "")
            
            if template_domain and template_domain in url_domain:
                # Try to extract username
                # Replace {username} with a capture pattern
                username = extract_username_from_url(url, profile_template)
                if username:
                    return (key, username)
        except:
            continue
    
    return None

def extract_username_from_url(url: str, template: str) -> Optional[str]:
    """Extract username from a URL given its template pattern."""
    import re
    
    # Convert template to regex: https://github.com/{username} -> https://github.com/(.+)
    # Escape special chars, then replace {username}
    pattern = re.escape(template).replace(r"\{username\}", r"([^/?#]+)")
    pattern = pattern.replace("https\\:", "https?\\:")  # Allow http or https
    pattern = pattern.replace("www\\.", "(www\\.)?")  # Optional www
    
    match = re.match(pattern, url, re.IGNORECASE)
    if match:
        return match.group(match.lastindex) if match.lastindex else None
    
    # Fallback: try to get last path component
    try:
        from urllib.parse import urlparse
        path = urlparse(url).path.strip("/")
        if path:
            # Handle @ prefix (twitter, tiktok, youtube, etc.)
            parts = path.split("/")
            username = parts[-1] if parts else path
            return username.lstrip("@")
    except:
        pass
    
    return None

def get_photo_url(service: str, username: str) -> Optional[str]:
    """
    Get direct photo URL for a service/username if available.
    Returns the URL template with {username} replaced, or None if not available.
    """
    svc = get_service(service)
    if not svc:
        return None
    
    photo_url = svc.get("photo_url")
    if photo_url:
        return photo_url.replace("{username}", username)
    
    return None

def get_photo_api(service: str, username: str) -> Optional[str]:
    """
    Get API endpoint to fetch photo URL for a service/username.
    Returns the API URL with {username} replaced, or None if not available.
    """
    svc = get_service(service)
    if not svc:
        return None
    
    photo_api = svc.get("photo_api")
    if photo_api:
        return photo_api.replace("{username}", username)
    
    return None

def get_profile_url(service: str, username: str) -> Optional[str]:
    """Get profile URL for a service/username."""
    svc = get_service(service)
    if not svc:
        return None
    
    profile_url = svc.get("profile_url")
    if profile_url:
        return profile_url.replace("{username}", username)
    
    return None

def is_apple_native(service: str) -> bool:
    """Check if a service is Apple-native (can use `social add`)."""
    svc = get_service(service)
    return svc.get("apple_native", False) if svc else False

def list_services_with_photos() -> list[str]:
    """List all services that have photo URL or API support."""
    return [k for k, v in SERVICES.items() 
            if v.get("photo_url") or v.get("photo_api")]

def get_service_info(service: str) -> dict:
    """Get service info by name (case-insensitive). Returns legacy format for compatibility."""
    svc = SERVICES.get(service.lower())
    if not svc:
        return {}
    # Return legacy format
    return {"name": svc["name"], "url": svc["profile_url"].replace("{username}", "")}

def normalize_service(service: str) -> str:
    """Normalize service name to proper case (instagram -> Instagram)."""
    svc = SERVICES.get(service.lower())
    return svc["name"] if svc else service.capitalize()

def get_service_url_template(service: str) -> str:
    """Get URL template for a service (without {username} placeholder)."""
    svc = SERVICES.get(service.lower())
    if not svc:
        return ""
    return svc["profile_url"].replace("{username}", "")

def get_service_domain(service: str) -> str:
    """Extract domain from service profile URL."""
    svc = SERVICES.get(service.lower())
    if not svc:
        return ""
    url = svc.get("profile_url", "")
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
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
    select_fields = sql_select(["id", "firstName", "lastName", "organization", "jobTitle"])
    sql = f"""
        SELECT DISTINCT {select_fields}
        FROM ZABCDRECORD r
        WHERE r.{sql_column("firstName")} LIKE ? 
           OR r.{sql_column("lastName")} LIKE ?
           OR r.{sql_column("organization")} LIKE ?
           OR (r.{sql_column("firstName")} || ' ' || r.{sql_column("lastName")}) LIKE ?
        LIMIT 50
    """
    pattern = f"%{query}%"
    return query_contacts(sql, (pattern, pattern, pattern, pattern))

def search_by_phone(digits: str) -> list[dict]:
    """Search contacts by phone number (last 4+ digits)."""
    # Use last 4 digits for indexed lookup
    last_four = digits[-4:] if len(digits) >= 4 else digits
    select_fields = sql_select(["id", "firstName", "lastName", "organization"])
    phone_table = SCHEMA_RELATIONS["phones"]["table"]
    phone_col = SCHEMA_RELATIONS["phones"]["fields"]["number"]
    sql = f"""
        SELECT DISTINCT {select_fields}, p.{phone_col} as phone
        FROM ZABCDRECORD r
        JOIN {phone_table} p ON p.ZOWNER = r.Z_PK
        WHERE p.ZLASTFOURDIGITS = ?
        LIMIT 20
    """
    return query_contacts(sql, (last_four,))

def translate_where(where_clause: str) -> str:
    """Translate our field names to SQLite column names in a WHERE clause.
    
    Also supports virtual fields:
        - has_photo: true if contact has any photo data (embedded OR reference)
        - no_photo: true if contact has no photo at all (both fields NULL)
    """
    import re
    result = where_clause
    
    # Handle virtual "has_photo" and "no_photo" convenience fields FIRST
    # These expand to compound conditions before field translation
    # Any data (even 38-byte references) counts as having a photo
    result = re.sub(
        r'\bhas_photo\s*=\s*true\b',
        '(photo IS NOT NULL OR thumbnail IS NOT NULL)',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'\bhas_photo\s*=\s*false\b',
        '(photo IS NULL AND thumbnail IS NULL)',
        result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'\bno_photo\s*=\s*true\b',
        '(photo IS NULL AND thumbnail IS NULL)',
        result, flags=re.IGNORECASE
    )
    
    # Translate main SCHEMA fields (e.g., photo → r.ZIMAGEDATA)
    for field, mapping in SCHEMA.items():
        result = re.sub(rf'\b{field}\b', f'r.{mapping["sql"]}', result, flags=re.IGNORECASE)
    
    # Translate SCHEMA_RELATIONS fields (e.g., url → u.ZURL)
    # These need special handling for table aliases
    for relation, config in SCHEMA_RELATIONS.items():
        for field_name, sql_col in config["fields"].items():
            # Use table alias: phones→p, emails→e, urls→u, socials→s
            alias = relation[0]  # First letter
            result = re.sub(rf'\b{field_name}\b', f'{alias}.{sql_col}', result, flags=re.IGNORECASE)
    
    return result

def search_where(where_clause: str, limit: int = 50) -> list[dict]:
    """
    Search contacts with custom WHERE clause using our field names.
    
    Examples:
        search_where("photo IS NULL")
        search_where("firstName LIKE 'J%' AND organization IS NOT NULL")
        search_where("photo IS NULL AND url LIKE '%instagram%'")
    """
    select_fields = sql_select(["id", "firstName", "lastName", "organization", "jobTitle"])
    translated_where = translate_where(where_clause)
    where_lower = where_clause.lower()
    
    # Build JOINs based on which relation fields are referenced
    joins = []
    if "url" in where_lower:
        joins.append(f'LEFT JOIN {SCHEMA_RELATIONS["urls"]["table"]} u ON u.ZOWNER = r.Z_PK')
    if "phone" in where_lower or "number" in where_lower:
        joins.append(f'LEFT JOIN {SCHEMA_RELATIONS["phones"]["table"]} p ON p.ZOWNER = r.Z_PK')
    if "email" in where_lower or "address" in where_lower:
        joins.append(f'LEFT JOIN {SCHEMA_RELATIONS["emails"]["table"]} e ON e.ZOWNER = r.Z_PK')
    
    join_clause = "\n            ".join(joins) if joins else ""
    
    sql = f"""
        SELECT DISTINCT {select_fields}
        FROM ZABCDRECORD r
        {join_clause}
        WHERE {translated_where}
        LIMIT {limit}
    """
    
    return query_contacts(sql, ())

def get_photo_info(contact_id: str) -> list[dict]:
    """Get photo information from SQLite.
    
    Returns array of photo objects, each with:
        - type: "image" or "thumbnail"
        - storage: "embedded" or "reference"
        - size: bytes
    """
    # Ensure :ABPerson suffix is present (SQLite stores full ID)
    if not contact_id.endswith(":ABPerson"):
        contact_id = contact_id + ":ABPerson"
    
    for db_path in get_contact_databases():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    length(ZIMAGEDATA) as image_size,
                    length(ZTHUMBNAILIMAGEDATA) as thumb_size
                FROM ZABCDRECORD 
                WHERE ZUNIQUEID = ?
            """, (contact_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row or (row[0] is None and row[1] is None):
                continue
            
            image_size, thumb_size = row
            photos = []
            
            # Classify image
            if image_size:
                photos.append({
                    "type": "image",
                    "storage": "reference" if image_size < 100 else "embedded",
                    "size": image_size
                })
            
            # Classify thumbnail
            if thumb_size:
                photos.append({
                    "type": "thumbnail",
                    "storage": "reference" if thumb_size < 100 else "embedded",
                    "size": thumb_size
                })
            
            return photos
        except sqlite3.Error:
            continue
    
    return []


def get_contact_details(contact_id: str) -> Optional[dict]:
    """Get full contact details by ID using AppleScript (ensures consistency after writes)."""
    # First get name from SQLite (fast lookup to find the contact)
    select_fields = sql_select(["firstName", "lastName"])
    sql = f"""
        SELECT {select_fields}
        FROM ZABCDRECORD r WHERE r.{sql_column("id")} = ?
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
    
    # Add photo information from SQLite
    contact["photos"] = get_photo_info(contact_id)
    
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
        # Normalize phone number to include country code
        number = normalize_phone(number)
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
    
    # Normalize phone number to include country code
    normalized_number = normalize_phone(phone.number)
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                make new phone at end of phones of thePerson with properties {{label:"{phone.label}", value:"{escape_applescript(normalized_number)}"}}
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
# Photo Functions
# =============================================================================

def set_photo_from_file(contact_id: str, file_path: str) -> tuple[bool, str]:
    """Set contact photo from a local image file."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set imagePath to POSIX file "{escape_applescript(file_path)}"
                set imageData to read imagePath as picture
                set image of thePerson to imageData
                save
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    return run_applescript(script)

def set_photo_from_url(contact_id: str, url: str) -> tuple[bool, str]:
    """Download image from URL and set as contact photo."""
    import tempfile
    import urllib.request
    
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    # Determine file extension from URL
    ext = ".jpg"
    if ".png" in url.lower():
        ext = ".png"
    elif ".gif" in url.lower():
        ext = ".gif"
    
    # Download to temp file
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp_path = tmp.name
        
        urllib.request.urlretrieve(url, tmp_path)
        
        # Set the photo
        success, result = set_photo_from_file(contact_id, tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return success, result
    except Exception as e:
        return False, f"Failed to download image: {e}"

def clear_photo(contact_id: str) -> tuple[bool, str]:
    """Remove photo from contact."""
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found"
    
    script = f'''
        tell application "Contacts"
            try
                set thePerson to first person whose first name is "{escape_applescript(contact.get('firstName', ''))}" and last name is "{escape_applescript(contact.get('lastName', ''))}"
                set image of thePerson to missing value
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

def migrate_urls_to_socials(contact_id: str) -> list[str]:
    """
    Scan contact's URLs for recognized social profiles and migrate them.
    Returns list of services that were migrated.
    """
    contact = get_contact_details(contact_id)
    if not contact:
        return []
    
    migrated = []
    urls_to_remove = []
    
    for url_entry in contact.get("urls", []):
        url = url_entry.get("url", "")
        if not url:
            continue
        
        # Check if this URL matches a known social service
        result = get_service_from_url(url)
        if result:
            service_key, username = result
            service_info = get_service(service_key)
            
            if service_info and username:
                # Check if this social already exists
                existing_socials = [s.get("service", "").lower() for s in contact.get("socials", [])]
                service_name = service_info["name"]
                
                if service_name.lower() not in existing_socials:
                    # Add as social profile
                    social = Social(service=service_key, username=username)
                    success, _ = add_social_applescript(contact_id, social)
                    
                    if success:
                        migrated.append(service_name)
                        urls_to_remove.append(url)
    
    # Remove migrated URLs
    for url in urls_to_remove:
        remove_url_applescript(contact_id, url)
    
    return migrated


def fix_contact_socials(contact_id: str) -> tuple[bool, str, list[str]]:
    """Fix corrupted social profiles and migrate social URLs for a contact.
    
    Returns (success, message, migrated_services).
    """
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found", []
    
    # First, migrate any social URLs to proper social profiles
    migrated = migrate_urls_to_socials(contact_id)
    
    # Re-fetch contact after migration
    contact = get_contact_details(contact_id)
    if not contact:
        return False, "Contact not found", []
    
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
    success, result = run_applescript(script)
    return success, result, migrated


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
    search_parser.add_argument("--where", help="Custom WHERE clause using field names (e.g., 'photo IS NULL')")
    
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
    
    # photo subcommands
    photo_parser = subparsers.add_parser("photo", help="Photo operations")
    photo_sub = photo_parser.add_subparsers(dest="action", required=True)
    
    photo_set = photo_sub.add_parser("set", help="Set photo from URL or file")
    photo_set.add_argument("id", help="Contact ID")
    photo_set.add_argument("source", help="Image URL or local file path")
    
    photo_clear = photo_sub.add_parser("clear", help="Remove photo")
    photo_clear.add_argument("id", help="Contact ID")
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == "search":
        if args.phone:
            results = search_by_phone(args.phone)
        elif args.where:
            results = search_where(args.where)
        elif args.query:
            results = search_by_name(args.query)
        else:
            parser.error("Provide a query, --phone, or --where")
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
        success, result, migrated = fix_contact_socials(args.id)
        if success:
            msg = "Social profiles fixed"
            if migrated:
                msg += f". Migrated URLs to socials: {', '.join(migrated)}"
            output_json({"success": True, "message": msg, "migrated": migrated})
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
    
    elif args.command == "photo":
        if args.action == "set":
            # Check if source is URL or file path
            source = args.source
            if source.startswith("http://") or source.startswith("https://"):
                success, result = set_photo_from_url(args.id, source)
            else:
                # Treat as file path
                success, result = set_photo_from_file(args.id, source)
        elif args.action == "clear":
            success, result = clear_photo(args.id)
        
        if success:
            output_json({"success": True, "message": f"Photo {'cleared' if args.action == 'clear' else 'set'}"})
        else:
            output_json({"success": False, "error": result})
            sys.exit(1)

if __name__ == "__main__":
    main()

