# src/utils/tier.py

import json
import os
from enum import Enum
from typing import Dict

# ---------- Constants & paths ----------
DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
TIERS_PATH = os.path.join(DATA_DIR, "tiers.json")

# Your admin IDs (add more if needed)
ADMIN_IDS = {6860530316}

# ---------- Tier enum (kept for compatibility) ----------
class Tier(str, Enum):
    FREE = "Free"
    ALPHA = "Alpha"
    GODMODE = "GodMode"

# ---------- Storage helpers ----------
def _ensure_store() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(TIERS_PATH):
        with open(TIERS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_tiers() -> Dict[str, str]:
    _ensure_store()
    with open(TIERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tiers(tiers: Dict[str, str]) -> None:
    _ensure_store()
    tmp = TIERS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tiers, f, indent=2, ensure_ascii=False)
    os.replace(tmp, TIERS_PATH)

# ---------- Public API used around the bot ----------
def get_tier(user_id: int) -> str:
    """Return the user's tier name; defaults to 'Free'."""
    tiers = load_tiers()
    return tiers.get(str(user_id), Tier.FREE.value)

def set_tier(user_id: int, tier: str) -> None:
    """Persist a user's tier."""
    tiers = load_tiers()
    tiers[str(user_id)] = tier
    save_tiers(tiers)

def list_tiers() -> Dict[str, str]:
    """Return the full mapping {user_id: tier}."""
    return load_tiers()

def is_admin(user_id: int) -> bool:
    """Single source-of-truth admin check."""
    try:
        return int(user_id) in ADMIN_IDS
    except Exception:
        return False
