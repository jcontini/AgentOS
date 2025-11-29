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

if __name__ == "__main__":
    test_crud_lifecycle()

