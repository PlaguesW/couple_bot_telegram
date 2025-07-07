from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — начать\n"
        "/help — помощь\n"
        "/ideas — идеи для свиданий\n"
        "/dates — запланированные свидания\n"
        "/couple — информация о паре"
    )