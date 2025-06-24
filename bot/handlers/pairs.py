from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.inline import main_menu, back_to_menu_button

router = Router()

class PairStates(StatesGroup):
    waiting_for_join_code = State()

@router.callback_query(F.data == "create_pair")
async def create_pair_handler(callback: CallbackQuery):
    """Создание новой пары"""
    user = await db.get_user(callback.from_user.id)
    
    # Проверяем, нет ли уже пары
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await message.answer("У вас уже есть пара!")
        return
    
    if len(invite_code) != 6:
        await message.answer(
            "❌ Неверный формат кода!\n"
            "Код должен состоять из 6 символов."
        )
        return
    
    success = await db.join_pair(user['id'], invite_code)
    
    if success:
        await state.clear()
        
        # Получаем информацию о партнере
        pair = await db.get_user_pair(user['id'])
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await message.answer(
            f"🎉 Отлично! Вы присоединились к паре!\n\n"
            f"Ваш партнер: {partner['name']} 💕\n\n"
            "Теперь вы можете использовать все функции бота!",
            reply_markup=main_menu()
        )
        
        # Уведомляем партнера
        try:
            from main import bot
            await bot.send_message(
                partner['telegram_id'],
                f"🎉 {user['name']} присоединился к вашей паре!\n\n"
                "Теперь вы можете начать планировать свидания вместе! 💕",
                reply_markup=main_menu()
            )
        except Exception:
            pass  # Игнорируем ошибки отправки уведомлений
    else:
        await message.answer(
            "❌ Код не найден или пара уже заполнена!\n\n"
            "Проверьте правильность кода или попросите партнера создать новую пару."
        )

@router.callback_query(F.data == "pair_info")
async def pair_info_handler(callback: CallbackQuery):
    """Информация о паре"""
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("У вас нет активной пары!", show_alert=True)
        return
    
    partner_id = await db.get_partner_id(user['id'])
    partner = await db.get_user_by_id(partner_id)
    
    # Статистика пары
    history = await db.get_date_history(pair['id'], limit=100)
    completed_dates = len([h for h in history if h['status'] == 'accepted'])
    pending_proposals = await db.get_pending_proposals(pair['id'])
    
    pair_date = pair['created_at'].strftime("%d.%m.%Y")
    
    await callback.message.edit_text(
        f"👫 Информация о паре\n\n"
        f"💕 Партнер: {partner['name']}\n"
        f"📅 Пара создана: {pair_date}\n"
        f"🎯 Завершенных свиданий: {completed_dates}\n"
        f"⏳ Ожидающих предложений: {len(pending_proposals)}\n"
        f"🔗 Код пары: `{pair['invite_code']}`",
        parse_mode="Markdown",
        reply_markup=back_to_menu_button()
    )
    
    await callback.answer()
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await callback.answer("У вас уже есть пара!", show_alert=True)
        return
    
    # Создаем пару
    invite_code = await db.create_pair(user['id'])
    
    await callback.message.edit_text(
        f"✅ Пара создана!\n\n"
        f"Ваш код приглашения: `{invite_code}`\n\n"
        "Отправьте этот код своему партнеру.\n"
        "Партнер должен написать команду:\n"
        f"`/join {invite_code}`\n\n"
        "Или попросите партнера нажать кнопку 'Присоединиться к паре' "
        "и ввести код.",
        parse_mode="Markdown",
        reply_markup=back_to_menu_button()
    )
    
    await callback.answer("Пара создана! 🎉")

@router.callback_query(F.data == "join_pair")
async def join_pair_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса присоединения к паре"""
    user = await db.get_user(callback.from_user.id)
    
    # Проверяем, нет ли уже пары
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await callback.answer("У вас уже есть пара!", show_alert=True)
        return
    
    await state.set_state(PairStates.waiting_for_join_code)
    
    await callback.message.edit_text(
        "💌 Введите код приглашения от вашего партнера:\n\n"
        "Код состоит из 6 символов (например: ABC123)",
        reply_markup=back_to_menu_button()
    )
    
    await callback.answer()

@router.message(PairStates.waiting_for_join_code)
async def join_pair_process(message: Message, state: FSMContext):
    """Обработка кода приглашения"""
    invite_code = message.text.strip().upper()
    
    if len(invite_code) != 6:
        await message.answer(
            "❌ Неверный формат кода!\n"
            "Код должен состоять из 6 символов."
        )
        return
    
    user = await db.get_user(message.from_user.id)
    success = await db.join_pair(user['id'], invite_code)
    
    if success:
        await state.clear()
        
        # Получаем информацию о партнере
        pair = await db.get_user_pair(user['id'])
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await message.answer(
            f"🎉 Отлично! Вы присоединились к паре!\n\n"
            f"Ваш партнер: {partner['name']} 💕\n\n"
            "Теперь вы можете использовать все функции бота!",
            reply_markup=main_menu()
        )
        
        # Уведомляем партнера
        try:
            from main import bot
            await bot.send_message(
                partner['telegram_id'],
                f"🎉 {user['name']} присоединился к вашей паре!\n\n"
                "Теперь вы можете начать планировать свидания вместе! 💕",
                reply_markup=main_menu()
            )
        except Exception:
            pass  # Игнорируем ошибки отправки уведомлений
    else:
        await message.answer(
            "❌ Код не найден или пара уже заполнена!\n\n"
            "Проверьте правильность кода или попросите партнера создать новую пару."
        )

@router.command(Command("join"))
async def join_pair_command(message: Message, state: FSMContext):
    """Прямое присоединение к паре через команду /join CODE"""
    args = message.text.split()
    
    if len(args) != 2:
        await message.answer(
            "Использование: `/join КОД`\n\n"
            "Например: `/join ABC123`",
            parse_mode="Markdown"
        )
        return
    
    invite_code = args[1].strip().upper()
    user = await db.get_user(message.from_user.id)
    
    # Проверяем, нет ли уже пары