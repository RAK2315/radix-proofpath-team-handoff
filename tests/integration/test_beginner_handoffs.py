"""Protect the runnable handoff examples and the requested minimal student-facing structure."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from shared.contracts.models import Extraction, MatchingResult, Profile, ReadinessResult

FEATURES = ["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"]


@pytest.mark.parametrize("feature", FEATURES)
def test_beginner_teaching_example_runs_actual_api(feature):
    result = subprocess.run(
        [sys.executable, "scripts/module_example.py", feature], capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"PASS {feature}" in result.stdout


@pytest.mark.parametrize("feature", FEATURES)
def test_minimal_folder_and_complete_same_guide_examples(feature):
    root = Path(feature)
    expected = {"START_HERE.pdf", "START_HERE.md", "backend", "frontend", "tests", "samples", "run.ps1"}
    actual = {path.name for path in root.iterdir() if path.name != "__pycache__"}
    assert actual == expected
    markdown = (root / "START_HERE.md").read_text(encoding="utf-8")
    model = {
        "jd_analytics": Extraction,
        "resume_parsing": Extraction,
        "profile_builder": Profile,
        "talent_check": ReadinessResult,
        "skill_matching": MatchingResult,
    }[feature]
    snapshot = json.loads((root / "samples/output.json").read_text())
    model.model_validate(snapshot)
    # The full output must actually be embedded in the one document, not just linked elsewhere.
    import re

    embedded = [json.loads(text) for text in re.findall(r"```json\n(.*?)\n```", markdown, re.S)]
    assert snapshot in embedded
    for sample in (root / "samples").iterdir():
        assert sample.name in markdown
    for phrase in ["Already implemented", "Currently missing", "How do I know", "Copy this prompt"]:
        assert phrase in markdown
    assert "run.ps1 setup" in markdown and "run.ps1 test" in markdown
