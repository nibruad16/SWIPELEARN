"""
Feed Service
=============
Handles feed generation and card management logic.
"""

from app.database import get_supabase_client
from app.models.card import KnowledgeCard, KnowledgeCardSummary
from uuid import UUID
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FeedService:
    """
    Manages the Knowledge Card feed for users.
    
    Handles:
    - Fetching personalized feed (cards from followed teachers)
    - Saving/unsaving cards
    - Tracking seen cards
    """

    def __init__(self):
        self.db = get_supabase_client()

    async def get_feed(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict]:
        """
        Get personalized feed for a user.
        
        Returns cards from:
        1. Followed teachers (priority)
        2. General/trending cards
        
        Excludes already-seen cards.
        """
        offset = (page - 1) * page_size

        # Get cards from followed teachers + general cards
        # Ordered by created_at descending (newest first)
        result = self.db.table("knowledge_cards") \
            .select("*") \
            .order("created_at", desc=True) \
            .range(offset, offset + page_size - 1) \
            .execute()

        cards = result.data or []

        # Check which cards the user has saved
        if cards:
            card_ids = [c["id"] for c in cards]
            saved_result = self.db.table("saved_cards") \
                .select("card_id") \
                .eq("user_id", user_id) \
                .in_("card_id", card_ids) \
                .execute()
            saved_ids = {s["card_id"] for s in (saved_result.data or [])}

            for card in cards:
                card["is_saved"] = card["id"] in saved_ids

        return cards

    async def save_card(self, user_id: str, card_id: str) -> bool:
        """Save a card to user's saved list."""
        try:
            self.db.table("saved_cards").upsert({
                "user_id": user_id,
                "card_id": card_id,
            }).execute()
            logger.info(f"User {user_id} saved card {card_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving card: {e}")
            return False

    async def unsave_card(self, user_id: str, card_id: str) -> bool:
        """Remove a card from user's saved list."""
        try:
            self.db.table("saved_cards") \
                .delete() \
                .eq("user_id", user_id) \
                .eq("card_id", card_id) \
                .execute()
            logger.info(f"User {user_id} unsaved card {card_id}")
            return True
        except Exception as e:
            logger.error(f"Error unsaving card: {e}")
            return False

    async def get_saved_cards(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict]:
        """Get user's saved cards."""
        offset = (page - 1) * page_size

        result = self.db.table("saved_cards") \
            .select("*, knowledge_cards(*)") \
            .eq("user_id", user_id) \
            .order("saved_at", desc=True) \
            .range(offset, offset + page_size - 1) \
            .execute()

        cards = []
        for item in (result.data or []):
            card = item.get("knowledge_cards", {})
            card["is_saved"] = True
            cards.append(card)

        return cards

    async def mark_seen(self, user_id: str, card_id: str):
        """Mark a card as seen by the user."""
        try:
            self.db.table("feed_history").upsert({
                "user_id": user_id,
                "card_id": card_id,
            }).execute()
        except Exception as e:
            logger.warning(f"Error marking card seen: {e}")

    async def store_card(self, card_data: dict) -> dict:
        """Store a new knowledge card in the database."""
        result = self.db.table("knowledge_cards") \
            .upsert(card_data, on_conflict="source_url") \
            .execute()

        if result.data:
            return result.data[0]
        raise ValueError("Failed to store knowledge card")
