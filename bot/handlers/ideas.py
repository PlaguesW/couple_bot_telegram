from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import db
from keyboards.inline import (
    category_menu, 
    idea_action_keyboard, 
    back_to_menu_button,
    main_menu
)

router = Router()

CATEGORY_MAPPING = {
    'home': 'дом',
    'outdoor': 'активность', 
    'entertainment': 'культура',
    'food': 'ресторан',
    'creative': 'творчество',
    'sport': 'активность',
    'learning': 'культура',
    'romantic': 'романтика'
}

@router.callback_query(F.data == "get_idea")
async def get_idea_handler(callback: CallbackQuery):
    """Обработчик получения идеи - показать меню категорий"""
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем наличие пары
    pair = await db.get_user_pair(user['id'])
    if not pair:
        await callback.message.edit_text(
            "❌ Для получения идей нужно создать пару или присоединиться к существующей!\n\n"
            "Используйте кнопку '👥 Настройки пары' для создания или присоединения к паре.",
            reply_markup=back_to_menu_button()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "💡 Выберите категорию идеи или получите случайную:",
        reply_markup=category_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "random_idea")
async def random_idea_handler(callback: CallbackQuery):
    """Обработчик случайной идеи"""
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    try:
        idea = await db.get_random_idea()
        if not idea:
            await callback.message.edit_text(
                "😔 К сожалению, идеи не найдены.\n"
                "Попробуйте позже или обратитесь к администратору.",
                reply_markup=back_to_menu_button()
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            f"💡 <b>{idea['title']}</b>\n\n"
            f"📝 {idea['description']}\n\n"
            f"🏷️ Категория: {idea['category']}",
            reply_markup=idea_action_keyboard(idea['id']),
            parse_mode='HTML'
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении идеи: {e}", show_alert=True)

@router.callback_query(F.data.startswith("category_"))
async def category_idea_handler(callback: CallbackQuery):
    """Обработчик идеи по категории"""
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    category_key = callback.data.replace("category_", "")
    category = CATEGORY_MAPPING.get(category_key)
    
    if not category:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    
    try:
        idea = await db.get_random_idea_by_category(category)
        if not idea:
            await callback.message.edit_text(
                f"😔 К сожалению, в категории '{category}' идеи не найдены.\n"
                "Попробуйте другую категорию или случайную идею.",
                reply_markup=category_menu()
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            f"💡 <b>{idea['title']}</b>\n\n"
            f"📝 {idea['description']}\n\n"
            f"🏷️ Категория: {idea['category']}",
            reply_markup=idea_action_keyboard(idea['id']),
            parse_mode='HTML'
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении идеи: {e}", show_alert=True)

@router.callback_query(F.data.startswith("propose_idea_"))
async def propose_idea_handler(callback: CallbackQuery):
    """Обработчик предложения идеи партнеру"""
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    idea_id = int(callback.data.replace("propose_idea_", ""))
    
    try:
        # Получаем пару пользователя
        pair = await db.get_user_pair(user['id'])
        if not pair:
            await callback.answer("У вас нет пары для предложения идеи", show_alert=True)
            return
        
        # Получаем информацию об идее
        idea = await db.get_idea_by_id(idea_id)
        if not idea:
            await callback.answer("Идея не найдена", show_alert=True)
            return
        
        # Создаем предложение
        proposal_id = await db.create_date_proposal(pair['id'], idea_id, user['id'])
        
        # Получаем информацию о партнере
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await callback.message.edit_text(
            f"✅ Предложение отправлено!\n\n"
            f"💡 <b>{idea['title']}</b>\n"
            f"📝 {idea['description']}\n\n"
            f"Ваш партнер {partner['name']} получит уведомление о предложении.",
            reply_markup=main_menu(),
            parse_mode='HTML'
        )
        
        # Отправляем уведомление партнеру
        try:
            from aiogram import Bot
            from config import BOT_TOKEN
            from keyboards.inline import proposal_response_keyboard
            
            bot = Bot(token=BOT_TOKEN)
            
            await bot.send_message(
                partner['telegram_id'],
                f"💌 У вас новое предложение свидания от {user['name']}!\n\n"
                f"💡 <b>{idea['title']}</b>\n"
                f"📝 {idea['description']}\n\n"
                f"🏷️ Категория: {idea['category']}",
                reply_markup=proposal_response_keyboard(proposal_id),
                parse_mode='HTML'
            )
            await bot.session.close()
        except Exception:
            pass  # Не критичная ошибка
        
        await callback.answer("Предложение отправлено! 💕")
        
    except Exception as e:
        await callback.answer(f"Ошибка при отправке предложения: {e}", show_alert=True)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🏠 Главное меню\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )
    await callback.answer()