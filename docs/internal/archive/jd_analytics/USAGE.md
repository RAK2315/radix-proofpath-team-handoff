# Use JD Analytics

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Start the API and UI using [the root setup](../README.md); local mode needs no credentials. Choose JD Analytics, upload a PDF/DOCX, review skills/company/role and groups, confirm ambiguous meanings and save. Click a source link for evidence. Continue to Resume Parsing or select this reviewed JD in Matching.

Independent API example from project-root PowerShell:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/examples/jd/0 -OutFile synthetic-jd.docx
curl.exe -H "X-ProofPath-Client: cli" -F "file=@synthetic-jd.docx" http://127.0.0.1:8000/api/jd/extract
.\.venv\Scripts\python.exe -m pytest jd_analytics/tests -q
npm run test -- jd_analytics/frontend
```

Use the returned ID/current revision for GET/PATCH in `/docs`; do not reuse unrelated example UUIDs. Six synthetic examples exist at indexes 0–5. Local extraction is vocabulary-limited. To use hosted extraction, configure the server model/key, restart and explicitly select hosted processing per upload. Unreadable/scanned/encrypted documents fail with actionable messages; OCR is not enabled. Original JD acceptance remains pending because no pack was supplied. See [contract errors](CONTRACT.md) and [actual test report](../docs/TEST_REPORT.md).

## Pre-submission audit update

In the JD page, choose Paste text, enter the complete posting, name its source and click Extract pasted JD. Inspect its exact quote and Save reviewed JD. A full synthetic posting and executable browser/API steps are in ../docs/DEMO_GUIDE.md. Dirty record switches warn before discarding review; failed workspace refresh preserves accepted extraction data.
