# utils/check_admin.py
try:
    from config import ADMIN_IDS  # preferred
except Exception:
    # fallback if some places still define only ADMIN_ID
    try:
        from config import ADMIN_ID
        ADMIN_IDS = [ADMIN_ID]
    except Exception:
        ADMIN_IDS = []

def is_admin(user_id: int) -> bool:
    return int(user_id) in {int(x) for x in ADMIN_IDS}
