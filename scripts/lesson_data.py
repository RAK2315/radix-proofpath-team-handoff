"""Beginner lessons. Written for this handoff, independently of the archived manuals."""

LESSONS = {
    "jd_analytics": {
        "number": 1,
        "title": "JD Analytics",
        "tagline": "Turn a job advert into clear requirements.",
        "purpose": "Help a student see what a job actually asks for. A JD is a job description. Your part reads it, lists the skills and keeps the words that support each requirement.",
        "why": "Skill Matching cannot make a fair comparison until it knows which skills are required, which are preferred and which are alternatives.",
        "input": "A job description as PDF, Word (.docx) or pasted text.",
        "output": "A saved, reviewed list of skills, categories and requirement groups, linked to the original text.",
        "example": "An advert says Required: Python. The result contains Python, category COD (Coding), the quote Required: Python and a mandatory group. It does not invent a proficiency level.",
        "requirements": [
            "Read any text-based PDF or DOCX JD and return a structured skill list, not just a summary.",
            "Use LLM extraction: an LLM is a language model that can interpret prose. Keep the existing Groq path; a keyword-only demo does not verify this requirement.",
            "Place each skill in exactly one of the twelve RADIX categories, or OTHER when none fits. Keep named technologies such as Python.",
            "Run on its own with at least two different JDs and send the saved result to Module 5. Test the official examples when organizers supply them.",
        ],
        "built": "Upload and paste, PDF/Word reading, direct Groq structured extraction, checked quotes, skill editing, required/preferred groups, AND/OR alternatives, saved revisions and a review screen already work. Groq is implemented and mock-tested, not live-verified.",
        "tasks": [
            "Run the existing part before editing it. Use the tiny Python sample and a different JD from data/synthetic/reconstructed/.",
            "Compare every extracted skill and group with the document. Correct omissions through the review screen; investigate the parser only when you can reproduce the error.",
            "Improve an actual weakness, such as bare Testing or unfamiliar terms, and add a test using that exact wording. Keep false positives visible too.",
            "Verify save/reload and the handoff into matching. If you have an authorized Groq key, test a synthetic document with explicit consent and record real model quality separately.",
        ],
        "missing": "Official organizer JDs and live Groq evaluation are pending. Scanned image PDFs have no OCR (image-to-text reading) here. Do not rebuild the functioning upload or scoring system.",
        "innovation": "ProofPath adds importance, AND/OR groups and source links. These are team extensions. Preserve them; do not describe team weights as an employer's official scoring policy.",
        "flow": [
            (
                "Choose input",
                "The user uploads PDF/Word or pastes the full JD. Pasted text is also kept as a private source document.",
            ),
            (
                "Read text",
                "The shared reader extracts page text. Empty, broken or unsupported files produce an error.",
            ),
            (
                "Find requirements",
                "With a configured key and this input's permission, Groq proposes structured fields. Otherwise limited local rules run and the screen says so.",
            ),
            (
                "Check evidence",
                "The server checks each proposed quote against the supplied text. A language model cannot create a new source or a skill rating.",
            ),
            (
                "Review and save",
                "The user edits names, categories, importance and alternatives, then saves a reviewed revision.",
            ),
            (
                "Hand off",
                "Module 5 loads this saved JD and its current revision. Later edits require a new comparison.",
            ),
        ],
        "request_file": "input.json",
        "response_file": "output.json",
        "request_intro": "The full request example describes a file upload. It is a description of the form fields, not a JSON body to send to this endpoint. The browser sends the actual file as multipart/form-data: a form that can carry a file.",
        "endpoint": "POST /api/jd/extract",
        "receiver": "A candidate supplies the file; Module 5 receives the reviewed Extraction result.",
        "fields": [
            (
                "file / hosted_consent",
                "The file is required. Consent defaults to false; true allows this input's text to reach the configured provider.",
            ),
            (
                "id / revision / document_id",
                "Server-created record ID, saved version and private source ID. Example IDs are snapshots; use new IDs returned by your own run.",
            ),
            (
                "skills / requirement_groups",
                "Skill objects contain names, category codes, quotes and source links. Groups refer to skill_id values and say AND/OR and mandatory/preferred/unspecified.",
            ),
            (
                "review_status / llm_status",
                "needs_review means a human must check it. rules_only means local rules; processed means the model returned accepted output. Neither proves semantic accuracy.",
            ),
        ],
        "api_notes": "Paste uses POST /api/jd/extract-text with required text (15-120000 characters), optional source_name and hosted_consent=false. GET /api/jd/{id} loads it; PATCH /api/jd/{id} sends the complete edited Extraction, retaining id and revision. Save with review_status=reviewed. A stale save returns 409, meaning reload before retrying.",
        "sources": [
            (
                "backend/service.py",
                "Start here. Finds requirements, groups and local parsing warnings; supplies the JD instructions to Groq.",
            ),
            (
                "backend/router.py",
                "Receives pasted input and joins the upload/review routes. A route is the server address that handles a request.",
            ),
            ("frontend/JDAnalyticsPage.tsx", "Owns upload, extraction and save actions on the screen."),
            (
                "frontend/RequirementReview.tsx",
                "Edits importance, alternatives and group review; PasteJD.tsx owns pasted input.",
            ),
        ],
        "shared_sources": "shared/integrations/llm.py (Groq calls), shared/integrations/extraction.py (grounding/local skills), shared/integrations/documents.py (file text), shared/contracts/models.py (agreed fields). Read these when needed; coordinate shared changes with the Scrum Master.",
        "screen": "Expect an Upload file / Paste text choice, editable company/role, skill cards with source links, requirement groups and Save reviewed JD. Try a source link before presenting the result.",
        "tests": [
            (
                "Python sample",
                "Upload samples/practice-jd-SYNTHETIC.docx, then its PDF. Both should find Python/COD and one mandatory group. Wrong: no Python, extra unrelated skills or a made-up rating.",
            ),
            (
                "Paste",
                "Paste Required: Python and SQL. Expect two skills in one AND group. Compare the exact source words and save/reload; do not accept a success message alone.",
            ),
            (
                "Different wording",
                "Try a reconstructed data JD and Required: Python and either PyTorch or TensorFlow. Inspect groups; the OR pair must not become two compulsory skills.",
            ),
            (
                "Bad or unknown input",
                "Try an empty file, text renamed .pdf and Required: Apache Arrow. Expect a useful error or a visible review warning; never quietly claim complete coverage.",
            ),
            (
                "Provider failure",
                "Without consent, no model call is allowed. Mock tests cover bad quotes and provider failure. A fallback must say rules/unavailable; HTTP 200 alone does not prove LLM use.",
            ),
        ],
        "judge": "I own the part that turns a job advert into requirements. It accepts a PDF, Word file or pasted text. Our existing Groq path can interpret prose when configured and permitted; local rules remain clearly labelled. Every proposed skill keeps source evidence. The user reviews importance and alternatives before saving, and matching uses that saved version. My tests check the actual words and groups, including failure cases. Live model quality and the official organizer pack are separate pending checks.",
        "questions": [
            (
                "Why not just count keywords?",
                "Prose contains alternatives, negation and implied requirements. Rules are a limited fallback; the LLM path still needs a live quality test.",
            ),
            (
                "Is confidence a skill level?",
                "No. It describes support for the extraction, not the candidate's ability.",
            ),
            (
                "How does another module use it?",
                "Module 5 loads the reviewed JD by ID and revision using the shared fields.",
            ),
        ],
    },
    "resume_parsing": {
        "number": 2,
        "title": "Resume Parsing",
        "tagline": "Read a CV and show what supports each claim.",
        "purpose": "Read a candidate's CV and turn its skills, education, projects and experience into editable information. A CV mention is a claim, not a measured ability score.",
        "why": "Typing every CV field is slow. Your part gives Profile Builder a useful starting point while letting the candidate correct mistakes.",
        "input": "A text-based resume PDF or Word (.docx) file, plus optional permission to use Groq.",
        "output": "A reviewed resume record containing skill claims, source quotes and the background fields that can be supported by the CV.",
        "example": "Asha's synthetic CV says Python and describes a Python quiz. Show Python/COD and the quoted text, plus the project and education. Do not turn that mention into Python level 8.",
        "requirements": [
            "Accept a resume PDF or DOCX, including layouts that differ from the sample.",
            "Use the LLM extraction pattern to find technologies and technical signal; preserve the existing Groq implementation. Rules-only output is a fallback, not verified LLM extraction.",
            "Return skills in the shared format, each with one RADIX category or OTHER and supporting evidence. Return education, projects and experience when reliably present.",
            "Run independently on at least two different resumes; send the reviewed output to Module 3. Test the missing official sample pack when it becomes available.",
        ],
        "built": "PDF/Word upload, section reading, direct Groq structured proposals, checked quotes, editable fields, negation/review flags and reviewed save/reload already work. No numeric proficiency is inferred. Actual Groq quality remains unverified.",
        "tasks": [
            "Run the existing upload screen and the supplied single-skill CV first. Read the source and compare every returned field.",
            "Try a second layout. Check whether projects and internships stay in the right sections; missing fields should remain empty, not invented.",
            "Reproduce and improve one real omission or layout problem. Add a regression test so that exact error cannot quietly return.",
            "Save the reviewed CV, import it into Profile Builder and confirm that all twelve ratings are still Unknown. Test Groq separately if a private authorized key becomes available.",
        ],
        "missing": "Original organizer resumes and live Groq evaluation are pending. OCR for image-only PDFs and perfect understanding of every layout are not implemented. Current rules can miss Rust, implicit data cleaning and some wrapped skills.",
        "innovation": "ProofPath connects a skill claim to the page and words that support it. Conflicting or negative claims remain visible for review. Preserve this trail; a reviewed claim is still not independently verified competence.",
        "flow": [
            (
                "Upload",
                "The candidate chooses a PDF or Word CV. The existing reader handles text-based files and checks file validity.",
            ),
            (
                "Read sections",
                "Page text and headings help separate education, projects, work and other background.",
            ),
            (
                "Extract fields",
                "Groq identifies structured claims when configured and explicitly allowed. Otherwise local rules run with an honest label.",
            ),
            (
                "Check quotes",
                "The server checks proposed words against the source. Unsupported fields cannot become trusted source facts.",
            ),
            (
                "Review",
                "The candidate fixes names, fields, categories and claims, then saves a reviewed resume.",
            ),
            (
                "Import",
                "Module 3 imports the reviewed record as a draft. Only a profile save makes it the profile used by assessments.",
            ),
        ],
        "request_file": "input.json",
        "response_file": "output.json",
        "request_intro": "This complete request example describes the upload form. Send the actual file, not this JSON object, to the endpoint. multipart/form-data means the browser form contains file bytes as well as ordinary fields.",
        "endpoint": "POST /api/resumes/extract",
        "receiver": "The candidate provides the CV; Module 3 receives the reviewed Extraction result.",
        "fields": [
            (
                "file / hosted_consent",
                "File is required. Consent defaults to false and applies to this input only.",
            ),
            (
                "name / email / section arrays",
                "Background values supported by the CV. Empty arrays mean no reliable extracted entry; they are not proof of no experience.",
            ),
            (
                "skills / evidence / source_document_id",
                "Named claims, exact quotes and a private document link. verification_status stays unverified; confidence is separate from ability.",
            ),
            (
                "id / revision / review_status",
                "Keep the returned ID and version when saving. Set reviewed only after checking. Source and skill IDs in the printed example belong to that captured run.",
            ),
        ],
        "api_notes": "GET /api/resumes/{id} loads the record. PATCH /api/resumes/{id} sends the complete edited Extraction with the same id/current revision and review_status=reviewed. Module 3 uses POST /api/profiles/import-resume with resume_id, a profile draft and optional replace_existing=false. Unreviewed imports are rejected.",
        "sources": [
            (
                "backend/service.py",
                "Open first. Reads headings/background and supplies the resume extraction instructions.",
            ),
            ("backend/router.py", "Connects the feature to common upload, load and review routes."),
            (
                "frontend/ResumeParsingPage.tsx",
                "Displays upload, editable extracted sections, skill claims and review/save controls.",
            ),
            (
                "tests/test_extraction.py",
                "Small backend examples that show how the parser is expected to behave.",
            ),
        ],
        "shared_sources": "shared/integrations/llm.py (Groq), shared/integrations/extraction.py (quotes and skills), shared/integrations/documents.py (reading files), shared/contracts/models.py (fields). Request these exact files from your assistant if the bug crosses the feature boundary.",
        "screen": "Expect a CV file choice, extracted name/background, editable skills and source evidence, then Save reviewed resume. Show a project quote and an error state as well as the success screen.",
        "tests": [
            (
                "Basic CV",
                "Upload samples/practice-cv-SYNTHETIC.pdf, then .docx. Expect Asha Sample, Python/COD, the quiz project and invented education. Wrong: invented employment or an automatic rating.",
            ),
            (
                "Second layout",
                "Use a different synthetic CV in data/synthetic/reconstructed/ or extraction-eval/documents/. Compare sections and quotes, not candidate names or a fixed expected skill count.",
            ),
            (
                "Negation/conflict",
                "Try authorized text saying No production Kubernetes experience. It must not become a positive proven ability. Keep uncertainty visible for human review.",
            ),
            (
                "Broken/empty CV",
                "Upload an empty file or text renamed .pdf. Expect a clear error and the ability to try again. An image-only PDF needs readable text/OCR outside this implementation.",
            ),
            (
                "Review/import",
                "Save corrected fields, reload and import the reviewed result into Module 3. The fields should survive and all twelve ability ratings should stay Unknown.",
            ),
        ],
        "judge": "My module reads a resume and prepares editable information for Profile Builder. It finds named skill claims and reliable education, projects and experience, with links to the supporting source. The existing Groq path checks structured proposals and quotes; local rules are a clearly labelled fallback. A person reviews the result before import. I test different layouts, missing fields and misleading claims. A CV mention never becomes a proficiency score. Live model quality and original organizer resumes remain separate checks.",
        "questions": [
            (
                "Does Python in a CV prove expertise?",
                "No. It supports an unverified claim. Numeric self-ratings are entered separately.",
            ),
            (
                "What if a field is missing?",
                "Leave it empty and let the candidate add it; do not fabricate details.",
            ),
            (
                "What about scanned resumes?",
                "This reader needs text. Image-only PDFs need OCR, which is not included here.",
            ),
        ],
    },
    "profile_builder": {
        "number": 3,
        "title": "Profile Builder",
        "tagline": "Save one useful profile for both assessments.",
        "purpose": "Let a candidate combine reviewed CV information with details the CV may miss. Save it so both assessments use the same candidate record.",
        "why": "A resume is only a starting point. Hackathons, internships, certificates and preferred roles help create a fuller profile. Later edits must persist correctly.",
        "input": "Manual form entries, an optional reviewed resume from Module 2 and an optional CV upload.",
        "output": "A saved candidate profile with its ID and revision, editable background, source-linked claims and twelve separate self-ratings that may stay Unknown.",
        "example": "Asha adds her name and preferred role, saves, then reloads the page. Her details remain. Importing a CV fills a draft; it does not silently replace her saved edits or assign ability levels.",
        "requirements": [
            "Collect basic details, skills, hackathons/internships, certifications, preferred roles and a CV upload.",
            "Allow manual entry; pre-fill from Resume Parsing where available.",
            "Validate, save and load a profile in the shared JSON format. JSON means named fields in a text record that other modules can read.",
            "Run without a live parser, and give the same saved profile to Modules 4 and 5. Use ordinary code; this form does not need an LLM.",
        ],
        "built": "The form, direct CV upload, reviewed-resume import, fill-empty/replace choice, create/load/update/delete, local persistence and revision checks already work. The passport shows current claims and source links.",
        "tasks": [
            "Run the form, create a manual profile and reload it. Check all required background fields, not just name and skills.",
            "Load the supplied reviewed resume through the local synthetic workspace. Import, inspect the draft and save deliberately.",
            "Test fill-empty versus replace: keep a manual education entry, import again, and confirm it only changes when replacement is explicitly selected.",
            "Check invalid entries, stale saves, source links and both assessment handoffs. Improve only a reproduced issue; add a test for that issue.",
        ],
        "missing": "Live Supabase persistence and official sample acceptance remain unverified. The passport does not keep an immutable historical timeline. Do not promise that feature or rebuild the working form.",
        "innovation": "The Living Skill Passport already keeps current claims, quotes and profile revision. Evidence confidence remains separate from twelve optional numeric self-ratings. Adding a quote must never raise a rating automatically.",
        "flow": [
            ("Start", "Create a blank profile or choose a reviewed resume. Both paths work without Groq."),
            (
                "Fill the draft",
                "Import fills supported fields. Existing manual fields are preserved unless Replace is selected.",
            ),
            (
                "Add details",
                "Enter projects, internships, hackathons, certificates, preferred roles and CV reference. Inspect skills and their sources.",
            ),
            (
                "Keep ratings separate",
                "Each official category starts as Unknown (JSON null). A user may explicitly choose a self-rating from 1 to 10.",
            ),
            (
                "Save and reload",
                "The server checks fields and source ownership, saves the profile and returns its current version. A conflicting old save is rejected.",
            ),
            (
                "Assess",
                "Modules 4 and 5 load this same saved ID/version. Career GPS makes a temporary copy and cannot save hypothetical claims here.",
            ),
        ],
        "request_file": "input.json",
        "response_file": "output.json",
        "endpoint": "POST /api/profiles",
        "request_intro": "Send the following complete JSON body to create a simple manual profile. Only name is mandatory on creation; omitted fields receive the defaults shown in the complete response. This example deliberately has no imported claims.",
        "receiver": "The user and optional Module 2 provide inputs. Modules 4 and 5 receive the saved Profile.",
        "fields": [
            (
                "name / email / background",
                "name is required and cannot be blank. Email may be empty but must have a valid shape if supplied. Education and other multi-entry fields are arrays.",
            ),
            (
                "skills / cv_file",
                "Skills follow the shared Skill fields. cv_file is a private document ID, not a public URL or a path to somebody's computer.",
            ),
            (
                "ratings",
                "Exactly twelve category entries are stored; each level is null (Unknown) or a number 1-10 with self_reported origin. OTHER is not a thirteenth rating.",
            ),
            (
                "id / revision",
                "The server returns the profile identity/version. Keep both on update; do not hardcode the example's generated ID into the UI.",
            ),
        ],
        "api_notes": "GET /api/profiles lists records; GET /api/profiles/{id} loads one. PATCH /api/profiles/{id} needs the full Profile with its current revision; DELETE removes it. POST /api/profiles/import-resume needs resume_id and profile, with replace_existing=false by default. It returns a draft; save that draft explicitly. POST /api/documents uploads a CV without extracting it.",
        "sources": [
            (
                "frontend/ProfileBuilderPage.tsx",
                "Open first. The form, import preview, save button and rating controls live here.",
            ),
            (
                "backend/service.py",
                "Combines reviewed fields, preserves manual entries and checks that source documents belong to the user.",
            ),
            ("backend/router.py", "Creates, loads, updates, imports and deletes records."),
            ("tests/test_final_merge.py", "Examples for import conflicts, replacement and unknown ratings."),
        ],
        "shared_sources": "shared/contracts/models.py defines Profile, Skill and Rating. shared/integrations/store.py saves records; documents.py handles CVs. Read those if needed, but coordinate any shared storage/schema change with the Scrum Master.",
        "screen": "Expect basic/background fields, import preview and replacement choice, a source-linked skill passport, twelve Unknown/1-10 controls and Save profile. Show persistence after reload; a success toast alone is insufficient.",
        "tests": [
            (
                "Manual save",
                "Enter samples/input.json values. Save/reload: name, education and preferred role remain. Compare output.json; IDs vary, twelve null ratings do not. Attach samples/cv-upload-SYNTHETIC.pdf and check the saved CV opens correctly.",
            ),
            (
                "Import",
                "Read samples/reviewed-resume.json, import-request.json and import-preview.json. Load synthetic inputs in the browser and import its reviewed resume. Preview must not silently save or rate skills.",
            ),
            (
                "Manual conflict",
                "Enter your own education, import without Replace and check it is preserved. Select Replace intentionally and check the preview changes before saving.",
            ),
            (
                "Invalid / old save",
                "Try a blank name, invalid email and ratings outside 1-10. Expect validation. A stale revision returns 409; keep the draft, reload and reconcile the changes.",
            ),
            (
                "Assessments / GPS",
                "Save a candidate and use the same ID in both assessments. Run a what-if and return: no hypothetical skills or ratings may appear in the saved profile.",
            ),
        ],
        "judge": "I own the candidate's saved profile. A person can type details or start from a reviewed resume, then add projects, hackathons, internships, certificates and preferred roles. Import first creates a draft, so it does not silently overwrite saved work. The profile keeps evidence links and separate optional self-ratings; Unknown stays unknown. Both assessments load the same saved revision. I verify save/reload, import conflicts and invalid entries. The current passport is persistent, but it is not an immutable history timeline.",
        "questions": [
            (
                "Does import save automatically?",
                "No. The user inspects the merged draft and explicitly saves it.",
            ),
            (
                "Why are ratings Unknown?",
                "A CV mention does not measure proficiency. Only an explicit self-rating sets a number.",
            ),
            (
                "What happens if two edits conflict?",
                "An old revision is rejected with 409 so the user can reload and reconcile.",
            ),
        ],
    },
    "talent_check": {
        "number": 4,
        "title": "Talent Check",
        "tagline": "Compare twelve self-ratings with one company's bar.",
        "purpose": "Show a candidate where their own stated levels meet or fall below a selected company's twelve expected levels. Explain every row and the overall calculation.",
        "why": "Company readiness is different from matching a single advert. The user needs to see which broad categories need attention and where the standards came from.",
        "input": "A saved profile from Module 3 and a selected company with an authorized twelve-category benchmark.",
        "output": "An overall readiness percentage when all ratings are known, twelve comparison rows, gaps, actions and the benchmark source. Missing ratings produce an incomplete result, not fake zero ability.",
        "example": "In our invented lab, Asha rates SQL as 4 and Synthetic Data Co expects 9. SQL attainment is 4/9; its share is (4/9)/12 x 100 = 3.7037 points. All twelve lab ratings at 4 give 74.9% overall.",
        "requirements": [
            "Load a saved candidate profile and let the user select one company.",
            "Compare across all twelve official RADIX categories, showing candidate and required levels and the gap.",
            "Return a readiness score and per-category breakdown using an explicitly defined formula. The brief permits a team scoring decision; it does not prescribe this formula.",
            "Use real organizer expectations for official readiness. The current organizer table is staging_company_skill_levels; access stays read-only. Run independently using clearly synthetic fixtures while access is missing.",
        ],
        "built": "Read-only benchmark loading/mapping/validation, explicit synthetic mode, twelve-row scoring, unknown-rating handling, source receipts and the comparison screen already work. Career GPS reuses this same scorer.",
        "tasks": [
            "Run the working screen with Synthetic Data Co. Independently calculate two rows and the whole percentage from the provided values.",
            "Compare two candidate profiles or change one explicit rating. Show a real arithmetic change, not a hardcoded score.",
            "Test Unknown, missing company, malformed benchmarks and unavailable real source. Improve a reproduced failure and add a test.",
            "When the Scrum Master has authorized organizer access, confirm actual column mappings and all twelve values. Keep real-source acceptance pending until that succeeds.",
        ],
        "missing": "Actual organizer schema, authorized access and real company values are unavailable. Live Supabase acceptance is pending. Never fill these gaps with invented Google/Microsoft/Oracle expectations.",
        "innovation": "ProofPath shows row contributions, source provenance and useful next actions. Evidence coverage is a separate count; adding quotes does not change readiness unless the user changes a self-rating.",
        "flow": [
            (
                "Choose profile",
                "Read the saved candidate's twelve explicit self-ratings. Skill mentions do not supply those numbers.",
            ),
            (
                "Choose source",
                "The user explicitly selects synthetic mode for lab data. Real mode requires a genuine authorized source.",
            ),
            (
                "Validate company",
                "Require exactly twelve unique category values in range 1-10. Missing or invalid data returns a useful error.",
            ),
            (
                "Compare rows",
                "For each category: attainment = min(candidate / required, 1). A higher self-rating cannot contribute more than that category's full share.",
            ),
            (
                "Calculate",
                "If all twelve ratings are known, average the twelve attainments x 100, rounded to one decimal. Otherwise show a null overall score and unknown rows.",
            ),
            (
                "Explain",
                "Show candidate, required, shortfall, contribution and source. Save the result receipt; pass the same evaluator to GPS.",
            ),
        ],
        "request_file": "input.json",
        "response_file": "output.json",
        "endpoint": "POST /api/talent-check/evaluate",
        "request_intro": "Send this complete JSON request. profile_id must identify a profile already saved in your own workspace. This example uses the synthetic candidate.json with twelve explicit level-4 ratings and company.json's invented lab values.",
        "receiver": "Module 3 supplies the saved Profile. The user sees readiness; Module 5's GPS reuses the pure calculation for previews.",
        "fields": [
            (
                "profile_id / company_id / benchmark_mode",
                "profile_id and a company selection are required for this route. Mode defaults to real; synthetic must be chosen explicitly. Do not silently switch modes on failure.",
            ),
            (
                "skillset_gap",
                "Exactly twelve rows. required_level is a benchmark, candidate_level is a self-rating, gap is true/false/null and contribution is that row's score share.",
            ),
            (
                "readiness_score / status",
                "0-100 only when all twelve ratings exist; otherwise null and incomplete. rating_completeness counts known ratings, not proven ability.",
            ),
            (
                "benchmark_source / hash / receipt_id",
                "Where the values came from, which snapshot was used and the saved result reference. Synthetic source notice must remain visible.",
            ),
        ],
        "api_notes": "GET /api/talent-check/companies?mode=synthetic lists lab companies. Without that parameter it requests real data. GET /api/talent-check/benchmark-status explains real-source availability. Evaluations use the profile's current saved revision and record the benchmark snapshot. Unknown is never converted to zero.",
        "sources": [
            (
                "backend/scoring.py",
                "Open first. Short, deterministic twelve-category calculation; used again by GPS.",
            ),
            (
                "backend/benchmark_repository.py",
                "Loads and validates authorized real data or explicitly chosen synthetic values.",
            ),
            ("backend/router.py", "Loads the saved profile/company, runs scoring and records the result."),
            (
                "frontend/TalentCheckPage.tsx",
                "Shows the score, source information, twelve rows and related evidence.",
            ),
        ],
        "shared_sources": "shared/contracts/models.py defines Profile, ReadinessRow and ReadinessResult. shared/integrations/store.py loads profiles; receipts.py records source snapshots. Do not replace the shared model or add a second, conflicting GPS formula.",
        "screen": "Expect company/source selection, Run Talent Check, overall score or Incomplete, twelve readable rows, candidate-versus-required values and source details. The synthetic label must be obvious.",
        "tests": [
            (
                "Known arithmetic",
                "Use samples/candidate.json and company.json. The example command checks all twelve level-4 ratings give 74.9. Browser: Load synthetic inputs, choose Synthetic Data Co and run.",
            ),
            (
                "One category",
                "SQL is 4 versus 9: shortfall 5, attainment 0.4444..., contribution 3.7037 points. Wrong: confidence changes this number or evidence creates a higher level.",
            ),
            (
                "Unknown rating",
                "Clear a saved rating in the integrated Profile Builder, then assess. Expect twelve rows but incomplete/null score. The independent example's candidate is separate from your browser's records.",
            ),
            (
                "Unavailable source",
                "Choose missing/real company data without credentials. Expect a useful source error; do not display lab values as official or a fake 0% readiness.",
            ),
            (
                "Bad data / repeat",
                "Tests reject duplicate/missing/out-of-range benchmark categories. Repeat the same inputs: arithmetic must be identical even if receipt IDs or fetch timestamps differ.",
            ),
        ],
        "judge": "I compare a saved candidate's explicit self-ratings with one company's twelve-category expectations. Every row shows the required level, candidate level, gap and contribution. We average capped candidate-to-required ratios, so the calculation is explainable and repeatable. Unknown ratings keep the overall result incomplete. Lab values are visibly synthetic; official readiness needs authorized organizer data. Adding evidence does not raise ability. Career GPS calls this same scorer, so its preview uses consistent mathematics without saving profile changes.",
        "questions": [
            (
                "Is this a hiring probability?",
                "No. It is a transparent comparison of self-ratings and the chosen expectations.",
            ),
            (
                "What if a rating or benchmark is missing?",
                "A missing rating gives incomplete/null readiness; missing or invalid benchmarks give a source error.",
            ),
            (
                "Are the lab values official?",
                "No. They are invented and labelled; real organizer values still need authorized verification.",
            ),
        ],
    },
    "skill_matching": {
        "number": 5,
        "title": "Skill Matching + Career GPS",
        "tagline": "Explain one job match and explore a reversible next step.",
        "purpose": "Compare one saved candidate with one saved job description. Explain matched claims, evidence gaps and the reason for each score contribution. Let the candidate try temporary improvements.",
        "why": "A percentage alone does not tell a student what to do. The gap list and source reasoning show where the evidence does or does not cover this particular job.",
        "input": "A saved profile and reviewed JD from Modules 3 and 1. Company data is optional and is only needed for company-readiness previews.",
        "output": "A match percentage, matched/missing skills and contribution details. Career GPS returns separate hypothetical results and actions without changing the saved profile.",
        "example": "The tiny teaching JD requires Python and the candidate has no entered skills. Match is 0%. Add hypothetical Python: projected match is 100%, while the saved profile stays empty. This describes entered evidence coverage, not true ability.",
        "requirements": [
            "Compare a profile or resume-derived skill list with one extracted JD, not a company's general reputation. This UI uses the saved profile; import a reviewed resume through Module 3 first.",
            "Return a 0-100 match score plus matched and missing skills. Explain gaps rather than giving only a number.",
            "Handle equivalent names using exact/alias/fuzzy review logic. The brief allows simple matching here; an LLM is not mandatory for this module.",
            "Run independently with saved input fixtures and visibly differ across candidates and JDs. Preserve the shared handoff format and the full integrated journey.",
        ],
        "built": "Alias normalization, required/preferred weights, AND/OR groups, duplicate handling, uncertain states, source decisions, GPS recalculation, ranked suggestions, reset and stale-version checks already work.",
        "tasks": [
            "Run the tiny 0-to-100 terminal example, then the richer Mira browser demo (75 to 87.5 with Docker). These are different inputs, so their scores differ.",
            "Follow a matched and missing decision from JD words to candidate claim or absence, contribution and suggested action.",
            "Test aliases, OR alternatives, empty JD, conflicting claims and stale revisions. Improve only a reproduced issue and add a test.",
            "Verify GPS arithmetic, reset and identical saved profile JSON before/after. Never save a hypothetical skill or silently mark a fuzzy suggestion as matched.",
        ],
        "missing": "Official sample acceptance is pending. Fuzzy suggestions need human confirmation; unknown terms can leave results provisional. GPS does not promise a learning time or a guaranteed job outcome.",
        "innovation": "ProofPath connects JD quote -> CV claim/absence -> score contribution -> gap -> action. GPS separately changes hypothetical named claims or category levels. Evidence confidence cannot stand in for actual competency.",
        "flow": [
            (
                "Load pair",
                "Read the current saved profile and reviewed JD. A specific job is necessary; a company name alone is not enough.",
            ),
            (
                "Compare names",
                "Normalize aliases such as JS/JavaScript. Unconfirmed fuzzy suggestions or conflicting claims remain review items.",
            ),
            (
                "Score groups",
                "Mandatory groups weigh 2, preferred/unspecified weigh 1. AND gets the fraction matched; OR is covered if any member matches.",
            ),
            (
                "Explain",
                "Score = 100 x weighted coverage / total weight. Show the exact source, contribution and evidence gap. No JD requirements means unscorable/null, not 100%.",
            ),
            (
                "Try a change",
                "GPS copies the input, adds hypothetical claims or levels and runs the same matching/readiness functions again.",
            ),
            (
                "Reset",
                "Clear hypothetical changes and return to the baseline. Check the actual saved profile is identical. Stale versions require reloading the baseline.",
            ),
        ],
        "request_file": "input.json",
        "response_file": "output.json",
        "endpoint": "POST /api/matching/evaluate",
        "request_intro": "Send this complete JSON body using current saved IDs. The teaching sample has one reviewed mandatory Python requirement and an empty candidate skill list. Its complete 0% response follows; this is not the richer Mira browser fixture.",
        "receiver": "Module 1 supplies the reviewed JD; Module 3 supplies the saved profile. The user receives matching, explanations and optional GPS previews.",
        "fields": [
            (
                "profile_id / jd_id",
                "Both saved IDs are needed for matching. Numerical competency ratings and company benchmarks are not required for named-JD coverage.",
            ),
            (
                "match_score / status",
                "Coverage of extracted groups, not a hiring probability. complete, provisional or unscorable explains whether unresolved input remains.",
            ),
            (
                "matched_skills / missing_skills",
                "Decisions keep requirement importance, source evidence, reason and points. Missing evidence is not proof of missing ability.",
            ),
            (
                "contributions / revisions",
                "One contribution per requirement group; weights and coverage explain the total. Revisions bind calculations to the saved inputs.",
            ),
        ],
        "api_notes": "POST /api/matching/scenarios/preview takes profile_id, jd_id, profile_revision, jd_revision, optional skill_overrides/category_overrides and optional company selection. samples/scenario-request.json is a full request; scenario-expected.json is a labelled result summary, not the complete ScenarioResult. The full result contains baseline/projected match, optional baseline/projected readiness, deltas, recommendations and a notice. Preview never updates Profile.",
        "sources": [
            (
                "backend/matcher.py",
                "Open first. Name aliases, requirement groups, contributions and matching decisions.",
            ),
            (
                "backend/scenarios.py",
                "Copies input, recalculates previews and ranks single-change suggestions.",
            ),
            ("backend/router.py", "Loads saved inputs, checks versions and exposes evaluate/preview routes."),
            (
                "frontend/SkillMatchingPage.tsx",
                "Shows scores, decisions, controls and reset. ReasoningChain.tsx shows source-to-action explanations.",
            ),
        ],
        "shared_sources": "shared/contracts/models.py defines MatchingResult and ScenarioRequest/Result. talent_check/backend/scoring.py and benchmark_repository.py are existing pure-code dependencies in the same clone; no second teammate server is needed. shared/integrations/receipts.py keeps result snapshots.",
        "screen": "Expect a candidate/job pair, Analyze this match, matched and gap lists, a clickable explanation chain, and Career GPS with baseline/projected scores and Reset. Keep job coverage and company readiness clearly named.",
        "tests": [
            (
                "Tiny pair",
                "samples/profile.json has no entered skills; jd.json requires Python. The example command must return 0%, then 100% after hypothetical Python, with saved profile unchanged.",
            ),
            (
                "Richer browser pair",
                "Load synthetic inputs and analyze Mira/Junior Data Engineer: 75%. Hypothetical Docker gives 87.5%. Reset returns 75%. These fixtures differ from the tiny JSON example.",
            ),
            (
                "Source reasoning",
                "Open a Python match in the richer pair: its two-word mandatory AND group gives Python 12.50 points. Open Docker's gap: no equivalent claim and zero contribution.",
            ),
            (
                "Aliases / alternatives",
                "Tests compare JS/JavaScript and AWS OR GCP. An alias may match; a spelling suggestion must not silently earn points. One OR member is enough.",
            ),
            (
                "Empty / stale / unchanged",
                "Empty JD gives null/unscorable; a stale revision gives 409. Check saved profile JSON before/after scenarios and reset; any added hypothetical claim is a bug.",
            ),
        ],
        "judge": "My part compares a candidate with one actual job description and explains the result. It scores reviewed requirement groups, handles aliases and alternatives, and shows matched evidence and gaps. Each decision connects the JD words to a candidate claim or absence and its score contribution. Career GPS tries temporary changes and reruns the same mathematics. Reset restores the baseline, and saved profile data never changes. Confidence is separate from ability, and the score measures extracted requirement coverage rather than a hiring guarantee.",
        "questions": [
            (
                "Does 100% guarantee selection?",
                "No. It means coverage of the extracted, reviewed requirement groups for these inputs.",
            ),
            (
                "Can a what-if change my real skills?",
                "No. It uses a temporary copy; saved profile equality is tested.",
            ),
            (
                "Is company readiness the same score?",
                "No. Named-JD coverage and twelve-category self-rating comparison use different inputs and formulas.",
            ),
        ],
    },
}
