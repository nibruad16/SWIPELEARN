"""
DB client — mirrors ride-share's packages/db/src/index.ts
Exports a single Supabase client instance used by all services.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_db() -> Client:
    """Return singleton Supabase client (service role — bypasses RLS)."""
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


def get_anon_db() -> Client:
    """Return Supabase client using anon key (respects RLS — for auth ops)."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)
