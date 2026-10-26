# Matching and scenario contracts

Authority: [Pydantic](../shared/contracts/models.py), [OpenAPI](../shared/contracts/openapi.json), [generated TS](../shared/contracts/generated.ts). Full valid examples: [matching.json](../docs/examples/matching.json) and [scenario.json](../docs/examples/scenario.json). UUIDs are run-specific.

`POST /api/matching/evaluate` takes `{"profile_id":"CURRENT_PROFILE_ID","jd_id":"CURRENT_JD_ID"}`. MatchingResult preserves jd_source_file, match_score, matched_skills and missing_skills, and adds ambiguous_matches, contributions, status, revisions, rules_version, methodology and receipt_id. Decisions carry JD/candidate evidence, importance, reason, action and exact/alias/unresolved/missing type. Empty JD is unscorable/null. Unreviewed or unresolved input is provisional.

`POST /api/matching/scenarios/preview` adds baseline profile_revision/jd_revision, optional company_id/benchmark_mode/benchmark_hash, skill_overrides (names in that JD) and category_overrides (official codes to 1–10).

Valid shape with current IDs/revisions: `{"profile_id":"CURRENT_PROFILE_ID","jd_id":"CURRENT_JD_ID","profile_revision":1,"jd_revision":2,"company_id":"lab-systems","benchmark_mode":"synthetic","skill_overrides":["Docker"],"category_overrides":{"COD":8}}`. Capture the baseline benchmark_hash to freeze before/after comparisons.

ScenarioResult contains hypothetical=true, baseline/projected match/readiness, separate deltas, single-change recommendations and a no-profile-write notice. Missing/incomplete readiness has null values. Skills affect JD coverage; category levels affect company readiness. Evidence clarification earns no automatic score.

Invalid example: an override name outside that JD is 422. Missing JD is 422; missing/unowned inputs 404; stale revision/hash 409. Mutations require X-ProofPath-Client; authenticated mode requires verified Bearer token.

## Pre-submission audit update

Contribution groups include score_contribution (points out of 100), member_count and matched_count. Matched/missing decisions also expose score_contribution; missing/unresolved coverage contributes zero. Claim status needs_review produces provisional/unresolved results, never automatic coverage. Projected readiness uses rating_origin=hypothetical for changed levels, with actual baselines self_reported.
