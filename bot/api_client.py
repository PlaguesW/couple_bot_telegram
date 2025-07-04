import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from config import API_BASE_URL, API_TIMEOUT

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[Any, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[Any, Any]:
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return {"status": "not_found"}  # Изменили структуру ответа
                    else:
                        error_text = await response.text()
                        return {"error": f"Ошибка API: {response.status} - {error_text}"}
            except asyncio.TimeoutError:
                return {"error": "Timeout error"}
            except Exception as e:
                return {"error": f"Connection error: {str(e)}"}
    
    # Methods for working with users
    async def create_user(self, telegram_id: int, username: str, first_name: str) -> Dict[Any, Any]:
        """Create new user in the system"""
        return await self._make_request(
            "POST", 
            "/user/",  # Изменили с /users/register
            {
                "id": telegram_id,  # Изменили с user_id/telegram_id
                "username": username,
                "name": first_name
            }
        )
    
    async def get_user(self, telegram_id: int) -> Dict[Any, Any]:
        """Get all information about a user"""
        return await self._make_request(
            "GET", 
            f"/user/{telegram_id}",  # Изменили с /users/profile?user_id=
            params=None  # Параметры больше не нужны
        )
    
    # Methods for working with pairs
    async def create_pair(self, creator_telegram_id: int) -> Dict[Any, Any]:
        """Создание новой пары"""
        return await self._make_request(
            "POST", 
            "/pair/",  # Изменили с /pairs/
            {"creator_id": creator_telegram_id}  # Изменили параметр
        )
    
    async def join_pair(self, code: str, joiner_telegram_id: int) -> Dict[Any, Any]:
        """Connecting to an existing pair"""
        return await self._make_request(
            "POST", 
            f"/pair/{code}/join",  # Изменили с /pairs/{code}/join
            {"joiner_id": joiner_telegram_id}  # Изменили параметр
        )
    
    async def get_user_pair(self, telegram_id: int) -> Dict[Any, Any]:
        """Get pair information for a user"""
        return await self._make_request(
            "GET", 
            f"/user/{telegram_id}/pair"  # Оставили как есть (но проверьте в бекенде)
        )
    
    # Methods for working with date ideas
    async def get_random_idea(self, category: Optional[str] = None) -> Dict[Any, Any]:
        """Get a random date idea"""
        params = {"category": category} if category else None
        return await self._make_request(
            "GET", 
            "/idea/random",  # Изменили с /ideas/random
            params=params
        )
    
    async def get_ideas_by_category(self, category: str) -> Dict[Any, Any]:
        """Get date ideas by category"""
        return await self._make_request(
            "GET", 
            f"/idea/category/{category}"  # Изменили с /ideas/category/
        )
    
    # Methods for working with date proposals
    async def create_date_proposal(
        self, 
        pair_id: int, 
        proposer_telegram_id: int, 
        idea_id: int,
        custom_description: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Create a date proposal"""
        return await self._make_request(
            "POST", 
            "/date_proposal/",  # Изменили с /date_proposals/
            {
                "pair_id": pair_id,
                "proposer_id": proposer_telegram_id,  # Изменили параметр
                "idea_id": idea_id,
                "custom_description": custom_description
            }
        )
    
    async def respond_to_proposal(
        self, 
        proposal_id: int, 
        responder_telegram_id: int, 
        accepted: bool
    ) -> Dict[Any, Any]:
        """Respond to a date proposal"""
        return await self._make_request(
            "PUT", 
            f"/date_proposal/{proposal_id}/respond",  # Изменили с /date_proposals/
            {
                "responder_id": responder_telegram_id,  # Изменили параметр
                "accepted": accepted
            }
        )
    
    async def get_pending_proposals(self, telegram_id: int) -> Dict[Any, Any]:
        """Get pending date proposals for a user"""
        return await self._make_request(
            "GET", 
            f"/user/{telegram_id}/pending_proposals"  # Оставили как есть
        )
    
    async def get_pair_history(self, pair_id: int) -> Dict[Any, Any]:
        """Get history of dates for a pair"""
        return await self._make_request(
            "GET", 
            f"/pair/{pair_id}/history"  # Изменили с /pairs/
        )

api_client = APIClient()