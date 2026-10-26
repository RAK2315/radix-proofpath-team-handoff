# Groq evaluation status

26 October 2026. **No real Groq key has been supplied and no actual model call was made.** The page 7 LLM extraction requirement is implemented in code but is not yet operationally demonstrated with a live model.

| Status | Evidence |
| --- | --- |
| IMPLEMENTED | Strict proposal schema, Groq HTTP transport, module prompts, source alignment/spans, review/status, rules fallback, bounded requests and synthetic evaluation CLI. |
| MOCK-TESTED | Controlled HTTP responses verify strict request format, unknown Rust extraction, AND/OR relationships, whitespace/page alignment, absent consent, injection, unsupported evidence, state/proficiency injection, bounded repair and 401/403/429/503 failure handling. These tests do not measure model quality. |
| LIVE-VERIFIED | None. No successful provider execution, model quality, live latency or billing has been measured. |
| EXTERNALLY BLOCKED | Live Groq API key/model entitlement; official JD/resume pack; organizer benchmarks; cloud Supabase/HF/Vercel acceptance. |

## Executed rules baseline

Command: `python -m scripts.evaluate_llm` using the project virtualenv. No network/model calls.

- Fourteen invented sources: seven JD and seven resume documents, each in PDF/DOCX, 28 format observations. The first twelve sources were used for prior development; two new instruction-injection probes supplement them. These are not 28 independent documents or a held-out accuracy study.
- Manually specified expected skills were not generated from model predictions.
- Final counts: **98 true positives, 0 false positives, 8 false negatives**; precision **100%**, recall **92.45%** on this development set's named-skill labels. Quote validation and the twelve-unknown competency invariant pass on every observation.
- Both injection probes exclude the injected Kubernetes claim in both formats. The first run exposed four false positives, which prompted the instruction-line exclusion and regression tests. The final figures therefore include development fixes.
- Eight remaining format-level misses are unfamiliar Rust/Apache Arrow and implicit Data Cleaning from the existing development set. No official benchmark or broad semantic quality is established by this baseline.

Raw result: [groq-rules-baseline.json](<docs/evaluation/groq-rules-baseline.json>). This file explicitly reports zero successful live calls.

## Required live evaluation

Follow the setup guide and run `python -m scripts.evaluate_llm --live --authorize-synthetic --output docs/evaluation/groq-live.json` after securely adding a real key. The CLI never reads the personal CV; hosted tests require both explicit flags and a separate output path. Failed model calls/fallbacks count as unsuccessful model extraction, not baseline-assisted successes.

Inspect raw TP/FP/FN, supported unfamiliar skills, importance/group accuracy, false claims, injection exclusions, exact source alignment, schema errors/refusals/truncation, fallback reliability, latency and actual usage. Suggested targets remain >=90% precision, >=85% recall, 100% provenance for accepted source claims, zero automatic ratings and zero critical designated AND/OR errors. These are project engineering targets, not organizer thresholds. Correctness of all mandatory/optional relationships also needs manual review across representative unfamiliar inputs.

Live results must identify model/provider/prompt versions and actual successes/failures. A single successful smoke call is not sufficient to claim the full extraction requirement verified. Record novel failure cases without modifying labels to fit predictions. Test the original six JDs/four resumes separately when provided.
