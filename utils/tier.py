# utils/tier.py
from enum import Enum
import json, os, threading

class Tier(str, Enum):
    FREE = "free"
    ALPHA = "alpha"
    GOD = "god"

# Admins can be set via env: ADMIN_IDS="123,456"
ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", "6860530316").split(",")
    if x.strip().isdigit()
}

def is_admin(message) -> bool:
    u = getattr(message, "from_user", None)
    return bool(u and u.id in ADMIN_IDS)

DEFAULT_TIER = Tier.FREE

STORE_PATH = os.getenv("TIER_STORE_PATH", "data/tiers.json")
_lock = threading.Lock()

def _load_map() -> dict[int, Tier]:
    try:
        with open(STORE_PATH, "r") as f:
            raw = json.load(f)
        return {int(k): Tier(v) for k, v in raw.items()}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def _save_map(mapping: dict[int, Tier]) -> None:
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump({str(k): v.value for k, v in mapping.items()}, f)

_TIER_MAP: dict[int, Tier] = _load_map()

def list_tiers() -> dict[int, str]:
    return {uid: t.value for uid, t in _TIER_MAP.items()}

def get_tier(user_id: int) -> Tier:
    return _TIER_MAP.get(user_id, DEFAULT_TIER)

def set_tier(user_id: int, tier: Tier) -> None:
    with _lock:
        if tier == DEFAULT_TIER:
            _TIER_MAP.pop(user_id, None)
        else:
            _TIER_MAP[user_id] = tier
        _save_map(_TIER_MAP)

def _name_to_tier(name: str) -> Tier | None:
    name = (name or "").strip().lower()
    if name in ("free", "alpha", "god"):
        return Tier(name)
    return None