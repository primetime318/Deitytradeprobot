from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("✅ DeityTradePro Bot is running!")

@router.message(F.text == "/help")
async def help_handler(message: Message):
    await message.answer(
        "📌 Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/signal - Show a trade signal\n"
        "/broadcast - Admin broadcast"
    )