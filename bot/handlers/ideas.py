from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.services.api_client import api_client
from bot.keyboards.inline import (
    get_ideas_categories_keyboard, 
    get_ideas_list_keyboard, 
    get_idea_action_keyboard,
    get_main_menu
)
from bot.utils.decorators import require_registration

router = Router()


@router.callback_query(F.data == "get_ideas")
@require_registration
async def show_ideas_categories(callback: types.CallbackQuery, state: FSMContext, user):
    """Show ideas categories"""
    await state.clear()
    
    await callback.message.edit_text(
        "💡 <b>Идеи для свиданий</b>\n\n"
        "Выбери категорию, которая тебя интересует:",
        parse_mode="HTML",
        reply_markup=get_ideas_categories_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ideas_"))
@require_registration
async def show_ideas_by_category(callback: types.CallbackQuery, state: FSMContext, user):
    """show ideas by selected category"""
    category = callback.data.replace("ideas_", "")
    
    # Save current category in state
    await state.update_data(current_category=category)
    
    if category == "random":
        ideas = await api_client.get_random_ideas(count=5)
        category_name = "Случайные идеи"
    else:
        category_map = {
            "entertainment": "развлечения",
            "food": "еда", 
            "active": "активный отдых",
            "creative": "творчество",
            "home": "дома"
        }
        category_name = category_map.get(category, category)
        ideas = await api_client.get_ideas(category=category, limit=10)
    
    if not ideas:
        await callback.message.edit_text(
            f"😔 <b>Идеи не найдены</b>\n\n"
            f"К сожалению, в категории '{category_name}' пока нет идей.\n"
            f"Попробуй другую категорию!",
            parse_mode="HTML",
            reply_markup=get_ideas_categories_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"💡 <b>Идеи: {category_name.title()}</b>\n\n"
        f"Найдено идей: {len(ideas)}\n"
        f"Выбери интересную идею:",
        parse_mode="HTML",
        reply_markup=get_ideas_list_keyboard(ideas)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("idea_"))
@require_registration  
async def show_idea_details(callback: types.CallbackQuery, state: FSMContext, user):
    """Показать детали идеи"""
    idea_id = int(callback.data.replace("idea_", ""))
    
    # GetIdeaResponse while use idea list from state or make a new request
    data = await state.get_data()
    category = data.get("current_category")
    
    if category == "random":
        ideas = await api_client.get_random_ideas(count=10)
    else:
        ideas = await api_client.get_ideas(category=category, limit=20)
    
    idea = next((i for i in ideas if i.id == idea_id), None)
    
    if not idea:
        await callback.answer("❌ Идея не найдена")
        return
    
    # Check if user has a pair
    user_pair = await api_client.get_user_pair(user.id)
    
    description = idea.description if idea.description else "Описание не указано"
    category_text = f"📂 <b>Категория:</b> {idea.category}\n" if idea.category else ""
    
    message_text = (
        f"💡 <b>{idea.title}</b>\n\n"
        f"{category_text}"
        f"📝 <b>Описание:</b>\n{description}\n\n"
    )
    
    if user_pair:
        partner = user_pair.user2 if user_pair.user1.id == user.id else user_pair.user1
        message_text += f"💕 Можешь предложить эту идею партнеру ({partner.name})!"
    else:
        message_text += "ℹ️ Создай пару, чтобы предлагать идеи партнеру!"
    
    keyboard = get_idea_action_keyboard(idea_id) if user_pair else get_ideas_categories_keyboard()
    
    await callback.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "refresh_ideas")
@require_registration
async def refresh_ideas(callback: types.CallbackQuery, state: FSMContext, user):
    """Update ideas list"""
    data = await state.get_data()
    category = data.get("current_category", "random")
    
    # Imitate the idea refresh by re-fetching ideas
    callback.data = f"ideas_{category}"
    await show_ideas_by_category(callback, state, user)


@router.callback_query(F.data == "back_to_ideas")
@require_registration
async def back_to_ideas(callback: types.CallbackQuery, state: FSMContext, user):
    """Return to ideas categories"""
    data = await state.get_data()
    category = data.get("current_category")
    
    if category:
        callback.data = f"ideas_{category}"
        await show_ideas_by_category(callback, state, user)
    else:
        await show_ideas_categories(callback, state, user)


@router.callback_query(F.data.startswith("propose_idea_"))
@require_registration
async def propose_idea_to_partner(callback: types.CallbackQuery, state: FSMContext, user):
    """Send idea proposal to partner"""
    idea_id = int(callback.data.replace("propose_idea_", ""))
    
    # Get user pair
    user_pair = await api_client.get_user_pair(user.id)
    if not user_pair:
        await callback.answer("❌ У тебя нет пары!")
        return
    
    # Get idea details
    data = await state.get_data()
    category = data.get("current_category")
    
    if category == "random":
        ideas = await api_client.get_random_ideas(count=10)
    else:
        ideas = await api_client.get_ideas(category=category, limit=20)
    
    idea = next((i for i in ideas if i.id == idea_id), None)
    if not idea:
        await callback.answer("❌ Идея не найдена")
        return
    
    partner = user_pair.user2 if user_pair.user1.id == user.id else user_pair.user1
    
    try:
        from bot.main import bot
        
        # Send proposal message to partner
        await bot.send_message(
            partner.telegram_id,
            f"💕 <b>Предложение от {user.name}!</b>\n\n"
            f"💡 <b>Идея:</b> {idea.title}\n"
            f"📝 <b>Описание:</b> {idea.description or 'Не указано'}\n\n"
            f"Что скажешь? 😊",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="😍 Супер идея!", callback_data=f"like_idea_{idea_id}"),
                    types.InlineKeyboardButton(text="🤔 Подумаю", callback_data=f"maybe_idea_{idea_id}")
                ],
                [types.InlineKeyboardButton(text="💬 Обсудим", callback_data=f"discuss_idea_{idea_id}")]
            ])
        )
        
        await callback.message.edit_text(
            f"✅ <b>Идея отправлена!</b>\n\n"
            f"💡 <b>Идея:</b> {idea.title}\n"
            f"👤 <b>Партнер:</b> {partner.name}\n\n"
            f"Партнер получил твое предложение! 📨",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
        logger.info(f"Idea {idea_id} proposed by {user.name} to {partner.name}")
        
    except Exception as e:
        logger.error(f"Failed to send idea proposal: {e}")
        await callback.answer("❌ Не удалось отправить предложение")
    
    await callback.answer("Предложение отправлено! 💕")


# Response handlers for idea actions
@router.callback_query(F.data.startswith(("like_idea_", "maybe_idea_", "discuss_idea_")))
async def handle_idea_response(callback: types.CallbackQuery):
    """Обработка ответа на предложение идеи"""
    action = callback.data.split("_")[0]
    idea_id = callback.data.split("_")[-1]
    
    responses = {
        "like": "😍 Супер идея!",
        "maybe": "🤔 Подумаю над этим",
        "discuss": "💬 Давай обсудим детали"
    }
    
    response_text = responses.get(action, "Получен ответ")
    
    #* Here we could log the response or take further actions
    
    await callback.message.edit_text(
        f"{callback.message.text}\n\n"
        f"<b>💭 Твой ответ:</b> {response_text}",
        parse_mode="HTML"
    )
    
    await callback.answer(f"Ответ отправлен: {response_text}")