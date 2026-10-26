# RADIX ProofPath engineering rules

The implementation is authorized. Preserve five root feature folders: jd_analytics, resume_parsing, profile_builder, talent_check, skill_matching. Each owns backend, frontend, tests and docs. apps are composition only; shared is generic infrastructure/contracts/UI.

Never invent company benchmarks or imply synthetic data is official. staging_company_skill_levels is read-only. Keep privileged keys server-side. Unknown candidate competency remains null; extraction confidence is not competency. What-if state never changes saved profiles. Record actual test commands and limitations. Read docs/BUILD_PLAN.md and module plans for requirements. No autonomous agent delegation is requested.
