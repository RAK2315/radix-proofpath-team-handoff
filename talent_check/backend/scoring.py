from shared.contracts.models import CATEGORIES, Profile

RULES_VERSION = "readiness-1.0-equal-capped"


def evaluate(profile: Profile, company: dict, bundle: dict) -> dict:
    ratings = {rating.category_code: rating.level for rating in profile.ratings}
    rows = []
    for code, label in CATEGORIES.items():
        required, candidate = company["levels"][code], ratings[code]
        known = candidate is not None
        attainment = min(candidate / required, 1) if candidate is not None else None
        evidence = [
            s.model_dump(mode="json")
            for s in profile.skills
            if s.category_code == code and s.source_type == "document" and s.claim_status == "claimed"
        ]
        rows.append(
            {
                "category_code": code,
                "category_name": label,
                "required_level": required,
                "candidate_level": candidate,
                "gap": candidate < required if known else None,
                "shortfall": max(required - candidate, 0) if known else None,
                "status": "unknown"
                if not known
                else "below_expected"
                if candidate < required
                else "above_expected"
                if candidate > required
                else "meets_expected",
                "attainment": attainment,
                "contribution": round(100 * attainment / 12, 4) if attainment is not None else None,
                "evidence": evidence,
                "rating_origin": "self_reported",
                "recommended_action": f"Assess {label} first"
                if not known
                else f"Explore improving {label} from {candidate:g} toward {required:g}"
                if candidate < required
                else "Maintain capability and add supporting evidence",
            }
        )
    complete = all(r["attainment"] is not None for r in rows)
    return {
        "company": company["name"],
        "company_id": company["id"],
        "profile_id": profile.id,
        "profile_revision": profile.revision,
        "skillset_gap": rows,
        "readiness_score": round(100 * sum(r["attainment"] for r in rows) / 12, 1) if complete else None,
        "status": "complete" if complete else "incomplete",
        "rating_completeness": sum(r["candidate_level"] is not None for r in rows),
        "evidence_coverage": sum(bool(r["evidence"]) for r in rows),
        "rules_version": RULES_VERSION,
        "benchmark_source": {
            k: bundle.get(k) for k in ["source_mode", "source_table", "fetched_at", "content_hash", "notice"]
        },
        "benchmark_hash": bundle["content_hash"],
        "methodology": "Mean of capped candidate/required attainment across all 12 categories. Self-reported levels; evidence links do not verify ability. Not an employer decision or hiring probability.",
    }
