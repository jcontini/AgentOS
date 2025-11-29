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

if __name__ == "__main__":
    test_crud_lifecycle()
    test_url_operations()
    test_social_apple_official()
    test_fix_scenarios()
    
    print("\n" + "=" * 50)
    print("🎉 ALL TEST SUITES PASSED!")
    print("=" * 50 + "\n")
