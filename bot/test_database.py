import pytest
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bot'))

from database import Database
import asyncpg

@pytest.fixture
async def db():
    """Фикстура для создания тестовой базы данных"""
    test_db_url = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    
    database = Database()
    database.pool = None
    
    yield database

@pytest.mark.asyncio
async def test_generate_invite_code():
    """Тест генерации кода приглашения"""
    db = Database()
    
    code = db.generate_invite_code()
    
    assert len(code) == 6
    assert code.isalnum()
    assert code.isupper()

@pytest.mark.asyncio
async def test_category_mapping():
    """Тест маппинга категорий"""
    try:
        from handlers.ideas import CATEGORY_MAPPING
        
        assert 'home' in CATEGORY_MAPPING
        assert 'romantic' in CATEGORY_MAPPING
        assert CATEGORY_MAPPING['home'] == 'дом'
        assert CATEGORY_MAPPING['romantic'] == 'романтика'
    except ImportError:
        pytest.skip("handlers.ideas module not available")

def test_config_loading():
    """Тест загрузки конфигурации"""
    from config import BOT_TOKEN, DATABASE_URL
    
    assert BOT_TOKEN is not None
    assert DATABASE_URL is not None

@pytest.mark.asyncio
async def test_database_methods_exist():
    """Проверка наличия необходимых методов в Database"""
    db = Database()
    
    required_methods = [
        'add_user', 'create_user', 'delete_user', 'get_user', 
        'get_user_by_id', 'create_pair', 'join_pair', 
        'get_user_pair', 'get_random_idea', 'get_ideas_by_category'
    ]
    
    for method in required_methods:
        assert hasattr(db, method), f"Метод {method} отсутствует в Database"
        assert callable(getattr(db, method)), f"Метод {method} не является функцией"

def test_invite_code_format():
    """Тест формата кода приглашения"""
    db = Database()
    
    codes = [db.generate_invite_code() for _ in range(10)]
    
    for code in codes:
        assert len(code) == 6, f"Код {code} имеет неправильную длину"
        assert code.isalnum(), f"Код {code} содержит недопустимые символы"
        assert code.isupper(), f"Код {code} не в верхнем регистре"
    
    assert len(set(codes)) >= 8, "Слишком много повторяющихся кодов"

@pytest.mark.asyncio
async def test_database_initialization():
    """Тест инициализации базы данных"""
    db = Database()
    
    assert db.pool is None
    
    assert hasattr(db, 'connect')
    assert hasattr(db, 'disconnect')
    assert hasattr(db, 'init_db')

def test_imports():
    """Тест импорта всех необходимых модулей"""
    try:
        import config
        import database
        import main
        from handlers import start, pairs, ideas, dates
        from keyboards import inline
        
        assert True  #
    except ImportError as e:
        try:
            import config
            import database
            import main
            assert True
        except ImportError as core_e:
            pytest.fail(f"Ошибка импорта основных модулей: {core_e}")
        # Пропускаем тест, если проблема с дополнительными модулями
        pytest.skip(f"Некоторые модули недоступны: {e}")

@pytest.mark.asyncio 
async def test_user_operations_structure():
    """Тест структуры операций с пользователями"""
    db = Database()
    
    import inspect
    
    add_user_sig = inspect.signature(db.add_user)
    add_user_params = list(add_user_sig.parameters.keys())
    assert 'telegram_id' in add_user_params
    assert 'name' in add_user_params
    
    create_user_sig = inspect.signature(db.create_user)
    create_user_params = list(create_user_sig.parameters.keys())
    assert 'telegram_id' in create_user_params
    
    get_user_sig = inspect.signature(db.get_user)
    get_user_params = list(get_user_sig.parameters.keys())
    assert 'telegram_id' in get_user_params

@pytest.mark.asyncio
async def test_database_methods_signature():
    """Тест сигнатур методов базы данных"""
    db = Database()
    import inspect
    
    expected_params = {
        'add_user': ['telegram_id', 'name'],
        'create_user': ['telegram_id'],
        'get_user': ['telegram_id'],
        'delete_user': ['telegram_id'],
        'create_pair': ['user_id'],
        'join_pair': ['user_id', 'invite_code'],
        'get_user_pair': ['user_id'],
        'get_random_idea': [],
        'get_ideas_by_category': ['category']
    }
    
    for method_name, expected in expected_params.items():
        if hasattr(db, method_name):
            method = getattr(db, method_name)
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            if 'self' in params:
                params.remove('self')
            
            for expected_param in expected:
                assert expected_param in params, f"Метод {method_name} должен содержать параметр {expected_param}"

def test_database_class_structure():
    """Тест структуры класса Database"""
    db = Database()
    
    assert hasattr(db, 'pool')
    
    assert db.pool is None
    
    essential_methods = [
        'connect', 'disconnect', 'init_db', 'create_tables',
        'add_user', 'get_user', 'create_pair', 'join_pair'
    ]
    
    for method in essential_methods:
        assert hasattr(db, method), f"Отсутствует метод {method}"
        assert callable(getattr(db, method)), f"{method} не является функцией"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])