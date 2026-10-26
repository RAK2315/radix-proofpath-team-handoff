"""Private Supabase object access in the same user context as JSON records."""

from urllib.parse import quote

import httpx

from shared.integrations.auth import Identity
from shared.integrations.config import setting
from shared.integrations.errors import AppError
from shared.integrations.store import remote_headers


def object_request(user: Identity, method: str, path: str, content: bytes | None = None) -> bytes:
    if not path.startswith(user.owner + "/") or ".." in path.split("/"):
        raise AppError("SOURCE_MISMATCH", "Object path must belong to the authenticated owner", 403)
    bucket = setting("RADIX_DOCUMENT_BUCKET", "proofpath-documents")
    url = f"{setting('SUPABASE_URL')}/storage/v1/object/{quote(bucket, safe='')}/{quote(path, safe='/')}"
    headers = {**remote_headers(user), "Content-Type": "application/octet-stream"}
    try:
        response = httpx.request(method, url, headers=headers, content=content, timeout=30)
        if method == "DELETE" and response.status_code == 404:
            return b""
        response.raise_for_status()
        return response.content
    except httpx.HTTPError:
        raise AppError(
            "OBJECT_STORAGE_UNAVAILABLE",
            "Private file operation failed; check bucket policies and retry",
            503,
        ) from None
