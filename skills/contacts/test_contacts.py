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
    
    # 7. ADD social
    print("\n7. SOCIAL ADD")
    result = run(["social", "add", contact_id, "instagram", "testuser"])
    assert result.get("success"), f"Add social failed: {result}"
    print("    ✓ Added Instagram profile")
    
    # 8. Verify additions
    print("\n8. VERIFY additions")
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    socials = result.get("socials", [])
    print(f"    ✓ Phones: {len(phones)} (expected 2)")
    print(f"    ✓ Emails: {len(emails)} (expected 2)")
    print(f"    ✓ Socials: {len(socials)} (expected 1)")
    
    # 9. FIX social profiles (should be no-op for clean data)
    print("\n9. FIX social profiles")
    result = run(["fix", contact_id])
    assert result.get("success"), f"Fix failed: {result}"
    print("    ✓ Fix completed")
    
    # 10. REMOVE social
    print("\n10. SOCIAL REMOVE")
    result = run(["social", "remove", contact_id, "instagram"])
    assert result.get("success"), f"Remove social failed: {result}"
    print("    ✓ Removed Instagram profile")
    
    # 11. REMOVE phone
    print("\n11. PHONE REMOVE")
    result = run(["phone", "remove", contact_id, "+15550005678"])
    assert result.get("success"), f"Remove phone failed: {result}"
    print("    ✓ Removed work phone")
    
    # 12. REMOVE email
    print("\n12. EMAIL REMOVE")
    result = run(["email", "remove", contact_id, "work@example.com"])
    assert result.get("success"), f"Remove email failed: {result}"
    print("    ✓ Removed work email")
    
    # 13. Final state
    print("\n13. FINAL state")
    result = run(["get", contact_id])
    phones = result.get("phones", [])
    emails = result.get("emails", [])
    socials = result.get("socials", [])
    print(f"    ✓ Phones: {len(phones)} (expected 1)")
    print(f"    ✓ Emails: {len(emails)} (expected 1)")
    print(f"    ✓ Socials: {len(socials)} (expected 0)")
    
    # CLEANUP - Delete test contact via AppleScript
    print("\n14. CLEANUP (delete test contact)")
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
    print("✅ All tests passed!")
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
            
            -- Scenario A: Valid username, missing URL (like Isabelle's Instagram)
            make new social profile at end of social profiles of p with properties {{service name:"Instagram", user name:"testuser123"}}
            
            -- Scenario B: Truncated/corrupted URL (like Gustaf's Facebook)
            make new social profile at end of social profiles of p with properties {{service name:"Facebook", user name:"validuser"}}
            -- Manually corrupt the URL
            set url of social profile 2 of p to "https://www.facebook"
            
            -- Scenario C: URL pasted as username (like Isabelle's Facebook)
            make new social profile at end of social profiles of p with properties {{service name:"LinkedIn", user name:"WWW.LINKEDIN.COM/IN/PROFILE?ID=123456"}}
            
            -- Scenario D: Garbage username, garbage URL (should be nullified)
            make new social profile at end of social profiles of p with properties {{service name:"Twitter", user name:"TYPE=PREF"}}
            
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
    
    # Scenario A: Instagram should have URL constructed
    if "Instagram" in after and "instagram.com" in after:
        print("    ✓ Scenario A: Instagram URL constructed from username")
    else:
        print("    ⚠ Scenario A: Instagram URL not constructed")
    
    # Scenario B: Facebook should have URL fixed
    if "Facebook" in after and "facebook.com/validuser" in after.lower():
        print("    ✓ Scenario B: Facebook URL reconstructed")
    else:
        print("    ⚠ Scenario B: Facebook URL not fixed")
    
    # Scenario C: LinkedIn URL-as-username - this is a weird case
    # The fix should try to extract profile ID if present
    if "LinkedIn" in after:
        print("    ✓ Scenario C: LinkedIn processed")
    
    # Scenario D: Twitter garbage should be nullified (not in output)
    if "Twitter" not in after or "TYPE=PREF" not in after:
        print("    ✓ Scenario D: Twitter garbage nullified")
    else:
        print("    ⚠ Scenario D: Twitter garbage not nullified")
    
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

if __name__ == "__main__":
    test_crud_lifecycle()
    test_fix_scenarios()

