"""
Progress Router
================
REST endpoints for user progress: XP, streaks, and badges.

Endpoints:
  GET  /progress/me           — Full progress snapshot
  POST /progress/swipe        — Record a card swipe (awards XP)
  POST /progress/save         — Record a card save (awards bonus XP)
  GET  /progress/leaderboard  — Top users by XP (anonymous display)
"""

from fastapi import APIRouter, Depends, HTTPException
from app.routers.auth import get_current_user
from app.database import get_supabase_client
from swipelearn_services.progress_tracker import ProgressTracker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress", tags=["Progress & Gamification"])

# Singleton service instance
_progress_tracker = ProgressTracker()


@router.get("/me", response_model=dict)
async def get_my_progress(
    user: dict = Depends(get_current_user),
):
    """
    Return the authenticated user's full progress snapshot.

    Response::

        {
            "user_id": "...",
            "xp": 350,
            "level": 3,
            "streak_days": 5,
            "longest_streak": 12,
            "cards_read": 47,
            "badges": [
                {
                    "id": "streak_3",
                    "name": "On Fire 🔥",
                    "description": "...",
                    "earned": true,
                    "earned_at": "2026-05-01T..."
                },
                ...
            ],
            "last_active_date": "2026-05-05"
        }
    """
    try:
        return await _progress_tracker.get_progress(user["id"])
    except Exception as e:
        logger.error(f"Error fetching progress for {user['id']}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch progress")


@router.post("/swipe", response_model=dict)
async def record_swipe(
    body: dict = {},
    user: dict = Depends(get_current_user),
):
    """
    Record that the user swiped / read a card.

    Optional body::

        { "card_id": "<uuid>" }

    Response::

        {
            "xp_earned": 10,
            "total_xp": 360,
            "level": 3,
            "streak_days": 6,
            "new_badges": [...],
            "streak_extended": true
        }
    """
    try:
        card_id: str | None = body.get("card_id") if body else None
        return await _progress_tracker.record_swipe(user["id"], card_id=card_id)
    except Exception as e:
        logger.error(f"Error recording swipe for {user['id']}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to record swipe")


@router.post("/save", response_model=dict)
async def record_save(
    user: dict = Depends(get_current_user),
):
    """
    Award bonus XP for saving a card.

    Response::

        {
            "xp_earned": 10,
            "total_xp": 370,
            "level": 3
        }
    """
    try:
        return await _progress_tracker.record_save(user["id"])
    except Exception as e:
        logger.error(f"Error recording save XP for {user['id']}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to record save XP")


@router.get("/leaderboard", response_model=dict)
async def get_leaderboard(
    limit: int = 10,
    user: dict = Depends(get_current_user),
):
    """
    Return top N users by XP for the leaderboard.
    Displays only anonymized display names or first-name + last initial.

    Response::

        {
            "leaderboard": [
                {"rank": 1, "display_name": "Alice K.", "xp": 4200, "level": 7},
                ...
            ],
            "my_rank": 23,
            "my_xp": 370
        }
    """
    try:
        db = get_supabase_client()

        # Top N by XP
        top_result = db.table("user_progress") \
            .select("user_id, xp") \
            .order("xp", desc=True) \
            .limit(max(1, min(limit, 50))) \
            .execute()

        top_rows = top_result.data or []

        # Fetch display names for those users
        user_ids = [r["user_id"] for r in top_rows]
        names_result = db.table("profiles") \
            .select("id, display_name") \
            .in_("id", user_ids) \
            .execute()
        name_map = {r["id"]: r.get("display_name", "Anonymous") for r in (names_result.data or [])}

        from swipelearn_services.progress_tracker import ProgressTracker
        leaderboard = []
        for rank, row in enumerate(top_rows, start=1):
            full_name = name_map.get(row["user_id"], "Anonymous")
            # Anonymize: "Alice Kim" → "Alice K."
            parts = full_name.split()
            display = f"{parts[0]} {parts[1][0]}." if len(parts) >= 2 else full_name
            leaderboard.append({
                "rank": rank,
                "display_name": display,
                "xp": row["xp"],
                "level": ProgressTracker._xp_to_level(row["xp"]),
                "is_me": row["user_id"] == user["id"],
            })

        # Caller's own rank
        all_result = db.table("user_progress") \
            .select("user_id, xp") \
            .order("xp", desc=True) \
            .execute()
        all_rows = all_result.data or []
        my_rank = next(
            (i + 1 for i, r in enumerate(all_rows) if r["user_id"] == user["id"]),
            None,
        )
        my_row = next((r for r in all_rows if r["user_id"] == user["id"]), None)

        return {
            "leaderboard": leaderboard,
            "my_rank": my_rank,
            "my_xp": my_row["xp"] if my_row else 0,
        }

    except Exception as e:
        logger.error(f"Leaderboard error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch leaderboard")
