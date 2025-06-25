from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards.inline import main_menu, pair_setup_menu, back_to_menu_button

router = Router()

class PairStates(StatesGroup):
    waiting_for_join_code = State()

@router.callback_query(F.data == "create_pair")
async def create_pair_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик создания пары"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем, есть ли уже пара
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await callback.answer("У вас уже есть пара!", show_alert=True)
        return
    
    try:
        # Создаем пару
        invite_code = await db.create_pair(user['id'])
        
        await callback.message.edit_text(
            f"🎉 Пара создана!\n\n"
            f"Ваш код приглашения: `{invite_code}`\n\n"
            "📋 Отправьте этот код своему партнеру\n"
            "👥 Партнер должен написать боту:\n"
            f"`/join {invite_code}`\n\n"
            "Или нажать кнопку 'Присоединиться к паре' и ввести код.",
            parse_mode="Markdown",
            reply_markup=back_to_menu_button()
        )
        
        await callback.answer("Пара успешно создана! 🎉")
        
    except Exception as e:
        await callback.answer(f"Ошибка при создании пары: {e}", show_alert=True)

@router.callback_query(F.data == "join_pair")
async def join_pair_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик присоединения к паре"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем, есть ли уже пара
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await callback.answer("У вас уже есть пара!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔗 Введите код приглашения:\n\n"
        "Код должен состоять из 6 символов (буквы и цифры).\n"
        "Например: ABC123",
        reply_markup=back_to_menu_button()
    )
    
    await state.set_state(PairStates.waiting_for_join_code)
    await callback.answer()

@router.message(PairStates.waiting_for_join_code)
async def process_join_code(message: Message, state: FSMContext):
    """Обработка кода приглашения"""
    invite_code = message.text.strip().upper()
    
    # Проверяем формат кода
    if len(invite_code) != 6:
        await message.answer(
            "❌ Неверный формат кода!\n\n"
            "Код должен состоять из 6 символов.\n"
            "Попробуйте еще раз:",
            reply_markup=back_to_menu_button()
        )
        return
    
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        await state.clear()
        return
    
    try:
        # Попытка присоединиться к паре
        success = await db.join_pair(user['id'], invite_code)
        
        if success:
            # Получаем информацию о партнере
            pair = await db.get_user_pair(user['id'])
            partner_id = pair['user1_id']  # Создатель пары
            partner = await db.get_user_by_id(partner_id)
            
            await message.answer(
                f"🎉 Вы успешно присоединились к паре!\n\n"
                f"Ваш партнер: {partner['name']} 💕\n\n"
                "Теперь вы можете пользоваться всеми функциями бота вместе!",
                reply_markup=main_menu()
            )
            
            # Уведомляем партнера
            try:
                from aiogram import Bot
                from config import BOT_TOKEN
                bot = Bot(token=BOT_TOKEN)
                
                await bot.send_message(
                    partner['telegram_id'],
                    f"🎉 {user['name']} присоединился к вашей паре!\n\n"
                    "Теперь вы можете пользоваться ботом вместе! 💕",
                    reply_markup=main_menu()
                )
                await bot.session.close()
            except Exception:
                pass  # Не критичная ошибка
            
        else:
            await message.answer(
                "❌ Не удалось присоединиться к паре!\n\n"
                "Возможные причины:\n"
                "• Неверный код приглашения\n"
                "• Пара уже заполнена\n"
                "• Вы не можете присоединиться к собственной паре\n\n"
                "Попробуйте еще раз:",
                reply_markup=back_to_menu_button()
            )
            return
            
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при присоединении к паре: {e}\n\n"
            "Попробуйте еще раз:",
            reply_markup=back_to_menu_button()
        )
        return
    
    await state.clear()

@router.message(Command("join"))
async def join_command_handler(message: Message, state: FSMContext):
    """Обработчик команды /join с кодом"""
    await state.clear()
    
    # Получаем код из команды
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Неверный формат команды!\n\n"
            "Используйте: `/join КОД_ПРИГЛАШЕНИЯ`\n"
            "Например: `/join ABC123`",
            parse_mode="Markdown",
            reply_markup=pair_setup_menu()
        )
        return
    
    invite_code = args[1].strip().upper()
    
    # Проверяем формат кода
    if len(invite_code) != 6:
        await message.answer(
            "❌ Неверный формат кода!\n\n"
            "Код должен состоять из 6 символов.",
            reply_markup=pair_setup_menu()
        )
        return
    
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return
    
    # Проверяем, есть ли уже пара
    existing_pair = await db.get_user_pair(user['id'])
    if existing_pair:
        await message.answer(
            "У вас уже есть пара!",
            reply_markup=main_menu()
        )
        return
    
    try:
        # Попытка присоединиться к паре
        success = await db.join_pair(user['id'], invite_code)
        
        if success:
            # Получаем информацию о партнере
            pair = await db.get_user_pair(user['id'])
            partner_id = pair['user1_id']  # Создатель пары
            partner = await db.get_user_by_id(partner_id)
            
            await message.answer(
                f"🎉 Вы успешно присоединились к паре!\n\n"
                f"Ваш партнер: {partner['name']} 💕\n\n"
                "Теперь вы можете пользоваться всеми функциями бота вместе!",
                reply_markup=main_menu()
            )
            
            # Уведомляем партнера
            try:
                from aiogram import Bot
                from config import BOT_TOKEN
                bot = Bot(token=BOT_TOKEN)
                
                await bot.send_message(
                    partner['telegram_id'],
                    f"🎉 {user['name']} присоединился к вашей паре!\n\n"
                    "Теперь вы можете пользоваться ботом вместе! 💕",
                    reply_markup=main_menu()
                )
                await bot.session.close()
            except Exception:
                pass  # Не критичная ошибка
            
        else:
            await message.answer(
                "❌ Не удалось присоединиться к паре!\n\n"
                "Возможные причины:\n"
                "• Неверный код приглашения\n"
                "• Пара уже заполнена\n"
                "• Вы не можете присоединиться к собственной паре",
                reply_markup=pair_setup_menu()
            )
            
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при присоединении к паре: {e}",
            reply_markup=pair_setup_menu()
        )