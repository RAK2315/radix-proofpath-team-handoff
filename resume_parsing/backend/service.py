import re

from shared.contracts.models import Extraction
from shared.integrations.config import setting
from shared.integrations.errors import AppError
from shared.integrations.extraction import hosted_extract, instruction_like, local_skills

HEADINGS = {
    "education": "education",
    "projects": "projects",
    "experience": "experience",
    "work experience": "experience",
    "internships": "internships",
    "certifications": "certifications",
    "professional experience": "experience",
    "technical projects": "projects",
    "selected projects": "projects",
    "selected work": "projects",
    "portfolio projects": "projects",
    "project experience": "projects",
    "academic qualifications": "education",
    "academic background": "education",
    "internship experience": "internships",
    "hackathons": "hackathons",
    "awards & achievements": "achievements",
    "awards and achievements": "achievements",
    "achievements": "achievements",
    "awards": "achievements",
}


def extract(sections: list[dict], filename: str, hosted: bool = False) -> Extraction:
    if hosted and setting("RADIX_LLM_MODE", "auto") != "rules":
        try:
            result = hosted_extract(
                "resume",
                sections,
                filename,
                "Extract candidate name/email, technical skill claims, education, projects, employment, internships, certifications, hackathons and achievements. Section arrays contain source quotes only. Do not invent skill levels. Empty requirement_groups; company and role null. Mark inferred skills; do not count negated mentions as positive claims.",
            )
        except AppError as error:
            if setting("RADIX_LLM_FALLBACK", "rules") != "rules":
                raise
            result = extract(sections, filename, False)
            result.llm_status = "unavailable"
            result.warnings.insert(
                0, f"Model unavailable ({error.code}). Rules-only fallback; review omissions."
            )
    else:
        text = "\n".join(s["text"] for s in sections)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        # Bound both address parts and prohibit restarting within the same long word.
        # The old unbounded local-part pattern was quadratic on documents without @.
        email = re.search(r"(?<![\w.+-])[\w.+-]{1,64}@[\w.-]{1,253}\.[A-Za-z]{2,63}(?![\w.-])", text)
        labelled_name = next(
            (
                re.sub(r"^name\s*:\s*", "", line, flags=re.I)
                for line in lines[:12]
                if re.match(r"^name\s*:", line, re.I)
            ),
            None,
        )
        candidate_name = labelled_name or next(
            (
                line
                for line in lines[:8]
                if not re.search(
                    r"(?:synthetic.*(?:test|document|resume)|curriculum vitae|^resume$|@|https?://)",
                    line,
                    re.I,
                )
            ),
            "",
        )
        result = Extraction(
            source_type="resume",
            source_file=filename,
            name=candidate_name.strip(),
            email=email[0] if email else "",
            skills=local_skills(sections, filename, "resume"),
            warnings=[
                "Limited local extraction. Review name, section boundaries and skills; no ability levels inferred."
            ],
        )
        current = None
        for line in lines[1:]:
            heading = re.sub(r"\s+", " ", line.rstrip(":")).lower()
            if heading in HEADINGS:
                current = HEADINGS[heading]
            elif heading in {
                "skills",
                "technical skills",
                "core competencies",
                "summary",
                "professional summary",
                "contact",
                "preferred roles",
                "interests",
                "hobbies",
                "languages",
                "references",
                "publications",
                "volunteering",
            }:
                current = None
            elif current:
                getattr(result, current).append(line)
        for skill in result.skills:
            if skill.evidence in "\n".join(result.projects) or all(
                any(line.strip() in p for p in result.projects)
                for line in skill.evidence.splitlines()
                if line.strip()
            ):
                skill.evidence_type = "project_mention"
        if any(s.claim_status == "needs_review" for s in result.skills):
            result.warnings.append(
                "Conflicting or negated skill mentions need review before they count toward a match."
            )
    result.sections, result.source_file, result.source_type = sections, filename, "resume"
    result.warnings.extend(dict.fromkeys(s["layout_warning"] for s in sections if s.get("layout_warning")))
    result.company = result.role = None
    if setting("RADIX_LLM_MODE", "auto") == "rules":
        result.llm_status = "rules_only"
    if any(instruction_like(s["text"]) for s in sections):
        result.warnings.append(
            "Instruction-like document text is untrusted; inspect the source before accepting claims."
        )
    result.review_status = "needs_review"
    return result
