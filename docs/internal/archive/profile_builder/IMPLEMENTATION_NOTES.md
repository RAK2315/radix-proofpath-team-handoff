# Profile Builder — Role 3

Create a complete editable candidate profile for Talent Check and Skill Matching. Mandatory fields include basic details, education, skills, internships, hackathons, certifications, preferred roles and CV. Projects/experience, explicit self-ratings and the evidence passport are additions.

`backend/router.py` handles create/load/update/delete and import preview. `backend/service.py` merges a reviewed resume and validates owned document claims. `frontend/ProfileBuilderPage.tsx` owns the form, direct CV attachment, import choice and twelve ratings. Tests live in `tests/test_profiles.py` and the frontend component test.

Local SQLite persists profiles across clients/reloads. The optional Supabase adapter uses the authenticated user's token, owner filters and RLS on team-owned records. Updates compare revisions. Import fills empty fields by default; replacement is explicit. The preview never saves until Save profile. CV attachment also works independently of resume parsing.

Each official category has one self-reported 1–10 rating or null. Document claims require an owned source and matching quote; hypothetical claims cannot be saved. Deleting sources removes linked claims and invalidates receipts. UI renames become manual corrections.

Persistence, all sections, import preservation, revision conflicts, deletion, owner isolation and scenario non-mutation are tested locally. Live Supabase auth/RLS is unverified without an authorized project. There is no complete sign-in product, encrypted local DB or independent competency verification.

[Usage](USAGE.md) · [Contract](CONTRACT.md) · [Checklist](PLAN.md) · [Organizer setup](../docs/ORGANIZER_SETUP.md)

## Pre-submission audit update

Achievements are an additional editable section and survive reviewed import/save/load. Unsaved record changes warn, failures preserve drafts, and accepted saves are cached before refreshing lists. The passport persists current claims/sources/revisions; a longitudinal historical timeline is not implemented.
