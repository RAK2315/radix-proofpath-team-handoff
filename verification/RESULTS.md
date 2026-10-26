# Verified teammate handoff baseline

Executed 26 October 2026 on Windows, Python 3.10, Node 24. A fresh `.venv` was installed from
`requirements.lock.txt`; `npm ci` installed the lockfile dependencies. No personal CV, official organizer
pack, live Groq call or live Supabase connection was used for these checks.

## Actual commands and results

| Command from repository root | Observed result |
|---|---|
| `.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt` | Successful clean environment installation |
| `npm ci` | Successful; 244 packages audited, zero reported vulnerabilities at installation time |
| `npx playwright install chromium` | Successful; browser available |
| `.\.venv\Scripts\python.exe -m pytest -q` | **140 passed**, one Starlette/httpx TestClient deprecation warning; 14.98 s |
| `npm run test` | **17 passed**, nine files; 2.23 s |
| `npm run test:e2e` | **9 passed**, integrated app; 57.0 s |
| `npm run test:handoff` | **5 passed**, one independently hosted feature per project; 23.1 s |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed, including after generating all five module bundles |
| `npm run format:check` | Passed |
| `.\.venv\Scripts\python.exe -m ruff check .` | Passed |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | Passed |
| `.\.venv\Scripts\python.exe -m mypy apps shared jd_analytics/backend resume_parsing/backend profile_builder/backend talent_check/backend skill_matching/backend --explicit-package-bases` | Passed; 30 source files |
| `npm run build` | Passed; integrated React production bundle generated |
| `RADIX_MODULE` set successively to each feature, then `npm run build:module` | All **five** selected-feature production builds passed |
| `.\.venv\Scripts\python.exe scripts/check_module.py MODULE` | All five passed; also executed as separate processes in the backend suite |
| `.\.venv\Scripts\python.exe scripts/scan_handoff.py` | Passed focused credential/private-file/document-label scan; staged scan repeated before publication |

The 140 backend tests include six new handoff tests: five real selected-feature API subprocess checks
and one guide/asset/matrix check. Personal-CV browser tests were deliberately excluded from this shared
repository; all nine integrated browser tests here use synthetic inputs. Counts describe this baseline,
not a teammate's future work.

## What independent operation actually checked

| Feature | Real API check | Real browser check |
|---|---|---|
| JD Analytics | DOCX extraction, pasted JD, review/save/reload revision, corrupt PDF rejection | Paste/extract/edit/save and source-linked output |
| Resume Parsing | PDF extraction, six named claims plus sections, review/reload, corrupt PDF rejection | Fresh synthetic PDF upload and reviewed save |
| Profile Builder | Reviewed import with twelve null ratings; create/update/reload/delete; stale revision rejection | Import, unknown-rating invariant, save and browser reload |
| Talent Check | Twelve rows, 74.9 synthetic readiness, deterministic repeat, missing/official source errors | Twelve comparison rows and 74.9 output |
| Matching + GPS | 75 baseline; Docker 87.5; SQL projection 79.5 readiness; reset; identical saved profile; stale scenario rejection | 12.50-point source chain, Docker projection and reset without profile changes |

Each standalone API mounts one feature router. Downstream features use explicit, pre-reviewed synthetic
upstream snapshots in the local harness. Loading those snapshots is not a fresh extraction demonstration.
Module 5 reuses Module 4's pure scorer and repository from the same clone; no second module server is needed.
The five browser projects check desktop operation and 390 px horizontal fit. Mobile screenshots are in
`screenshots/`; these are synthetic and do not establish exhaustive accessibility/browser coverage.

## Reconstructed six-JD/four-CV test pack

The 20 PDF/DOCX files are visibly labelled **SYNTHETIC RECONSTRUCTION - NOT OFFICIAL ORGANIZER DATA**.
Labels were specified in `scripts/create_reconstructed_pack.py` before extraction. Predictions are stored
separately in `data/synthetic/reconstructed/computed/`. `matrix-results.json` records 20 document-format
observations, 24 candidate/job matches and 12 invented-lab company comparisons.

| Fictional candidate | Google SWE | Google data | Microsoft SWE | Microsoft data | Oracle associate | Oracle support |
|---|---:|---:|---:|---:|---:|---:|
| Ananya | 87.5 | 28.6 | 66.7 | 41.7 | 77.8 | 60.0 |
| Karthik | 31.2 | 92.9 | 33.3 | 100.0 | 44.4 | 40.0 |
| Priya | 18.8 | 14.3 | 16.7 | 50.0 | 33.3 | 100.0 |
| Rohan | 87.5 | 100.0 | 83.3 | 100.0 | 77.8 | 100.0 |

These are deterministic rules-parser outputs on invented text, not official employer fit. All three
declared direction checks passed. They do not prove general extraction accuracy or guarantee that the
all-rounder outranks every specialist for every job.

Known differences remain visible: bare **Testing** is missed in three JD texts in both formats (six
observations); Priya gets an extra Problem Solving claim through troubleshooting (two formats); Rohan's
wrapped PDF skills line misses Shell Scripting (one observation). Do not silently remove these differences
from labels. Review/correct the output or improve and retest the parser. The older unfamiliar development
set also retains its documented Rust, Apache Arrow and implicit Data Cleaning limitations.

## PDF and publication checks

All five final guides contain nine pages. Their 45 pages and all ten reconstructed PDF pages were
rendered with Poppler and visually inspected. Source, guide, exact API contracts and editable Markdown
are included; intermediate page images stay local. Harmless Poppler fallback-font warnings appeared for
the synthetic PDFs; rendered text and labels were readable without clipping.

Packaging fixes: corrected escaped PowerShell commands in module READMEs; excluded generated module
bundles from ESLint; fixed selected-host TypeScript inference; removed the extra guide page; made the
scanner prune ignored directories before walking them. Shared support is stored once, not copied five times.

Only allowlisted source and synthetic artifacts were copied to this handoff repository. Private `.env`,
uploads, databases, original documents, personal reports, dependency directories and build output are
ignored/excluded. The staged publication scan checks known credential patterns, forbidden storage paths,
known private-CV markers and PDF/DOCX synthetic labels. This is a focused scan, not a complete security audit.

## External acceptance and limits

- **Implemented/mock-tested:** direct Groq strict-JSON transport, consent, grounding and failure fallback.
  Actual Groq inference quality remains unverified without an authorized key and consented input.
- **Implemented, live-unverified:** Supabase adapters, RLS/auth/private-document assumptions and organizer
  benchmark mappings. Real company data is unavailable; organizer staging remains read-only.
- Original six JDs, four resumes and official benchmark acceptance remain pending. Reconstructions never
  replace that acceptance. No HF/Vercel application deployment was performed.
- The current passport persists current claims, sources and profile revisions. It is not an immutable
  longitudinal evidence history. Unknown competency remains null; confidence never sets a skill rating.
- This packaging task does not add the broader attachment's `langchain-groq` wrapper or synthetic model
  response cache. Existing direct Groq code must not be described as LangChain.
- Teammates must execute their own setup/tests and fill `DELIVERY.md` before returning their own GitHub
  URL and immutable tested commit. This report cannot substitute for that verification.

See `../docs/DEMO_GUIDE.md` for the executed all-five-module demonstration.
