"""
Knowledge Card Schemas
Pydantic models for Knowledge Card data validation.
"""

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional


class KnowledgeCardCreate(BaseModel):
    """Schema for creating a knowledge card from a URL."""
    url: HttpUrl


class KnowledgeCardBase(BaseModel):
    """Base schema for a Knowledge Card."""
    title: str
    author: Optional[str] = None
    tl_dr: str
    key_points: list[str]
    steal_insight: str


class KnowledgeCard(KnowledgeCardBase):
    """Full Knowledge Card schema with DB fields."""
    id: UUID
    source_url: str
    teacher_id: Optional[UUID] = None
    created_at: datetime
    is_saved: bool = False

    class Config:
        from_attributes = True


class KnowledgeCardSummary(BaseModel):
    """Lightweight card for feed display."""
    id: UUID
    title: str
    author: Optional[str] = None
    tl_dr: str
    key_points: list[str]
    steal_insight: str
    source_url: str
    is_saved: bool = False
    created_at: datetime


class SummarizeRequest(BaseModel):
    """Request schema for URL summarization."""
    url: HttpUrl
    save_teacher: bool = False


class SummarizeResponse(BaseModel):
    """Response from summarization endpoint."""
    card: KnowledgeCard
    teacher_name: Optional[str] = None
    message: str = "Successfully summarized"
