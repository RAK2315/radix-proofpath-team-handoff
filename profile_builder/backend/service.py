"""Pure resume merge and validation of persisted candidate claims."""

from shared.contracts.models import Extraction, Profile, ResumeImportRequest, uid
from shared.integrations import store
from shared.integrations.auth import Identity
from shared.integrations.errors import AppError
from shared.integrations.extraction import validate_evidence


def import_resume(request: ResumeImportRequest, resume: Extraction) -> Profile:
    if resume.review_status != "reviewed":
        raise AppError("REVIEW_REQUIRED", "Review and save the resume before importing")
    merged = request.profile.model_copy(deep=True)
    for field in (
        "name",
        "email",
        "education",
        "projects",
        "experience",
        "certifications",
        "internships",
        "hackathons",
        "achievements",
    ):
        if request.replace_existing or not getattr(merged, field):
            setattr(merged, field, getattr(resume, field))
    names = {s.skill_name.strip().casefold() for s in merged.skills}
    for skill in resume.skills:
        name = skill.skill_name.strip().casefold()
        existing = [s for s in merged.skills if s.skill_name.strip().casefold() == name]
        conflicting_new = (
            skill.claim_status == "needs_review"
            and existing
            and not any(s.claim_status == "needs_review" for s in existing)
        )
        if name not in names or conflicting_new:
            # Keep the original claim and the new conflicting source visible. An import
            # must not discard a negated mention just because the name already exists.
            if any(s.skill_id == skill.skill_id for s in merged.skills):
                skill = skill.model_copy(update={"skill_id": uid()})
            merged.skills.append(skill.model_copy(deep=True))
            names.add(name)
    merged.cv_file = resume.document_id
    return merged


def validate_sources(profile: Profile, user: Identity):
    if profile.cv_file:
        store.get(user, "document", profile.cv_file)
    for skill in profile.skills:
        if skill.source_type == "hypothetical":
            raise AppError("HYPOTHETICAL_CLAIM", "Scenario claims cannot be saved to actual profiles")
        if skill.source_type == "document":
            if not skill.source_document_id:
                raise AppError("SOURCE_REQUIRED", "Document claims require an owned source document")
            document = store.get(user, "document", skill.source_document_id)
            validate_evidence(
                Extraction(source_type="resume", source_file=document["source_file"], skills=[skill]),
                document["sections"],
            )
            skill.source_file = document["source_file"]
