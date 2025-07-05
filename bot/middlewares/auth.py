from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from ..api_client import api_client
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентификации пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        
        # Получаем ID пользователя из события
        user_id = event.from_user.id
        user = event.from_user
        
        logger.info(f"Auth middleware for user {user_id}")
        
        try:
            # Проверяем существование пользователя в базе
            user_response = await api_client.get_user(user_id)
            
            if "error" in user_response and user_response.get("status") == 404:
                logger.info(f"User {user_id} not found, creating new user")
                
                # Пользователь не найден, создаем нового
                user_data = {
                    "user_id": user_id,
                    "telegram_id": user_id,
                    "name": user.full_name or "Пользователь",
                    "username": user.username or "",
                    "created_at": None  # Будет установлено на сервере
                }
                
                create_response = await api_client.create_user(user_data)
                
                if "error" in create_response:
                    logger.error(f"Failed to create user {user_id}: {create_response}")
                    # Не блокируем выполнение, если не удалось создать пользователя
                else:
                    logger.info(f"User {user_id} created successfully")
            
            elif "error" not in user_response:
                logger.info(f"User {user_id} found in database")
            else:
                logger.error(f"Error checking user {user_id}: {user_response}")
        
        except Exception as e:
            logger.error(f"Error in auth middleware for user {user_id}: {str(e)}")
            # Не блокируем выполнение при ошибках
        
        # Добавляем информацию о пользователе в данные
        data["user_id"] = user_id
        data["user"] = user
        
        # Продолжаем выполнение обработчика
        return await handler(event, data)