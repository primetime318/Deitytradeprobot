from aiogram import Router, F
from aiogram.types import Message

btc_whale_router = Router()

@btc_whale_router.message(F.text == "/btcwhale")
async def btc_whale_status(message: Message):
    await message.answer("✅ BTC whale tracking module is active and working.")