from fastapi import Depends

from jd_analytics.backend.service import extract
from shared.contracts.models import Extraction, TextJDRequest, uid
from shared.integrations import store
from shared.integrations.auth import Identity, identity
from shared.integrations.documents import persist_document
from shared.integrations.extraction_routes import extraction_router
from shared.integrations.quota import reserve_hosted

router = extraction_router("/api/jd", "jd", extract)


@router.post("/extract-text", response_model=Extraction)
def paste(request: TextJDRequest, user: Identity = Depends(identity)):
    filename = request.source_name.replace("\\", "/").rsplit("/", 1)[-1].strip() or "Pasted job description"
    if not filename.lower().endswith(".txt"):
        filename += ".txt"
    sections = [{"page": None, "text": request.text}]
    reserve_hosted(user, sections, request.hosted_consent)
    result = extract(sections, filename, request.hosted_consent)
    result.id = uid()
    document = persist_document(user, filename, request.text.encode("utf-8"), sections, "pasted_text")
    result.document_id = document["id"]
    result.input_method = "pasted_text"
    for skill in result.skills:
        skill.source_document_id = document["id"]
    return store.save(user, "jd", result.model_dump(mode="json"))
