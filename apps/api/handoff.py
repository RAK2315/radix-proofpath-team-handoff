"""Loopback-only synthetic fixtures for independently exercising one feature."""

import json

from fastapi import APIRouter, Depends

from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.config import ROOT, setting
from shared.integrations.documents import persist_document
from shared.integrations.errors import AppError

router = APIRouter(prefix="/api/handoff", tags=["Local synthetic handoff support"])


def local_user(user: Identity = Depends(identity)):
    if setting("RADIX_AUTH_MODE", "local") != "local" or setting("RADIX_ENV") == "production":
        raise AppError("LOCAL_ONLY", "Handoff fixtures are available only in loopback development", 403)
    return user


def context(user: Identity):
    bundle = json.loads((ROOT / "data/synthetic/benchmarks.json").read_text(encoding="utf-8"))
    return {
        "profiles": store.list_records(user, "profile"),
        "jds": store.list_records(user, "jd"),
        "resumes": store.list_records(user, "resume"),
        "companies": [{"id": c["id"], "name": c["name"]} for c in bundle["companies"]],
        "notice": "SYNTHETIC INPUTS AND BENCHMARKS - not official organizer data or fresh parsing",
    }


@router.get("/context")
def workspace(user: Identity = Depends(local_user)):
    return context(user)


@router.post("/seed")
def seed(user: Identity = Depends(local_user)):
    originals = {}
    records = {}
    for kind in ("jd", "resume"):
        value = json.loads((ROOT / f"data/synthetic/handoff/{kind}-SYNTHETIC.json").read_text())
        old_document = value["document_id"]
        # Idempotent: preserve the user's edited saved input instead of overwriting it.
        try:
            existing = store.get(user, kind, value["id"])
            originals[old_document] = existing["document_id"]
            records[kind] = existing
            continue
        except AppError as error:
            if error.code != "NOT_FOUND":
                raise
        content = (ROOT / "demo/final" / value["source_file"]).read_bytes()
        document = persist_document(user, value["source_file"], content, value["sections"])
        originals[old_document] = document["id"]
        value["document_id"] = document["id"]
        for skill in value["skills"]:
            skill["source_document_id"] = document["id"]
        records[kind] = store.save(user, kind, value)
    profile = json.loads((ROOT / "data/synthetic/handoff/profile-SYNTHETIC.json").read_text())
    try:
        store.get(user, "profile", profile["id"])
    except AppError as error:
        if error.code != "NOT_FOUND":
            raise
        profile["cv_file"] = originals[profile["cv_file"]]
        for skill in profile["skills"]:
            skill["source_document_id"] = originals[skill["source_document_id"]]
        store.save(user, "profile", profile)
    return context(user)
