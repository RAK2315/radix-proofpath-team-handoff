# Profile Builder - teammate guide (editable)

Assume you own this module. Run/test it and push your working copy to YOUR OWN GitHub. Return URL, SHA, evidence and limitations; no central PR is required.

## Your responsibility

Combine reviewed resume information with manual details into one saved candidate profile. This is the stable record that both assessment modules use.

## Required input

Manual details, an optional reviewed resume ID, optional CV upload, and twelve optional 1-10 self-ratings.

## Guaranteed output

A saved Profile with an ID/revision, background fields, source-linked claims, CV reference and exactly twelve rating entries. Unknown ratings remain null.

## Organizer requirement

Participant Brief p.8 requires basics, skills, hackathons/internships, certifications, preferred roles and CV upload, with save/load. Resume prefill is desirable. Evidence passport and explicit self-ratings support our integrated design.

## Build in order

1. **Start manually** - Create a Profile with a nonblank name. Let defaults fill arrays and twelve null ratings. Do not block consumers waiting for resume extraction.
2. **Build all sections** - Keep name/email, education, projects, experience, internships, hackathons, certifications, preferred roles and achievements. Treat multiline entries as string arrays.
3. **Import a reviewed resume** - POST import-resume with the current profile draft. Default replace_existing=false preserves nonempty manual fields; import returns a preview, not a saved record.
4. **Preserve evidence** - Keep source_document_id, exact quotes, confidence, claim basis and review state on imported skills. A duplicate name must not hide a new conflicting claim.
5. **Separate ratings** - Show twelve Unknown/1-10 controls. Parse Unknown as null, not zero. Keep self_reported origin. Importing evidence cannot increase any rating.
6. **Save safely** - Use POST for create and PATCH with the full current Profile/revision for updates. Retain drafts on failure; reconcile 409 conflicts rather than silently overwriting.
7. **Prove both consumers** - Reload the saved record and select it in Talent Check and Skill Matching. Export a small synthetic handoff only; do not share private CVs or keys.

## Run and verify

Use README.md for fresh setup. From the full repo root:

```powershell
.\profile_builder\run.ps1 api
# Separate terminal:
.\profile_builder\run.ps1 web
# Verify:
.\profile_builder\run.ps1 check
```

## Screen structure

- **1  START: New profile | Import reviewed resume** - Select an existing saved profile or create a new draft; import is optional.
- **2  BASICS + STORY: Name/email + experience sections** - Readable labelled forms, one entry per line. Show the attached CV reference.
- **3  PASSPORT: Skills + source links + confidence** - Keep manual and document claims distinguishable. Review conflicts before matching.
- **4  SELF-RATINGS: 12 RADIX categories: Unknown or 1-10** - Separate panel on desktop; stack below form on mobile. Explain that the rubric is team-designed.
- **5  SAVE: Save profile -> assessments** - Show saved version, unsaved changes, successful save and useful errors.

## API endpoints

- `POST /api/profiles` - Create validated Profile; returns 201 and saved revision.
- `POST /api/profiles/import-resume` - resume_id + profile + replace_existing=false; merged draft only.
- `GET /api/profiles[/ID]` - List/load owned profiles.
- `PATCH /api/profiles/ID` - Full Profile with current revision; increments on success.
- `DELETE /api/profiles/ID` - Delete owned profile and invalidate receipts.
- `POST /api/documents` - Multipart CV attachment; use returned document ID as cv_file.

See request-example.json and the FULL response-example.json here. Canonical required/optional fields and types are in shared/contracts/models.py and shared/contracts/openapi.json.

## Logic

Module 3 owns candidate persistence. A parsed resume is an input, not a replacement for the user's existing profile. Keep review provenance and competency separate all the way through.

- **Import with replace_existing=false** - Fill empty background fields from the reviewed resume. Keep nonempty manual values. Merge skill names without losing a new conflicting source.
- **Import with replace_existing=true** - Explicitly replace imported background fields. Understand that current skill merging is still conservative; this option is not a blanket overwrite of all skill claims or ratings.
- **User adds evidence** - Add the source-backed claim if valid. Do not change a category rating, confidence-based proficiency or assessment score automatically.
- **Save profile** - Validate source ownership/quotes. Reject hypothetical source claims. Persist the current revision, and invalidate old evaluation receipts on changes.
- **User selects Unknown** - Store null. Numeric values must be finite 1-10, not booleans or 0. Keep exactly one row for each official category.

A manually entered skill is self-reported, not document-verified. All verification_status values remain unverified. Source deletion removes dependent document claims; saved self-ratings remain self-reported.

## Tests

Read TESTING.md for three normal and three failure cases. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest profile_builder/tests -q
npm run test -- profile_builder/frontend
```

## Demonstration

1. Open Profile Builder. Import the reviewed Mira resume. Explain that this creates an editable draft.
2. Show education/projects/internship, CV link and the six source-linked skills. Add preferred role Junior Data Engineer if desired.
3. Point out all twelve ratings are initially Unknown. This is the important invariant after parsing/import.
4. For the synthetic numeric demo only, deliberately set every category to 4 and say these are invented self-ratings. Click Save profile.
5. Reload the page, show the saved version and unchanged fields, then hand the same profile ID/revision to Modules 4 and 5.

## Explain to judges

- 0:00-0:35: My module turns extracted evidence and manual information into one saved candidate record.
- 0:35-1:25: Show the reviewed resume import and additional story fields. Explain that import previews, Save persists.
- 1:25-2:15: Open a source claim and show Unknown ratings. Explain why evidence confidence is not proficiency.
- 2:15-3:10: Enter clearly labelled synthetic ratings, save and reload. Describe revision checks and private ownership.
- 3:10-4:00: Hand the same profile ID to both assessors. Explain one conflict/failure behavior and the passport's current limits.

## Likely questions

**Why not rate from the resume automatically?** Mentions and confidence are not measured ability. Unknown stays null; the user supplies explicit self-ratings.

**What happens when two people edit?** Current revision checks reject stale saves with 409. The UI keeps the draft for reconciliation.

**Is it a full evidence history?** It saves current claims, sources and revision. A historical timeline is not implemented.

## Return to Scrum Master

Publish to your own GitHub repository and fill DELIVERY.md with actual executed results. Follow ../SUBMIT_YOUR_REPOSITORY.md. Never commit private CVs or secrets. Live Groq, Supabase and organizer data remain pending unless actually verified.
