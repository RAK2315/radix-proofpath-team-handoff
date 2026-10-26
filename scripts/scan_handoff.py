"""Check prospective/staged publication files without printing sensitive values."""

import argparse
import json
import os
import re
import subprocess
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ".git",
    ".venv",
    ".venv-deploy",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "test-results",
    "playwright-report",
    "dist",
    "dist-module",
    "local",
}
PATTERNS = [
    rb"gsk_[A-Za-z0-9_-]{20,}",
    rb"(?:ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}",
    rb"sk-proj-[A-Za-z0-9_-]{20,}",
    rb"sb_secret_[A-Za-z0-9_-]{20,}",
    rb"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{15,}",
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]


def scan(staged=False):
    if staged:
        names = subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=ROOT).decode().split("\0")
        paths = [ROOT / name for name in names if name]
    else:
        paths = []
        for directory, folders, files in os.walk(ROOT):
            folders[:] = [
                name
                for name in folders
                if name not in SKIP
                and not (Path(directory) / name)
                .relative_to(ROOT)
                .as_posix()
                .startswith(("data/private", "data/original", "data/company_benchmarks", "deploy/hf-space"))
            ]
            paths.extend(Path(directory) / name for name in files)
    errors = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(
            ("data/private/", "data/original/", "data/company_benchmarks/")
        ) or path.name.endswith((".sqlite3", ".log")):
            errors.append((relative, "private persistence/log path"))
            continue
        if path.name.startswith(".env") and path.name not in {".env.example", ".env.frontend.example"}:
            errors.append((relative, "private environment file"))
            continue
        content = (
            subprocess.check_output(["git", "show", f":{relative}"], cwd=ROOT)
            if staged
            else path.read_bytes()
        )
        if path.suffix == ".pdf":
            from pypdf import PdfReader

            text = "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(content)).pages)
            if "SYNTHETIC" not in text and path.name != "GUIDE.pdf":
                errors.append((relative, "unlabelled PDF"))
            content += text.encode()
        elif path.suffix == ".docx":
            with zipfile.ZipFile(BytesIO(content)) as archive:
                xml = archive.read("word/document.xml")
                if b"SYNTHETIC" not in xml:
                    errors.append((relative, "unlabelled DOCX"))
                content += xml
        private_markers = [b"rehaan" + b"_cv", b"Rehaan" + b" Ahmad" + b" Khan"]
        if any(marker.lower() in content.lower() for marker in private_markers):
            errors.append((relative, "personal CV marker"))
        if any(re.search(pattern, content) for pattern in PATTERNS):
            errors.append((relative, "possible credential"))
    report = {
        "scanned_files": len(paths),
        "errors": errors,
        "scope": "Focused credential/private-path/document-label scan, not an exhaustive security audit",
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    scan(parser.parse_args().staged)
