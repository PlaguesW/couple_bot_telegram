from aiogram import Router, F
from aiogram.types import Message

from api_client import api_client

router = Router()

@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    """Показ профиля пользователя"""
    # Получаем информацию о пользователе
    user_response = await api_client.get_user(message.from_user.id)
    
    if "error" in user_response:
        await message.answer(f"❌ {user_response['error']}")
        return
    
    # Получаем информацию о паре
    pair_response = await api_client.get_user_pair(message.from_user.id)
    
    profile_text = f"👤 <b>Ваш профиль</b>\n\n"
    profile_text += f"🆔 ID: {user_response['telegram_id']}\n"
    profile_text += f"👨‍💼 Имя: {user_response['first_name']}\n"
    
    if user_response.get('username'):
        profile_text += f"📱 Username: @{user_response['username']}\n"
    
    if "error" not in pair_response and pair_response:
        profile_text += f"\n💑 <b>Ваша пара</b>\n"
        profile_text += f"🆔 Код пары: <code>{pair_response['code']}</code>\n"
        profile_text += f"📅 Создана: {pair_response['created_at'][:10]}\n"
        
        # Получаем партнера
        partner = None
        for member in pair_response.get('members', []):
            if member['telegram_id'] != message.from_user.id:
                partner = member
                break
        
        if partner:
            profile_text += f"💕 Партнер: {partner['first_name']}\n"
    else:
        profile_text += f"\n💔 Вы пока не состоите в паре\n"
        profile_text += f"Создайте новую пару или присоединитесь к существующей!"
    
    await message.answer(profile_text)

@router.message(F.text == "📚 История")
async def show_history(message: Message):
    """Показ истории свиданий"""
    # Сначала получаем пару пользователя
    pair_response = await api_client.get_user_pair(message.from_user.id)
    
    if "error" in pair_response:
        await message.answer("❌ Вы не состоите в паре")
        return
    
    # Получаем историю пары
    history_response = await api_client.get_pair_history(pair_response['id'])
    
    if "error" in history_response:
        await message.answer(f"❌ {history_response['error']}")
        return
    
    if not history_response:
        await message.answer("📭 У вас пока нет истории свиданий")
        return
    
    history_text = "📚 <b>История ваших свиданий</b>\n\n"
    
    accepted_count = 0
    declined_count = 0
    
    for i, proposal in enumerate(history_response[-10:], 1):  # Последние 10
        idea = proposal['idea']
        proposer = proposal['proposer']
        status = "✅" if proposal['accepted'] else "❌"
        
        if proposal['accepted']:
            accepted_count += 1
        else:
            declined_count += 1
        
        history_text += (
            f"{i}. {status} <b>{idea['title']}</b>\n"
            f"   Предложил: {proposer['first_name']}\n"
            f"   Дата: {proposal['created_at'][:10]}\n\n"
        )
    
    stats_text = (
        f"📊 <b>Статистика</b>\n"
        f"✅ Принято: {accepted_count}\n"
        f"❌ Отклонено: {declined_count}\n"
        f"🎯 Всего предложений: {len(history_response)}"
    )
    
    await message.answer(history_text + stats_text)