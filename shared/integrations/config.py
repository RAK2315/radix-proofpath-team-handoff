import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def setting(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def data_dir() -> Path:
    path = Path(setting("RADIX_DATA_DIR", str(ROOT / "data/private")))
    path.mkdir(parents=True, exist_ok=True)
    return path


def public_key() -> str:
    return setting("SUPABASE_PUBLISHABLE_KEY") or setting("SUPABASE_ANON_KEY")


def allowed_origins() -> list[str]:
    raw = setting("RADIX_ALLOWED_ORIGINS") or setting("RADIX_ALLOWED_ORIGIN", "http://127.0.0.1:5173")
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


def validate_config() -> None:
    import base64
    import json
    from urllib.parse import urlparse

    for name in ("RADIX_AUTH_MODE", "RADIX_STORAGE_MODE"):
        if setting(name, "local") not in {"local", "supabase"}:
            raise RuntimeError(f"Unsupported {name}")
    if setting("RADIX_DOCUMENT_STORAGE_MODE", "local") not in {"local", "supabase"}:
        raise RuntimeError("Unsupported RADIX_DOCUMENT_STORAGE_MODE")
    if (
        setting("RADIX_DOCUMENT_STORAGE_MODE", "local") == "supabase"
        and setting("RADIX_STORAGE_MODE", "local") != "supabase"
    ):
        raise RuntimeError("Remote document storage requires remote JSON persistence")
    if setting("RADIX_LLM_MODE", "auto") not in {"auto", "hosted", "rules"}:
        raise RuntimeError("RADIX_LLM_MODE must be auto, hosted or rules")
    if setting("RADIX_LLM_FALLBACK", "rules") not in {"rules", "error"}:
        raise RuntimeError("RADIX_LLM_FALLBACK must be rules or error")
    if not 1 <= float(setting("RADIX_LLM_TIMEOUT_SECONDS", "45")) <= 60:
        raise RuntimeError("LLM timeout must be 1–60 seconds")
    if not 256 <= int(setting("RADIX_LLM_MAX_OUTPUT_TOKENS", "8192")) <= 16384:
        raise RuntimeError("LLM completion limit must be 256–16384")
    if (
        setting("RADIX_STORAGE_MODE", "local") == "supabase"
        and setting("RADIX_AUTH_MODE", "local") != "supabase"
    ):
        raise RuntimeError("Supabase storage requires Supabase authentication")
    if setting("RADIX_AUTH_MODE", "local") == "supabase":
        if not setting("SUPABASE_URL").startswith("https://") or not public_key():
            raise RuntimeError("Supabase HTTPS URL and publishable key are required")
        key = public_key()
        try:
            payload = key.split(".")[1]
            role = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))).get("role")
        except (ValueError, IndexError, UnicodeError):
            role = None
        if key.startswith("sb_secret_") or role == "service_role":
            raise RuntimeError("Normal user access requires a publishable key, never a secret key")
    if setting("RADIX_ENV", "development") == "production":
        if setting("RADIX_AUTH_MODE") != "supabase" or setting("RADIX_STORAGE_MODE") != "supabase":
            raise RuntimeError(
                "Production requires Supabase auth and persistence; local defaults are forbidden"
            )
        if setting("RADIX_DOCUMENT_STORAGE_MODE") != "supabase":
            raise RuntimeError("Production requires private Supabase object storage")
        if not allowed_origins() or any(
            urlparse(o).scheme != "https"
            or not urlparse(o).netloc
            or urlparse(o).path
            or urlparse(o).query
            or urlparse(o).fragment
            or urlparse(o).username
            or "*" in o
            for o in allowed_origins()
        ):
            raise RuntimeError("Production origins must be exact HTTPS origins")
