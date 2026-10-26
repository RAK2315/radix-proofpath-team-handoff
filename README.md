# RADIX ProofPath - start with your one guide

Clone this **whole private repository**. Shared code and dependencies are stored once, so downloading
only a module directory is not enough. Each person runs their module independently; no teammate server,
API key or database account is needed for synthetic local work.

| Your part | Read one guide | Same content for an AI assistant |
|---|---|---|
| 1. JD Analytics | [START_HERE.pdf](jd_analytics/START_HERE.pdf) | [Markdown](jd_analytics/START_HERE.md) |
| 2. Resume Parsing | [START_HERE.pdf](resume_parsing/START_HERE.pdf) | [Markdown](resume_parsing/START_HERE.md) |
| 3. Profile Builder | [START_HERE.pdf](profile_builder/START_HERE.pdf) | [Markdown](profile_builder/START_HERE.md) |
| 4. Talent Check | [START_HERE.pdf](talent_check/START_HERE.pdf) | [Markdown](talent_check/START_HERE.md) |
| 5. Matching + Career GPS | [START_HERE.pdf](skill_matching/START_HERE.pdf) | [Markdown](skill_matching/START_HERE.md) |

Your module folder contains only the two guide formats, `backend/`, `frontend/`, `tests/`, `samples/`
and `run.ps1`. The source already works. Understand it, test it, improve a real issue and publish your
working clone to **your own GitHub**. Return the URL, tested commit, results and limitations.

## Run it on Windows

Install Python 3.10+, Node.js 24, Git and an editor. Open PowerShell at the repository root.
Replace `jd_analytics` below with your assigned folder:

```powershell
.\jd_analytics\run.ps1 setup
# Terminal 1:
.\jd_analytics\run.ps1 api
# Terminal 2, same root:
.\jd_analytics\run.ps1 web
```

Open **http://127.0.0.1:5173/**. Only one module uses the default ports at a time.
`Load synthetic inputs` supplies reviewed upstream examples; it does not claim fresh parsing.

```powershell
.\jd_analytics\run.ps1 example
.\jd_analytics\run.ps1 test
```

`example` checks the small sample in a temporary database. `test` runs that module's API, Python,
React and browser checks plus type/lint/build checks. Stop on errors and record your actual results.
Each guide explains every command, source file, sample, required field and known limitation.

## Scrum Master only

[SCRUM_MASTER.md](SCRUM_MASTER.md) explains distribution and integration. The original integrated app
still runs with `python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000` and `npm run dev`.
[Verification](verification/RESULTS.md) records actual tests; [demo](docs/DEMO_GUIDE.md) gives the full journey.
Previous documents are preserved under [docs/internal/archive/](docs/internal/archive/), not assigned reading.

No real CVs, private exports or keys belong in Git. All samples are explicitly synthetic. Live Groq
quality, real Supabase/RLS and original organizer data acceptance remain unverified; nothing is deployed.
