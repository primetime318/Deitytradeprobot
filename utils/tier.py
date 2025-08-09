# utils/tier.py

import json
import os

TIERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")

# Your Telegram user IDs that should be treated as bot admins
ADMINS = [
    6860530316  # <-- Your ID
]

def load_tiers():
    if not os.path.exists(TIERS_FILE):
        return {}
    with open(TIERS_FILE, "r") as f:
        return json.load(f)

def save_tiers(tiers):
    with open(TIERS_FILE, "w") as f:
        json.dump(tiers, f, indent=4)

def get_tier(user_id: int):
    tiers = load_tiers()
    return tiers.get(str(user_id), "Free")  # Default to Free tier

def set_tier(user_id: int, tier: str):
    tiers = load_tiers()
    tiers[str(user_id)] = tier
    save_tiers(tiers)

def is_admin(user_id: int) -> bool:
    """Check if a given user ID is an admin."""
    return user_id in ADMINS
