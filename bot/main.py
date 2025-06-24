import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import Database

# Импорт обработчиков
from handlers import start, pairs, ideas, dates

async def main():
    """Главная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализация диспетчера с хранилищем состояний
    dp = Dispatcher(storage=MemoryStorage())
    
    # Инициализация базы данных
    try:
        db = Database()
        await db.init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(pairs.router)
    dp.include_router(ideas.router)
    dp.include_router(dates.router)
    
    # Удаление webhook и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("Bot started successfully")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")