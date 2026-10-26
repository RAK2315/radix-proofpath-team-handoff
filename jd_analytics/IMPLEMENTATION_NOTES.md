# JD Analytics — Role 1

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Upload a PDF/DOCX JD, review its required skills and hand a saved revision to Skill Matching. This implements the mandatory JD/category handoff. ProofPath adds source quotes, review provenance and explicit importance/alternative groups.

`backend/service.py` interprets shared document text; `backend/router.py` registers generic upload/review plumbing. `frontend/JDAnalyticsPage.tsx` owns the page; `RequirementReview.tsx` edits groups. Backend tests are in `tests/test_extraction.py`; component tests are beside the page.

Local extraction uses a bounded vocabulary. It identifies company/role when labelled, maps skills and groups same-line requirements. Mixed AND/OR wording remains unresolved until a person edits/confirms the group. Hosted structured extraction is implemented with schema/quote validation and one repair attempt. It requires server configuration and per-upload consent.

The UI supports upload, category/name corrections, company/role edits, source inspection, group importance/operator/members and reviewed save/load. Ungrouped manual skills count as individual requirements. Sources remain unverified claims; confidence is not competency.

Two synthetic JDs in both formats, invalid files, evidence grounding, mixed wording and the matching handoff are tested. The organizer's six JDs and a live model are unavailable. Implicit requirements and unfamiliar terms need human review; no OCR or broad layout-quality guarantee is claimed.

[Usage](USAGE.md) · [Contract](CONTRACT.md) · [Checklist](PLAN.md) · [Actual tests](../docs/TEST_REPORT.md)

## Pre-submission audit update

Pasted JDs are now supported alongside file upload. The private original text remains downloadable. Required/preferred headings and repeated mentions preserve their strongest importance and source quote; employer/title metadata is excluded. Requirement-group source links and normalized contribution points are inspectable.
