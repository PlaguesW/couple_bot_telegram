from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from api_client import api_client, APIError
from states import CoupleStates
from keyboards.inline import (
    couple_setup_keyboard, 
    main_menu_keyboard, 
    couple_info_keyboard,
    confirmation_keyboard,
    back_keyboard
)
from keyboards.reply import cancel_keyboard

router = Router()


@router.callback_query(F.data == "create_couple")
async def create_couple_callback(callback: CallbackQuery, user: dict, has_couple: bool, **kwargs):
    """Создать новую пару"""
    await callback.answer()
    
    if has_couple:
        await callback.message.edit_text(
            "❌ У вас уже есть пара! Сначала покиньте текущую пару, чтобы создать новую.",
            reply_markup=back_keyboard()
        )
        return
    
    try:
        async with api_client:
            couple_data = await api_client.create_couple(user["id"])
        
        invite_code = couple_data["invite_code"]
        
        await callback.message.edit_text(
            f"✅ Пара успешно создана!\n\n"
            f"🔗 **Код приглашения:** `{invite_code}`\n\n"
            f"Отправьте этот код своему партнеру, чтобы он мог присоединиться к паре.\n\n"
            f"💡 Код можно найти в разделе \"👫 Моя пара\"",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except APIError as e:
        logger.error(f"Error creating couple: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании пары. Попробуйте позже.",
            reply_markup=couple_setup_keyboard()
        )


@router.callback_query(F.data == "join_couple")
async def join_couple_callback(callback: CallbackQuery, state: FSMContext, user: dict, has_couple: bool, **kwargs):
    """Присоединиться к паре"""
    await callback.answer()
    
    if has_couple:
        await callback.message.edit_text(
            "❌ У вас уже есть пара! Сначала покиньте текущую пару, чтобы присоединиться к новой.",
            reply_markup=back_keyboard()
        )
        return
    
    await callback.message.edit_text(
        "🔗 Введите код приглашения от вашего партнера:\n\n"
        "Код состоит из 6 символов (например: ABC123)",
        reply_markup=back_keyboard()
    )
    await state.set_state(CoupleStates.waiting_for_invite_code)


@router.message(StateFilter(CoupleStates.waiting_for_invite_code))
async def process_invite_code(message: Message, state: FSMContext, user: dict, **kwargs):
    """Обработать код приглашения"""
    invite_code = message.text.strip().upper()
    
    if len(invite_code) != 6:
        await message.answer("❌ Код должен содержать 6 символов. Попробуйте еще раз:")
        return
    
    try:
        # Проверяем, существует ли пара с таким кодом
        async with api_client:
            couple_data = await api_client.get_couple_by_code(invite_code)
        
        # Проверяем, что пара не полная
        if couple_data.get("user2_id"):
            await message.answer(
                "❌ Эта пара уже полная. Попробуйте другой код:",
                reply_markup=back_keyboard()
            )
            return
        
        # Проверяем, что пользователь не пытается присоединиться к своей же паре
        if couple_data.get("user1_id") == user["id"]:
            await message.answer(
                "❌ Вы не можете присоединиться к своей собственной паре. Попробуйте другой код:",
                reply_markup=back_keyboard()
            )
            return
        
        # Сохраняем код для подтверждения
        await state.update_data(invite_code=invite_code)
        
        await message.answer(
            f"✅ Пара найдена!\n\n"
            f"🔗 Код: {invite_code}\n\n"
            f"Вы уверены, что хотите присоединиться к этой паре?",
            reply_markup=confirmation_keyboard("join_couple", invite_code)
        )
        await state.set_state(CoupleStates.waiting_for_confirmation)
        
    except APIError as e:
        if "404" in str(e):
            await message.answer(
                "❌ Пара с таким кодом не найдена. Проверьте код и попробуйте еще раз:",
                reply_markup=back_keyboard()
            )
        else:
            logger.error(f"Error checking invite code: {e}")
            await message.answer(
                "❌ Произошла ошибка при проверке кода. Попробуйте позже.",
                reply_markup=couple_setup_keyboard()
            )


@router.callback_query(F.data.startswith("confirm_join_couple"))
async def confirm_join_couple(callback: CallbackQuery, state: FSMContext, user: dict, **kwargs):
    """Подтвердить присоединение к паре"""
    await callback.answer()
    
    data = await state.get_data()
    invite_code = data.get("invite_code")
    
    if not invite_code:
        await callback.message.edit_text(
            "❌ Ошибка: код приглашения не найден.",
            reply_markup=couple_setup_keyboard()
        )
        await state.clear()
        return
    
    try:
        async with api_client:
            couple_data = await api_client.join_couple(user["id"], invite_code)
        
        await callback.message.edit_text(
            f"🎉 Поздравляем! Вы успешно присоединились к паре!\n\n"
            f"Теперь вы можете:\n"
            f"• 💡 Получать идеи для свиданий\n"
            f"• 💕 Предлагать свидания партнеру\n"
            f"• 📚 Вести историю ваших свиданий\n\n"
            f"Удачных свиданий! 💕",
            reply_markup=main_menu_keyboard()
        )
        
        await state.clear()
        
    except APIError as e:
        logger.error(f"Error joining couple: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при присоединении к паре. Попробуйте позже.",
            reply_markup=couple_setup_keyboard()
        )
        await state.clear()


@router.callback_query(F.data.startswith("cancel_join_couple"))
async def cancel_join_couple(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отменить присоединение к паре"""
    await callback.answer()
    
    await callback.message.edit_text(
        "❌ Присоединение к паре отменено.",
        reply_markup=couple_setup_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "couple_info")
async def couple_info_callback(callback: CallbackQuery, couple: dict, **kwargs):
    """Информация о паре"""
    await callback.answer()
    
    try:
        async with api_client:
            couple_data = await api_client.get_couple(couple["id"])
        
        # Получаем информацию о партнерах
        user1_name = couple_data.get("user1", {}).get("name", "Партнер 1")
        user2_name = couple_data.get("user2", {}).get("name", "Партнер 2") if couple_data.get("user2") else "Ожидание..."
        
        # Получаем статистику
        async with api_client:
            history = await api_client.get_date_history(couple["id"], limit=100)
        
        completed_dates = len([d for d in history if d.get("date_status") == "completed"])
        pending_dates = len([d for d in history if d.get("date_status") == "pending"])
        
        created_date = couple_data.get("created_at", "").split("T")[0] if couple_data.get("created_at") else "Неизвестно"
        
        info_text = f"""
👫 **Информация о паре**

**Участники:**
• {user1_name}
• {user2_name}

**Статистика:**
• 📅 Создана: {created_date}
• ✅ Завершенные свидания: {completed_dates}
• ⏳ Ожидающие предложения: {pending_dates}
• 📊 Всего предложений: {len(history)}

**Код приглашения:** `{couple_data.get('invite_code', 'Неизвестно')}`
        """
        
        await callback.message.edit_text(
            info_text,
            reply_markup=couple_info_keyboard(couple["id"]),
            parse_mode="Markdown"
        )
        
    except APIError as e:
        logger.error(f"Error getting couple info: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении информации о паре.",
            reply_markup=back_keyboard()
        )


@router.callback_query(F.data.startswith("couple_stats_"))
async def couple_stats_callback(callback: CallbackQuery, couple: dict, **kwargs):
    """Детальная статистика пары"""
    await callback.answer()
    
    try:
        async with api_client:
            history = await api_client.get_date_history(couple["id"], limit=100)
        
        # Анализируем статистику
        total_proposals = len(history)
        completed_dates = len([d for d in history if d.get("date_status") == "completed"])
        accepted_dates = len([d for d in history if d.get("date_status") == "accepted"])
        rejected_dates = len([d for d in history if d.get("date_status") == "rejected"])
        pending_dates = len([d for d in history if d.get("date_status") == "pending"])
        
        # Статистика по категориям
        categories = {}
        for event in history:
            if event.get("idea") and event.get("idea").get("category"):
                category = event["idea"]["category"]
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
        
        # Топ категории
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        stats_text = f"""
📊 **Детальная статистика пары**

**Общие показатели:**
• 📝 Всего предложений: {total_proposals}
• ✅ Завершенных свиданий: {completed_dates}
• 💕 Принятых предложений: {accepted_dates}
• ❌ Отклоненных предложений: {rejected_dates}
• ⏳ Ожидающих ответа: {pending_dates}

**Популярные категории:**
        """
        
        for i, (category, count) in enumerate(top_categories, 1):
            stats_text += f"{i}. {category}: {count} раз\n"
        
        if completed_dates > 0:
            success_rate = (completed_dates / total_proposals) * 100 if total_proposals > 0 else 0
            stats_text += f"\n🎯 **Процент завершенных свиданий:** {success_rate:.1f}%"
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=back_keyboard("couple_info"),
            parse_mode="Markdown"
        )
        
    except APIError as e:
        logger.error(f"Error getting couple stats: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении статистики.",
            reply_markup=back_keyboard("couple_info")
        )


@router.callback_query(F.data.startswith("invite_code_"))
async def invite_code_callback(callback: CallbackQuery, couple: dict, **kwargs):
    """Показать код приглашения"""
    await callback.answer()
    
    try:
        async with api_client:
            couple_data = await api_client.get_couple(couple["id"])
        
        invite_code = couple_data.get("invite_code")
        
        await callback.message.edit_text(
            f"🔗 **Код приглашения вашей пары:**\n\n"
            f"`{invite_code}`\n\n"
            f"Отправьте этот код партнеру, чтобы он мог присоединиться к паре.\n\n"
            f"💡 Код можно скопировать, нажав на него.",
            reply_markup=back_keyboard("couple_info"),
            parse_mode="Markdown"
        )
        
    except APIError as e:
        logger.error(f"Error getting invite code: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении кода приглашения.",
            reply_markup=back_keyboard("couple_info")
        )


# Обработчики для Reply клавиатур
@router.message(F.text == "👫 Моя пара")
async def couple_info_message(message: Message, couple: dict, **kwargs):
    """Информация о паре через Reply клавиатуру"""
    # Используем тот же код, что и в callback
    fake_callback = type('obj', (object,), {
        'answer': lambda: None,
        'message': message,
        'from_user': message.from_user
    })()
    
    await couple_info_callback(fake_callback, couple=couple, **kwargs)


@router.message(F.text == "➕ Создать пару")
async def create_couple_message(message: Message, user: dict, has_couple: bool, **kwargs):
    """Создать пару через Reply клавиатуру"""
    if has_couple:
        await message.answer(
            "❌ У вас уже есть пара! Сначала покиньте текущую пару, чтобы создать новую.",
            reply_markup=back_keyboard()
        )
        return
    
    try:
        async with api_client:
            couple_data = await api_client.create_couple(user["id"])
        
        invite_code = couple_data["invite_code"]
        
        await message.answer(
            f"✅ Пара успешно создана!\n\n"
            f"🔗 **Код приглашения:** `{invite_code}`\n\n"
            f"Отправьте этот код своему партнеру, чтобы он мог присоединиться к паре.\n\n"
            f"💡 Код можно найти в разделе \"👫 Моя пара\"",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except APIError as e:
        logger.error(f"Error creating couple: {e}")
        await message.answer(
            "❌ Произошла ошибка при создании пары. Попробуйте позже.",
            reply_markup=couple_setup_keyboard()
        )


@router.message(F.text == "🔗 Присоединиться")
async def join_couple_message(message: Message, state: FSMContext, user: dict, has_couple: bool, **kwargs):
    """Присоединиться к паре через Reply клавиатуру"""
    if has_couple:
        await message.answer(
            "❌ У вас уже есть пара! Сначала покиньте текущую пару, чтобы присоединиться к новой.",
            reply_markup=back_keyboard()
        )
        return
    
    await message.answer(
        "🔗 Введите код приглашения от вашего партнера:\n\n"
        "Код состоит из 6 символов (например: ABC123)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(CoupleStates.waiting_for_invite_code)