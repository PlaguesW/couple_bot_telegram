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
        """Base method for making API requests"""
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
                        return {"error": "Не найдено"}
                    else:
                        error_text = await response.text()
                        return {"error": f"Ошибка API: {response.status} - {error_text}"}
            except asyncio.TimeoutError:
                return {"error": "Превышено время ожидания ответа от сервера"}
            except Exception as e:
                return {"error": f"Ошибка соединения: {str(e)}"}
    
    # Methods for working with users
    async def create_user(self, telegram_id: int, username: str, first_name: str) -> Dict[Any, Any]:
        """Create new user in the system"""
        return await self._make_request(
            "POST", 
            "/users/", 
            {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name
            }
        )
    
    async def get_user(self, telegram_id: int) -> Dict[Any, Any]:
        """Get all information about a user"""
        return await self._make_request("GET", f"/users/{telegram_id}")
    
    # Methods for working with pairs
    async def create_pair(self, creator_telegram_id: int) -> Dict[Any, Any]:
        """Создание новой пары"""
        return await self._make_request(
            "POST", 
            "/pairs/", 
            {"creator_telegram_id": creator_telegram_id}
        )
    
    async def join_pair(self, code: str, joiner_telegram_id: int) -> Dict[Any, Any]:
        """Connecting to an existing pair"""
        return await self._make_request(
            "POST", 
            f"/pairs/{code}/join", 
            {"joiner_telegram_id": joiner_telegram_id}
        )
    
    async def get_user_pair(self, telegram_id: int) -> Dict[Any, Any]:
        """Get pair information for a user"""
        return await self._make_request("GET", f"/users/{telegram_id}/pair")
    
    # Methods for working with date ideas
    async def get_random_idea(self, category: Optional[str] = None) -> Dict[Any, Any]:
        """Get a random date idea"""
        params = {"category": category} if category else None
        return await self._make_request("GET", "/ideas/random", params=params)
    
    async def get_ideas_by_category(self, category: str) -> Dict[Any, Any]:
        """Get date ideas by category"""
        return await self._make_request("GET", f"/ideas/category/{category}")
    
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
            "/date_proposals/", 
            {
                "pair_id": pair_id,
                "proposer_telegram_id": proposer_telegram_id,
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
            f"/date_proposals/{proposal_id}/respond", 
            {
                "responder_telegram_id": responder_telegram_id,
                "accepted": accepted
            }
        )
    
    async def get_pending_proposals(self, telegram_id: int) -> Dict[Any, Any]:
        """Get pending date proposals for a user"""
        return await self._make_request("GET", f"/users/{telegram_id}/pending_proposals")
    
    async def get_pair_history(self, pair_id: int) -> Dict[Any, Any]:
        """Get history of dates for a pair"""
        return await self._make_request("GET", f"/pairs/{pair_id}/history")

api_client = APIClient()