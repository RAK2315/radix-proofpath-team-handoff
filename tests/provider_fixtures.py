"""Controlled fake provider output. Never presented as live inference evidence."""


def proposal(quote="Python project", name="Python", category="COD"):
    return {
        "company": None,
        "role": None,
        "name": None,
        "email": None,
        "skills": [
            {
                "key": "s1",
                "skill_name": name,
                "normalized_name": name,
                "category_code": category,
                "evidence": quote,
                "source_page": 1,
                "confidence": "medium",
                "claim_basis": "explicit",
                "negated_or_conflicting": False,
            }
        ],
        "requirement_groups": [],
        "education": [],
        "projects": [],
        "experience": [],
        "certifications": [],
        "internships": [],
        "hackathons": [],
        "achievements": [],
        "warnings": [],
    }
