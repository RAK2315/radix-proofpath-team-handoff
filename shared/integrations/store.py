"""Owner-scoped JSON records. Local SQLite or user-context Supabase REST/RLS."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

import httpx

from shared.integrations.auth import Identity
from shared.integrations.config import data_dir, public_key, setting
from shared.integrations.errors import AppError


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _db():
    db = None
    try:
        db = sqlite3.connect(data_dir() / "proofpath.sqlite3", timeout=15)
        db.execute(
            "CREATE TABLE IF NOT EXISTS records (owner TEXT, kind TEXT, id TEXT, revision INTEGER, payload TEXT, updated_at TEXT, PRIMARY KEY(owner,kind,id))"
        )
        with db:
            yield db
    except (sqlite3.Error, OSError):
        raise AppError(
            "STORAGE_UNAVAILABLE",
            "Local storage is unavailable. Check disk space and write permissions, then retry; keep your unsaved draft.",
            503,
        ) from None
    finally:
        if db is not None:
            db.close()


def _remote(user: Identity, method: str, **kwargs):
    if not user.token:
        raise AppError("AUTH_REQUIRED", "Supabase persistence requires authenticated user context", 401)
    headers = remote_headers(user)
    headers["Prefer"] = "return=representation"
    try:
        response = httpx.request(
            method,
            f"{setting('SUPABASE_URL')}/rest/v1/proofpath_records",
            headers=headers,
            timeout=20,
            **kwargs,
        )
        response.raise_for_status()
        return response.json() if response.content else []
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 409:
            raise AppError(
                "REVISION_CONFLICT", "Record changed or already exists; reload before saving", 409
            ) from None
        raise AppError(
            "STORAGE_UNAVAILABLE", "Supabase storage request failed; check grants/RLS and connection", 503
        ) from None
    except (httpx.HTTPError, ValueError):
        raise AppError(
            "STORAGE_UNAVAILABLE", "Supabase storage request failed; check grants/RLS and connection", 503
        ) from None


def remote_headers(user: Identity) -> dict[str, str]:
    if not user.token:
        raise AppError("AUTH_REQUIRED", "Remote storage requires an authenticated session", 401)
    if user.maintenance:
        # Used only by the explicitly invoked private maintenance CLI, never HTTP identities.
        headers = {"apikey": user.token}
        if not user.token.startswith("sb_secret_"):
            headers["Authorization"] = f"Bearer {user.token}"
        return headers
    return {"apikey": public_key(), "Authorization": f"Bearer {user.token}"}


def _payload(raw: str):
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("Expected record object")
        return value
    except (ValueError, TypeError):
        raise AppError(
            "STORAGE_UNAVAILABLE",
            "Stored record is unreadable; restore from a known backup before retrying",
            503,
        ) from None


def list_records(user: Identity, kind: str) -> list[dict[str, Any]]:
    if setting("RADIX_STORAGE_MODE", "local") == "supabase":
        records: list[dict[str, Any]] = []
        while True:
            batch = _remote(
                user,
                "GET",
                params={
                    "owner": f"eq.{user.owner}",
                    "kind": f"eq.{kind}",
                    "select": "payload",
                    "order": "updated_at.desc,id.asc",
                    "offset": len(records),
                    "limit": 500,
                },
            )
            if not batch:
                break
            records.extend(batch)
        return [r["payload"] for r in records]
    with _db() as db:
        rows = db.execute(
            "SELECT payload FROM records WHERE owner=? AND kind=? ORDER BY updated_at DESC",
            (user.owner, kind),
        ).fetchall()
    return [_payload(r[0]) for r in rows]


def get(user: Identity, kind: str, record_id: str) -> dict[str, Any]:
    if setting("RADIX_STORAGE_MODE", "local") == "supabase":
        rows = _remote(
            user,
            "GET",
            params={
                "owner": f"eq.{user.owner}",
                "kind": f"eq.{kind}",
                "id": f"eq.{record_id}",
                "select": "payload",
            },
        )
        value = rows[0]["payload"] if rows else None
    else:
        with _db() as db:
            row = db.execute(
                "SELECT payload FROM records WHERE owner=? AND kind=? AND id=?", (user.owner, kind, record_id)
            ).fetchone()
        value = _payload(row[0]) if row else None
    if value is None:
        raise AppError("NOT_FOUND", "Record not found or not owned by this user", 404)
    return value


def save(user: Identity, kind: str, payload: dict[str, Any], expected: int | None = None):
    record_id = payload["id"]
    revision = 1 if expected is None else expected + 1
    payload = {**payload, "revision": revision}
    if setting("RADIX_STORAGE_MODE", "local") == "supabase":
        row = {
            "owner": user.owner,
            "kind": kind,
            "id": record_id,
            "revision": revision,
            "payload": payload,
            "updated_at": now(),
        }
        if expected is None:
            _remote(user, "POST", json=row)
        else:
            rows = _remote(
                user,
                "PATCH",
                params={
                    "owner": f"eq.{user.owner}",
                    "kind": f"eq.{kind}",
                    "id": f"eq.{record_id}",
                    "revision": f"eq.{expected}",
                },
                json=row,
            )
            if not rows:
                raise AppError("REVISION_CONFLICT", "Record changed; reload before saving", 409)
    else:
        with _db() as db:
            try:
                if expected is None:
                    db.execute(
                        "INSERT INTO records VALUES (?,?,?,?,?,?)",
                        (user.owner, kind, record_id, revision, json.dumps(payload), now()),
                    )
                else:
                    cursor = db.execute(
                        "UPDATE records SET revision=?,payload=?,updated_at=? WHERE owner=? AND kind=? AND id=? AND revision=?",
                        (revision, json.dumps(payload), now(), user.owner, kind, record_id, expected),
                    )
                    if not cursor.rowcount:
                        raise AppError("REVISION_CONFLICT", "Record changed; reload before saving", 409)
            except sqlite3.IntegrityError:
                raise AppError("REVISION_CONFLICT", "Record already exists", 409) from None
    return payload


def delete(user: Identity, kind: str, record_id: str):
    get(user, kind, record_id)
    if setting("RADIX_STORAGE_MODE", "local") == "supabase":
        _remote(
            user,
            "DELETE",
            params={"owner": f"eq.{user.owner}", "kind": f"eq.{kind}", "id": f"eq.{record_id}"},
        )
    else:
        with _db() as db:
            db.execute("DELETE FROM records WHERE owner=? AND kind=? AND id=?", (user.owner, kind, record_id))


def invalidate_receipts(user: Identity):
    # Conservative deletion on personal-data changes avoids stale personal evidence in receipts.
    for receipt in list_records(user, "receipt"):
        delete(user, "receipt", receipt["id"])
