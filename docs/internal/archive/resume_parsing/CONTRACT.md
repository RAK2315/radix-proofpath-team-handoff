# Resume contract

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Authority: [Pydantic](../shared/contracts/models.py), [OpenAPI](../shared/contracts/openapi.json), [generated TS](../shared/contracts/generated.ts). Full valid synthetic output: [resume.json](../docs/examples/resume.json). Example UUIDs are not preseeded workspace IDs.

- `POST /api/resumes/extract`: multipart file and optional hosted_consent=false.
- `GET /api/resumes` or `/api/resumes/{id}`: owned records.
- `PATCH /api/resumes/{id}`: full Extraction plus expected revision and reviewed status.
- `DELETE /api/resumes/{id}`: delete extraction/receipts; delete the original separately under Data & privacy.

Output has source_type=resume, company/role null, source filename, skills, name/email, education/projects/experience/certifications, sections/document ID and parser/model/prompt versions. Missing facts stay empty. Confidence high/medium/low describes extraction, never ability. All claims remain unverified. Every document claim carries source_document_id and an exact quote; PDF page starts at 1, DOCX page is null.

File limits match JD ingestion: PDF/DOCX, 10 MB, 50 PDF pages, 120,000 text characters and 40 MB expanded DOCX. Unsupported extension is 415; corrupt/scanned/encrypted input or fabricated quotes are 422; oversized is 413; stale revision is 409. Invalid example: a document quote not found in its claimed page is rejected. No hypothetical claims can be reviewed into actual extraction.

Profile Builder imports only reviewed output into a draft. Mutations need X-ProofPath-Client; Supabase-auth mode also needs a verified Bearer token.

## Pre-submission audit update

Extraction additionally includes internships, hackathons and achievements arrays, input_method and claim_status on each skill (claimed|needs_review). This is review status, not independent verification; all verification_status values remain unverified. Negated/conflicting mentions need review. Adding confidence or evidence never assigns a rating.
