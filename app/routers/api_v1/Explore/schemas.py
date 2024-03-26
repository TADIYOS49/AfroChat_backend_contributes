from typing import List
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, HttpUrl


class EntityType(Enum):
    RECOMMENDED = "Recommended"
    FEATURED = "Featured"
    FAVORITE = "Favorite"
    DISCOVER = "Discover"
    TOOL = "Tool"
    ATHLETE = "Athlete"
    AUTHOR = "Author & Poet"
    BUSINESS_MAGNATE = "Business Magnate"
    CELEBRITY_CHEF = "Celebrity Chef"
    COMEDIAN = "Comedian"
    DOCTOR = "Doctor"
    ENTREPRENEUR = "Entrepreneur"
    FICTIONAL = "Fictional"
    HISTORIAN = "Historian"
    INFLUENCER = "Influencer"
    MEDICAL_PROFESSIONAL = "Medical Professional"
    MUSICIAN = "Musician"
    PHILOSOPHER = "Philosopher"
    POLITICIAN = "Politician"
    PSYCHOLOGIST = "Psychologist"
    SCIENTIST = "Scientist"
    SPACE_EXPLORER = "Space Explorer"
    SPIRITUAL_LEADERS = "Spiritual Leaders"
    TECHNOCRAT = "Technocrat"
    ASSISTANT = "Assistant"


class EntityExists(BaseModel):
    exists: bool
    message: str


class CategoryOut(BaseModel):
    title: str
    description: str = ""


class EntityCategories(BaseModel):
    categories: List[CategoryOut]


class EntityOut(BaseModel):
    id: UUID
    name: str = Field(..., max_length=100)
    image: str = Field(..., max_length=200)
    default_color: str = "#EEF6FE"
    description: str = Field(..., max_length=5000)
    is_premium: bool = False
    creator_uuid: UUID = None
    created_at: datetime = "2023-12-01"
    created_by: str = "Afrochat"
    type: str = Field(..., max_length=200)
    is_preferable_entity: bool = False
    total_messages: int
