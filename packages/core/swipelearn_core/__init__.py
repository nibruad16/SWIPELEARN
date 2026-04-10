# SwipeLearn Core — Shared models and schemas
"""
Shared domain models for the SwipeLearn platform.

This package provides Pydantic schemas used across all backend packages:
- packages/api (routers reference these models)
- packages/services (services return/consume these models)

Install: pip install -e packages/core
"""

from swipelearn_core.models.card import (
    KnowledgeCardCreate,
    KnowledgeCardBase,
    KnowledgeCard,
    KnowledgeCardSummary,
    SummarizeRequest,
    SummarizeResponse,
)
from swipelearn_core.models.teacher import (
    TeacherCreate,
    Teacher,
    TeacherWithCards,
    UserTeacher,
)
from swipelearn_core.models.user import (
    UserSignup,
    UserLogin,
    UserProfile,
    AuthResponse,
    TokenData,
)

__all__ = [
    # Card models
    "KnowledgeCardCreate",
    "KnowledgeCardBase",
    "KnowledgeCard",
    "KnowledgeCardSummary",
    "SummarizeRequest",
    "SummarizeResponse",
    # Teacher models
    "TeacherCreate",
    "Teacher",
    "TeacherWithCards",
    "UserTeacher",
    # User models
    "UserSignup",
    "UserLogin",
    "UserProfile",
    "AuthResponse",
    "TokenData",
]
