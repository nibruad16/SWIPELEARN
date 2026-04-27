"""
Cards Router
=============
Handles Knowledge Card creation (URL summarization) and retrieval.
"""

from fastapi import APIRouter, HTTPException, Depends
from swipelearn_core.models.card import SummarizeRequest, SummarizeResponse, KnowledgeCard
from swipelearn_services.scraper import ContentScraper
from swipelearn_services.summarizer import SummarizerAI
from swipelearn_services.feed_service import FeedService
from app.routers.auth import get_current_user
from app.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cards", tags=["Knowledge Cards"])

# Service instances
scraper = ContentScraper()
summarizer = SummarizerAI()
feed_service = FeedService()


@router.post("/summarize", response_model=dict)
async def summarize_url(
    request: SummarizeRequest,
    user: dict = Depends(get_current_user),
):
    """
    Summarize a blog post URL into a Knowledge Card.

    Flow:
    1. Scrape the URL for clean content
    2. Send to AI for summarization
    3. Store the Knowledge Card in DB
    4. Optionally link to a Teacher

    Args:
        request: Contains the URL and save_teacher flag.
        user: Authenticated user from JWT.

    Returns:
        The created Knowledge Card.
    """
    url = str(request.url)

    # Check if card already exists for this URL
    db = get_supabase_client()
    existing = db.table("knowledge_cards") \
        .select("*") \
        .eq("source_url", url) \
        .execute()

    if existing.data:
        logger.info(f"Card already exists for URL: {url}")
        return {
            "card": existing.data[0],
            "message": "Card already exists for this URL",
            "is_new": False,
        }

    try:
        # Step 1: Scrape
        scraped = await scraper.scrape(url)

        # Step 2: Summarize
        metadata = {
            "title": scraped.title,
            "author": scraped.author,
            "url": url,
        }
        card_base = await summarizer.process(scraped.text, metadata)

        # Step 3: Store in DB
        card_data = {
            "source_url": url,
            "title": card_base.title,
            "author": card_base.author,
            "tl_dr": card_base.tl_dr,
            "key_points": card_base.key_points,
            "steal_insight": card_base.steal_insight,
            "raw_content": scraped.text[:5000],  # Store truncated raw text
        }

        # Step 4: Handle teacher linking
        teacher_name = None
        if request.save_teacher and scraped.author:
            teacher_result = db.table("teachers") \
                .upsert(
                    {
                        "name": scraped.author,
                        "website_url": f"https://{scraped.domain}",
                    },
                    on_conflict="name,website_url",
                ) \
                .execute()

            if teacher_result.data:
                teacher = teacher_result.data[0]
                card_data["teacher_id"] = teacher["id"]
                teacher_name = teacher["name"]

                # Auto-follow the teacher
                db.table("user_teachers").upsert({
                    "user_id": user["id"],
                    "teacher_id": teacher["id"],
                }).execute()

        stored_card = await feed_service.store_card(card_data)

        return {
            "card": stored_card,
            "teacher_name": teacher_name,
            "message": "Successfully summarized",
            "is_new": True,
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Summarization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to summarize URL")


@router.get("/{card_id}", response_model=dict)
async def get_card(
    card_id: str,
    user: dict = Depends(get_current_user),
):
    """Get a single Knowledge Card by ID."""
    db = get_supabase_client()

    result = db.table("knowledge_cards") \
        .select("*") \
        .eq("id", card_id) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")

    card = result.data[0]

    # Check if user has saved this card
    saved = db.table("saved_cards") \
        .select("card_id") \
        .eq("user_id", user["id"]) \
        .eq("card_id", card_id) \
        .execute()

    card["is_saved"] = bool(saved.data)

    return card


@router.post("/{card_id}/save")
async def save_card(
    card_id: str,
    user: dict = Depends(get_current_user),
):
    """Save a card to user's saved list."""
    success = await feed_service.save_card(user["id"], card_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save card")
    return {"message": "Card saved"}


@router.delete("/{card_id}/save")
async def unsave_card(
    card_id: str,
    user: dict = Depends(get_current_user),
):
    """Remove a card from user's saved list."""
    success = await feed_service.unsave_card(user["id"], card_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to unsave card")
    return {"message": "Card removed from saved list"}
