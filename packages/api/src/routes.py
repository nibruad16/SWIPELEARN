"""
API Routes — mirrors ride-share's packages/api/src/routes.ts
Mounts all domain routers under /api.
"""

from fastapi import APIRouter
from src.services import CardService, FeedService, TeacherService

router = APIRouter()

card_service = CardService()
feed_service = FeedService()
teacher_service = TeacherService()


# ── Cards ──────────────────────────────────────
@router.post("/cards/summarize")
async def summarize_url(body: dict):
    url = body.get("url")
    save_teacher = body.get("save_teacher", False)
    result = await card_service.summarize(url, save_teacher=save_teacher)
    return result


@router.get("/cards/{card_id}")
async def get_card(card_id: str):
    return await card_service.get(card_id)


@router.post("/cards/{card_id}/save")
async def save_card(card_id: str):
    return await card_service.save(card_id)


@router.delete("/cards/{card_id}/save")
async def unsave_card(card_id: str):
    return await card_service.unsave(card_id)


# ── Feed ───────────────────────────────────────
@router.get("/feed")
async def get_feed(page: int = 1, page_size: int = 20):
    return await feed_service.get_feed(page=page, page_size=page_size)


@router.get("/feed/saved")
async def get_saved(page: int = 1, page_size: int = 20):
    return await feed_service.get_saved(page=page, page_size=page_size)


@router.post("/feed/seen/{card_id}")
async def mark_seen(card_id: str):
    return await feed_service.mark_seen(card_id)


# ── Teachers ───────────────────────────────────
@router.get("/teachers")
async def get_teachers():
    return await teacher_service.get_all()


@router.post("/teachers")
async def follow_teacher(body: dict):
    return await teacher_service.follow(body)


@router.delete("/teachers/{teacher_id}")
async def unfollow_teacher(teacher_id: str):
    return await teacher_service.unfollow(teacher_id)


@router.get("/teachers/{teacher_id}/cards")
async def get_teacher_cards(teacher_id: str, page: int = 1):
    return await teacher_service.get_cards(teacher_id, page=page)
