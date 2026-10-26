# Use Talent Check

Start [the API/UI](../README.md) and save a profile. Choose Real company data only once an authorized source exists; otherwise choose Synthetic lab explicitly. Select a company, run Talent Check, filter gaps/unknowns and click any of the twelve rows to inspect arithmetic and linked evidence. Source mode/time remain visible; Refresh company data requests a new validated snapshot.

After replacing CURRENT_PROFILE_ID with an actual saved ID:

```powershell
$payload = @{profile_id='CURRENT_PROFILE_ID';company_id='lab-systems';benchmark_mode='synthetic'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/talent-check/evaluate -Headers @{'X-ProofPath-Client'='cli'} -ContentType 'application/json' -Body $payload
.\.venv\Scripts\python.exe -m pytest talent_check/tests -q
npm run test -- talent_check/frontend
```

All twelve explicit self-ratings are required for the final percentage; unknowns remain visible. Inspect `/api/receipts/{receipt_id}` for frozen inputs. No real URL/key/export was supplied; real mode correctly returns unavailable. [Organizer setup](../docs/ORGANIZER_SETUP.md) covers read-only schema inspection, mapping, filters, cache and atomic genuine export. Synthetic fixture tests do not prove real company values. [Contract](CONTRACT.md) · [Test report](../docs/TEST_REPORT.md).
