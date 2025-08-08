# alert_router.py
import json
import logging
from pathlib import Path

# Injected by main.py
BOT = None

# tiers.json will hold your chat IDs per tier
TIERS_PATH = Path("tiers.json")

_cache = {
    "DEFAULT_GROUP_ID": None,
    "TIERS": {}
}

def _load():
    global _cache
    try:
        data = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
        _cache["DEFAULT_GROUP_ID"] = data.get("DEFAULT_GROUP_ID")
        _cache["TIERS"] = data.get("TIERS", {})
    except Exception as e:
        logging.warning(f"[alert_router] Could not load tiers.json: {e}. Using defaults.")
        # If tiers.json missing, everything falls back to DEFAULT_GROUP_ID=None

def _get_chat_id(tier: str | None) -> int | None:
    if not _cache["TIERS"] and _cache["DEFAULT_GROUP_ID"] is None:
        _load()
    if tier:
        # normalize like "T1", "ALPHA", "alpha", etc.
        key = str(tier).strip().upper()
        if key in _cache["TIERS"]:
            return _cache["TIERS"][key]
    return _cache["DEFAULT_GROUP_ID"]

async def send(text: str, tier: str | None = None, parse_mode: str | None = "Markdown", disable_web_page_preview: bool = True):
    """
    Sends a message to the tier's chat if configured, otherwise to DEFAULT_GROUP_ID.
    If no chat is configured at all, silently no-ops (but logs warning).
    """
    chat_id = _get_chat_id(tier)
    if chat_id is None:
        logging.warning("[alert_router] No chat configured for tier=%s and no DEFAULT_GROUP_ID. Message suppressed.", tier)
        return
    try:
        await BOT.send_message(chat_id, text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        logging.exception("[alert_router] Failed to send message: %s", e)

async def announce_active(service_name: str):
    """
    Sends a one-time 'active' message to DEFAULT_GROUP_ID (good for boot logs).
    """
    chat_id = _get_chat_id(None)  # DEFAULT_GROUP_ID
    if chat_id is None:
        return
    try:
        await BOT.send_message(chat_id, f"✅ {service_name} is active.")
    except Exception:
        pass