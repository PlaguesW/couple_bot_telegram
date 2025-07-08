from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.api_client import (
    create_date_proposal, 
    respond_to_proposal, 
    get_date_history,
    get_user_by_telegram_id,
    get_user_couple
)
from keyboards.inline import proposal_response_keyboard

router = Router()

class DateStates(StatesGroup):
    idea_choice = State()
    date_choice = State()

@router.message(F.text == "/date_propose")
async def date_propose_start(message: Message, state: FSMContext):
    await state.set_state(DateStates.idea_choice)
    await message.answer("Введи ID идеи для предложения свидания:")

@router.message(DateStates.idea_choice)
async def date_propose_send(message: Message, state: FSMContext):
    try:
        idea_id = int(message.text)
        await state.update_data(idea_id=idea_id)
        await state.set_state(DateStates.date_choice)
        await message.answer("Напиши дату свидания (YYYY-MM-DD HH:MM):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID идеи (число):")

@router.callback_query(F.data.startswith("propose_idea_"))
async def propose_idea_handler(callback: CallbackQuery, state: FSMContext):
    try:
        idea_id = int(callback.data.split("_")[2])  
        
        # Получаем информацию о пользователе
        user_data = await get_user_by_telegram_id(callback.from_user.id)
        user_id = user_data["id"]
        
        # Получаем информацию о паре
        couple_data = await get_user_couple(user_id)
        couple_id = couple_data["id"]
        
        # Создаем предложение свидания
        await create_date_proposal(
            couple_id=couple_id,
            idea_id=idea_id,
            proposer_id=user_id
        )
        
        await callback.message.answer("Предложение отправлено ✅")
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при создании предложения: {str(e)}")
        await callback.answer()

@router.message(F.text == "/date_history")
async def date_history(message: Message):
    try:
        # Получаем информацию о пользователе
        user_data = await get_user_by_telegram_id(message.from_user.id)
        user_id = user_data["id"]
        
        # Получаем информацию о паре
        couple_data = await get_user_couple(user_id)
        couple_id = couple_data["id"]
        
        # Получаем историю свиданий
        history = await get_date_history(couple_id)
        
        if not history:
            return await message.answer("У вас ещё нет истории свиданий.")
        
        for evt in history:
            # Формируем текст в зависимости от структуры данных
            idea_title = evt.get("idea", {}).get("title", "Неизвестная идея")
            scheduled_date = evt.get("scheduled_date", "Дата не указана")
            date_status = evt.get("date_status", "pending")
            
            text = (
                f"💕 {idea_title}\n"
                f"📅 {scheduled_date}\n"
                f"📊 Статус: {date_status}"
            )
            
            if date_status == "pending":
                await message.answer(text, reply_markup=proposal_response_keyboard(evt["id"]))
            else:
                await message.answer(text)
                
    except Exception as e:
        await message.answer(f"Ошибка при получении истории: {str(e)}")

@router.callback_query(F.data.startswith("accept_"))
async def date_accept_handler(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
        
        # Получаем информацию о пользователе
        user_data = await get_user_by_telegram_id(callback.from_user.id)
        user_id = user_data["id"]
        
        await respond_to_proposal(event_id, "accepted", user_id)
        await callback.message.answer("Вы приняли предложение ✅")
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при принятии предложения: {str(e)}")
        await callback.answer()

@router.callback_query(F.data.startswith("reject_"))
async def date_reject_handler(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
        
        # Получаем информацию о пользователе
        user_data = await get_user_by_telegram_id(callback.from_user.id)
        user_id = user_data["id"]
        
        await respond_to_proposal(event_id, "rejected", user_id)
        await callback.message.answer("Вы отклонили предложение ❌")
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при отклонении предложения: {str(e)}")
        await callback.answer()

@router.callback_query(F.data.startswith("details_"))
async def date_details_handler(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
        
        # Здесь можно добавить получение детальной информации о событии
        # event_data = await get_date_event(event_id)
        
        await callback.answer("Детали события", show_alert=True)
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)