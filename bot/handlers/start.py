from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from api_client import api_client
from keyboards.main_menu import get_main_menu
from keyboards.inline import get_join_pair_keyboard

router = Router()

class PairJoining(StatesGroup):
    waiting_for_code = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    # Проверяем, есть ли пользователь в системе
    user_response = await api_client.get_user(message.from_user.id)
    
    if "error" in user_response:
        # Создаем нового пользователя
        create_response = await api_client.create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or ""
        )
        
        if "error" in create_response:
            await message.answer("❌ Произошла ошибка при регистрации. Попробуйте позже.")
            return
    
    # Проверяем, есть ли у пользователя пара
    pair_response = await api_client.get_user_pair(message.from_user.id)
    
    if "error" not in pair_response and pair_response:
        await message.answer(
            f"👋 С возвращением! Вы уже в паре.\n\n"
            f"🆔 Код пары: <code>{pair_response['code']}</code>",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в Couple Bot!\n\n"
            "🔹 Создайте пару или присоединитесь к существующей",
            reply_markup=get_join_pair_keyboard()
        )

@router.callback_query(F.data == "create_pair")
async def create_pair_handler(callback: CallbackQuery):
    """Создание новой пары"""
    response = await api_client.create_pair(callback.from_user.id)
    
    if "error" in response:
        await callback.message.edit_text(
            f"❌ Ошибка создания пары: {response['error']}"
        )
        return
    
    await callback.message.edit_text(
        f"✅ Пара создана!\n\n"
        f"🆔 Код для партнера: <code>{response['code']}</code>\n\n"
        f"Отправьте этот код своему партнеру, чтобы он мог присоединиться к паре.",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "join_pair")
async def join_pair_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса присоединения к паре"""
    await state.set_state(PairJoining.waiting_for_code)
    await callback.message.edit_text(
        "🔤 Введите код пары, который получили от партнера:"
    )

@router.message(PairJoining.waiting_for_code)
async def join_pair_by_code(message: Message, state: FSMContext):
    """Присоединение к паре по коду"""
    code = message.text.strip().upper()
    
    response = await api_client.join_pair(code, message.from_user.id)
    
    if "error" in response:
        await message.answer(
            f"❌ {response['error']}\n\n"
            f"Попробуйте еще раз или нажмите /start для возврата в главное меню."
        )
        return
    
    await state.clear()
    await message.answer(
        "✅ Успешно присоединились к паре!\n\n"
        "Теперь вы можете предлагать свидания друг другу! 💕",
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
async def help_handler(message: Message):
    """Справка по боту"""
    help_text = """
🤖 <b>Couple Bot - Помощник для пар</b>

<b>Основные команды:</b>
/start - Запуск бота
/help - Эта справка

<b>Как использовать:</b>
1️⃣ Один партнер создает пару и получает код
2️⃣ Второй партнер присоединяется по коду
3️⃣ Получайте идеи и предлагайте свидания!

<b>Возможности:</b>
💡 Случайные идеи для свиданий
📝 Предложения свиданий партнеру
✅ Принятие/отклонение предложений
📚 История ваших свиданий
    """
    await message.answer(help_text)