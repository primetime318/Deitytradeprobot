from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

# Replace with your actual Telegram Bot token
BOT_TOKEN="7289921090:AAG8udGqbHhyV95_O5aXPeTnwrw9HjjZfw0"

# Replace with your actual Telegram group ID
GROUP_ID = -1002715449952

# ✅ Set parse_mode using DefaultBotProperties
BOT = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
# config.py
ADMIN_IDS = [6860530316]  # List so you can add more later if needed
