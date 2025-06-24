from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from keyboards.inline import categories_menu, propose_idea_buttons, back_to_menu_button

router = Router()

@router.callback_query(F.data == "daily_idea")
async def daily_idea_handler(callback: CallbackQuery):
    """Получение идеи дня"""
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("Сначала нужно создать пару!", show_alert=True)
        return
    
    idea = await db.get_random_idea()
    
    if not idea:
        await callback.message.edit_text(
            "😔 К сожалению, идеи закончились!\n\n"
            "Попробуйте позже или предложите свою идею администратору.",
            reply_markup=back_to_menu_button()
        )
        return
    
    await callback.message.edit_text(
        f"💡 Идея дня:\n\n"
        f"**{idea['title']}**\n\n"
        f"{idea['description']}\n\n"
        f"Категория: {idea['category']} 🏷️",
        parse_mode="Markdown",
        reply_markup=propose_idea_buttons(idea['id'])
    )
    
    await callback.answer()

@router.callback_query(F.data == "propose_date")
async def propose_date_menu(callback: CallbackQuery):
    """Меню для предложения свидания"""
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("Сначала нужно создать пару!", show_alert=True)
        return
    
    categories = await db.get_all_categories()
    
    await callback.message.edit_text(
        "💕 Предложить свидание\n\n"
        "Выберите категорию идей:",
        reply_markup=categories_menu(categories)
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def category_ideas_handler(callback: CallbackQuery):
    """Получение идей по категории"""
    category = callback.data.split("_", 1)[1]
    
    ideas = await db.get_ideas_by_category(category)
    
    if not ideas:
        await callback.answer("В этой категории пока нет идей!", show_alert=True)
        return
    
    # Берем случайную идею из категории
    import random
    idea = random.choice(ideas)
    
    await callback.message.edit_text(
        f"💡 Идея из категории '{category}':\n\n"
        f"**{idea['title']}**\n\n"
        f"{idea['description']}\n\n"
        f"Категория: {idea['category']} 🏷️",
        parse_mode="Markdown",
        reply_markup=propose_idea_buttons(idea['id'])
    )
    
    await callback.answer()

@router.callback_query(F.data == "random_idea")
async def random_idea_handler(callback: CallbackQuery):
    """Случайная идея"""
    idea = await db.get_random_idea()
    
    if not idea:
        await callback.answer("Идеи закончились!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🎲 Случайная идея:\n\n"
        f"**{idea['title']}**\n\n"
        f"{idea['description']}\n\n"
        f"Категория: {idea['category']} 🏷️",
        parse_mode="Markdown",
        reply_markup=propose_idea_buttons(idea['id'])
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("propose_"))
async def propose_idea_handler(callback: CallbackQuery):
    """Предложение идеи партнеру"""
    idea_id = int(callback.data.split("_")[1])
    
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("У вас нет активной пары!", show_alert=True)
        return
    
    # Создаем предложение
    proposal_id = await db.create_date_proposal(pair['id'], idea_id, user['id'])
    
    # Получаем информацию об идее
    idea = await db.get_random_idea()  # Временно, нужно добавить get_idea_by_id
    
    # Уведомляем создателя предложения
    await callback.message.edit_text(
        f"✅ Предложение отправлено!\n\n"
        f"Ваш партнер получил уведомление о предложении свидания.\n"
        f"Ожидайте ответа! 💕",
        reply_markup=back_to_menu_button()
    )
    
    # Отправляем уведомление партнеру
    partner_id = await db.get_partner_id(user['id'])
    partner = await db.get_user_by_id(partner_id)
    
    try:
        from main import bot
        from keyboards.inline import proposal_response_buttons
        
        await bot.send_message(
            partner['telegram_id'],
            f"💕 Новое предложение свидания!\n\n"
            f"От: {user['name']}\n\n"
            f"**{idea['title']}**\n\n"
            f"{idea['description']}\n\n"
            f"Что скажете?",
            parse_mode="Markdown",
            reply_markup=proposal_response_buttons(proposal_id)
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
    
    await callback.answer("Предложение отправлено! ✅")