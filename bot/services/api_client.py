import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger

from bot.config import settings
from bot.models.schemas import UserCreate, UserResponse, PairCreate, PairResponse, IdeaResponse, EventCreate, EventResponse


class APIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=settings.API_TIMEOUT)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Base method for making API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        logger.error(f"API request failed: {response.status} - {await response.text()}")
                        return None
        except asyncio.TimeoutError:
            logger.error(f"API request timeout: {method} {url}")
            return None
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
    
    # Users endpoints
    async def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Creaate a new user"""
        result = await self._make_request("POST", "/users/", user_data.model_dump())
        return UserResponse(**result) if result else None
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserResponse]:
        """Get user by Telegram ID"""
        result = await self._make_request("GET", f"/users/telegram/{telegram_id}")
        return UserResponse(**result) if result else None
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        result = await self._make_request("GET", f"/users/username/{username}")
        return UserResponse(**result) if result else None
    
    # Pairs endpoints
    async def create_pair(self, pair_data: PairCreate) -> Optional[PairResponse]:
        """Create a new pair of users"""
        result = await self._make_request("POST", "/pairs/", pair_data.model_dump())
        return PairResponse(**result) if result else None
    
    async def get_user_pair(self, user_id: int) -> Optional[PairResponse]:
        """Get user pair by user ID"""
        result = await self._make_request("GET", f"/pairs/user/{user_id}")
        return PairResponse(**result) if result else None
    
    # Ideas endpoints
    async def get_ideas(self, category: Optional[str] = None, limit: int = 10) -> List[IdeaResponse]:
        """Get ideas for dates"""
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        result = await self._make_request("GET", "/ideas/", params=params)
        return [IdeaResponse(**idea) for idea in result] if result else []
    
    async def get_random_ideas(self, count: int = 5) -> List[IdeaResponse]:
        """Get random ideas for dates"""
        result = await self._make_request("GET", f"/ideas/random?count={count}")
        return [IdeaResponse(**idea) for idea in result] if result else []
    
    # Events endpoints
    async def create_event(self, event_data: EventCreate) -> Optional[EventResponse]:
        """Create new event for a pair"""
        result = await self._make_request("POST", "/events/", event_data.model_dump())
        return EventResponse(**result) if result else None
    
    async def get_user_events(self, user_id: int) -> List[EventResponse]:
        """Get all events for a user"""
        result = await self._make_request("GET", f"/events/user/{user_id}")
        return [EventResponse(**event) for event in result] if result else []
    
    async def respond_to_event(self, event_id: int, response: str) -> Optional[EventResponse]:
        """Response to an event"""
        result = await self._make_request("PUT", f"/events/{event_id}/respond", {"response": response})
        return EventResponse(**result) if result else None


# Global instance of APIClient
api_client = APIClient()