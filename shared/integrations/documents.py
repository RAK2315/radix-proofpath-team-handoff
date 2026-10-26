import base64
import hashlib
import io
import re
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import PurePath
from typing import Any

from docx import Document
from pypdf import PdfReader

from shared.contracts.models import uid
from shared.integrations import store
from shared.integrations.auth import Identity
from shared.integrations.config import setting
from shared.integrations.errors import AppError
from shared.integrations.object_storage import object_request

MAX_BYTES = 10 * 1024 * 1024


def reading_order(text: str) -> tuple[str, bool]:
    """Linearize a conservative, heading-led two-column layout, not arbitrary tables.

    Require a stable wide gutter in at least three rows and headings on both sides.
    Complicated page layouts still need human review; retain that disclosure.
    """
    lines = text.splitlines()
    gaps = [(i, match) for i, line in enumerate(lines) for match in re.finditer(r"(?<=\S) {8,}(?=\S)", line)]
    for index, gap in gaps:
        left, right = lines[index][: gap.start()].strip(), lines[index][gap.end() :].strip()
        if not all(re.fullmatch(r"[A-Za-z][A-Za-z &/-]{2,45}", part) for part in (left, right)):
            continue
        aligned = [(i, m) for i, m in gaps if i >= index and abs(m.end() - gap.end()) <= 2]
        if len(aligned) < 3:
            continue
        split_at = gap.end()
        columns: list[list[str]] = [[], []]
        for line in lines[index:]:
            columns[0].append(line[:split_at].rstrip())
            columns[1].append(line[split_at:].strip())
        return "\n".join(lines[:index] + columns[0] + [""] + columns[1]), True
    return text, False


def read_document(filename: str, content: bytes) -> list[dict]:
    sections: list[dict[str, Any]]
    if len(content) > MAX_BYTES:
        raise AppError("FILE_TOO_LARGE", "Maximum upload size is 10 MB", 413)
    suffix = PurePath(filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise AppError("UNSUPPORTED_FILE", "Upload a PDF or DOCX file", 415)
    try:
        if suffix == ".pdf":
            if not content.startswith(b"%PDF-"):
                raise ValueError("PDF signature does not match")
            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                raise ValueError("Password-protected PDFs are unsupported")
            if len(reader.pages) > 50:
                raise ValueError("Maximum 50 pages")
            sections = []
            for i, page in enumerate(reader.pages):
                # PDF templates can write objects out of visual order; preserve displayed sections.
                text = page.extract_text(extraction_mode="layout") or page.extract_text() or ""
                text, columns = reading_order(text)
                section = {"page": i + 1, "text": text}
                if columns:
                    section["layout_warning"] = (
                        "Two-column reading order reconstructed; check section boundaries and quotes against the original PDF."
                    )
                sections.append(section)
        else:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise ValueError("Not a Word document")
                if any("vbaProject" in f.filename for f in archive.infolist()):
                    raise ValueError("Macro-enabled documents are unsupported")
                if sum(f.file_size for f in archive.infolist()) > 40 * 1024 * 1024:
                    raise ValueError("Expanded DOCX exceeds safe size")
            doc = Document(io.BytesIO(content))
            blocks: list[str] = []
            for block in doc.iter_inner_content():
                if hasattr(block, "rows"):
                    # Separate cells by a line break: joining multiline cells with a pipe
                    # attached a right-hand heading to the final left-hand paragraph.
                    for row in block.rows:
                        blocks.extend(c.text for c in row.cells)
                else:
                    blocks.append(block.text)
            text = "\n".join(blocks)
            sections = [{"page": None, "text": text}]
        text = "\n".join(s["text"] for s in sections)
        if len(text.strip()) < 15:
            raise ValueError("No readable text. Scanned PDFs need OCR, which is not enabled")
        if len(text) > 120000:
            raise ValueError("Extracted text exceeds 120,000 characters")
        return sections
    except AppError:
        raise
    except Exception as exc:
        message = str(exc) if isinstance(exc, ValueError) else "File is corrupt or unreadable"
        raise AppError("UNREADABLE_DOCUMENT", message) from None


def persist_document(
    user: Identity, filename: str, content: bytes, sections: list[dict], origin: str = "file"
):
    cleanup(user)
    safe_name = filename.replace("\\", "/").rsplit("/", 1)[-1][:150]
    document_id = uid()
    payload = {
        "id": document_id,
        "source_file": safe_name,
        "sections": sections,
        "content_hash": hashlib.sha256(content).hexdigest(),
        "origin": origin,
        "created_at": store.now(),
    }
    if setting("RADIX_DOCUMENT_STORAGE_MODE", "local") == "supabase":
        path = f"{user.owner}/{document_id}/original"
        object_request(user, "POST", path, content)
        payload["object_path"] = path
        try:
            return store.save(user, "document", payload)
        except AppError:
            object_request(user, "DELETE", path)
            raise
    payload["content_base64"] = base64.b64encode(content).decode()
    return store.save(user, "document", payload)


def original_bytes(user: Identity, document: dict) -> bytes:
    if document.get("object_path"):
        return object_request(user, "GET", document["object_path"])
    return base64.b64decode(document["content_base64"])


def remove_document(user: Identity, document_id: str):
    document = store.get(user, "document", document_id)
    if document.get("object_path"):
        object_request(user, "DELETE", document["object_path"])
    for kind in ("jd", "resume"):
        for value in store.list_records(user, kind):
            if value.get("document_id") == document_id:
                store.delete(user, kind, value["id"])
    for profile in store.list_records(user, "profile"):
        claims = [s for s in profile["skills"] if s.get("source_document_id") != document_id]
        if profile.get("cv_file") == document_id or len(claims) != len(profile["skills"]):
            profile["skills"] = claims
            if profile.get("cv_file") == document_id:
                profile["cv_file"] = None
            store.save(user, "profile", profile, profile["revision"])
    store.invalidate_receipts(user)
    # Metadata stays present until all dependent records are removed, allowing retry.
    store.delete(user, "document", document_id)


def cleanup(user: Identity):
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    for value in store.list_records(user, "document"):
        if datetime.fromisoformat(value["created_at"]) < cutoff:
            remove_document(user, value["id"])
