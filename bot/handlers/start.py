from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger

from api_client import api_client, APIError
from states import RegistrationStates
from keyboards.inline import main_menu_keyboard, couple_setup_keyboard
from keyboards.reply import registration_keyboard, main_menu_reply, cancel_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, is_registered: bool, user_info: dict = None, **kwargs):
    """Команда /start"""
    if is_registered:
        await message.answer(
            "👋 Добро пожаловать обратно!\n\n"
            "Выберите, что хотите сделать:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            "🎉 Добро пожаловать в Couple Bot!\n\n"
            "Я помогу вам планировать свидания и проводить время вместе со своей второй половинкой.\n\n"
            "Для начала работы нужно зарегистрироваться:",
            reply_markup=registration_keyboard()
        )


@router.message(F.text == "📝 Зарегистрироваться")
async def start_registration(message: Message, state: FSMContext, is_registered: bool, **kwargs):
    """Начать регистрацию"""
    if is_registered:
        await message.answer(
            "✅ Вы уже зарегистрированы!",
            reply_markup=main_menu_keyboard()
        )
        return
    
    await message.answer(
        "👤 Давайте знакомиться!\n\n"
        "Как вас зовут? Введите ваше имя:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(StateFilter(RegistrationStates.waiting_for_name), F.text != "❌ Отмена")
async def process_name(message: Message, state: FSMContext, user_info: dict, **kwargs):
    """Обработать введенное имя"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте еще раз:")
        return
    
    if len(name) > 50:
        await message.answer("❌ Имя слишком длинное. Попробуйте еще раз:")
        return
    
    try:
        # Регистрируем пользователя
        async with api_client:
            user_data = await api_client.register_user(
                telegram_id=user_info["telegram_id"],
                name=name,
                username=user_info["username"]
            )
        
        await message.answer(
            f"✅ Отлично, {name}! Вы успешно зарегистрированы.\n\n"
            "Теперь вам нужно создать пару или присоединиться к существующей:",
            reply_markup=couple_setup_keyboard()
        )
        
        await state.clear()
        
    except APIError as e:
        logger.error(f"Registration error: {e}")
        await message.answer(
            "❌ Произошла ошибка при регистрации. Попробуйте позже.",
            reply_markup=registration_keyboard()
        )
        await state.clear()


@router.message(StateFilter(RegistrationStates.waiting_for_name), F.text == "❌ Отмена")
async def cancel_registration(message: Message, state: FSMContext, **kwargs):
    """Отменить регистрацию"""
    await message.answer(
        "❌ Регистрация отменена.",
        reply_markup=registration_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, is_registered: bool, has_couple: bool, **kwargs):
    """Вернуться в главное меню"""
    await callback.answer()
    
    if not is_registered:
        await callback.message.edit_text(
            "🎉 Добро пожаловать в Couple Bot!\n\n"
            "Я помогу вам планировать свидания и проводить время вместе со своей второй половинкой.\n\n"
            "Для начала работы нужно зарегистрироваться:",
            reply_markup=registration_keyboard()
        )
    elif not has_couple:
        await callback.message.edit_text(
            "👫 Для использования бота вам нужна пара!\n\n"
            "Создайте новую пару или присоединитесь к существующей:",
            reply_markup=couple_setup_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🏠 Главное меню\n\n"
            "Выберите, что хотите сделать:",
            reply_markup=main_menu_keyboard()
        )


@router.message(Command("help"))
async def cmd_help(message: Message, **kwargs):
    """Команда помощи"""
    help_text = """
🤖 **Couple Bot - Помощник для пар**

**Основные команды:**
/start - Начать работу с ботом
/help - Показать это сообщение
/menu - Открыть главное меню

**Как пользоваться:**
1. 📝 Зарегистрируйтесь в боте
2. 👫 Создайте пару или присоединитесь к существующей
3. 💡 Получайте идеи для свиданий
4. 💕 Предлагайте свидания партнеру
5. 📚 Ведите историю ваших свиданий

**Возможности:**
• Ежедневные идеи для свиданий
• Система предложений и ответов
• История всех свиданий
• Статистика вашей пары
• Различные категории активностей

**Поддержка:**
Если у вас возникли проблемы, напишите /support
    """
    
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("menu"))
async def cmd_menu(message: Message, is_registered: bool, has_couple: bool, **kwargs):
    """Показать главное меню"""
    if not is_registered:
        await message.answer(
            "❌ Сначала зарегистрируйтесь в боте командой /start"
        )
        return
    
    if not has_couple:
        await message.answer(
            "❌ Сначала создайте пару или присоединитесь к существующей",
            reply_markup=couple_setup_keyboard()
        )
        return
    
    await message.answer(
        "🏠 Главное меню\n\n"
        "Выберите, что хотите сделать:",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery, **kwargs):
    """Показать помощь через callback"""
    await callback.answer()
    
    help_text = """
🤖 **Couple Bot - Помощник для пар**

**Основные функции:**
• 💡 Получение идей для свиданий по категориям
• 💕 Предложение свиданий партнеру
• 📋 Просмотр активных предложений
• 📚 История всех свиданий пары
• 👫 Управление парой и настройки

**Как предложить свидание:**
1. Нажмите "💕 Предложить свидание"
2. Выберите категорию
3. Выберите понравившуюся идею
4. Подтвердите предложение

**Как ответить на предложение:**
• Заходите в "📋 Мои предложения"
• Выбирайте предложение
• Принимайте или отклоняйте

Удачных свиданий! 💕
    """
    
    await callback.message.edit_text(help_text, parse_mode="Markdown")


@router.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery, **kwargs):
    """Информация о боте"""
    await callback.answer()
    
    about_text = """
🤖 **Couple Bot v1.0**

Телеграм-бот для планирования свиданий и укрепления отношений.

**Создан для:**
• Пар, которые хотят разнообразить свои свидания
• Тех, кто ищет новые идеи для совместного времяпрепровождения
• Планирования и учета романтических моментов

**Технологии:**
• Python + aiogram 3.x
• FastAPI Backend
• PostgreSQL Database

**Версия:** 1.0.0
**Разработчик:** @your_username

💕 Желаем вам незабываемых свиданий!
    """
    
    await callback.message.edit_text(about_text, parse_mode="Markdown")