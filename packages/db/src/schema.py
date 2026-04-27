"""
DB Schema — mirrors ride-share's packages/db/src/schema.ts
Defines the SwipeLearn table structure using Python dataclasses
that map 1:1 to the Supabase PostgreSQL schema.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class KnowledgeCard:
    """knowledge_cards table"""
    id: UUID
    source_url: str           # UNIQUE — prevents duplicate processing
    title: str
    author: Optional[str]
    teacher_id: Optional[UUID]
    tl_dr: str
    key_points: list[str]     # JSONB in DB
    steal_insight: str
    raw_content: Optional[str]
    created_at: datetime
    is_saved: bool = False    # virtual — computed from saved_cards join


@dataclass
class Teacher:
    """teachers table"""
    id: UUID
    name: str
    website_url: str
    blog_rss_url: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    posts_count: int = 0      # virtual — computed from knowledge_cards count


@dataclass
class SavedCard:
    """saved_cards table"""
    user_id: UUID
    card_id: UUID
    saved_at: datetime


@dataclass
class UserTeacher:
    """user_teachers table — follow relationships"""
    user_id: UUID
    teacher_id: UUID
    followed_at: datetime


@dataclass
class FeedHistory:
    """feed_history table — seen tracking"""
    user_id: UUID
    card_id: UUID
    seen_at: datetime
