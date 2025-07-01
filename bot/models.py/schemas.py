from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: str
    age: int
    gender: GenderEnum


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    name: str
    age: int
    gender: GenderEnum
    created_at: datetime
    is_active: bool


class PairCreate(BaseModel):
    user1_id: int
    user2_id: int


class PairResponse(BaseModel):
    id: int
    user1: UserResponse
    user2: UserResponse
    created_at: datetime
    is_active: bool


class IdeaResponse(BaseModel):
    id: int
    title: str
    description: str
    category: Optional[str]
    is_active: bool


class EventCreate(BaseModel):
    pair_id: int
    idea_id: Optional[int]
    title: str
    description: Optional[str]
    proposed_date: Optional[datetime]
    initiator_id: int


class EventResponse(BaseModel):
    id: int
    pair: PairResponse
    idea: Optional[IdeaResponse]
    title: str
    description: Optional[str]
    proposed_date: Optional[datetime]
    initiator: UserResponse
    status: str
    created_at: datetime