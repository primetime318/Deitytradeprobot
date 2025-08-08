from aiogram import Router, F
from aiogram.types import Message

eth_whale_router = Router()

@eth_whale_router.message(F.text == "/ethwhale")
async def eth_whale_status(message: Message):
    await message.answer("✅ ETH whale tracking module is active and working.")