from aiogram import Router
from aiogram.types import Message
from utils.tier import is_admin
from config import ADMIN_IDS  # keep both imports to see what prod loads

debug_router = Router()

@debug_router.message()
async def _debug_admin(m: Message):
    if m.text != "/whoami":  # keep it cheap
        return
    await m.answer(
        f"uid={m.from_user.id}\n"
        f"is_admin={is_admin(m.from_user.id)}\n"
        f"ADMIN_IDS={ADMIN_IDS}"
    )
