from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💡 Получить идею", callback_data="get_idea"),
        InlineKeyboardButton(text="💕 Предложить свидание", callback_data="propose_date")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои предложения", callback_data="my_proposals"),
        InlineKeyboardButton(text="📚 История свиданий", callback_data="date_history")
    )
    builder.row(
        InlineKeyboardButton(text="👫 Моя пара", callback_data="couple_info"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    
    return builder.as_markup()


def couple_setup_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для настройки пары"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Создать пару", callback_data="create_couple"),
        InlineKeyboardButton(text="🔗 Присоединиться", callback_data="join_couple")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def category_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории идей"""
    builder = InlineKeyboardBuilder()
    
    categories = [
        ("🌹 Романтические", "romantic"),
        ("🏠 Домашние", "home"),
        ("🎭 Культурные", "cultural"),
        ("🏃 Активные", "active"),
        ("💰 Бюджетные", "budget"),
        ("🎲 Случайная", "random")
    ]
    
    for text, callback_data in categories:
        builder.row(InlineKeyboardButton(text=text, callback_data=f"category_{callback_data}"))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    
    return builder.as_markup()


def idea_action_keyboard(idea_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с идеей"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💕 Предложить свидание", callback_data=f"propose_idea_{idea_id}"),
        InlineKeyboardButton(text="🔄 Другая идея", callback_data="get_another_idea")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_categories")
    )
    
    return builder.as_markup()


def proposal_response_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на предложение"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{event_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{event_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Подробнее", callback_data=f"details_{event_id}")
    )
    
    return builder.as_markup()


def proposals_list_keyboard(proposals: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура со списком предложений"""
    builder = InlineKeyboardBuilder()
    
    for proposal in proposals:
        event_id = proposal.get("id")
        idea_title = proposal.get("idea", {}).get("title", "Неизвестная идея")
        status = proposal.get("date_status", "pending")
        
        if status == "pending":
            emoji = "⏳"
        elif status == "accepted":
            emoji = "✅"
        else:
            emoji = "❌"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {idea_title}", 
                callback_data=f"view_proposal_{event_id}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    
    return builder.as_markup()


def date_history_keyboard(history: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура истории свиданий с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Показываем 5 записей на странице
    page_size = 5
    start_idx = page * page_size
    end_idx = start_idx + page_size
    
    page_history = history[start_idx:end_idx]
    
    for event in page_history:
        event_id = event.get("id")
        idea_title = event.get("idea", {}).get("title", "Неизвестная идея")
        status = event.get("date_status", "pending")
        
        if status == "completed":
            emoji = "✅"
        elif status == "accepted":
            emoji = "💕"
        elif status == "rejected":
            emoji = "❌"
        else:
            emoji = "⏳"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {idea_title}", 
                callback_data=f"view_event_{event_id}"
            )
        )
    
    # Навигация по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Пред", callback_data=f"history_page_{page-1}"))
    if end_idx < len(history):
        nav_buttons.append(InlineKeyboardButton(text="След ▶️", callback_data=f"history_page_{page+1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    
    return builder.as_markup()


def couple_info_keyboard(couple_id: int) -> InlineKeyboardMarkup:
    """Клавиатура информации о паре"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data=f"couple_stats_{couple_id}"),
        InlineKeyboardButton(text="🔗 Код приглашения", callback_data=f"invite_code_{couple_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def confirmation_keyboard(action: str, data: str = "") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{data}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}")
    )
    
    return builder.as_markup()


def back_keyboard(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """Простая клавиатура "Назад" """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data))
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications"),
        InlineKeyboardButton(text="🌍 Язык", callback_data="change_language")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Помощь", callback_data="help"),
        InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
    )
    
    return builder.as_markup()