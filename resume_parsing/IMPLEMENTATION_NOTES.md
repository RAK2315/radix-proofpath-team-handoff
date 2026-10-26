# Resume Parsing — Role 2

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Turn a PDF/DOCX resume into editable skills, name/email, education, projects, experience and certifications. This implements the mandatory resume/profile handoff. ProofPath retains exact source quotes, extraction confidence and unverified claim origins separately from competency.

`backend/service.py` interprets resume sections; `backend/router.py` registers upload/review routes. `frontend/ResumeParsingPage.tsx` owns upload, field/skill correction, saved-resume selection and review. Feature checks are in `tests/test_extraction.py` and the page's component test.

Local mode uses bounded vocabulary and heading heuristics; missing facts remain empty. Hosted mode is optional, consented per upload and schema/quote-validated. Reviewed results import into Profile Builder as a draft. No ability levels are inferred. Existing manual profile fields survive unless replacement is explicitly chosen.

Two synthetic resumes in PDF/DOCX, absent fields and the reviewed import path are tested. The four organizer resumes are absent, and live provider quality is unverified. Complex multi-column layouts, unusual headings and contradictions need human/source-pack acceptance. OCR is not implemented. Originals expire on access-triggered cleanup after seven days or can be deleted under Data & privacy.

[Usage](USAGE.md) · [Contract](CONTRACT.md) · [Checklist](PLAN.md) · [Actual tests](../docs/TEST_REPORT.md)

## Pre-submission audit update

The audit corrected visual reading order for the user-supplied PDF and preserves DOCX paragraph/table ordering. Explicit internships, hackathons and achievements are now reviewable/importable. Negated or conflicting skill claims are flagged needs_review and excluded from automatic matching until reviewed. The personal CV audit is documented in ../docs/CV_AUDIT_REPORT.md.
