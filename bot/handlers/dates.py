from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from api_client import api_client
from keyboards.inline import (
    get_date_categories_keyboard, 
    get_proposal_response_keyboard,
    get_date_actions_keyboard
)

router = Router()

class DateProposal(StatesGroup):
    writing_custom_description = State()

@router.message(F.text == "💡 Получить идею")
async def get_random_idea(message: Message):
    """Получение случайной идеи для свидания"""
    response = await api_client.get_random_idea()
    
    if "error" in response:
        await message.answer(f"❌ {response['error']}")
        return
    
    idea = response
    await message.answer(
        f"💡 <b>{idea['title']}</b>\n\n"
        f"📝 {idea['description']}\n\n"
        f"🏷 Категория: {idea['category']}\n"
        f"💰 Бюджет: {idea['budget_level']}",
        reply_markup=get_date_actions_keyboard(idea['id'])
    )

@router.message(F.text == "📂 Идеи по категориям")
async def show_categories(message: Message):
    """Показ категорий идей"""
    await message.answer(
        "🗂 Выберите категорию:",
        reply_markup=get_date_categories_keyboard()
    )

@router.callback_query(F.data.startswith("category_"))
async def show_category_ideas(callback: CallbackQuery):
    """Показ идей по выбранной категории"""
    category = callback.data.split("category_")[1]
    
    response = await api_client.get_ideas_by_category(category)
    
    if "error" in response:
        await callback.answer(f"❌ {response['error']}")
        return
    
    if not response:
        await callback.message.edit_text("😔 В этой категории пока нет идей")
        return
    
    ideas_text = f"📂 <b>Категория: {category}</b>\n\n"
    for i, idea in enumerate(response[:5], 1):  # Показываем только 5 идей
        ideas_text += f"{i}. <b>{idea['title']}</b>\n{idea['description'][:100]}...\n\n"
    
    if len(response) > 5:
        ideas_text += f"И еще {len(response) - 5} идей..."
    
    await callback.message.edit_text(ideas_text)

@router.callback_query(F.data.startswith("propose_"))
async def propose_date(callback: CallbackQuery):
    """Предложить свидание партнеру"""
    idea_id = int(callback.data.split("propose_")[1])
    
    # Получаем пару пользователя
    pair_response = await api_client.get_user_pair(callback.from_user.id)
    
    if "error" in pair_response:
        await callback.answer("❌ Вы не состоите в паре")
        return
    
    # Создаем предложение свидания
    proposal_response = await api_client.create_date_proposal(
        pair_id=pair_response['id'],
        proposer_telegram_id=callback.from_user.id,
        idea_id=idea_id
    )
    
    if "error" in proposal_response:
        await callback.answer(f"❌ {proposal_response['error']}")
        return
    
    await callback.message.edit_text(
        "✅ Предложение отправлено партнеру!\n\n"
        "Ожидайте ответа 💕"
    )
    
    # Здесь можно добавить отправку уведомления партнеру

@router.message(F.text == "📋 Мои предложения")
async def show_pending_proposals(message: Message):
    """Показ входящих предложений"""
    response = await api_client.get_pending_proposals(message.from_user.id)
    
    if "error" in response:
        await message.answer(f"❌ {response['error']}")
        return
    
    if not response:
        await message.answer("📭 У вас нет новых предложений свиданий")
        return
    
    for proposal in response:
        idea = proposal['idea']
        proposer = proposal['proposer']
        
        text = (
            f"💌 <b>Предложение от {proposer['first_name']}</b>\n\n"
            f"💡 <b>{idea['title']}</b>\n"
            f"📝 {idea['description']}\n\n"
            f"🏷 Категория: {idea['category']}\n"
            f"💰 Бюджет: {idea['budget_level']}"
        )
        
        await message.answer(
            text,
            reply_markup=get_proposal_response_keyboard(proposal['id'])
        )

@router.callback_query(F.data.startswith("accept_") | F.data.startswith("decline_"))
async def respond_to_proposal(callback: CallbackQuery):
    """Ответ на предложение свидания"""
    action, proposal_id = callback.data.split("_")
    proposal_id = int(proposal_id)
    accepted = action == "accept"
    
    response = await api_client.respond_to_proposal(
        proposal_id=proposal_id,
        responder_telegram_id=callback.from_user.id,
        accepted=accepted
    )
    
    if "error" in response:
        await callback.answer(f"❌ {response['error']}")
        return
    
    if accepted:
        await callback.message.edit_text(
            "✅ Предложение принято!\n\n"
            "Отличного свидания! 💕"
        )
    else:
        await callback.message.edit_text(
            "❌ Предложение отклонено\n\n"
            "Возможно, в следующий раз найдется что-то подходящее 😊"
        )