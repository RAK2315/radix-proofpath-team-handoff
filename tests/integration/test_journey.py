from fastapi.testclient import TestClient

from apps.api.main import app
from shared.contracts.models import CATEGORIES
from shared.integrations.examples import example_docx


def reviewed(client, kind, index):
    response = client.post(
        f"/api/{kind}/extract", files={"file": (f"synthetic-{kind}-{index}.docx", example_docx(kind, index))}
    )
    assert response.status_code == 200
    value = response.json()
    response = client.patch(f"/api/{kind}/{value['id']}", json={**value, "review_status": "reviewed"})
    assert response.status_code == 200
    return response.json()


def test_complete_five_module_journey_and_persistence(client):
    jd = reviewed(client, "jd", 0)
    resume = reviewed(client, "resumes", 0)
    profile = client.post(
        "/api/profiles",
        json={
            "name": resume["name"],
            "email": resume["email"],
            "skills": resume["skills"],
            "cv_file": resume["document_id"],
            "ratings": [{"category_code": c, "level": 4} for c in CATEGORIES],
        },
    ).json()
    request = {"profile_id": profile["id"], "company_id": "lab-systems", "benchmark_mode": "synthetic"}
    readiness = client.post("/api/talent-check/evaluate", json=request).json()
    assert len(readiness["skillset_gap"]) == 12 and readiness["readiness_score"] > 0
    assert readiness["benchmark_source"]["source_mode"] == "synthetic_test"
    match_request = {"profile_id": profile["id"], "jd_id": jd["id"]}
    match = client.post("/api/matching/evaluate", json=match_request).json()
    assert 0 < match["match_score"] < 100
    receipt = client.get(f"/api/receipts/{match['receipt_id']}").json()
    assert receipt["inputs"]["profile"] == profile
    assert receipt["result"]["match_score"] == match["match_score"]
    scenario = client.post(
        "/api/matching/scenarios/preview",
        json={
            **match_request,
            **request,
            "profile_revision": profile["revision"],
            "jd_revision": jd["revision"],
            "skill_overrides": ["Docker"],
            "benchmark_hash": readiness["benchmark_hash"],
        },
    ).json()
    assert scenario["match_delta"] > 0
    # A fresh API client opens the same persistent database, not in-memory state.
    with TestClient(app, headers={"X-ProofPath-Client": "test"}) as second_client:
        assert second_client.get(f"/api/profiles/{profile['id']}").json() == profile
    assert (
        client.post("/api/matching/evaluate", json=match_request).json()["match_score"]
        == match["match_score"]
    )
    profile["name"] = "Synthetic edited candidate"
    assert client.patch(f"/api/profiles/{profile['id']}", json=profile).status_code == 200
    assert client.get(f"/api/receipts/{match['receipt_id']}").status_code == 404


def test_synthetic_two_candidate_two_job_matrix(client):
    jobs = [reviewed(client, "jd", index) for index in range(2)]
    candidates = [reviewed(client, "resumes", index) for index in range(2)]
    scores = []
    for candidate in candidates:
        profile = client.post(
            "/api/profiles", json={"name": candidate["name"], "skills": candidate["skills"]}
        ).json()
        scores.append(
            [
                client.post(
                    "/api/matching/evaluate", json={"profile_id": profile["id"], "jd_id": jd["id"]}
                ).json()["match_score"]
                for jd in jobs
            ]
        )
    assert scores[0][0] > scores[1][0]
    assert scores[0] != scores[1]
    assert all(0 <= value <= 100 for row in scores for value in row)


def test_missing_real_source_is_explicit(client):
    response = client.get("/api/talent-check/companies")
    assert response.status_code == 503
    assert response.json()["code"] == "BENCHMARK_NOT_CONFIGURED"
    assert client.get("/api/health").json()["status"] == "ok"


def test_request_protection_and_safe_errors(client):
    assert (
        client.post(
            "/api/profiles", json={"name": "Synthetic"}, headers={"Origin": "https://untrusted.invalid"}
        ).status_code
        == 403
    )
    with TestClient(app) as other:
        assert other.post("/api/profiles", json={"name": "Synthetic"}).status_code == 403
    response = client.post("/api/profiles", json={"name": "", "secret_extra": "private-value"})
    assert response.status_code == 422 and "private-value" not in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
