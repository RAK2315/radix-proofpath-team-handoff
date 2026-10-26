---
title: RADIX ProofPath API
sdk: docker
app_port: 7860
---

FastAPI composition of all five RADIX ProofPath modules. Requires configured Supabase Auth,
JSON records, private file bucket and quota migration. Groq extraction is opt-in per input.
Synthetic benchmark mode is explicitly labelled; real benchmarks require organizer authorization.
No model weights, user documents or credentials are included in this repository bundle.

Liveness: `/api/health`. Configuration presence: `/api/status` (not a dependency health test).
