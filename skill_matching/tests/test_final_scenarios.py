from copy import deepcopy
from itertools import product

import pytest
from pydantic import ValidationError

from jd_analytics.backend.service import extract as extract_jd
from resume_parsing.backend.service import extract as extract_resume
from scripts.evaluation_documents import cases, render
from shared.contracts.models import CATEGORIES, Profile, Rating, ScenarioRequest
from shared.integrations.documents import read_document
from skill_matching.backend.matcher import evaluate
from skill_matching.backend.scenarios import preview
from talent_check.backend.benchmark_repository import load
from talent_check.backend.scoring import evaluate as readiness


def demo_inputs():
    fixture = {case["id"]: case for case in cases()}
    jd = extract_jd(
        read_document("synthetic.docx", render(fixture["jd-demo-data"], "docx")), "synthetic.docx"
    )
    jd.review_status = "reviewed"
    resume = extract_resume(
        read_document("synthetic.pdf", render(fixture["resume-demo-mira"], "pdf")), "synthetic.pdf"
    )
    profile = Profile(
        name="Synthetic Mira",
        skills=resume.skills,
        ratings=[Rating(category_code=code, level=4) for code in CATEGORIES],
    )
    return profile, jd


def test_scenario_grid_same_engines_bounded_deterministic_and_reversible():
    profile, jd = demo_inputs()
    original = deepcopy(profile.model_dump())
    bundle = load("synthetic")
    company = next(c for c in bundle["companies"] if c["id"] == "lab-data")
    for names, level in product(
        [[], ["Docker"], ["AWS"], ["Docker", "AWS"], ["AWS", "GCP"], ["Docker", "AWS", "GCP"]], [1, 4, 9, 10]
    ):
        request = ScenarioRequest(
            profile_id=profile.id,
            jd_id=jd.id,
            profile_revision=profile.revision,
            jd_revision=jd.revision,
            company_id=company["id"],
            benchmark_mode="synthetic",
            skill_overrides=names,
            category_overrides={"SQL": level},
        )
        result = preview(profile, jd, request, bundle)
        assert result == preview(profile, jd, request, bundle)
        assert result["baseline_match"] == evaluate(profile, jd)
        assert result["baseline_readiness"] == readiness(profile, company, bundle)
        assert 0 <= result["projected_match"]["match_score"] <= 100
        assert 0 <= result["projected_readiness"]["readiness_score"] <= 100
        assert profile.model_dump() == original
        assert result["projected_match"]["match_score"] >= result["baseline_match"]["match_score"]
        points = sum(g["score_contribution"] for g in result["projected_match"]["contributions"])
        assert round(points, 1) == result["projected_match"]["match_score"]
    empty = ScenarioRequest(profile_id=profile.id, jd_id=jd.id, profile_revision=1, jd_revision=1)
    reset = preview(profile, jd, empty, None)
    assert reset["match_delta"] == 0


@pytest.mark.parametrize("level", [0, 11, float("nan"), float("inf"), True])
def test_invalid_hypothetical_level_is_rejected(level):
    with pytest.raises(ValidationError):
        ScenarioRequest(
            profile_id="synthetic",
            jd_id="synthetic",
            profile_revision=1,
            jd_revision=1,
            category_overrides={"SQL": level},
        )
