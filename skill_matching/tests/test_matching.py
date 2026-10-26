import pytest

from shared.contracts.models import Extraction, Requirement, ScenarioRequest, Skill
from shared.integrations.errors import AppError
from skill_matching.backend.matcher import evaluate
from skill_matching.backend.scenarios import preview
from talent_check.backend.benchmark_repository import load


def job(names, operator="AND"):
    skills = [Skill(skill_name=name, category_code="COD") for name in names]
    return Extraction(
        source_type="jd",
        source_file="synthetic.docx",
        skills=skills,
        review_status="reviewed",
        requirement_groups=[
            Requirement(
                skill_ids=[s.skill_id for s in skills], operator=operator, requirement_type="mandatory"
            )
        ],
    )


def test_weighted_and_or_and_non_equivalence(profile):
    profile.skills = [Skill(skill_name="JS", category_code="COD")]
    jd = job(["JavaScript", "Java"])
    result = evaluate(profile, jd)
    assert result["match_score"] == 50
    assert result["matched_skills"][0]["decision_type"] == "alias"
    jd.requirement_groups[0].operator = "OR"
    assert evaluate(profile, jd)["match_score"] == 100
    assert evaluate(profile, jd)["missing_skills"] == []


def test_manual_unassigned_skills_count_and_duplicates_strongest(profile):
    profile.skills = [Skill(skill_name="Python", category_code="COD")]
    jd = job(["Python"])
    jd.requirement_groups[0].requirement_type = "preferred"
    jd.requirement_groups.append(Requirement(skill_ids=[jd.skills[0].skill_id], requirement_type="mandatory"))
    jd.skills.append(Skill(skill_name="SQL", category_code="SQL"))
    result = evaluate(profile, jd)
    assert result["match_score"] == 66.7
    assert len(result["contributions"]) == 2


def test_empty_and_ambiguous_are_honest(profile):
    assert evaluate(profile, Extraction(source_type="jd", source_file="empty.docx"))["status"] == "unscorable"


def test_close_match_requires_review(profile):
    profile.skills = [Skill(skill_name="Pythonn", category_code="COD")]
    result = evaluate(profile, job(["Python"]))
    assert result["status"] == "provisional" and result["match_score"] == 0


def test_scenario_same_engines_pure_and_reset(profile):
    profile.skills = [Skill(skill_name="Python", category_code="COD")]
    jd = job(["Python", "SQL"])
    bundle = load("synthetic")
    request = ScenarioRequest(
        profile_id=profile.id,
        jd_id=jd.id,
        profile_revision=1,
        jd_revision=1,
        company_id="lab-systems",
        benchmark_mode="synthetic",
        benchmark_hash=bundle["content_hash"],
        skill_overrides=["SQL"],
    )
    original = profile.model_dump(mode="json")
    result = preview(profile, jd, request, bundle)
    assert result["match_delta"] == 50 and result["readiness_delta"] == 0
    assert result["projected_match"]["match_score"] == 100
    assert profile.model_dump(mode="json") == original
    request.skill_overrides = []
    request.category_overrides = {"COD": 8}
    result = preview(profile, jd, request, bundle)
    assert result["match_delta"] == 0 and result["readiness_delta"] > 0
    request.category_overrides = {}
    assert preview(profile, jd, request, bundle)["match_delta"] == 0
    assert profile.model_dump(mode="json") == original


@pytest.mark.parametrize(
    "change,code",
    [
        ({"profile_revision": 2}, "STALE_BASELINE"),
        ({"benchmark_hash": "changed"}, "STALE_BENCHMARK"),
        ({"skill_overrides": ["not in JD"]}, "INVALID_SCENARIO_SKILL"),
    ],
)
def test_stale_or_invalid_scenario(profile, change, code):
    jd = job(["Python"])
    request = (
        ScenarioRequest(profile_id=profile.id, jd_id=jd.id, profile_revision=1, jd_revision=1, **change)
        if "profile_revision" not in change
        else ScenarioRequest(profile_id=profile.id, jd_id=jd.id, jd_revision=1, **change)
    )
    with pytest.raises(AppError) as error:
        preview(profile, jd, request, load("synthetic"))
    assert error.value.code == code
