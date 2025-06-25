from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline import main_menu, category_menu, idea_action_keyboard, back_to_menu_button

router = Router()

@router.callback_query(F.data == "get_idea")
async def get_idea_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик получения идеи для свидания"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем наличие пары
    pair = await db.get_user_pair(user['id'])
    if not pair or not pair['user2_id']:
        await callback.answer("Для получения идей нужно создать пару!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💡 Выберите категорию идей для свидания:\n\n"
        "Или получите случайную идею из всех категорий!",
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
            await callback.answer("Идеи не найдены", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"💡 **{idea['title']}**\n\n"
            f"📝 {idea['description']}\n\n"
            f"🏷️ Категория: {idea['category'].title()}",
            parse_mode="Markdown",
            reply_markup=idea_action_keyboard(idea['id'])
        )
        
        await callback.answer("Вот идея для вас! 💡")
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении идеи: {e}", show_alert=True)

@router.callback_query(F.data.startswith("category_"))
async def category_idea_handler(callback: CallbackQuery):
    """Обработчик идей по категориям"""
    category = callback.data.replace("category_", "")
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    try:
        ideas = await db.get_ideas_by_category(category)
        if not ideas:
            await callback.answer(f"Идеи в категории '{category}' не найдены", show_alert=True)
            return
        
        # Берем первую идею из списка (они уже перемешаны в запросе)
        idea = ideas[0]
        
        await callback.message.edit_text(
            f"💡 **{idea['title']}**\n\n"
            f"📝 {idea['description']}\n\n"
            f"🏷️ Категория: {idea['category'].title()}",
            parse_mode="Markdown",
            reply_markup=idea_action_keyboard(idea['id'])
        )
        
        await callback.answer(f"Идея из категории '{category.title()}'! 💡")
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении идеи: {e}", show_alert=True)

@router.callback_query(F.data.startswith("propose_idea_"))
async def propose_idea_handler(callback: CallbackQuery):
    """Обработчик предложения идеи партнеру"""
    idea_id = int(callback.data.replace("propose_idea_", ""))
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Получаем пару пользователя
    pair = await db.get_user_pair(user['id'])
    if not pair or not pair['user2_id']:
        await callback.answer("У вас нет пары для предложения!", show_alert=True)
        return
    
    try:
        # Создаем предложение свидания
        proposal_id = await db.create_date_proposal(pair['id'], idea_id, user['id'])
        
        # Получаем информацию об идее
        idea = await db.get_idea_by_id(idea_id)
        
        # Получаем информацию о партнере
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await callback.message.edit_text(
            f"✅ Предложение отправлено!\n\n"
            f"💡 **{idea['title']}**\n"
            f"📝 {idea['description']}\n\n"
            f"Ваш партнер {partner['name']} получит уведомление о предложении.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_button()
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
                f"💡 **{idea['title']}**\n"
                f"📝 {idea['description']}\n\n"
                f"🏷️ Категория: {idea['category'].title()}",
                parse_mode="Markdown",
                reply_markup=proposal_response_keyboard(proposal_id)
            )
            await bot.session.close()
        except Exception:
            pass  # Не критичная ошибка
        
        await callback.answer("Предложение отправлено партнеру! 💌")
        
    except Exception as e:
        await callback.answer(f"Ошибка при отправке предложения: {e}", show_alert=True)