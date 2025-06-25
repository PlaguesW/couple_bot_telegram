from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline import main_menu, back_to_menu_button, proposal_response_keyboard

router = Router()

@router.callback_query(F.data == "propose_date")
async def propose_date_menu(callback: CallbackQuery, state: FSMContext):
    """Меню предложения свидания"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем наличие пары
    pair = await db.get_user_pair(user['id'])
    if not pair or not pair['user2_id']:
        await callback.answer("Для предложения свиданий нужно создать пару!", show_alert=True)
        return
    
    from keyboards.inline import category_menu
    
    await callback.message.edit_text(
        "💌 Выберите идею для предложения партнеру:\n\n"
        "Выберите категорию или получите случайную идею!",
        reply_markup=category_menu()
    )
    
    await callback.answer()

@router.callback_query(F.data == "my_proposals")
async def my_proposals_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик просмотра предложений"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем наличие пары
    pair = await db.get_user_pair(user['id'])
    if not pair or not pair['user2_id']:
        await callback.answer("Для просмотра предложений нужно создать пару!", show_alert=True)
        return
    
    try:
        # Получаем ожидающие предложения
        pending_proposals = await db.get_pending_proposals(pair['id'])
        
        if not pending_proposals:
            await callback.message.edit_text(
                "📋 У вас нет новых предложений свиданий.\n\n"
                "Когда партнер предложит вам свидание, оно появится здесь!",
                reply_markup=back_to_menu_button()
            )
            await callback.answer()
            return
        
        # Показываем первое предложение
        proposal = pending_proposals[0]
        
        await callback.message.edit_text(
            f"💌 Предложение от {proposal['proposer_name']}:\n\n"
            f"💡 **{proposal['title']}**\n"
            f"📝 {proposal['description']}\n\n"
            f"📅 Предложено: {proposal['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Осталось предложений: {len(pending_proposals)}",
            parse_mode="Markdown",
            reply_markup=proposal_response_keyboard(proposal['id'])
        )
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении предложений: {e}", show_alert=True)

@router.callback_query(F.data.startswith("accept_"))
async def accept_proposal_handler(callback: CallbackQuery):
    """Обработчик принятия предложения"""
    proposal_id = int(callback.data.replace("accept_", ""))
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    try:
        # Принимаем предложение
        success = await db.respond_to_proposal(proposal_id, 'accepted')
        
        if success:
            await callback.message.edit_text(
                "✅ Предложение принято!\n\n"
                "Ваш партнер получит уведомление о том, что вы согласились на свидание. 💕\n\n"
                "Приятно провести время вместе!",
                reply_markup=back_to_menu_button()
            )
            
            # Уведомляем партнера
            try:
                # Получаем информацию о предложении и партнере
                pair = await db.get_user_pair(user['id'])
                partner_id = await db.get_partner_id(user['id'])
                partner = await db.get_user_by_id(partner_id)
                
                from aiogram import Bot
                from config import BOT_TOKEN
                
                bot = Bot(token=BOT_TOKEN)
                
                await bot.send_message(
                    partner['telegram_id'],
                    f"🎉 {user['name']} принял ваше предложение свидания!\n\n"
                    "Время планировать встречу! 💕",
                    reply_markup=main_menu()
                )
                await bot.session.close()
            except Exception:
                pass  # Не критичная ошибка
            
            await callback.answer("Предложение принято! 🎉")
        else:
            await callback.answer("Ошибка: предложение уже недоступно", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"Ошибка при принятии предложения: {e}", show_alert=True)

@router.callback_query(F.data.startswith("decline_"))
async def decline_proposal_handler(callback: CallbackQuery):
    """Обработчик отклонения предложения"""
    proposal_id = int(callback.data.replace("decline_", ""))
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    try:
        # Отклоняем предложение
        success = await db.respond_to_proposal(proposal_id, 'declined')
        
        if success:
            await callback.message.edit_text(
                "❌ Предложение отклонено.\n\n"
                "Ваш партнер получит уведомление. Не расстраивайтесь - впереди еще много возможностей! 😊",
                reply_markup=back_to_menu_button()
            )
            
            # Уведомляем партнера
            try:
                partner_id = await db.get_partner_id(user['id'])
                partner = await db.get_user_by_id(partner_id)
                
                from aiogram import Bot
                from config import BOT_TOKEN
                
                bot = Bot(token=BOT_TOKEN)
                
                await bot.send_message(
                    partner['telegram_id'],
                    f"😔 {user['name']} не готов к этому свиданию сейчас.\n\n"
                    "Не расстраивайтесь! Попробуйте предложить что-то другое! 😊",
                    reply_markup=main_menu()
                )
                await bot.session.close()
            except Exception:
                pass  # Не критичная ошибка
            
            await callback.answer("Предложение отклонено")
        else:
            await callback.answer("Ошибка: предложение уже недоступно", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"Ошибка при отклонении предложения: {e}", show_alert=True)

@router.callback_query(F.data == "date_history")
async def date_history_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик истории свиданий"""
    await state.clear()
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем наличие пары
    pair = await db.get_user_pair(user['id'])
    if not pair or not pair['user2_id']:
        await callback.answer("Для просмотра истории нужно создать пару!", show_alert=True)
        return
    
    try:
        # Получаем историю свиданий
        history = await db.get_date_history(pair['id'], limit=10)
        
        if not history:
            await callback.message.edit_text(
                "📚 История свиданий пуста.\n\n"
                "Когда вы начнете принимать или отклонять предложения, они появятся здесь!",
                reply_markup=back_to_menu_button()
            )
            await callback.answer()
            return
        
        # Формируем текст истории
        history_text = "📚 **История ваших свиданий:**\n\n"
        
        for item in history:
            status_emoji = "✅" if item['status'] == 'accepted' else "❌"
            date_str = item['created_at'].strftime('%d.%m.%Y')
            
            history_text += (
                f"{status_emoji} **{item['title']}**\n"
                f"👤 Предложил: {item['proposer_name']}\n"
                f"📅 {date_str}\n\n"
            )
        
        if len(history_text) > 4000:  # Telegram ограничение
            history_text = history_text[:3900] + "...\n\n(Показаны последние записи)"
        
        await callback.message.edit_text(
            history_text,
            parse_mode="Markdown",
            reply_markup=back_to_menu_button()
        )
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка при получении истории: {e}", show_alert=True)