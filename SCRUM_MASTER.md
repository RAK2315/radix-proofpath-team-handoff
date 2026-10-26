# Scrum Master: distribute and integrate

Invite teammates to this private repository through Settings -> Collaborators. Send each person the
repository link, their assigned folder link and **only that folder's START_HERE.pdf** as the main guide.
They clone the whole repository for shared dependencies. START_HERE.md has the same teaching content;
the PDF alone is sufficient to ask an AI for help understanding the task. Code edits still require
the exact source files named inside it. Historical documents are not assigned reading.

| Person | Folder | Independent input | Output to integrate |
|---|---|---|---|
| 1 | `jd_analytics/` | PDF/DOCX/pasted JD | Reviewed Extraction -> Module 5 |
| 2 | `resume_parsing/` | PDF/DOCX CV | Reviewed Extraction -> Module 3 |
| 3 | `profile_builder/` | Manual form or reviewed CV | Saved Profile -> Modules 4/5 |
| 4 | `talent_check/` | Saved profile + chosen benchmark/company | Twelve rows + readiness |
| 5 | `skill_matching/` | Saved profile + reviewed JD | Match/gaps + reversible GPS |

Common contracts, readers, persistence, UI helpers, dependency locks and composition remain stored
once. Module 5 reuses Module 4's pure scorer/repository in the same clone, without a second server.

## Receive working code

Teammates run `run.ps1 example` and `run.ps1 test`, fix demonstrated issues and push the full working
clone to **their own private GitHub**. Require URL/access, tested commit SHA, changed files, actual
commands/results, three normal + three failure cases, synthetic screenshots and known limitations.
They do not need to merge centrally. Do not accept copied passing counts.

## Integrate

1. Keep this verified baseline. Clone each returned repository separately and verify its exact SHA.
2. Run its documented setup/tests. Compare owned feature changes before transferring them into an
   integration checkout. Review shared/schema/provider/storage changes deliberately.
3. Preserve one `shared/contracts/models.py`, OpenAPI and TypeScript contract. Example UUIDs in guides
   are snapshots. Integrate with real returned IDs, current revisions and owned source-document links.
4. Wire JD -> Resume -> reviewed import/Profile save -> Talent Check -> Matching/GPS. Import is a draft;
   ensure saved human corrections reach downstream assessments.
5. Rehearse `docs/DEMO_GUIDE.md`: Mira 74.9 readiness, 75 match, Docker 87.5, SQL 9 projects 79.5 readiness,
   reset and unchanged profile. The tiny Asha teaching cases intentionally have different inputs/scores.
6. Run all checks, inspect failures, scan staged files and freeze the tested SHA.

```powershell
# Clear module selection in a new terminal so all five browser projects run:
Remove-Item Env:RADIX_MODULE -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m pytest -q
npm run test
npm run typecheck
npm run lint
npm run build
npm run test:e2e
npm run test:handoff
.\.venv\Scripts\python.exe scripts/scan_handoff.py --staged
```

Never combine `.env`, private stores, node_modules or virtual environments from teammates. Keep failed
changes isolated while the owner fixes them. Preserve a recoverable working baseline.

## Pending external checks

Original six JDs/four CVs, authorized organizer benchmark schema/data, live Groq quality and live
Supabase/RLS remain pending. Use labelled synthetic practice data now. Keep staging read-only and keys
server-side. Unknown competency stays null; confidence is not competency. GPS never saves hypothetical
claims. The passport stores current claims/revisions, not immutable history. No cloud deployment is assigned.

Current results are in `verification/RESULTS.md`. Historical detail remains in `docs/internal/archive/`.
