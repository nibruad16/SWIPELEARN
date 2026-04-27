"""
Auth Router
============
Handles user authentication: signup, login, Google OAuth.
Delegates to Supabase Auth.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from swipelearn_core.models.user import UserSignup, UserLogin, AuthResponse, UserProfile
from app.database import get_supabase_auth_client, get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict)
async def signup(user_data: UserSignup):
    """
    Register a new user with email and password.
    Creates a Supabase auth user and a profile record.
    """
    try:
        client = get_supabase_auth_client()
        
        # Create user in Supabase Auth
        response = client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })

        if not response.user:
            raise HTTPException(status_code=400, detail="Signup failed")

        # Create profile
        db = get_supabase_client()
        db.table("profiles").upsert({
            "id": str(response.user.id),
            "display_name": user_data.display_name or user_data.email.split("@")[0],
        }).execute()

        return {
            "message": "User created successfully",
            "user_id": str(response.user.id),
            "access_token": response.session.access_token if response.session else None,
            "refresh_token": response.session.refresh_token if response.session else None,
        }

    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    """Login with email and password."""
    try:
        client = get_supabase_auth_client()
        
        response = client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })

        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
            },
        }

    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/google", response_model=dict)
async def google_auth(request: Request):
    """
    Handle Google OAuth.
    Frontend sends the Google ID token, backend verifies with Supabase.
    """
    body = await request.json()
    id_token = body.get("id_token")

    if not id_token:
        raise HTTPException(status_code=400, detail="id_token is required")

    try:
        client = get_supabase_auth_client()

        response = client.auth.sign_in_with_id_token({
            "provider": "google",
            "token": id_token,
        })

        if not response.session:
            raise HTTPException(status_code=401, detail="Google auth failed")

        # Upsert profile
        db = get_supabase_client()
        db.table("profiles").upsert({
            "id": str(response.user.id),
            "display_name": response.user.user_metadata.get("full_name", ""),
            "avatar_url": response.user.user_metadata.get("avatar_url", ""),
        }).execute()

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "display_name": response.user.user_metadata.get("full_name", ""),
            },
        }

    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=401, detail="Google authentication failed")


async def get_current_user(request: Request) -> dict:
    """
    Dependency: Extract and verify user from Authorization header.
    Used as a dependency injection for protected endpoints.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    try:
        client = get_supabase_auth_client()
        response = client.auth.get_user(token)

        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "id": str(response.user.id),
            "email": response.user.email,
        }

    except Exception as e:
        logger.error(f"Auth verification error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")
