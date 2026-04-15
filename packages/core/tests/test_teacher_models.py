"""
Tests for Teacher schemas (swipelearn_core.models.teacher).

Covers:
- TeacherCreate input validation (name, URL, optional RSS)
- Teacher full DB model
- TeacherWithCards composite model
- UserTeacher follow relationship
"""

import pytest
from uuid import UUID
from datetime import datetime, timezone
from pydantic import ValidationError

from swipelearn_core.models.teacher import (
    TeacherCreate,
    Teacher,
    TeacherWithCards,
    UserTeacher,
)
from swipelearn_core.models.card import KnowledgeCardSummary
from tests.conftest import TEACHER_ID, USER_ID, CARD_ID, NOW


# ─────────────────────────────────────────────
#  TeacherCreate Tests
# ─────────────────────────────────────────────

class TestTeacherCreate:
    """Tests for the teacher creation/follow input schema."""

    def test_creates_with_required_fields(self, valid_teacher_create_data):
        teacher = TeacherCreate(**valid_teacher_create_data)
        assert teacher.name == "Dan Abramov"
        assert str(teacher.website_url).startswith("https://overreacted.io")

    def test_blog_rss_url_is_optional(self, valid_teacher_create_data):
        """RSS URL must be optional — we auto-discover it from the website."""
        teacher = TeacherCreate(**valid_teacher_create_data)
        assert teacher.blog_rss_url is None

    def test_blog_rss_url_can_be_provided(self, valid_teacher_create_data):
        data = {**valid_teacher_create_data, "blog_rss_url": "https://overreacted.io/rss.xml"}
        teacher = TeacherCreate(**data)
        assert str(teacher.blog_rss_url).startswith("https://")

    def test_avatar_url_is_optional(self, valid_teacher_create_data):
        teacher = TeacherCreate(**valid_teacher_create_data)
        assert teacher.avatar_url is None

    def test_avatar_url_can_be_string(self, valid_teacher_create_data):
        data = {**valid_teacher_create_data, "avatar_url": "https://cdn.example.com/avatar.jpg"}
        teacher = TeacherCreate(**data)
        assert teacher.avatar_url == "https://cdn.example.com/avatar.jpg"

    def test_invalid_website_url_raises(self):
        with pytest.raises(ValidationError):
            TeacherCreate(name="Test", website_url="not-a-url")

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError) as exc:
            TeacherCreate(website_url="https://example.com")
        assert "name" in str(exc.value)

    def test_missing_website_url_raises(self):
        with pytest.raises(ValidationError) as exc:
            TeacherCreate(name="Test Teacher")
        assert "website_url" in str(exc.value)

    def test_empty_name_is_accepted_by_pydantic(self, valid_teacher_create_data):
        """Pydantic allows empty strings — business logic rejects at router level."""
        data = {**valid_teacher_create_data, "name": ""}
        teacher = TeacherCreate(**data)
        assert teacher.name == ""

    def test_invalid_rss_url_raises(self, valid_teacher_create_data):
        data = {**valid_teacher_create_data, "blog_rss_url": "not-a-url"}
        with pytest.raises(ValidationError):
            TeacherCreate(**data)


# ─────────────────────────────────────────────
#  Teacher (DB model) Tests
# ─────────────────────────────────────────────

class TestTeacher:
    """Tests for the full Teacher schema (DB-hydrated)."""

    def test_creates_with_all_fields(self, valid_teacher_db_data):
        teacher = Teacher(**valid_teacher_db_data)
        assert teacher.id == TEACHER_ID
        assert teacher.name == "Dan Abramov"
        assert teacher.website_url == "https://overreacted.io"
        assert teacher.blog_rss_url == "https://overreacted.io/rss.xml"
        assert teacher.posts_count == 12
        assert isinstance(teacher.created_at, datetime)

    def test_posts_count_defaults_to_zero(self, valid_teacher_db_data):
        """New teachers have no posts yet."""
        data = {k: v for k, v in valid_teacher_db_data.items() if k != "posts_count"}
        teacher = Teacher(**data)
        assert teacher.posts_count == 0

    def test_blog_rss_url_is_optional(self, valid_teacher_db_data):
        data = {**valid_teacher_db_data, "blog_rss_url": None}
        teacher = Teacher(**data)
        assert teacher.blog_rss_url is None

    def test_avatar_url_is_optional(self, valid_teacher_db_data):
        data = {**valid_teacher_db_data, "avatar_url": None}
        teacher = Teacher(**data)
        assert teacher.avatar_url is None

    def test_id_is_uuid_type(self, valid_teacher_db_data):
        teacher = Teacher(**valid_teacher_db_data)
        assert isinstance(teacher.id, UUID)

    def test_created_at_is_datetime_type(self, valid_teacher_db_data):
        teacher = Teacher(**valid_teacher_db_data)
        assert isinstance(teacher.created_at, datetime)

    def test_missing_id_raises(self, valid_teacher_db_data):
        del valid_teacher_db_data["id"]
        with pytest.raises(ValidationError):
            Teacher(**valid_teacher_db_data)

    def test_missing_name_raises(self, valid_teacher_db_data):
        del valid_teacher_db_data["name"]
        with pytest.raises(ValidationError):
            Teacher(**valid_teacher_db_data)


# ─────────────────────────────────────────────
#  TeacherWithCards Tests
# ─────────────────────────────────────────────

class TestTeacherWithCards:
    """Tests for the Teacher + cards composite model."""

    def test_cards_defaults_to_empty_list(self, valid_teacher_db_data):
        teacher = TeacherWithCards(**valid_teacher_db_data)
        assert teacher.cards == []

    def test_inherits_all_teacher_fields(self, valid_teacher_db_data):
        teacher = TeacherWithCards(**valid_teacher_db_data)
        assert teacher.id == TEACHER_ID
        assert teacher.name == "Dan Abramov"
        assert teacher.posts_count == 12

    def test_cards_field_holds_knowledge_card_summaries(self, valid_teacher_db_data, valid_card_db_data):
        """Cards list must accept KnowledgeCardSummary items."""
        card = KnowledgeCardSummary(**valid_card_db_data)
        teacher = TeacherWithCards(**valid_teacher_db_data, cards=[card])
        assert len(teacher.cards) == 1
        assert teacher.cards[0].title == "A Complete Guide to useEffect"


# ─────────────────────────────────────────────
#  UserTeacher Tests
# ─────────────────────────────────────────────

class TestUserTeacher:
    """Tests for the user-teacher follow relationship schema."""

    def test_creates_with_all_fields(self, valid_teacher_db_data):
        teacher = Teacher(**valid_teacher_db_data)
        rel = UserTeacher(
            user_id=str(USER_ID),
            teacher_id=str(TEACHER_ID),
            followed_at=NOW.isoformat(),
            teacher=teacher,
        )
        assert rel.user_id == USER_ID
        assert rel.teacher_id == TEACHER_ID
        assert isinstance(rel.followed_at, datetime)
        assert rel.teacher.name == "Dan Abramov"

    def test_missing_user_id_raises(self, valid_teacher_db_data):
        teacher = Teacher(**valid_teacher_db_data)
        with pytest.raises(ValidationError):
            UserTeacher(
                teacher_id=str(TEACHER_ID),
                followed_at=NOW.isoformat(),
                teacher=teacher,
            )

    def test_missing_teacher_raises(self):
        with pytest.raises(ValidationError):
            UserTeacher(
                user_id=str(USER_ID),
                teacher_id=str(TEACHER_ID),
                followed_at=NOW.isoformat(),
            )
