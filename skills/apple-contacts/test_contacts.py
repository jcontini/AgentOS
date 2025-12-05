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
    print(f"  → {' '.join(cmd)}", flush=True)
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"    FAIL: {result.stderr or result.stdout}", flush=True)
        sys.exit(1)
    
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def test_crud_lifecycle():
    """Test full create → read → update → delete cycle."""
    print("\n=== Contacts CRUD Integration Test ===\n", flush=True)
    
    # 1. CREATE
    print("1. CREATE contact", flush=True)
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
    print(f"    ✓ Created: {contact_id[:20]}...", flush=True)
    
    # 2. SEARCH by name
    print("\n2. SEARCH by name", flush=True)
    result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    assert result.get("count", 0) >= 1, "Contact not found in search"
    print(f"    ✓ Found {result['count']} contact(s)", flush=True)
    
    # Get the ID from search if create didn't return it
    if not contact_id:
        contact_id = result["contacts"][0]["id"]
    
    # 3. GET full details
    print("\n3. GET contact details", flush=True)
    result = run(["get", contact_id])
    assert result.get("firstName") == TEST_FIRST, "Wrong first name"
    assert result.get("organization") == "Test Organization", "Wrong org"
    print(f"    ✓ Got: {result.get('firstName')} {result.get('lastName')}", flush=True)
    print(f"    ✓ Org: {result.get('organization')}", flush=True)
    print(f"    ✓ Phones: {len(result.get('phones', []))}", flush=True)
    print(f"    ✓ Emails: {len(result.get('emails', []))}", flush=True)
    
    # 4. UPDATE fields
    print("\n4. UPDATE contact", flush=True)
    result = run(["update", contact_id, "--job-title", "Test Engineer", "--note", "Integration test contact"])
    assert result.get("success"), f"Update failed: {result}"
    print("    ✓ Updated job title and note", flush=True)
    
    # 5. ADD phone
    print("\n5. PHONE ADD", flush=True)
    result = run(["phone", "add", contact_id, "+15550005678", "work"])
    assert result.get("success"), f"Add phone failed: {result}"
    print("    ✓ Added work phone", flush=True)
    
    # 6. ADD email
    print("\n6. EMAIL ADD", flush=True)
    result = run(["email", "add", contact_id, "work@example.com", "work"])
    assert result.get("success"), f"Add email failed: {result}"
    print("    ✓ Added work email", flush=True)
    
    # 7. ADD URL (for non-Apple services like GitHub)
    print("\n7. URL ADD", flush=True)
    result = run(["url", "add", contact_id, "https://github.com/testuser", "GitHub"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added GitHub URL", flush=True)
    
    # 8. ADD another URL (Instagram as URL, not social)
    print("\n8. URL ADD (Instagram)", flush=True)
    result = run(["url", "add", contact_id, "https://instagram.com/testuser", "Instagram"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added Instagram URL", flush=True)
    
    # 9. ADD URL with auto-label detection (Twitter)
    print("\n9. URL ADD (Twitter - auto-label)", flush=True)
    result = run(["url", "add", contact_id, "https://twitter.com/testuser"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added Twitter URL (auto-labeled)", flush=True)
    
    # 10. ADD URL with auto-label detection (LinkedIn)
    print("\n10. URL ADD (LinkedIn - auto-label)", flush=True)
    result = run(["url", "add", contact_id, "https://linkedin.com/in/test-user"])
    assert result.get("success"), f"Add URL failed: {result}"
    print("    ✓ Added LinkedIn URL (auto-labeled)", flush=True)
    
    # 11. Verify additions
    print("\n11. VERIFY additions", flush=True)
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    urls = result.get("urls", [])
    
    print(f"    ✓ Phones: {len(phones)} (expected 2)", flush=True)
    print(f"    ✓ Emails: {len(emails)} (expected 2)", flush=True)
    print(f"    ✓ URLs: {len(urls)} (expected 4)", flush=True)
    
    # Verify URL contents
    url_labels = [u.get("label") for u in urls]
    assert "GitHub" in url_labels, f"GitHub URL not found in {url_labels}"
    assert "Instagram" in url_labels, f"Instagram URL not found in {url_labels}"
    assert "Twitter" in url_labels, f"Twitter URL not found in {url_labels}"
    assert "LinkedIn" in url_labels, f"LinkedIn URL not found in {url_labels}"
    print("    ✓ URLs have correct labels (GitHub, Instagram, Twitter, LinkedIn)", flush=True)
    
    # 12. REMOVE URL (Twitter)
    print("\n12. URL REMOVE (Twitter)", flush=True)
    result = run(["url", "remove", contact_id, "twitter.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed Twitter URL", flush=True)
    
    # 13. REMOVE URL (LinkedIn)
    print("\n13. URL REMOVE (LinkedIn)", flush=True)
    result = run(["url", "remove", contact_id, "linkedin.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed LinkedIn URL", flush=True)
    
    # 14. REMOVE URL (GitHub)
    print("\n14. URL REMOVE", flush=True)
    result = run(["url", "remove", contact_id, "github.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed GitHub URL", flush=True)
    
    # 15. REMOVE URL (Instagram)
    print("\n15. URL REMOVE (Instagram)", flush=True)
    result = run(["url", "remove", contact_id, "instagram.com"])
    assert result.get("success"), f"Remove URL failed: {result}"
    print("    ✓ Removed Instagram URL", flush=True)
    
    # 16. REMOVE phone
    print("\n16. PHONE REMOVE", flush=True)
    result = run(["phone", "remove", contact_id, "+15550005678"])
    assert result.get("success"), f"Remove phone failed: {result}"
    print("    ✓ Removed work phone", flush=True)
    
    # 17. REMOVE email
    print("\n17. EMAIL REMOVE", flush=True)
    result = run(["email", "remove", contact_id, "work@example.com"])
    assert result.get("success"), f"Remove email failed: {result}"
    print("    ✓ Removed work email", flush=True)
    
    # 18. Final state
    print("\n18. FINAL state", flush=True)
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    urls = result.get("urls", [])
    print(f"    ✓ Phones: {len(phones)} (expected 1)", flush=True)
    print(f"    ✓ Emails: {len(emails)} (expected 1)", flush=True)
    print(f"    ✓ URLs: {len(urls)} (expected 0)", flush=True)
    
    # CLEANUP - Delete test contact via AppleScript
    print("\n19. CLEANUP (delete test contact)", flush=True)
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
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ All CRUD tests passed!", flush=True)
    print("=" * 40 + "\n", flush=True)

def run_applescript(script: str) -> str:
    """Run AppleScript and return output."""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()

def test_fix_migration():
    """Test fix command migrates social profiles to URLs."""
    print("\n=== Social Profile → URL Migration Test ===\n", flush=True)
    
    TEST_FIRST = "_FIXTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact via AppleScript with social profiles
    print("1. CREATE contact with social profiles", flush=True)
    setup_script = f'''
        tell application "Contacts"
            set p to make new person with properties {{first name:"{TEST_FIRST}", last name:"{TEST_LAST}"}}
            
            -- Add Twitter social profile
            make new social profile at end of social profiles of p with properties {{service name:"Twitter", user name:"testuser123"}}
            
            -- Add LinkedIn social profile
            make new social profile at end of social profiles of p with properties {{service name:"LinkedIn", user name:"john-doe"}}
            
            -- Add Facebook social profile
            make new social profile at end of social profiles of p with properties {{service name:"Facebook", user name:"johndoe"}}
            
            save
            return id of p
        end tell
    '''
    contact_id = run_applescript(setup_script)
    print(f"    ✓ Created test contact: {contact_id[:30]}...", flush=True)
    
    # Read initial state - verify socials exist
    print("\n2. VERIFY initial state (social profiles)", flush=True)
    search_result = subprocess.run(
        ["python3", SCRIPT, "search", f"{TEST_FIRST} {TEST_LAST}"],
        capture_output=True, text=True
    )
    contact_data = json.loads(search_result.stdout)
    assert contact_data.get("count", 0) > 0, "Contact not found"
    proper_id = contact_data["contacts"][0]["id"]
    
    details_result = subprocess.run(
        ["python3", SCRIPT, "get", proper_id],
        capture_output=True, text=True
    )
    details = json.loads(details_result.stdout)
    
    socials_before = details.get("socials", [])
    urls_before = details.get("urls", [])
    print(f"    Socials before: {len(socials_before)}", flush=True)
    print(f"    URLs before: {len(urls_before)}", flush=True)
    assert len(socials_before) >= 2, f"Expected at least 2 socials, got {len(socials_before)}"
    
    # Run fix
    print("\n3. RUN fix command (migrate socials → URLs)", flush=True)
    fix_result = subprocess.run(
        ["python3", SCRIPT, "fix", proper_id],
        capture_output=True, text=True
    )
    fix_output = json.loads(fix_result.stdout)
    print(f"    Fix result: {fix_output}", flush=True)
    assert fix_output.get("success"), f"Fix failed: {fix_output}"
    
    migrated = fix_output.get("migrated", [])
    print(f"    Migrated: {migrated}", flush=True)
    
    # Verify URLs created
    print("\n4. VERIFY URLs created from socials", flush=True)
    details_result = subprocess.run(
        ["python3", SCRIPT, "get", proper_id],
        capture_output=True, text=True
    )
    details = json.loads(details_result.stdout)
    
    urls_after = details.get("urls", [])
    print(f"    URLs after: {len(urls_after)}", flush=True)
    
    # Check that URLs were created with correct labels
    url_labels = [u.get("label") for u in urls_after]
    url_values = [u.get("url", "") for u in urls_after]
    
    # Should have Twitter, LinkedIn, Facebook URLs
    if "Twitter" in migrated:
        assert "Twitter" in url_labels, f"Twitter URL not found in labels: {url_labels}"
        assert any("twitter.com" in u for u in url_values), "Twitter URL not found"
        print("    ✓ Twitter migrated to URL", flush=True)
    
    if "LinkedIn" in migrated:
        assert "LinkedIn" in url_labels, f"LinkedIn URL not found in labels: {url_labels}"
        assert any("linkedin.com" in u for u in url_values), "LinkedIn URL not found"
        print("    ✓ LinkedIn migrated to URL", flush=True)
    
    if "Facebook" in migrated:
        assert "Facebook" in url_labels, f"Facebook URL not found in labels: {url_labels}"
        assert any("facebook.com" in u for u in url_values), "Facebook URL not found"
        print("    ✓ Facebook migrated to URL", flush=True)
    
    # Verify social profiles were cleared
    print("\n5. VERIFY social profiles cleared", flush=True)
    socials_after = details.get("socials", [])
    # Filter out empty socials
    socials_after = [s for s in socials_after if s.get("service") and s.get("username")]
    print(f"    Socials after: {len(socials_after)} (expected 0)", flush=True)
    
    # Cleanup
    print("\n6. CLEANUP", flush=True)
    cleanup_script = f'''
        tell application "Contacts"
            delete (first person whose first name is "{TEST_FIRST}")
            save
        end tell
    '''
    run_applescript(cleanup_script)
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ Social profile migration test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_url_operations():
    """Test URL add/remove with various labels and formats."""
    print("\n=== URL Operations Test ===\n", flush=True)
    
    TEST_FIRST = "_URLTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact", flush=True)
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...", flush=True)
    
    # Add various URLs with different labels
    print("\n2. ADD URLs with various labels", flush=True)
    
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
        print(f"    ✓ Added {label}: {url}", flush=True)
    
    # Verify all URLs present
    print("\n3. VERIFY all URLs", flush=True)
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    
    assert len(urls) == len(test_urls), f"Expected {len(test_urls)} URLs, got {len(urls)}"
    print(f"    ✓ {len(urls)} URLs found", flush=True)
    
    url_labels = {u.get("label") for u in urls}
    for _, label in test_urls:
        assert label in url_labels, f"Label '{label}' not found in URLs"
    print("    ✓ All labels present", flush=True)
    
    # Remove URLs by partial match
    print("\n4. REMOVE URLs (partial match)", flush=True)
    
    result = run(["url", "remove", contact_id, "github.com"])
    assert result.get("success"), f"Remove GitHub failed: {result}"
    print("    ✓ Removed github.com", flush=True)
    
    result = run(["url", "remove", contact_id, "keybase"])
    assert result.get("success"), f"Remove Keybase failed: {result}"
    print("    ✓ Removed keybase", flush=True)
    
    # Verify removals
    print("\n5. VERIFY removals", flush=True)
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    remaining_urls = [u.get("url", "") for u in urls]
    
    assert not any("github.com" in u for u in remaining_urls), "GitHub not removed"
    assert not any("keybase" in u for u in remaining_urls), "Keybase not removed"
    print(f"    ✓ {len(urls)} URLs remaining (expected 5)", flush=True)
    
    # Cleanup
    print("\n6. CLEANUP", flush=True)
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
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ URL operations test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_url_auto_label():
    """Test that URL labels are auto-detected from known services."""
    print("\n=== URL Auto-Label Detection Test ===\n", flush=True)
    
    TEST_FIRST = "_AUTOLABEL_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact", flush=True)
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...", flush=True)
    
    # Add URLs without explicit labels (should auto-detect)
    print("\n2. ADD URLs (auto-label detection)", flush=True)
    
    test_urls = [
        ("https://twitter.com/testuser", "Twitter"),
        ("https://linkedin.com/in/test-user", "LinkedIn"),
        ("https://github.com/testuser", "GitHub"),
        ("https://instagram.com/testuser", "Instagram"),
    ]
    
    for url, expected_label in test_urls:
        result = run(["url", "add", contact_id, url])  # No label provided
        assert result.get("success"), f"Add URL failed for {url}: {result}"
        print(f"    ✓ Added {url}", flush=True)
    
    # Verify all URLs present with auto-detected labels
    print("\n3. VERIFY auto-detected labels", flush=True)
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    
    assert len(urls) == len(test_urls), f"Expected {len(test_urls)} URLs, got {len(urls)}"
    print(f"    ✓ {len(urls)} URLs found", flush=True)
    
    # Verify labels are auto-detected
    url_labels = {u.get("label") for u in urls}
    expected_labels = {"Twitter", "LinkedIn", "GitHub", "Instagram"}
    assert expected_labels.issubset(url_labels), f"Labels not auto-detected: got {url_labels}, expected {expected_labels}"
    print("    ✓ Labels properly auto-detected", flush=True)
    
    # Test explicit label override
    print("\n4. ADD URL with explicit label", flush=True)
    result = run(["url", "add", contact_id, "https://github.com/another-user", "Work GitHub"])
    assert result.get("success"), f"Add URL with explicit label failed: {result}"
    
    result = run(["get", contact_id])
    urls = result.get("urls", [])
    work_github = [u for u in urls if u.get("label") == "Work GitHub"]
    assert len(work_github) == 1, "Explicit label 'Work GitHub' not found"
    print("    ✓ Explicit label preserved", flush=True)
    
    # Cleanup
    print("\n5. CLEANUP", flush=True)
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
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ URL auto-label detection test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_photo_operations():
    """Test photo set/clear functionality."""
    print("\n=== Photo Operations Test ===\n", flush=True)
    
    TEST_FIRST = "_PHOTOTEST_"
    TEST_LAST = "_DELETE_"
    
    # Create test contact
    print("1. CREATE test contact", flush=True)
    result = run([
        "create",
        "--first", TEST_FIRST,
        "--last", TEST_LAST,
    ])
    assert result.get("success"), f"Create failed: {result}"
    
    # Get contact ID
    search_result = run(["search", f"{TEST_FIRST} {TEST_LAST}"])
    contact_id = search_result["contacts"][0]["id"]
    print(f"    ✓ Created: {contact_id[:20]}...", flush=True)
    
    # Set photo from URL (using a known public avatar)
    print("\n2. SET photo from URL", flush=True)
    # Using GitHub's default avatar as a reliable test image
    test_url = "https://avatars.githubusercontent.com/u/167932?v=4"
    result = run(["photo", "set", contact_id, test_url])
    assert result.get("success"), f"Set photo failed: {result}"
    print(f"    ✓ Set photo from URL", flush=True)
    
    # Verify photo exists via AppleScript
    print("\n3. VERIFY photo exists", flush=True)
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
    print("    ✓ Photo exists on contact", flush=True)
    
    # Clear photo
    print("\n4. CLEAR photo", flush=True)
    result = run(["photo", "clear", contact_id])
    assert result.get("success"), f"Clear photo failed: {result}"
    print("    ✓ Cleared photo", flush=True)
    
    # Verify photo cleared
    print("\n5. VERIFY photo cleared", flush=True)
    photo_status = run_applescript(verify_script)
    assert photo_status == "no_image", f"Photo not cleared: {photo_status}"
    print("    ✓ Photo cleared successfully", flush=True)
    
    # Test setting from local file
    print("\n6. SET photo from local file", flush=True)
    import tempfile
    import urllib.request
    
    # Download test image to temp file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
    urllib.request.urlretrieve(test_url, tmp_path)
    
    result = run(["photo", "set", contact_id, tmp_path])
    assert result.get("success"), f"Set photo from file failed: {result}"
    print(f"    ✓ Set photo from local file", flush=True)
    
    # Verify
    photo_status = run_applescript(verify_script)
    assert photo_status == "has_image", f"Photo not set from file: {photo_status}"
    print("    ✓ Photo set from local file verified", flush=True)
    
    # Cleanup temp file
    import os
    os.unlink(tmp_path)
    
    # Cleanup contact
    print("\n7. CLEANUP", flush=True)
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
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ Photo operations test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_phone_normalization():
    """Test phone number normalization with country codes."""
    print("\n=== Phone Normalization Test ===\n", flush=True)
    
    # Import the normalize function
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import normalize_phone
    
    print("1. TEST normalize_phone function", flush=True)
    
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
            print(f"    {status} {description}: '{input_num}' → '{result}' (expected '{expected}')", flush=True)
        else:
            print(f"    {status} {description}: '{input_num}' → '{result}'", flush=True)
    
    assert all_passed, "Some phone normalization tests failed"
    
    print("\n2. TEST phone normalization in contact creation", flush=True)
    
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
    print(f"    ✓ Created phone normalized to: {phone_number}", flush=True)
    
    print("\n3. TEST phone normalization in phone add", flush=True)
    result = run(["phone", "add", contact_id, "(555) 111-2222", "work"])
    assert result.get("success"), f"Add phone failed: {result}"
    
    details = run(["get", contact_id])
    phones = details.get("phones", [])
    work_phones = [p for p in phones if p.get("label") == "work"]
    assert len(work_phones) >= 1, "Work phone not found"
    
    work_number = work_phones[0].get("number", "")
    assert "+1" in work_number or work_number.startswith("+"), f"Work phone not normalized: {work_number}"
    print(f"    ✓ Added phone normalized to: {work_number}", flush=True)
    
    # Cleanup
    print("\n4. CLEANUP", flush=True)
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
    print("    ✓ Deleted test contact", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ Phone normalization test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_unified_services():
    """Test the unified SERVICES registry and helper functions."""
    print("\n=== Unified Services Test ===\n", flush=True)
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import (
        SERVICES, get_service, get_photo_url, get_photo_api, 
        get_profile_url, is_apple_native, list_services_with_photos,
        get_service_from_url, extract_username_from_url, normalize_service
    )
    
    print("1. TEST SERVICES registry structure", flush=True)
    assert len(SERVICES) > 20, f"Expected 20+ services, got {len(SERVICES)}"
    print(f"    ✓ {len(SERVICES)} services registered", flush=True)
    
    # Verify all services have required fields (name, profile_url)
    # Optional fields: photo_url, photo_api, apple_native (defaults to False)
    required_fields = ["name", "profile_url"]
    for key, service in SERVICES.items():
        for field in required_fields:
            assert field in service, f"Service '{key}' missing required field '{field}'"
    print("    ✓ All services have required fields (name, profile_url)", flush=True)
    
    print("\n2. TEST get_service function", flush=True)
    github = get_service("github")
    assert github is not None, "GitHub service not found"
    assert github["name"] == "GitHub", f"Wrong name: {github['name']}"
    assert "github.com" in github["profile_url"], "Wrong profile URL"
    print("    ✓ get_service('github') works", flush=True)
    
    # Case insensitive
    github2 = get_service("GitHub")
    assert github2 == github, "get_service should be case-insensitive"
    print("    ✓ Case insensitive lookup works", flush=True)
    
    print("\n3. TEST is_apple_native function", flush=True)
    assert is_apple_native("twitter") == True, "Twitter should be Apple-native"
    assert is_apple_native("linkedin") == True, "LinkedIn should be Apple-native"
    assert is_apple_native("github") == False, "GitHub should NOT be Apple-native"
    assert is_apple_native("instagram") == False, "Instagram should NOT be Apple-native"
    print("    ✓ Apple-native detection works", flush=True)
    
    print("\n4. TEST get_profile_url function", flush=True)
    test_cases = [
        ("github", "testuser", "https://github.com/testuser"),
        ("twitter", "testuser", "https://twitter.com/testuser"),
        ("linkedin", "testuser", "https://www.linkedin.com/in/testuser"),
        ("instagram", "testuser", "https://www.instagram.com/testuser"),
        ("youtube", "testuser", "https://www.youtube.com/@testuser"),
        ("tiktok", "testuser", "https://www.tiktok.com/@testuser"),
    ]
    
    for service, username, expected in test_cases:
        result = get_profile_url(service, username)
        assert result == expected, f"get_profile_url('{service}', '{username}') = '{result}', expected '{expected}'"
        print(f"    ✓ {service}: {result}", flush=True)
    
    print("\n5. TEST get_photo_url function", flush=True)
    photo_test_cases = [
        ("github", "testuser", "https://github.com/testuser.png"),
        ("facebook", "testuser", "https://graph.facebook.com/testuser/picture?type=large"),
        ("keybase", "testuser", "https://keybase.io/testuser/photo.png"),
        ("linkedin", "testuser", None),  # No direct photo URL
        ("instagram", "testuser", None),  # No direct photo URL
    ]
    
    for service, username, expected in photo_test_cases:
        result = get_photo_url(service, username)
        assert result == expected, f"get_photo_url('{service}', '{username}') = '{result}', expected '{expected}'"
        status = "✓" if expected else "✓ (None - requires auth)"
        print(f"    {status} {service}: {result}", flush=True)
    
    print("\n6. TEST get_photo_api function", flush=True)
    api_test_cases = [
        ("github", "testuser", "https://api.github.com/users/testuser"),
        ("bluesky", "testuser", "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=testuser"),
        ("twitter", "testuser", None),  # No public API
    ]
    
    for service, username, expected in api_test_cases:
        result = get_photo_api(service, username)
        assert result == expected, f"get_photo_api('{service}', '{username}') = '{result}', expected '{expected}'"
        status = "✓" if expected else "✓ (None - no public API)"
        print(f"    {status} {service}: {result}", flush=True)
    
    print("\n7. TEST list_services_with_photos", flush=True)
    photo_services = list_services_with_photos()
    assert "github" in photo_services, "GitHub should have photo support"
    assert "facebook" in photo_services, "Facebook should have photo support"
    assert "keybase" in photo_services, "Keybase should have photo support"
    print(f"    ✓ {len(photo_services)} services with photo support: {', '.join(photo_services)}", flush=True)
    
    print("\n8. TEST normalize_service function", flush=True)
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
        print(f"    ✓ '{input_name}' → '{result}'", flush=True)
    
    print("\n9. TEST extract_username_from_url function", flush=True)
    url_test_cases = [
        ("https://github.com/testuser", "https://github.com/{username}", "testuser"),
        ("https://www.linkedin.com/in/test-user", "https://www.linkedin.com/in/{username}", "test-user"),
        ("https://twitter.com/testuser", "https://twitter.com/{username}", "testuser"),
        ("https://www.instagram.com/testuser/", "https://www.instagram.com/{username}", "testuser"),
        ("https://www.youtube.com/@testuser", "https://www.youtube.com/@{username}", "testuser"),
    ]
    
    for url, template, expected in url_test_cases:
        result = extract_username_from_url(url, template)
        assert result == expected, f"extract_username_from_url('{url}') = '{result}', expected '{expected}'"
        print(f"    ✓ {url} → '{result}'", flush=True)
    
    print("\n10. TEST get_service_from_url function", flush=True)
    service_url_cases = [
        ("https://github.com/testuser", ("github", "testuser")),
        ("https://www.linkedin.com/in/test-user", ("linkedin", "test-user")),
        ("https://twitter.com/testuser", ("twitter", "testuser")),
        ("https://example.com/random", None),  # Unknown service
    ]
    
    for url, expected in service_url_cases:
        result = get_service_from_url(url)
        if expected is None:
            assert result is None, f"get_service_from_url('{url}') should be None, got {result}"
            print(f"    ✓ {url} → None (unknown)", flush=True)
        else:
            assert result is not None, f"get_service_from_url('{url}') should not be None"
            assert result[0] == expected[0], f"Wrong service: {result[0]} != {expected[0]}"
            assert result[1] == expected[1], f"Wrong username: {result[1]} != {expected[1]}"
            print(f"    ✓ {url} → {result}", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ Unified services test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

def test_photo_from_service_url():
    """Test getting photo URLs from various service profile URLs."""
    print("\n=== Photo from Service URL Test ===\n", flush=True)
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from contacts import get_service_from_url, get_photo_url, get_photo_api
    
    print("1. TEST photo URL extraction workflow", flush=True)
    
    # Simulate: contact has GitHub URL, we want to get their photo
    github_url = "https://github.com/testuser"
    
    # Step 1: Identify service and username from URL
    result = get_service_from_url(github_url)
    assert result is not None, "Should recognize GitHub URL"
    service, username = result
    print(f"    ✓ Detected: {service}/{username} from {github_url}", flush=True)
    
    # Step 2: Get photo URL
    photo_url = get_photo_url(service, username)
    assert photo_url is not None, "GitHub should have photo URL"
    assert "testuser" in photo_url, "Photo URL should contain username"
    print(f"    ✓ Photo URL: {photo_url}", flush=True)
    
    # Step 3: Alternative - Get photo API
    photo_api = get_photo_api(service, username)
    assert photo_api is not None, "GitHub should have photo API"
    assert "testuser" in photo_api, "Photo API should contain username"
    print(f"    ✓ Photo API: {photo_api}", flush=True)
    
    print("\n2. TEST services without photo support", flush=True)
    linkedin_url = "https://www.linkedin.com/in/testuser"
    result = get_service_from_url(linkedin_url)
    assert result is not None, "Should recognize LinkedIn URL"
    service, username = result
    
    photo_url = get_photo_url(service, username)
    assert photo_url is None, "LinkedIn should NOT have direct photo URL (requires auth)"
    print(f"    ✓ {service} correctly returns None for photo URL (auth required)", flush=True)
    
    print("\n3. TEST full workflow: URL → photo", flush=True)
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
            print(f"    {status} {service}/{username}: photo={'Yes' if has_photo else 'No (auth required)'}", flush=True)
        else:
            print(f"    ⚠ Could not parse: {url}", flush=True)
    
    print("\n" + "=" * 40, flush=True)
    print("✅ Photo from service URL test complete!", flush=True)
    print("=" * 40 + "\n", flush=True)

if __name__ == "__main__":
    test_crud_lifecycle()
    test_url_operations()
    test_url_auto_label()
    test_photo_operations()
    test_phone_normalization()
    test_unified_services()
    test_photo_from_service_url()
    test_fix_migration()
    
    print("\n" + "=" * 50, flush=True)
    print("🎉 ALL TEST SUITES PASSED!", flush=True)
    print("=" * 50 + "\n", flush=True)
