from uuid import NAMESPACE_URL, uuid5

from shared.contracts.models import CATEGORIES, Extraction, Profile, ScenarioRequest, Skill
from shared.integrations.errors import AppError
from skill_matching.backend.matcher import evaluate as match
from talent_check.backend.benchmark_repository import select
from talent_check.backend.scoring import evaluate as readiness


def project(profile: Profile, request: ScenarioRequest) -> Profile:
    copy = profile.model_copy(deep=True)
    for rating in copy.ratings:
        if rating.category_code in request.category_overrides:
            rating.level = request.category_overrides[rating.category_code]
    for name in dict.fromkeys(request.skill_overrides):
        copy.skills.append(
            Skill(
                skill_id=str(
                    uuid5(
                        NAMESPACE_URL, f"proofpath:scenario:{profile.id}:{profile.revision}:{name.casefold()}"
                    )
                ),
                skill_name=name,
                category_code="OTHER",
                evidence="Hypothetical scenario only",
                source_type="hypothetical",
            )
        )
    return copy


def delta(after, before):
    return round(after - before, 1) if after is not None and before is not None else None


def preview(profile: Profile, jd: Extraction, request: ScenarioRequest, bundle: dict | None) -> dict:
    if profile.revision != request.profile_revision or jd.revision != request.jd_revision:
        raise AppError("STALE_BASELINE", "Profile/JD changed. Run matching again before simulating", 409)
    if bundle and request.benchmark_hash and request.benchmark_hash != bundle["content_hash"]:
        raise AppError("STALE_BENCHMARK", "Benchmark changed. Refresh the baseline before simulating", 409)
    allowed = {s.skill_name for s in jd.skills}
    if not set(request.skill_overrides).issubset(allowed):
        raise AppError("INVALID_SCENARIO_SKILL", "Hypothetical skills must come from the selected JD")
    hypothetical = project(profile, request)
    baseline_match, projected_match = match(profile, jd), match(hypothetical, jd)
    company = select(bundle, request.company_id) if bundle and request.company_id else None
    base_ready = readiness(profile, company, bundle) if company and bundle else None
    projected_ready = readiness(hypothetical, company, bundle) if company and bundle else None
    if projected_ready:
        for row in projected_ready["skillset_gap"]:
            if row["category_code"] in request.category_overrides:
                row["rating_origin"] = "hypothetical"
    recommendations = []
    seen = set()
    for item in baseline_match["missing_skills"]:
        if item["skill_name"] in seen:
            continue
        seen.add(item["skill_name"])
        if item["decision_type"] == "unresolved":
            recommendations.append(
                {
                    "type": "evidence",
                    "skill_name": item["skill_name"],
                    "action": f"Review the requirement for {item['skill_name']}",
                    "match_delta": None,
                    "readiness_delta": None,
                    "reason": item["reason"],
                }
            )
            continue
        single = request.model_copy(
            update={"category_overrides": {}, "skill_overrides": [item["skill_name"]]}
        )
        gain = delta(match(project(profile, single), jd)["match_score"], baseline_match["match_score"])
        recommendations.append(
            {
                "type": "capability",
                "skill_name": item["skill_name"],
                "category_code": item["category_code"],
                "action": f"Review and demonstrate {item['skill_name']}",
                "match_delta": gain,
                "readiness_delta": 0,
                "reason": item["jd_evidence"]["evidence"],
            }
        )
    if base_ready and company and bundle:
        for row in base_ready["skillset_gap"]:
            code = row["category_code"]
            if row["candidate_level"] is None:
                recommendations.append(
                    {
                        "type": "evidence",
                        "category_code": code,
                        "action": f"Self-assess {CATEGORIES[code]}",
                        "match_delta": None,
                        "readiness_delta": None,
                        "reason": "Unknown ability. Assess first; no automatic score gain.",
                    }
                )
            elif row["gap"]:
                single = request.model_copy(
                    update={"category_overrides": {code: row["required_level"]}, "skill_overrides": []}
                )
                gain = delta(
                    readiness(project(profile, single), company, bundle)["readiness_score"],
                    base_ready["readiness_score"],
                )
                recommendations.append(
                    {
                        "type": "capability",
                        "category_code": code,
                        "target_level": row["required_level"],
                        "action": f"Explore {CATEGORIES[code]} toward level {row['required_level']:g}",
                        "match_delta": 0,
                        "readiness_delta": gain,
                        "reason": row["recommended_action"],
                    }
                )
    return {
        "hypothetical": True,
        "baseline_match": baseline_match,
        "projected_match": projected_match,
        "baseline_readiness": base_ready,
        "projected_readiness": projected_ready,
        "match_delta": delta(projected_match["match_score"], baseline_match["match_score"]),
        "readiness_delta": delta(projected_ready["readiness_score"], base_ready["readiness_score"])
        if base_ready and projected_ready
        else None,
        "recommendations": recommendations,
        "profile_revision": profile.revision,
        "notice": "Projected changes are hypothetical. Saved profile, evidence and verification status are unchanged.",
    }
