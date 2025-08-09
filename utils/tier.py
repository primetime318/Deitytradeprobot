# src/utils/tier.py

import json
import os
from typing import Dict

# tiers are stored here as: { "123456789": "Alpha", ... }
TIERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")

# Your admin(s) – add more IDs if needed
ADMINS = {6860530316}

def _ensure_store():
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
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

def get_tier(user_id: int) -> str:
    tiers = load_tiers()
    return tiers.get(str(user_id), "Free")

def set_tier(user_id: int, tier: str) -> None:
    tiers = load_tiers()
    tiers[str(user_id)] = tier
    save_tiers(tiers)

def is_admin(user_id: int) -> bool:
    # single source of truth for admin checks
    try:
        uid = int(user_id)
    except Exception:
        return False
    return uid in ADMINS
