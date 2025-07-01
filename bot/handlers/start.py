from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.services.api_client import api_client
from bot.keyboards.inline import get_main_menu, get_back_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """/start - function to handle the start command"""
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Check if user already exists
    user = await api_client.get_user_by_telegram_id(user_id)
    
    if user:
        # User is already registered
        await message.answer(
            f"Привет, {user.name}! 👋\n\n"
            "Добро пожаловать обратно в бот для пар! 💕\n"
            "Выбери, что хочешь сделать:",
            reply_markup=get_main_menu()
        )
    else:
        # New user, prompt registration
        await message.answer(
            f"Привет, {message.from_user.first_name or 'друг'}! 👋\n\n"
            "Добро пожаловать в бот для пар! 💕\n\n"
            "Этот бот поможет тебе:\n"
            "• Создать пару с партнером\n"
            "• Найти идеи для свиданий\n"
            "• Планировать романтические встречи\n\n"
            "Для начала тебе нужно зарегистрироваться. "
            "Нажми на кнопку ниже, чтобы продолжить! ⬇️",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="start_registration")]
            ])
        )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """/help - function to show help information"""
    help_text = """
🤖 <b>Помощь по боту для пар</b>

<b>Основные функции:</b>
👫 <b>Создание пары</b> - объединение с партнером
💡 <b>Идеи для свиданий</b> - получить вдохновение
💕 <b>Предложение свидания</b> - пригласить на встречу
📋 <b>Мои свидания</b> - история и планы

<b>Команды:</b>
/start - Главное меню
/help - Эта справка
/menu - Показать главное меню

<b>Как пользоваться:</b>
1️⃣ Сначала зарегистрируйся
2️⃣ Создай пару с партнером
3️⃣ Получай идеи и планируй свидания!

❓ <b>Нужна помощь?</b> Напиши @your_support_username
    """
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_back_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
    """show main menu"""
    await state.clear()
    
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        await message.answer(
            "📋 <b>Главное меню</b>\n\n"
            "Выбери нужное действие:",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "Сначала нужно зарегистрироваться! Используй команду /start",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="start_registration")]
            ])
        )


@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """return to main menu from any state"""
    await state.clear()
    
    user = await api_client.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await callback.message.edit_text(
            "📋 <b>Главное меню</b>\n\n"
            "Выбери нужное действие:",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        await callback.message.edit_text(
            "Сначала нужно зарегистрироваться!",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="start_registration")]
            ])
        )
    
    await callback.answer()