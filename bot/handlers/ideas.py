from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import IdeaStates, DateProposalStates
from services.api_client import (
    get_ideas, add_idea, update_idea, delete_idea, get_random_idea,
    get_user_by_telegram_id, get_user_couple, create_date_proposal
)
from keyboards.inline import idea_action_keyboard
from loguru import logger
import random

router = Router()

@router.message(F.text == "/ideas")
async def show_ideas(message: Message):
    """Показать все идеи"""
    try:
        ideas = await get_ideas()
        if not ideas:
            return await message.answer("На данный момент нет идей 😔")
        
        for idea in ideas:
            await message.answer(
                f"📝 *{idea['title']}*\n{idea['description']}",
                parse_mode="Markdown",
                reply_markup=idea_action_keyboard(idea_id=idea['id'])
            )
    except Exception as e:
        logger.error(f"Error getting ideas: {e}")
        await message.answer("Произошла ошибка при получении идей 😔")

@router.callback_query(F.data.startswith("idea_"))
async def idea_action_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик действий с идеями"""
    try:
        action, idea_id = callback.data.split('_', 1)
        await state.update_data(idea_id=int(idea_id))
        
        if action == "idea_edit":
            await state.set_state(IdeaStates.creating_title)
            await callback.message.answer("Введите новый заголовок:")
        elif action == "idea_delete":
            await delete_idea(int(idea_id))
            await callback.message.answer("Идея удалена ✅")
        elif action == "idea_like":
            await callback.message.edit_text("❤️ Идея понравилась!")
        elif action == "idea_dislike":
            await callback.message.edit_text("👎 Идея не понравилась")
        elif action == "idea_create_date":
            # Создаем предложение свидания на основе идеи
            await create_date_from_idea(callback, int(idea_id))
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in idea action handler: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "get_idea")
async def get_random_idea_handler(callback: CallbackQuery):
    """Получить случайную идею для свидания"""
    try:
        ideas = await get_ideas()
        if not ideas:
            await callback.message.answer("На данный момент нет идей 😔")
            return
        
        # Выбираем случайную идею
        random_idea = random.choice(ideas)
        
        await callback.message.answer(
            f"💡 *Идея для свидания:*\n\n"
            f"📝 *{random_idea['title']}*\n"
            f"{random_idea['description']}",
            parse_mode="Markdown",
            reply_markup=idea_action_keyboard(idea_id=random_idea['id'])
        )
    except Exception as e:
        logger.error(f"Error getting random idea: {e}")
        await callback.message.answer("Произошла ошибка при получении идеи 😔")
    
    await callback.answer()

@router.callback_query(F.data == "suggest_date")
async def suggest_date_handler(callback: CallbackQuery, state: FSMContext):
    """Предложить свидание партнеру"""
    try:
        # Получаем пользователя
        user = await get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден. Пожалуйста, зарегистрируйтесь.")
            return
        
        # Получаем пару пользователя
        couple = await get_user_couple(user['id'])
        if not couple:
            await callback.message.answer("❌ Вы не состоите в паре. Создайте пару или присоединитесь к существующей.")
            return
        
        # Проверяем, что пара завершена (есть оба партнера)
        if not couple.get('user2_id'):
            await callback.message.answer("❌ Ваша пара не завершена. Пригласите партнера присоединиться к паре.")
            return
        
        # Сохраняем данные пары в состояние
        await state.update_data(couple_id=couple['id'], user_id=user['id'])
        
        # Показываем доступные идеи для предложения
        ideas = await get_ideas()
        if not ideas:
            await callback.message.answer("На данный момент нет идей для свидания 😔")
            return
        
        await state.set_state(DateProposalStates.selecting_idea)
        await callback.message.answer(
            "💕 Выберите идею для свидания:",
            reply_markup=await create_ideas_selection_keyboard(ideas)
        )
        
    except Exception as e:
        logger.error(f"Error in suggest_date_handler: {e}")
        await callback.message.answer("Произошла ошибка при создании предложения свидания 😔")
    
    await callback.answer()

@router.callback_query(F.data.startswith("select_idea_"), DateProposalStates.selecting_idea)
async def select_idea_for_date(callback: CallbackQuery, state: FSMContext):
    """Выбрать идею для предложения свидания"""
    try:
        idea_id = int(callback.data.split('_')[-1])
        data = await state.get_data()
        
        # Создаем предложение свидания
        proposal = await create_date_proposal(
            couple_id=data['couple_id'],
            idea_id=idea_id,
            proposer_id=data['user_id']
        )
        
        await callback.message.answer(
            "✅ Предложение свидания отправлено партнеру!\n"
            "Он получит уведомление и сможет принять или отклонить предложение."
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error selecting idea for date: {e}")
        await callback.message.answer("Произошла ошибка при создании предложения 😔")
    
    await callback.answer()

@router.callback_query(F.data == "my_suggestions")
async def my_suggestions_handler(callback: CallbackQuery):
    """Показать мои предложения"""
    try:
        # Получаем пользователя
        user = await get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден.")
            return
        
        # Получаем пару пользователя
        couple = await get_user_couple(user['id'])
        if not couple:
            await callback.message.answer("❌ Вы не состоите в паре.")
            return
        
        # Получаем историю предложений
        from services.api_client import get_date_history
        history = await get_date_history(couple['id'])
        
        if not history:
            await callback.message.answer("📋 У вас пока нет предложений свиданий.")
            return
        
        await callback.message.answer("📋 *Ваши предложения свиданий:*", parse_mode="Markdown")
        
        for event in history:
            status_emoji = {
                'pending': '⏳',
                'accepted': '✅',
                'rejected': '❌',
                'completed': '🎉'
            }.get(event.get('status', 'pending'), '❓')
            
            await callback.message.answer(
                f"{status_emoji} *{event.get('idea_title', 'Неизвестная идея')}*\n"
                f"📝 {event.get('idea_description', 'Описание отсутствует')}\n"
                f"📅 Создано: {event.get('created_at', 'Неизвестно')}\n"
                f"🔄 Статус: {event.get('status', 'pending')}",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error in my_suggestions_handler: {e}")
        await callback.message.answer("Произошла ошибка при получении предложений 😔")
    
    await callback.answer()

async def create_date_from_idea(callback: CallbackQuery, idea_id: int):
    """Создать предложение свидания на основе идеи"""
    try:
        # Получаем пользователя
        user = await get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден.")
            return
        
        # Получаем пару пользователя
        couple = await get_user_couple(user['id'])
        if not couple:
            await callback.message.answer("❌ Вы не состоите в паре.")
            return
        
        # Создаем предложение свидания
        proposal = await create_date_proposal(
            couple_id=couple['id'],
            idea_id=idea_id,
            proposer_id=user['id']
        )
        
        await callback.message.answer(
            "✅ Предложение свидания создано!\n"
            "Ваш партнер получит уведомление."
        )
        
    except Exception as e:
        logger.error(f"Error creating date from idea: {e}")
        await callback.message.answer("Произошла ошибка при создании предложения свидания 😔")

async def create_ideas_selection_keyboard(ideas):
    """Создать клавиатуру для выбора идей"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    for idea in ideas[:10]:  # Ограничиваем количество
        keyboard.append([
            InlineKeyboardButton(
                text=f"💡 {idea['title'][:30]}...",
                callback_data=f"select_idea_{idea['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_selection")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Остальные обработчики для добавления/редактирования идей
@router.message(F.text == "/idea_add")
async def idea_add_start(message: Message, state: FSMContext):
    """Начать добавление новой идеи"""
    await state.set_state(IdeaStates.creating_title)
    await message.answer("Введите заголовок идеи:")

@router.message(IdeaStates.creating_title)
async def idea_add_desc(message: Message, state: FSMContext):
    """Ввод описания идеи"""
    await state.update_data(title=message.text)
    await state.set_state(IdeaStates.creating_description)
    await message.answer("Введите описание идеи:")

@router.message(IdeaStates.creating_description)
async def idea_add_category(message: Message, state: FSMContext):
    """Ввод категории идеи"""
    await state.update_data(description=message.text)
    await state.set_state(IdeaStates.creating_category)
    await message.answer("Введите категорию идеи (например: романтика, приключения, дом):")

@router.message(IdeaStates.creating_category)
async def idea_add_send(message: Message, state: FSMContext):
    """Сохранить идею"""
    try:
        data = await state.get_data()
        await add_idea(data["title"], data["description"], message.text)
        await message.answer("Идея добавлена ✅")
    except Exception as e:
        logger.error(f"Error adding idea: {e}")
        await message.answer("Произошла ошибка при добавлении идеи 😔")
    
    await state.clear()

@router.callback_query(F.data == "cancel_selection")
async def cancel_selection(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор"""
    await state.clear()
    await callback.message.answer("Выбор отменен")
    await callback.answer()