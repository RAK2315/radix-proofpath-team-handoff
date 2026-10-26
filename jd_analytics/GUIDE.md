# JD Analytics - teammate guide (editable)

Assume you own this module. Run/test it and push your working copy to YOUR OWN GitHub. Return URL, SHA, evidence and limitations; no central PR is required.

## Your responsibility

Turn a job description into a reviewed list of what the employer asks for. Keep the exact words behind every requirement, and hand that saved list to Skill Matching.

## Required input

A PDF/DOCX job description, or pasted JD text. Optional, explicit permission to send this input's text to Groq.

## Guaranteed output

A saved Extraction with source_type=jd: company, role, skills, requirement groups, source evidence and review state.

## Organizer requirement

Participant Brief p.7 calls this LLM EXTRACTION. PDF/DOCX input, structured skills and the 12-category mapping are part of the core requirement. Pasted input and ProofPath source/importance controls extend it.

## Build in order

1. **Trace one JD** - Open the example JD and your service/router/UI files. Follow text -> extraction -> review -> saved revision -> matcher. Write down each boundary before editing.
2. **Keep both inputs** - Retain PDF/DOCX upload and Paste text. Reuse the shared document reader; do not write a second upload store or parser in the frontend.
3. **Extract proposals** - Keep JD-specific instructions in this module. Ask for real requirements, unfamiliar technologies, importance and relationships. Reuse the shared Groq schema/transport.
4. **Ground the output** - Every document skill and group needs a quote that exists in the source. Keep page/span links. Do not accept a fabricated source, model-owned ID or proficiency value.
5. **Make review usable** - Let the reviewer edit names/categories, add/remove skills and repair groups. Confirm unreviewed claims, group meanings and unparsed coverage explicitly.
6. **Save one contract** - PATCH the full current Extraction, not a reduced custom shape. Keep its ID, document ID and current revision. Cache success before refreshing the workspace.
7. **Prove the handoff** - Give Module 5 a saved, reviewed JD. Compare its group list with the original text, then run the feature and integration checks on page 7.

## Run and verify

Use README.md for fresh setup. From the full repo root:

```powershell
.\jd_analytics\run.ps1 api
# Separate terminal:
.\jd_analytics\run.ps1 web
# Verify:
.\jd_analytics\run.ps1 check
```

## Screen structure

- **1  INPUT: Upload file | Paste text** - Drop PDF/DOCX or paste full responsibilities and qualifications. Separate optional Groq consent.
- **2  CONTEXT: Company + Role + processing status** - Keep absent company/role blank. Show LLM processed/model or rules-only/fallback honestly.
- **3  SKILLS: Skill | category | confidence | source** - Search/filter by skill family. Open the exact quote. Edit, add, remove and confirm claims.
- **4  REQUIREMENTS: Importance | AND / OR | members** - Show group source and 'Group meaning reviewed'. Preserve alternatives instead of counting all as compulsory.
- **5  SAVE: Save reviewed JD** - Show saved revision and next step. Unsaved changes must remain visible.

## API endpoints

- `POST /api/jd/extract` - Multipart: file; hosted_consent=false by default.
- `POST /api/jd/extract-text` - JSON: text, source_name, hosted_consent.
- `GET /api/jd[/ID]` - List/load the current user's saved JD extractions.
- `PATCH /api/jd/ID` - Full Extraction, current revision, review_status=reviewed.
- `DELETE /api/jd/ID` - Remove extraction; original deletion is separate.

See request-example.json and the FULL response-example.json here. Canonical required/optional fields and types are in shared/contracts/models.py and shared/contracts/openapi.json.

## Logic

Read responsibilities and qualifications as requirements. Company names and job titles provide context; words in those fields alone are not required skills. A named technology outside the old vocabulary still belongs in the reviewed result.

- **Required: Python and SQL** - One mandatory AND group. Both members matter; each receives half of that group's potential coverage.
- **Python and either PyTorch or TensorFlow** - Two mandatory groups: Python alone (AND), plus PyTorch/TensorFlow (OR). Do not make all three mandatory.
- **Docker would be useful** - Preferred group, not mandatory. Use the source wording and context.
- **Rust / Apache Arrow is unfamiliar** - Groq may propose it with checked evidence; rules may miss it. Keep missing-coverage warnings until a human corrects them.
- **No Java required** - Negated/contextual wording must not become a positive compulsory requirement. Keep uncertainty visible for review.

No numeric candidate skill levels. No scores computed here. Confidence means confidence in extraction, not candidate ability. No private document leaves the backend for Groq without the input's consent.

## Tests

Read TESTING.md for three normal and three failure cases. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest jd_analytics/tests -q
npm run test -- jd_analytics/frontend
```

## Demonstration

1. Open JD Analytics. Upload demo/final/junior-data-engineer-jd-SYNTHETIC.docx in rules mode for the fixed demo.
2. Point to Synthetic Data Co and Junior Data Engineer. Explain that the employer and document are invented fixtures.
3. Show five groups: Python+SQL, Pandas, Linux, Docker, and AWS OR GCP. The first three are mandatory; the final two preferred.
4. Open a source quote. Show how category and importance can be corrected, then save the reviewed JD.
5. Hand over the current JD ID/revision. If demonstrating Groq, use an authorized synthetic input and show the actual processing label; do not claim it ran during the fixed rules demo.

## Explain to judges

- 0:00-0:35: My module answers what this specific job asks for. It takes a JD, not a candidate, and creates structured requirements.
- 0:35-1:20: Show upload/paste, company/role and the skills. Explain one category and one original source quote.
- 1:20-2:15: Show importance and AWS OR GCP. Explain why either alternative can satisfy that group.
- 2:15-3:10: Explain Groq proposals, deterministic evidence checks and human review. Show the truthful current processing mode.
- 3:10-4:00: Save the review, name the JD ID/revision handoff and explain one failure state. Transition to resume parsing.

## Likely questions

**Why an LLM?** Natural prose and unfamiliar technology names exceed a fixed keyword list. Source checks and human review limit unsupported proposals.

**Is LangChain mandatory?** The intended module uses LLM extraction. The current implementation calls Groq directly; LangChain itself is not prescribed by the brief.

**What if Groq fails?** Return a labelled rules fallback, or a safe error if configured. Do not call rules results LLM processed.

## Return to Scrum Master

Publish to your own GitHub repository and fill DELIVERY.md with actual executed results. Follow ../SUBMIT_YOUR_REPOSITORY.md. Never commit private CVs or secrets. Live Groq, Supabase and organizer data remain pending unless actually verified.
