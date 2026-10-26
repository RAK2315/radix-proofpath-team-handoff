import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from apps.api.main import app
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import cleanup, persist_document
from shared.integrations.errors import AppError
from shared.integrations.examples import example_docx
from shared.integrations.extraction import hosted_extract


def test_hosted_response_grounding_retry_and_forced_provenance(monkeypatch):
    monkeypatch.setenv("RADIX_LLM_API_KEY", "synthetic-key")
    monkeypatch.setenv("RADIX_LLM_MODEL", "synthetic-model")
    calls = []

    def respond(url, **kwargs):
        calls.append(kwargs["json"])
        quote = "Fabricated claim" if len(calls) == 1 else "Python project"
        from tests.provider_fixtures import proposal

        extracted = proposal(quote=quote)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(extracted)}}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr("shared.integrations.llm.httpx.post", respond)
    result = hosted_extract("resume", [{"page": 1, "text": "Python project"}], "synthetic.pdf")
    assert len(calls) == 2
    assert result.skills[0].source_type == "document"
    assert result.skills[0].source_file == "synthetic.pdf"
    assert "untrusted data" in calls[0]["messages"][0]["content"]


def test_provider_failure_does_not_silently_fabricate(monkeypatch):
    monkeypatch.setenv("RADIX_LLM_API_KEY", "synthetic-key")
    monkeypatch.setenv("RADIX_LLM_MODEL", "synthetic-model")

    def unavailable(*args, **kwargs):
        raise httpx.ConnectError("synthetic failure")

    monkeypatch.setattr("shared.integrations.llm.httpx.post", unavailable)
    with pytest.raises(AppError) as error:
        hosted_extract("resume", [{"page": 1, "text": "Python project"}], "synthetic.pdf")
    assert error.value.code == "LLM_UNAVAILABLE"


def test_expired_document_cleanup_and_two_user_document_receipt_access(client, user):
    document = persist_document(
        user, "synthetic.docx", example_docx("resumes", 0), [{"page": None, "text": "Python project"}]
    )
    document["created_at"] = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    store.save(user, "document", document, document["revision"])
    app.dependency_overrides[identity] = lambda: Identity("synthetic-owner-b")
    try:
        assert client.get(f"/api/documents/{document['id']}/download").status_code == 404
        assert client.delete(f"/api/documents/{document['id']}").status_code == 404
        assert client.get("/api/documents").json() == []
    finally:
        app.dependency_overrides.clear()
    cleanup(user)
    assert store.list_records(user, "document") == []


def test_openapi_snapshot_matches_runtime():
    from pathlib import Path

    assert json.loads(Path("shared/contracts/openapi.json").read_text(encoding="utf-8")) == app.openapi()
