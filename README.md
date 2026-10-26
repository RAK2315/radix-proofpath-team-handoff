# RADIX ProofPath - five runnable teammate handoffs

Five people, five module folders, one shared dependency/runtime area. This repository contains actual
working starting code, clearly synthetic fixtures and current contracts. Each teammate assumes ownership
of their module, tests it, then pushes their working copy to **their own GitHub repository** and returns
the URL, commit SHA and real test evidence. No merge or pull request is required from teammates.

| Person's module | Start here |
|---|---|
| 1. JD Analytics | [jd_analytics/README.md](jd_analytics/README.md), [PDF](jd_analytics/GUIDE.pdf) |
| 2. Resume Parsing | [resume_parsing/README.md](resume_parsing/README.md), [PDF](resume_parsing/GUIDE.pdf) |
| 3. Profile Builder | [profile_builder/README.md](profile_builder/README.md), [PDF](profile_builder/GUIDE.pdf) |
| 4. Talent Check | [talent_check/README.md](talent_check/README.md), [PDF](talent_check/GUIDE.pdf) |
| 5. Skill Matching / GPS | [skill_matching/README.md](skill_matching/README.md), [PDF](skill_matching/GUIDE.pdf) |

Clone the **whole repository once**. A folder download alone omits intentionally shared infrastructure.
All source for a feature lives in its root folder; `shared/`, `apps/`, dependency locks and reusable
test assets are stored once. Module 5 explicitly reuses Module 4's pure scorer/repository, but does not
require another teammate's server. Other modules use fixed upstream input fixtures in the standalone harness.

## Setup (Windows PowerShell, repository root)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
npm ci
npx playwright install chromium
```

Tested with Python 3.10 and Node 24. No API key or Supabase account is required for local synthetic tests.
See `.env.example` for optional Groq configuration; do not overwrite an existing private `.env`.

## Run one module

Example for JD Analytics (substitute your folder name):

```powershell
# Terminal 1:
.\jd_analytics\run.ps1 api
# Terminal 2:
.\jd_analytics\run.ps1 web
# Verification:
.\jd_analytics\run.ps1 check
```

Open http://127.0.0.1:5173/; schema at http://127.0.0.1:8000/docs.
Click **Load synthetic inputs** to supply pre-reviewed upstream inputs. It is not a fresh parsing demo.
Run only one module on these default ports at a time. If PowerShell scripts are restricted, set
`$env:RADIX_MODULE='jd_analytics'`, then run Python uvicorn for `apps.api.standalone:app` and
`npm run dev:module` in separate terminals. Do not bypass device policies.

## Integrated app (Scrum Master)

```powershell
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
# Separate terminal:
npm run dev
```

The original five-feature app remains available; the standalone wrapper is additional composition only.
Use [SCRUM_MASTER.md](SCRUM_MASTER.md) for distribution and integration and
[SUBMIT_YOUR_REPOSITORY.md](SUBMIT_YOUR_REPOSITORY.md) for the teammate GitHub workflow.

## Tests and honest status

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm run test
npm run typecheck
npm run lint
npm run build
npm run test:e2e
npm run test:handoff
```

See `verification/RESULTS.md` for actual results on this clean handoff checkout. Each teammate must run
their own commands and fill `DELIVERY.md`; they must not reuse someone else's passing counts.
Rules mode is testable offline. Groq integration exists and has mocked protocol tests; actual model
quality/live-provider execution remains pending a real authorized key and explicit input consent.
Supabase adapters exist; live RLS/organizer standards remain externally pending. No website is deployed.

The reconstructed test pack has six synthetic JDs and four fictional CVs in both PDF/DOCX. Real company
names in those labelled reconstructions do not make their content official. Company benchmark fixtures
use explicitly invented lab companies. Never commit a real CV, personal reports, keys or private exports.
