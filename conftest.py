# ruff: noqa: E402
import io
import os

import pytest
from docx import Document
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

# Tests must not inherit production mode or inference credentials from a developer's .env.
# Set before importing the app; dotenv does not override existing environment variables.
for name, value in {
    "RADIX_ENV": "development",
    "RADIX_AUTH_MODE": "local",
    "RADIX_STORAGE_MODE": "local",
    "RADIX_DOCUMENT_STORAGE_MODE": "local",
    "RADIX_ALLOWED_ORIGIN": "http://127.0.0.1:5173",
    "RADIX_ALLOWED_ORIGINS": "",
    "RADIX_LLM_API_KEY": "",
    "GROQ_API_KEY": "",
}.items():
    os.environ[name] = value

from apps.api.main import app, rate
from shared.contracts.models import CATEGORIES, Profile, Rating
from shared.integrations.auth import Identity
from talent_check.backend.benchmark_repository import _cache


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("RADIX_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("RADIX_STORAGE_MODE", "local")
    monkeypatch.setenv("RADIX_AUTH_MODE", "local")
    for name in (
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "RADIX_BENCHMARK_URL",
        "RADIX_BENCHMARK_KEY",
        "RADIX_BENCHMARK_EXPORT",
        "RADIX_LLM_API_KEY",
        "RADIX_LLM_MODEL",
        "RADIX_LLM_URL",
        "GROQ_API_KEY",
        "SUPABASE_PUBLISHABLE_KEY",
        "RADIX_ENV",
        "RADIX_DOCUMENT_STORAGE_MODE",
        "RADIX_LLM_MODE",
        "RADIX_LLM_FALLBACK",
        "RADIX_LLM_TIMEOUT_SECONDS",
        "RADIX_LLM_MAX_OUTPUT_TOKENS",
    ):
        monkeypatch.delenv(name, raising=False)
    _cache.clear()
    rate.clear()


@pytest.fixture
def client():
    with TestClient(app, headers={"X-ProofPath-Client": "test"}) as connection:
        yield connection


@pytest.fixture
def user():
    return Identity("synthetic-owner-a")


@pytest.fixture
def profile():
    return Profile(
        name="Synthetic Candidate",
        email="candidate@example.test",
        ratings=[Rating(category_code=c, level=4) for c in CATEGORIES],
    )


def docx_bytes(lines):
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()


def pdf_bytes(lines):
    stream = io.BytesIO()
    document = canvas.Canvas(stream)
    for index, line in enumerate(lines):
        document.drawString(40, 790 - 20 * index, line)
    document.save()
    return stream.getvalue()
