# commands/hedge_router.py

from aiogram import Router, F
from aiogram.types import Message

hedge_router = Router()

@hedge_router.message(F.text.startswith("/hedgeplan"))
async def hedge_plan_handler(message: Message):
    await message.answer("🛡️ Hedge Plan activated. Analyzing best hedge entries...")

@hedge_router.message(F.text.startswith("/hedgescan"))
async def hedge_scan_handler(message: Message):
    await message.answer("🔍 Hedge Scan running... Scanning for smart hedge opportunities.")

@hedge_router.message(F.text.startswith("/riskdrop"))
async def risk_drop_handler(message: Message):
    await message.answer("⚠️ Risk Drop Alert: Monitoring high-volatility assets.")

@hedge_router.message(F.text.startswith("/hedgehelp"))
async def hedge_help_handler(message: Message):
    await message.answer(
        "📘 Hedge Commands:\n"
        "/hedgeplan [ASSET] - Generate hedge strategy\n"
        "/hedgescan - Scan for potential hedge setups\n"
        "/riskdrop - Show risk-based entry zones\n"
        "/hedgehelp - Show this help menu"
    )