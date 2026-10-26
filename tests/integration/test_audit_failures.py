import json
import sqlite3

import httpx
import pytest

from shared.integrations import store
from shared.integrations.errors import AppError


def test_sqlite_failure_is_actionable_without_private_paths(monkeypatch, user):
    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("private-path should never be reflected")

    monkeypatch.setattr(store.sqlite3, "connect", fail)
    with pytest.raises(AppError) as error:
        store.list_records(user, "profile")
    assert error.value.code == "STORAGE_UNAVAILABLE"
    assert "private-path" not in error.value.message


def test_remote_conflicts_are_not_misreported_as_outages(monkeypatch, user):
    monkeypatch.setenv("RADIX_STORAGE_MODE", "supabase")
    user.token = "synthetic-token"

    def respond(method, url, **kwargs):
        return httpx.Response(
            409, json={"message": "synthetic duplicate"}, request=httpx.Request(method, url)
        )

    monkeypatch.setattr(store.httpx, "request", respond)
    with pytest.raises(AppError) as error:
        store.save(user, "profile", {"id": "synthetic-id"})
    assert error.value.status == 409


def test_bad_benchmark_mapping_and_timestamp_are_actionable(tmp_path):
    from talent_check.backend.benchmark_repository import TABLE, load, load_export, normalize_rows

    with pytest.raises(AppError):
        normalize_rows(
            [{"company": "Synthetic", "category_code": "COD", "required_level": 5}], {"category_map": []}
        )
    bundle = load("synthetic")
    bundle.update(source_mode="export", source_table=TABLE, fetched_at="yesterday")
    path = tmp_path / "synthetic-invalid-export.json"
    path.write_text(json.dumps(bundle))
    with pytest.raises(AppError):
        load_export(str(path))


def test_empty_provider_choices_fail_with_bounded_repair(monkeypatch):
    from shared.integrations.extraction import hosted_extract

    monkeypatch.setenv("RADIX_LLM_API_KEY", "synthetic-key")
    monkeypatch.setenv("RADIX_LLM_MODEL", "synthetic-model")
    calls = []

    def respond(url, **kwargs):
        calls.append(url)
        return httpx.Response(200, json={"choices": []}, request=httpx.Request("POST", url))

    monkeypatch.setattr("shared.integrations.llm.httpx.post", respond)
    with pytest.raises(AppError) as error:
        hosted_extract("jd", [{"page": None, "text": "Required Python"}], "synthetic.txt")
    assert error.value.code == "LLM_INVALID_OUTPUT" and len(calls) == 2
