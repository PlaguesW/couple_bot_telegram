from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states import RegistrationStates
from bot.services.api_client import api_client
from bot.models.schemas import UserCreate, GenderEnum
from bot.keyboards.inline import get_gender_keyboard, get_main_menu, get_cancel_keyboard

router = Router()


@router.callback_query(F.data == "start_registration")
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    """Start registration process"""
    await state.set_state(RegistrationStates.waiting_for_name)
    
    await callback.message.edit_text(
        "📝 <b>Регистрация</b>\n\n"
        "Как тебя зовут? Напиши свое имя:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user's name during registration"""
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer(
            "❌ Имя должно быть от 2 до 50 символов.\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Save name in state
    await state.update_data(name=name)
    await state.set_state(RegistrationStates.waiting_for_age)
    
    await message.answer(
        f"Приятно познакомиться, {name}! 😊\n\n"
        "Теперь укажи свой возраст (число от 16 до 100):",
        reply_markup=get_cancel_keyboard()
    )



@router.callback_query(F.data == "cancel")
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    """Cancel registration process"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Регистрация отменена.\n\n"
        "Ты можешь начать заново, используя команду /start"
    )
    await callback.answer("Регистрация отменена")