# Exact JD Analytics contract

Read `CONTRACT.md`, `request-example.json`, and the full current `response-example.json` here.
Canonical types: `../shared/contracts/models.py`; generated API: `../shared/contracts/openapi.json`.
The response model is `Extraction`; `id`, revisions, source IDs and ownership come from the running API.
The examples are synthetic snapshots; their IDs do not exist in your new local database.
Use the IDs returned after uploading/saving, or the local fixture loader.
Resume upload is multipart; its request-example describes fields rather than a JSON upload body.

All mutations use `X-ProofPath-Client: web` (or cli). Cloud calls additionally use the signed-in user's JWT.
Numeric competency is null or 1-10, never extraction confidence. Company synthetic values are never official.
Use `GET /docs` on the local API for interactive request/response schemas.
