import json
import os

TIERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'tiers.json')

def load_tiers():
    if not os.path.exists(TIERS_FILE):
        return {}
    with open(TIERS_FILE, 'r') as f:
        return json.load(f)

def save_tiers(tiers):
    with open(TIERS_FILE, 'w') as f:
        json.dump(tiers, f, indent=4)

def get_tier(user_id):
    tiers = load_tiers()
    return tiers.get(str(user_id), "Free")

def set_tier(user_id, tier):
    tiers = load_tiers()
    tiers[str(user_id)] = tier
    save_tiers(tiers)

def list_tiers():
    """Return a list of all user_id: tier pairs."""
    return load_tiers()
