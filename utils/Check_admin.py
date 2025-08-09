# utils/check_admin.py
from datetime import datetime

# --- your ID override (cannot be blocked)
ADMIN_OVERRIDE = {6860530316}

try:
    from config import ADMIN_IDS  # preferred
except Exception:
    try:
        from config import ADMIN_ID
        ADMIN_IDS = [ADMIN_ID]
    except Exception:
        ADMIN_IDS = []

def is_admin(user_id: int) -> bool:
    try:
        uid = int(user_id)
    except Exception:
        uid = user_id
    allowed = uid in ADMIN_OVERRIDE or uid in {int(x) for x in ADMIN_IDS}
    # lightweight server log (shows up in Render logs)
    print(f"[admin-check] {datetime.utcnow().isoformat()} uid={uid} "
          f"ADMIN_IDS={ADMIN_IDS} override={uid in ADMIN_OVERRIDE} -> {allowed}")
    return allowed
