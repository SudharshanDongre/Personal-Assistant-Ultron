#!/usr/bin/env python3
"""Test script for PHASE 5: User Management"""

import users
import os
import json


def test_user_management():
    print("=" * 60)
    print("PHASE 5: USER MANAGEMENT IMPLEMENTATION TEST")
    print("=" * 60)

    # Test 1: Get current user
    print("\n✓ Test 1: Get current user")
    current = users.get_current_user()
    print(f"  Current user: {current}")
    assert current == "default", "Default user not set"

    # Test 2: List users
    print("\n✓ Test 2: List all users")
    user_list = users.list_users()
    print(f"  Registered users: {user_list}")
    assert "default" in user_list, "Default user not in list"

    # Test 3: Load default user preferences
    print("\n✓ Test 3: Load default user preferences")
    prefs = users.load_user_preferences("default")
    print(f"  Preferences keys: {list(prefs.keys())}")
    print(f"  Response style: {prefs.get('response_style')}")
    assert "user_id" in prefs, "user_id not in preferences"

    # Test 4: Create new user
    print("\n✓ Test 4: Create new user 'developer'")
    result = users.create_user("developer", {
        "work_style": "code_first",
        "response_style": "technical"
    })
    print(f"  Creation successful: {result}")
    assert "developer" in users.list_users(), "Developer user not created"

    # Test 5: Switch user
    print("\n✓ Test 5: Switch to 'developer' user")
    result = users.switch_user("developer")
    print(f"  Switch successful: {result}")
    assert users.get_current_user() == "developer", "Switch failed"

    # Test 6: Get user context
    print("\n✓ Test 6: Get user context for 'developer'")
    context = users.get_user_context("developer")
    print(f"  User name: {context.get('name')}")
    print(f"  Preferences: {context.get('preferences')}")

    # Test 7: Save updated preferences
    print("\n✓ Test 7: Save updated preferences")
    updated = users.load_user_preferences("developer")
    updated["preferred_voice_speed"] = 180
    updated["learning_enabled"] = True
    result = users.save_user_preferences("developer", updated)
    print(f"  Save successful: {result}")

    # Test 8: Verify preferences file
    print("\n✓ Test 8: Verify preferences file on disk")
    prefs_file = os.path.join("user_data", "developer", "preferences.json")
    assert os.path.exists(prefs_file), "Preferences file not created"
    with open(prefs_file, "r") as f:
        saved_prefs = json.load(f)
    print(f"  File exists: {prefs_file}")
    print(f"  Voice speed saved: {saved_prefs.get('preferred_voice_speed')}")
    assert saved_prefs.get("preferred_voice_speed") == 180

    # Test 9: Verify directory structure
    print("\n✓ Test 9: Verify user directory structure")
    dev_dir = os.path.join("user_data", "developer")
    assert os.path.isdir(dev_dir), "User directory not created"
    assert os.path.isdir(os.path.join(dev_dir, "documents")), "Documents dir not created"
    print(f"  Developer directory structure created successfully")

    # Test 10: Switch back to default
    print("\n✓ Test 10: Switch back to default user")
    users.switch_user("default")
    assert users.get_current_user() == "default"
    print(f"  Back to default user: {users.get_current_user()}")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - PHASE 5 IMPLEMENTATION SUCCESSFUL!")
    print("=" * 60)


if __name__ == "__main__":
    test_user_management()
