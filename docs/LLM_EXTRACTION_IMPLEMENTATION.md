# Groq extraction implementation

Updated 26 October 2026. **IMPLEMENTED and MOCK-TESTED; live Groq execution is EXTERNALLY BLOCKED by the absent API key. Nothing deployed.**

JD Analytics and Resume Parsing now use a shared strict structured-output transport while keeping their own domain instructions and postprocessing in their feature folders. Their existing upload/paste/review/import contracts remain in use. Python HTTP calls are sufficient for this integration; no LangChain agent, tools or model-weight download is needed.

## Pipeline

1. The existing PDF/DOCX reader validates size/signature/format and obtains page-aware source text. Pasted JD text is retained as an original private source too.
2. With no per-input hosted consent, the existing deterministic feature parser runs. A configured key never overrides this choice.
3. With consent and `auto`/`hosted` mode, a bounded list of rule candidates is supplied as context, explicitly **not ground truth**. The feature's prompt asks Groq for semantic requirements or resume claims, including unfamiliar names and defensible inferred skills.
4. The generic provider schema has no profile ratings, saved-record identifiers, lifecycle states, arbitrary source sections or verified-status fields. It asks for skills, source evidence, typed identity facts, section quotes and AND/OR groups. Groq receives `json_schema` with `strict: true`. The default evaluated candidate model is `openai/gpt-oss-20b`; it has not actually been executed here. The server endpoint/model remain configurable.
5. Pydantic validates the proposal. Deterministic code checks identity values against quotes, aligns whitespace-only quote differences to original text, creates character spans/page locations, validates skill references, reconciles duplicate normalized identities and retains conflicting-source warnings. Explicit skill names/known aliases must occur in the quote. Inferred skills remain marked inferred and require human judgment.
6. Instruction-like source lines cannot support accepted model claims. Obvious injection lines are excluded by rules too. This is defense in depth, not a claim of universal prompt-injection immunity or semantic factual verification.
7. The server assigns identifiers, original source provenance and review state. Every model skill starts `needs_review`; all verification states remain unverified. No competency levels are inferred. Reviewers can inspect each claim, confirm individually or explicitly confirm all after source review, correct categories/groups, remove claims and add manual claims. Saved reviews preserve the original processing method/model metadata.
8. Downstream Profile Builder, Talent Check, Skill Matching and Career GPS use the existing reviewed contracts/scoring engines. What-if changes remain separate from saved profiles.

Mixed logic such as **Python AND (PyTorch OR TensorFlow)** is represented as two required groups: a singleton AND group for Python and an OR group for the alternatives. Unresolved relationships remain flagged for review; model output is not assumed correct merely because its schema validates.

## Bounds and failure handling

- Two concurrent hosted calls per API process; Docker runs one worker. Cloud API requests first reserve two-attempt estimated budgets through the restricted owner/global quota RPC. Failures to check quota do not result in a model call. Local private CLI evaluation does not use this authenticated cloud RPC.
- Default request budget 45 seconds and maximum completion 8,192 tokens; validated configurable bounds are 1–60 seconds and 256–16,384 output tokens. Provider HTTP timeout governs network operations; it is not a hard process-kill watchdog for malicious document parsing.
- Serialized prompt/schema input is bounded at 110,000 bytes; rule suggestions are capped at 30, with 600-character quotes. Larger valid uploads can still use rules. Input/output limits are resource controls, not quality guarantees.
- At most one regeneration after invalid JSON/schema/references/evidence. No unbounded network retry; 429/auth/provider errors return safe codes and fall back by default. The UI discloses the fallback, and no raw provider error/payload is reflected.
- `RADIX_LLM_FALLBACK=error` exposes a reviewable failure instead; `rules` returns deterministic output with `llm_status=unavailable`. `RADIX_LLM_MODE=rules` forbids provider use; `auto` and `hosted` both require explicit consent. No local Ollama/model-weight inference was added for this Groq deployment.
- A source quote proves source presence, not actual ability or that an inferred claim is semantically justified. Human review remains necessary. Scanned PDFs still require OCR that is not implemented.

## Supported configuration and status

- Primary target: Groq Chat Completions with a schema-capable model. The default endpoint is `https://api.groq.com/openai/v1/chat/completions`.
- Other HTTPS endpoints implementing the same strict chat-completions schema protocol can be configured, but have not been live-tested. This is not a claim of universal provider/model compatibility.
- `extraction_mode`: existing `local_limited`, `hosted_llm`, `manual`.
- `llm_status`: `not_requested`, `processed`, `unavailable`, `rules_only`.
- Provider metadata records actual configured model, prompt/parser version, successful-attempt usage and elapsed time. Usage on a failed repair attempt may not be present in a successful response's usage block; provider billing is authoritative.
- `GET /api/status` reports configuration presence/model/mode/provider. It does not make a paid probe or prove dependency connectivity.

See [setup](<docs/DEPLOYMENT_SETUP.md>) for exact key locations, accounts and live-test commands; [evaluation](<docs/LLM_EXTRACTION_EVALUATION.md>) for what has actually run. Original organizer data and live official benchmarking remain pending.

Primary implementation references: [Groq structured outputs](https://console.groq.com/docs/structured-outputs), [current models](https://console.groq.com/docs/models), [provider data controls](https://console.groq.com/docs/your-data).
