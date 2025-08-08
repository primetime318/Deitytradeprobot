from aiogram import Router, types

catchall_router = Router()

@catchall_router.message()
async def catch_all(msg: types.Message):
    if msg.text and msg.text.startswith("/"):
        await msg.answer(
            f"🤔 Unknown or disabled command: <code>{msg.text}</code>",
            parse_mode="HTML"
        )