# 3. Profile Builder: your working module

Assume YOU own this module. Read `GUIDE.pdf`, inspect and run the provided code, improve it where needed,
then **test it and publish your working copy to YOUR OWN GitHub repository**. Return that link and the
actual evidence listed below to the Scrum Master. You do not need to merge into this repository or open a PR.

## What you build and own

Your working source is here: `backend/`, `frontend/`, `tests/`, `PLAN.md`, `CONTRACT.md`, `USAGE.md`.
This is functional starting code, not an empty assignment. Understand the functions and verify the
input/output contract before claiming it works. `IMPLEMENTATION_NOTES.md` preserves the earlier feature notes.
Do not replace the shared schema, category names, auth/storage plumbing, or another teammate's module.
The shared runtime, package locks and test helpers are stored once at the repository root.
For Module 5, Talent Check's pure scorer/benchmark repository is an explicit existing dependency;
you do not need its server or UI running.

## Clone the COMPLETE repository once

Do not download only this directory: it intentionally uses `../shared`, `../apps` and root dependencies.
You can run this module alone without the other modules' web/API routes or any other teammate's server.
Only one module server uses the default 8000/5173 ports at a time.

## Setup (PowerShell, repository root)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r profile_builder/requirements.txt
npm ci
npx playwright install chromium
```

Python 3.10+ and Node 24.x are the tested versions. No cloud credentials are needed for local synthetic tests.
Keep `.env` private if configuring Groq; start from `.env.example` only if `.env` does not already exist.

## Run YOUR module

```powershell
# Terminal 1, from repository root:
.\profile_builder\run.ps1 api
# Terminal 2:
.\profile_builder\run.ps1 web
```

Open **http://127.0.0.1:5173/**. The header identifies your standalone module.
Click **Load synthetic inputs** when you need upstream saved JD/resume/profile inputs.
These are pre-reviewed synthetic snapshots, not a live parsing claim. Upload fresh files to test extraction.
API schema: **http://127.0.0.1:8000/docs**. This standalone composition mounts only your feature's routes,
shared document/receipt routes and a local-only fixture context. The original integrated app remains available
with the normal root commands in the root README.

## Prove it works

```powershell
.\profile_builder\run.ps1 check
.\.venv\Scripts\python.exe -m pytest profile_builder/tests -q
npm run test -- profile_builder/frontend
npm run typecheck
npm run lint
npm run build
```

`check` executes your real standalone API in a temporary store and checks module-specific outputs.
It forces rules mode, never sends personal documents or charges Groq. Unit/component tests supplement it.
See `TESTING.md` for three normal + three failure cases and expected results.
For live Groq (Modules 1/2), use your own private key and explicit synthetic-input consent; record model,
actual calls, output quality and failures separately. A rules result or HTTP 200 is not live-model proof.
Supabase/official source acceptance stays pending; do not request missing organizer keys from teammates.

## Push to YOUR GitHub and return

See `../SUBMIT_YOUR_REPOSITORY.md` for exact steps. Use a repository you own and choose its visibility
with the Scrum Master; private is the default. Do not push to someone else's remote accidentally.
If private, grant the Scrum Master access. Teammates do not need to publish a website.

Return these items in `DELIVERY.md`:

1. Your repository URL, module name and commit SHA.
2. What you built/changed and which files you own.
3. Setup/run commands that you executed successfully.
4. Actual test commands, counts and failures (paste safe output).
5. At least three normal and three edge/failure cases, expected versus actual.
6. Screenshots: input, output/source explanation and a failure/recovery state, synthetic only.
7. Known limitations and live-Groq/Supabase status using implemented/mock-tested/live-verified/pending.
8. A statement confirming no keys, private CVs or hidden hardcoded scores were committed.

If something fails, fix it or report the failure honestly. The Scrum Master needs an actual working part,
not just screenshots or code that only imports. Use the independent-repository submission workflow in this README and the refreshed guide.
