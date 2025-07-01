from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.states import PairStates
from bot.services.api_client import api_client
from bot.models.schemas import PairCreate
from bot.keyboards.inline import get_main_menu, get_cancel_keyboard, get_pair_invitation_keyboard
from bot.utils.decorators import require_registration

router = Router()


@router.callback_query(F.data == "create_pair")
@require_registration
async def start_create_pair(callback: types.CallbackQuery, state: FSMContext, user):
    """Create a pair with a partner"""
    
    # Check if user already has a pair
    existing_pair = await api_client.get_user_pair(user.id)
    
    if existing_pair:
        partner = existing_pair.user2 if existing_pair.user1.id == user.id else existing_pair.user1
        
        await callback.message.edit_text(
            f"💕 <b>У тебя уже есть пара!</b>\n\n"
            f"👤 <b>Партнер:</b> {partner.name}\n"
            f"📅 <b>Пара создана:</b> {existing_pair.created_at.strftime('%d.%m.%Y')}\n\n"
            f"Теперь вы можете планировать свидания вместе! 🎉",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        await callback.answer()
        return
    
    await state.set_state(PairStates.waiting_for_partner_username)
    
    await callback.message.edit_text(
        "👫 <b>Создание пары</b>\n\n"
        "Укажи username твоего партнера в Telegram (без @).\n"
        "Например: <code>john_doe</code>\n\n"
        "⚠️ Убедись, что партнер тоже зарегистрирован в этом боте!",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(PairStates.waiting_for_partner_username)
async def process_partner_username(message: types.Message, state: FSMContext):
    """Update partner username during pair creation"""
    username = message.text.strip().replace("@", "")
    
    if not username:
        await message.answer(
            "❌ Пожалуйста, укажи корректный username.\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Get current user from state
    current_user = await api_client.get_user_by_telegram_id(message.from_user.id)
    if not current_user:
        await message.answer("❌ Ошибка: пользователь не найден")
        await state.clear()
        return
    
    # Check if user is trying to pair with themselves
    if username.lower() == (current_user.username or "").lower():
        await message.answer(
            "😅 Нельзя создать пару с самим собой!\n"
            "Укажи username своего партнера:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Find the partner by username
    partner = await api_client.get_user_by_username(username)
    
    if not partner:
        await message.answer(
            f"❌ Пользователь @{username} не найден.\n\n"
            "Убедись, что:\n"
            "• Username указан правильно\n"
            "• Партнер зарегистрирован в боте\n\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Check if partner is already paired
    partner_pair = await api_client.get_user_pair(partner.id)
    if partner_pair:
        await message.answer(
            f"❌ У пользователя @{username} уже есть пара.\n"
            "Попробуй указать другого партнера:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Save partner in state
    await state.update_data(partner=partner)
    
    # Create the pair
    pair_data = PairCreate(
        user1_id=current_user.id,
        user2_id=partner.id
    )
    
    pair = await api_client.create_pair(pair_data)
    
    if pair:
        await state.clear()
        
        await message.answer(
            f"✅ <b>Пара создана!</b>\n\n"
            f"👤 <b>Ты:</b> {current_user.name}\n"
            f"💕 <b>Партнер:</b> {partner.name}\n\n"
            f"Теперь вы можете планировать свидания вместе! 🎉\n"
            f"Партнер получит уведомление о создании пары.",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
        # Send notification to partner
        try:
            from bot.main import bot  # Import bot instance here to avoid circular import issues
            
            await bot.send_message(
                partner.telegram_id,
                f"💕 <b>Отличные новости!</b>\n\n"
                f"Пользователь {current_user.name} создал с тобой пару! 🎉\n\n"
                f"Теперь вы можете планировать свидания вместе.\n"
                f"Используй /menu для доступа к функциям бота.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send pair notification: {e}")
        
        logger.info(f"Pair created: {current_user.name} + {partner.name}")
    else:
        await message.answer(
            "❌ <b>Ошибка создания пары</b>\n\n"
            "Не удалось создать пару. Попробуй еще раз позже.",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        await state.clear()


@router.callback_query(F.data == "cancel", PairStates.waiting_for_partner_username)
async def cancel_pair_creation(callback: types.CallbackQuery, state: FSMContext):
    """Cancel pair creation process"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Создание пары отменено.",
        reply_markup=get_main_menu()
    )
    await callback.answer("Создание пары отменено")