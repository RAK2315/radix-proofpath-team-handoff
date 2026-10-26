# Use Profile Builder

Start [the API/UI](../README.md). Choose Profile Builder and enter a manual profile or import a reviewed resume. Replacement of non-empty basic/section fields is explicit; default import fills empty fields and adds distinct skills. Add internships/hackathons/certifications/preferred roles, attach a CV directly if needed, and assess twelve categories or leave unknowns. Save and reload to verify persistence.

Create an independently usable profile from PowerShell:

```powershell
$payload = @{name='Synthetic Candidate';email='candidate@example.test'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/profiles -Headers @{'X-ProofPath-Client'='cli'} -ContentType 'application/json' -Body $payload
.\.venv\Scripts\python.exe -m pytest profile_builder/tests -q
npm run test -- profile_builder/frontend
```

Use the returned ID/current revision for GET/PATCH. Blank names, invalid email/ratings, unsupported source claims and stale revisions fail visibly. Unknown ratings are valid for saving; they block a final readiness percentage. Local records live in private SQLite. Supabase requires authorized team-owned tables, verified user tokens and live RLS validation: [organizer setup](../docs/ORGANIZER_SETUP.md). Delete a profile here; delete originals under Data & privacy. [Contract](CONTRACT.md) · [Test report](../docs/TEST_REPORT.md).

## Pre-submission audit update

Save/reload includes achievements. You can cancel an unsaved record switch. A failed write keeps the draft; if a write succeeds and its subsequent list refresh fails, the accepted saved record remains selected locally and can be reloaded when connected.
