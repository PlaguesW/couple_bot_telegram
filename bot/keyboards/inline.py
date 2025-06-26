from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Получить идею", callback_data="get_idea")],
        [InlineKeyboardButton(text="💌 Предложить свидание", callback_data="propose_date")],
        [InlineKeyboardButton(text="📋 Мои предложения", callback_data="my_proposals")],
        [InlineKeyboardButton(text="📚 История свиданий", callback_data="date_history")],
        [InlineKeyboardButton(text="👥 Настройки пары", callback_data="pair_settings")]
    ])
    return keyboard

def pair_setup_menu():
    """Меню настройки пары"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Создать пару", callback_data="create_pair")],
        [InlineKeyboardButton(text="🔗 Присоединиться к паре", callback_data="join_pair")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])
    return keyboard

def category_menu():
    """Меню выбора категории идей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Случайная идея", callback_data="random_idea")],
        [InlineKeyboardButton(text="🏠 Дома", callback_data="category_home")],
        [InlineKeyboardButton(text="🌳 На улице", callback_data="category_outdoor")],
        [InlineKeyboardButton(text="🎭 Развлечения", callback_data="category_entertainment")],
        [InlineKeyboardButton(text="🍽️ Еда", callback_data="category_food")],
        [InlineKeyboardButton(text="🎨 Творчество", callback_data="category_creative")],
        [InlineKeyboardButton(text="💪 Спорт", callback_data="category_sport")],
        [InlineKeyboardButton(text="🎓 Обучение", callback_data="category_learning")],
        [InlineKeyboardButton(text="🌙 Романтика", callback_data="category_romantic")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    return keyboard

def idea_action_keyboard(idea_id):
    """Клавиатура действий с идеей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💌 Предложить партнеру", callback_data=f"propose_idea_{idea_id}")],
        [InlineKeyboardButton(text="🎲 Другая идея", callback_data="random_idea")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])
    return keyboard

def proposal_response_keyboard(proposal_id):
    """Клавиатура ответа на предложение"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{proposal_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{proposal_id}")
        ],
        [InlineKeyboardButton(text="📋 Другие предложения", callback_data="my_proposals")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])
    return keyboard

def back_to_menu_button():
    """Простая кнопка возврата в меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])
    return keyboard

def pair_settings_menu():
    """Меню настроек пары"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Информация о паре", callback_data="pair_info")],
        [InlineKeyboardButton(text="💔 Покинуть пару", callback_data="leave_pair")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    return keyboard

def confirm_leave_pair_keyboard():
    """Подтверждение выхода из пары"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, покинуть", callback_data="confirm_leave_pair"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="pair_settings")
        ]
    ])
    return keyboard