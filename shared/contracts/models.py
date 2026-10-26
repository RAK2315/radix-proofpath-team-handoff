"""Canonical versioned contracts. Competency and extraction confidence are separate."""

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from shared.contracts.taxonomy import SKILL_FAMILIES, family_for

CATEGORIES = {
    "COD": "Coding",
    "DSA": "Data Structures & Algorithms",
    "OOD": "Object-Oriented Design",
    "APTI": "Aptitude",
    "COMM": "Communication",
    "AI": "AI",
    "CLOUD": "Cloud",
    "SQL": "SQL",
    "SWE": "Software Engineering",
    "SYSD": "System Design",
    "NETW": "Networking",
    "OS": "Operating Systems",
}
Category = Literal[
    "COD", "DSA", "OOD", "APTI", "COMM", "AI", "CLOUD", "SQL", "SWE", "SYSD", "NETW", "OS", "OTHER"
]


def uid() -> str:
    return str(uuid4())


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class Skill(Contract):
    skill_id: str = Field(default_factory=uid)
    skill_name: str = Field(min_length=1, max_length=100)
    category_code: Category
    skill_family: str = Field(default="Other", min_length=1, max_length=60)
    evidence: str = Field(default="Manual claim", max_length=3000)
    confidence: Literal["high", "medium", "low"] = "low"
    source_page: int | None = None
    source_file: str | None = None
    source_document_id: str | None = None
    source_type: Literal["document", "manual", "hypothetical"] = "manual"
    evidence_type: Literal["resume_mention", "project_mention", "jd_requirement", "manual_entry"] = (
        "manual_entry"
    )
    verification_status: Literal["unverified"] = "unverified"
    claim_status: Literal["claimed", "needs_review"] = "claimed"
    claim_basis: Literal["explicit", "inferred"] = "explicit"
    normalized_name: str | None = None
    source_start: int | None = Field(default=None, ge=0)
    source_end: int | None = Field(default=None, ge=0)

    @model_validator(mode="before")
    @classmethod
    def classify_legacy_claim(cls, data):
        if isinstance(data, dict) and "skill_family" not in data:
            data = {**data, "skill_family": family_for(data.get("skill_name", ""))}
        return data

    @field_validator("skill_family")
    @classmethod
    def known_family(cls, value):
        if value not in SKILL_FAMILIES:
            raise ValueError("Choose a supported descriptive skill family")
        return value

    @field_validator("skill_name")
    @classmethod
    def meaningful_name(cls, value):
        if not value.strip():
            raise ValueError("Enter a non-empty skill name")
        return value.strip()


class Requirement(Contract):
    requirement_id: str = Field(default_factory=uid)
    skill_ids: list[str] = Field(min_length=1)
    operator: Literal["AND", "OR"] = "AND"
    requirement_type: Literal["mandatory", "preferred", "unspecified"] = "unspecified"
    requires_review: bool = False
    evidence: str = ""
    source_page: int | None = None


