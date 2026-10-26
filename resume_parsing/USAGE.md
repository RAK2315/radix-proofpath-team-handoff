# Use Resume Parsing

> Groq update (26 October 2026): semantic EXTRACTION is now IMPLEMENTED and MOCK-TESTED,
> using consented strict JSON proposals, checked source quotes/spans and editable review.
> Actual model execution remains EXTERNALLY BLOCKED until a Groq key is supplied.
> The mandatory LLM gate is not claimed live-verified. See
> [implementation](../docs/LLM_EXTRACTION_IMPLEMENTATION.md),
> [evaluation](../docs/LLM_EXTRACTION_EVALUATION.md) and
> [exact key/account setup](../docs/DEPLOYMENT_SETUP.md).


Start [the local API/UI](../README.md), choose Resume Parsing and upload a PDF/DOCX. Correct name/email, skills/categories and sections; inspect source evidence, then Save reviewed resume. Choose saved resumes with the module selector. Import the review from Profile Builder; this creates a draft and does not overwrite manual fields by default.

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/examples/resumes/0 -OutFile synthetic-resume.docx
curl.exe -H "X-ProofPath-Client: cli" -F "file=@synthetic-resume.docx" http://127.0.0.1:8000/api/resumes/extract
.\.venv\Scripts\python.exe -m pytest resume_parsing/tests -q
npm run test -- resume_parsing/frontend
```

Four synthetic inputs exist at indexes 0–3. Use returned IDs for review; full responses/errors are in [CONTRACT.md](CONTRACT.md). Local mode needs no keys and never infers competency. Hosted processing needs server config and explicit per-upload choice; missing provider configuration or failures are shown. Originals may be deleted in Data & privacy; access-triggered cleanup expires them after seven days. Complex layouts and the absent original pack still need human acceptance. [Test report](../docs/TEST_REPORT.md).

## Pre-submission audit update

Review achievements/internships/hackathons where the source contains them. A conflicting claim has an explicit confirmation control; inspect its quote before clearing the flag. The personal CV can be audited locally with python -m scripts.audit_candidate --cv PATH (virtualenv Python), which never opts into hosted extraction.
