"""Read-only official benchmark access. Raw schema mapping is explicit/validated."""

import hashlib
import json
import math
import time
from datetime import datetime
from pathlib import Path

import httpx

from shared.contracts.models import CATEGORIES
from shared.integrations.config import ROOT, public_key, setting
from shared.integrations.errors import AppError
from shared.integrations.store import now

_cache: dict = {}
TABLE = "staging_company_skill_levels"


def digest(companies: list[dict]) -> str:
    return hashlib.sha256(json.dumps(companies, sort_keys=True).encode()).hexdigest()


def normalize_rows(rows: list[dict], mapping: dict | None = None) -> list[dict]:
    if not rows:
        raise AppError(
            "BENCHMARK_EMPTY", "No accessible benchmark records; check read grants and filters", 503
        )
    mapping = dict(mapping or {})
    if any(not isinstance(row, dict) for row in rows) or any(
        key in mapping and not isinstance(mapping[key], dict) for key in ("category_map", "wide_levels")
    ):
        raise AppError(
            "BENCHMARK_CONFIG", "Benchmark rows and nested category/wide mappings must be objects", 503
        )
    choices = {
        "company": ["company_name", "company"],
        "category": ["category_code", "skillset_code", "skill_code"],
        "level": ["required_level", "expected_level", "competency_level", "level"],
    }
    for field, candidates in choices.items():
        if field not in mapping and not (field in {"category", "level"} and "wide_levels" in mapping):
            present = [name for name in candidates if name in rows[0]]
            if len(present) != 1:
                raise AppError(
                    "BENCHMARK_SCHEMA",
                    f"Cannot unambiguously map {field}; set RADIX_BENCHMARK_MAPPING after schema inspection",
                    503,
                )
            mapping[field] = present[0]
    companies: dict[str, dict] = {}
    aliases = {name.lower(): code for code, name in CATEGORIES.items()}
    aliases.update({str(k).lower(): v for k, v in mapping.get("category_map", {}).items()})
    try:
        for row in rows:
            name = str(row[mapping["company"]]).strip()
            if not name or name == "None":
                raise ValueError("Company name missing")
            company_id = str(row[mapping["company_id"]]) if mapping.get("company_id") else name
            if not company_id.strip() or company_id == "None":
                raise ValueError("Company ID missing")
            company = companies.setdefault(company_id, {"id": company_id, "name": name, "levels": {}})
            if company["name"] != name:
                raise ValueError("Company ID has conflicting names")
            pairs = (
                [(code, row[column]) for code, column in mapping["wide_levels"].items()]
                if "wide_levels" in mapping
                else [(row[mapping["category"]], row[mapping["level"]])]
            )
            for raw_code, raw_level in pairs:
                raw = str(raw_code).strip()
                code = raw.upper() if raw.upper() in CATEGORIES else aliases.get(raw.lower())
                if code not in CATEGORIES or code in company["levels"]:
                    raise ValueError(
                        f"Unmapped or duplicate category: {raw}. Resolve role/version dimensions explicitly"
                    )
                if isinstance(raw_level, bool):
                    raise ValueError("Boolean is not a competency level")
                level = float(raw_level)
                if not math.isfinite(level) or not 1 <= level <= 10:
                    raise ValueError("Expected competency must be 1–10")
                company["levels"][code] = level
        if any(set(c["levels"]) != set(CATEGORIES) for c in companies.values()):
            raise ValueError("Every company needs exactly 12 valid category expectations")
    except (KeyError, TypeError, ValueError) as exc:
        raise AppError("BENCHMARK_INVALID", str(exc), 503) from None
    return sorted(companies.values(), key=lambda c: c["name"])


