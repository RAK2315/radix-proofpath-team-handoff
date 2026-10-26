from fastapi import APIRouter, Depends, Response

from profile_builder.backend.service import import_resume, validate_sources
from shared.contracts.models import Extraction, Profile, ResumeImportRequest
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import cleanup
from shared.integrations.errors import AppError

router = APIRouter(prefix="/api/profiles", tags=["Profile Builder"])


@router.get("", response_model=list[Profile])
def profiles(user: Identity = Depends(identity)):
    cleanup(user)
    return store.list_records(user, "profile")


@router.post("", response_model=Profile, status_code=201)
def create(profile: Profile, user: Identity = Depends(identity)):
    cleanup(user)
    validate_sources(profile, user)
    return store.save(user, "profile", profile.model_dump(mode="json"))


@router.post("/import-resume", response_model=Profile)
def import_preview(request: ResumeImportRequest, user: Identity = Depends(identity)):
    cleanup(user)
    resume = Extraction.model_validate(store.get(user, "resume", request.resume_id))
    return import_resume(request, resume)


@router.get("/{profile_id}", response_model=Profile)
def load(profile_id: str, user: Identity = Depends(identity)):
    cleanup(user)
    return store.get(user, "profile", profile_id)


@router.patch("/{profile_id}", response_model=Profile)
def update(profile_id: str, profile: Profile, user: Identity = Depends(identity)):
    if profile.id != profile_id:
        raise AppError("ID_MISMATCH", "Profile ID cannot change")
    cleanup(user)
    validate_sources(profile, user)
    result = store.save(user, "profile", profile.model_dump(mode="json"), profile.revision)
    store.invalidate_receipts(user)
    return result


@router.delete("/{profile_id}", status_code=204)
def remove(profile_id: str, user: Identity = Depends(identity)):
    store.delete(user, "profile", profile_id)
    store.invalidate_receipts(user)
    return Response(status_code=204)
