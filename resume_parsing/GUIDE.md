# Resume Parsing - teammate guide (editable)

Assume you own this module. Run/test it and push your working copy to YOUR OWN GitHub. Return URL, SHA, evidence and limitations; no central PR is required.

## Your responsibility

Read a candidate's resume and turn its supported statements into editable skill claims and background fields. Keep each claim attached to its source, then hand the reviewed extraction to Profile Builder.

## Required input

A PDF or DOCX resume, plus optional explicit consent for Groq to process this input's text.

## Guaranteed output

A saved Extraction with source_type=resume: name/email, skills, education, projects, experience and other supported sections. It is not a proficiency assessment.

## Organizer requirement

Participant Brief p.7 labels this LLM EXTRACTION. Preserve PDF/DOCX support, structured skills, reliable background fields and tolerance for varied layouts. Source evidence and explicit review are ProofPath additions.

## Build in order

1. **Trace one resume** - Read the Mira synthetic CV and your service/router/UI. Identify exactly what is extracted and where Profile Builder reads it.
2. **Reuse ingestion** - Use the shared PDF/DOCX reader and private document storage. Do not add a second upload endpoint, public CV URL or browser-only PDF parser.
3. **Extract supported facts** - Ask Groq for identity, explicit/inferred skill claims and background sections. Include unfamiliar technologies. Missing facts remain empty; section arrays contain original quotes.
4. **Keep source grounding** - Preserve original quote, PDF page or null DOCX page, source document ID and available spans. Treat document instructions as untrusted content.
5. **Require review** - Show every proposed skill and supported section. Let the user correct/delete/add claims and explicitly confirm unreviewed skills.
6. **Save the extraction** - PATCH the full current Extraction with reviewed status. Retain accepted data if a later workspace refresh fails.
7. **Prove import** - Give Module 3 the reviewed ID. Verify fields/evidence survive import and all twelve candidate competency levels remain null unless already set by the user.

## Run and verify

Use README.md for fresh setup. From the full repo root:

```powershell
.\resume_parsing\run.ps1 api
# Separate terminal:
.\resume_parsing\run.ps1 web
# Verify:
.\resume_parsing\run.ps1 check
```

## Screen structure

- **1  SELECT / UPLOAD: Choose saved resume | Drop PDF/DOCX** - Allow a new upload without hiding saved extractions. Groq consent is a separate input decision.
- **2  PROCESSING: LLM processed + model / rules-only** - Show source name and fallback warnings. Do not label every parse as AI.
- **3  IDENTITY: Candidate name + email** - Editable fields. Do not guess missing contact details.
- **4  CLAIMS + SECTIONS: Skills, evidence, education, projects...** - Readable cards, skill-family filters, exact source drawer and editable section text.
- **5  SAVE / HANDOFF: Save reviewed resume -> Build your profile** - Save a reviewed extraction before asking Module 3 to import it.

## API endpoints

- `POST /api/resumes/extract` - Multipart: file; hosted_consent=false unless opted in.
- `GET /api/resumes[/ID]` - List/load owned saved extractions.
- `PATCH /api/resumes/ID` - Full Extraction + current revision + reviewed status.
- `DELETE /api/resumes/ID` - Delete extraction; delete original separately in Data & privacy.

See request-example.json and the FULL response-example.json here. Canonical required/optional fields and types are in shared/contracts/models.py and shared/contracts/openapi.json.

## Logic

A resume is evidence of what the document says. It does not establish that the candidate is skilled, truthful or independently verified. Preserve that distinction from extraction to the final presentation.

- **'Built a Python pipeline'** - Extract Python with the exact project quote. Confidence describes how clearly the text supports that extraction.
- **'Rust' is not in the old vocabulary** - A source-grounded Groq proposal can preserve it. Use a sensible RADIX category; do not drop it because a fixed dictionary lacks it.
- **'Prepared messy records for analysis'** - May support an inferred Data Cleaning proposal. Mark inferred; a human must judge the meaning, even when the quote matches.
- **'No production Kubernetes experience'** - Do not turn it into positive competency. Keep a negated/conflicting claim unresolved and source-visible.
- **Missing name, date or qualification** - Leave blank/empty instead of completing it from guesses. Do not merge two employers into one experience entry.

Never assign 1-10 ratings from resume mentions, confidence, project count or an LLM. Imported claims remain unverified. Private CV processing on Groq requires the input's explicit consent.

## Tests

Read TESTING.md for three normal and three failure cases. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest resume_parsing/tests -q
npm run test -- resume_parsing/frontend
```

## Demonstration

1. Open Resume Parsing. Upload demo/final/mira-cv-SYNTHETIC.pdf with hosted consent off for the fixed rules demo.
2. Show Mira Sen (synthetic), email, six claims: Python, SQL, Pandas, NumPy, Git and Linux.
3. Open Python evidence and its original source. Show education, selected work/projects and the synthetic internship.
4. Point out that extraction confidence and verified ability are different. No numeric competency rating was produced.
5. Save reviewed resume; hand its current ID to Profile Builder. For a live Groq demo, use synthetic input and show the real processing result, including any review corrections.

## Explain to judges

- 0:00-0:35: My module reads the candidate's document. It extracts supported facts, not a hiring decision.
- 0:35-1:25: Upload Mira, show identity and six extracted claims. Open one exact project quote.
- 1:25-2:15: Explain explicit versus inferred claims, unfamiliar terms and why negation needs review.
- 2:15-3:10: Show editable projects/education. Explain format limits and LLM/rules status honestly.
- 3:10-4:00: Save the review, explain the resume-ID handoff and emphasize that ratings remain unknown.

## Likely questions

**Does Python in a CV mean Python level 8?** No. It is an unverified source claim. Numeric self-ratings are collected separately by Profile Builder.

**Can it read every CV layout?** No. Common text-based PDFs/DOCX work with review; scans, complex reading order and implicit meaning have limits.

**What does source evidence prove?** Only that the quoted text occurs in the document, not skill proficiency or authorship.

## Return to Scrum Master

Publish to your own GitHub repository and fill DELIVERY.md with actual executed results. Follow ../SUBMIT_YOUR_REPOSITORY.md. Never commit private CVs or secrets. Live Groq, Supabase and organizer data remain pending unless actually verified.
