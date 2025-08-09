import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from commands.command_router import router as command_router
from commands.alert_router import alert_router
from eth_whale_monitor import eth_whale_router
from btc_whale_monitor import btc_whale_router
from xrp_whale_monitor import xrp_whale_router
from commands.hedge_router import hedge_router
from commands.util_router import util_router
from commands.signal_router import signal_router
from commands.catchall_router import catchall_router
from router.system_router import system_router
from commands.alert_router import alert_router
from router.tier_router import tier_router
from commands.debug_admin import debug_router
from utils.tier import get_tier, Tier, is_admin, set_tier, list_tiers

# Logging
logging.basicConfig(level=logging.INFO)

# Bot + Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Include routers
dp.include_router(command_router)
dp.include_router(alert_router)
dp.include_router(eth_whale_router)
dp.include_router(btc_whale_router)
dp.include_router(xrp_whale_router)
dp.include_router(hedge_router)
dp.include_router(system_router)
dp.include_router(signal_router)
dp.include_router(tier_router)
dp.include_router(debug_router)
# --- NEW ROUTERS ---
from commands.util_router import util_router
from commands.signal_router import signal_router
from commands.catchall_router import catchall_router

# --- INCLUDE NEW ROUTERS ---
dp.include_router(util_router)       # /id, /ping
dp.include_router(catchall_router)# Catch-all for unknown commands (must be last)
dp.include_router(debug_router)
# Background whale monitors
async def eth_whale_router_polling():
    from eth_whale_monitor import monitor_eth_whales
    await monitor_eth_whales(bot)

async def btc_whale_router_polling():
    from btc_whale_monitor import monitor_btc_whales
    await monitor_btc_whales(bot)

async def xrp_whale_router_polling():
    from xrp_whale_monitor import monitor_xrp_whales
    await monitor_xrp_whales(bot)

async def on_startup():
    print("Bot started. Listening for updates...")
    asyncio.create_task(alert_scheduler.scheduled_alerts(bot))
    asyncio.create_task(eth_whale_router_polling())
    asyncio.create_task(btc_whale_router_polling())
    asyncio.create_task(xrp_whale_router_polling())

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot, on_startup=on_startup))