class Extraction(Contract):
    schema_version: Literal["1.0"] = "1.0"
    id: str = Field(default_factory=uid)
    revision: int = Field(default=1, ge=1)
    source_type: Literal["jd", "resume"]
    source_file: str
    company: str | None = None
    role: str | None = None
    skills: list[Skill] = Field(default_factory=list, max_length=200)
    requirement_groups: list[Requirement] = Field(default_factory=list, max_length=200)
    name: str = ""
    email: str = ""
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    hackathons: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    review_status: Literal["needs_review", "reviewed"] = "needs_review"
    extraction_mode: Literal["local_limited", "hosted_llm", "manual"] = "local_limited"
    parser_version: str = "local-layout-review-1.3"
    input_method: Literal["file", "pasted_text"] = "file"
    model_version: str | None = None
    prompt_version: str | None = None
    llm_status: Literal["not_requested", "processed", "unavailable", "rules_only"] = "not_requested"
    llm_metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    document_id: str | None = None

    @model_validator(mode="after")
    def references(self):
        ids = [s.skill_id for s in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate skill IDs")
        group_ids = [group.requirement_id for group in self.requirement_groups]
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("Duplicate requirement IDs")
        for group in self.requirement_groups:
            if not set(group.skill_ids).issubset(ids) or len(set(group.skill_ids)) != len(group.skill_ids):
                raise ValueError("Requirement references missing or duplicate skills")
        return self


class TextJDRequest(Contract):
    text: str = Field(min_length=15, max_length=120000)
    source_name: str = Field(default="Pasted job description", min_length=1, max_length=120)
    hosted_consent: bool = False

    @field_validator("text")
    @classmethod
    def meaningful_text(cls, value):
        if len(value.strip()) < 15:
            raise ValueError("Paste at least 15 non-whitespace characters")
        return value


class Rating(Contract):
    category_code: str
    level: float | None = Field(default=None, ge=1, le=10)
    origin: Literal["self_reported"] = "self_reported"

    @field_validator("level", mode="before")
    @classmethod
    def numeric_not_boolean(cls, value):
        if isinstance(value, bool):
            raise ValueError("Competency must be a number or null, not boolean")
        return value

    @model_validator(mode="after")
    def valid_category(self):
        if self.category_code not in CATEGORIES:
            raise ValueError("Ratings require one of the 12 official categories")
        return self


class Profile(Contract):
    schema_version: Literal["1.0"] = "1.0"
    id: str = Field(default_factory=uid)
    revision: int = Field(default=1, ge=1)
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(default="", max_length=254)
    education: list[str] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list, max_length=200)
    hackathons: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    cv_file: str | None = None
    ratings: list[Rating] = Field(default_factory=lambda: [Rating(category_code=c) for c in CATEGORIES])

    @model_validator(mode="after")
    def valid_profile(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Enter a non-empty name")
        ids = [s.skill_id for s in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate skill IDs")
        if self.email and ("@" not in self.email or "." not in self.email.rsplit("@", 1)[1]):
            raise ValueError("Enter a valid email address or leave it empty")
        codes = [r.category_code for r in self.ratings]
        if len(codes) != 12 or set(codes) != set(CATEGORIES):
            raise ValueError("Provide exactly one rating entry for each of the 12 categories (null allowed)")
        return self


class ResumeImportRequest(Contract):
    resume_id: str
    profile: Profile
    replace_existing: bool = False


class EvaluationRequest(Contract):
    profile_id: str
    jd_id: str | None = None
    company_id: str | None = None
    benchmark_mode: Literal["real", "synthetic"] = "real"


class ScenarioRequest(EvaluationRequest):
    profile_revision: int
    jd_revision: int
    benchmark_hash: str | None = None
    category_overrides: dict[str, float] = Field(default_factory=dict)
    skill_overrides: list[str] = Field(default_factory=list, max_length=200)

    @field_validator("category_overrides", mode="before")
    @classmethod
    def no_boolean_levels(cls, value):
        if isinstance(value, dict) and any(isinstance(level, bool) for level in value.values()):
            raise ValueError("Hypothetical levels must be numbers, not booleans")
        return value

    @model_validator(mode="after")
    def valid_overrides(self):
        if any(c not in CATEGORIES or not 1 <= level <= 10 for c, level in self.category_overrides.items()):
            raise ValueError("Scenario categories require official codes and levels 1–10")
        return self


class ReadinessRow(Contract):
    category_code: str
    category_name: str
    required_level: float = Field(ge=1, le=10)
    candidate_level: float | None = Field(ge=1, le=10)
    gap: bool | None
    shortfall: float | None
    status: Literal["unknown", "below_expected", "meets_expected", "above_expected"]
    attainment: float | None
    contribution: float | None
    evidence: list[Skill]
    rating_origin: Literal["self_reported", "hypothetical"]
    recommended_action: str


class ReadinessResult(Contract):
    company: str
    company_id: str
    profile_id: str
    profile_revision: int
    skillset_gap: list[ReadinessRow] = Field(min_length=12, max_length=12)
    readiness_score: float | None = Field(ge=0, le=100)
    status: Literal["complete", "incomplete"]
    rating_completeness: int = Field(ge=0, le=12)
    evidence_coverage: int = Field(ge=0, le=12)
    rules_version: str
    benchmark_source: dict[str, Any]
    benchmark_hash: str
    methodology: str
    receipt_id: str | None = None


class MatchingResult(Contract):
    jd_source_file: str
    jd_id: str
    jd_revision: int
    profile_id: str
    profile_revision: int
    match_score: float | None = Field(ge=0, le=100)
    matched_skills: list[dict[str, Any]]
    missing_skills: list[dict[str, Any]]
    ambiguous_matches: list[dict[str, Any]]
    contributions: list[dict[str, Any]]
    rules_version: str
    status: Literal["unscorable", "provisional", "complete"]
    methodology: str
    receipt_id: str | None = None


class ScenarioResult(Contract):
    hypothetical: Literal[True]
    baseline_match: MatchingResult
    projected_match: MatchingResult
    baseline_readiness: ReadinessResult | None
    projected_readiness: ReadinessResult | None
    match_delta: float | None
    readiness_delta: float | None
    recommendations: list[dict[str, Any]]
    profile_revision: int
    notice: str
