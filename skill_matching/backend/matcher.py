import re
from difflib import get_close_matches
from typing import Any

from shared.contracts.models import Extraction, Profile, Requirement

RULES_VERSION = "match-1.3-incomplete-extraction-disclosure"
ALIASES = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "nodejs": "node.js",
    "structured query language": "sql",
    "ml": "machine learning",
    "oop": "object-oriented design",
    "sklearn": "scikit-learn",
    "huggingface": "hugging face",
}


def canonical(name: str) -> str:
    value = re.sub(r"\s+", " ", name.strip().lower())
    return ALIASES.get(value, value)


def evaluate(profile: Profile, jd: Extraction) -> dict:
    uncertain = {canonical(s.skill_name) for s in profile.skills if s.claim_status == "needs_review"}
    candidate = {
        canonical(s.skill_name): s
        for s in profile.skills
        if s.claim_status == "claimed" and canonical(s.skill_name) not in uncertain
    }
    skills = {s.skill_id: s for s in jd.skills}
    groups = list(jd.requirement_groups)
    covered = {sid for group in groups for sid in group.skill_ids}
    # A manually added skill is still a requirement, even before grouping it.
    groups += [
        Requirement(requirement_id=f"atomic-{s.skill_id}", skill_ids=[s.skill_id])
        for s in jd.skills
        if s.skill_id not in covered
    ]
    # For duplicate groups retain the strongest reviewed importance, independent of order.
    groups.sort(key=lambda g: g.requirement_type != "mandatory")
    seen: set = set()
    contributions: list[dict[str, Any]] = []
    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for group in groups:
        members = {canonical(skills[sid].skill_name): sid for sid in group.skill_ids}
        names = tuple(sorted(members))
        signature = (group.operator if len(names) > 1 else "AND", names)
        if signature in seen:
            continue
        seen.add(signature)
        decisions: list[dict[str, Any]] = []
        for sid in members.values():
            need = skills[sid]
            if group.evidence:
                need = need.model_copy(update={"evidence": group.evidence, "source_page": group.source_page})
            name = canonical(need.skill_name)
            unresolved = group.requires_review or need.claim_status == "needs_review" or name in uncertain
            found = candidate.get(name) if not unresolved else None
            suggestions = get_close_matches(name, list(candidate), n=1, cutoff=0.78) if not found else []
            if name in uncertain:
                suggestions = [name]
            decision = {
                "requirement_id": group.requirement_id,
                "skill_name": need.skill_name,
                "category_code": need.category_code,
                "matched": found is not None,
                "requirement_type": group.requirement_type,
                "jd_evidence": need.model_dump(mode="json"),
                "candidate_evidence": found.model_dump(mode="json") if found else None,
                "decision_type": "unresolved"
                if unresolved
                else "exact"
                if found and found.skill_name.lower() == need.skill_name.lower()
                else "alias"
                if found
                else "unresolved"
                if suggestions
                else "missing",
                "reason": "Conflicting claim or ambiguous requirement; review the source before scoring"
                if unresolved
                else f"Matched {found.skill_name} via normalized name/alias"
                if found
                else "No equivalent reviewed skill claim found",
                "suggested_review": suggestions,
            }
            decision["recommended_action"] = (
                "Review ambiguous wording or equivalence before assuming a capability gap"
                if unresolved or suggestions
                else "Maintain capability and clarify supporting evidence"
                if found
                else f"Review source coverage for {need.skill_name}; demonstrate existing ability or develop it if needed"
            )
            decisions.append(decision)
        hits = sum(d["matched"] for d in decisions)
        coverage = float(bool(hits)) if group.operator == "OR" else hits / len(decisions)
        weight = 2 if group.requirement_type == "mandatory" else 1
        for decision in decisions:
            if decision["matched"]:
                matched.append(decision)
            elif not (group.operator == "OR" and hits):
                missing.append(decision)
                if decision["suggested_review"] or decision["decision_type"] == "unresolved":
                    ambiguous.append(decision)
        contributions.append(
            {
                "requirement_id": group.requirement_id,
                "operator": group.operator,
                "requirement_type": group.requirement_type,
                "skills": [d["skill_name"] for d in decisions],
                "weight": weight,
                "coverage": coverage,
                "weighted_contribution": weight * coverage,
                "requires_review": group.requires_review,
                "member_count": len(decisions),
                "matched_count": hits,
            }
        )
    total = sum(g["weight"] for g in contributions)
    for group_result in contributions:
        group_result["score_contribution"] = round(100 * group_result["weighted_contribution"] / total, 4)
    groups_by_id = {group["requirement_id"]: group for group in contributions}
    for decision in matched + missing:
        group_result = groups_by_id[decision["requirement_id"]]
        divisor = (
            group_result["member_count"]
            if group_result["operator"] == "AND"
            else max(group_result["matched_count"], 1)
        )
        decision["score_contribution"] = (
            round(100 * group_result["weight"] / total / divisor, 4) if decision["matched"] else 0.0
        )
    return {
        "jd_source_file": jd.source_file,
        "jd_id": jd.id,
        "jd_revision": jd.revision,
        "profile_id": profile.id,
        "profile_revision": profile.revision,
        "match_score": round(100 * sum(g["weighted_contribution"] for g in contributions) / total, 1)
        if total
        else None,
        "matched_skills": matched,
        "missing_skills": missing,
        "ambiguous_matches": ambiguous,
        "contributions": contributions,
        "rules_version": RULES_VERSION,
        "status": "unscorable"
        if not total
        else "provisional"
        if ambiguous
        or jd.review_status != "reviewed"
        or any(w.startswith("Requirement not fully parsed;") for w in jd.warnings)
        else "complete",
        "methodology": "Weighted extracted requirement-group coverage: mandatory 2, preferred/unspecified 1 (team heuristic). AND fraction, OR any. Unparsed requirement warnings keep the result provisional until reviewed. Confidence is not competency; named technologies require equivalent claims.",
    }
