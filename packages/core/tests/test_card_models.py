"""
Tests for KnowledgeCard schemas (swipelearn_core.models.card).

Covers:
- KnowledgeCardBase creation and validation
- KnowledgeCard (full DB model) with optional fields
- KnowledgeCardSummary lightweight feed model
- SummarizeRequest URL validation
- Field constraints and edge cases
"""

import pytest
from uuid import UUID
from datetime import datetime, timezone
from pydantic import ValidationError

from swipelearn_core.models.card import (
    KnowledgeCardBase,
    KnowledgeCard,
    KnowledgeCardSummary,
    KnowledgeCardCreate,
    SummarizeRequest,
    SummarizeResponse,
)
from tests.conftest import CARD_ID, TEACHER_ID, NOW


# ─────────────────────────────────────────────
#  KnowledgeCardBase Tests
# ─────────────────────────────────────────────

class TestKnowledgeCardBase:
    """Tests for the KnowledgeCardBase schema."""

    def test_creates_with_all_required_fields(self, valid_card_base_data):
        card = KnowledgeCardBase(**valid_card_base_data)
        assert card.title == "A Complete Guide to useEffect"
        assert card.author == "Dan Abramov"
        assert card.tl_dr == "useEffect is a synchronization mechanism, not a lifecycle hook."
        assert len(card.key_points) == 3
        assert card.steal_insight == "Think of effects as synchronizing React to an external system."

    def test_author_is_optional(self, valid_card_base_data):
        """Author field must be nullable — not all blogs expose author metadata."""
        data = {**valid_card_base_data, "author": None}
        card = KnowledgeCardBase(**data)
        assert card.author is None

    def test_key_points_must_be_a_list(self, valid_card_base_data):
        data = {**valid_card_base_data, "key_points": "not a list"}
        with pytest.raises(ValidationError):
            KnowledgeCardBase(**data)

    def test_key_points_can_have_up_to_five_items(self, valid_card_base_data):
        data = {**valid_card_base_data, "key_points": ["p1", "p2", "p3", "p4", "p5"]}
        card = KnowledgeCardBase(**data)
        assert len(card.key_points) == 5

    def test_missing_title_raises(self, valid_card_base_data):
        del valid_card_base_data["title"]
        with pytest.raises(ValidationError) as exc:
            KnowledgeCardBase(**valid_card_base_data)
        assert "title" in str(exc.value)

    def test_missing_tl_dr_raises(self, valid_card_base_data):
        del valid_card_base_data["tl_dr"]
        with pytest.raises(ValidationError) as exc:
            KnowledgeCardBase(**valid_card_base_data)
        assert "tl_dr" in str(exc.value)

    def test_missing_steal_insight_raises(self, valid_card_base_data):
        del valid_card_base_data["steal_insight"]
        with pytest.raises(ValidationError) as exc:
            KnowledgeCardBase(**valid_card_base_data)
        assert "steal_insight" in str(exc.value)

    def test_missing_key_points_raises(self, valid_card_base_data):
        del valid_card_base_data["key_points"]
        with pytest.raises(ValidationError) as exc:
            KnowledgeCardBase(**valid_card_base_data)
        assert "key_points" in str(exc.value)

    def test_model_dump_produces_correct_keys(self, valid_card_base_data):
        card = KnowledgeCardBase(**valid_card_base_data)
        dumped = card.model_dump()
        assert set(dumped.keys()) == {"title", "author", "tl_dr", "key_points", "steal_insight"}


# ─────────────────────────────────────────────
#  KnowledgeCard (Full DB model) Tests
# ─────────────────────────────────────────────

