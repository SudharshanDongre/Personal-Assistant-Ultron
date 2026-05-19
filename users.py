"""User Management Module - PHASE 5

Handles user profiles, switching, and personalization.

Functions:
  - get_current_user()
  - switch_user(user_id)
  - create_user(user_id, preferences)
  - get_user_context(user_id)
  - load_user_preferences(user_id)
  - save_user_preferences(user_id, preferences)
"""

import os
import json
from typing import Dict, Optional, Any

# Global state
CURRENT_USER = "default"

# User profiles: user_id -> profile data
USER_PROFILES = {
    "default": {
        "name": "Sudarshan Sir",
        "preferences": {},
    }
}

# Path to user data directory
USER_DATA_DIR = "user_data"


def ensure_user_directory(user_id: str) -> str:
    """Ensure user data directory exists. Returns path."""
    user_path = os.path.join(USER_DATA_DIR, user_id)
    os.makedirs(user_path, exist_ok=True)
    os.makedirs(os.path.join(user_path, "documents"), exist_ok=True)
    return user_path


def get_current_user() -> str:
    """Return the currently active user ID."""
    global CURRENT_USER
    return CURRENT_USER


def switch_user(user_id: str) -> bool:
    """
    Switch to a different user.
    
    Args:
        user_id: The user ID to switch to
        
    Returns:
        True if switch successful, False if user doesn't exist
    """
    global CURRENT_USER
    
    if user_id not in USER_PROFILES:
        print(f"User '{user_id}' not found. Creating new profile...")
        create_user(user_id, {})
    
    CURRENT_USER = user_id
    print(f"Switched to user: {user_id}")
    return True


def create_user(user_id: str, preferences: Optional[Dict[str, Any]] = None) -> bool:
    """
    Create a new user profile.
    
    Args:
        user_id: Unique user identifier
        preferences: Optional user preferences dictionary
        
    Returns:
        True if created successfully
    """
    if user_id in USER_PROFILES:
        print(f"User '{user_id}' already exists")
        return False
    
    # Create profile
    USER_PROFILES[user_id] = {
        "name": user_id.capitalize(),
        "preferences": preferences or {},
    }
    
    # Create user directory structure
    ensure_user_directory(user_id)
    
    # Initialize empty preferences file
    prefs_path = os.path.join(USER_DATA_DIR, user_id, "preferences.json")
    save_user_preferences(user_id, preferences or {})
    
    print(f"Created user profile: {user_id}")
    return True


def get_user_context(user_id: str) -> Dict[str, Any]:
    """
    Load all user metadata and preferences.
    
    Args:
        user_id: The user ID to load context for
        
    Returns:
        Dictionary with user context (name, preferences, etc.)
    """
    if user_id not in USER_PROFILES:
        raise ValueError(f"User '{user_id}' not found")
    
    context = dict(USER_PROFILES[user_id])
    
    # Try to load preferences from file
    try:
        prefs_path = os.path.join(USER_DATA_DIR, user_id, "preferences.json")
        if os.path.exists(prefs_path):
            with open(prefs_path, "r") as f:
                context["preferences"] = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load preferences for {user_id}: {e}")
    
    return context


def load_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Load user preferences from file.
    
    Args:
        user_id: The user ID to load preferences for
        
    Returns:
        User preferences dictionary
    """
    prefs_path = os.path.join(USER_DATA_DIR, user_id, "preferences.json")
    
    if not os.path.exists(prefs_path):
        # Return default preferences
        return {
            "user_id": user_id,
            "response_style": "helpful",
            "preferred_voice_speed": 160,
            "learning_enabled": True,
        }
    
    try:
        with open(prefs_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return {}


def save_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to file.
    
    Args:
        user_id: The user ID to save preferences for
        preferences: The preferences dictionary to save
        
    Returns:
        True if saved successfully
    """
    user_path = ensure_user_directory(user_id)
    prefs_path = os.path.join(user_path, "preferences.json")
    
    try:
        # Ensure user_id is in preferences
        preferences["user_id"] = user_id
        
        with open(prefs_path, "w") as f:
            json.dump(preferences, f, indent=2)
        
        # Update in-memory profile
        if user_id in USER_PROFILES:
            USER_PROFILES[user_id]["preferences"] = preferences
        
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False


def list_users() -> list:
    """Return list of all registered users."""
    return list(USER_PROFILES.keys())


def get_user_info(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile information."""
    return USER_PROFILES.get(user_id)


def delete_user(user_id: str) -> bool:
    """
    Delete a user profile.
    
    Args:
        user_id: The user ID to delete
        
    Returns:
        True if deleted successfully
    """
    global CURRENT_USER
    
    if user_id not in USER_PROFILES:
        print(f"User '{user_id}' not found")
        return False
    
    if user_id == "default":
        print("Cannot delete default user")
        return False
    
    # Switch to default if deleting current user
    if CURRENT_USER == user_id:
        CURRENT_USER = "default"
    
    # Remove from profiles
    del USER_PROFILES[user_id]
    
    # Note: You might want to also delete user_data directory here
    # Uncomment below if desired:
    # import shutil
    # user_path = os.path.join(USER_DATA_DIR, user_id)
    # if os.path.exists(user_path):
    #     shutil.rmtree(user_path)
    
    print(f"Deleted user: {user_id}")
    return True


# Initialize default user directory on import
ensure_user_directory("default")
