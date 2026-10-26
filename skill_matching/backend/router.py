from fastapi import APIRouter, Depends

from shared.contracts.models import (
    EvaluationRequest,
    Extraction,
    MatchingResult,
    Profile,
    ScenarioRequest,
    ScenarioResult,
)
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import cleanup
from shared.integrations.errors import AppError
from shared.integrations.receipts import record
from skill_matching.backend import matcher, scenarios
from talent_check.backend import benchmark_repository as benchmarks

router = APIRouter(prefix="/api/matching", tags=["Skill Matching"])


def inputs(request, user):
    cleanup(user)
    if not request.jd_id:
        raise AppError("JD_REQUIRED", "Choose one specific JD")
    return Profile.model_validate(store.get(user, "profile", request.profile_id)), Extraction.model_validate(
        store.get(user, "jd", request.jd_id)
    )


@router.post("/evaluate", response_model=MatchingResult)
def evaluate(request: EvaluationRequest, user: Identity = Depends(identity)):
    profile, jd = inputs(request, user)
    result = matcher.evaluate(profile, jd)
    return record(
        user,
        "matching",
        {"profile": profile.model_dump(mode="json"), "jd": jd.model_dump(mode="json")},
        result,
    )


@router.post("/scenarios/preview", response_model=ScenarioResult)
def preview(request: ScenarioRequest, user: Identity = Depends(identity)):
    profile, jd = inputs(request, user)
    bundle = benchmarks.load(request.benchmark_mode) if request.company_id else None
    return scenarios.preview(profile, jd, request, bundle)