class TestKnowledgeCard:
    """Tests for the full KnowledgeCard schema (DB-hydrated model)."""

    def test_creates_with_all_db_fields(self, valid_card_db_data):
        card = KnowledgeCard(**valid_card_db_data)
        assert card.id == CARD_ID
        assert card.source_url == "https://overreacted.io/a-complete-guide-to-useeffect/"
        assert card.teacher_id == TEACHER_ID
        assert card.is_saved is False
        assert isinstance(card.created_at, datetime)

    def test_teacher_id_is_optional(self, valid_card_db_data):
        """Cards can exist without a linked teacher (direct URL paste)."""
        data = {**valid_card_db_data, "teacher_id": None}
        card = KnowledgeCard(**data)
        assert card.teacher_id is None

    def test_is_saved_defaults_to_false(self, valid_card_db_data):
        data = {k: v for k, v in valid_card_db_data.items() if k != "is_saved"}
        card = KnowledgeCard(**data)
        assert card.is_saved is False

    def test_inherits_base_fields(self, valid_card_db_data):
        """KnowledgeCard must expose all KnowledgeCardBase fields."""
        card = KnowledgeCard(**valid_card_db_data)
        assert card.title == "A Complete Guide to useEffect"
        assert card.tl_dr == "useEffect is a synchronization mechanism, not a lifecycle hook."
        assert len(card.key_points) == 3

    def test_id_is_uuid_type(self, valid_card_db_data):
        card = KnowledgeCard(**valid_card_db_data)
        assert isinstance(card.id, UUID)

    def test_created_at_is_datetime_type(self, valid_card_db_data):
        card = KnowledgeCard(**valid_card_db_data)
        assert isinstance(card.created_at, datetime)

    def test_missing_id_raises(self, valid_card_db_data):
        del valid_card_db_data["id"]
        with pytest.raises(ValidationError):
            KnowledgeCard(**valid_card_db_data)

    def test_missing_source_url_raises(self, valid_card_db_data):
        del valid_card_db_data["source_url"]
        with pytest.raises(ValidationError):
            KnowledgeCard(**valid_card_db_data)

    def test_missing_created_at_raises(self, valid_card_db_data):
        del valid_card_db_data["created_at"]
        with pytest.raises(ValidationError):
            KnowledgeCard(**valid_card_db_data)


# ─────────────────────────────────────────────
#  KnowledgeCardSummary Tests
# ─────────────────────────────────────────────

class TestKnowledgeCardSummary:
    """Tests for the lightweight feed card schema."""

    def test_creates_from_db_data(self, valid_card_db_data):
        summary = KnowledgeCardSummary(**valid_card_db_data)
        assert summary.id == CARD_ID
        assert summary.title == "A Complete Guide to useEffect"
        assert summary.is_saved is False

    def test_has_no_raw_content_field(self, valid_card_db_data):
        """Summary model must NOT expose raw_content — keeps feed payloads small."""
        summary = KnowledgeCardSummary(**valid_card_db_data)
        assert not hasattr(summary, "raw_content")

    def test_is_subset_of_knowledge_card_fields(self, valid_card_db_data):
        """Every field in Summary must be a subset of KnowledgeCard fields."""
        summary = KnowledgeCardSummary(**valid_card_db_data)
        summary_keys = set(summary.model_dump().keys())
        card = KnowledgeCard(**valid_card_db_data)
        card_keys = set(card.model_dump().keys())
        assert summary_keys.issubset(card_keys)


# ─────────────────────────────────────────────
#  SummarizeRequest Tests
# ─────────────────────────────────────────────

class TestSummarizeRequest:
    """Tests for the POST /cards/summarize request schema."""

    def test_valid_https_url(self):
        req = SummarizeRequest(url="https://overreacted.io/a-complete-guide-to-useeffect/")
        assert str(req.url).startswith("https://")

    def test_valid_http_url(self):
        req = SummarizeRequest(url="http://blog.example.com/post")
        assert str(req.url).startswith("http://")

    def test_save_teacher_defaults_to_false(self):
        req = SummarizeRequest(url="https://blog.example.com/post")
        assert req.save_teacher is False

    def test_save_teacher_can_be_set_to_true(self):
        req = SummarizeRequest(
            url="https://overreacted.io/a-complete-guide-to-useeffect/",
            save_teacher=True,
        )
        assert req.save_teacher is True

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            SummarizeRequest(url="not-a-url")

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            SummarizeRequest()

    def test_plain_domain_without_scheme_raises(self):
        """URLs without a scheme must be rejected."""
        with pytest.raises(ValidationError):
            SummarizeRequest(url="overreacted.io/post")


# ─────────────────────────────────────────────
#  KnowledgeCardCreate Tests
# ─────────────────────────────────────────────

class TestKnowledgeCardCreate:
    """Tests for the URL-only creation schema."""

    def test_valid_url(self):
        create = KnowledgeCardCreate(url="https://overreacted.io/a-complete-guide-to-useeffect/")
        assert str(create.url).startswith("https://")

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            KnowledgeCardCreate(url="definitely not a url")
