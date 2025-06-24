import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Добавляем путь к корневой папке проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loading():
    """Тест загрузки конфигурации"""
    import config
    # Проверяем, что конфигурация загружается
    assert hasattr(config, 'BOT_TOKEN')
    assert hasattr(config, 'DATABASE_URL')
    assert hasattr(config, 'DEBUG')
    assert hasattr(config, 'ADMIN_IDS')

def test_config_values():
    """Тест значений конфигурации"""
    import config
    # Проверяем, что BOT_TOKEN установлен
    assert config.BOT_TOKEN is not None
    assert len(config.BOT_TOKEN) > 0
    
    # Проверяем DATABASE_URL
    assert config.DATABASE_URL is not None
    
    # Проверяем, что ADMIN_IDS это список
    assert isinstance(config.ADMIN_IDS, list)

@pytest.mark.asyncio
async def test_database_creation():
    """Тест создания объекта базы данных"""
    from database import Database
    
    # Создаем объект базы данных
    db = Database()
    
    # Проверяем, что объект создался
    assert db is not None
    assert hasattr(db, 'init_db')
    assert hasattr(db, 'create_tables')
    assert hasattr(db, 'connect')

def test_keyboard_functions():
    """Тест функций клавиатур"""
    from keyboards.inline import (
        main_menu, 
        pair_setup_menu, 
        get_pair_keyboard, 
        get_join_keyboard,
        back_to_menu_button
    )
    
    # Тестируем основные функции клавиатур
    assert main_menu() is not None
    assert pair_setup_menu() is not None
    assert get_pair_keyboard() is not None
    assert get_join_keyboard() is not None
    assert back_to_menu_button() is not None

def test_handlers_import():
    """Тест импорта обработчиков"""
    try:
        from handlers import start, pairs, ideas, dates
        assert True  # Если импорт прошел успешно
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать обработчики: {e}")

def test_category_emoji():
    """Тест функции получения эмодзи категорий"""
    from keyboards.inline import get_category_emoji
    
    # Тестируем известные категории
    assert get_category_emoji('романтика') == '💕'
    assert get_category_emoji('дом') == '🏠'
    assert get_category_emoji('активность') == '🏃'
    
    # Тестируем неизвестную категорию
    assert get_category_emoji('неизвестная') == '⭐'