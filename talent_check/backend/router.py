from typing import Literal

from fastapi import APIRouter, Depends

from shared.contracts.models import EvaluationRequest, Profile, ReadinessResult
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import cleanup
from shared.integrations.errors import AppError
from shared.integrations.receipts import record
from talent_check.backend import benchmark_repository as benchmarks
from talent_check.backend.scoring import evaluate

router = APIRouter(prefix="/api/talent-check", tags=["Talent Check"])


@router.get("/companies")
def companies(
    mode: Literal["real", "synthetic"] = "real", refresh: bool = False, user: Identity = Depends(identity)
):
    bundle = benchmarks.load("synthetic" if mode == "synthetic" else "real", refresh)
    return {
        "companies": [{"id": c["id"], "name": c["name"]} for c in bundle["companies"]],
        "source": {k: v for k, v in bundle.items() if k != "companies"},
    }


@router.get("/benchmark-status")
def status(user: Identity = Depends(identity)):
    try:
        bundle = benchmarks.load()
        return {
            "available": True,
            "source_mode": bundle["source_mode"],
            "company_count": len(bundle["companies"]),
            "columns": bundle.get("columns", []),
            "fetched_at": bundle["fetched_at"],
        }
    except AppError as exc:
        return {"available": False, "code": exc.code, "message": exc.message}


@router.post("/evaluate", response_model=ReadinessResult)
def check(request: EvaluationRequest, user: Identity = Depends(identity)):
    cleanup(user)
    if not request.company_id:
        raise AppError("COMPANY_REQUIRED", "Select a company")
    profile = Profile.model_validate(store.get(user, "profile", request.profile_id))
    bundle = benchmarks.load(request.benchmark_mode)
    result = evaluate(profile, benchmarks.select(bundle, request.company_id), bundle)
    return record(
        user, "readiness", {"profile": profile.model_dump(mode="json"), "benchmark": bundle}, result
    )
