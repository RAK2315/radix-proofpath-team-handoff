import pytest
from pydantic import ValidationError

from shared.contracts.models import CATEGORIES, Extraction, Profile, Rating, ScenarioRequest, Skill


def test_category_contract():
    assert len(CATEGORIES) == 12
    assert Skill(skill_name="Power BI", category_code="OTHER").category_code == "OTHER"
    with pytest.raises(ValidationError):
        Rating(category_code="OTHER", level=5)
    with pytest.raises(ValidationError):
        Skill(skill_name="Python", category_code="INVALID")


@pytest.mark.parametrize("level", [0, 11, float("nan"), float("inf")])
def test_invalid_levels(level):
    with pytest.raises(ValidationError):
        Rating(category_code="COD", level=level)


def test_unknown_not_zero():
    profile = Profile(name="Synthetic")
    assert len(profile.ratings) == 12 and all(r.level is None for r in profile.ratings)
    with pytest.raises(ValidationError):
        Profile(name=" ")
    with pytest.raises(ValidationError):
        Profile(name="Synthetic", ratings=[Rating(category_code="COD")] * 12)


def test_reference_and_confidence_validation():
    with pytest.raises(ValidationError):
        Extraction(
            source_type="jd", source_file="synthetic.pdf", requirement_groups=[{"skill_ids": ["missing"]}]
        )
    with pytest.raises(ValidationError):
        Skill(skill_name="Python", category_code="COD", confidence="verified")
    with pytest.raises(ValidationError):
        ScenarioRequest(
            profile_id="p", jd_id="j", profile_revision=1, jd_revision=1, category_overrides={"OTHER": 5}
        )
