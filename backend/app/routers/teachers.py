"""
Teachers Router
================
Handles teacher (creator) management: follow, unfollow, list, view cards.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.teacher import TeacherCreate, Teacher
from app.services.teacher_tracker import TeacherTracker
from app.routers.auth import get_current_user
from app.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teachers", tags=["Teachers"])

teacher_tracker = TeacherTracker()


@router.get("")
async def list_teachers(
    user: dict = Depends(get_current_user),
):
    """
    List all teachers the user follows.
    Includes post count for each teacher.
    """
    db = get_supabase_client()

    # Get user's followed teachers
    result = db.table("user_teachers") \
        .select("*, teachers(*)") \
        .eq("user_id", user["id"]) \
        .order("followed_at", desc=True) \
        .execute()

    teachers = []
    for item in (result.data or []):
        teacher = item.get("teachers", {})
        if teacher:
            # Get post count
            count_result = db.table("knowledge_cards") \
                .select("id", count="exact") \
                .eq("teacher_id", teacher["id"]) \
                .execute()
            teacher["posts_count"] = count_result.count or 0
            teacher["followed_at"] = item["followed_at"]
            teachers.append(teacher)

    return {"teachers": teachers}


@router.post("")
async def follow_teacher(
    teacher_data: TeacherCreate,
    user: dict = Depends(get_current_user),
):
    """
    Follow a new teacher (creator).
    
    Creates the teacher record if it doesn't exist,
    and discovers their RSS feed for automatic monitoring.
    """
    db = get_supabase_client()
    website_url = str(teacher_data.website_url)

    # Check if teacher already exists
    existing = db.table("teachers") \
        .select("*") \
        .eq("website_url", website_url) \
        .execute()

    if existing.data:
        teacher = existing.data[0]
    else:
        # Discover RSS feed
        rss_url = await teacher_tracker.discover_rss_feed(website_url)

        # Create teacher
        teacher_record = {
            "name": teacher_data.name,
            "website_url": website_url,
            "blog_rss_url": rss_url,
            "avatar_url": teacher_data.avatar_url,
        }

        result = db.table("teachers") \
            .insert(teacher_record) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create teacher")

        teacher = result.data[0]

    # Create follow relationship
    db.table("user_teachers").upsert({
        "user_id": user["id"],
        "teacher_id": teacher["id"],
    }).execute()

    return {
        "message": f"Now following {teacher['name']}",
        "teacher": teacher,
    }


@router.delete("/{teacher_id}")
async def unfollow_teacher(
    teacher_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Unfollow a teacher.
    Removes the follow relationship but keeps the teacher record and cards.
    """
    db = get_supabase_client()

    db.table("user_teachers") \
        .delete() \
        .eq("user_id", user["id"]) \
        .eq("teacher_id", teacher_id) \
        .execute()

    return {"message": "Teacher unfollowed"}


@router.get("/{teacher_id}/cards")
async def get_teacher_cards(
    teacher_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user: dict = Depends(get_current_user),
):
    """Get all Knowledge Cards from a specific teacher."""
    db = get_supabase_client()
    offset = (page - 1) * page_size

    result = db.table("knowledge_cards") \
        .select("*") \
        .eq("teacher_id", teacher_id) \
        .order("created_at", desc=True) \
        .range(offset, offset + page_size - 1) \
        .execute()

    cards = result.data or []

    # Check saved status
    if cards:
        card_ids = [c["id"] for c in cards]
        saved_result = db.table("saved_cards") \
            .select("card_id") \
            .eq("user_id", user["id"]) \
            .in_("card_id", card_ids) \
            .execute()
        saved_ids = {s["card_id"] for s in (saved_result.data or [])}
        for card in cards:
            card["is_saved"] = card["id"] in saved_ids

    return {
        "cards": cards,
        "page": page,
        "has_more": len(cards) == page_size,
    }
