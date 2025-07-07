from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_reply() -> ReplyKeyboardMarkup:
    """Главное меню в виде reply клавиатуры"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="💡 Получить идею"),
        KeyboardButton(text="💕 Предложить свидание")
    )
    builder.row(
        KeyboardButton(text="📋 Мои предложения"),
        KeyboardButton(text="📚 История свиданий")
    )
    builder.row(
        KeyboardButton(text="👫 Моя пара"),
        KeyboardButton(text="⚙️ Настройки")
    )
    
    return builder.as_markup(resize_keyboard=True)


def registration_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для регистрации"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(KeyboardButton(text="📝 Зарегистрироваться"))
    builder.row(KeyboardButton(text="ℹ️ Помощь"))
    
    return builder.as_markup(resize_keyboard=True)


def couple_setup_reply() -> ReplyKeyboardMarkup:
    """Клавиатура для настройки пары"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="➕ Создать пару"),
        KeyboardButton(text="🔗 Присоединиться")
    )
    builder.row(KeyboardButton(text="◀️ Назад"))
    
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура Да/Нет"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Да"),
        KeyboardButton(text="❌ Нет")
    )
    return builder.as_markup(resize_keyboard=True)


def skip_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой пропуска"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="⏭️ Пропустить"),
        KeyboardButton(text="❌ Отмена")
    )
    return builder.as_markup(resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardMarkup:
    """Удалить клавиатуру"""
    return ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        remove_keyboard=True
    )