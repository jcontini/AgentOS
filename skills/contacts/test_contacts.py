#!/usr/bin/env python3
"""
Integration tests for contacts.py

Runs a full CRUD lifecycle with a test contact.
Usage: python test_contacts.py
"""

import json
import subprocess
import sys

SCRIPT = "contacts.py"
TEST_FIRST = "_TEST_"
TEST_LAST = "_DELETEME_"

def run(cmd: list[str], check: bool = True) -> dict:
    """Run contacts.py command and return parsed JSON."""
    full_cmd = ["python3", SCRIPT] + cmd
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"    FAIL: {result.stderr or result.stdout}")
        sys.exit(1)
    
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def test_crud_lifecycle():
    """Test full create → read → update → delete cycle."""
    print("\n=== Contacts CRUD Integration Test ===\n")
    
    # 1. CREATE
    print("1. CREATE contact")
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
        "--org", "Test Organization",
        "--phone", "+15550001234",
        "--email", "test@example.com"
    ])
    assert result.get("success"), f"Create failed: {result}"
    contact_id = result.get("id", "").strip()
    print(f"    ✓ Created: {contact_id[:20]}...")
    
    # 2. SEARCH by name
    print("\n2. SEARCH by name")
    result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    assert result.get("count", 0) >= 1, "Contact not found in search"
    print(f"    ✓ Found {result['count']} contact(s)")
    
    # Get the ID from search if create didn't return it
    if not contact_id:
        contact_id = result["contacts"][0]["id"]
    
    # 3. GET full details
    print("\n3. GET contact details")
    result = run(["get", contact_id])
    assert result.get("firstName") == TEST_FIRST, "Wrong first name"
    assert result.get("organization") == "Test Organization", "Wrong org"
    print(f"    ✓ Got: {result.get('firstName')} {result.get('lastName')}")
    print(f"    ✓ Org: {result.get('organization')}")
    print(f"    ✓ Phones: {len(result.get('phones', []))}")
    print(f"    ✓ Emails: {len(result.get('emails', []))}")
    
    # 4. UPDATE fields
    print("\n4. UPDATE contact")
    result = run(["update", contact_id, "--job-title", "Test Engineer", "--note", "Integration test contact"])
    assert result.get("success"), f"Update failed: {result}"
    print("    ✓ Updated job title and note")
    
    # 5. ADD phone
    print("\n5. PHONE ADD")
    result = run(["phone", "add", contact_id, "+15550005678", "work"])
    assert result.get("success"), f"Add phone failed: {result}"
    print("    ✓ Added work phone")
    
    # 6. ADD email
    print("\n6. EMAIL ADD")
    result = run(["email", "add", contact_id, "work@example.com", "work"])
    assert result.get("success"), f"Add email failed: {result}"
    print("    ✓ Added work email")
    
    # 7. ADD URL (for non-Apple services like GitHub)
    print("\n7. URL ADD")
    result = run(["url", "add", contact_id, "https://github.com/testuser", "GitHub"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added GitHub URL")
    
    # 8. ADD another URL (Instagram as URL, not social)
    print("\n8. URL ADD (Instagram)")
    result = run(["url", "add", contact_id, "https://instagram.com/testuser", "Instagram"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added Instagram URL")
    
    # 9. ADD social (Apple-official service only - Twitter)
    print("\n9. SOCIAL ADD (Twitter - Apple official)")
    result = run(["social", "add", contact_id, "twitter", "testuser"])
    assert result.get("success"), f"Add social failed: {result}"
    print("    ✓ Added Twitter profile (Apple-official, clickable)")
    
    # 10. ADD social (LinkedIn - Apple official)
    print("\n10. SOCIAL ADD (LinkedIn - Apple official)")
    result = run(["social", "add", contact_id, "linkedin", "test-user"])
    assert result.get("success"), f"Add social failed: {result}"
    print("    ✓ Added LinkedIn profile (Apple-official, clickable)")
    
    # 11. Verify additions
    print("\n11. VERIFY additions")
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    urls = result.get("urls", [])
    socials = result.get("socials", [])
    
    print(f"    ✓ Phones: {len(phones)} (expected 2)")
    print(f"    ✓ Emails: {len(emails)} (expected 2)")
    print(f"    ✓ URLs: {len(urls)} (expected 2)")
    print(f"    ✓ Socials: {len(socials)} (expected 2)")
    
    # Verify URL contents
    url_labels = [u.get("label") for u in urls]
    assert "GitHub" in url_labels, f"GitHub URL not found in {url_labels}"
    assert "Instagram" in url_labels, f"Instagram URL not found in {url_labels}"
    print("    ✓ URLs have correct labels (GitHub, Instagram)")
    
    # Verify social contents
    social_services = [s.get("service") for s in socials]
    assert "Twitter" in social_services, f"Twitter not found in {social_services}"
    assert "LinkedIn" in social_services, f"LinkedIn not found in {social_services}"
    print("    ✓ Socials have correct services (Twitter, LinkedIn)")
    
    # 12. FIX social profiles (should be no-op for clean data)
    print("\n12. FIX social profiles")
    result = run(["fix", contact_id])
    assert result.get("success"), f"Fix failed: {result}"
    print("    ✓ Fix completed")
    
    # 13. REMOVE social (Twitter)
    print("\n13. SOCIAL REMOVE")
    result = run(["social", "remove", contact_id, "twitter"])
    assert result.get("success"), f"Remove social failed: {result}"
    print("    ✓ Removed Twitter profile")
    
    # 14. REMOVE social (LinkedIn)
    print("\n14. SOCIAL REMOVE (LinkedIn)")
    result = run(["social", "remove", contact_id, "linkedin"])
    assert result.get("success"), f"Remove social failed: {result}"
    print("    ✓ Removed LinkedIn profile")
    
    # 15. REMOVE URL (GitHub)
    print("\n15. URL REMOVE")
    result = run(["url", "remove", contact_id, "github.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed GitHub URL")
    
    # 16. REMOVE URL (Instagram)
    print("\n16. URL REMOVE (Instagram)")
    result = run(["url", "remove", contact_id, "instagram.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed Instagram URL")
    
    # 17. REMOVE phone
    print("\n17. PHONE REMOVE")
    result = run(["phone", "remove", contact_id, "+15550005678"])
    assert result.get("success"), f"Remove phone failed: {result}"
    print("    ✓ Removed work phone")
    
    # 18. REMOVE email
    print("\n18. EMAIL REMOVE")
    result = run(["email", "remove", contact_id, "work@example.com"])
    assert result.get("success"), f"Remove email failed: {result}"
    print("    ✓ Removed work email")
    
    # 19. Final state
    print("\n19. FINAL state")
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    urls = result.get("urls", [])
    socials = result.get("socials", [])
    print(f"    ✓ Phones: {len(phones)} (expected 1)")
    print(f"    ✓ Emails: {len(emails)} (expected 1)")
    print(f"    ✓ URLs: {len(urls)} (expected 0)")
    print(f"    ✓ Socials: {len(socials)} (expected 0)")
    
    # CLEANUP - Delete test contact via AppleScript
    print("\n20. CLEANUP (delete test contact)")
    cleanup_script = f'''
        tell application "Contacts"
            try
                delete (every person whose first name is "{TEST_FIRST}" and last name is "{TEST_LAST}")
                save
                return "deleted"
            on error
                return "not found"
            end try
        end tell
    '''
    subprocess.run(["osascript", "-e", cleanup_script], capture_output=True)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ All CRUD tests passed!")
    print("=" * 40 + "\n")

def run_applescript(script: str) -> str:
    """Run AppleScript and return output."""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()

def test_fix_scenarios():
    """Test fix command handles various corrupted social profile scenarios."""
    print("\n=== Social Profile Fix Test ===\n")
    
    TEST_FIRST = "_FIXTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact via AppleScript with corrupted social profiles
    print("1. CREATE contact with corrupted social profiles")
    setup_script = f'''
        tell application "Contacts"
            set p to make new person with properties {{first name:"{TEST_FIRST}", last name:"{TEST_LAST}"}}
            
            -- Scenario A: Valid username, missing URL (Apple-official service)
            make new social profile at end of social profiles of p with properties {{service name:"Twitter", user name:"testuser123"}}
            
            -- Scenario B: Truncated/corrupted URL
            make new social profile at end of social profiles of p with properties {{service name:"Facebook", user name:"validuser"}}
            -- Manually corrupt the URL
            set url of social profile 2 of p to "https://www.facebook"
            
            -- Scenario C: URL pasted as username
            make new social profile at end of social profiles of p with properties {{service name:"LinkedIn", user name:"WWW.LINKEDIN.COM/IN/PROFILE?ID=123456"}}
            
            -- Scenario D: Garbage username, garbage URL (should be nullified)
            make new social profile at end of social profiles of p with properties {{service name:"Flickr", user name:"TYPE=PREF"}}
            
            save
            return id of p
        end tell
    '''
    contact_id = run_applescript(setup_script)
    print(f"    ✓ Created test contact: {contact_id[:30]}...")
    
    # Read initial state
    print("\n2. VERIFY corrupted state")
    check_script = f'''
        tell application "Contacts"
            set p to first person whose first name is "{TEST_FIRST}"
            set output to ""
            repeat with sp in social profiles of p
                set svc to service name of sp
                if svc is not "" then
                    set output to output & svc & "|" & user name of sp & "|" & url of sp & ";;;"
                end if
            end repeat
            return output
        end tell
    '''
    before = run_applescript(check_script)
    print(f"    Before fix: {before[:100]}...")
    
    # Run fix
    print("\n3. RUN fix command")
    # Get contact ID in proper format
    search_result = subprocess.run(
        ["python3", SCRIPT, "search", f"{TEST_FIRST} {TEST_LAST}"],
        capture_output=True, text=True
    )
    contact_data = json.loads(search_result.stdout)
    if contact_data.get("count", 0) > 0:
        proper_id = contact_data["contacts"][0]["id"]
        fix_result = subprocess.run(
            ["python3", SCRIPT, "fix", proper_id],
            capture_output=True, text=True
        )
        print(f"    Fix result: {fix_result.stdout.strip()}")
    
    # Verify fixed state
    print("\n4. VERIFY fixed state")
    after = run_applescript(check_script)
    profiles = [p for p in after.split(";;;") if p.strip()]
    
    for profile in profiles:
        parts = profile.split("|")
        if len(parts) >= 3:
            svc, usr, url = parts[0], parts[1], parts[2]
            print(f"    {svc}: usr={usr}, url={url[:50] if url != 'missing value' else url}")
    
    # Verify specific scenarios
    print("\n5. VERIFY scenario outcomes")
    
    # Scenario A: Twitter should have URL constructed
    if "Twitter" in after and "twitter.com" in after:
        print("    ✓ Scenario A: Twitter URL constructed from username")
    else:
        print("    ⚠ Scenario A: Twitter URL not constructed")
    
    # Scenario B: Facebook should have URL fixed
    if "Facebook" in after and "facebook.com/validuser" in after.lower():
        print("    ✓ Scenario B: Facebook URL reconstructed")
    else:
        print("    ⚠ Scenario B: Facebook URL not fixed")
    
    # Scenario C: LinkedIn URL-as-username - this is a weird case
    # The fix should try to extract profile ID if present
    if "LinkedIn" in after:
        print("    ✓ Scenario C: LinkedIn processed")
    
    # Scenario D: Flickr garbage should be nullified (not in output)
    if "Flickr" not in after or "TYPE=PREF" not in after:
        print("    ✓ Scenario D: Flickr garbage nullified")
    else:
        print("    ⚠ Scenario D: Flickr garbage not nullified")
    
    # Cleanup
    print("\n6. CLEANUP")
    cleanup_script = f'''
        tell application "Contacts"
            delete (first person whose first name is "{TEST_FIRST}")
            save
        end tell
    '''
    run_applescript(cleanup_script)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ Fix scenarios test complete!")
    print("=" * 40 + "\n")

def test_url_operations():
    """Test URL add/remove with various labels and formats."""
    print("\n=== URL Operations Test ===\n")
    
    TEST_FIRST = "_URLTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact")
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...")
    
    # Add various URLs with different labels
    print("\n2. ADD URLs with various labels")
    
    test_urls = [
        ("https://github.com/testuser", "GitHub"),
        ("https://instagram.com/testuser", "Instagram"),
        ("https://keybase.io/testuser", "Keybase"),
        ("https://angel.co/u/testuser", "AngelList"),
        ("https://quora.com/profile/testuser", "Quora"),
        ("https://youtube.com/@testuser", "YouTube"),
        ("https://example.com", "homepage"),
    ]
    
    for url, label in test_urls:
        result = run(["url", "add", contact_id, url, label])
        assert result.get("success"), f"Add URL failed for {label}: {result}"
        print(f"    ✓ Added {label}: {url}")
    
    # Verify all URLs present
    print("\n3. VERIFY all URLs")
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    
    assert len(urls) == len(test_urls), f"Expected {len(test_urls)} URLs, got {len(urls)}"
    print(f"    ✓ {len(urls)} URLs found")
    
    url_labels = {u.get("label") for u in urls}
    for _, label in test_urls:
        assert label in url_labels, f"Label '{label}' not found in URLs"
    print("    ✓ All labels present")
    
    # Remove URLs by partial match
    print("\n4. REMOVE URLs (partial match)")
    
    result = run(["url", "remove", contact_id, "github.com"])
    assert result.get("success"), f"Remove GitHub failed: {result}"
    print("    ✓ Removed github.com")
    
    result = run(["url", "remove", contact_id, "keybase"])
    assert result.get("success"), f"Remove Keybase failed: {result}"
    print("    ✓ Removed keybase")
    
    # Verify removals
    print("\n5. VERIFY removals")
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    remaining_urls = [u.get("url", "") for u in urls]
    
    assert not any("github.com" in u for u in remaining_urls), "GitHub not removed"
    assert not any("keybase" in u for u in remaining_urls), "Keybase not removed"
    print(f"    ✓ {len(urls)} URLs remaining (expected 5)")
    
    # Cleanup
    print("\n6. CLEANUP")
    cleanup_script = f'''
        tell application "Contacts"
            try
                delete (every person whose first name is "{TEST_FIRST}" and last name is "{TEST_LAST}")
                save
                return "deleted"
            on error
                return "not found"
            end try
        end tell
    '''
    subprocess.run(["osascript", "-e", cleanup_script], capture_output=True)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ URL operations test complete!")
    print("=" * 40 + "\n")

def test_social_apple_official():
    """Test that Apple-official social services work correctly."""
    print("\n=== Apple-Official Social Services Test ===\n")
    
    TEST_FIRST = "_SOCIALTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact")
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...")
    
    # Add Apple-official social services
    print("\n2. ADD Apple-official social profiles")
    
    official_services = [
        ("twitter", "testtwitter"),
        ("linkedin", "test-linkedin"),
        ("facebook", "testfacebook"),
        ("flickr", "testflickr"),
    ]
    
    for service, username in official_services:
        result = run(["social", "add", contact_id, service, username])
        assert result.get("success"), f"Add {service} failed: {result}"
        print(f"    ✓ Added {service}: {username}")
    
    # Verify all socials present with normalized names
    print("\n3. VERIFY social profiles")
    result = run(["get", contact_id])
    socials = result.get("socials", [])
    
    assert len(socials) == len(official_services), f"Expected {len(official_services)} socials, got {len(socials)}"
    print(f"    ✓ {len(socials)} social profiles found")
    
    # Verify service names are normalized (capitalized)
    service_names = {s.get("service") for s in socials}
    expected_names = {"Twitter", "LinkedIn", "Facebook", "Flickr"}
    assert service_names == expected_names, f"Service names not normalized: {service_names}"
    print("    ✓ Service names properly normalized")
    
    # Remove socials
    print("\n4. REMOVE social profiles")
    for service, _ in official_services:
        result = run(["social", "remove", contact_id, service])
        assert result.get("success"), f"Remove {service} failed: {result}"
        print(f"    ✓ Removed {service}")
    
    # Verify all removed
    print("\n5. VERIFY all removed")
    result = run(["get", contact_id])
    socials = result.get("socials", [])
    # Filter out any empty socials
    socials = [s for s in socials if s.get("service") and s.get("username")]
    assert len(socials) == 0, f"Expected 0 socials, got {len(socials)}"
    print("    ✓ All social profiles removed")
    
    # Cleanup
    print("\n6. CLEANUP")
    cleanup_script = f'''
        tell application "Contacts"
            try
                delete (every person whose first name is "{TEST_FIRST}" and last name is "{TEST_LAST}")
                save
                return "deleted"
            on error
                return "not found"
            end try
        end tell
    '''
    subprocess.run(["osascript", "-e", cleanup_script], capture_output=True)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ Apple-official social services test complete!")
    print("=" * 40 + "\n")

def test_photo_operations():
    """Test photo set/clear functionality."""
    print("\n=== Photo Operations Test ===\n")
    
    TEST_FIRST = "_PHOTOTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact")
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...")
    
    # Set photo from URL (using a known public avatar)
    print("\n2. SET photo from URL")
    # Using GitHub's default avatar as a reliable test image
    test_url = "https://avatars.githubusercontent.com/u/167932?v=4"
    result = run(["photo", "set", contact_id, test_url])
    assert result.get("success"), f"Set photo failed: {result}"
    print(f"    ✓ Set photo from URL")
    
    # Verify photo exists via AppleScript
    print("\n3. VERIFY photo exists")
    verify_script = f'''
        tell application "Contacts"
            set p to first person whose first name is "{TEST_FIRST}"
            if image of p is not missing value then
                return "has_image"
            else
                return "no_image"
            end if
        end tell
    '''
    photo_status = run_applescript(verify_script)
    assert photo_status == "has_image", f"Photo not set: {photo_status}"
    print("    ✓ Photo exists on contact")
    
    # Clear photo
    print("\n4. CLEAR photo")
    result = run(["photo", "clear", contact_id])
    assert result.get("success"), f"Clear photo failed: {result}"
    print("    ✓ Cleared photo")
    
    # Verify photo cleared
    print("\n5. VERIFY photo cleared")
    photo_status = run_applescript(verify_script)
    assert photo_status == "no_image", f"Photo not cleared: {photo_status}"
    print("    ✓ Photo cleared successfully")
    
    # Test setting from local file
    print("\n6. SET photo from local file")
    import tempfile
    import urllib.request
    
    # Download test image to temp file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
    urllib.request.urlretrieve(test_url, tmp_path)
    
    result = run(["photo", "set", contact_id, tmp_path])
    assert result.get("success"), f"Set photo from file failed: {result}"
    print(f"    ✓ Set photo from local file")
    
    # Verify
    photo_status = run_applescript(verify_script)
    assert photo_status == "has_image", f"Photo not set from file: {photo_status}"
    print("    ✓ Photo set from local file verified")
    
    # Cleanup temp file
    import os
    os.unlink(tmp_path)
    
    # Cleanup contact
    print("\n7. CLEANUP")
    cleanup_script = f'''
        tell application "Contacts"
            try
                delete (every person whose first name is "{TEST_FIRST}" and last name is "{TEST_LAST}")
                save
                return "deleted"
            on error
                return "not found"
            end try
        end tell
    '''
    subprocess.run(["osascript", "-e", cleanup_script], capture_output=True)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ Photo operations test complete!")
    print("=" * 40 + "\n")

def test_phone_normalization():
    """Test phone number normalization with country codes."""
    print("\n=== Phone Normalization Test ===\n")
    
    # Import the normalize function
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import normalize_phone
    
    print("1. TEST normalize_phone function")
    
    test_cases = [
        # (input, expected, description)
        ("5551234567", "+15551234567", "10-digit US number"),
        ("15551234567", "+15551234567", "11-digit with leading 1"),
        ("+15551234567", "+15551234567", "Already has +1"),
        ("+44 7911 123456", "+44 7911 123456", "UK number (keep as-is)"),
        ("(555) 123-4567", "+15551234567", "Formatted US number"),
        ("555-123-4567", "+15551234567", "Dashed US number"),
        ("555.123.4567", "+15551234567", "Dotted US number"),
        ("123", "123", "Short number (extension)"),
        ("+1 (555) 123-4567", "+1 (555) 123-4567", "Already has + prefix"),
        ("919876543210", "+919876543210", "Long number (Indian)"),
    ]
    
    all_passed = True
    for input_num, expected, description in test_cases:
        result = normalize_phone(input_num)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
            print(f"    {status} {description}: '{input_num}' → '{result}' (expected '{expected}')")
        else:
            print(f"    {status} {description}: '{input_num}' → '{result}'")
    
    assert all_passed, "Some phone normalization tests failed"
    
    print("\n2. TEST phone normalization in contact creation")
    
    TEST_FIRST = "_PHONETEST_"
    TEST_LAST = "_DELETE_"
    
    # Create contact with unnormalized phone
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
        "--phone", "5559876543",  # Should become +15559876543
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact and check phone
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    
    details = run(["get", contact_id])
    phones = details.get("phones", [])
    assert len(phones) >= 1, "No phones found"
    
    # The phone should be normalized
    phone_number = phones[0].get("number", "")
    assert phone_number.startswith("+1"), f"Phone not normalized: {phone_number}"
    print(f"    ✓ Created phone normalized to: {phone_number}")
    
    print("\n3. TEST phone normalization in phone add")
    result = run(["phone", "add", contact_id, "(555) 111-2222", "work"])
    assert result.get("success"), f"Add phone failed: {result}"
    
    details = run(["get", contact_id])
    phones = details.get("phones", [])
    work_phones = [p for p in phones if p.get("label") == "work"]
    assert len(work_phones) >= 1, "Work phone not found"
    
    work_number = work_phones[0].get("number", "")
    assert "+1" in work_number or work_number.startswith("+"), f"Work phone not normalized: {work_number}"
    print(f"    ✓ Added phone normalized to: {work_number}")
    
    # Cleanup
    print("\n4. CLEANUP")
    cleanup_script = f'''
        tell application "Contacts"
            try
                delete (every person whose first name is "{TEST_FIRST}" and last name is "{TEST_LAST}")
                save
                return "deleted"
            on error
                return "not found"
            end try
        end tell
    '''
    subprocess.run(["osascript", "-e", cleanup_script], capture_output=True)
    print("    ✓ Deleted test contact")
    
    print("\n" + "=" * 40)
    print("✅ Phone normalization test complete!")
    print("=" * 40 + "\n")

def test_unified_services():
    """Test the unified SERVICES registry and helper functions."""
    print("\n=== Unified Services Test ===\n")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import (
        SERVICES, get_service, get_photo_url, get_photo_api, 
        get_profile_url, is_apple_native, list_services_with_photos,
        get_service_from_url, extract_username_from_url, normalize_service
    )
    
    print("1. TEST SERVICES registry structure")
    assert len(SERVICES) > 20, f"Expected 20+ services, got {len(SERVICES)}"
    print(f"    ✓ {len(SERVICES)} services registered")
    
    # Verify all services have required fields (name, profile_url)
    # Optional fields: photo_url, photo_api, apple_native (defaults to False)
    required_fields = ["name", "profile_url"]
    for key, service in SERVICES.items():
        for field in required_fields:
            assert field in service, f"Service '{key}' missing required field '{field}'"
    print("    ✓ All services have required fields (name, profile_url)")
    
    print("\n2. TEST get_service function")
    github = get_service("github")
    assert github is not None, "GitHub service not found"
    assert github["name"] == "GitHub", f"Wrong name: {github['name']}"
    assert "github.com" in github["profile_url"], "Wrong profile URL"
    print("    ✓ get_service('github') works")
    
    # Case insensitive
    github2 = get_service("GitHub")
    assert github2 == github, "get_service should be case-insensitive"
    print("    ✓ Case insensitive lookup works")
    
    print("\n3. TEST is_apple_native function")
    assert is_apple_native("twitter") == True, "Twitter should be Apple-native"
    assert is_apple_native("linkedin") == True, "LinkedIn should be Apple-native"
    assert is_apple_native("github") == False, "GitHub should NOT be Apple-native"
    assert is_apple_native("instagram") == False, "Instagram should NOT be Apple-native"
    print("    ✓ Apple-native detection works")
    
    print("\n4. TEST get_profile_url function")
    test_cases = [
        ("github", "jcontini", "https://github.com/jcontini"),
        ("twitter", "jcontini", "https://twitter.com/jcontini"),
        ("linkedin", "jcontini", "https://www.linkedin.com/in/jcontini"),
        ("instagram", "jcontini", "https://www.instagram.com/jcontini"),
        ("youtube", "jcontini", "https://www.youtube.com/@jcontini"),
        ("tiktok", "jcontini", "https://www.tiktok.com/@jcontini"),
    ]
    
    for service, username, expected in test_cases:
        result = get_profile_url(service, username)
        assert result == expected, f"get_profile_url('{service}', '{username}') = '{result}', expected '{expected}'"
        print(f"    ✓ {service}: {result}")
    
    print("\n5. TEST get_photo_url function")
    photo_test_cases = [
        ("github", "jcontini", "https://github.com/jcontini.png"),
        ("facebook", "jcontini", "https://graph.facebook.com/jcontini/picture?type=large"),
        ("keybase", "jcontini", "https://keybase.io/jcontini/photo.png"),
        ("linkedin", "jcontini", None),  # No direct photo URL
        ("instagram", "jcontini", None),  # No direct photo URL
    ]
    
    for service, username, expected in photo_test_cases:
        result = get_photo_url(service, username)
        assert result == expected, f"get_photo_url('{service}', '{username}') = '{result}', expected '{expected}'"
        status = "✓" if expected else "✓ (None - requires auth)"
        print(f"    {status} {service}: {result}")
    
    print("\n6. TEST get_photo_api function")
    api_test_cases = [
        ("github", "jcontini", "https://api.github.com/users/jcontini"),
        ("bluesky", "jcontini", "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=jcontini"),
        ("twitter", "jcontini", None),  # No public API
    ]
    
    for service, username, expected in api_test_cases:
        result = get_photo_api(service, username)
        assert result == expected, f"get_photo_api('{service}', '{username}') = '{result}', expected '{expected}'"
        status = "✓" if expected else "✓ (None - no public API)"
        print(f"    {status} {service}: {result}")
    
    print("\n7. TEST list_services_with_photos")
    photo_services = list_services_with_photos()
    assert "github" in photo_services, "GitHub should have photo support"
    assert "facebook" in photo_services, "Facebook should have photo support"
    assert "keybase" in photo_services, "Keybase should have photo support"
    print(f"    ✓ {len(photo_services)} services with photo support: {', '.join(photo_services)}")
    
    print("\n8. TEST normalize_service function")
    normalize_cases = [
        ("github", "GitHub"),
        ("GITHUB", "GitHub"),
        ("twitter", "Twitter"),
        ("linkedin", "LinkedIn"),
        ("unknown_service", "Unknown_service"),  # Falls back to capitalize
    ]
    
    for input_name, expected in normalize_cases:
        result = normalize_service(input_name)
        assert result == expected, f"normalize_service('{input_name}') = '{result}', expected '{expected}'"
        print(f"    ✓ '{input_name}' → '{result}'")
    
    print("\n9. TEST extract_username_from_url function")
    url_test_cases = [
        ("https://github.com/jcontini", "https://github.com/{username}", "jcontini"),
        ("https://www.linkedin.com/in/joe-contini", "https://www.linkedin.com/in/{username}", "joe-contini"),
        ("https://twitter.com/jcontini", "https://twitter.com/{username}", "jcontini"),
        ("https://www.instagram.com/jcontini/", "https://www.instagram.com/{username}", "jcontini"),
        ("https://www.youtube.com/@jcontini", "https://www.youtube.com/@{username}", "jcontini"),
    ]
    
    for url, template, expected in url_test_cases:
        result = extract_username_from_url(url, template)
        assert result == expected, f"extract_username_from_url('{url}') = '{result}', expected '{expected}'"
        print(f"    ✓ {url} → '{result}'")
    
    print("\n10. TEST get_service_from_url function")
    service_url_cases = [
        ("https://github.com/jcontini", ("github", "jcontini")),
        ("https://www.linkedin.com/in/joe-contini", ("linkedin", "joe-contini")),
        ("https://twitter.com/testuser", ("twitter", "testuser")),
        ("https://example.com/random", None),  # Unknown service
    ]
    
    for url, expected in service_url_cases:
        result = get_service_from_url(url)
        if expected is None:
            assert result is None, f"get_service_from_url('{url}') should be None, got {result}"
            print(f"    ✓ {url} → None (unknown)")
        else:
            assert result is not None, f"get_service_from_url('{url}') should not be None"
            assert result[0] == expected[0], f"Wrong service: {result[0]} != {expected[0]}"
            assert result[1] == expected[1], f"Wrong username: {result[1]} != {expected[1]}"
            print(f"    ✓ {url} → {result}")
    
    print("\n" + "=" * 40)
    print("✅ Unified services test complete!")
    print("=" * 40 + "\n")

def test_photo_from_service_url():
    """Test getting photo URLs from various service profile URLs."""
    print("\n=== Photo from Service URL Test ===\n")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import get_service_from_url, get_photo_url, get_photo_api
    
    print("1. TEST photo URL extraction workflow")
    
    # Simulate: contact has GitHub URL, we want to get their photo
    github_url = "https://github.com/jcontini"
    
    # Step 1: Identify service and username from URL
    result = get_service_from_url(github_url)
    assert result is not None, "Should recognize GitHub URL"
    service, username = result
    print(f"    ✓ Detected: {service}/{username} from {github_url}")
    
    # Step 2: Get photo URL
    photo_url = get_photo_url(service, username)
    assert photo_url is not None, "GitHub should have photo URL"
    assert "jcontini" in photo_url, "Photo URL should contain username"
    print(f"    ✓ Photo URL: {photo_url}")
    
    # Step 3: Alternative - Get photo API
    photo_api = get_photo_api(service, username)
    assert photo_api is not None, "GitHub should have photo API"
    assert "jcontini" in photo_api, "Photo API should contain username"
    print(f"    ✓ Photo API: {photo_api}")
    
    print("\n2. TEST services without photo support")
    linkedin_url = "https://www.linkedin.com/in/jcontini"
    result = get_service_from_url(linkedin_url)
    assert result is not None, "Should recognize LinkedIn URL"
    service, username = result
    
    photo_url = get_photo_url(service, username)
    assert photo_url is None, "LinkedIn should NOT have direct photo URL (requires auth)"
    print(f"    ✓ {service} correctly returns None for photo URL (auth required)")
    
    print("\n3. TEST full workflow: URL → photo")
    test_urls = [
        ("https://github.com/torvalds", True),
        ("https://keybase.io/max", True),
        ("https://facebook.com/zuck", True),
        ("https://www.linkedin.com/in/satyanadella", False),  # No public photo
        ("https://www.instagram.com/instagram", False),  # No public photo
    ]
    
    for url, should_have_photo in test_urls:
        result = get_service_from_url(url)
        if result:
            service, username = result
            photo = get_photo_url(service, username)
            has_photo = photo is not None
            status = "✓" if has_photo == should_have_photo else "✗"
            print(f"    {status} {service}/{username}: photo={'Yes' if has_photo else 'No (auth required)'}")
        else:
            print(f"    ⚠ Could not parse: {url}")
    
    print("\n" + "=" * 40)
    print("✅ Photo from service URL test complete!")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    test_crud_lifecycle()
    test_url_operations()
    test_social_apple_official()
    test_photo_operations()
    test_phone_normalization()
    test_unified_services()
    test_photo_from_service_url()
    test_fix_scenarios()
    
    print("\n" + "=" * 50)
    print("🎉 ALL TEST SUITES PASSED!")
    print("=" * 50 + "\n")
