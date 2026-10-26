# Talent Check — Role 4

Compare one saved profile with a selected company's expectations across all twelve official RADIX categories. This is a company comparison; Skill Matching handles one specific JD.

`backend/benchmark_repository.py` owns read-only Supabase pagination, observed-schema mapping, validation, caching and export fallback. `backend/scoring.py` owns pure arithmetic; `backend/router.py` exposes source/evaluation routes. `frontend/TalentCheckPage.tsx` shows all twelve aligned comparisons, filters, contribution/evidence drawers and source information. Feature tests are in `tests/test_readiness.py` and the page's component test.

Readiness is `100 × mean(min(candidate/required,1))`, rounded to one decimal. Unknown ratings remain null and block the final percentage. Shortfall and evidence coverage are separate. Every result records a benchmark hash, rule version and receipt. Career GPS calls this exact evaluator.

Real mode only uses authorized `staging_company_skill_levels` rows or a genuine retrieved export. Invalid/missing/duplicate/OTHER standards fail visibly. A 15-minute cache and manual refresh preserve source snapshots. Export writes atomically with provenance and checksum. No staging write exists.

Three explicitly invented synthetic employers support testing. Mocked read pagination, strict mapping, export checks, arithmetic, twelve dimensions and input-dependent comparisons pass. Actual Google/Microsoft/Oracle FSS records, schema, permissions and live readiness remain unverified because no URL/key/export was supplied. Synthetic tests do not complete real-data acceptance.

[Usage](USAGE.md) · [Contract](CONTRACT.md) · [Checklist](PLAN.md) · [Exact organizer setup](../docs/ORGANIZER_SETUP.md)
