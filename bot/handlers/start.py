from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import main_menu, pair_setup_menu, back_to_menu_button

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    user = await db.get_user(message.from_user.id)
    
    # Регистрируем нового пользователя
    if not user:
        success = await db.add_user(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            username=message.from_user.username
        )
        if success:
            user = await db.get_user(message.from_user.id)
    
    # Проверяем, есть ли у пользователя пара
    pair = await db.get_user_pair(user['id'])
    
    if not pair:
        # Пользователь без пары
        await message.answer(
            f"Привет, {user['name']}! 👋\n\n"
            "🌟 Добро пожаловать в бота для романтических свиданий!\n\n"
            "Здесь вы с партнером можете:\n"
            "• 💡 Получать ежедневные идеи для свиданий\n"
            "• 💕 Предлагать друг другу активности\n"
            "• 📚 Вести историю ваших встреч\n\n"
            "Для начала нужно создать пару или присоединиться к существующей:",
            reply_markup=pair_setup_menu()
        )
    elif not pair['user2_id']:
        # Пользователь создал пару, но партнер еще не присоединился
        await message.answer(
            f"Привет, {user['name']}! 👋\n\n"
            f"Ваш код приглашения: `{pair['invite_code']}`\n\n"
            "Отправьте этот код своему партнеру, чтобы он мог присоединиться к паре.\n"
            "Партнер должен написать боту команду:\n"
            f"`/join {pair['invite_code']}`",
            parse_mode="Markdown",
            reply_markup=back_to_menu_button()
        )
    else:
        # У пользователя есть полная пара
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await message.answer(
            f"Привет, {user['name']}! 👋\n\n"
            f"Ваш партнер: {partner['name']} 💕\n\n"
            "Что будем делать?",
            reply_markup=main_menu()
        )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.message.edit_text(
            "Для использования бота нужно создать пару или присоединиться к существующей:",
            reply_markup=pair_setup_menu()
        )
    else:
        partner_id = await db.get_partner_id(user['id'])
        partner = await db.get_user_by_id(partner_id)
        
        await callback.message.edit_text(
            f"Ваш партнер: {partner['name']} 💕\n\n"
            "Что будем делать?",
            reply_markup=main_menu()
        )
    
    await callback.answer()