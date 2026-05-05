"""
Progress Tracker Service
=========================
Gamification engine for SwipeLearn.

Handles:
- Daily learning streaks (consecutive day tracking)
- XP (experience points) awarded for swipe actions
- Badge / achievement unlocking
- Leaderboard snapshot data

Design Pattern: Observer-like — reacts to card-swipe events and updates
user progress state in Supabase atomically.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  XP Config
# ─────────────────────────────────────────────

XP_SWIPE_CARD = 5          # Awarded every time a card is swiped / read
XP_SAVE_CARD = 10          # Saving a card shows intent
XP_FIRST_OF_DAY = 20       # Bonus for opening the app today
XP_STREAK_MULTIPLIER = 2   # Doubles XP when on a streak ≥ 7 days

# ─────────────────────────────────────────────
#  Badge Definitions
# ─────────────────────────────────────────────

BADGES: list[dict] = [
    {"id": "first_swipe",     "name": "First Swipe",      "description": "Swiped your very first card!",           "xp_threshold": None, "streak_threshold": None, "cards_threshold": 1},
    {"id": "curious",         "name": "Curious Mind",     "description": "Read 10 knowledge cards.",               "xp_threshold": None, "streak_threshold": None, "cards_threshold": 10},
    {"id": "explorer",        "name": "Explorer",         "description": "Read 50 knowledge cards.",               "xp_threshold": None, "streak_threshold": None, "cards_threshold": 50},
    {"id": "scholar",         "name": "Scholar",          "description": "Read 200 knowledge cards.",              "xp_threshold": None, "streak_threshold": None, "cards_threshold": 200},
    {"id": "streak_3",        "name": "On Fire 🔥",       "description": "Maintained a 3-day learning streak.",    "xp_threshold": None, "streak_threshold": 3,    "cards_threshold": None},
    {"id": "streak_7",        "name": "Weekly Warrior",   "description": "Maintained a 7-day learning streak.",   "xp_threshold": None, "streak_threshold": 7,    "cards_threshold": None},
    {"id": "streak_30",       "name": "Unstoppable",      "description": "Maintained a 30-day learning streak.",  "xp_threshold": None, "streak_threshold": 30,   "cards_threshold": None},
    {"id": "xp_500",          "name": "Knowledge Seeker", "description": "Earned 500 XP.",                        "xp_threshold": 500,  "streak_threshold": None, "cards_threshold": None},
    {"id": "xp_2000",         "name": "Grand Scholar",    "description": "Earned 2 000 XP.",                      "xp_threshold": 2000, "streak_threshold": None, "cards_threshold": None},
]


class ProgressTracker:
    """
    Manages user progress: XP, streaks, and badges.

    Usage::

        tracker = ProgressTracker()
        result  = await tracker.record_swipe(user_id="abc-123")
        print(result["xp_earned"], result["new_badges"])
    """

    def __init__(self) -> None:
        # Lazy import to keep service independent of API layer
        from app.database import get_supabase_client  # type: ignore
        self.db = get_supabase_client()

    # ─────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────

    async def get_progress(self, user_id: str) -> dict:
        """
        Return the full progress snapshot for a user.

        Returns::

            {
                "user_id": str,
                "xp": int,
                "level": int,
                "streak_days": int,
                "longest_streak": int,
                "cards_read": int,
                "badges": [{"id": str, "name": str, ...}],
                "last_active_date": str | None,
            }
        """
        row = self._fetch_or_create_progress(user_id)
        badges = self._fetch_badges(user_id)

        return {
            "user_id": user_id,
            "xp": row["xp"],
            "level": self._xp_to_level(row["xp"]),
            "streak_days": row["streak_days"],
            "longest_streak": row["longest_streak"],
            "cards_read": row["cards_read"],
            "badges": badges,
            "last_active_date": row.get("last_active_date"),
        }

    async def record_swipe(self, user_id: str, card_id: Optional[str] = None) -> dict:
        """
        Called every time a user swipes / reads a card.

        Awards XP, updates streak, checks for new badges.

        Returns::

            {
                "xp_earned": int,
                "total_xp": int,
                "level": int,
                "streak_days": int,
                "new_badges": [...],
                "streak_extended": bool,
            }
        """
        row = self._fetch_or_create_progress(user_id)
        today = date.today()

        xp_earned = XP_SWIPE_CARD
        streak_extended = False

        # ── Streak logic ──
        last_active = self._parse_date(row.get("last_active_date"))
        streak_days = row["streak_days"]
        longest_streak = row["longest_streak"]

        if last_active is None or last_active < today - timedelta(days=1):
            # Streak broken or first time — reset to 1
            streak_days = 1
            xp_earned += XP_FIRST_OF_DAY
        elif last_active == today - timedelta(days=1):
            # Continued streak
            streak_days += 1
            streak_extended = True
            xp_earned += XP_FIRST_OF_DAY
        # else: already active today — no streak change, no first-of-day bonus

        # Apply streak multiplier
        if streak_days >= 7:
            xp_earned = int(xp_earned * XP_STREAK_MULTIPLIER)

        longest_streak = max(longest_streak, streak_days)
        new_total_xp = row["xp"] + xp_earned
        new_cards_read = row["cards_read"] + 1

        # ── Persist ──
        self.db.table("user_progress").upsert({
            "user_id": user_id,
            "xp": new_total_xp,
            "streak_days": streak_days,
            "longest_streak": longest_streak,
            "cards_read": new_cards_read,
            "last_active_date": today.isoformat(),
        }).execute()

        # ── Badge check ──
        new_badges = self._check_and_award_badges(
            user_id=user_id,
            xp=new_total_xp,
            streak_days=streak_days,
            cards_read=new_cards_read,
        )

        logger.info(
            f"Progress recorded | user={user_id} xp_earned={xp_earned} "
            f"streak={streak_days} cards_read={new_cards_read}"
        )

        return {
            "xp_earned": xp_earned,
            "total_xp": new_total_xp,
            "level": self._xp_to_level(new_total_xp),
            "streak_days": streak_days,
            "new_badges": new_badges,
            "streak_extended": streak_extended,
        }

    async def record_save(self, user_id: str) -> dict:
        """Award XP for saving a card."""
        row = self._fetch_or_create_progress(user_id)
        new_total_xp = row["xp"] + XP_SAVE_CARD

        self.db.table("user_progress").upsert({
            "user_id": user_id,
            "xp": new_total_xp,
        }).execute()

        return {
            "xp_earned": XP_SAVE_CARD,
            "total_xp": new_total_xp,
            "level": self._xp_to_level(new_total_xp),
        }

    # ─────────────────────────────────────────────
    #  Internal Helpers
    # ─────────────────────────────────────────────

    def _fetch_or_create_progress(self, user_id: str) -> dict:
        """Fetch the user_progress row or create it with defaults."""
        result = self.db.table("user_progress") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if result.data:
            return result.data

        # First-time user — insert default row
        defaults = {
            "user_id": user_id,
            "xp": 0,
            "streak_days": 0,
            "longest_streak": 0,
            "cards_read": 0,
            "last_active_date": None,
        }
        self.db.table("user_progress").insert(defaults).execute()
        return defaults

    def _fetch_badges(self, user_id: str) -> list[dict]:
        """Return all badges earned by the user."""
        result = self.db.table("user_badges") \
            .select("badge_id, earned_at") \
            .eq("user_id", user_id) \
            .execute()

        earned_ids = {row["badge_id"] for row in (result.data or [])}
        earned_at_map = {row["badge_id"]: row["earned_at"] for row in (result.data or [])}

        return [
            {**b, "earned": b["id"] in earned_ids, "earned_at": earned_at_map.get(b["id"])}
            for b in BADGES
        ]

    def _check_and_award_badges(
        self,
        user_id: str,
        xp: int,
        streak_days: int,
        cards_read: int,
    ) -> list[dict]:
        """Check all badge conditions and insert newly earned badges."""
        # Get already-earned badge IDs
        existing = self.db.table("user_badges") \
            .select("badge_id") \
            .eq("user_id", user_id) \
            .execute()
        already_earned = {row["badge_id"] for row in (existing.data or [])}

        new_badges: list[dict] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for badge in BADGES:
            bid = badge["id"]
            if bid in already_earned:
                continue

            earned = False
            if badge["xp_threshold"] is not None and xp >= badge["xp_threshold"]:
                earned = True
            if badge["streak_threshold"] is not None and streak_days >= badge["streak_threshold"]:
                earned = True
            if badge["cards_threshold"] is not None and cards_read >= badge["cards_threshold"]:
                earned = True

            if earned:
                try:
                    self.db.table("user_badges").insert({
                        "user_id": user_id,
                        "badge_id": bid,
                        "earned_at": now_iso,
                    }).execute()
                    new_badges.append(badge)
                    logger.info(f"Badge awarded | user={user_id} badge={bid}")
                except Exception as e:
                    logger.warning(f"Could not award badge {bid}: {e}")

        return new_badges

    @staticmethod
    def _xp_to_level(xp: int) -> int:
        """
        Simple level formula: level = floor(sqrt(xp / 100)) + 1.
        Level 1 = 0 XP, Level 2 = 100 XP, Level 5 = 1600 XP, …
        """
        import math
        return max(1, int(math.sqrt(xp / 100)) + 1)

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None
