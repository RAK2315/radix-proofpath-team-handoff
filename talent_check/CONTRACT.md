# Talent Check contract

Authority: [Pydantic](../shared/contracts/models.py), [OpenAPI](../shared/contracts/openapi.json), [generated TS](../shared/contracts/generated.ts). Complete valid response: [readiness.json](../docs/examples/readiness.json). Values are explicitly synthetic.

- `GET /api/talent-check/companies?mode=real&refresh=false`: company IDs/names and provenance. mode=synthetic is explicit.
- `GET /api/talent-check/benchmark-status`: source availability/error independently of process health.
- `POST /api/talent-check/evaluate`: `{profile_id,company_id,benchmark_mode:"real"}`.

Valid synthetic request after saving a profile: `{"profile_id":"CURRENT_PROFILE_ID","company_id":"lab-systems","benchmark_mode":"synthetic"}`. Real mode requires an actual returned company ID and authorized staging_company_skill_levels data or genuine retrieved export. No official-company constants ship.

ReadinessResult includes company, all twelve skillset_gap rows, score/null, completeness, separate evidence coverage, benchmark provenance/hash, rule version and receipt_id. Each row includes required/candidate levels, gap/null, shortfall, attainment, contribution, unverified claim links and recommended action. Unknown candidate ratings block the final percentage. Known score is 0–100; this is self-reported readiness, not one-JD fit or a hiring probability.

Invalid example: a source containing duplicate COD or only eleven categories returns 503; it is never filled. Null/boolean/out-of-range/OTHER expectations fail. No source returns BENCHMARK_NOT_CONFIGURED (503), unknown company 404, missing selection 422. Mutations need X-ProofPath-Client; auth mode needs Bearer token. [Organizer setup](../docs/ORGANIZER_SETUP.md) explains schema mapping and export provenance.
