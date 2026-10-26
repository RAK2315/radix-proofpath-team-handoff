# Skill Matching and Career GPS — Role 5

Explain a saved candidate's fit for one reviewed JD. Mandatory output is a match score plus matched/missing skills. ProofPath adds source-linked decisions, immutable receipts and reversible Career GPS previews.

`backend/matcher.py` owns exact/alias matching and requirement coverage. `backend/scenarios.py` deep-copies inputs and calls the same matcher and Talent Check evaluator. `backend/router.py` loads owned saved revisions. `frontend/SkillMatchingPage.tsx` owns breakdowns, evidence, sliders/toggles, ranked actions and reset. Tests live in `tests/test_matching.py` and the feature component test.

Mandatory groups weigh 2; preferred/unspecified groups weigh 1. AND coverage is the matched fraction; OR is any match. Equivalent duplicate groups count once with strongest importance. Ungrouped manual skills count. Java never silently equals JavaScript. Fuzzy suggestions and mixed wording need review and earn no automatic coverage; empty JDs are unscorable.

Career GPS separates named-skill coverage from category ratings. It validates baseline profile/JD revisions and benchmark hash, computes two independent deltas and never invokes profile save. Recommendations are separate single-change projections; evidence clarification earns no invented score gain. Click Try it or reset the controls.

Backend/browser tests verify arithmetic, alternatives, aliases, ambiguity, receipts, scenario reset and unchanged saved profiles. The synthetic 4×6 JD and 4×3 company matrices pass. The original pack and real company access are unavailable. Automatic semantic equivalence, learning-time promises, saved scenarios and pairwise optimization are not claimed.

[Usage](USAGE.md) · [Contract](CONTRACT.md) · [Checklist](PLAN.md) · [Actual tests](../docs/TEST_REPORT.md)

## Pre-submission audit update

The audit added explicit handling of conflicting/negated claims and visible normalized score points per group and matched decision. Single-member AND/OR duplicates count once. Projected readiness rows identify overridden levels as hypothetical. Recommendation duplicates are removed.
