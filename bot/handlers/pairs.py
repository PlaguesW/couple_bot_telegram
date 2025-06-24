from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import Database
from keyboards.inline import get_pair_keyboard, get_join_keyboard

router = Router()

class PairStates(StatesGroup):
    waiting_for_pair_name = State()
    waiting_for_join_code = State()

@router.message(Command("create_pair"))
async def create_pair_command(message: Message, state: FSMContext):
    """Обработчик команды создания пары"""
    try:
        db = Database()
        user_id = message.from_user.id
        
        # Проверяем, зарегистрирован ли пользователь
        user = await db.get_user(user_id)
        if not user:
            await message.answer("❌ Сначала необходимо зарегистрироваться. Используйте /start")
            return
        
        # Проверяем, не состоит ли пользователь уже в паре
        existing_pair = await db.get_user_pair(user_id)
        if existing_pair:
            await message.answer("❌ Вы уже состоите в паре. Используйте /leave_pair чтобы покинуть текущую пару.")
            return
        
        await message.answer("💕 Введите название для вашей пары:")
        await state.set_state(PairStates.waiting_for_pair_name)
        
    except Exception as e:
        logging.error(f"Error in create_pair_command: {e}")
        await message.answer("❌ Произошла ошибка при создании пары. Попробуйте позже.")

@router.message(PairStates.waiting_for_pair_name)
async def process_pair_name(message: Message, state: FSMContext):
    """Обработка названия пары"""
    try:
        db = Database()
        user_id = message.from_user.id
        pair_name = message.text.strip()
        
        if len(pair_name) < 2:
            await message.answer("❌ Название пары должно содержать минимум 2 символа. Попробуйте еще раз:")
            return
        
        if len(pair_name) > 50:
            await message.answer("❌ Название пары не должно превышать 50 символов. Попробуйте еще раз:")
            return
        
        # Создаем пару
        pair_data = await db.create_pair(user_id, pair_name)
        
        if pair_data:
            pair_id, pair_code = pair_data
            await message.answer(
                f"✅ Пара '{pair_name}' успешно создана!\n\n"
                f"🔐 Код для присоединения: `{pair_code}`\n\n"
                f"Отправьте этот код вашему партнеру, чтобы он мог присоединиться к паре.",
                parse_mode="Markdown",
                reply_markup=get_pair_keyboard()
            )
        else:
            await message.answer("❌ Не удалось создать пару. Попробуйте позже.")
        
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error in process_pair_name: {e}")
        await message.answer("❌ Произошла ошибка при создании пары. Попробуйте позже.")
        await state.clear()

