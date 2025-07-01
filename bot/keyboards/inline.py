from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from bot.models.schemas import GenderEnum, IdeaResponse


def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="👫 Создать пару", callback_data="create_pair")],
        [InlineKeyboardButton(text="💡 Идеи для свиданий", callback_data="get_ideas")],
        [InlineKeyboardButton(text="💕 Предложить свидание", callback_data="propose_date")],
        [InlineKeyboardButton(text="📋 Мои свидания", callback_data="my_events")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_pair_invitation_keyboard(invitation_id: str) -> InlineKeyboardMarkup:
    """Invitation keyboard for pairing"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_pair_{invitation_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_pair_{invitation_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ideas_categories_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting ideas categories"""
    keyboard = [
        [InlineKeyboardButton(text="🎬 Развлечения", callback_data="ideas_entertainment")],
        [InlineKeyboardButton(text="🍽️ Еда", callback_data="ideas_food")],
        [InlineKeyboardButton(text="🏃 Активный отдых", callback_data="ideas_active")],
        [InlineKeyboardButton(text="🎨 Творчество", callback_data="ideas_creative")],
        [InlineKeyboardButton(text="🏠 Дома", callback_data="ideas_home")],
        [InlineKeyboardButton(text="🎲 Случайные", callback_data="ideas_random")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ideas_list_keyboard(ideas: List[IdeaResponse]) -> InlineKeyboardMarkup:
    """List of ideas keyboard"""
    keyboard = []
    for idea in ideas:
        keyboard.append([InlineKeyboardButton(
            text=f"💡 {idea.title}", 
            callback_data=f"idea_{idea.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_ideas")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_idea_action_keyboard(idea_id: int) -> InlineKeyboardMarkup:
    """Keyboard for actions with a specific idea"""
    keyboard = [
        [InlineKeyboardButton(text="💕 Предложить партнеру", callback_data=f"propose_idea_{idea_id}")],
        [InlineKeyboardButton(text="◀️ Назад к идеям", callback_data="back_to_ideas")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_event_response_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Keyboard for responding to an event"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Согласен!", callback_data=f"event_accept_{event_id}")],
        [InlineKeyboardButton(text="❌ Не могу", callback_data=f"event_decline_{event_id}")],
        [InlineKeyboardButton(text="💬 Обсудить", callback_data=f"event_discuss_{event_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Back keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)