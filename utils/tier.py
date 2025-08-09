# utils/tier.py
# --- admin config (explicit) ---
ADMIN_ID = 6860530316
ADMIN_IDS = [ADMIN_ID]
# --------------------------------
import json
from enum import Enum
from pathlib import Path
from aiogram.types import Message
# utils/tier.py

def _name_to_tier(name: str):
    """
    Convert a tier name to its internal tier representation.
    Example: 'godmode' -> 'GodMode', 'alpha' -> 'Alpha'
    """
    tiers = {
        "free": "Free",
        "alpha": "Alpha",
        "godmode": "GodMode"
    }
    return tiers.get(name.lower())

TIERS_FILE = Path("data/tiers.json")
TIERS_FILE.parent.mkdir(parents=True, exist_ok=True)

class Tier(Enum):
    FREE = "free"
    ALPHA = "alpha"
    GOD = "god"

def _load() -> dict[str, str]:
    if TIERS_FILE.exists():
        try:
            return json.loads(TIERS_FILE.read_text())
        except Exception:
            return {}
    return {}

def _save(d: dict[str, str]) -> None:
    TIERS_FILE.write_text(json.dumps(d, indent=2))

def get_tier(user_id: int) -> Tier:
    data = _load()
    name = data.get(str(user_id), "free")
    try:
        return Tier(name)
    except Exception:
        return Tier.FREE

def set_tier(user_id: int, tier: Tier) -> None:
    data = _load()
    data[str(user_id)] = tier.value
    _save(data)

def list_tiers() -> dict[int, str]:
    return {int(k): v for k, v in _load().items()}

def is_admin(message: Message) -> bool:
    # Owner is always admin; add more IDs here if you like
    try:
        owner_id = int(message.bot['owner_id']) if 'owner_id' in message.bot else None
    except Exception:
        owner_id = None
    uid = message.from_user.id if message.from_user else 0
    return owner_id is not None and uid == owner_id

# Helper: check if user's tier meets a minimum
def meets(user_id: int, minimum: Tier) -> bool:
    order = [Tier.FREE, Tier.ALPHA, Tier.GOD]
    u = get_tier(user_id)
    return order.index(u) >= order.index(minimum)
