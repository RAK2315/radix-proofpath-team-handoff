"""Reusable HTTP plumbing only; feature extraction remains module owned."""

from collections.abc import Callable

from fastapi import APIRouter, Depends, File, Form, UploadFile

from shared.contracts.models import Extraction, uid
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import MAX_BYTES, cleanup, persist_document, read_document
from shared.integrations.errors import AppError
from shared.integrations.extraction import validate_evidence
from shared.integrations.quota import reserve_hosted


def extraction_router(prefix: str, kind: str, extractor: Callable) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[kind])

    @router.get("", response_model=list[Extraction])
    def listing(user: Identity = Depends(identity)):
        cleanup(user)
        return store.list_records(user, kind)

    @router.post("/extract", response_model=Extraction)
    def upload(
        file: UploadFile = File(...), hosted_consent: bool = Form(False), user: Identity = Depends(identity)
    ):
        content = file.file.read(MAX_BYTES + 1)
        filename = (file.filename or "upload").replace("\\", "/").rsplit("/", 1)[-1]
        sections = read_document(filename, content)
        reserve_hosted(user, sections, hosted_consent)
        result = extractor(sections, filename, hosted_consent)
        result.id = uid()
        document = persist_document(user, filename, content, sections)
        result.document_id = document["id"]
        for skill in result.skills:
            skill.source_document_id = document["id"]
        return store.save(user, kind, result.model_dump(mode="json"))

    @router.get("/{record_id}", response_model=Extraction)
    def load(record_id: str, user: Identity = Depends(identity)):
        cleanup(user)
        return store.get(user, kind, record_id)

    @router.patch("/{record_id}", response_model=Extraction)
    def review(record_id: str, extraction: Extraction, user: Identity = Depends(identity)):
        cleanup(user)
        previous = store.get(user, kind, record_id)
        if extraction.id != record_id or extraction.source_type != kind:
            raise AppError("ID_MISMATCH", "Extraction identity cannot change")
        if extraction.document_id != previous["document_id"]:
            raise AppError("SOURCE_MISMATCH", "Source document cannot change")
        extraction.sections = previous["sections"]
        extraction.source_file = previous["source_file"]
        extraction.extraction_mode = previous["extraction_mode"]
        extraction.input_method = previous.get("input_method", "file")
        extraction.parser_version = previous.get("parser_version", "local-vocabulary-1.0")
        extraction.model_version = previous.get("model_version")
        extraction.prompt_version = previous.get("prompt_version")
        extraction.llm_status = previous.get("llm_status", "not_requested")
        extraction.llm_metadata = previous.get("llm_metadata", {})
        for skill in extraction.skills:
            if skill.source_type == "document":
                skill.source_document_id = previous["document_id"]
                skill.source_file = previous["source_file"]
        validate_evidence(extraction, extraction.sections)
        result = store.save(user, kind, extraction.model_dump(mode="json"), extraction.revision)
        store.invalidate_receipts(user)
        return result

    @router.delete("/{record_id}", status_code=204)
    def remove(record_id: str, user: Identity = Depends(identity)):
        store.delete(user, kind, record_id)
        store.invalidate_receipts(user)

    return router
