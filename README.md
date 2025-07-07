# Couple_bot_telegram
# Couple Bot - Бот для романтических свиданий 💕


### Структура проекта
```
couple_bot_telegram/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Точка входа приложения
│   ├── config.py            # Конфигурация бота
│   ├── api_client.py        # Клиент для работы с backend API
│   ├── states.py            # Состояния для FSM
│   ├── handlers/            # Обработчики команд и сообщений
│   │   ├── __init__.py
│   │   ├── start.py         # Команда /start и регистрация
│   │   ├── couple.py        # Управление парами
│   │   ├── ideas.py         # Работа с идеями
│   │   ├── dates.py         # Предложения свиданий
│   │   └── help.py          # Помощь и информация
│   ├── keyboards/           # Клавиатуры
│   │   ├── __init__.py
│   │   ├── inline.py        # Inline клавиатуры
│   │   └── reply.py         # Reply клавиатуры
│   ├── middlewares/         # Middleware для бота
│   │   ├── __init__.py
│   │   └── auth.py          # Аутентификация пользователей
│   └── utils/               # Утилиты
│       ├── __init__.py
│       └── helpers.py       # Вспомогательные функции
├── requirements.txt
├── .env.example
├── README.md
└── docker-compose.yml       # Для запуска всего проекта
```
