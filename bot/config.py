import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")

# Настройки базы данных
DATABASE_URL = os.getenv('DATABASE_URL', 'database.db')

# Настройки для разработки
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ID администраторов (через запятую)
ADMIN_IDS = []
admin_ids_str = os.getenv('ADMIN_IDS', '')
if admin_ids_str:
    try:
        ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    except ValueError:
        print("Предупреждение: Некорректные ID администраторов в ADMIN_IDS")

# Настройки уведомлений
NOTIFICATIONS_ENABLED = os.getenv('NOTIFICATIONS_ENABLED', 'True').lower() == 'true'

# Интервал отправки идей свиданий (в часах)
IDEAS_INTERVAL_HOURS = int(os.getenv('IDEAS_INTERVAL_HOURS', '24'))

print(f"Конфигурация загружена:")
print(f"- BOT_TOKEN: {'✅ Установлен' if BOT_TOKEN else '❌ Не установлен'}")
print(f"- DATABASE_URL: {DATABASE_URL}")
print(f"- DEBUG: {DEBUG}")
print(f"- ADMIN_IDS: {ADMIN_IDS}")
print(f"- NOTIFICATIONS_ENABLED: {NOTIFICATIONS_ENABLED}")