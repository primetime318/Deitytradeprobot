# routers/system_router.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

system_router = Router(name="system")

@system_router.message(Command("ping"))
async def cmd_ping(message: Message):
    await message.answer("✅ pong")

@system_router.message(Command("id"))
async def cmd_id(message: Message):
    user_id = message.from_user.id if message.from_user else "unknown"
    chat_id = message.chat.id
    await message.answer(f"🆔 user_id: {user_id}\n👥 chat_id: {chat_id}")