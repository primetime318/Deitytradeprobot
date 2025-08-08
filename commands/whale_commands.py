from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_ID
import json

whale_router = Router()

@whale_router.message(Command("addwhale"))
async def add_whale(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ You are not authorized to add whales.")
        return

    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("⚠️ Usage: /addwhale [label] [wallet_address]")
            return

        label, wallet = parts[1], parts[2]
        with open("tracked_wallets.json", "r") as f:
            wallets = json.load(f)

        wallets.append({"label": label, "address": wallet})

        with open("tracked_wallets.json", "w") as f:
            json.dump(wallets, f, indent=2)

        await message.answer(f"✅ Whale added:\nLabel: {label}\nAddress: {wallet}")
    except Exception as e:
        await message.answer(f"⚠️ Error: {e}")

@whale_router.message(Command("whalelist"))
async def list_whales(message: types.Message):
    try:
        with open("tracked_wallets.json", "r") as f:
            wallets = json.load(f)

        if not wallets:
            await message.answer("🐋 No whales tracked yet.")
            return

        response = "📄 Tracked Whales:\n\n"
        for i, w in enumerate(wallets, 1):
            response += f"{i}. {w['label']} - `{w['address']}`\n"

        await message.answer(response, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠️ Error: {e}")
whale_router = Router()

# File path for storing tracked wallets
TRACKED_WALLETS_FILE = "tracked_wallets.json"

# Load wallet data
def load_tracked_wallets():
    if os.path.exists(TRACKED_WALLETS_FILE):
        with open(TRACKED_WALLETS_FILE, "r") as f:
            return json.load(f)
    return []

# Save wallet data
def save_tracked_wallets(wallets):
    with open(TRACKED_WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

# /whalelist command
@whale_router.message(Command("whalelist"))
async def whalelist_cmd(message: Message):
    wallets = load_tracked_wallets()
    if not wallets:
        await message.answer("No wallets are currently being tracked.")
        return

    response = "<b>🐋 Tracked Whale Wallets:</b>\n"
    for w in wallets:
        response += f"• {w['label']}: <code>{w['wallet']}</code>\n"
    await message.answer(response, parse_mode="HTML")

# /addwhale <label> <wallet>
@whale_router.message(Command("addwhale"))
async def addwhale_cmd(message: Message):
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❗ Usage: <code>/addwhale LABEL WALLET_ADDRESS</code>", parse_mode="HTML")
        return

    label = parts[1].strip()
    wallet = parts[2].strip()

    wallets = load_tracked_wallets()
    wallets.append({"label": label, "wallet": wallet})
    save_tracked_wallets(wallets)

    await message.answer(f"✅ Whale wallet added:\n<b>{label}</b>: <code>{wallet}</code>", parse_mode="HTML")
@whale_router.message(Command("addwhale"))
async def addwhale_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 You are not authorized to use this command.")
        return

    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        await message.answer("⚠️ Usage: /addwhale Label Address")
        return

    label, address = parts[1], parts[2]

    wallets = load_tracked_wallets()
    wallets.append({"label": label, "address": address})
    save_tracked_wallets(wallets)

    await message.answer(f"✅ Added whale wallet:\n<b>{label}</b>: <code>{address}</code>", parse_mode="HTML")