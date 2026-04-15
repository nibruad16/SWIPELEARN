"""
Shared pytest fixtures for swipelearn_core tests.
Provides reusable sample data for KnowledgeCard, Teacher, and User tests.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID


# ─────────────────────────────────────────────
#  Shared IDs
# ─────────────────────────────────────────────

CARD_ID = UUID("00000000-0000-0000-0000-000000000001")
TEACHER_ID = UUID("00000000-0000-0000-0000-000000000002")
USER_ID = UUID("00000000-0000-0000-0000-000000000003")
NOW = datetime(2026, 4, 15, 12, 0, 0, tzinfo=timezone.utc)


# ─────────────────────────────────────────────
#  Card Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def valid_card_base_data() -> dict:
    """Minimal valid KnowledgeCardBase payload."""
    return {
        "title": "A Complete Guide to useEffect",
        "author": "Dan Abramov",
        "tl_dr": "useEffect is a synchronization mechanism, not a lifecycle hook.",
        "key_points": [
            "Each render has its own props, state, and effects",
            "The dependency array controls when effects re-run",
            "Cleanup runs before the next effect and on unmount",
        ],
        "steal_insight": "Think of effects as synchronizing React to an external system.",
    }


@pytest.fixture
def valid_card_db_data(valid_card_base_data) -> dict:
    """Full KnowledgeCard payload including DB fields."""
    return {
        **valid_card_base_data,
        "id": str(CARD_ID),
        "source_url": "https://overreacted.io/a-complete-guide-to-useeffect/",
        "teacher_id": str(TEACHER_ID),
        "created_at": NOW.isoformat(),
        "is_saved": False,
    }


# ─────────────────────────────────────────────
#  Teacher Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def valid_teacher_create_data() -> dict:
    """Minimal valid TeacherCreate payload."""
    return {
        "name": "Dan Abramov",
        "website_url": "https://overreacted.io",
    }


@pytest.fixture
def valid_teacher_db_data() -> dict:
    """Full Teacher payload including DB fields."""
    return {
        "id": str(TEACHER_ID),
        "name": "Dan Abramov",
        "website_url": "https://overreacted.io",
        "blog_rss_url": "https://overreacted.io/rss.xml",
        "avatar_url": None,
        "created_at": NOW.isoformat(),
        "posts_count": 12,
    }


# ─────────────────────────────────────────────
#  User Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def valid_signup_data() -> dict:
    """Valid UserSignup payload."""
    return {
        "email": "learner@swipelearn.app",
        "password": "Secure123!",
        "display_name": "Test Learner",
    }


@pytest.fixture
def valid_login_data() -> dict:
    """Valid UserLogin payload."""
    return {
        "email": "learner@swipelearn.app",
        "password": "Secure123!",
    }
