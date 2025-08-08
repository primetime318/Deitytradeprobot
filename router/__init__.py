from aiogram import Router
from commands.whale_commands import whale_router

command_router = Router()
command_router.include_router(whale_router)
from .tier_router import tier_router as TierRouter