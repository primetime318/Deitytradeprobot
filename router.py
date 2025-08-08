# router.py
# Tier-aware router for sending alerts to the right chats with gating

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from aiogram import Router, types
from aiogram.filters import Command
from smart_signals import format_top_cryptos

router = Router()

@router.message(Command("topcoins"))
async def top_coins_handler(message: types.Message):
    try:
        text = format_top_cryptos()
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠️ Error fetching top coins: {e}")

TIERS_FILE = Path("tiers.json")

class TierRouter:
    """
    Reads tiers.json and routes alerts to the correct chats.
    Enforces per-tier rules:
      - allowed chains
      - min_usd_buy
      - delay_seconds (cooldown between messages sent to that chat)
    """

    def __init__(self, bot):
        self.bot = bot
        self.cfg: Dict[str, Any] = {}
        self.last_sent: Dict[int, float] = {}  # chat_id -> last send timestamp (seconds)
        self.reload()

    # ---------- config ----------
    def reload(self) -> None:
        if TIERS_FILE.exists():
            self.cfg = json.loads(TIERS_FILE.read_text())
        else:
            # Minimal safe default if file missing
            self.cfg = {
                "DEFAULT_GROUP_ID": None,
                "tiers": {
                    "free":      {"wallet_limit": 10,  "chains": ["eth"],               "min_usd_buy": 50000, "delay_seconds": 1800},
                    "standard":  {"wallet_limit": 25,  "chains": ["eth"],               "min_usd_buy": 25000, "delay_seconds": 900},
                    "alpha":     {"wallet_limit": 75,  "chains": ["eth","btc","xrp"],   "min_usd_buy": 10000, "delay_seconds": 60},
                    "godmode":   {"wallet_limit": 200, "chains": ["eth","btc","xrp"],   "min_usd_buy": 0,     "delay_seconds": 0},
                },
                "users": {},
                "groups": {}
            }

    # ---------- helpers ----------
    def _tier_for_chat(self, chat_id: int) -> Optional[str]:
        groups: Dict[str, str] = self.cfg.get("groups", {})
        # JSON keys are strings; normalize
        return groups.get(str(chat_id))

    def _rules_for_tier(self, tier: str) -> Optional[Dict[str, Any]]:
        tiers = self.cfg.get("tiers") or self.cfg.get("TIERS")  # support both casings
        if not tiers:
            return None
        return tiers.get(tier)

    def _cooldown_ok(self, chat_id: int, delay_seconds: int) -> bool:
        if delay_seconds <= 0:
            return True
        now = time.time()
        last = self.last_sent.get(chat_id, 0)
        return (now - last) >= delay_seconds

    def _mark_sent(self, chat_id: int) -> None:
        self.last_sent[chat_id] = time.time()

    # ---------- public API ----------
    async def send(self, *, chain: str, est_usd: float, text: str) -> None:
        """
        Route one alert to all eligible group chats.
        Fallback to DEFAULT_GROUP_ID if no group rule matches.
        """
        chain = (chain or "").lower()
        sent_any = False

        groups_map: Dict[str, str] = self.cfg.get("groups", {})
        # Iterate over configured groups and apply gating per group
        for gid_str, tier_name in groups_map.items():
            try:
                chat_id = int(gid_str)
            except ValueError:
                continue

            rules = self._rules_for_tier(tier_name or "")
            if not rules:
                continue

            # Chain gating
            if chain and rules.get("chains") and chain not in [c.lower() for c in rules["chains"]]:
                continue

            # Min USD gating
            min_usd = float(rules.get("min_usd_buy", 0))
            if est_usd is not None and est_usd < min_usd:
                continue

            # Cooldown gating
            delay = int(rules.get("delay_seconds", 0))
            if not self._cooldown_ok(chat_id, delay):
                continue

            # Send
            try:
                await self.bot.send_message(chat_id, text)
                self._mark_sent(chat_id)
                sent_any = True
            except Exception as e:
                # Don’t crash routing; just keep going
                print(f"[router] send error to {chat_id}: {e}")

        # Fallback if nothing matched/sent
        if not sent_any:
            default_gid = self.cfg.get("DEFAULT_GROUP_ID")
            if default_gid:
                try:
                    await self.bot.send_message(int(default_gid), text)
                except Exception as e:
                    print(f"[router] fallback send error to {default_gid}: {e}")

    # Backward compatible name if you wired route_alert earlier
    async def route_alert(self, *, chain: str, usd_value: float, text: str) -> None:
        await self.send(chain=chain, est_usd=usd_value, text=text)
        from aiogram import Router

command_router = Router()

# Example handler (if none exist yet)
@command_router.message()
async def handle_default(message):
    await message.answer("Command router is working.")