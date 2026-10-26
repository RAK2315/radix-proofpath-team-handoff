# Scrum Master: distribute, receive, integrate

The teammates **own and publish their own repositories**. They do not need to merge into this repository.
Give each person the root repository link plus their module folder link. Because this repo is private,
invite them under GitHub Settings -> Collaborators first, or distribute an approved clean ZIP. Never send keys.

| Module | Folder / guide / source | Synthetic assets | Access needed | Return | Your integration check |
|---|---|---|---|---|---|
| JD Analytics | `jd_analytics/` | Six reconstructed JDs, unknown/layout fixtures, Mira JD | None for rules; own/private Groq key for live test | Own repo + commit, source tests, review/source screenshots | Reviewed Extraction -> Module 5; AND/OR and importance correct |
| Resume Parsing | `resume_parsing/` | Four fictional CVs, unfamiliar/layout fixtures, Mira CV | None for rules; own/private Groq key for live test | Own repo + commit, section/evidence test results | Reviewed Extraction -> Module 3; all ratings remain unknown |
| Profile Builder | `profile_builder/` | Saved resume/profile JSON, Mira sources | Local SQLite; no cloud needed | Own repo + commit, create/import/save/reload/delete evidence | Same saved Profile/revision used by Modules 4 and 5 |
| Talent Check | `talent_check/` | Invented 12-category benchmarks and rated profiles | None for synthetic; organizer read access is pending | Own repo + commit, arithmetic/unknown/source errors | Twelve rows, deterministic formula, no unofficial standards |
| Matching / GPS | `skill_matching/` | Reviewed JD/profile, full match/scenario JSON | None for synthetic; Module 4 pure code in same clone | Own repo + commit, 75->87.5/reset/non-mutation evidence | Correct group coverage, source chain, pure GPS |

## Resource status

- **AVAILABLE NOW:** all five module sources, local backend/frontend compositions, pinned dependencies,
  exact contracts and automated unit/component/integration/browser checks.
- **GENERATED SYNTHETICALLY:** six JD/four CV reconstructions (20 PDF/DOCX files), manual expected labels,
  computed JSON/matrices, Mira journey and invented lab-company benchmarks. All visibly labelled.
- **WAITING FOR ORGANIZER:** original six JDs/four CVs, real `staging_company_skill_levels` schema/authorized data.
- **NEEDS YOUR CONFIGURATION:** real Groq key/live evaluation, Supabase credentials/RLS, HF/Vercel accounts,
  any cloud deployment, actual teammate role names and presentation rehearsal. Do not block local work on these.

## Receive a genuinely working part

Require `DELIVERY.md`: repo URL, immutable commit SHA, changed-file list, actual commands/results,
three normal + three failure cases, input/output/source screenshots and known limitations.
Ask the teammate to demonstrate the independent module running from their own checkout.
Do not accept copied passing numbers or a screenshot without repeatable setup and calculations.
Names in the synthetic reconstructed CVs are fictional; they are not team members.

## Your integration sequence

1. Preserve this verified baseline as a recoverable reference. Clone each returned repository into its own
   directory, record its URL/SHA and run the exact setup and module tests from `DELIVERY.md`.
2. Compare the teammate's feature folder with the baseline. Transfer their feature changes into an integration
   checkout. Shared-contract/provider/storage changes need deliberate review because every consumer depends on them.
   Never combine virtualenvs, private SQLite stores, `.env` files or node_modules from teammates.
3. Use one canonical `shared/contracts/models.py`, OpenAPI and generated TypeScript version. Validate the returned
   JSON examples; keep `OTHER` outside the twelve rated categories. Do not equate confidence with competency.
4. Wire in this order: JD -> Resume -> Profile save/import -> Talent Check -> Matching/GPS. Check actual IDs,
   revisions, source document ownership and that human corrections reach downstream computations.
5. Run all module checks and `pytest`, frontend tests, typecheck/lint/build and both browser suites.
   Check synthetic scores against source requirements, not against candidate names.
6. Re-run the Mira journey: five JD groups, six CV skills, unknown ratings before deliberate synthetic input,
   74.9 readiness, 75 JD match, Docker 87.5, SQL target readiness 79.5, reset and unchanged saved profile.
7. Scan staged files, save actual test evidence and freeze a known-good submission. Configure genuine standards
   only with authorized read access; never write organizer staging tables or silently replace missing data with lab values.

If a returned module fails, keep its changes isolated while the teammate fixes it. You own the integration
decision; teammates are told to deliver working code to their own GitHub, not to solve central merges.

## What this handoff does not claim

Groq's direct strict-JSON integration is implemented/mock-tested, not live-verified. The attached broader
implementation prompt's optional `langchain-groq` wrapper and authorized synthetic response cache have not
been added by this packaging task. No official-data or cloud acceptance is implied. Report those separately
if you decide they are needed; do not mislabel existing direct Groq calls as LangChain.

`verification/RESULTS.md` contains new checkout evidence. Deployment is prepared but not executed.
