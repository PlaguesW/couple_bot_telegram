from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from api_client import propose_date, respond_to_date, get_history
from keyboards.inline import respond_keyboard

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
    await state.update_data(idea_id=int(message.text))
    await state.set_state(DateStates.date_choice)
    await message.answer("Напиши дату свидания (YYYY-MM-DD HH:MM):")

@router.message(DateStates.date_choice)
async def date_propose_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    await propose_date(message.from_user.id, data["idea_id"], message.text)
    await message.answer("Предложение отправлено ✅")
    await state.clear()

@router.message(F.text == "/date_history")
async def date_history(message: Message):
    history = await get_history(message.from_user.id)
    if not history:
        return await message.answer("У вас ещё нет истории свиданий.")
    for evt in history:
        text = (
            f"{evt['idea_title']} — {evt['scheduled_date']}\n"
            f"Статус: {evt['date_status']}"
        )
        if evt["date_status"] == "pending":
            await message.answer(text, reply_markup=respond_keyboard(evt["id"]))
        else:
            await message.answer(text)

@router.callback_query(F.data.startswith("date_"))
async def date_response_handler(callback: CallbackQuery):
    action, event_id = callback.data.split(":")
    status = "accepted" if action == "date_accept" else "rejected"
    await respond_to_date(callback.from_user.id, int(event_id), status)
    await callback.message.answer(f"Вы {status} предложение ✅")
    await callback.answer()