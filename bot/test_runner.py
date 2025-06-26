import asyncio
import os
import sys
import subprocess
import json
from pathlib import Path

def run_unit_tests():
    """Запуск unit-тестов с pytest"""
    print("🧪 Запуск unit-тестов...")
    
    # Проверяем наличие pytest
    try:
        import pytest
    except ImportError:
        print("❌ pytest не установлен. Установите: pip install pytest pytest-asyncio")
        return False
    
    test_paths = []
    
    if os.path.exists('tests/'):
        test_paths.append('tests/')
    
    if os.path.exists('bot/test_database.py'):
        test_paths.append('bot/test_database.py')
    
    if not test_paths:
        print("❌ Не найдены файлы тестов")
        return False
    
    # Запускаем тесты
    cmd = [sys.executable, '-m', 'pytest'] + test_paths + ['-v', '--tb=short']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Предупреждения/Ошибки:", result.stderr)
    
    if "collected 0 items" in result.stdout:
        print("⚠️ Тесты не найдены или не собраны")
        return False
    
    return result.returncode == 0

def check_code_quality():
    """Проверка качества кода с помощью flake8"""
    print("📏 Проверка качества кода...")
    
    try:
        result = subprocess.run(['flake8', '.', '--exclude=venv,__pycache__,.git'],
                                capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Код соответствует стандартам")
            return True
        else:
            print("❌ Найдены проблемы в коде:")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("⚠️ flake8 не установлен. Установите: pip install flake8")
        return True

def test_imports():
    """Тестирование импортов всех модулей"""
    print("📦 Проверка импортов...")
    
    modules_to_test = [
        'config',
        'database',
        'main',
    ]
    
    optional_modules = [
        'handlers.start',
        'handlers.pairs',
        'handlers.ideas',
        'handlers.dates',
        'keyboards.inline'
    ]
    
    failed_imports = []
    optional_failed = []
    
    # Проверяем основные модули
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"⚠️ {module}: {e}")
            optional_failed.append(module)
    
    if failed_imports:
        print(f"\n❌ Не удалось импортировать {len(failed_imports)} основных модулей")
        return False
    else:
        if optional_failed:
            print(f"\n⚠️ Не удалось импортировать {len(optional_failed)} дополнительных модулей")
        print("\n✅ Все основные модули успешно импортированы")
        return True

async def test_database_connection():
    """Тестирование подключения к базе данных"""
    print("🗄️ Проверка подключения к базе данных...")
    
    try:
        if 'bot' not in sys.path:
            sys.path.insert(0, 'bot')
        
        from database import Database
        
        db = Database()
        await db.init_db()
        
        # Тестируем основные операции
        test_user_id = 999999999
        
        # Создание тестового пользователя
        success = await db.create_user(
            telegram_id=test_user_id,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        if not success:
            user = await db.get_user(test_user_id)
            if not user:
                print("❌ Не удалось создать или получить тестового пользователя")
                return False
        
        # Получение пользователя
        user = await db.get_user(test_user_id)
        if user:
            print("✅ Создание и получение пользователя работает")
        else:
            print("❌ Проблема с созданием/получением пользователя")
            return False
        
        # Удаление тестового пользователя
        await db.delete_user(test_user_id)
        
        await db.disconnect()
        
        print("✅ База данных работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return False

def generate_postman_collection():
    """Генерация коллекции для Postman"""
    print("📬 Генерация Postman коллекции...")
    
    collection_path = Path("tests/Couple_Bot_API.postman_collection.json")
    collection_path.parent.mkdir(exist_ok=True)
    
    # Простая коллекция для примера
    collection = {
        "info": {
            "name": "Couple Bot API",
            "description": "API тесты для Couple Bot",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/health",
                        "host": ["{{base_url}}"],
                        "path": ["health"]
                    }
                }
            }
        ],
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            }
        ]
    }
    
    with open(collection_path, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Коллекция сохранена в {collection_path}")
    return True

async def run_integration_tests():
    """Запуск интеграционных тестов"""
    print("🔗 Запуск интеграционных тестов...")
    
    # Проверка переменных окружения
    required_env_vars = ['BOT_TOKEN']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("Создайте файл .env на основе .env.example")
        return False
    
    # Тестирование базы данных
    db_test = await test_database_connection()
    
    return db_test

def check_project_structure():
    """Проверка структуры проекта"""
    print("📁 Проверка структуры проекта...")
    
    required_files = [
        'bot/main.py',
        'bot/config.py',
        'bot/database.py'
    ]
    
    optional_files = [
        'bot/handlers/__init__.py',
        'bot/keyboards/__init__.py',
        'requirements.txt',
        '.env.example'
    ]
    
    missing_required = []
    missing_optional = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_required.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    for file_path in optional_files:
        if not os.path.exists(file_path):
            missing_optional.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_required:
        print(f"❌ Отсутствуют обязательные файлы: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️ Отсутствуют рекомендуемые файлы: {', '.join(missing_optional)}")
    
    print("✅ Структура проекта в порядке")
    return True

def main():
    """Главная функция запуска всех тестов"""
    print("🚀 Запуск тестирования Couple Bot\n")
    
    results = {}
    
    # Проверка структуры проекта
    results['structure'] = check_project_structure()
    print()
    
    # Проверка импортов
    results['imports'] = test_imports()
    print()
    
    # Интеграционные тесты
    results['integration'] = asyncio.run(run_integration_tests())
    print()
    
    # Unit тесты
    results['unit_tests'] = run_unit_tests()
    print()
    
    # Качество кода
    # results['code_quality'] = check_code_quality()
    # print()
    
    # Генерация Postman коллекции
    results['postman'] = generate_postman_collection()
    print()
    
    # Итоговый отчет
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name.upper()}: {status}")
    
    print("=" * 50)
    print(f"ИТОГО: {passed_tests}/{total_tests} тестов прошли успешно")
    
    if passed_tests == total_tests:
        print("🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("⚠️ Некоторые тесты провалились. Проверьте вывод выше.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)