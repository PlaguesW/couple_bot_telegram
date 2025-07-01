from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from loguru import logger

from bot.states import EventStates
from bot.services.api_client import api_client
from bot.models.schemas import EventCreate
from bot.keyboards.inline import get_main_menu, get_cancel_keyboard, get_event_response_keyboard
from bot.utils.decorators import require_registration

router = Router()


@router.callback_query(F.data == "propose_date")
@require_registration
async def start_propose_date(callback: types.CallbackQuery, state: FSMContext, user):
    """Start proposing a date for an event"""
    
    # Check if user has a pair
    user_pair = await api_client.get_user_pair(user.id)
    if not user_pair:
        await callback.message.edit_text(
            "❌ <b>Нет пары</b>\n\n"
            "Сначала создай пару с партнером, чтобы предлагать свидания!",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="👫 Создать пару", callback_data="create_pair")],
                [types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
            ])
        )
        await callback.answer()
        return
    
    partner = user_pair.user2 if user_pair.user1.id == user.id else user_pair.user1
    await state.update_data(pair=user_pair, partner=partner)
    await state.set_state(EventStates.waiting_for_event_title)
    
    await callback.message.edit_text(
        f"💕 <b>Предложение свидания</b>\n\n"
        f"👤 <b>Партнер:</b> {partner.name}\n\n"
        f"Как назовешь свидание? Придумай интересное название!\n"
        f"Например: <i>Романтический ужин</i> или <i>Прогулка в парке</i>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(EventStates.waiting_for_event_title)
async def process_event_title(message: types.Message, state: FSMContext):
    """processing the title of the event"""
    title = message.text.strip()
    
    if len(title) < 3 or len(title) > 100:
        await message.answer(
            "❌ Название должно быть от 3 до 100 символов.\n"
            "Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(title=title)
    await state.set_state(EventStates.waiting_for_event_description)
    
    await message.answer(
        f"✅ Отличное название: <b>{title}</b>\n\n"
        f"Теперь опиши свидание подробнее. Что планируешь?\n"
        f"Или напиши <code>пропустить</code>, если хочешь добавить описание позже.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(EventStates.waiting_for_event_description)
async def process_event_description(message: types.Message, state: FSMContext):
    """Processing the description of the event"""
    description = message.text.strip()
    
    if description.lower() in ["пропустить", "skip", "-"]:
        description = None
    elif len(description) > 500:
        await message.answer(
            "❌ Описание слишком длинное (максимум 500 символов).\n"
            "Сократи его или напиши <code>пропустить</code>:",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(description=description)
    await state.set_state(EventStates.waiting_for_event_date)
    
    await message.answer(
        "📅 <b>Когда планируешь свидание?</b>\n\n"
        "Напиши дату и время в формате:\n"
        "• <code>завтра 19:00</code>\n"
        "• <code>15.03.2024 18:30</code>\n"
        "• <code>в субботу вечером</code>\n\n"
        "Или напиши <code>пропустить</code>, чтобы обсудить время позже.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(EventStates.waiting_for_event_date)
async def process_event_date(message: types.Message, state: FSMContext):
    """Processing the proposed date for the event"""
    date_text = message.text.strip()
    proposed_date = None
    
    if date_text.lower() not in ["пропустить", "skip", "-"]:
        # parse the date and time from the message
        try:
            if "завтра" in date_text.lower():
                tomorrow = datetime.now() + timedelta(days=1)
                if "19:00" in date_text:
                    proposed_date = tomorrow.replace(hour=19, minute=0, second=0, microsecond=0)
                elif "18:30" in date_text:
                    proposed_date = tomorrow.replace(hour=18, minute=30, second=0, microsecond=0)
                else:
                    proposed_date = tomorrow.replace(hour=19, minute=0, second=0, microsecond=0)
            
            elif "." in date_text and ":" in date_text:
                # Try to parse date in format "15.03.2024 18:30"
                parts = date_text.split()
                if len(parts) >= 2:
                    date_part, time_part = parts[0], parts[1]
                    day, month, year = map(int, date_part.split('.'))
                    hour, minute = map(int, time_part.split(':'))
                    proposed_date = datetime(year, month, day, hour, minute)
        except:
            # If parsing fails, we ignore the error and keep proposed_date as None
            pass
    
    # Get all data from state
    data = await state.get_data()
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    event_data = EventCreate(
        pair_id=data["pair"].id,
        title=data["title"],
        description=data.get("description"),
        proposed_date=proposed_date,
        initiator_id=user.id
    )
    
    # create the event using the API client
    event = await api_client.create_event(event_data)
    
    if event:
        await state.clear()
        
        partner = data["partner"]
        date_str = proposed_date.strftime("%d.%m.%Y в %H:%M") if proposed_date else "время не указано"
        
        # Send confirmation message to the user
        await message.answer(
            f"✅ <b>Свидание предложено!</b>\n\n"
            f"💕 <b>Название:</b> {event.title}\n"
            f"📝 <b>Описание:</b> {event.description or 'не указано'}\n"
            f"📅 <b>Дата:</b> {date_str}\n"
            f"👤 <b>Партнер:</b> {partner.name}\n\n"
            f"Партнер получит приглашение! 📨",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
        # Send invitation to partner
        try:
            from bot.main import bot
            
            invitation_text = (
                f"💕 <b>Приглашение на свидание!</b>\n\n"
                f"👤 <b>От:</b> {user.name}\n"
                f"💕 <b>Свидание:</b> {event.title}\n"
            )
            
            if event.description:
                invitation_text += f"📝 <b>Описание:</b> {event.description}\n"
            
            invitation_text += f"📅 <b>Дата:</b> {date_str}\n\n"
            invitation_text += "Что скажешь? 😊"
            invitation_text += "Выбери действие ниже:"
            await bot.send_message(
                partner.telegram_id,
                invitation_text,
                parse_mode="HTML",
                reply_markup=get_event_response_keyboard(event.id)
            )
            logger.info(f"Event {event.id} proposed by {user.name} to {partner.name}")
        except Exception as e:
            logger.error(f"Failed to send event proposal: {e}")
            await message.answer(
                "❌ Не удалось отправить приглашение партнеру. Попробуй еще раз позже.",
                reply_markup=get_main_menu()
            )
        await callback.answer("Свидание предложено! 💕"
                              )