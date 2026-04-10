"""
Teacher Schemas
Pydantic models for Teacher/Creator data validation.
"""

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional


class TeacherCreate(BaseModel):
    """Schema for adding a new teacher."""
    name: str
    website_url: HttpUrl
    blog_rss_url: Optional[HttpUrl] = None
    avatar_url: Optional[str] = None


class Teacher(BaseModel):
    """Full teacher schema."""
    id: UUID
    name: str
    website_url: str
    blog_rss_url: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    posts_count: int = 0

    class Config:
        from_attributes = True


class TeacherWithCards(Teacher):
    """Teacher with their knowledge cards."""
    cards: list["KnowledgeCardSummary"] = []


class UserTeacher(BaseModel):
    """Schema for user-teacher follow relationship."""
    user_id: UUID
    teacher_id: UUID
    followed_at: datetime
    teacher: Teacher


# Avoid circular import
from swipelearn_core.models.card import KnowledgeCardSummary  # noqa: E402

TeacherWithCards.model_rebuild()
