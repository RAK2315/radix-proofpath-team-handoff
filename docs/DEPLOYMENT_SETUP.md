# Deployment preparation and API-key setup

26 October 2026. Local preparation is implemented. **Nothing has been deployed, no cloud resources were changed, and no real Groq call has been verified.**

## Start with Groq locally

You need only a **Groq account and Groq API key** to try LLM extraction on the existing local application. Supabase, HF and Vercel are needed for the later cloud deployment, not for this local step.

1. Sign in at [Groq Console](https://console.groq.com/) and open **API Keys** to create a project key. Check that your account permits `openai/gpt-oss-20b`; model access and limits are account-specific. The model is served by Groq; no OpenAI API account/key is needed for this configuration.
2. Edit the existing private file [root .env](<.env>). Put the key **only** in this line:

   ```dotenv
   RADIX_LLM_API_KEY=YOUR_GROQ_KEY
   ```

   These settings are already present:

   ```dotenv
   RADIX_ENV=development
   RADIX_AUTH_MODE=local
   RADIX_STORAGE_MODE=local
   RADIX_DOCUMENT_STORAGE_MODE=local
   RADIX_LLM_MODE=auto
   RADIX_LLM_URL=https://api.groq.com/openai/v1/chat/completions
   RADIX_LLM_MODEL=openai/gpt-oss-20b
   RADIX_LLM_FALLBACK=rules
   RADIX_LLM_TIMEOUT_SECONDS=45
   RADIX_LLM_MAX_OUTPUT_TOKENS=8192
   ```

   `GROQ_API_KEY` is also supported as a server-side alias, but the named RADIX key takes precedence. Never put a real key in an example file, frontend variable, screenshot or chat. The root `.env` is ignored by Git and excluded from deployment bundles.
3. Restart the **Python API** so it reloads `.env`. Refreshing the browser alone does not reload server environment variables. If another process already owns port 8000, restart that known process; do not launch a competing copy.

   ```powershell
   Set-Location 'D:\Projects\26. jsssbootcamp'
   .\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
   ```

   In a separate terminal, if Vite is not already running:

   ```powershell
   Set-Location 'D:\Projects\26. jsssbootcamp'
   npm run dev
   ```

4. In **JD Analytics**, paste a JD or upload a PDF/DOCX. Select **Allow Groq to process this … text** before extracting. Use the same per-input checkbox for Resume Parsing. The checkbox appears when the backend reports a configured key. Configuration presence does not prove the key/model works.
5. Expect **LLM processed**, the actual model ID, source evidence and unreviewed claims. Check the quotes, relationships, identity and category assignments; confirm/correct the claims and save the review before importing/matching. A high evidence confidence never assigns competency. The twelve ratings stay unknown until explicitly supplied.
6. If a request fails, the default returns a labelled **Model unavailable / rules-only fallback** with a safe error code. That is not a successful LLM extraction. Use `RADIX_LLM_FALLBACK=error` to fail rather than fall back. `RADIX_LLM_MODE=rules` disables external calls even when the checkbox is selected. `auto` and `hosted` both require per-input consent; neither silently sends a CV.

The previously prepared synthetic demo launcher deliberately forces rules/local mode and disables keys. Use the normal application above to try Groq. The user's real CV has not been sent to Groq. Test an invented document first; select hosted processing for the personal CV only if you explicitly want its text sent to that provider.

## Run the synthetic model evaluation

The evaluator reads only invented fixtures: seven JD and seven resume sources, each in PDF/DOCX. It never reads the personal CV or private database. The original twelve sources are a development set; the two instruction-injection probes supplement them. This is not official-pack or held-out general accuracy.

Rules baseline, no external calls:

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate_llm
```

Once a key is configured, this explicitly sends those synthetic inputs to Groq and may use API quota:

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate_llm --live --authorize-synthetic --output docs/evaluation/groq-live.json
```

The two flags are intentionally required. Keep the baseline and live result files separate. Inspect actual successful-call count, precision/recall, group correctness, injection probes, schema/source validation, usage and latency; fallbacks count as unsuccessful model runs. A successful API response alone does not establish the page 7 requirement across unfamiliar documents.

## Accounts and permissions for the later cloud deployment

| Account | You provide | Where it goes |
| --- | --- | --- |
| [Groq](https://console.groq.com/) | Project API key, model access and suitable request/token/spend allowance. | Local root `.env` now; later **HF Space → Settings → Secrets → `RADIX_LLM_API_KEY`**. Never Vercel. |
| [Supabase](https://supabase.com/dashboard) | A **team-owned** project, project URL, publishable key, migration/bucket/Auth permission and at least two synthetic test accounts. Select a suitable region. | Backend `.env`/HF Variables: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`. Frontend public variables below. No privileged runtime key needed for normal users. |
| [Hugging Face](https://huggingface.co/) | Namespace with permission and eligible paid plan for Docker Spaces, a deploy token/login and chosen public/protected source visibility. | Deployment CLI login or private deployment credentials; never the browser. Personal PRO currently provides the required eligibility; CPU Basic has no hourly compute charge. Confirm billing first. |
| [Vercel](https://vercel.com/) | Project access and an appropriate Hobby/Pro account; project name, eventual domain if desired. | Vercel account/dashboard or CLI authorization. Git-provider integration is optional. |
| Organizer benchmark access | Authorized read-only access to `staging_company_skill_levels`, actual schema/filter scope, or a genuine permitted export. | HF Secrets for `RADIX_BENCHMARK_KEY` and optional `RADIX_BENCHMARK_ACCESS_TOKEN`; Variables for URL/mapping/filter. Keep separate from team app persistence. |

Current official hosting/billing sources and estimates are in [DEPLOYMENT_PLAN.md](<docs/DEPLOYMENT_PLAN.md>). No accounts, subscriptions or projects were created by this preparation.

## Prepare Supabase without connecting it yet

The reviewed migration file is [scripts/supabase.sql](<scripts/supabase.sql>). When you later authorize a migration in your team-owned project, it creates:

- `proofpath_records`: owner-scoped JSONB records with RLS and revision checks.
- Private bucket `proofpath-documents`, a 10 MiB object limit and owner-folder policies.
- `proofpath_usage` and `proofpath_reserve_extraction`: atomic daily quota reservations. Defaults are 50 requests / 2 million conservative tokens per user, 300 / 10 million globally. Both attempts and output budget are reserved; unused reservations are not refunded. These are app policy limits, not Groq account guarantees or an exact spending cap.

The migration revokes anonymous record access and does not touch organizer tables. It has not been applied or validated against live Postgres/RLS. Do not run it in the organizer project. For the initial controlled demo, disable public signup and create test users through Supabase Authentication → Users. The UI supports email/password sign-in, refresh and sign-out; signup/password-reset/email delivery are not added to the product.

Cloud configuration requires `RADIX_AUTH_MODE=supabase`, `RADIX_STORAGE_MODE=supabase` and `RADIX_DOCUMENT_STORAGE_MODE=supabase`. Missing/unsafe production settings fail startup. On authenticated API requests the backend verifies the session with Supabase and forwards the user JWT to records/files. Publishable keys identify the app; they are not user tokens. Never substitute a service-role/secret key for the public key.

### Frontend public settings

Locally copy [.env.frontend.example](<.env.frontend.example>) to root `.env.local` if testing cloud authentication/API integration. Later add the same values under **Vercel → Project → Settings → Environment Variables**, with appropriate Production/Preview scope:

```dotenv
VITE_API_BASE_URL=https://ACTUAL-SPACE-HOST.hf.space/api
VITE_SUPABASE_URL=https://YOUR-TEAM-PROJECT.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_PUBLISHABLE_KEY
```

These three values become public in the browser bundle. Nothing secret belongs in `VITE_*`. For ordinary local development leave them empty; `/api` uses the existing local proxy. Restart Vite after changing local frontend environment settings, or rebuild/redeploy a hosted frontend. Configure exact frontend origins in backend `RADIX_ALLOWED_ORIGINS`; comma-separated exact origins are supported. Supabase Site URL/auth redirects must use the actual approved frontend URLs.

The Vite configuration refuses a privileged Supabase secret/service-role key in the frontend. On Vercel it also requires the public cloud settings, preventing an accidental build that still depends on the local API proxy.

### Private files and retention

Originals are stored under `<authenticated-user-id>/<document-id>/original` in the private bucket; metadata/hash/text/spans stay in JSONB. The same authenticated API download route returns bytes with no permanent public URL. Failed metadata saves attempt object cleanup; metadata remains until dependent deletion succeeds so cleanup can be retried. Legacy base64 originals still download. No existing private data has been uploaded/migrated.

Access-triggered seven-day cleanup remains. For scheduled cleanup, provision an authorized private job runner later; no schedule was created. The implemented maintenance CLI defaults to **dry-run counting**:

```powershell
.\.venv\Scripts\python.exe -m scripts.cleanup_expired_documents
# After reviewing the dry run and authorizing deletion:
.\.venv\Scripts\python.exe -m scripts.cleanup_expired_documents --apply
```

It needs a separate `SUPABASE_MAINTENANCE_KEY` in the private job environment (Supabase secret/service-role key) plus Supabase storage configuration. This privileged credential belongs only to that scheduled job, not the frontend or normal API process. Do not schedule a 24/7 worker inside a sleeping Basic Space. Verify two-user isolation, failure recovery, retention scheduling and independent file backups before personal-data public use. A seven-day policy is not a promise of background expiry until the job is actually configured and verified.

## HF bundle and CLI preparation

Run the local packaging command; it does not upload or log in:

```powershell
.\.venv\Scripts\python.exe -m scripts.prepare_deployment
```

The generated [HF staging folder](<deploy/hf-space-ready>) contains all five backend packages, generic infrastructure/contracts, runtime lock, Dockerfile, Space metadata, labelled synthetic benchmark and a SHA-256 manifest. It excludes keys, personal documents, databases, original inputs, dependencies and test artifacts. Unexpected staging files cause refusal. [HF variables template](<deploy/hf-variables.env.example>) and [HF secrets template](<deploy/hf-secrets.env.example>) remain **outside** the upload folder; enter real values through HF settings or an external private file.

An isolated `.venv-deploy` now contains `huggingface_hub 2.3.0`; the older global CLI was left unchanged. **Windows Application Control blocked the new `hf.exe` launcher during version/help checks.** No login/upload command ran, and that restriction was not bypassed. Resolve launcher approval through the device's normal Windows/admin policy before using it. Current documented commands remain in the deployment plan; actual modern CLI execution is not yet verified on this device.

Docker is not on PATH, so the nonroot Linux image and runtime lock are prepared but not built/tested. No image digest is claimed. Verify with Docker or an authorized CI runner before deployment; production startup also requires actual Supabase settings. Vercel settings/security headers and upload exclusions are supplied in [vercel.json](<vercel.json>) and [.vercelignore](<.vercelignore>).

The supplied CSP allows connections to HF/Supabase platform hostnames. Tighten its `connect-src` to the actual two project origins before publication; update it if using custom API/Auth domains. Inline styles are permitted for existing charts; inline scripts are not. Verify CSP and CORS in a real hosted browser, not only the local Vite server.

## Remaining acceptance gates

Real Groq evaluation, live Supabase migrations/RLS/two-user file access, Linux Docker build, HF CLI launcher approval, cloud browser tests, scheduled retention and official benchmark acceptance remain open. The separate [cloud Playwright configuration](<playwright.cloud.config.ts>) starts no local servers and requires an authorized URL/test account; its smoke test is not a substitute for the complete release checklist. No deployment should be inferred from a successful local build or prepared upload folder.
