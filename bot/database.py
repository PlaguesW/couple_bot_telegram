import asyncpg
import asyncio
import random
import string
from typing import Optional, List, Dict, Any
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create connection pool to the database"""
        self.pool = await asyncpg.create_pool(DATABASE_URL)
    
    async def disconnect(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
    
    # Users
    async def add_user(self, telegram_id: int, name: str, username: str = None) -> bool:
        """Add a new user to the database"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO users (telegram_id, name, username) VALUES ($1, $2, $3)",
                    telegram_id, name, username
                )
                return True
            except asyncpg.UniqueViolationError:
                return False
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """GEtting user by Telegram ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return dict(row) if row else None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    
    # Pairs
    def generate_invite_code(self) -> str:
        """Generate a unique invite code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    async def create_pair(self, user_id: int) -> str:
        """Create a new pair and return the invite code"""
        async with self.pool.acquire() as conn:
            invite_code = self.generate_invite_code()
            # Check if the invite code is unique
            while await conn.fetchval("SELECT id FROM pairs WHERE invite_code = $1", invite_code):
                invite_code = self.generate_invite_code()
            
            await conn.execute(
                "INSERT INTO pairs (user1_id, invite_code) VALUES ($1, $2)",
                user_id, invite_code
            )
            return invite_code
    
    async def join_pair(self, user_id: int, invite_code: str) -> bool:
        """Join an existing pair using the invite code"""
        async with self.pool.acquire() as conn:
            # Check if the invite code exists and if the pair is not full
            pair = await conn.fetchrow(
                "SELECT * FROM pairs WHERE invite_code = $1 AND user2_id IS NULL",
                invite_code
            )
            if not pair or pair['user1_id'] == user_id:
                return False
            
            # Add the user to the pair
            await conn.execute(
                "UPDATE pairs SET user2_id = $1 WHERE invite_code = $2",
                user_id, invite_code
            )
            return True
    
    async def get_user_pair(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the pair of a user"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM pairs WHERE user1_id = $1 OR user2_id = $1",
                user_id
            )
            return dict(row) if row else None
    
    async def get_partner_id(self, user_id: int) -> Optional[int]:
        """Get the partner ID for a user"""
        pair = await self.get_user_pair(user_id)
        if not pair:
            return None
        
        return pair['user2_id'] if pair['user1_id'] == user_id else pair['user1_id']
    
    # Ideas
    async def get_random_idea(self) -> Optional[Dict[str, Any]]:
        """Get random active idea"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM ideas WHERE is_active = TRUE ORDER BY RANDOM() LIMIT 1"
            )
            return dict(row) if row else None
    
    async def get_idea_by_id(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Get idea by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM ideas WHERE id = $1",
                idea_id
            )
            return dict(row) if row else None
    
    async def get_ideas_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get idea by category"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM ideas WHERE category = $1 AND is_active = TRUE ORDER BY RANDOM()",
                category
            )
            return [dict(row) for row in rows]
    
    async def get_all_categories(self) -> List[str]:
        """Get all unique categories of ideas"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT DISTINCT category FROM ideas WHERE is_active = TRUE"
            )
            return [row['category'] for row in rows]
    
    # Date proposals
    async def create_date_proposal(self, pair_id: int, idea_id: int, proposer_id: int) -> int:
        """Make a date proposal"""
        async with self.pool.acquire() as conn:
            proposal_id = await conn.fetchval(
                "INSERT INTO date_proposals (pair_id, idea_id, proposer_id) VALUES ($1, $2, $3) RETURNING id",
                pair_id, idea_id, proposer_id
            )
            return proposal_id
    
    async def get_pending_proposals(self, pair_id: int) -> List[Dict[str, Any]]:
        """Get pending date proposals for a pair"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT dp.*, i.title, i.description, u.name as proposer_name 
                FROM date_proposals dp
                JOIN ideas i ON dp.idea_id = i.id
                JOIN users u ON dp.proposer_id = u.id
                WHERE dp.pair_id = $1 AND dp.status = 'pending'
                ORDER BY dp.created_at DESC
                """,
                pair_id
            )
            return [dict(row) for row in rows]
    
    async def respond_to_proposal(self, proposal_id: int, response: str) -> bool:
        """Answer to a date proposal"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE date_proposals SET status = $1 WHERE id = $2 AND status = 'pending'",
                response, proposal_id
            )
            return result != "UPDATE 0"
    
    async def get_date_history(self, pair_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get date history for a pair"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT dp.*, i.title, i.description, u.name as proposer_name 
                FROM date_proposals dp
                JOIN ideas i ON dp.idea_id = i.id
                JOIN users u ON dp.proposer_id = u.id
                WHERE dp.pair_id = $1 AND dp.status != 'pending'
                ORDER BY dp.created_at DESC
                LIMIT $2
                """,
                pair_id, limit
            )
            return [dict(row) for row in rows]

# Global instance of the database
db = Database()