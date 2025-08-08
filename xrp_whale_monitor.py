from aiogram import Router, F
from aiogram.types import Message

xrp_whale_router = Router()

@xrp_whale_router.message(F.text == "/xrpwhale")
async def xrp_whale_status(message: Message):
    await message.answer("✅ XRP whale tracking module is active and working.")