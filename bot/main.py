import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from bot.config import BOT_TOKEN #,LOG_LEVEL
from bot.middlewares.auth import AuthMiddleware
from .api_client import api_client

# Импортируем все обработчики
from bot.handlers import start, registration, pairs, ideas, events
from bot.handlers import dates  # Новый обработчик для свиданий

async def main():
    """Основная функция запуска бота"""
    
    #* Настройка логирования
    # logging.basicConfig(
    #     level=getattr(logging, LOG_LEVEL.upper()),
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.StreamHandler(),
    #         logging.FileHandler('bot.log', encoding='utf-8')
    #     ]
    # )
    
    # logger = logging.getLogger(__name__)
    # print("Starting Couple Bot...")
    
    # Создание сессии для бота
    session = AiohttpSession()
    
    # Создание бота
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            protect_content=False
        )
    )
    
    # Создание диспетчера
    dp = Dispatcher()
    
    # Подключение middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Подключение роутеров в правильном порядке
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(pairs.router)
    dp.include_router(ideas.router)
    dp.include_router(dates.router)  # Добавляем обработчик свиданий
    dp.include_router(events.router)
    
    # Запуск polling
    try:
        print("Bot is starting polling...")
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except Exception as e:
        logger.error(f"Error during polling: {str(e)}")
    finally:
        # Закрытие ресурсов
        print("Closing bot resources...")
        await api_client.close()
        await session.close()
        await bot.session.close()
        print("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")