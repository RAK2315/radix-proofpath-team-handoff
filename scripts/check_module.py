"""Execute one real feature API independently, in a fresh temporary database."""

import argparse
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check(module):
    with TemporaryDirectory(prefix="radix-module-check-") as temporary:
        os.environ.update(
            RADIX_MODULE=module,
            RADIX_ENV="development",
            RADIX_AUTH_MODE="local",
            RADIX_STORAGE_MODE="local",
            RADIX_DOCUMENT_STORAGE_MODE="local",
            RADIX_DATA_DIR=temporary,
            RADIX_LLM_MODE="rules",
            RADIX_LLM_API_KEY="",
            GROQ_API_KEY="",
            RADIX_ALLOWED_ORIGINS="",
        )
        from fastapi.testclient import TestClient

        from apps.api.standalone import app

        with TestClient(app, headers={"X-ProofPath-Client": "handoff-check"}) as client:

            def call(method, path, **kwargs):
                result = client.request(method, "/api" + path, **kwargs)
                result.raise_for_status()
                return result.json() if result.content else None

            context = call("POST", "/handoff/seed")
            candidate = context["profiles"][0]
            jd = context["jds"][0]
            resume = context["resumes"][0]
            if module in {"jd_analytics", "resume_parsing"}:
                kind = "jd" if module == "jd_analytics" else "resumes"
                filename = (
                    "junior-data-engineer-jd-SYNTHETIC.docx" if kind == "jd" else "mira-cv-SYNTHETIC.pdf"
                )
                value = call(
                    "POST",
                    f"/{kind}/extract",
                    files={"file": (filename, (ROOT / "demo/final" / filename).read_bytes())},
                )
                assert value["skills"] and value["review_status"] == "needs_review"
                assert value["llm_status"] == "rules_only"
                reviewed = call(
                    "PATCH", f"/{kind}/{value['id']}", json={**value, "review_status": "reviewed"}
                )
                assert reviewed["revision"] == 2
                assert call("GET", f"/{kind}/{value['id']}")["document_id"]
                if kind == "jd":
                    assert len(value["requirement_groups"]) == 5
                    pasted = call(
                        "POST",
                        "/jd/extract-text",
                        json={"text": "Required: Python and SQL", "hosted_consent": False},
                    )
                    assert len(pasted["skills"]) == 2
                else:
                    assert len(value["skills"]) == 6 and value["projects"] and value["internships"]
                assert (
                    client.post(
                        f"/api/{kind}/extract", files={"file": ("invalid.pdf", b"not a PDF")}
                    ).status_code
                    == 422
                )
                detail = (
                    "fresh upload, source claims, review revision, save/reload and corrupt-file rejection"
                )
            elif module == "profile_builder":
                draft = call(
                    "POST",
                    "/profiles/import-resume",
                    json={"resume_id": resume["id"], "profile": {"name": "Synthetic module test"}},
                )
                assert all(r["level"] is None for r in draft["ratings"])
                saved = call("POST", "/profiles", json=draft)
                assert call("GET", f"/profiles/{saved['id']}") == saved
                updated = call(
                    "PATCH",
                    f"/profiles/{saved['id']}",
                    json={**saved, "preferred_roles": ["Synthetic Data Engineer"]},
                )
                assert updated["revision"] == 2
                assert client.patch(f"/api/profiles/{saved['id']}", json=saved).status_code == 409
                call("DELETE", f"/profiles/{saved['id']}")
                assert client.get(f"/api/profiles/{saved['id']}").status_code == 404
                detail = (
                    "reviewed import, twelve null ratings, create/load/update/delete and stale-save rejection"
                )
            elif module == "talent_check":
                request = {
                    "profile_id": candidate["id"],
                    "company_id": "lab-data",
                    "benchmark_mode": "synthetic",
                }
                result = call("POST", "/talent-check/evaluate", json=request)
                assert result["readiness_score"] == 74.9 and len(result["skillset_gap"]) == 12
                assert call("POST", "/talent-check/evaluate", json=request)["readiness_score"] == 74.9
                assert (
                    client.post(
                        "/api/talent-check/evaluate", json={**request, "company_id": "missing"}
                    ).status_code
                    == 404
                )
                assert call("GET", "/talent-check/benchmark-status")["available"] is False
                detail = (
                    "74.9 synthetic score, twelve rows, deterministic repeat and unavailable official source"
                )
            else:
                request = {"profile_id": candidate["id"], "jd_id": jd["id"]}
                baseline = call("POST", "/matching/evaluate", json=request)
                assert baseline["match_score"] == 75
                scenario = {
                    **request,
                    "profile_revision": candidate["revision"],
                    "jd_revision": jd["revision"],
                    "company_id": "lab-data",
                    "benchmark_mode": "synthetic",
                    "skill_overrides": ["Docker"],
                    "category_overrides": {"SQL": 9},
                }
                projected = call("POST", "/matching/scenarios/preview", json=scenario)
                assert projected["projected_match"]["match_score"] == 87.5
                assert projected["projected_readiness"]["readiness_score"] == 79.5
                reset = call(
                    "POST",
                    "/matching/scenarios/preview",
                    json={**scenario, "skill_overrides": [], "category_overrides": {}},
                )
                assert reset["projected_match"]["match_score"] == 75
                assert call("GET", "/handoff/context")["profiles"][0] == candidate
                assert (
                    client.post(
                        "/api/matching/scenarios/preview", json={**scenario, "profile_revision": 999}
                    ).status_code
                    == 409
                )
                detail = "75 -> 87.5 match, 79.5 projected readiness, reset, identical saved profile and stale rejection"
            print(f"PASS {module}: {detail}; rules-only synthetic input; no network/provider calls")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "module",
        choices=["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"],
    )
    check(parser.parse_args().module)
