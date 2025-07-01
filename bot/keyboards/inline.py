from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_join_pair_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для создания/присоединения к паре"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👫 Создать пару",
                    callback_data="create_pair"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Присоединиться к паре",
                    callback_data="join_pair"
                )
            ]
        ]
    )
    return keyboard

def get_date_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с категориями свиданий"""
    categories = [
        ("❤️ Романтические", "romantic"),
        ("🏠 Домашние", "home"),
        ("🎨 Культурные", "cultural"),
        ("🏃 Активные", "active"),
        ("💰 Бюджетные", "budget")
    ]
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"category_{code}")]
            for name, code in categories
        ]
    )
    return keyboard

def get_date_actions_keyboard(idea_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с идеей свидания"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💕 Предложить партнеру",
                    callback_data=f"propose_{idea_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Другая идея",
                    callback_data="get_random_idea"
                )
            ]
        ]
    )
    return keyboard

def get_proposal_response_keyboard(proposal_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на предложение"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"accept_{proposal_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"decline_{proposal_id}"
                )
            ]
        ]
    )
    return keyboard

def create_pair_keyboard(pair_code: str) -> InlineKeyboardMarkup:
    """Клавиатура для управления парой"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Мои предложения",
                    callback_data="my_proposals"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Поделиться кодом пары",
                    callback_data=f"share_code_{pair_code}"
                )
            ]
        ]
    )
    return keyboard