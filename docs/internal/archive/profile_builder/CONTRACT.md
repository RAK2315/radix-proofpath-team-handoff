# Profile contract

Authority: [Pydantic](../shared/contracts/models.py), [OpenAPI](../shared/contracts/openapi.json), [generated TS](../shared/contracts/generated.ts). Full valid response: [profile.json](../docs/examples/profile.json). IDs are example-run-specific.

- `POST /api/profiles`: create (201). A complete minimal valid request is `{"name":"Synthetic Candidate","email":"candidate@example.test"}`; omitted fields/default ratings are filled.
- `GET /api/profiles` or `/api/profiles/{id}`: owned list/load.
- `PATCH /api/profiles/{id}`: complete Profile with current revision; increments revision.
- `DELETE /api/profiles/{id}`: deletes profile and invalidates receipts.
- `POST /api/profiles/import-resume`: `{resume_id,profile,replace_existing:false}` returns a merged draft without saving. Profile must have a valid non-empty name; UI substitutes the reviewed name when blank.
- `POST /api/documents`: multipart direct CV attachment; set returned id as cv_file.

Profile contains name/email, education, skills, hackathons, internships, certifications, preferred_roles, projects, experience, cv_file, ID/revision and exactly twelve ratings. Each rating has official category_code, null or 1–10 level and origin=self_reported. Unknown is null, not zero. Document claims require an owned source_document_id and matching quote; hypothetical claims cannot be saved.

Invalid request `{"name":" ","ratings":[{"category_code":"OTHER","level":0}]}` is 422. Invalid email/source claims are rejected; missing/unowned records return 404, duplicate create or stale update 409. Mutations need X-ProofPath-Client and auth mode requires Bearer token. Talent Check and Matching consume the same saved revision. No client-supplied owner is accepted.

## Pre-submission audit update

Profile additionally contains achievements: string[]. Imported claim_status is retained; a needs_review claim cannot satisfy matching automatically. Explicit review never changes any category rating. Competency booleans are rejected. Storage outages are sanitized 503 errors; remote duplicate/stale conflicts preserve 409 semantics.
