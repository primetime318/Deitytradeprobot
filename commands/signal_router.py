# commands/signal_router.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

signal_router = Router(name="signals")
from utils.tier import get_tier, Tier, is_admin
def build_signals_for_tier(tier: Tier) -> list[str]:
    base = [
        "• BTC: momentum ↑; prefer pullback buys on M30–H1",
        "• ETH: range → watch 1,950/1,980 flips",
    ]
    alpha_extra = [
        "• SOL: VWAP reclaim → scalp bias long",
    ]
    god_extra = [
        "• Risk: funding tilt incoming; reduce size on spikes",
        "• Corr: ETH/BTC beta ↑ → skew hedges 60/40",
    ]
    if tier == Tier.FREE:
        return base[:1]          # teaser for Free
    if tier == Tier.ALPHA:
        return base + alpha_extra
    return base + alpha_extra + god_extra  # God

@signal_router.message(Command("signals"))
async def cmd_signals(message: Message):
    tier = get_tier(message.from_user.id if message.from_user else 0)
    lines = build_signals_for_tier(tier)
    header = "📈 Signals Snapshot"
    sub = f"Tier: <b>{tier.value.title()}</b>"
    body = "\n".join(lines)
    tip = "\n\nTip: /hedgeplan BTC  |  /riskdrop"
    await message.answer(f"{header}\n{sub}\n\n{body}{tip}", parse_mode="HTML")
    # =========================
# Admin-Only Utility Commands
# =========================

from aiogram.filters import Command
from aiogram.types import Message
from utils.tier import is_admin  # Make sure utils/tier.py exists as shown earlier

# /forcesignal — Trigger manual signal drop
@signal_router.message(Command("forcesignal"))
async def cmd_force_signal(message: Message):
    if not is_admin(message):
        return await message.answer("⛔ You are not authorized to use this command.")
    # Replace the line below with your real signal logic
    await message.answer("🛠 Manual signal push triggered...")

# /forcehedge — Trigger manual hedge drop
@signal_router.message(Command("forcehedge"))
async def cmd_force_hedge(message: Message):
    if not is_admin(message):
        return await message.answer("⛔ You are not authorized to use this command.")
    # Replace the line below with your real hedge drop logic
    await message.answer("🛠 Manual hedge drop triggered...")

# /devon — Developer utility command
@signal_router.message(Command("devon"))
async def cmd_devon(message: Message):
    if not is_admin(message):
        return await message.answer("⛔ You are not authorized to use this command.")
    await message.answer("🧪 Developer mode active. Awaiting further instructions.")