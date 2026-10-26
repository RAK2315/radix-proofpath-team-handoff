import re
from typing import Literal

from shared.contracts.models import Extraction, Requirement
from shared.integrations.config import setting
from shared.integrations.errors import AppError
from shared.integrations.extraction import hosted_extract, instruction_like, local_skills, mentions, negated

REQUIRED_HEADINGS = {
    "requirements",
    "qualifications",
    "required qualifications",
    "minimum qualifications",
    "required skills",
    "what you bring",
    "what we're looking for",
    "what we are looking for",
    "essential skills",
    "must have",
    "must-have",
}
PREFERRED_HEADINGS = {
    "preferred qualifications",
    "nice to have",
    "nice-to-have",
    "desirable skills",
    "helpful extras",
    "bonus skills",
    "preferred skills",
}
RESPONSIBILITY_HEADINGS = {"responsibilities", "key responsibilities", "what you'll do", "what you will do"}


def unrecognized_terms(line: str, skills: list) -> list[str]:
    """Surface capitalized unfamiliar names; this does not assert they are skills."""
    from shared.integrations.extraction import VOCABULARY

    remaining = line
    aliases = [
        alias
        for skill in skills
        for alias in VOCABULARY.get(skill.skill_name, ("OTHER", [skill.skill_name]))[1]
    ]
    for alias in sorted(aliases, key=len, reverse=True):
        remaining = re.sub(r"(?<!\w)" + re.escape(alias) + r"(?![\w+#])", " ", remaining, flags=re.I)
    starters = {
        "Required",
        "Preferred",
        "Must",
        "You",
        "Hands-on",
        "Comfortable",
        "Familiarity",
        "Knowledge",
        "Basic",
        "Strong",
        "Good",
        "Ability",
        "Work",
        "Implement",
        "Perform",
        "Evaluate",
        "Explore",
        "Collaborate",
        "Assist",
        "Collect",
        "Build",
        "Experience",
        "No",
        "Not",
        "Minimum",
        "Essential",
        "Bonus",
        "Optional",
    }
    return [
        m.group().strip(".-")
        for m in re.finditer(r"\b[A-Z][A-Za-z0-9+#.-]*(?: [A-Z][A-Za-z0-9+#.-]*)*", remaining)
        if m.group().strip(".-") not in starters
    ]


def scoring_lines(sections: list[dict]) -> list[tuple[str, int | None, str, str]]:
    """Separate actual requirements from title, promotional copy and eligibility text.

    Explicit qualifications take priority; responsibilities contribute only new named skills.
    Returned source lines are unchanged for evidence validation.
    """
    rows = []
    block = "unknown"
    context = "unspecified"
    structured = any(
        line.strip().lower().rstrip(":") in REQUIRED_HEADINGS | PREFERRED_HEADINGS | RESPONSIBILITY_HEADINGS
        for section in sections
        for line in section["text"].splitlines()
    )
    for section in sections:
        for raw in section["text"].splitlines():
            line = raw.strip()
            if instruction_like(line):
                continue
            heading = line.lower().rstrip(":")
            if heading in REQUIRED_HEADINGS:
                block, context = "requirements", "mandatory"
                continue
            if heading in PREFERRED_HEADINGS:
                block, context = "requirements", "preferred"
                continue
            if heading in RESPONSIBILITY_HEADINGS:
                block, context = "responsibilities", "unspecified"
                continue
            if heading in {
                "about the job",
                "about the internship",
                "about us",
                "benefits",
                "who can apply?",
                "who can apply",
                "how to apply",
            }:
                block, context = "excluded", "unspecified"
                continue
            if structured and block not in {"requirements", "responsibilities"}:
                continue
            if re.match(r"(?:company|role|job title|position|duration|work mode|stipend)\s*:", line, re.I):
                continue
            rows.append((line, section["page"], block, context))
    return sorted(rows, key=lambda row: row[2] != "requirements")


