# JD contract

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Authority: [Pydantic](../shared/contracts/models.py), [OpenAPI](../shared/contracts/openapi.json), [generated TS](../shared/contracts/generated.ts). Schema 1.0 preserves the brief fields. Full valid synthetic response: [jd.json](../docs/examples/jd.json). Its UUIDs belong to that isolated example run.

- `POST /api/jd/extract`: multipart `file`, optional `hosted_consent=false`.
- `GET /api/jd` or `/api/jd/{id}`: owned saved extractions.
- `PATCH /api/jd/{id}`: full edited Extraction, current revision, review_status=reviewed. Success increments revision.
- `DELETE /api/jd/{id}`: remove extraction/receipts; original remains until explicit deletion or expiry.

Response includes source_type=jd, source_file, company/role, skills, groups, sections, document_id and parser/model/prompt versions. Each skill has one official category or OTHER, evidence, confidence high/medium/low, unverified status and source document/page. Groups contain valid skill IDs, AND/OR, mandatory/preferred/unspecified and requires_review. Unresolved meaning cannot earn automatic coverage.

PDF/DOCX only: 10 MB, 50 PDF pages, 120,000 text characters and 40 MB expanded DOCX limit. DOCX page is null. Quotes must occur exactly in their claimed source page. Document identity and filename are server-owned.

Invalid example: `{"skill_ids":["nonexistent"]}` in a group produces 422. Unsupported extension is 415; oversized is 413; corrupt/encrypted/scanned input is 422; stale revision is 409. Hosted configuration/provider errors are explicit. All mutations require X-ProofPath-Client; authenticated mode also requires Bearer token. Skill Matching consumes this reviewed revision.

## Pre-submission audit update

Additional endpoint: POST /api/jd/extract-text accepts {"text":"Required: Python and SQL","source_name":"Pasted job description","hosted_consent":false}. Text is 15–120,000 characters (whitespace-only rejected). Output is the same Extraction with input_method=pasted_text, a private .txt source and exact evidence; ordinary file input remains input_method=file. Requirement groups add evidence and source_page. Duplicate requirement IDs are invalid. Claim status needs_review prevents unsupported automatic coverage.
