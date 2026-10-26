# Skill Matching + Career GPS - teammate guide (editable)

Assume you own this module. Run/test it and push your working copy to YOUR OWN GitHub. Return URL, SHA, evidence and limitations; no central PR is required.

## Your responsibility

Compare the saved candidate's reviewed named claims with one reviewed JD. Explain matched, missing and unresolved requirements, then let the user explore reversible hypothetical improvements.

## Required input

Saved profile ID + saved JD ID. GPS also uses their current revisions, optional company/benchmark snapshot, named-skill overrides and category overrides.

## Guaranteed output

MatchingResult with score/null, matched/missing/ambiguous decisions and contributions. ScenarioResult adds baseline/projected outcomes and explicitly hypothetical changes.

## Organizer requirement

Participant Brief p.8 requires one-specific-JD score plus matched and missing skills. It permits exact/fuzzy matching; an LLM matcher is not required. Importance, ProofPath reasoning and Career GPS are our additions.

## Build in order

1. **Load the exact pair** - Use saved profile_id and jd_id; display the candidate and job clearly. Company benchmarks and numeric ratings are not needed for named-skill matching.
2. **Normalize conservatively** - Match exact names and reviewed aliases. Java is not JavaScript. A shared category is not enough to satisfy a named technology.
3. **Score requirement groups** - Use mandatory weight 2, preferred/unspecified weight 1. AND uses a matched fraction; OR needs any member. Deduplicate equivalent groups.
4. **Explain every decision** - Preserve JD quote, candidate quote or honest absence, importance, reason and contribution points. Treat fuzzy suggestions and unresolved claims as review tasks, not automatic matches.
5. **Record current revisions** - Return a result/receipt linked to input revisions and rules. Empty JD is unscorable; unreviewed/ambiguous coverage remains provisional.
6. **Preview on a copy** - GPS deep-copies the profile, applies only allowed explicit overrides and calls the same match/readiness engines. Hold revisions and benchmark hash fixed.
7. **Reset and prove no writes** - Reset removes hypothetical changes. Compare saved profile JSON before/after. Do not expose scenario values as actual evidence or save them behind the scenes.

## Run and verify

Use README.md for fresh setup. From the full repo root:

```powershell
.\skill_matching\run.ps1 api
# Separate terminal:
.\skill_matching\run.ps1 web
# Verify:
.\skill_matching\run.ps1 check
```

## Screen structure

- **1  PAIR + ACTION: Candidate + job | Analyze this match** - State exactly which saved pair is being assessed; avoid a generic unnamed percentage.
- **2  REPORT: Match % | matched | evidence gaps** - Missing list matters more than a big score. Show provisional/unscorable states.
- **3  REASONING: JD source -> candidate -> points -> action** - Click a skill to see original quotes or honest no-evidence state. Keep source download available.
- **4  CAREER GPS: Named-skill toggles + category levels** - Separate JD coverage from company readiness; mark all changes hypothetical.
- **5  RECOMMEND / RESET: Rank next actions | Reset scenario** - Show before/after and honest gaps. Reset restores baseline; actual profile is untouched.

## API endpoints

- `POST /api/matching/evaluate` - profile_id + jd_id; server loads saved records.
- `POST /api/matching/scenarios/preview` - Pair, current revisions, overrides and optional benchmark snapshot.
- `GET /api/receipts/ID` - Owned stored decision snapshot for the baseline assessment.

See request-example.json and the FULL response-example.json here. Canonical required/optional fields and types are in shared/contracts/models.py and shared/contracts/openapi.json.

## Logic

A score is weighted coverage of reviewed extracted requirements. It is not measured proficiency. Confidence is not a score multiplier, and unrelated extra skills do not reduce the match.

```text
weight = 2 if mandatory, otherwise 1
AND coverage = hits / member_count
OR coverage = 1 if any hit, otherwise 0
score = round(100 * sum(weight * coverage)
              / sum(weight), 1)
```

- **Synthetic Mira baseline** - Three required groups covered: Python+SQL, Pandas, Linux. Two preferred groups missing: Docker and AWS/GCP. Covered weight 6 / total 8 = 75.0%.
- **Python/SQL contribution** - Their mandatory group is 2/8 of total = 25 points. In its AND group each matched member contributes 12.5 points.
- **Add hypothetical Docker** - The preferred group adds 1/8 = 12.5 points, giving 87.5%. Category self-ratings do not change.
- **Add hypothetical AWS too** - AWS satisfies AWS OR GCP; score 100%. Do not additionally demand GCP or count both alternatives twice.
- **Move SQL category level to 9** - Readiness may change (74.9 -> 79.5 in the synthetic story); named-SQL JD coverage does not change just because its broad rating changed.

Do not save a ScenarioResult as a Profile. Recommendations are possibilities, not guarantees, study-time estimates or verified learning. Reset must restore baseline using unchanged actual saved inputs.

## Tests

Read TESTING.md for three normal and three failure cases. Run:

```powershell
.\.venv\Scripts\python.exe -m pytest skill_matching/tests -q
npm run test -- skill_matching/frontend
```

## Demonstration

1. Select the reviewed synthetic data JD and saved Mira profile. Click Analyze this match: baseline 75.0%; four matched decisions and three missing names across two groups.
2. Open Python in Matched: show JD quote, candidate quote, 12.50 points and next action. Open Docker gap: no candidate evidence, 0.00 points.
3. Choose Explore in Career GPS. This navigation must not automatically apply the missing skill. Toggle Docker: projected match 87.5%, readiness stays 74.9%.
4. Set SQL hypothetical level to 9: readiness 79.5%; named match remains 87.5%. Add AWS: match 100% because AWS OR GCP is satisfied.
5. Reset scenario: 75.0% / 74.9%. Return to Profile Builder: SQL still 4; no actual Docker/AWS claim was added.

## Explain to judges

- 0:00-0:35: My module compares this candidate with this particular JD. Company readiness is a separate result.
- 0:35-1:25: Show 75% and its missing list. Explain weight 6 of 8 rather than a mysterious AI-generated number.
- 1:25-2:15: Open Python and Docker reasoning chains. Distinguish supported evidence from an actual capability gap.
- 2:15-3:20: Simulate Docker and SQL. Show two separate score changes and explain why they differ.
- 3:20-4:00: Reset and verify saved inputs unchanged. Close with an honest limitation and the complete five-module journey.

## Likely questions

**Why not match only by category?** Knowing one AI technology does not prove another named tool. Exact names/reviewed aliases are safer; fuzzy similarity only suggests review.

**Can 100% mean guaranteed selection?** No. It means coverage of the reviewed extracted requirement groups, not a hiring probability or verified competence.

**Does the simulation improve the real profile?** No. It copies inputs and recalculates. Real changes require explicit editing/saving in Profile Builder.

## Return to Scrum Master

Publish to your own GitHub repository and fill DELIVERY.md with actual executed results. Follow ../SUBMIT_YOUR_REPOSITORY.md. Never commit private CVs or secrets. Live Groq, Supabase and organizer data remain pending unless actually verified.
