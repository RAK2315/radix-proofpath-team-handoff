"""Export the actual FastAPI contract for TypeScript generation and drift checks."""

import json
from pathlib import Path

from apps.api.main import app
from shared.contracts.taxonomy import SKILL_FAMILIES

if __name__ == "__main__":
    target = Path("shared/contracts/openapi.json")
    target.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported {target}")
    Path("shared/contracts/skill-families.json").write_text(
        json.dumps(list(SKILL_FAMILIES), indent=2) + "\n", encoding="utf-8"
    )
