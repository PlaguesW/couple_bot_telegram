import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
from config import settings


class APIClient:
    """Клиент для работы с backend API"""
    
    def __init__(self):
        self.base_url = settings.api_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполнить HTTP запрос к API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"API Error {response.status}: {response_data}")
                    raise APIError(f"API Error {response.status}: {response_data.get('detail', 'Unknown error')}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {e}")
    
    #* Users
    async def register_user(self, telegram_id: int, name: str, username: str = None) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        data = {
            "telegram_id": telegram_id,
            "name": name,
            "username": username
        }
        return await self._make_request("POST", "/auth/register", data=data)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Получить пользователя по ID"""
        return await self._make_request("GET", f"/users/{user_id}")
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Dict[str, Any]:
        """Получить пользователя по Telegram ID"""
        return await self._make_request("GET", f"/users/telegram/{telegram_id}")
    
    #* Pairs
    async def create_couple(self, user_id: int) -> Dict[str, Any]:
        """Создать новую пару"""
        data = {"user_id": user_id}
        return await self._make_request("POST", "/couples/", data=data)
    
    async def join_couple(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Присоединиться к паре по коду"""
        data = {
            "user_id": user_id,
            "invite_code": invite_code
        }
        return await self._make_request("POST", "/couples/join", data=data)
    
    async def get_couple(self, couple_id: int) -> Dict[str, Any]:
        """Получить информацию о паре"""
        return await self._make_request("GET", f"/couples/{couple_id}")
    
    async def get_couple_by_code(self, invite_code: str) -> Dict[str, Any]:
        """Получить пару по коду приглашения"""
        return await self._make_request("GET", f"/couples/code/{invite_code}")
    
    async def get_user_couple(self, user_id: int) -> Dict[str, Any]:
        """Получить пару пользователя"""
        return await self._make_request("GET", f"/couples/user/{user_id}")
    
    #* Ideas
    async def get_ideas(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить список идей"""
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await self._make_request("GET", "/ideas/", params=params)
    
    async def get_idea(self, idea_id: int) -> Dict[str, Any]:
        """Получить конкретную идею"""
        return await self._make_request("GET", f"/ideas/{idea_id}")
    
    async def create_idea(self, title: str, description: str, category: str) -> Dict[str, Any]:
        """Создать новую идею"""
        data = {
            "title": title,
            "description": description,
            "category": category
        }
        return await self._make_request("POST", "/ideas/", data=data)
    
    async def update_idea(self, idea_id: int, title: str = None, description: str = None, category: str = None) -> Dict[str, Any]:
        """Обновить идею"""
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if category:
            data["category"] = category
        
        return await self._make_request("PATCH", f"/ideas/{idea_id}", data=data)
    
    async def delete_idea(self, idea_id: int) -> Dict[str, Any]:
        """Удалить идею"""
        return await self._make_request("DELETE", f"/ideas/{idea_id}")
    
    async def get_random_idea(self, category: str = None) -> Dict[str, Any]:
        """Получить случайную идею"""
        params = {"category": category} if category else {}
        return await self._make_request("GET", "/ideas/random", params=params)
    
    #* Dates/Events
    async def create_date_proposal(
        self,
        couple_id: int,
        idea_id: int,
        proposer_id: int,
        scheduled_date: str = None
    ) -> Dict[str, Any]:
        """Создать предложение свидания"""
        data = {
            "couple_id": couple_id,
            "idea_id": idea_id,
            "proposer_id": proposer_id
        }
        if scheduled_date:
            data["scheduled_date"] = scheduled_date
        
        return await self._make_request("POST", "/dates/proposal", data=data)
    
    async def respond_to_proposal(self, event_id: int, response: str, user_id: int) -> Dict[str, Any]:
        """Ответить на предложение свидания"""
        data = {
            "event_id": event_id,
            "response": response,  # "accepted" или "rejected"
            "user_id": user_id
        }
        return await self._make_request("POST", "/dates/respond", data=data)
    
    async def get_date_history(self, couple_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить историю свиданий пары"""
        params = {"limit": limit}
        return await self._make_request("GET", f"/dates/history/{couple_id}", params=params)
    
    async def get_date_event(self, event_id: int) -> Dict[str, Any]:
        """Получить конкретное событие"""
        return await self._make_request("GET", f"/dates/{event_id}")
    
    async def get_pending_proposals(self, couple_id: int) -> List[Dict[str, Any]]:
        """Получить ожидающие предложения"""
        params = {"status": "pending"}
        return await self._make_request("GET", f"/dates/couple/{couple_id}", params=params)
    
    async def mark_date_completed(self, event_id: int, user_id: int) -> Dict[str, Any]:
        """Отметить свидание как завершенное"""
        data = {
            "event_id": event_id,
            "user_id": user_id
        }
        return await self._make_request("POST", "/dates/complete", data=data)


class APIError(Exception):
    """Исключение для ошибок API"""
    pass


# Глобальный экземпляр клиента
api_client = APIClient()

# Функции-обертки для совместимости с текущим кодом handlers
async def get_ideas(category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Получить список идей"""
    async with api_client as client:
        return await client.get_ideas(category, limit)

async def add_idea(title: str, description: str, category: str) -> Dict[str, Any]:
    """Добавить новую идею"""
    async with api_client as client:
        return await client.create_idea(title, description, category)

async def update_idea(idea_id: int, title: str = None, description: str = None, category: str = None) -> Dict[str, Any]:
    """Обновить идею"""
    async with api_client as client:
        return await client.update_idea(idea_id, title, description, category)

async def delete_idea(idea_id: int) -> Dict[str, Any]:
    """Удалить идею"""
    async with api_client as client:
        return await client.delete_idea(idea_id)

async def get_random_idea(category: str = None) -> Dict[str, Any]:
    """Получить случайную идею"""
    async with api_client as client:
        return await client.get_random_idea(category)

# Функции-обертки для работы с пользователями
async def register_user(telegram_id: int, name: str, username: str = None) -> Dict[str, Any]:
    """Регистрация нового пользователя"""
    async with api_client as client:
        return await client.register_user(telegram_id, name, username)

async def get_user_by_telegram_id(telegram_id: int) -> Dict[str, Any]:
    """Получить пользователя по Telegram ID"""
    async with api_client as client:
        return await client.get_user_by_telegram_id(telegram_id)

# Функции-обертки для работы с парами
async def create_couple(user_id: int) -> Dict[str, Any]:
    """Создать новую пару"""
    async with api_client as client:
        return await client.create_couple(user_id)

async def join_couple(user_id: int, invite_code: str) -> Dict[str, Any]:
    """Присоединиться к паре по коду"""
    async with api_client as client:
        return await client.join_couple(user_id, invite_code)

async def get_user_couple(user_id: int) -> Dict[str, Any]:
    """Получить пару пользователя"""
    async with api_client as client:
        return await client.get_user_couple(user_id)

# Функции-обертки для работы с событиями/свиданиями
async def create_date_proposal(couple_id: int, idea_id: int, proposer_id: int, scheduled_date: str = None) -> Dict[str, Any]:
    """Создать предложение свидания"""
    async with api_client as client:
        return await client.create_date_proposal(couple_id, idea_id, proposer_id, scheduled_date)

async def respond_to_proposal(event_id: int, response: str, user_id: int) -> Dict[str, Any]:
    """Ответить на предложение свидания"""
    async with api_client as client:
        return await client.respond_to_proposal(event_id, response, user_id)

async def get_date_history(couple_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Получить историю свиданий пары"""
    async with api_client as client:
        return await client.get_date_history(couple_id, limit)

async def get_pending_proposals(couple_id: int) -> List[Dict[str, Any]]:
    """Получить ожидающие предложения"""
    async with api_client as client:
        return await client.get_pending_proposals(couple_id)