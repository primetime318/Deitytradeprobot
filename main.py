import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from router.system_router import system_router  # ← single aggregator

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Include exactly ONE router (the aggregator)
dp.include_router(system_router)

# Optional background tasks. Uncomment only if these functions exist.
async def on_startup():
    print("Bot started. Listening for updates...")
    # from scheduler import alert_scheduler
    # asyncio.create_task(alert_scheduler.scheduled_alerts(bot))

    # If whale monitors run as background tasks (not routers), uncomment:
    # from eth_whale_monitor import monitor_eth_whales
    # from btc_whale_monitor import monitor_btc_whales
    # from xrp_whale_monitor import monitor_xrp_whales
    # asyncio.create_task(monitor_eth_whales(bot))
    # asyncio.create_task(monitor_btc_whales(bot))
    # asyncio.create_task(monitor_xrp_whales(bot))

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot, on_startup=on_startup))
