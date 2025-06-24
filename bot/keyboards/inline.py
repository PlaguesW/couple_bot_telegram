from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💡 Идея дня", callback_data="daily_idea")],
        [InlineKeyboardButton(text="💕 Предложить свидание", callback_data="propose_date")],
        [InlineKeyboardButton(text="📝 Мои предложения", callback_data="my_proposals")],
        [InlineKeyboardButton(text="📚 История свиданий", callback_data="date_history")],
        [InlineKeyboardButton(text="👫 Моя пара", callback_data="pair_info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню для создания/присоединения к паре
def pair_setup_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔗 Создать пару", callback_data="create_pair")],
        [InlineKeyboardButton(text="💌 Присоединиться к паре", callback_data="join_pair")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню категорий идей
def categories_menu(categories: list) -> InlineKeyboardMarkup:
    keyboard = []
    for category in categories:
        emoji = get_category_emoji(category)
        keyboard.append([InlineKeyboardButton(
            text=f"{emoji} {category.title()}", 
            callback_data=f"category_{category}"
        )])
    keyboard.append([InlineKeyboardButton(text="🎲 Случайная идея", callback_data="random_idea")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки для предложения идеи
def propose_idea_buttons(idea_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text="💕 Предложить партнеру", 
            callback_data=f"propose_{idea_id}"
        )],
        [InlineKeyboardButton(text="🎲 Другая идея", callback_data="daily_idea")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки для ответа на предложение
def proposal_response_buttons(proposal_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{proposal_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{proposal_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки навигации
def back_to_menu_button() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_category_emoji(category: str) -> str:
    """Получение эмодзи для категории"""
    emojis = {
        'романтика': '💕',
        'дом': '🏠',
        'активность': '🏃',
        'культура': '🎭',
        'ресторан': '🍽️',
        'творчество': '🎨',
        'релакс': '🧘',
        'общее': '⭐'
    }
    return emojis.get(category, '⭐')