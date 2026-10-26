from shared.contracts.models import Extraction, Profile, Requirement, ScenarioRequest, Skill
from skill_matching.backend.matcher import evaluate
from skill_matching.backend.scenarios import preview
from talent_check.backend.benchmark_repository import load
from talent_check.backend.scoring import evaluate as readiness


def test_conflicting_claim_is_provisional_not_automatic_match():
    skill = Skill(skill_name="Java", category_code="COD")
    jd = Extraction(source_type="jd", source_file="synthetic.txt", skills=[skill], review_status="reviewed")
    profile = Profile(
        name="Synthetic",
        skills=[
            Skill(
                skill_name="Java",
                category_code="COD",
                claim_status="needs_review",
                evidence="No Java experience",
            )
        ],
    )
    result = evaluate(profile, jd)
    assert result["match_score"] == 0 and result["status"] == "provisional"
    assert result["ambiguous_matches"][0]["decision_type"] == "unresolved"


def test_single_member_and_or_duplicates_count_once():
    skill = Skill(skill_name="Python", category_code="COD")
    jd = Extraction(
        source_type="jd",
        source_file="synthetic.txt",
        skills=[skill],
        requirement_groups=[
            Requirement(skill_ids=[skill.skill_id], operator="AND"),
            Requirement(skill_ids=[skill.skill_id], operator="OR"),
        ],
    )
    assert len(evaluate(Profile(name="Synthetic"), jd)["contributions"]) == 1


def test_more_evidence_or_confidence_never_changes_readiness(profile):
    bundle = load("synthetic")
    company = bundle["companies"][0]
    baseline = readiness(profile, company, bundle)
    profile.skills = [
        Skill(
            skill_name="SQL",
            category_code="SQL",
            source_type="manual",
            confidence="high",
            evidence="Self-reported claim",
        )
    ]
    manual = readiness(profile, company, bundle)
    assert manual["readiness_score"] == baseline["readiness_score"] and manual["evidence_coverage"] == 0
    profile.skills[0].source_type = "document"
    documented = readiness(profile, company, bundle)
    assert (
        documented["readiness_score"] == baseline["readiness_score"] and documented["evidence_coverage"] == 1
    )


def test_projected_levels_are_explicitly_hypothetical(profile):
    jd = Extraction(
        source_type="jd", source_file="synthetic.txt", skills=[Skill(skill_name="SQL", category_code="SQL")]
    )
    request = ScenarioRequest(
        profile_id=profile.id,
        jd_id=jd.id,
        profile_revision=1,
        jd_revision=1,
        company_id="lab-systems",
        category_overrides={"COD": 8},
    )
    result = preview(profile, jd, request, load("synthetic"))
    assert result["projected_readiness"]["skillset_gap"][0]["rating_origin"] == "hypothetical"
    assert result["baseline_readiness"]["skillset_gap"][0]["rating_origin"] == "self_reported"
    assert (
        sum(g["score_contribution"] for g in result["projected_match"]["contributions"])
        == result["projected_match"]["match_score"]
    )
