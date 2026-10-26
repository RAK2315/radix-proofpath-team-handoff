"""Reserve bounded hosted-extraction budgets through a restricted database RPC."""

import json

import httpx

from shared.integrations.auth import Identity
from shared.integrations.config import setting
from shared.integrations.errors import AppError
from shared.integrations.store import remote_headers


def reserve_hosted(user: Identity, sections: list[dict], consent: bool) -> None:
    if not consent or setting("RADIX_LLM_MODE", "auto") == "rules":
        return
    if not (setting("RADIX_LLM_API_KEY") or setting("GROQ_API_KEY")):
        return
    # Reserve for two attempts, prompt/schema overhead and the full output budget.
    estimate = min(
        300000,
        2
        * (
            len(json.dumps(sections).encode("utf-8"))
            + 50000
            + int(setting("RADIX_LLM_MAX_OUTPUT_TOKENS", "8192"))
        ),
    )
    if setting("RADIX_AUTH_MODE", "local") != "supabase":
        return  # Private local development; concurrency and input/output bounds still apply.
    try:
        response = httpx.post(
            f"{setting('SUPABASE_URL')}/rest/v1/rpc/proofpath_reserve_extraction",
            headers=remote_headers(user),
            json={"p_tokens": estimate},
            timeout=10,
        )
        if response.status_code == 429 or "QUOTA_EXCEEDED" in response.text:
            raise AppError(
                "EXTRACTION_QUOTA", "Daily hosted-extraction budget reached; use rules or try tomorrow", 429
            )
        response.raise_for_status()
    except httpx.HTTPError:
        raise AppError(
            "QUOTA_UNAVAILABLE", "Cannot verify hosted-extraction budget; no model request sent", 503
        ) from None
