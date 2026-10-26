# Use Skill Matching and Career GPS

Start [the local API/UI](../README.md). Select a saved profile and reviewed JD, then Analyze this match. Inspect matched/missing/unresolved requirements and the decision receipt. Review ambiguous group meanings or equivalences in the input before treating them as capability gaps.

```powershell
$payload = @{profile_id='CURRENT_PROFILE_ID';jd_id='CURRENT_JD_ID'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/matching/evaluate -Headers @{'X-ProofPath-Client'='cli'} -ContentType 'application/json' -Body $payload
.\.venv\Scripts\python.exe -m pytest skill_matching/tests -q
npm run test -- skill_matching/frontend
```

Replace IDs with current workspace records. Matching works without any benchmark connection. Career GPS adds company readiness only when a selected validated source exists. Toggle a missing skill, move a category slider or click Try it on a ranked action. The same engines calculate separate projected deltas. Reset removes overrides; saved profile values remain unchanged.

Stale revision/hash errors mean rerun the baseline, not overwrite the profile. Empty JDs are unscorable; close-string suggestions need human review. Missing live standards leave readiness unavailable without fabricating values. Full scenario/API examples are in [CONTRACT.md](CONTRACT.md). [Actual tests](../docs/TEST_REPORT.md) include backend purity/reset and the browser journey.

## Pre-submission audit update

Open a requirement decision to inspect its exact source and numeric point contribution. Conflicting claims must be reviewed at their source before they count. The audit/demo guide shows a real personal CV against an invented posting; that score is not official employer fit.
