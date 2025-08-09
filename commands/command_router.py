from aiogram import Router, types
from aiogram.filters import Command
import json
import os

tier_router = Router()

# Path to tiers.json file
TIERS_FILE = os.path.join("data", "tiers.json")

# Load tiers from file
def load_tiers():
    if os.path.exists(TIERS_FILE):
        with open(TIERS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save tiers to file
def save_tiers(tiers):
    with open(TIERS_FILE, "w") as f:
        json.dump(tiers, f, indent=4)

# /tier - check your current tier
@tier_router.message(Command("tier"))
async def cmd_tier(message: types.Message):
    tiers = load_tiers()
    tier = tiers.get(str(message.from_user.id), "Free")
    await message.answer(f"📜 Your tier: {tier}")

# /settier <user_id> <tier_name> - admin only
@tier_router.message(Command("settier"))
async def cmd_settier(message: types.Message):
    admin_id = 6860530316  # Your Telegram user ID
    args = message.text.split()

    if message.from_user.id != admin_id:
        await message.answer("⛔ You are not authorized to use this command.")
        return

    if len(args) != 3:
        await message.answer("⚠️ Usage: /settier <user_id> <tier_name>")
        return

    target_id = args[1]
    new_tier = args[2]

    tiers = load_tiers()
    tiers[target_id] = new_tier
    save_tiers(tiers)

    await message.answer(f"✅ Tier for user `{target_id}` set to **{new_tier}**")
