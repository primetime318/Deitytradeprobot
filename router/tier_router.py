# router/tier_router.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from html import escape as quote_html  # Using Python built-in escape

from utils.tier import (
    Tier,
    get_tier,
    set_tier,
    list_tiers,
    is_admin,
    _name_to_tier,  # internal helper is fine to reuse here
)

tier_router = Router(name="tier")


@tier_router.message(Command("tier"))
async def cmd_tier(message: Message):
    """Show the caller's current tier."""
    uid = message.from_user.id if message.from_user else 0
    t = get_tier(uid)
    tier_text = quote_html(t.value.title())
    await message.answer(f"🏷 Your tier: <b>{tier_text}</b>", parse_mode="HTML")


@tier_router.message(Command("settier"))
async def cmd_settier(message: Message):
    """
    Admin only.
    Usage:
        /settier <user_id> <free|alpha|god>
    Or reply to a user's message with:
        /settier <free|alpha|god>
    """
    if not is_admin(message):
        return await message.answer("⛔ You are not authorized to use this command.")

    text = (message.text or "").strip()
    parts = text.split(maxsplit=2)

    target_id = None
    tier_name = None

    # Case 1: /settier <user_id> <tier>
    if len(parts) == 3:
        _, uid_str, tier_name = parts
        if uid_str.isdigit():
            target_id = int(uid_str)

    # Case 2: reply + /settier <tier>
    if target_id is None and message.reply_to_message and len(parts) == 2:
        target_id = (
            message.reply_to_message.from_user.id
            if message.reply_to_message.from_user
            else None
        )
        tier_name = parts[1]

    if target_id is None or not tier_name:
        return await message.answer(
            "❗ Usage: /settier <user_id> <free|alpha|god>  (or reply with /settier <tier>)"
        )

    tier = _name_to_tier(tier_name)
    if tier is None:
        return await message.answer("❗ Tier must be one of: free, alpha, god")

    set_tier(target_id, tier)
    tier_text = quote_html(tier.value.title())
    await message.answer(
        f"✅ Set tier for <code>{target_id}</code> to <b>{tier_text}</b>.",
        parse_mode="HTML",
    )


@tier_router.message(Command("tiers"))
async def cmd_tiers(message: Message):
    """List all tier mappings (admin only)."""
    if not is_admin(message):
        return await message.answer("⛔ You are not authorized to use this command.")

    data = list_tiers()
    if not data:
        return await message.answer("ℹ️ No custom tiers set yet.")

    lines = [
        f"• <code>{uid}</code>: {quote_html(name.title())}"
        for uid, name in sorted(data.items())
    ]
    await message.answer("🧾 <b>Tiers</b>\n" + "\n".join(lines), parse_mode="HTML")