# Test and confirm YOUR module works

Run the exact commands in README.md. Use synthetic data; retain actual output and failures in DELIVERY.md.

## Three normal cases

1. **Mira JD/profile** - expected: 75.0 JD match, four matched decisions and three missing names in two groups.
2. **Hypothetical Docker then reset** - expected: 87.5 then 75; stored profile JSON identical.
3. **Docker plus SQL level 9** - expected: 87.5 JD match and 79.5 synthetic readiness; broad rating and named claims remain separate.

## Three failure/edge cases

1. **Empty JD** - expected: Unscorable/null rather than 0 or 100.
2. **Stale revision/hash or skill not in JD** - expected: 409/422; ask for current inputs.
3. **Conflicting claims / Java vs JavaScript** - expected: Unresolved or missing, not automatic equivalence.

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
