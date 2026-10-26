from apps.api.main import app
from shared.contracts.models import Skill
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.examples import example_docx


def test_roundtrip_all_sections_and_revision(client, profile):
    payload = profile.model_dump(mode="json")
    cv = client.post("/api/documents", files={"file": ("synthetic-cv.docx", example_docx("resumes", 0))})
    assert cv.status_code == 201 and "content_base64" not in cv.json()
    payload["cv_file"] = cv.json()["id"]
    assert client.get(f"/api/documents/{payload['cv_file']}/download").status_code == 200
    for field in [
        "education",
        "projects",
        "experience",
        "internships",
        "hackathons",
        "certifications",
        "preferred_roles",
    ]:
        payload[field] = [f"Synthetic {field}"]
    created = client.post("/api/profiles", json=payload)
    assert created.status_code == 201
    loaded = client.get(f"/api/profiles/{profile.id}").json()
    assert loaded == created.json()
    changed = client.patch(f"/api/profiles/{profile.id}", json={**loaded, "name": "Synthetic changed"})
    assert changed.json()["revision"] == 2
    assert client.patch(f"/api/profiles/{profile.id}", json=loaded).status_code == 409
    assert client.delete(f"/api/profiles/{profile.id}").status_code == 204
    assert client.get(f"/api/profiles/{profile.id}").status_code == 404


def test_other_owner_cannot_read_edit_delete(client, profile, user):
    store.save(user, "profile", profile.model_dump(mode="json"))
    app.dependency_overrides[identity] = lambda: Identity("synthetic-owner-b")
    try:
        assert client.get(f"/api/profiles/{profile.id}").status_code == 404
        assert (
            client.patch(f"/api/profiles/{profile.id}", json=profile.model_dump(mode="json")).status_code
            == 409
        )
        assert client.delete(f"/api/profiles/{profile.id}").status_code == 404
        assert client.get("/api/profiles").json() == []
    finally:
        app.dependency_overrides.clear()


def test_resume_import_preserves_manual_edits_and_unknowns(client, profile):
    resume = client.post(
        "/api/resumes/extract", files={"file": ("synthetic.docx", example_docx("resumes", 0))}
    ).json()
    request = {"resume_id": resume["id"], "profile": profile.model_dump(mode="json")}
    assert client.post("/api/profiles/import-resume", json=request).status_code == 422
    resume = client.patch(f"/api/resumes/{resume['id']}", json={**resume, "review_status": "reviewed"}).json()
    result = client.post("/api/profiles/import-resume", json=request).json()
    assert result["name"] == profile.name
    assert result["cv_file"] == resume["document_id"] and result["projects"]
    assert result["ratings"] == request["profile"]["ratings"]
    assert client.post("/api/profiles", json=result).status_code == 201
    client.delete(f"/api/documents/{resume['document_id']}")
    after = client.get(f"/api/profiles/{profile.id}").json()
    assert after["cv_file"] is None and after["skills"] == []


def test_actual_profile_rejects_hypothetical_or_unowned_source(client, profile):
    profile.skills = [Skill(skill_name="Python", category_code="COD", source_type="hypothetical")]
    assert client.post("/api/profiles", json=profile.model_dump(mode="json")).status_code == 422
    profile.skills[0].source_type = "document"
    assert client.post("/api/profiles", json=profile.model_dump(mode="json")).status_code == 422
