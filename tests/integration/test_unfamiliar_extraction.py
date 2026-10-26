import pytest

from jd_analytics.backend.service import extract as extract_jd
from resume_parsing.backend.service import extract as extract_resume
from scripts.evaluation_documents import cases, render
from shared.contracts.models import Profile, Skill
from shared.integrations.documents import read_document
from shared.integrations.extraction import validate_evidence
from skill_matching.backend.matcher import evaluate


@pytest.mark.parametrize("case", cases(), ids=lambda c: c["id"])
@pytest.mark.parametrize("extension", ["pdf", "docx"])
def test_unfamiliar_documents_have_expected_reviewable_output(case, extension):
    filename = f"{case['id']}.{extension}"
    sections = read_document(filename, render(case, extension))
    result = (extract_jd if case["kind"] == "jd" else extract_resume)(sections, filename)
    expected = set(case["expected_skills"]) - set(case.get("expected_misses", []))
    assert {s.skill_name for s in result.skills} == expected
    assert {s.skill_name for s in result.skills if s.claim_status == "needs_review"} == set(
        case.get("expected_review", [])
    )
    if "expected_name" in case:
        assert result.name == case["expected_name"]
    for field, source in case.get("expected_sections", {}).items():
        assert any(source in line for line in getattr(result, field))
    if "expected_groups" in case:
        names = {s.skill_id: s.skill_name for s in result.skills}

        def group_key(g):
            return ",".join(g["skills"])

        actual = [
            {
                "skills": sorted(names[sid] for sid in g.skill_ids),
                "importance": g.requirement_type,
                "operator": g.operator,
                "review": g.requires_review,
            }
            for g in result.requirement_groups
        ]
        expected_groups = [{**g, "skills": sorted(g["skills"])} for g in case["expected_groups"]]
        assert sorted(actual, key=group_key) == sorted(expected_groups, key=group_key)
    if case["id"] == "jd-unfamiliar-tech":
        assert any("Rust" in warning for warning in result.warnings)
        assert any("Apache Arrow" in warning for warning in result.warnings)
        assert result.requirement_groups[0].requires_review
    assert all(s.verification_status == "unverified" for s in result.skills)
    validate_evidence(result, sections)


def test_an_unknown_separate_requirement_cannot_silently_become_complete():
    jd = extract_jd([{"page": None, "text": "Requirements\n- Python\n- Apache Arrow"}], "synthetic.txt")
    jd.review_status = "reviewed"
    profile = Profile(name="Synthetic", skills=[Skill(skill_name="Python", category_code="COD")])
    result = evaluate(profile, jd)
    assert result["match_score"] == 100 and result["status"] == "provisional"
    assert any("Apache Arrow" in w for w in jd.warnings)
    jd.warnings = [w for w in jd.warnings if not w.startswith("Requirement not fully parsed;")]
    assert evaluate(profile, jd)["status"] == "complete"  # explicit human acknowledgement
