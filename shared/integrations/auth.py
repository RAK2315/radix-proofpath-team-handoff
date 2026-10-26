from dataclasses import dataclass

import httpx
from fastapi import Request

from shared.integrations.config import public_key, setting
from shared.integrations.errors import AppError


@dataclass
class Identity:
    owner: str
    token: str = ""
    maintenance: bool = False


def identity(request: Request) -> Identity:
    if setting("RADIX_AUTH_MODE", "local") == "local":
        if request.client and request.client.host not in {"127.0.0.1", "::1", "testclient"}:
            raise AppError("LOCAL_ONLY", "Local development is restricted to loopback", 403)
        return Identity("local-single-user")
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    if not token:
        raise AppError("AUTH_REQUIRED", "Sign in using a Supabase access token", 401)
    try:
        response = httpx.get(
            f"{setting('SUPABASE_URL')}/auth/v1/user",
            headers={"apikey": public_key(), "Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        return Identity(response.json()["id"], token)
    except (httpx.HTTPError, KeyError, ValueError):
        raise AppError("AUTH_INVALID", "Session is invalid or expired", 401) from None
