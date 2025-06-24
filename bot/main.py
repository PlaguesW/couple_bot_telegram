import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import db
from handlers import start, pairs, ideas, dates

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота...")
    
    # Connect to DB
    try:
        await db.connect()
        logger.info("Подключение к базе данных успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return
    
    # Routers
    dp.include_router(start.router)
    dp.include_router(pairs.router)
    dp.include_router(ideas.router)
    dp.include_router(dates.router)
    
    # Setting up commands
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="join", description="💌 Присоединиться к паре"),
        BotCommand(command="help", description="❓ Помощь"),
    ])
    
    try:
        # Delete any existing webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен и работает...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Close connections
        
        await db.disconnect()
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")