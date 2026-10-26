"""Prepare an allowlisted HF source folder, never upload or authenticate."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ("jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching")


def prepare() -> dict:
    files: dict[str, Path] = {}
    for directory in (
        "apps/api",
        "shared/integrations",
        "shared/contracts",
        *(f"{f}/backend" for f in FEATURES),
    ):
        for source in (ROOT / directory).rglob("*.py"):
            files[source.relative_to(ROOT).as_posix()] = source
    for path in (
        "requirements.runtime.lock.txt",
        "pyproject.toml",
        "data/synthetic/benchmarks.json",
        "scripts/cleanup_expired_documents.py",
    ):
        files[path] = ROOT / path
    for name in ("Dockerfile", "README.md"):
        files[name] = ROOT / "deploy/hf" / name
    files[".dockerignore"] = ROOT / ".dockerignore"
    destination = ROOT / "deploy/hf-space-ready"
    expected = set(files) | {"DEPLOYMENT_MANIFEST.json"}
    # Refuse a dirty staging folder rather than accidentally retaining or deleting sensitive files.
    if destination.exists():
        unexpected = {
            p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()
        } - expected
        if unexpected:
            raise RuntimeError("Staging contains unexpected files; inspect it before continuing")
    manifest = {}
    for relative, source in files.items():
        content = source.read_bytes()
        if re.search(rb"(?:gsk_|sk-proj-|sb_secret_)[A-Za-z0-9_-]{20,}|-----BEGIN .*PRIVATE KEY", content):
            raise RuntimeError("Possible credential in deployment source: " + relative)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        manifest[relative] = hashlib.sha256(content).hexdigest()
    (destination / "DEPLOYMENT_MANIFEST.json").write_text(json.dumps({"files": manifest}, indent=2) + "\n")
    for relative, digest in manifest.items():
        if hashlib.sha256((destination / relative).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Deployment manifest mismatch")
    return {"directory": str(destination), "files": len(manifest), "uploaded": False}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
