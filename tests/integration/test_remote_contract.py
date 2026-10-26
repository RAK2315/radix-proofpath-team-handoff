import httpx
from starlette.requests import Request

from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.errors import AppError


def test_mocked_supabase_pagination_owner_token_and_revision(monkeypatch):
    monkeypatch.setenv("RADIX_STORAGE_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "synthetic-public-key")
    user = Identity("synthetic-owner", "synthetic-user-token")
    calls = []

    def respond(method, url, **kwargs):
        calls.append((method, url, kwargs))
        assert kwargs["headers"]["Authorization"] == "Bearer synthetic-user-token"
        assert url.endswith("/proofpath_records")
        params = kwargs.get("params", {})
        if method == "GET":
            assert params["owner"] == "eq.synthetic-owner"
            return httpx.Response(
                200,
                json=[{"payload": {"id": "synthetic-record"}}] if params["offset"] == 0 else [],
                request=httpx.Request(method, url),
            )
        assert params["revision"] == "eq.1"
        return httpx.Response(200, json=[kwargs["json"]], request=httpx.Request(method, url))

    monkeypatch.setattr(store.httpx, "request", respond)
    assert len(store.list_records(user, "profile")) == 1
    assert len(calls) == 2
    assert store.save(user, "profile", {"id": "synthetic-record"}, expected=1)["revision"] == 2


def test_auth_verifies_token_with_server_not_claimed_owner(monkeypatch):
    monkeypatch.setenv("RADIX_AUTH_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")

    def verify(url, **kwargs):
        assert url.endswith("/auth/v1/user")
        assert kwargs["headers"]["Authorization"] == "Bearer synthetic-user-token"
        return httpx.Response(200, json={"id": "verified-synthetic-user"}, request=httpx.Request("GET", url))

    monkeypatch.setattr("shared.integrations.auth.httpx.get", verify)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer synthetic-user-token")]})
    assert identity(request).owner == "verified-synthetic-user"


def test_local_auth_rejects_non_loopback():
    request = Request({"type": "http", "headers": [], "client": ("192.0.2.1", 1234)})
    try:
        identity(request)
    except AppError as error:
        assert error.code == "LOCAL_ONLY"
    else:
        raise AssertionError("Local mode must not accept remote clients")
