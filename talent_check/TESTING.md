# Test and confirm YOUR module works

Run the exact commands in README.md. Use synthetic data; retain actual output and failures in DELIVERY.md.

## Three normal cases

1. **Synthetic Mira + lab-data** - expected: 74.9 readiness, twelve rows, SQL 4 versus 9, contribution 3.7037.
2. **All ratings 4, all requirements 8 (pure test)** - expected: 50.0 readiness; one rating to 8 gives 54.2.
3. **Different synthetic profiles** - expected: Different explainable category rows and deterministic repeats.

## Three failure/edge cases

1. **One unknown self-rating** - expected: Incomplete/null final score, known rows still visible.
2. **Missing or duplicate company category** - expected: Reject source; do not fill with invented values.
3. **No authorized real Supabase data** - expected: Unavailable real source; no silent lab substitution.

## How to check real correctness

Before extraction, manually list expected skills and supporting quotes from an unfamiliar authorized JD/CV.
A false positive is a proposed skill not supported by that source; a false negative is a required/source-supported
skill that was missed. Count both and inspect AND/OR/importance and background sections independently.
Do not derive the expected answer from the same model output you are grading. Use fictional or consented
sources; no private originals or raw personal provider payloads belong in Git.

For Modules 1/2 record rules and real-model runs separately. A configured key, valid JSON or HTTP 200 does not
prove semantic accuracy. Show actual model/version, source-grounding outcomes, misses and limitations.

The reconstructed matrix intentionally reports rules-parser misses (such as the bare word Testing) and
layout differences rather than hiding them. A teammate should correct the reviewed output or improve
extraction and demonstrate the effect without hardcoding candidate rankings or changing expected labels.

## Evidence to return

- Input screenshot and the output/source reasoning screenshot, synthetic only.
- A failure screenshot followed by recovery, with the draft/input retained where applicable.
- Exact test commands and console result, plus the commit SHA tested.
- Bug entries: reproduction steps, expected/actual, severity, affected input and fix/retest result.
- Three normal + three edge cases filled with YOUR observed results, not just the expected list above.
