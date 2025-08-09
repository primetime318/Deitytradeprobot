# commands/alert_router.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.tier import get_tier, 

alert_router = Router(name="alerts")

def build_hedge_entries(tier: Tier) -> list[str]:
    base = [
        "BTC: ladder 0.25% @ 64,250 / 63,900 • invalidation 63,400",
    ]
    alpha_extra = [
        "ETH: stagger 0.3% @ 2,430 / 2,405 • stop 2,380",
    ]
    god_extra = [
        "SOL: micro-hedge 0.2% @ 167.2 • expand 165.8 if vol ↑",
        "Note: widen stops if funding > 0.05%",
    ]
    if tier == Tier.FREE:
        return base[:1]
    if tier == Tier.ALPHA:
        return base + alpha_extra
    return base + alpha_extra + god_extra

@alert_router.message(Command("hedgedrop"))
async def cmd_hedgedrop(message: Message):
    tier = get_tier(message.from_user.id if message.from_user else 0)
    header = "🛡️ Hedge Drop"
    sub = f"Tier: <b>{tier.value.title()}</b>"
    body = "\n".join(build_hedge_entries(tier))
    tip = "\n\nUse /hedgeplan BTC or /hedgeplan ETH for tailored plan."
    await message.answer(f"{header}\n{sub}\n\n{body}{tip}", parse_mode="HTML")
