from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from api_client import api_client

class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication in the bot"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Check if the event is a message or callback query
        user_response = await api_client.get_user(event.from_user.id)
        if "error" in user_response:
            # If there is an error in the response, send an error message
            return
        # Add user information to the data dictionary
        data['user'] = user_response
        # Continue processing the event with the handler
        return await handler(event, data)
    async def on_pre_process_message(
        self, message: Message, data: Dict[str, Any]
    ) -> None:
        """Check authorization for messages"""
        await self.__call__(self.on_pre_process_message_handler, message, data)
    async def on_pre_process_callback_query(
        self, callback_query: CallbackQuery, data: Dict[str, Any]
    ) -> None:
        """Check authorization for callback queries"""
        await self.__call__(self.on_pre_process_callback_query_handler, callback_query, data)
    async def on_pre_process_message_handler(
        self, message: Message, data: Dict[str, Any]
    ) -> None:
        """Message handler for processing messages"""
        # Here needs to be added logic for processing messages
    async def on_pre_process_callback_query_handler(
        self, callback_query: CallbackQuery, data: Dict[str, Any]
    ) -> None:
        """Callback query handler for processing callback queries"""
        # Here needs to be added logic for processing callback queries
        pass
# Регистрация middleware в приложении
def setup_middleware(dp):
    """Function to set up middleware in the bot"""
    dp.update.middleware(AuthMiddleware())
    return dp