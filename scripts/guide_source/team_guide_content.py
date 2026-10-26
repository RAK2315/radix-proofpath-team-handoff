"""Human-written handoff content, checked against the current five-module source."""

MODULES = [
    dict(
        n=1,
        name="JD Analytics",
        folder="jd_analytics",
        title="Understand the job.",
        mission="Turn a job description into a reviewed list of what the employer asks for. Keep the exact words behind every requirement, and hand that saved list to Skill Matching.",
        input="A PDF/DOCX job description, or pasted JD text. Optional, explicit permission to send this input's text to Groq.",
        output="A saved Extraction with source_type=jd: company, role, skills, requirement groups, source evidence and review state.",
        receives="The candidate supplies a JD. You do not need a resume, profile or company benchmark to run your module.",
        hands="Module 5 receives the saved JD ID and revision. Its matcher loads the reviewed skills and groups; it does not scrape your screen.",
        required="Participant Brief p.7 calls this LLM EXTRACTION. PDF/DOCX input, structured skills and the 12-category mapping are part of the core requirement. Pasted input and ProofPath source/importance controls extend it.",
        win="A teammate can upload two different JDs, inspect/correct the skills, save a review, reload it and explain why the two jobs ask for different things.",
        files=[
            (
                "backend/service.py",
                "Feature-specific extraction instructions, local rules and requirement grouping.",
            ),
            ("backend/router.py", "Composes extraction routes and owns the pasted-text endpoint."),
            ("frontend/JDAnalyticsPage.tsx", "Upload/paste flow, skill review and saved JD state."),
            ("frontend/RequirementReview.tsx", "Importance, AND/OR, group members and review controls."),
            ("frontend/PasteJD.tsx", "Text input, source name and per-input consent."),
        ],
        steps=[
            (
                "Trace one JD",
                "Open the example JD and your service/router/UI files. Follow text -> extraction -> review -> saved revision -> matcher. Write down each boundary before editing.",
            ),
            (
                "Keep both inputs",
                "Retain PDF/DOCX upload and Paste text. Reuse the shared document reader; do not write a second upload store or parser in the frontend.",
            ),
            (
                "Extract proposals",
                "Keep JD-specific instructions in this module. Ask for real requirements, unfamiliar technologies, importance and relationships. Reuse the shared Groq schema/transport.",
            ),
            (
                "Ground the output",
                "Every document skill and group needs a quote that exists in the source. Keep page/span links. Do not accept a fabricated source, model-owned ID or proficiency value.",
            ),
            (
                "Make review usable",
                "Let the reviewer edit names/categories, add/remove skills and repair groups. Confirm unreviewed claims, group meanings and unparsed coverage explicitly.",
            ),
            (
                "Save one contract",
                "PATCH the full current Extraction, not a reduced custom shape. Keep its ID, document ID and current revision. Cache success before refreshing the workspace.",
            ),
            (
                "Prove the handoff",
                "Give Module 5 a saved, reviewed JD. Compare its group list with the original text, then run the feature and integration checks on page 7.",
            ),
        ],
        ui_title="Decode the job.",
        ui_blocks=[
            (
                "1  INPUT",
                "Upload file | Paste text",
                "Drop PDF/DOCX or paste full responsibilities and qualifications. Separate optional Groq consent.",
            ),
            (
                "2  CONTEXT",
                "Company + Role + processing status",
                "Keep absent company/role blank. Show LLM processed/model or rules-only/fallback honestly.",
            ),
            (
                "3  SKILLS",
                "Skill | category | confidence | source",
                "Search/filter by skill family. Open the exact quote. Edit, add, remove and confirm claims.",
            ),
            (
                "4  REQUIREMENTS",
                "Importance | AND / OR | members",
                "Show group source and 'Group meaning reviewed'. Preserve alternatives instead of counting all as compulsory.",
            ),
            (
                "5  SAVE",
                "Save reviewed JD",
                "Show saved revision and next step. Unsaved changes must remain visible.",
            ),
        ],
        ui_states=[
            ("Nothing uploaded", "Explain upload/paste and show no invented results."),
            ("Extracting", "Disable duplicate submit; keep entered text until a result is accepted."),
            (
                "Model fails",
                "Show Model unavailable / rules-only fallback; retain source and review warnings.",
            ),
            (
                "Save fails / 409",
                "Keep the draft. For a stale revision reload and reconcile; do not silently overwrite.",
            ),
        ],
        endpoints=[
            ("POST /api/jd/extract", "Multipart: file; hosted_consent=false by default."),
            ("POST /api/jd/extract-text", "JSON: text, source_name, hosted_consent."),
            ("GET /api/jd[/ID]", "List/load the current user's saved JD extractions."),
            ("PATCH /api/jd/ID", "Full Extraction, current revision, review_status=reviewed."),
            ("DELETE /api/jd/ID", "Remove extraction; original deletion is separate."),
        ],
        request_label="Accepted pasted-JD request; this is complete JSON",
        request={
            "text": "Company: Synthetic Example Co\nRole: ML Intern\nRequired: Python and either PyTorch or TensorFlow.",
            "source_name": "Synthetic ML JD",
            "hosted_consent": False,
        },
        response_keys=[
            "id",
            "revision",
            "source_type",
            "source_file",
            "company",
            "role",
            "review_status",
            "extraction_mode",
            "llm_status",
            "document_id",
        ],
        logic_title="A skill list is not enough. Preserve the relationship.",
        logic_intro="Read responsibilities and qualifications as requirements. Company names and job titles provide context; words in those fields alone are not required skills. A named technology outside the old vocabulary still belongs in the reviewed result.",
        logic_rows=[
            (
                "Required: Python and SQL",
                "One mandatory AND group. Both members matter; each receives half of that group's potential coverage.",
            ),
            (
                "Python and either PyTorch or TensorFlow",
                "Two mandatory groups: Python alone (AND), plus PyTorch/TensorFlow (OR). Do not make all three mandatory.",
            ),
            ("Docker would be useful", "Preferred group, not mandatory. Use the source wording and context."),
            (
                "Rust / Apache Arrow is unfamiliar",
                "Groq may propose it with checked evidence; rules may miss it. Keep missing-coverage warnings until a human corrects them.",
            ),
            (
                "No Java required",
                "Negated/contextual wording must not become a positive compulsory requirement. Keep uncertainty visible for review.",
            ),
        ],
        special="The group contract supports flat AND/OR groups. Mixed statements need a correct decomposition or a requires_review flag. Never invent nested-group fields without a team-wide schema change.",
        guard="No numeric candidate skill levels. No scores computed here. Confidence means confidence in extraction, not candidate ability. No private document leaves the backend for Groq without the input's consent.",
        unitcmd=".\\.venv\\Scripts\\python.exe -m pytest jd_analytics/tests -q",
        frontcmd="npm run test -- jd_analytics/frontend",
        tests=[
            (
                "Two different synthetic JDs, PDF + DOCX",
                "Useful skills/groups appear; differences reflect source text, not hardcoded employer names.",
            ),
            ("Paste same source", "Same contract and private source linkage; input_method=pasted_text."),
            (
                "Python AND an ML-library alternative",
                "Two correct groups; alternatives are not all compulsory.",
            ),
            (
                "Groq off / denied / invalid quote",
                "No unauthorized call; honest rules fallback or safe error; fabricated quote never accepted.",
            ),
            ("Manual correction + save/reload", "Latest review revision is loaded by Module 5."),
            (
                "Empty/corrupt/scanned/large input",
                "Useful error; no invented extraction. Existing input limits remain enforced.",
            ),
        ],
        demo=[
            "Open JD Analytics. Upload demo/final/junior-data-engineer-jd-SYNTHETIC.docx in rules mode for the fixed demo.",
            "Point to Synthetic Data Co and Junior Data Engineer. Explain that the employer and document are invented fixtures.",
            "Show five groups: Python+SQL, Pandas, Linux, Docker, and AWS OR GCP. The first three are mandatory; the final two preferred.",
            "Open a source quote. Show how category and importance can be corrected, then save the reviewed JD.",
            "Hand over the current JD ID/revision. If demonstrating Groq, use an authorized synthetic input and show the actual processing label; do not claim it ran during the fixed rules demo.",
        ],
        talk=[
            (
                "0:00-0:35",
                "My module answers what this specific job asks for. It takes a JD, not a candidate, and creates structured requirements.",
            ),
            (
                "0:35-1:20",
                "Show upload/paste, company/role and the skills. Explain one category and one original source quote.",
            ),
            (
                "1:20-2:15",
                "Show importance and AWS OR GCP. Explain why either alternative can satisfy that group.",
            ),
            (
                "2:15-3:10",
                "Explain Groq proposals, deterministic evidence checks and human review. Show the truthful current processing mode.",
            ),
            (
                "3:10-4:00",
                "Save the review, name the JD ID/revision handoff and explain one failure state. Transition to resume parsing.",
            ),
        ],
        qa=[
            (
                "Why an LLM?",
                "Natural prose and unfamiliar technology names exceed a fixed keyword list. Source checks and human review limit unsupported proposals.",
            ),
            (
                "Is LangChain mandatory?",
                "The intended module uses LLM extraction. The current implementation calls Groq directly; LangChain itself is not prescribed by the brief.",
            ),
            (
                "What if Groq fails?",
                "Return a labelled rules fallback, or a safe error if configured. Do not call rules results LLM processed.",
            ),
        ],
        transition="We now know what the job asks for. Module 2 will extract what the candidate's resume actually says.",
    ),
    dict(
        n=2,
        name="Resume Parsing",
        folder="resume_parsing",
        title="Find the candidate's evidence.",
        mission="Read a candidate's resume and turn its supported statements into editable skill claims and background fields. Keep each claim attached to its source, then hand the reviewed extraction to Profile Builder.",
        input="A PDF or DOCX resume, plus optional explicit consent for Groq to process this input's text.",
        output="A saved Extraction with source_type=resume: name/email, skills, education, projects, experience and other supported sections. It is not a proficiency assessment.",
        receives="The candidate supplies a resume. You do not need a JD, company or benchmark to parse it.",
        hands="Module 3 receives a reviewed resume ID. Its import-resume operation merges the saved Extraction into a profile draft; it does not copy values from your UI.",
        required="Participant Brief p.7 labels this LLM EXTRACTION. Preserve PDF/DOCX support, structured skills, reliable background fields and tolerance for varied layouts. Source evidence and explicit review are ProofPath additions.",
        win="Two contrasting resumes produce different source-backed claims. The reviewer can correct a name/section, save it, and import it without any automatic competency rating.",
        files=[
            ("backend/service.py", "Resume-specific instructions, local section rules and postprocessing."),
            ("backend/router.py", "Composes the shared extraction HTTP plumbing for resumes."),
            (
                "frontend/ResumeParsingPage.tsx",
                "Upload, saved-resume selection, field editing and review save.",
            ),
            ("tests/test_extraction.py + test_audit.py", "Resume evidence, layout and section regressions."),
        ],
        steps=[
            (
                "Trace one resume",
                "Read the Mira synthetic CV and your service/router/UI. Identify exactly what is extracted and where Profile Builder reads it.",
            ),
            (
                "Reuse ingestion",
                "Use the shared PDF/DOCX reader and private document storage. Do not add a second upload endpoint, public CV URL or browser-only PDF parser.",
            ),
            (
                "Extract supported facts",
                "Ask Groq for identity, explicit/inferred skill claims and background sections. Include unfamiliar technologies. Missing facts remain empty; section arrays contain original quotes.",
            ),
            (
                "Keep source grounding",
                "Preserve original quote, PDF page or null DOCX page, source document ID and available spans. Treat document instructions as untrusted content.",
            ),
            (
                "Require review",
                "Show every proposed skill and supported section. Let the user correct/delete/add claims and explicitly confirm unreviewed skills.",
            ),
            (
                "Save the extraction",
                "PATCH the full current Extraction with reviewed status. Retain accepted data if a later workspace refresh fails.",
            ),
            (
                "Prove import",
                "Give Module 3 the reviewed ID. Verify fields/evidence survive import and all twelve candidate competency levels remain null unless already set by the user.",
            ),
        ],
        ui_title="Experience, unpacked.",
        ui_blocks=[
            (
                "1  SELECT / UPLOAD",
                "Choose saved resume | Drop PDF/DOCX",
                "Allow a new upload without hiding saved extractions. Groq consent is a separate input decision.",
            ),
            (
                "2  PROCESSING",
                "LLM processed + model / rules-only",
                "Show source name and fallback warnings. Do not label every parse as AI.",
            ),
            (
                "3  IDENTITY",
                "Candidate name + email",
                "Editable fields. Do not guess missing contact details.",
            ),
            (
                "4  CLAIMS + SECTIONS",
                "Skills, evidence, education, projects...",
                "Readable cards, skill-family filters, exact source drawer and editable section text.",
            ),
            (
                "5  SAVE / HANDOFF",
                "Save reviewed resume -> Build your profile",
                "Save a reviewed extraction before asking Module 3 to import it.",
            ),
        ],
        ui_states=[
            ("No resume", "Explain accepted formats and human review."),
            ("Wrong/incomplete extraction", "Let the reviewer fix it; never hide the source."),
            ("Groq unavailable", "Show rules-only fallback and likely omissions; preserve the input."),
            ("Empty/scan/encrypted PDF", "Explain that readable text is required; OCR is not implemented."),
        ],
        endpoints=[
            ("POST /api/resumes/extract", "Multipart: file; hosted_consent=false unless opted in."),
            ("GET /api/resumes[/ID]", "List/load owned saved extractions."),
            ("PATCH /api/resumes/ID", "Full Extraction + current revision + reviewed status."),
            ("DELETE /api/resumes/ID", "Delete extraction; delete original separately in Data & privacy."),
        ],
        request_label="Upload fields; multipart, not a JSON string containing a path",
        request_code='file = actual PDF/DOCX bytes\nhosted_consent = "false"\n\nPOST /api/resumes/extract\nHeader: X-ProofPath-Client: web\nContent-Type: browser sets multipart boundary',
        response_keys=[
            "id",
            "revision",
            "source_type",
            "source_file",
            "name",
            "email",
            "education",
            "internships",
            "review_status",
            "llm_status",
            "document_id",
        ],
        logic_title="A mention is a claim. It is not a measured skill level.",
        logic_intro="A resume is evidence of what the document says. It does not establish that the candidate is skilled, truthful or independently verified. Preserve that distinction from extraction to the final presentation.",
        logic_rows=[
            (
                "'Built a Python pipeline'",
                "Extract Python with the exact project quote. Confidence describes how clearly the text supports that extraction.",
            ),
            (
                "'Rust' is not in the old vocabulary",
                "A source-grounded Groq proposal can preserve it. Use a sensible RADIX category; do not drop it because a fixed dictionary lacks it.",
            ),
            (
                "'Prepared messy records for analysis'",
                "May support an inferred Data Cleaning proposal. Mark inferred; a human must judge the meaning, even when the quote matches.",
            ),
            (
                "'No production Kubernetes experience'",
                "Do not turn it into positive competency. Keep a negated/conflicting claim unresolved and source-visible.",
            ),
            (
                "Missing name, date or qualification",
                "Leave blank/empty instead of completing it from guesses. Do not merge two employers into one experience entry.",
            ),
        ],
        special="PDF pages start at 1. DOCX has no reliable physical page count here, so source_page=null. Multi-column reconstruction is conservative and emits review warnings. Scanned PDFs do not have OCR support.",
        guard="Never assign 1-10 ratings from resume mentions, confidence, project count or an LLM. Imported claims remain unverified. Private CV processing on Groq requires the input's explicit consent.",
        unitcmd=".\\.venv\\Scripts\\python.exe -m pytest resume_parsing/tests -q",
        frontcmd="npm run test -- resume_parsing/frontend",
        tests=[
            (
                "Two contrasting resumes, PDF + DOCX",
                "Different skill/background outputs with defensible evidence; no candidate-name shortcuts.",
            ),
            (
                "Unfamiliar technology + varied heading",
                "Retain supported proposal; separate projects, internships and education correctly.",
            ),
            ("Negated/conflicting mention", "Needs review; cannot automatically satisfy matching."),
            ("Long unbroken word / missing @", "No pathological email-regex slowdown; no invented email."),
            (
                "Review/save/import",
                "Profile draft contains the reviewed fields and source references; ratings unchanged.",
            ),
            (
                "Provider error / invalid quote / no consent",
                "Bounded failure/fallback; unsupported claim rejected; no unauthorized request.",
            ),
        ],
        demo=[
            "Open Resume Parsing. Upload demo/final/mira-cv-SYNTHETIC.pdf with hosted consent off for the fixed rules demo.",
            "Show Mira Sen (synthetic), email, six claims: Python, SQL, Pandas, NumPy, Git and Linux.",
            "Open Python evidence and its original source. Show education, selected work/projects and the synthetic internship.",
            "Point out that extraction confidence and verified ability are different. No numeric competency rating was produced.",
            "Save reviewed resume; hand its current ID to Profile Builder. For a live Groq demo, use synthetic input and show the real processing result, including any review corrections.",
        ],
        talk=[
            (
                "0:00-0:35",
                "My module reads the candidate's document. It extracts supported facts, not a hiring decision.",
            ),
            (
                "0:35-1:25",
                "Upload Mira, show identity and six extracted claims. Open one exact project quote.",
            ),
            (
                "1:25-2:15",
                "Explain explicit versus inferred claims, unfamiliar terms and why negation needs review.",
            ),
            (
                "2:15-3:10",
                "Show editable projects/education. Explain format limits and LLM/rules status honestly.",
            ),
            (
                "3:10-4:00",
                "Save the review, explain the resume-ID handoff and emphasize that ratings remain unknown.",
            ),
        ],
        qa=[
            (
                "Does Python in a CV mean Python level 8?",
                "No. It is an unverified source claim. Numeric self-ratings are collected separately by Profile Builder.",
            ),
            (
                "Can it read every CV layout?",
                "No. Common text-based PDFs/DOCX work with review; scans, complex reading order and implicit meaning have limits.",
            ),
            (
                "What does source evidence prove?",
                "Only that the quoted text occurs in the document, not skill proficiency or authorship.",
            ),
        ],
        transition="We now have reviewed resume evidence. Module 3 adds the rest of the candidate's story and saves a complete profile.",
    ),
    dict(
        n=3,
        name="Profile Builder",
        folder="profile_builder",
        title="Save the candidate's story.",
        mission="Combine reviewed resume information with manual details into one saved candidate profile. This is the stable record that both assessment modules use.",
        input="Manual details, an optional reviewed resume ID, optional CV upload, and twelve optional 1-10 self-ratings.",
        output="A saved Profile with an ID/revision, background fields, source-linked claims, CV reference and exactly twelve rating entries. Unknown ratings remain null.",
        receives="Module 2 hands you a reviewed resume ID. Your form must also work independently with manual input; it cannot require parsing first.",
        hands="Modules 4 and 5 receive the same saved profile ID/revision. They must not use a second, differently shaped candidate object.",
        required="Participant Brief p.8 requires basics, skills, hackathons/internships, certifications, preferred roles and CV upload, with save/load. Resume prefill is desirable. Evidence passport and explicit self-ratings support our integrated design.",
        win="Create a manual candidate, save/reload it, import a reviewed resume without losing manual work, and show the exact same saved profile in both assessment modules.",
        files=[
            ("backend/service.py", "Reviewed resume merge and source validation."),
            ("backend/router.py", "Profile create/load/update/delete and import-preview routes."),
            (
                "frontend/ProfileBuilderPage.tsx",
                "Full form, CV attachment, evidence passport and self-ratings.",
            ),
            (
                "tests/test_profiles.py + test_final_merge.py",
                "Persistence, revisions, merge, sources and conflicting claims.",
            ),
        ],
        steps=[
            (
                "Start manually",
                "Create a Profile with a nonblank name. Let defaults fill arrays and twelve null ratings. Do not block consumers waiting for resume extraction.",
            ),
            (
                "Build all sections",
                "Keep name/email, education, projects, experience, internships, hackathons, certifications, preferred roles and achievements. Treat multiline entries as string arrays.",
            ),
            (
                "Import a reviewed resume",
                "POST import-resume with the current profile draft. Default replace_existing=false preserves nonempty manual fields; import returns a preview, not a saved record.",
            ),
            (
                "Preserve evidence",
                "Keep source_document_id, exact quotes, confidence, claim basis and review state on imported skills. A duplicate name must not hide a new conflicting claim.",
            ),
            (
                "Separate ratings",
                "Show twelve Unknown/1-10 controls. Parse Unknown as null, not zero. Keep self_reported origin. Importing evidence cannot increase any rating.",
            ),
            (
                "Save safely",
                "Use POST for create and PATCH with the full current Profile/revision for updates. Retain drafts on failure; reconcile 409 conflicts rather than silently overwriting.",
            ),
            (
                "Prove both consumers",
                "Reload the saved record and select it in Talent Check and Skill Matching. Export a small synthetic handoff only; do not share private CVs or keys.",
            ),
        ],
        ui_title="More than your resume.",
        ui_blocks=[
            (
                "1  START",
                "New profile | Import reviewed resume",
                "Select an existing saved profile or create a new draft; import is optional.",
            ),
            (
                "2  BASICS + STORY",
                "Name/email + experience sections",
                "Readable labelled forms, one entry per line. Show the attached CV reference.",
            ),
            (
                "3  PASSPORT",
                "Skills + source links + confidence",
                "Keep manual and document claims distinguishable. Review conflicts before matching.",
            ),
            (
                "4  SELF-RATINGS",
                "12 RADIX categories: Unknown or 1-10",
                "Separate panel on desktop; stack below form on mobile. Explain that the rubric is team-designed.",
            ),
            (
                "5  SAVE",
                "Save profile -> assessments",
                "Show saved version, unsaved changes, successful save and useful errors.",
            ),
        ],
        ui_states=[
            ("New draft", "All twelve rating values unknown; no automatic score or evidence."),
            ("Imported preview", "Fields are editable; tell the user to save before assessment."),
            ("Saved / reloaded", "Same ID, current revision and saved CV/claims remain visible."),
            ("Save fails / conflict", "Keep draft and show retry/reload guidance; no false success."),
        ],
        endpoints=[
            ("POST /api/profiles", "Create validated Profile; returns 201 and saved revision."),
            (
                "POST /api/profiles/import-resume",
                "resume_id + profile + replace_existing=false; merged draft only.",
            ),
            ("GET /api/profiles[/ID]", "List/load owned profiles."),
            ("PATCH /api/profiles/ID", "Full Profile with current revision; increments on success."),
            ("DELETE /api/profiles/ID", "Delete owned profile and invalidate receipts."),
            ("POST /api/documents", "Multipart CV attachment; use returned document ID as cv_file."),
        ],
        request_label="Minimal complete create request; defaults are server-filled",
        request={"name": "Synthetic Candidate", "email": "candidate@example.test"},
        response_keys=["id", "revision", "name", "email", "cv_file", "preferred_roles"],
        logic_title="Import fills a draft; only Save makes it authoritative.",
        logic_intro="Module 3 owns candidate persistence. A parsed resume is an input, not a replacement for the user's existing profile. Keep review provenance and competency separate all the way through.",
        logic_rows=[
            (
                "Import with replace_existing=false",
                "Fill empty background fields from the reviewed resume. Keep nonempty manual values. Merge skill names without losing a new conflicting source.",
            ),
            (
                "Import with replace_existing=true",
                "Explicitly replace imported background fields. Understand that current skill merging is still conservative; this option is not a blanket overwrite of all skill claims or ratings.",
            ),
            (
                "User adds evidence",
                "Add the source-backed claim if valid. Do not change a category rating, confidence-based proficiency or assessment score automatically.",
            ),
            (
                "Save profile",
                "Validate source ownership/quotes. Reject hypothetical source claims. Persist the current revision, and invalidate old evaluation receipts on changes.",
            ),
            (
                "User selects Unknown",
                "Store null. Numeric values must be finite 1-10, not booleans or 0. Keep exactly one row for each official category.",
            ),
        ],
        special="The Living Skill Passport currently persists the current claims, source links and profile revision. There is no historical timeline or immutable evidence archive UI. Present what exists; do not promise an implemented history view.",
        guard="A manually entered skill is self-reported, not document-verified. All verification_status values remain unverified. Source deletion removes dependent document claims; saved self-ratings remain self-reported.",
        unitcmd=".\\.venv\\Scripts\\python.exe -m pytest profile_builder/tests -q",
        frontcmd="npm run test -- profile_builder/frontend",
        tests=[
            ("Manual profile without parsing", "Create/save/load works; all twelve ratings default to null."),
            (
                "Reviewed vs unreviewed resume import",
                "Unreviewed input rejected; reviewed output merges into a draft and requires Save.",
            ),
            (
                "Manual field + duplicate/conflicting claim",
                "Manual work is preserved; new contradictory evidence is not silently discarded.",
            ),
            (
                "Invalid rating/email/source",
                "Reject invalid values, missing/unowned documents and hypothetical claims.",
            ),
            (
                "Save/reload and stale revision",
                "Persistence works; stale PATCH returns 409 without losing edits.",
            ),
            (
                "Both assessment consumers",
                "Same saved ID/revision used in Modules 4/5; scenario preview never mutates it.",
            ),
        ],
        demo=[
            "Open Profile Builder. Import the reviewed Mira resume. Explain that this creates an editable draft.",
            "Show education/projects/internship, CV link and the six source-linked skills. Add preferred role Junior Data Engineer if desired.",
            "Point out all twelve ratings are initially Unknown. This is the important invariant after parsing/import.",
            "For the synthetic numeric demo only, deliberately set every category to 4 and say these are invented self-ratings. Click Save profile.",
            "Reload the page, show the saved version and unchanged fields, then hand the same profile ID/revision to Modules 4 and 5.",
        ],
        talk=[
            (
                "0:00-0:35",
                "My module turns extracted evidence and manual information into one saved candidate record.",
            ),
            (
                "0:35-1:25",
                "Show the reviewed resume import and additional story fields. Explain that import previews, Save persists.",
            ),
            (
                "1:25-2:15",
                "Open a source claim and show Unknown ratings. Explain why evidence confidence is not proficiency.",
            ),
            (
                "2:15-3:10",
                "Enter clearly labelled synthetic ratings, save and reload. Describe revision checks and private ownership.",
            ),
            (
                "3:10-4:00",
                "Hand the same profile ID to both assessors. Explain one conflict/failure behavior and the passport's current limits.",
            ),
        ],
        qa=[
            (
                "Why not rate from the resume automatically?",
                "Mentions and confidence are not measured ability. Unknown stays null; the user supplies explicit self-ratings.",
            ),
            (
                "What happens when two people edit?",
                "Current revision checks reject stale saves with 409. The UI keeps the draft for reconciliation.",
            ),
            (
                "Is it a full evidence history?",
                "It saves current claims, sources and revision. A historical timeline is not implemented.",
            ),
        ],
        transition="The profile is now saved. Module 4 compares its self-ratings with a selected company's benchmark, while Module 5 compares named claims with one JD.",
    ),
    dict(
        n=4,
        name="Talent Check",
        folder="talent_check",
        title="Compare with the company bar.",
        mission="Compare a saved candidate's twelve explicit competency self-ratings with the selected company's twelve expected levels. Show what is known, the gaps and every part of the arithmetic.",
        input="A saved profile ID, a selected company ID, and explicit real or synthetic benchmark mode. A JD is not required.",
        output="ReadinessResult: score or null, exactly twelve category rows, completeness, evidence coverage, benchmark provenance/hash and an inspectable receipt.",
        receives="Module 3 supplies the saved profile. The read-only benchmark repository supplies company expectations; it is separate from app-owned profile storage.",
        hands="The user receives a company-level readiness explanation. Module 5's GPS can reuse the same pure readiness evaluator for clearly hypothetical category changes.",
        required="Participant Brief p.8 requires a company readiness score plus per-category gaps across all twelve RADIX categories. Our host update identifies staging_company_skill_levels as the read-only source. Synthetic data cannot satisfy official-data acceptance.",
        win="Two different rated profiles produce explainably different results. Missing ratings or unavailable company data are shown honestly instead of silently substituting values.",
        files=[
            (
                "backend/benchmark_repository.py",
                "Read-only source, mapping, validation, cache and permitted export loading.",
            ),
            ("backend/scoring.py", "Pure twelve-category readiness arithmetic; reused by GPS."),
            ("backend/router.py", "Company/status/evaluate endpoints and result receipts."),
            (
                "frontend/TalentCheckPage.tsx",
                "Company comparison, source provenance, chart and row evidence.",
            ),
        ],
        steps=[
            (
                "Agree what readiness means",
                "Read scoring.py and the formula on page 5. The equal-weight capped ratio is a team design decision, not an employer screening algorithm.",
            ),
            (
                "Load a saved profile",
                "Use the same Profile contract as Module 3. Do not assign ratings, replace Unknown with zero or scrape named skill counts.",
            ),
            (
                "Read a valid source",
                "Keep organizer access GET-only. Inspect actual schema before configuring mappings/filters. Each company needs exactly twelve unique valid 1-10 expectations.",
            ),
            (
                "Handle unavailable data",
                "Return a clear source error. Synthetic lab mode must be deliberately selected and permanently labelled; never silently use it as official data.",
            ),
            (
                "Compute one row per category",
                "Show candidate level, required level, shortfall, gap, attainment and contribution. Unknown values produce nulls; final score requires all twelve levels.",
            ),
            (
                "Expose provenance",
                "Show source mode/table, fetched time/hash and rule version through result/receipt. Evidence coverage is a separate count, not a score multiplier.",
            ),
            (
                "Prove reuse",
                "Compare two profiles, verify arithmetic and feed the same evaluator to GPS. Do not create a second inconsistent formula.",
            ),
        ],
        ui_title="Know where you stand.",
        ui_blocks=[
            (
                "1  SELECT",
                "Saved candidate + company + source mode",
                "Company readiness settings must distinguish Real source from Synthetic lab.",
            ),
            (
                "2  ACTION",
                "Run Talent Check",
                "Require saved profile and selected valid company. A JD is not needed.",
            ),
            (
                "3  SUMMARY",
                "Readiness % / Unassessed + X/12",
                "State that ratings are self-reported. Do not show a final number when categories are unknown.",
            ),
            (
                "4  COMPARISON",
                "12 rows + candidate/expectation bars",
                "Full category labels, values, gap and row evidence. Filters: All 12, Gaps, Unknown.",
            ),
            (
                "5  SOURCE",
                "Source card + decision receipt",
                "Show synthetic notice or genuine provenance; explain arithmetic without calling it a hiring probability.",
            ),
        ],
        ui_states=[
            ("No profile", "Ask for a saved profile, not a raw CV score."),
            ("No real benchmark", "Explain missing source; offer an explicit labelled lab mode."),
            ("Some ratings unknown", "Show known rows and completeness; final score null, not 0%."),
            ("All twelve assessed", "Show bounded score, all twelve gaps and source information."),
        ],
        endpoints=[
            (
                "GET /api/talent-check/companies",
                "?mode=real|synthetic&refresh=false; returns IDs/names and provenance.",
            ),
            (
                "GET /api/talent-check/benchmark-status",
                "Source availability/error; separate from process liveness.",
            ),
            (
                "POST /api/talent-check/evaluate",
                "profile_id + company_id + benchmark_mode; returns ReadinessResult.",
            ),
        ],
        request_label="Complete synthetic evaluation request; replace ID with current saved ID",
        request={"profile_id": "CURRENT_PROFILE_ID", "company_id": "lab-data", "benchmark_mode": "synthetic"},
        response_keys=[
            "company",
            "company_id",
            "readiness_score",
            "status",
            "rating_completeness",
            "evidence_coverage",
            "rules_version",
        ],
        logic_title="Show the arithmetic, not only the percentage.",
        logic_intro="For each category, divide the candidate level by the required level and cap the result at 1. Average all twelve category attainments. Stronger skills cannot compensate beyond the cap for weaker categories.",
        formula="attainment = min(candidate / required, 1)\nshortfall = max(required - candidate, 0)\ngap = candidate < required\ncontribution = 100 * attainment / 12\nscore = round(100 * sum(attainments) / 12, 1)",
        logic_rows=[
            (
                "Simple synthetic arithmetic",
                "If all twelve required levels are 8 and all candidate levels are 4, every attainment is 0.5; readiness = 50.0%.",
            ),
            (
                "Raise one of those ratings to 8",
                "One category reaches 1.0; the remaining eleven stay 0.5. New score = 54.2%. The change is explainable.",
            ),
            (
                "Unknown candidate category",
                "Return candidate_level=null, gap=null and attainment/contribution=null for that row. Final readiness_score=null, status=incomplete.",
            ),
            (
                "Mira synthetic SQL row",
                "Candidate 4, invented requirement 9: attainment 4/9; shortfall 5; contribution 3.7037 points out of 100.",
            ),
            (
                "Evidence added",
                "The evidence-linked count may change. The score must not change unless an explicit candidate rating or benchmark changes.",
            ),
        ],
        special="Real expectations must come from authorized staging_company_skill_levels reads or a permitted genuine export. Reject missing, duplicate, boolean, out-of-range or conflicting categories; do not fill gaps with guesses. The current cache is 15 minutes; refresh is explicit.",
        guard="All examples here are synthetic. No official company bar has been verified. The formula is a self-reported readiness estimate, not a hiring probability, guarantee or employer-approved cutoff.",
        unitcmd=".\\.venv\\Scripts\\python.exe -m pytest talent_check/tests -q",
        frontcmd="npm run test -- talent_check/frontend",
        tests=[
            (
                "All twelve known / arithmetic fixture",
                "Exact formula and 0-100 bound; repeated inputs give identical score.",
            ),
            (
                "One unknown / incomplete profile",
                "Score null; known row gaps still shown; null is not converted to zero.",
            ),
            (
                "Two different candidate profiles",
                "Different appropriate category outcomes; no constant or name-based score.",
            ),
            (
                "Missing/duplicate/invalid benchmark",
                "Source error; no invented expectation and no silent synthetic substitution.",
            ),
            ("Add evidence without changing rating", "Readiness unchanged; evidence count remains separate."),
            (
                "GPS category change/reset",
                "Same evaluator yields the projection; actual saved profile remains unchanged.",
            ),
        ],
        demo=[
            "Select the saved synthetic Mira profile with all twelve explicitly invented ratings set to 4.",
            "Open company readiness settings; choose Synthetic lab and Synthetic Data Co (lab-data). Keep the synthetic label visible.",
            "Click Run Talent Check: expected fixed-fixture score 74.9%, twelve category rows, 12/12 assessed.",
            "Open SQL: self-rating 4 against synthetic requirement 9 gives 3.7037 contribution points and a shortfall of 5.",
            "Explain Unknown behavior and source provenance. Hand the same formula/benchmark snapshot to GPS; official benchmark validation remains pending.",
        ],
        talk=[
            (
                "0:00-0:35",
                "My module compares a candidate with a company's general bar across twelve categories, not one job posting.",
            ),
            (
                "0:35-1:25",
                "Select synthetic company and show 74.9% plus twelve rows. Clearly label the invented standards.",
            ),
            ("1:25-2:15", "Open SQL and calculate 4/9, shortfall 5 and 3.7037 contribution points."),
            (
                "2:15-3:10",
                "Explain unknown ratings, source provenance and why evidence never raises proficiency automatically.",
            ),
            (
                "3:10-4:00",
                "Show how changing the candidate changes the score. Transition to the separate specific-JD comparison.",
            ),
        ],
        qa=[
            (
                "Why no score with one unknown?",
                "The chosen formula averages all twelve assessed categories. Treating missing ability as zero would make an unsupported claim.",
            ),
            (
                "Are those official Google/Microsoft expectations?",
                "No. The demo is synthetic. Genuine authorized organizer data is still needed for real company acceptance.",
            ),
            (
                "Why not use an LLM for the percentage?",
                "Plain deterministic arithmetic is more transparent and repeatable. The brief describes this module as plain code.",
            ),
        ],
        transition="Company readiness is one view. Module 5 now asks whether this candidate's reviewed named skills cover this particular job's requirements.",
    ),
    dict(
        n=5,
        name="Skill Matching + Career GPS",
        folder="skill_matching",
        title="Explain the match. Explore the next step.",
        mission="Compare the saved candidate's reviewed named claims with one reviewed JD. Explain matched, missing and unresolved requirements, then let the user explore reversible hypothetical improvements.",
        input="Saved profile ID + saved JD ID. GPS also uses their current revisions, optional company/benchmark snapshot, named-skill overrides and category overrides.",
        output="MatchingResult with score/null, matched/missing/ambiguous decisions and contributions. ScenarioResult adds baseline/projected outcomes and explicitly hypothetical changes.",
        receives="Module 1 supplies the reviewed JD; Module 3 supplies the saved profile. Module 4 supplies the readiness evaluator and optional benchmark snapshot for GPS.",
        hands="The candidate receives a source-to-claim-to-points-to-action explanation. GPS returns a preview only; it never saves capability changes to the real profile.",
        required="Participant Brief p.8 requires one-specific-JD score plus matched and missing skills. It permits exact/fuzzy matching; an LLM matcher is not required. Importance, ProofPath reasoning and Career GPS are our additions.",
        win="Different candidates/jobs produce understandable differences. A missing Docker claim has a source-backed reason, a reversible projection, and no silent change to the stored profile.",
        files=[
            ("backend/matcher.py", "Deterministic alias/group coverage and explanations."),
            ("backend/scenarios.py", "Pure copied-profile projections and same-engine recommendations."),
            ("backend/router.py", "Loads saved inputs, evaluates and records receipts."),
            ("frontend/SkillMatchingPage.tsx", "Match report, breakdown, GPS controls and reset."),
            (
                "frontend/ReasoningChain.tsx + MatchLauncher.tsx",
                "Evidence chain and direct CV-to-JD entry flow.",
            ),
        ],
        steps=[
            (
                "Load the exact pair",
                "Use saved profile_id and jd_id; display the candidate and job clearly. Company benchmarks and numeric ratings are not needed for named-skill matching.",
            ),
            (
                "Normalize conservatively",
                "Match exact names and reviewed aliases. Java is not JavaScript. A shared category is not enough to satisfy a named technology.",
            ),
            (
                "Score requirement groups",
                "Use mandatory weight 2, preferred/unspecified weight 1. AND uses a matched fraction; OR needs any member. Deduplicate equivalent groups.",
            ),
            (
                "Explain every decision",
                "Preserve JD quote, candidate quote or honest absence, importance, reason and contribution points. Treat fuzzy suggestions and unresolved claims as review tasks, not automatic matches.",
            ),
            (
                "Record current revisions",
                "Return a result/receipt linked to input revisions and rules. Empty JD is unscorable; unreviewed/ambiguous coverage remains provisional.",
            ),
            (
                "Preview on a copy",
                "GPS deep-copies the profile, applies only allowed explicit overrides and calls the same match/readiness engines. Hold revisions and benchmark hash fixed.",
            ),
            (
                "Reset and prove no writes",
                "Reset removes hypothetical changes. Compare saved profile JSON before/after. Do not expose scenario values as actual evidence or save them behind the scenes.",
            ),
        ],
        ui_title="Find your path forward.",
        ui_blocks=[
            (
                "1  PAIR + ACTION",
                "Candidate + job | Analyze this match",
                "State exactly which saved pair is being assessed; avoid a generic unnamed percentage.",
            ),
            (
                "2  REPORT",
                "Match % | matched | evidence gaps",
                "Missing list matters more than a big score. Show provisional/unscorable states.",
            ),
            (
                "3  REASONING",
                "JD source -> candidate -> points -> action",
                "Click a skill to see original quotes or honest no-evidence state. Keep source download available.",
            ),
            (
                "4  CAREER GPS",
                "Named-skill toggles + category levels",
                "Separate JD coverage from company readiness; mark all changes hypothetical.",
            ),
            (
                "5  RECOMMEND / RESET",
                "Rank next actions | Reset scenario",
                "Show before/after and honest gaps. Reset restores baseline; actual profile is untouched.",
            ),
        ],
        ui_states=[
            ("Missing candidate or JD", "Guide to saved inputs; do not invent an assessment."),
            ("Unreviewed/ambiguous input", "Label provisional, show unresolved reasons and review route."),
            ("Empty JD skills", "Unscorable, score null; not 0% or 100%."),
            ("Stale scenario revision/hash", "409 asks for a fresh baseline; never mix snapshots."),
        ],
        endpoints=[
            ("POST /api/matching/evaluate", "profile_id + jd_id; server loads saved records."),
            (
                "POST /api/matching/scenarios/preview",
                "Pair, current revisions, overrides and optional benchmark snapshot.",
            ),
            ("GET /api/receipts/ID", "Owned stored decision snapshot for the baseline assessment."),
        ],
        request_label="Complete baseline evaluation request; use current saved IDs",
        request={"profile_id": "CURRENT_PROFILE_ID", "jd_id": "CURRENT_JD_ID"},
        response_keys=[
            "jd_source_file",
            "jd_revision",
            "profile_revision",
            "match_score",
            "status",
            "rules_version",
        ],
        logic_title="Match requirements first. Simulate improvements separately.",
        logic_intro="A score is weighted coverage of reviewed extracted requirements. It is not measured proficiency. Confidence is not a score multiplier, and unrelated extra skills do not reduce the match.",
        formula="weight = 2 if mandatory, otherwise 1\nAND coverage = hits / member_count\nOR coverage = 1 if any hit, otherwise 0\nscore = round(100 * sum(weight * coverage)\n              / sum(weight), 1)",
        logic_rows=[
            (
                "Synthetic Mira baseline",
                "Three required groups covered: Python+SQL, Pandas, Linux. Two preferred groups missing: Docker and AWS/GCP. Covered weight 6 / total 8 = 75.0%.",
            ),
            (
                "Python/SQL contribution",
                "Their mandatory group is 2/8 of total = 25 points. In its AND group each matched member contributes 12.5 points.",
            ),
            (
                "Add hypothetical Docker",
                "The preferred group adds 1/8 = 12.5 points, giving 87.5%. Category self-ratings do not change.",
            ),
            (
                "Add hypothetical AWS too",
                "AWS satisfies AWS OR GCP; score 100%. Do not additionally demand GCP or count both alternatives twice.",
            ),
            (
                "Move SQL category level to 9",
                "Readiness may change (74.9 -> 79.5 in the synthetic story); named-SQL JD coverage does not change just because its broad rating changed.",
            ),
        ],
        special="A skill toggle changes named JD coverage; a category slider changes company readiness. The two mechanisms are deliberately separate. Fuzzy suggestions/unresolved evidence get review recommendations without promised automatic gains.",
        guard="Do not save a ScenarioResult as a Profile. Recommendations are possibilities, not guarantees, study-time estimates or verified learning. Reset must restore baseline using unchanged actual saved inputs.",
        unitcmd=".\\.venv\\Scripts\\python.exe -m pytest skill_matching/tests -q",
        frontcmd="npm run test -- skill_matching/frontend",
        tests=[
            (
                "Two candidates x two JDs",
                "Explainably different scores; deterministic repeats and bounded values.",
            ),
            (
                "AND/OR, duplicates, aliases",
                "Correct group arithmetic; Java/JavaScript not equivalent; no double counting.",
            ),
            (
                "Unknown/conflicting/unreviewed evidence",
                "Unresolved/provisional output, no automatic false match.",
            ),
            (
                "Empty JD / no company benchmarks",
                "Empty is unscorable; JD matching still works without company data.",
            ),
            (
                "Scenario invalid/stale input",
                "Reject skill outside JD, invalid category value and stale revision/hash.",
            ),
            (
                "Preview/reset/non-mutation",
                "Expected deltas and identical saved profile JSON before/after; same engines used.",
            ),
        ],
        demo=[
            "Select the reviewed synthetic data JD and saved Mira profile. Click Analyze this match: baseline 75.0%; four matched decisions and three missing names across two groups.",
            "Open Python in Matched: show JD quote, candidate quote, 12.50 points and next action. Open Docker gap: no candidate evidence, 0.00 points.",
            "Choose Explore in Career GPS. This navigation must not automatically apply the missing skill. Toggle Docker: projected match 87.5%, readiness stays 74.9%.",
            "Set SQL hypothetical level to 9: readiness 79.5%; named match remains 87.5%. Add AWS: match 100% because AWS OR GCP is satisfied.",
            "Reset scenario: 75.0% / 74.9%. Return to Profile Builder: SQL still 4; no actual Docker/AWS claim was added.",
        ],
        talk=[
            (
                "0:00-0:35",
                "My module compares this candidate with this particular JD. Company readiness is a separate result.",
            ),
            (
                "0:35-1:25",
                "Show 75% and its missing list. Explain weight 6 of 8 rather than a mysterious AI-generated number.",
            ),
            (
                "1:25-2:15",
                "Open Python and Docker reasoning chains. Distinguish supported evidence from an actual capability gap.",
            ),
            (
                "2:15-3:20",
                "Simulate Docker and SQL. Show two separate score changes and explain why they differ.",
            ),
            (
                "3:20-4:00",
                "Reset and verify saved inputs unchanged. Close with an honest limitation and the complete five-module journey.",
            ),
        ],
        qa=[
            (
                "Why not match only by category?",
                "Knowing one AI technology does not prove another named tool. Exact names/reviewed aliases are safer; fuzzy similarity only suggests review.",
            ),
            (
                "Can 100% mean guaranteed selection?",
                "No. It means coverage of the reviewed extracted requirement groups, not a hiring probability or verified competence.",
            ),
            (
                "Does the simulation improve the real profile?",
                "No. It copies inputs and recalculates. Real changes require explicit editing/saving in Profile Builder.",
            ),
        ],
        transition="Together the five modules connect original job text, candidate claims, saved profile, company readiness and reversible next-step exploration.",
    ),
]
