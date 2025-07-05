import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import get_categories_keyboard, get_ideas_keyboard, get_date_proposal_keyboard
from ..api_client import api_client
import logging

logger = logging.getLogger(__name__)

router = Router()

class DateStates(StatesGroup):
    choosing_category = State()
    viewing_ideas = State()
    creating_proposal = State()

@router.message(F.text == "💡 Получить идеи")
async def get_ideas_menu(message: Message, state: FSMContext):
    """Показать меню категорий идей"""
    await state.set_state(DateStates.choosing_category)
    
    keyboard = get_categories_keyboard()
    await message.answer(
        "🎯 Выберите категорию для получения идей:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("category_"))
async def show_category_ideas(callback_query: CallbackQuery, state: FSMContext):
    """Показать идеи выбранной категории"""
    await callback_query.answer()
    
    category = callback_query.data.split("_")[1]
    logger.info(f"Requesting ideas for category: {category}")
    
    try:
        response = await api_client.get_ideas_by_category(category)
        logger.info(f"API response: {response}")
        
        # Проверяем наличие ошибки
        if "error" in response:
            await callback_query.message.answer(
                "❌ Произошла ошибка при получении идей. Попробуйте позже."
            )
            return
        
        # Обрабатываем ответ от API
        # Ответ может быть в разных форматах, проверяем все варианты
        ideas = []
        if isinstance(response, dict):
            ideas = response.get("ideas", response.get("data", []))
        elif isinstance(response, list):
            ideas = response
        
        if not ideas:
            await callback_query.message.answer(
                f"🤷‍♂️ Идеи для категории '{category}' не найдены."
            )
            return
        
        # Ограничиваем количество идей
        limited_ideas = ideas[:5] if len(ideas) > 5 else ideas
        
        # Формируем текст ответа
        category_names = {
            "romantic": "Романтические",
            "active": "Активные",
            "home": "Домашние",
            "creative": "Творческие",
            "adventure": "Приключения"
        }
        
        category_name = category_names.get(category, category.capitalize())
        text = f"💡 {category_name} идеи:\n\n"
        
        for i, idea in enumerate(limited_ideas, 1):
            if isinstance(idea, dict):
                title = idea.get("title", "Без названия")
                description = idea.get("description", "Без описания")
                text += f"{i}. **{title}**\n{description}\n\n"
            else:
                text += f"{i}. {str(idea)}\n\n"
        
        # Добавляем кнопки для действий
        keyboard = get_ideas_keyboard(category)
        
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(DateStates.viewing_ideas)
        
    except Exception as e:
        logger.error(f"Error in show_category_ideas: {str(e)}")
        await callback_query.message.answer(
            "❌ Произошла ошибка при обработке запроса."
        )

@router.callback_query(F.data.startswith("propose_"))
async def propose_date(callback_query: CallbackQuery, state: FSMContext):
    """Предложить паре пойти на свидание"""
    await callback_query.answer()
    
    category = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    try:
        # Получаем информацию о паре пользователя
        pair_response = await api_client.get_user_pair(user_id)
        
        if "error" in pair_response:
            await callback_query.message.answer(
                "❌ Вы не состоите в паре. Сначала создайте пару или присоединитесь к существующей."
            )
            return
        
        # Получаем идеи категории для предложения
        ideas_response = await api_client.get_ideas_by_category(category)
        
        if "error" in ideas_response:
            await callback_query.message.answer(
                "❌ Не удалось получить идеи для предложения."
            )
            return
        
        ideas = ideas_response.get("ideas", ideas_response.get("data", []))
        if not ideas:
            await callback_query.message.answer(
                "❌ Нет доступных идей для предложения."
            )
            return
        
        # Берем случайную идею или первую
        idea = ideas[0] if ideas else {"title": "Свидание", "description": f"Свидание в категории {category}"}
        idea_id = idea.get("id") if isinstance(idea, dict) else None
        
        # Создаем предложение о свидании
        proposal_data = {
            "proposer_id": user_id,
            "pair_id": pair_response.get("id"),
            "idea_id": idea_id,
            "idea_title": idea.get("title", "Свидание") if isinstance(idea, dict) else str(idea),
            "message": f"Предлагаю пойти на свидание: {idea.get('title', 'Свидание')}"
        }
        
        proposal_response = await api_client.create_date_proposal(proposal_data)
        
        if "error" in proposal_response:
            await callback_query.message.answer(
                "❌ Не удалось создать предложение о свидании."
            )
            return
        
        await callback_query.message.answer(
            f"✅ Предложение о свидании отправлено!\n\n"
            f"💡 Идея: {idea.get('title', 'Свидание')}\n"
            f"📝 Описание: {idea.get('description', 'Без описания')}\n\n"
            f"Ждем ответа от вашего партнера!"
        )
        
    except Exception as e:
        logger.error(f"Error in propose_date: {str(e)}")
        await callback_query.message.answer(
            "❌ Произошла ошибка при создании предложения."
        )

@router.callback_query(F.data.startswith("proposal_"))
async def handle_proposal_response(callback_query: CallbackQuery, state: FSMContext):
    """Обработка ответа на предложение о свидании"""
    await callback_query.answer()
    
    action = callback_query.data.split("_")[1]  # accept или decline
    proposal_id = int(callback_query.data.split("_")[2])
    
    try:
        accepted = action == "accept"
        response = await api_client.respond_to_proposal(proposal_id, accepted)
        
        if "error" in response:
            await callback_query.message.answer(
                "❌ Не удалось обработать ответ на предложение."
            )
            return
        
        if accepted:
            await callback_query.message.answer(
                "✅ Вы приняли предложение о свидании!\n"
                "🎉 Отлично проведите время вместе!"
            )
        else:
            await callback_query.message.answer(
                "❌ Вы отклонили предложение о свидании.\n"
                "Может быть, в следующий раз?"
            )
            
    except Exception as e:
        logger.error(f"Error in handle_proposal_response: {str(e)}")
        await callback_query.message.answer(
            "❌ Произошла ошибка при обработке ответа."
        )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    """Вернуться к выбору категорий"""
    await callback_query.answer()
    await state.set_state(DateStates.choosing_category)
    
    keyboard = get_categories_keyboard()
    await callback_query.message.edit_text(
        "🎯 Выберите категорию для получения идей:",
        reply_markup=keyboard
    )