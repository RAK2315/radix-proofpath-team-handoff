import ast
from pathlib import Path


def test_feature_ownership_and_shared_import_boundaries():
    features = {"jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"}
    for feature in features:
        for item in [
            "backend/router.py",
            "frontend",
            "tests",
            "START_HERE.md",
            "START_HERE.pdf",
            "samples",
            "run.ps1",
        ]:
            assert (Path(feature) / item).exists(), (feature, item)
        for historical in ["PLAN.md", "CONTRACT.md", "USAGE.md"]:
            assert (Path("docs/internal/archive") / feature / historical).exists()
    for file in Path("shared").rglob("*.py"):
        for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in features, file
