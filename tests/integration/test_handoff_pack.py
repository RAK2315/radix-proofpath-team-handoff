import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "module", ["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"]
)
def test_selected_module_real_api_independently(module):
    result = subprocess.run(
        [sys.executable, "scripts/check_module.py", module],
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "RADIX_MODULE": module},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"PASS {module}" in result.stdout


def test_all_guides_assets_labels_and_computed_matrix():
    from pypdf import PdfReader

    features = ["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"]
    for feature in features:
        assert 8 <= len(PdfReader(Path(feature) / "START_HERE.pdf").pages) <= 10
        for name in [
            "START_HERE.md",
            "run.ps1",
            "samples/input.json",
            "samples/output.json",
        ]:
            assert (Path(feature) / name).is_file(), (feature, name)
    folder = Path("data/synthetic/reconstructed")
    assert len(list(folder.glob("*.pdf"))) == 10
    assert len(list(folder.glob("*.docx"))) == 10
    report = json.loads((folder / "matrix-results.json").read_text())
    assert all(report["direction_checks"].values())
    assert len(report["observations"]) == 20
    assert len(report["matching"]) == 4
    assert all(len(row) == 6 for row in report["matching"].values())
