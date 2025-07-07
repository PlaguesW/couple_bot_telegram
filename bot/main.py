import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from handlers import start, help, couple, ideas, dates

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment")

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Инициализация диспетчера
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация всех роутеров
def register_handlers():
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(couple.router)
    dp.include_router(ideas.router)
    dp.include_router(dates.router)

async def main():
    """Основная функция запуска бота"""
    register_handlers()
    logger.info("Bot is starting...")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("Бот остановлен")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())