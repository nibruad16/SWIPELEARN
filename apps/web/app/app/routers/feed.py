"""
Feed Router
============
Handles the Knowledge Card feed and saved cards list.
"""

from fastapi import APIRouter, Depends, Query
from swipelearn_services.feed_service import FeedService
from app.routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feed", tags=["Feed"])

feed_service = FeedService()


@router.get("")
async def get_feed(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page"),
    user: dict = Depends(get_current_user),
):
    """
    Get the user's personalized Knowledge Card feed.
    
    Returns paginated cards from followed teachers and general content.
    Cards are ordered by creation date (newest first).
    """
    cards = await feed_service.get_feed(
        user_id=user["id"],
        page=page,
        page_size=page_size,
    )

    return {
        "cards": cards,
        "page": page,
        "page_size": page_size,
        "has_more": len(cards) == page_size,
    }


@router.get("/saved")
async def get_saved(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user: dict = Depends(get_current_user),
):
    """Get the user's saved Knowledge Cards."""
    cards = await feed_service.get_saved_cards(
        user_id=user["id"],
        page=page,
        page_size=page_size,
    )

    return {
        "cards": cards,
        "page": page,
        "page_size": page_size,
        "has_more": len(cards) == page_size,
    }


@router.post("/seen/{card_id}")
async def mark_seen(
    card_id: str,
    user: dict = Depends(get_current_user),
):
    """Mark a card as seen by the user (for feed algorithm)."""
    await feed_service.mark_seen(user["id"], card_id)
    return {"message": "Card marked as seen"}
