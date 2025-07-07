# Couple Bot Telegram

Telegram-бот для планирования свиданий, взаимодействующий с REST API приложения [Couple Bot Backend](https://github.com/PlaguesW/couple_bot_backend).

---

## 🚀 Возможности

- Регистрация пользователя / начальное приветствие  
- Создание пары и присоединение по коду приглашения  
- Просмотр списка, добавление, редактирование и удаление идей  
- Предложение свидания и ответ на него (принятие/отклонение)  
- Просмотр истории ваших свиданий  

---

## 🧱 Структура проекта
```
couple_bot_telegram/
├── bot/
│   ├── __init__.py
│   ├── main.py              
│   ├── config.py           
│   ├── api_client.py        
│   ├── states.py            
│   ├── handlers/            
│   │   ├── __init__.py
│   │   ├── start.py         
│   │   ├── couple.py        
│   │   ├── ideas.py         
│   │   ├── dates.py        
│   │   └── help.py          
│   ├── keyboards/           
│   │   ├── __init__.py
│   │   ├── inline.py        
│   │   └── reply.py         
│   ├── middlewares/         
│   │   ├── __init__.py
│   │   └── auth.py          
│   └── utils/               
│       ├── __init__.py
│       └── helpers.py       
├── requirements.txt
├── .env.example
├── README.md
└── docker-compose.yml       
```
## ⚙️ Установка и запуск

1. Клонируй репозиторий:
```bash
git clone https://github.com/PlaguesW/couple_bot_telegram.git
cd couple_bot_telegram