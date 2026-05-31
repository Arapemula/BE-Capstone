from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import request


def _get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return token or None


def _get_supabase_user(token: str) -> dict | None:
    supabase_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    if not supabase_url or not supabase_key:
        return None

    auth_request = Request(
        f"{supabase_url}/auth/v1/user",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {token}",
        },
        method="GET",
    )

    try:
        with urlopen(auth_request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None


def get_current_user_context() -> dict | None:
    token = _get_bearer_token()
    if not token:
        return None

    user = _get_supabase_user(token)
    if not user or not user.get("id"):
        return None

    metadata = user.get("user_metadata") or {}
    email = user.get("email") or ""
    name = metadata.get("full_name") or metadata.get("name") or (email.split("@")[0] if email else "SkillMap User")

    return {
        "external_id": user["id"],
        "email": email or f"{user['id']}@supabase.local",
        "name": name,
        "provider": "supabase",
    }
