import httpx
import pytest

from shared.integrations import documents, store
from shared.integrations.auth import Identity
from shared.integrations.config import allowed_origins, validate_config
from shared.integrations.errors import AppError
from shared.integrations.object_storage import object_request
from shared.integrations.quota import reserve_hosted


def test_production_fails_closed(monkeypatch):
    monkeypatch.setenv("RADIX_ENV", "production")
    with pytest.raises(RuntimeError, match="Supabase auth"):
        validate_config()
    monkeypatch.setenv("RADIX_AUTH_MODE", "supabase")
    monkeypatch.setenv("RADIX_STORAGE_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "synthetic-public")
    with pytest.raises(RuntimeError, match="object storage"):
        validate_config()
    monkeypatch.setenv("RADIX_DOCUMENT_STORAGE_MODE", "supabase")
    monkeypatch.setenv("RADIX_ALLOWED_ORIGINS", "https://synthetic.vercel.app,https://preview.synthetic.test")
    validate_config()
    assert len(allowed_origins()) == 2
    monkeypatch.setenv("RADIX_ALLOWED_ORIGINS", "https://*.vercel.app")
    with pytest.raises(RuntimeError, match="exact HTTPS"):
        validate_config()


def test_object_storage_uses_user_jwt_and_blocks_other_owner(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_synthetic")
    user = Identity("owner-a", "user-token")

    def request(method, url, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer user-token"
        assert kwargs["headers"]["apikey"] == "sb_publishable_synthetic"
        assert "/proofpath-documents/owner-a/" in url
        return httpx.Response(200, content=b"synthetic", request=httpx.Request(method, url))

    monkeypatch.setattr("shared.integrations.object_storage.httpx.request", request)
    assert object_request(user, "GET", "owner-a/doc/original") == b"synthetic"
    with pytest.raises(AppError):
        object_request(user, "GET", "owner-b/doc/original")
    with pytest.raises(AppError):
        object_request(user, "GET", "owner-a/../doc/original")


def test_object_upload_metadata_failure_compensates(monkeypatch, user):
    monkeypatch.setenv("RADIX_DOCUMENT_STORAGE_MODE", "supabase")
    calls = []
    monkeypatch.setattr(documents, "object_request", lambda u, m, p, c=None: calls.append(m))

    def fail(*args, **kwargs):
        raise AppError("STORAGE_UNAVAILABLE", "synthetic outage", 503)

    monkeypatch.setattr(store, "save", fail)
    with pytest.raises(AppError):
        documents.persist_document(user, "synthetic.pdf", b"synthetic", [])
    assert calls == ["POST", "DELETE"]


def test_remote_original_has_no_base64_and_delete_removes_object(monkeypatch, user):
    monkeypatch.setenv("RADIX_DOCUMENT_STORAGE_MODE", "supabase")
    calls = []
    monkeypatch.setattr(documents, "object_request", lambda u, m, p, c=None: calls.append(m) or b"synthetic")
    record = documents.persist_document(user, "synthetic.pdf", b"synthetic", [])
    assert "content_base64" not in record and record["object_path"].startswith(user.owner + "/")
    assert documents.original_bytes(user, record) == b"synthetic"
    documents.remove_document(user, record["id"])
    assert calls == ["POST", "GET", "DELETE"] and store.list_records(user, "document") == []


def test_quota_must_succeed_before_hosted_call(monkeypatch):
    monkeypatch.setenv("RADIX_AUTH_MODE", "supabase")
    monkeypatch.setenv("RADIX_LLM_API_KEY", "synthetic-key")
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")

    def limited(url, **kwargs):
        assert kwargs["json"]["p_tokens"] > 8192
        return httpx.Response(400, text="QUOTA_EXCEEDED", request=httpx.Request("POST", url))

    monkeypatch.setattr("shared.integrations.quota.httpx.post", limited)
    with pytest.raises(AppError) as error:
        reserve_hosted(Identity("owner", "jwt"), [{"text": "synthetic text"}], True)
    assert error.value.code == "EXTRACTION_QUOTA"


def test_cors_preflight_and_body_envelope(client):
    result = client.options(
        "/api/jd/extract",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,x-proofpath-client,content-type",
        },
    )
    assert result.status_code == 200
    assert result.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    denied = client.options(
        "/api/jd/extract",
        headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"},
    )
    assert denied.status_code == 400 and "access-control-allow-origin" not in denied.headers
    assert client.post("/api/documents", content=b"x" * (11 * 1024 * 1024 + 1)).status_code == 413
