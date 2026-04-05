"""
Supabase Database Client
Provides a configured Supabase client for database operations.
"""

from supabase import create_client, Client
from app.config import get_settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client using service key for backend operations."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_auth_client() -> Client:
    """Create and return a Supabase client using anon key for auth operations."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)
