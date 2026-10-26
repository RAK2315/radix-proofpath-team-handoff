import json

import httpx
import pytest

from shared.contracts.models import CATEGORIES
from shared.integrations.errors import AppError
from talent_check.backend import benchmark_repository as repository
from talent_check.backend.scoring import evaluate


def rows():
    return [
        {"company_name": "Synthetic Test Co", "category_code": code, "required_level": 8}
        for code in CATEGORIES
    ]


def test_twelve_dimensions_known_arithmetic_unknown_and_monotonic(profile):
    company = repository.normalize_rows(rows())[0]
    bundle = {"content_hash": "synthetic", "source_mode": "synthetic_test"}
    result = evaluate(profile, company, bundle)
    assert result["readiness_score"] == 50.0 and len(result["skillset_gap"]) == 12
    assert all(row["gap"] for row in result["skillset_gap"])
    profile.ratings[0].level = 8
    assert evaluate(profile, company, bundle)["readiness_score"] == 54.2
    profile.ratings[0].level = None
    unknown = evaluate(profile, company, bundle)
    assert unknown["readiness_score"] is None and unknown["skillset_gap"][0]["gap"] is None
    for rating in profile.ratings:
        rating.level = 10
    assert evaluate(profile, company, bundle)["readiness_score"] == 100


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.pop(),
        lambda r: r.append(r[0]),
        lambda r: r[0].update(required_level=None),
        lambda r: r[0].update(required_level=0),
        lambda r: r[0].update(required_level=True),
        lambda r: r[0].update(category_code="OTHER"),
        lambda r: r[0].update(required_level=float("nan")),
    ],
    ids=["missing", "duplicate", "null", "zero", "bool", "other", "nan"],
)
def test_bad_benchmarks_never_filled(mutate):
    records = rows()
    mutate(records)
    with pytest.raises(AppError):
        repository.normalize_rows(records)


def test_wide_schema_explicit_map():
    record = {"employer": "Synthetic Test Co", **{code: 7 for code in CATEGORIES}}
    result = repository.normalize_rows(
        [record], {"company": "employer", "wide_levels": {c: c for c in CATEGORIES}}
    )
    assert result[0]["levels"] == dict.fromkeys(CATEGORIES, 7)


def test_mocked_readonly_pagination(monkeypatch):
    monkeypatch.setenv("RADIX_BENCHMARK_URL", "https://synthetic.invalid")
    monkeypatch.setenv("RADIX_BENCHMARK_KEY", "synthetic-test-key")
    calls = []

    def handle(request):
        calls.append(request)
        offset = int(request.headers["range"].split("-")[0])
        batch = rows()[offset : offset + 5]
        return httpx.Response(
            200, json=batch, headers={"content-range": f"{offset}-{offset + len(batch) - 1}/12"}
        )

    real_client = httpx.Client
    monkeypatch.setattr(
        repository.httpx, "Client", lambda **kw: real_client(transport=httpx.MockTransport(handle), **kw)
    )
    result = repository.fetch_live()
    assert len(calls) == 3 and len(result["companies"][0]["levels"]) == 12
    assert all(request.method == "GET" for request in calls)


def test_export_checksum_and_no_synthetic_official_fallback(tmp_path):
    companies = repository.normalize_rows(rows())
    export = {
        "source_table": repository.TABLE,
        "source_mode": "live",
        "fetched_at": "2026-10-26T00:00:00+00:00",
        "companies": companies,
        "content_hash": repository.digest(companies),
    }
    path = tmp_path / "synthetic-test-export.json"
    path.write_text(json.dumps(export))
    assert repository.load_export(str(path))["source_mode"] == "export"
    export["companies"][0]["levels"]["COD"] = 9
    path.write_text(json.dumps(export))
    with pytest.raises(AppError):
        repository.load_export(str(path))
    with pytest.raises(AppError) as error:
        repository.load("real")
    assert error.value.code == "BENCHMARK_NOT_CONFIGURED"


def test_company_candidate_matrix(profile):
    bundle = repository.load("synthetic")
    first = [evaluate(profile, c, bundle)["readiness_score"] for c in bundle["companies"]]
    for rating in profile.ratings:
        rating.level = 8
    second = [evaluate(profile, c, bundle)["readiness_score"] for c in bundle["companies"]]
    assert len(set(first)) > 1
    assert all(a < b for a, b in zip(first, second, strict=True))
