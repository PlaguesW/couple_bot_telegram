import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List
from bot.config import API_URL

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making {method} request to {url}")
        if data:
            logger.info(f"Request data: {data}")
        
        try:
            async with session.request(method, url, json=data) as response:
                response_text = await response.text()
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response text: {response_text}")
                
                if response.status == 404:
                    return {"error": "Not found", "status": 404}
                elif response.status >= 400:
                    return {"error": f"HTTP {response.status}", "status": response.status}
                
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {"data": response_text}
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {"error": str(e), "status": 500}
    
    # Методы для пользователей
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/users/{user_id}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/users/", user_data)
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PUT", f"/users/{user_id}", user_data)
    
    # Методы для пар
    async def get_user_pair(self, user_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/users/{user_id}/pair")
    
    async def create_pair(self, pair_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/pairs/", pair_data)
    
    async def join_pair(self, user_id: int, pair_code: str) -> Dict[str, Any]:
        return await self._request("POST", f"/pairs/join", {
            "user_id": user_id,
            "pair_code": pair_code
        })
    
    # Методы для идей
    async def get_ideas_by_category(self, category: str) -> Dict[str, Any]:
        return await self._request("GET", f"/ideas/category/{category}")
    
    async def get_all_ideas(self) -> Dict[str, Any]:
        return await self._request("GET", "/ideas/")
    
    async def create_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/ideas/", idea_data)
    
    # Методы для событий/свиданий
    async def get_events(self, user_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/events/user/{user_id}")
    
    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/events/", event_data)
    
    async def create_date_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/events/proposal", proposal_data)
    
    async def respond_to_proposal(self, proposal_id: int, response: bool) -> Dict[str, Any]:
        return await self._request("POST", f"/events/proposal/{proposal_id}/respond", {
            "accepted": response
        })
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

# Глобальный экземпляр клиента
api_client = APIClient()