



<div style="font-family: monospace; background-color: #f5; padding: 15px; border-radius: 5px;">
<pre>
bot/
├── main.py              # Точка входа
├── config.py            # Конфигурация
├── api_client.py        # HTTP клиент для работы с API
├── handlers/            # Обработчики команд
│   ├── __init__.py
│   ├── start.py         # Регистрация и создание пар
│   ├── dates.py         # Работа со свиданиями
│   └── profile.py       # Профиль и история
├── keyboards/           # Клавиатуры
│   ├── __init__.py
│   ├── main_menu.py
│   └── inline.py
├── middlewares/         # Middleware
│   ├── __init__.py
│   └── auth.py          # Авторизация пользователей
├── utils/               # Утилиты
│   ├── __init__.py
│   └── helpers.py
├── requirements.txt     # Зависимости
└── .env.example         # Пример конфигурации               
</pre>
</div>