@router.message(Command("join"))
async def join_pair_command(message: Message, state: FSMContext):
    """Обработчик команды присоединения к паре"""
    try:
        db = Database()
        user_id = message.from_user.id
        
        # Проверяем, зарегистрирован ли пользователь
        user = await db.get_user(user_id)
        if not user:
            await message.answer("❌ Сначала необходимо зарегистрироваться. Используйте /start")
            return
        
        # Проверяем, не состоит ли пользователь уже в паре
        existing_pair = await db.get_user_pair(user_id)
        if existing_pair:
            await message.answer("❌ Вы уже состоите в паре. Используйте /leave_pair чтобы покинуть текущую пару.")
            return
        
        await message.answer("🔐 Введите код пары для присоединения:")
        await state.set_state(PairStates.waiting_for_join_code)
        
    except Exception as e:
        logging.error(f"Error in join_pair_command: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(PairStates.waiting_for_join_code)
async def process_join_code(message: Message, state: FSMContext):
    """Обработка кода присоединения к паре"""
    try:
        db = Database()
        user_id = message.from_user.id
        join_code = message.text.strip().upper()
        
        if len(join_code) != 6:
            await message.answer("❌ Код должен состоять из 6 символов. Попробуйте еще раз:")
            return
        
        # Пытаемся присоединиться к паре
        result = await db.join_pair(user_id, join_code)
        
        if result:
            pair_info = await db.get_pair_info(result)
            if pair_info:
                await message.answer(
                    f"✅ Вы успешно присоединились к паре '{pair_info['name']}'!\n\n"
                    f"💕 Теперь вы можете отправлять друг другу сообщения и предложения свиданий.",
                    reply_markup=get_pair_keyboard()
                )
                
                # Уведомляем партнера
                partner_id = await db.get_partner_id(user_id)
                if partner_id:
                    partner_name = message.from_user.first_name or "Ваш партнер"
                    await message.bot.send_message(
                        partner_id,
                        f"🎉 {partner_name} присоединился к вашей паре!"
                    )
            else:
                await message.answer("❌ Произошла ошибка при получении информации о паре.")
        else:
            await message.answer("❌ Неверный код пары или пара уже полная. Проверьте код и попробуйте еще раз.")
        
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error in process_join_code: {e}")
        await message.answer("❌ Произошла ошибка при присоединении к паре. Попробуйте позже.")
        await state.clear()

@router.message(Command("pair_info"))
async def pair_info_command(message: Message):
    """Информация о текущей паре"""
    try:
        db = Database()
        user_id = message.from_user.id
        
        pair = await db.get_user_pair(user_id)
        if not pair:
            await message.answer("❌ Вы не состоите в паре. Используйте /create_pair или /join")
            return
        
        pair_info = await db.get_pair_info(pair['id'])
        if not pair_info:
            await message.answer("❌ Не удалось получить информацию о паре.")
            return
        
        partner_info = await db.get_partner_info(user_id)
        partner_name = "Не найден"
        if partner_info:
            partner_name = partner_info.get('first_name', 'Неизвестный')
            if partner_info.get('username'):
                partner_name += f" (@{partner_info['username']})"
        
        stats = await db.get_pair_stats(pair['id'])
        
        info_text = (
            f"💕 **Информация о паре**\\n\\n"
            f"📝 Название: {pair_info['name']}\\n"
            f"👫 Партнер: {partner_name}\\n"
            f"📅 Создана: {pair_info['created_at'].strftime('%d.%m.%Y')}\\n\\n"
            f"📊 **Статистика:**\\n"
            f"💌 Сообщений: {stats.get('messages', 0)}\\n"
            f"💡 Предложений свиданий: {stats.get('proposals', 0)}\\n"
            f"✅ Принятых предложений: {stats.get('accepted', 0)}"
        )
        
        await message.answer(info_text, parse_mode="MarkdownV2")
        
    except Exception as e:
        logging.error(f"Error in pair_info_command: {e}")
        await message.answer("❌ Произошла ошибка при получении информации о паре.")

@router.message(Command("leave_pair"))
async def leave_pair_command(message: Message):
    """Покинуть текущую пару"""
    try:
        db = Database()
        user_id = message.from_user.id
        
        pair = await db.get_user_pair(user_id)
        if not pair:
            await message.answer("❌ Вы не состоите в паре.")
            return
        
        # Получаем информацию о партнере для уведомления
        partner_info = await db.get_partner_info(user_id)
        
        # Покидаем пару
        success = await db.leave_pair(user_id)
        
        if success:
            await message.answer("✅ Вы покинули пару. Используйте /create_pair или /join для создания новой пары.")
            
            # Уведомляем партнера
            if partner_info:
                user_name = message.from_user.first_name or "Ваш партнер"
                await message.bot.send_message(
                    partner_info['telegram_id'],
                    f"💔 {user_name} покинул пару. Используйте /create_pair или /join для создания новой пары."
                )
        else:
            await message.answer("❌ Произошла ошибка при попытке покинуть пару.")
        
    except Exception as e:
        logging.error(f"Error in leave_pair_command: {e}")
        await message.answer("❌ Произошла ошибка при попытке покинуть пару.")

@router.callback_query(F.data == "pair_info")
async def pair_info_callback(callback: CallbackQuery):
    """Callback для информации о паре"""
    await callback.message.delete()
    await pair_info_command(callback.message)
    await callback.answer()

@router.callback_query(F.data == "leave_pair")
async def leave_pair_callback(callback: CallbackQuery):
    """Callback для выхода из пары"""
    await callback.message.delete()
    await leave_pair_command(callback.message)
    await callback.answer()