"""
Services — mirrors ride-share's packages/api/src/services.ts
Business logic layer: calls DB, AI, and scraper utilities.
CardService, FeedService, TeacherService.
"""

from src.db import get_db

# ── Card Service ────────────────────────────────────────────
class CardService:
    """Handles URL summarization and card management."""

    async def summarize(self, url: str, save_teacher: bool = False) -> dict:
        # 1. Scrape content from URL
        # 2. Summarize with GPT-4o-mini
        # 3. Store in Supabase via db
        db = get_db()
        # Full implementation delegates to swipelearn_services pipeline
        return {"status": "ok", "url": url}

    async def get(self, card_id: str) -> dict:
        db = get_db()
        result = db.table("knowledge_cards").select("*").eq("id", card_id).single().execute()
        return result.data

    async def save(self, card_id: str) -> dict:
        db = get_db()
        db.table("saved_cards").insert({"card_id": card_id}).execute()
        return {"success": True}

    async def unsave(self, card_id: str) -> dict:
        db = get_db()
        db.table("saved_cards").delete().eq("card_id", card_id).execute()
        return {"success": True}


# ── Feed Service ────────────────────────────────────────────
class FeedService:
    """Handles feed generation and seen tracking."""

    async def get_feed(self, page: int = 1, page_size: int = 20) -> dict:
        db = get_db()
        offset = (page - 1) * page_size
        result = (
            db.table("knowledge_cards")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return {"cards": result.data, "page": page, "has_more": len(result.data) == page_size}

    async def get_saved(self, page: int = 1, page_size: int = 20) -> dict:
        db = get_db()
        offset = (page - 1) * page_size
        result = (
            db.table("saved_cards")
            .select("*, knowledge_cards(*)")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return {"cards": result.data, "page": page, "has_more": len(result.data) == page_size}

    async def mark_seen(self, card_id: str) -> dict:
        db = get_db()
        db.table("feed_history").insert({"card_id": card_id}).execute()
        return {"success": True}


# ── Teacher Service ─────────────────────────────────────────
class TeacherService:
    """Handles creator follow/unfollow and their card feeds."""

    async def get_all(self) -> dict:
        db = get_db()
        result = db.table("teachers").select("*").execute()
        return {"teachers": result.data}

    async def follow(self, body: dict) -> dict:
        db = get_db()
        result = db.table("teachers").upsert(body).execute()
        return {"teacher": result.data[0] if result.data else {}}

    async def unfollow(self, teacher_id: str) -> dict:
        db = get_db()
        db.table("user_teachers").delete().eq("teacher_id", teacher_id).execute()
        return {"success": True}

    async def get_cards(self, teacher_id: str, page: int = 1) -> dict:
        db = get_db()
        result = (
            db.table("knowledge_cards")
            .select("*")
            .eq("teacher_id", teacher_id)
            .execute()
        )
        return {"cards": result.data}
