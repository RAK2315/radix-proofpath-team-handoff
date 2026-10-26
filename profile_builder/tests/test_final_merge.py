from profile_builder.backend.service import import_resume
from shared.contracts.models import Extraction, Profile, ResumeImportRequest, Skill
from skill_matching.backend.matcher import evaluate


def test_import_does_not_hide_new_conflicting_evidence_for_existing_claim():
    profile = Profile(
        name="Synthetic", skills=[Skill(skill_name="Python", category_code="COD", source_type="manual")]
    )
    resume = Extraction(
        source_type="resume",
        source_file="synthetic.txt",
        review_status="reviewed",
        skills=[
            Skill(
                skill_name="Python",
                category_code="COD",
                evidence="No Python experience",
                claim_status="needs_review",
            )
        ],
    )
    merged = import_resume(ResumeImportRequest(resume_id=resume.id, profile=profile), resume)
    jd = Extraction(
        source_type="jd",
        source_file="synthetic.txt",
        review_status="reviewed",
        skills=[Skill(skill_name="Python", category_code="COD")],
    )
    assert evaluate(merged, jd)["status"] == "provisional"
    assert evaluate(merged, jd)["match_score"] == 0
    assert merged.skills[0] == profile.skills[0]  # preserve original claim and its origin
    assert any(s.evidence == "No Python experience" for s in merged.skills)
    again = import_resume(ResumeImportRequest(resume_id=resume.id, profile=merged), resume)
    assert again.skills == merged.skills
