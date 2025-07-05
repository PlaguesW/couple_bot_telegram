import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Основные настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

#* Настройки базы данных (если нужны для кеширования)
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# *Настройки логирования
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

#* Настройки Redis (если используется)
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Валидация обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Проверка URL API
if not API_URL.startswith(('http://', 'https://')):
    API_URL = f"http://{API_URL}"

print(f"Bot configuration loaded:")
print(f"API_URL: {API_URL}")
# print(f"LOG_LEVEL: {LOG_LEVEL}")