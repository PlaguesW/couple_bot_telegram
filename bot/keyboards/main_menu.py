from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💡 Получить идею"),
                KeyboardButton(text="📂 Идеи по категориям")
            ],
            [
                KeyboardButton(text="📋 Мои предложения"),
                KeyboardButton(text="📚 История")
            ],
            [
                KeyboardButton(text="👤 Профиль")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard