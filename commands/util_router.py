from aiogram import Router, types
from aiogram.filters import Command

util_router = Router()

@util_router.message(Command("id"))
async def show_ids(msg: types.Message):
    await msg.answer(
        f"🆔 user_id: <code>{msg.from_user.id}</code>\n"
        f"👥 chat_id: <code>{msg.chat.id}</code>",
        parse_mode="HTML"
    )

@util_router.message(Command("ping"))
async def ping(msg: types.Message):
    await msg.answer("✅ pong")