def extract(sections: list[dict], filename: str, hosted: bool = False) -> Extraction:
    if hosted and setting("RADIX_LLM_MODE", "auto") != "rules":
        try:
            result = hosted_extract(
                "jd",
                sections,
                filename,
                "Extract job company/title, required and preferred skills including unfamiliar technologies and implicit responsibilities. Preserve AND/OR logic: Python and either PyTorch or TensorFlow becomes mandatory Python AND plus a separate mandatory PyTorch OR TensorFlow group. Keep ambiguous mixtures unresolved. No resume identity or education fields.",
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
        company = re.search(r"^Company:\s*(.+)", text, re.M | re.I)
        role = re.search(r"^(?:Role|Job title|Position):\s*(.+)", text, re.M | re.I)
        standalone_role = next(
            (
                line.strip()
                for line in text.splitlines()[:8]
                if len(line.strip()) < 100
                and ":" not in line
                and re.search(
                    r"\b(?:intern|engineer|developer|analyst|scientist|designer|manager)\b", line, re.I
                )
            ),
            None,
        )
        rows = scoring_lines(sections)
        result = Extraction(
            source_type="jd",
            source_file=filename,
            company=company[1].strip() if company else None,
            role=role[1].strip() if role else standalone_role,
            skills=local_skills([{"page": page, "text": line} for line, page, _, _ in rows], filename, "jd"),
            warnings=[
                "Limited local vocabulary extraction; implicit requirements and unfamiliar technologies need manual review."
            ],
        )
        groups: dict[tuple, Requirement] = {}
        formal_names = {
            s.skill_name
            for s in result.skills
            if any(block == "requirements" and mentions(line, s.skill_name) for line, _, block, _ in rows)
        }
        for line, page, block, inherited in rows:
            if re.match(r"(?:company|role|job title|position)\s*:", line, re.I):
                continue
            skills = [
                skill
                for skill in result.skills
                if mentions(line, skill.skill_name)
                and not (block == "responsibilities" and skill.skill_name in formal_names)
            ]
            explicit: Literal["mandatory", "preferred", "unspecified"] = (
                "mandatory"
                if re.search(r"\b(?:required|must|essential|mandatory|minimum)\b", line, re.I)
                else "preferred"
                if re.search(
                    r"preferred|nice.to.have|bonus|optional|(?:is|an?)\s+(?:advantage|plus)|beneficial",
                    line,
                    re.I,
                )
                else "unspecified"
            )
            unknown = unrecognized_terms(line, skills)
            if block == "requirements" and (unknown or not skills) and line:
                result.warnings.append(
                    "Requirement not fully parsed; review/add missing members: " + line[:250]
                )
            if not skills:
                continue
            mixed = bool(re.search(r"\band\b", line, re.I) and re.search(r"\bor\b", line, re.I))
            if mixed:
                result.warnings.append("Mixed AND/OR wording requires explicit group review: " + line[:150])
            importance = explicit if explicit != "unspecified" else inherited
            group = Requirement(
                skill_ids=[s.skill_id for s in skills],
                operator="OR" if re.search(r"\bor\b", line, re.I) else "AND",
                requirement_type=importance,  # type: ignore[arg-type]
                requires_review=mixed
                or bool(unknown and block == "requirements")
                or any(negated(line, s.skill_name) for s in skills),
                evidence=line,
                source_page=page,
            )
            signature = (group.operator, tuple(sorted(group.skill_ids)))
            previous = groups.get(signature)
            if previous is None or (
                group.requirement_type == "mandatory" and previous.requirement_type != "mandatory"
            ):
                groups[signature] = group
        result.requirement_groups = list(groups.values())
    result.sections, result.source_file, result.source_type = sections, filename, "jd"
    result.warnings.extend(dict.fromkeys(s["layout_warning"] for s in sections if s.get("layout_warning")))
    if setting("RADIX_LLM_MODE", "auto") == "rules":
        result.llm_status = "rules_only"
    if any(instruction_like(s["text"]) for s in sections):
        result.warnings.append(
            "Instruction-like document text is untrusted; inspect the source before accepting claims."
        )
    result.review_status = "needs_review"
    return result
