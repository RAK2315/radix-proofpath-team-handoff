# Talent Check - teammate guide (editable)

Assume you own this module. Run/test it and push your working copy to YOUR OWN GitHub. Return URL, SHA, evidence and limitations; no central PR is required.

## Your responsibility

Compare a saved candidate's twelve explicit competency self-ratings with the selected company's twelve expected levels. Show what is known, the gaps and every part of the arithmetic.

## Required input

A saved profile ID, a selected company ID, and explicit real or synthetic benchmark mode. A JD is not required.

## Guaranteed output

ReadinessResult: score or null, exactly twelve category rows, completeness, evidence coverage, benchmark provenance/hash and an inspectable receipt.

## Organizer requirement

Participant Brief p.8 requires a company readiness score plus per-category gaps across all twelve RADIX categories. Our host update identifies staging_company_skill_levels as the read-only source. Synthetic data cannot satisfy official-data acceptance.

## Build in order

1. **Agree what readiness means** - Read scoring.py and the formula on page 5. The equal-weight capped ratio is a team design decision, not an employer screening algorithm.
2. **Load a saved profile** - Use the same Profile contract as Module 3. Do not assign ratings, replace Unknown with zero or scrape named skill counts.
3. **Read a valid source** - Keep organizer access GET-only. Inspect actual schema before configuring mappings/filters. Each company needs exactly twelve unique valid 1-10 expectations.
4. **Handle unavailable data** - Return a clear source error. Synthetic lab mode must be deliberately selected and permanently labelled; never silently use it as official data.
5. **Compute one row per category** - Show candidate level, required level, shortfall, gap, attainment and contribution. Unknown values produce nulls; final score requires all twelve levels.
6. **Expose provenance** - Show source mode/table, fetched time/hash and rule version through result/receipt. Evidence coverage is a separate count, not a score multiplier.
7. **Prove reuse** - Compare two profiles, verify arithmetic and feed the same evaluator to GPS. Do not create a second inconsistent formula.

## Run and verify

Use README.md for fresh setup. From the full repo root:

```powershell
.\talent_check\run.ps1 api
# Separate terminal:
.\talent_check\run.ps1 web
# Verify:
.\talent_check\run.ps1 check
```

## Screen structure

- **1  SELECT: Saved candidate + company + source mode** - Company readiness settings must distinguish Real source from Synthetic lab.
- **2  ACTION: Run Talent Check** - Require saved profile and selected valid company. A JD is not needed.
- **3  SUMMARY: Readiness % / Unassessed + X/12** - State that ratings are self-reported. Do not show a final number when categories are unknown.
- **4  COMPARISON: 12 rows + candidate/expectation bars** - Full category labels, values, gap and row evidence. Filters: All 12, Gaps, Unknown.
- **5  SOURCE: Source card + decision receipt** - Show synthetic notice or genuine provenance; explain arithmetic without calling it a hiring probability.

## API endpoints

- `GET /api/talent-check/companies` - ?mode=real|synthetic&refresh=false; returns IDs/names and provenance.
- `GET /api/talent-check/benchmark-status` - Source availability/error; separate from process liveness.
- `POST /api/talent-check/evaluate` - profile_id + company_id + benchmark_mode; returns ReadinessResult.

See request-example.json and the FULL response-example.json here. Canonical required/optional fields and types are in shared/contracts/models.py and shared/contracts/openapi.json.

## Logic

For each category, divide the candidate level by the required level and cap the result at 1. Average all twelve category attainments. Stronger skills cannot compensate beyond the cap for weaker categories.

```text
attainment = min(candidate / required, 1)
shortfall = max(required - candidate, 0)
gap = candidate < required
contribution = 100 * attainment / 12
score = round(100 * sum(attainments) / 12, 1)
```

- **Simple synthetic arithmetic** - If all twelve required levels are 8 and all candidate levels are 4, every attainment is 0.5; readiness = 50.0%.
- **Raise one of those ratings to 8** - One category reaches 1.0; the remaining eleven stay 0.5. New score = 54.2%. The change is explainable.
- **Unknown candidate category** - Return candidate_level=null, gap=null and attainment/contribution=null for that row. Final readiness_score=null, status=incomplete.
- **Mira synthetic SQL row** - Candidate 4, invented requirement 9: attainment 4/9; shortfall 5; contribution 3.7037 points out of 100.
- **Evidence added** - The evidence-linked count may change. The score must not change unless an explicit candidate rating or benchmark changes.

All examples here are synthetic. No official company bar has been verified. The formula is a self-reported readiness estimate, not a hiring probability, guarantee or employer-approved cutoff.

## Tests

Read TESTING.md for three normal and three failure cases. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest talent_check/tests -q
npm run test -- talent_check/frontend
```

## Demonstration

1. Select the saved synthetic Mira profile with all twelve explicitly invented ratings set to 4.
2. Open company readiness settings; choose Synthetic lab and Synthetic Data Co (lab-data). Keep the synthetic label visible.
3. Click Run Talent Check: expected fixed-fixture score 74.9%, twelve category rows, 12/12 assessed.
4. Open SQL: self-rating 4 against synthetic requirement 9 gives 3.7037 contribution points and a shortfall of 5.
5. Explain Unknown behavior and source provenance. Hand the same formula/benchmark snapshot to GPS; official benchmark validation remains pending.

## Explain to judges

- 0:00-0:35: My module compares a candidate with a company's general bar across twelve categories, not one job posting.
- 0:35-1:25: Select synthetic company and show 74.9% plus twelve rows. Clearly label the invented standards.
- 1:25-2:15: Open SQL and calculate 4/9, shortfall 5 and 3.7037 contribution points.
- 2:15-3:10: Explain unknown ratings, source provenance and why evidence never raises proficiency automatically.
- 3:10-4:00: Show how changing the candidate changes the score. Transition to the separate specific-JD comparison.

## Likely questions

**Why no score with one unknown?** The chosen formula averages all twelve assessed categories. Treating missing ability as zero would make an unsupported claim.

**Are those official Google/Microsoft expectations?** No. The demo is synthetic. Genuine authorized organizer data is still needed for real company acceptance.

**Why not use an LLM for the percentage?** Plain deterministic arithmetic is more transparent and repeatable. The brief describes this module as plain code.

## Return to Scrum Master

Publish to your own GitHub repository and fill DELIVERY.md with actual executed results. Follow ../SUBMIT_YOUR_REPOSITORY.md. Never commit private CVs or secrets. Live Groq, Supabase and organizer data remain pending unless actually verified.
