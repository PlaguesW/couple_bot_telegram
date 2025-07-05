from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора категорий идей"""
    builder = InlineKeyboardBuilder()
    
    categories = [
        ("💕 Романтические", "category_romantic"),
        ("🏃 Активные", "category_active"),
        ("🏠 Домашние", "category_home"),
        ("🎨 Творческие", "category_creative"),
        ("🌟 Приключения", "category_adventure")
    ]
    
    for text, callback_data in categories:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    builder.adjust(2)  # По 2 кнопки в ряд
    return builder.as_markup()

def get_ideas_keyboard(category: str) -> InlineKeyboardMarkup:
    """Клавиатура для действий с идеями"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="💌 Предложить свидание",
            callback_data=f"propose_{category}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔄 Другие идеи",
            callback_data=f"category_{category}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_categories"
        )
    )
    
    builder.adjust(1)  # По 1 кнопке в ряд
    return builder.as_markup()

def get_date_proposal_keyboard(proposal_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на предложение свидания"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="✅ Принять",
            callback_data=f"proposal_accept_{proposal_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"proposal_decline_{proposal_id}"
        )
    )
    
    builder.adjust(2)  # По 2 кнопки в ряд
    return builder.as_markup()

def get_pair_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления парами"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="👥 Создать пару",
            callback_data="create_pair"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔗 Присоединиться к паре",
            callback_data="join_pair"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="📊 Моя пара",
            callback_data="my_pair"
        )
    )
    
    builder.adjust(1)  # По 1 кнопке в ряд
    return builder.as_markup()

def get_registration_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для регистрации"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="📝 Зарегистрироваться",
            callback_data="register"
        )
    )
    
    return builder.as_markup()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="💡 Идеи для свиданий",
            callback_data="get_ideas"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="👥 Управление парой",
            callback_data="manage_pair"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="📅 Мои события",
            callback_data="my_events"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="⚙️ Настройки",
            callback_data="settings"
        )
    )
    
    builder.adjust(2)  # По 2 кнопки в ряд
    return builder.as_markup()