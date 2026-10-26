# ruff: noqa: E402
"""Local single-feature composition; domain code remains feature-owned."""

import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.contracts.models import CATEGORIES
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.body_limit import BodyLimitMiddleware
from shared.integrations.config import allowed_origins, public_key, setting, validate_config
from shared.integrations.documents import (
    MAX_BYTES,
    cleanup,
    original_bytes,
    persist_document,
    read_document,
    remove_document,
)
from shared.integrations.errors import AppError
from shared.integrations.examples import router as examples_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    yield


app = FastAPI(
    title="RADIX ProofPath",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if setting("RADIX_ENV") == "production" else "/docs",
    redoc_url=None if setting("RADIX_ENV") == "production" else "/redoc",
)
origins = allowed_origins()
app.add_middleware(BodyLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-ProofPath-Client"],
    expose_headers=["X-Request-ID"],
)
rate: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def protections(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    if request.method in {"POST", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in origins:
            return JSONResponse(
                {
                    "code": "ORIGIN_REJECTED",
                    "message": "Request origin is not allowed",
                    "request_id": request_id,
                },
                status_code=403,
            )
        if not request.headers.get("x-proofpath-client"):
            return JSONResponse(
                {
                    "code": "CLIENT_HEADER_REQUIRED",
                    "message": "Include X-ProofPath-Client: web (or cli)",
                    "request_id": request_id,
                },
                status_code=403,
            )
    if request.url.path.endswith(("/extract", "/extract-text")):
        client = request.client.host if request.client else "unknown"
        q = rate[client]
        while q and q[0] < time.monotonic() - 60:
            q.popleft()
        if len(q) >= 20:
            return JSONResponse(
                {
                    "code": "RATE_LIMIT",
                    "message": "Maximum 20 extraction requests per minute",
                    "request_id": request_id,
                },
                status_code=429,
            )
        q.append(time.monotonic())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(AppError)
async def app_error(request: Request, exc: AppError):
    return JSONResponse(
        {
            "code": exc.code,
            "message": exc.message,
            "request_id": request.state.request_id,
            "retryable": exc.status >= 500,
        },
        status_code=exc.status,
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(
        {
            "code": "VALIDATION_ERROR",
            "message": "Check the highlighted input fields",
            "details": details,
            "request_id": request.state.request_id,
        },
        status_code=422,
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/status")
def status():
    return {
        "storage_mode": setting("RADIX_STORAGE_MODE", "local"),
        "auth_mode": setting("RADIX_AUTH_MODE", "local"),
        "llm_configured": bool(setting("RADIX_LLM_API_KEY") or setting("GROQ_API_KEY"))
        and setting("RADIX_LLM_MODE", "auto") != "rules",
        "llm_model": setting("RADIX_LLM_MODEL", "openai/gpt-oss-20b"),
        "llm_mode": setting("RADIX_LLM_MODE", "auto"),
        "llm_provider": "Groq"
        if "api.groq.com/" in setting("RADIX_LLM_URL", "https://api.groq.com/openai/v1/chat/completions")
        else "configured provider",
        "document_storage_mode": setting("RADIX_DOCUMENT_STORAGE_MODE", "local"),
        "benchmark_configured": bool(
            (setting("RADIX_BENCHMARK_URL") or setting("SUPABASE_URL"))
            and (setting("RADIX_BENCHMARK_KEY") or public_key())
        )
        or bool(setting("RADIX_BENCHMARK_EXPORT")),
        "categories": CATEGORIES,
    }


@app.get("/api/receipts/{receipt_id}")
def receipt(receipt_id: str, user: Identity = Depends(identity)):
    cleanup(user)
    return store.get(user, "receipt", receipt_id)


@app.get("/api/documents")
def documents(user: Identity = Depends(identity)):
    cleanup(user)
    return [
        {k: v for (k, v) in d.items() if k != "content_base64"} for d in store.list_records(user, "document")
    ]


@app.get("/api/documents/{document_id}/download")
def download(document_id: str, user: Identity = Depends(identity)):
    cleanup(user)
    doc = store.get(user, "document", document_id)
    return Response(
        original_bytes(user, doc),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment"},
    )


@app.post("/api/documents", status_code=201)
def upload_document(file: UploadFile = File(...), user: Identity = Depends(identity)):
    content = file.file.read(MAX_BYTES + 1)
    filename = (file.filename or "upload").replace("\\", "/").rsplit("/", 1)[-1]
    sections = read_document(filename, content)
    document = persist_document(user, filename, content, sections)
    return {k: v for (k, v) in document.items() if k != "content_base64"}


@app.delete("/api/documents/{document_id}", status_code=204)
def delete_document(document_id: str, user: Identity = Depends(identity)):
    remove_document(user, document_id)
    return Response(status_code=204)


from importlib import import_module

from apps.api.handoff import router as handoff_router

module = setting("RADIX_MODULE", "jd_analytics")
allowed = {"jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"}
if module not in allowed:
    raise RuntimeError("Choose a valid RADIX_MODULE")
app.include_router(import_module(f"{module}.backend.router").router)
app.include_router(handoff_router)
app.include_router(examples_router)
