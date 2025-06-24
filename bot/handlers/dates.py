from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from keyboards.inline import back_to_menu_button, main_menu

router = Router()

@router.callback_query(F.data.startswith("accept_"))
async def accept_proposal_handler(callback: CallbackQuery):
    """Accepting a date proposal"""
    proposal_id = int(callback.data.split("_")[1])
    
    success = await db.respond_to_proposal(proposal_id, 'accepted')
    
    if not success:
        await callback.answer("Предложение уже недоступно!", show_alert=True)
        return
    
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    partner_id = await db.get_partner_id(user['id'])
    partner = await db.get_user_by_id(partner_id)
    
    await callback.message.edit_text(
        f"✅ Предложение принято!\n\n"
        f"Отличный выбор! Желаем вам прекрасно провести время вместе! 💕\n\n"
        f"Не забудьте отметить свидание как завершенное после того, как сходите!",
        reply_markup=back_to_menu_button()
    )
    
    # Уведомляем инициатора
    try:
        from main import bot
        await bot.send_message(
            partner['telegram_id'],
            f"🎉 {user['name']} принял ваше предложение свидания!\n\n"
            f"Время планировать детали! 💕",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
    
    await callback.answer("Предложение принято! 🎉")

@router.callback_query(F.data.startswith("reject_"))
async def reject_proposal_handler(callback: CallbackQuery):
    """Rejecting a date proposal"""
    proposal_id = int(callback.data.split("_")[1])
    
    success = await db.respond_to_proposal(proposal_id, 'rejected')
    
    if not success:
        await callback.answer("Предложение уже недоступно!", show_alert=True)
        return
    
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    partner_id = await db.get_partner_id(user['id'])
    partner = await db.get_user_by_id(partner_id)
    
    await callback.message.edit_text(
        f"❌ Предложение отклонено\n\n"
        f"Ничего страшного! Может быть, в следующий раз найдется что-то более подходящее 😊",
        reply_markup=back_to_menu_button()
    )
    
    # Уведомляем инициатора
    try:
        from main import bot
        await bot.send_message(
            partner['telegram_id'],
            f"😔 {user['name']} отклонил ваше предложение свидания.\n\n"
            f"Не расстраивайтесь! Попробуйте предложить что-то другое 💪",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
    
    await callback.answer("Предложение отклонено")

@router.callback_query(F.data == "my_proposals")
async def my_proposals_handler(callback: CallbackQuery):
    """List of user's proposals"""
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("У вас нет активной пары!", show_alert=True)
        return
    
    proposals = await db.get_pending_proposals(pair['id'])
    
    if not proposals:
        await callback.message.edit_text(
            "📝 Ожидающие предложения\n\n"
            "У вас нет ожидающих предложений свиданий.\n\n"
            "Предложите что-то партнеру или подождите предложений от него! 😊",
            reply_markup=back_to_menu_button()
        )
        await callback.answer()
        return
    
    # Group proposals by proposer
    my_proposals = [p for p in proposals if p['proposer_id'] == user['id']]
    partner_proposals = [p for p in proposals if p['proposer_id'] != user['id']]
    
    text = "📝 Ожидающие предложения\n\n"
    
    if partner_proposals:
        text += "💌 Предложения от партнера:\n"
        for proposal in partner_proposals[:3]:  # 3
            text += f"• {proposal['title']}\n"
        if len(partner_proposals) > 3:
            text += f"... и еще {len(partner_proposals) - 3}\n"
        text += "\n"
    
    if my_proposals:
        text += "📤 Ваши предложения:\n"
        for proposal in my_proposals[:3]:  # 3
            text += f"• {proposal['title']} (ожидает ответа)\n"
        if len(my_proposals) > 3:
            text += f"... и еще {len(my_proposals) - 3}\n"
        text += "\n"
    
    text += f"Всего ожидающих предложений: {len(proposals)}"
    
    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_button()
    )
    
    await callback.answer()

@router.callback_query(F.data == "date_history")
async def date_history_handler(callback: CallbackQuery):
    """History of dates for the pair"""
    user = await db.get_user(callback.from_user.id)
    pair = await db.get_user_pair(user['id'])
    
    if not pair or not pair['user2_id']:
        await callback.answer("У вас нет активной пары!", show_alert=True)
        return
    
    history = await db.get_date_history(pair['id'], limit=10)
    
    if not history:
        await callback.message.edit_text(
            "📚 История свиданий\n\n"
            "У вас пока нет истории свиданий.\n\n"
            "Начните предлагать идеи друг другу! 💕",
            reply_markup=back_to_menu_button()
        )
        await callback.answer()
        return
    
    # Статистика
    accepted_count = len([h for h in history if h['status'] == 'accepted'])
    rejected_count = len([h for h in history if h['status'] == 'rejected'])
    
    text = f"📚 История свиданий\n\n"
    text += f"✅ Принято: {accepted_count}\n"
    text += f"❌ Отклонено: {rejected_count}\n\n"
    
    text += "Последние свидания:\n"
    
    for i, date in enumerate(history[:5], 1):
        status_emoji = "✅" if date['status'] == 'accepted' else "❌"
        date_str = date['created_at'].strftime("%d.%m")
        text += f"{i}. {status_emoji} {date['title']} ({date_str})\n"
    
    if len(history) > 5:
        text += f"... и еще {len(history) - 5} свиданий"
    
    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_button()
    )
    
    await callback.answer()