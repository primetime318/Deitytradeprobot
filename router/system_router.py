from aiogram import Router

# Import each router ONCE and only assemble them here
from commands.command_router import router as command_router
from commands.alert_router import alert_router
from commands.signal_router import signal_router
from commands.hedge_router import hedge_router
from commands.util_router import util_router
from router.tier_router import tier_router
from commands.debug_admin import debug_router
from commands.catchall_router import catchall_router  # keep last

# If your whale monitors are Routers (not background tasks), import them here:
# from eth_whale_monitor import eth_whale_router
# from btc_whale_monitor import btc_whale_router
# from xrp_whale_monitor import xrp_whale_router

system_router = Router(name="system")

# Order matters. General → specific. Catch-all must be last.
system_router.include_router(command_router)
system_router.include_router(alert_router)
system_router.include_router(signal_router)
system_router.include_router(hedge_router)
system_router.include_router(util_router)
system_router.include_router(tier_router)
system_router.include_router(debug_router)

# Optional whale routers (ONLY if they are Router() objects)
# system_router.include_router(eth_whale_router)
# system_router.include_router(btc_whale_router)
# system_router.include_router(xrp_whale_router)

system_router.include_router(catchall_router)  # ← last
