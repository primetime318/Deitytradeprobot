from aiogram import Router, types
from aiogram.filters import Command
from utils.tier import get_tier, set_tier, list_tiers

tier_router = Router()

# Command: /mytier
@tier_router.message(Command("mytier"))
async def my_tier_handler(message: types.Message):
    tier = get_tier(message.from_user.id)
    await message.reply(f"💎 Your current tier: **{tier}**")

# Command: /settier (Admin only)
@tier_router.message(Command("settier"))
async def set_tier_handler(message: types.Message):
    if message.chat.type != "private":
        await message.reply("⚠ Please use this command in a private chat.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply("Usage: /settier <user_id> <tier>")
        return

    try:
        target_id = int(args[1])
    except ValueError:
        await message.reply("⚠ Invalid user ID.")
        return

    new_tier = args[2]
    set_tier(target_id, new_tier)
    await message.reply(f"✅ Tier for user {target_id} set to **{new_tier}**.")

# Command: /tiers (List all users & tiers) - Admin only
@tier_router.message(Command("tiers"))
async def list_tiers_handler(message: types.Message):
    tiers = list_tiers()
    if not tiers:
        await message.reply("No users have tiers assigned yet.")
        return

    reply_text = "📋 **Current Tiers:**\n"
    for user_id, tier in tiers.items():
        reply_text += f"- {user_id}: {tier}\n"

    await message.reply(reply_text)