def read_source() -> dict:
    """Read rows independently of normalization so a new schema can be inspected first."""
    url = setting("RADIX_BENCHMARK_URL") or setting("SUPABASE_URL")
    key = setting("RADIX_BENCHMARK_KEY") or public_key()
    if not url or not key:
        raise AppError(
            "BENCHMARK_NOT_CONFIGURED",
            "Real company benchmarks need authorized Supabase URL/read key or a genuine export. No company levels have been invented.",
            503,
        )
    rows: list[dict] = []
    try:
        filters = json.loads(setting("RADIX_BENCHMARK_FILTER", "{}") or "{}")
        if not isinstance(filters, dict):
            raise ValueError("Filter must be an object")
        with httpx.Client(timeout=20) as client:
            offset = 0
            while True:
                headers = {
                    "apikey": key,
                    "Range-Unit": "items",
                    "Range": f"{offset}-{offset + 499}",
                    "Prefer": "count=exact",
                }
                token = setting("RADIX_BENCHMARK_ACCESS_TOKEN") or (key if not key.startswith("sb_") else "")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                response = client.get(
                    f"{url.rstrip('/')}/rest/v1/{TABLE}",
                    headers=headers,
                    params={"select": "*", **filters},
                )
                response.raise_for_status()
                batch = response.json()
                if not isinstance(batch, list):
                    raise ValueError("Unexpected table response")
                rows.extend(batch)
                total = response.headers.get("content-range", "").rsplit("/", 1)[-1]
                offset += len(batch)
                if not batch or (total.isdigit() and offset >= int(total)):
                    break
                if offset > 100000:
                    raise ValueError("Benchmark query is too broad; configure a narrower filter")
    except httpx.HTTPError:
        raise AppError(
            "BENCHMARK_UNAVAILABLE",
            "Supabase benchmark read failed; check project URL, grants, mapping and filters",
            503,
        ) from None
    except (ValueError, TypeError):
        raise AppError(
            "BENCHMARK_CONFIG", "Benchmark mapping/filter JSON or server response is invalid", 503
        ) from None
    return {"rows": rows, "project_host": url.split("://")[-1].split("/")[0]}


def fetch_live() -> dict:
    source = read_source()
    rows = source["rows"]
    try:
        mapping = json.loads(setting("RADIX_BENCHMARK_MAPPING", "{}") or "{}")
    except ValueError:
        raise AppError("BENCHMARK_CONFIG", "RADIX_BENCHMARK_MAPPING must be a JSON object", 503) from None
    if not isinstance(mapping, dict):
        raise AppError("BENCHMARK_CONFIG", "RADIX_BENCHMARK_MAPPING must be a JSON object", 503)
    companies = normalize_rows(rows, mapping)
    return {
        "companies": companies,
        "source_mode": "live",
        "source_table": TABLE,
        "fetched_at": now(),
        "project_host": source["project_host"],
        "mapping": mapping,
        "schema_version": "benchmark-1.0",
        "columns": sorted(rows[0]),
        "record_count": len(rows),
        "content_hash": digest(companies),
    }


def load_export(path: str) -> dict:
    try:
        bundle = json.loads(Path(path).read_text(encoding="utf-8"))
        if bundle["source_table"] != TABLE or bundle.get("source_mode") not in {"live", "export"}:
            raise ValueError("Export must originate from the official table")
        rows = [
            {"company": c["name"], "company_id": c["id"], "category_code": code, "required_level": level}
            for c in bundle["companies"]
            for code, level in c["levels"].items()
        ]
        companies = normalize_rows(
            rows,
            {
                "company": "company",
                "company_id": "company_id",
                "category": "category_code",
                "level": "required_level",
            },
        )
        if digest(companies) != bundle["content_hash"] or not bundle.get("fetched_at"):
            raise ValueError("Export checksum/provenance invalid")
        fetched = datetime.fromisoformat(bundle["fetched_at"].replace("Z", "+00:00"))
        if fetched.tzinfo is None:
            raise ValueError("Export timestamp must include a timezone")
        return {**bundle, "companies": companies, "source_mode": "export"}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise AppError(
            "BENCHMARK_EXPORT_INVALID", f"Cannot load validated export: {type(exc).__name__}", 503
        ) from None


def load(mode: str = "real", refresh: bool = False) -> dict:
    if mode == "synthetic":
        bundle = json.loads((ROOT / "data/synthetic/benchmarks.json").read_text(encoding="utf-8"))
        return {**bundle, "content_hash": digest(bundle["companies"])}
    if not refresh and _cache and time.monotonic() - _cache.get("time", 0) < 900:
        return _cache["bundle"]
    try:
        bundle = fetch_live()
    except AppError:
        export = setting("RADIX_BENCHMARK_EXPORT")
        if not export:
            raise
        bundle = load_export(export)
        bundle["notice"] = "Live source unavailable; using a validated exported snapshot. Check fetched_at."
    _cache.update(time=time.monotonic(), bundle=bundle)
    return bundle


def select(bundle: dict, company_id: str) -> dict:
    company = next((c for c in bundle["companies"] if c["id"] == company_id), None)
    if not company:
        raise AppError("COMPANY_NOT_FOUND", "Select a company from the current benchmark source", 404)
    return company
