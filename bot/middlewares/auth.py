from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger

from ..api_client import api_client, APIError


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем telegram_id пользователя
        if isinstance(event, Message):
            telegram_id = event.from_user.id
            username = event.from_user.username
            full_name = event.from_user.full_name
        elif isinstance(event, CallbackQuery):
            telegram_id = event.from_user.id
            username = event.from_user.username
            full_name = event.from_user.full_name
        else:
            return await handler(event, data)
        
        # Проверяем, есть ли пользователь в базе
        try:
            async with api_client:
                user_data = await api_client.get_user_by_telegram_id(telegram_id)
                data["user"] = user_data
                data["is_registered"] = True
                logger.info(f"User {telegram_id} authenticated successfully")
        except APIError as e:
            # Пользователь не найден или другая ошибка
            if "404" in str(e) or "not found" in str(e).lower():
                # Пользователь не зарегистрирован
                data["user"] = None
                data["is_registered"] = False
                data["user_info"] = {
                    "telegram_id": telegram_id,
                    "username": username,
                    "full_name": full_name
                }
                logger.info(f"User {telegram_id} not registered yet")
            else:
                # Другая ошибка API
                logger.error(f"API error for user {telegram_id}: {e}")
                data["user"] = None
                data["is_registered"] = False
                data["api_error"] = str(e)
        
        # Проверяем, есть ли у пользователя пара (если он зарегистрирован)
        if data.get("is_registered") and data.get("user"):
            try:
                async with api_client:
                    user_id = data["user"]["id"]
                    couple_data = await api_client.get_user_couple(user_id)
                    data["couple"] = couple_data
                    data["has_couple"] = True
                    logger.info(f"User {telegram_id} has couple {couple_data.get('id')}")
            except APIError as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    # У пользователя нет пары
                    data["couple"] = None
                    data["has_couple"] = False
                    logger.info(f"User {telegram_id} has no couple")
                else:
                    logger.error(f"Error getting couple for user {telegram_id}: {e}")
                    data["couple"] = None
                    data["has_couple"] = False
        else:
            data["couple"] = None
            data["has_couple"] = False
        
        return await handler(event, data)