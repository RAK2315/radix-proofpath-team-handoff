"""Run a small teaching example through one real local API, without keys or network calls."""

import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULES = ["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"]


def example(module: str, write: bool = False):
    with TemporaryDirectory(prefix="proofpath-teaching-") as directory:
        os.environ.update(
            RADIX_MODULE=module,
            RADIX_ENV="development",
            RADIX_AUTH_MODE="local",
            RADIX_STORAGE_MODE="local",
            RADIX_DOCUMENT_STORAGE_MODE="local",
            RADIX_DATA_DIR=directory,
            RADIX_LLM_MODE="rules",
            RADIX_LLM_API_KEY="",
            GROQ_API_KEY="",
            RADIX_ALLOWED_ORIGINS="",
        )
        from fastapi.testclient import TestClient

        from apps.api.standalone import app
        from shared.contracts.models import Extraction, Profile, Rating, Requirement, Skill
        from shared.integrations import store
        from shared.integrations.auth import Identity
        from shared.integrations.documents import persist_document

        files = {}
        samples = ROOT / module / "samples"
        user_id = "local-single-user"
        with TestClient(app, headers={"X-ProofPath-Client": user_id}) as client:

            def call(path, payload=None, upload=None):
                result = client.post("/api" + path, json=payload, files=upload)
                result.raise_for_status()
                return result.json()

            if module in MODULES[:2]:
                kind = "jd" if module == "jd_analytics" else "resumes"
                filename = "practice-jd-SYNTHETIC.docx" if kind == "jd" else "practice-cv-SYNTHETIC.pdf"
                files["input.json"] = {
                    "method": "POST",
                    "path": f"/api/{kind}/extract",
                    "encoding": "multipart/form-data",
                    "file": filename,
                    "hosted_consent": False,
                }
                output = call(
                    f"/{kind}/extract",
                    upload={"file": (filename, (samples / filename).read_bytes())},
                )
                assert [s["skill_name"] for s in output["skills"]] == ["Python"]
                assert output["llm_status"] == "rules_only"
                assert output["review_status"] == "needs_review"
                files["output.json"] = output
                files["expected.json"] = {
                    "provenance": "SYNTHETIC teaching example; not organizer material",
                    "skills": ["Python"],
                    "category": "COD",
                    "review_status": "needs_review",
                    "llm_status": "rules_only",
                    "competency_inferred": False,
                    "note": "IDs vary. Check source words, sections and meaning, not just HTTP status.",
                }
                if kind == "jd":
                    assert len(output["requirement_groups"]) == 1
                    assert output["requirement_groups"][0]["requirement_type"] == "mandatory"
                else:
                    assert output["name"] == "Asha Sample (synthetic)"
                    assert output["projects"] and output["education"]
                detail = "Python/COD extracted with real source evidence; needs review; no ability rating"
            elif module == "profile_builder":
                files["input.json"] = {
                    "name": "Asha Sample (synthetic)",
                    "email": "asha@example.test",
                    "education": ["Invented computing course"],
                    "preferred_roles": ["Junior Developer"],
                }
                output = call("/profiles", files["input.json"])
                files["output.json"] = output
                assert len(output["ratings"]) == 12 and all(r["level"] is None for r in output["ratings"])
                assert client.get("/api/profiles/" + output["id"]).json() == output
                context = call("/handoff/seed")
                files["reviewed-resume.json"] = context["resumes"][0]
                files["import-request.json"] = {
                    "resume_id": context["resumes"][0]["id"],
                    "profile": files["input.json"],
                    "replace_existing": False,
                }
                preview = call("/profiles/import-resume", files["import-request.json"])
                assert all(r["level"] is None for r in preview["ratings"])
                files["import-preview.json"] = preview
                detail = "saved and reloaded profile; twelve unknown ratings; reviewed resume import preview"
            elif module == "talent_check":
                profile = Profile(name="Asha Sample (synthetic)")
                profile.ratings = [Rating(category_code=r.category_code, level=4) for r in profile.ratings]
                store.save(Identity(user_id), "profile", profile.model_dump(mode="json"))
                files["candidate.json"] = profile.model_dump(mode="json")
                bundle = json.loads((ROOT / "data/synthetic/benchmarks.json").read_text())
                company = next(c for c in bundle["companies"] if c["id"] == "lab-data")
                files["company.json"] = {
                    "provenance": "SYNTHETIC teaching values, not official expectations",
                    **company,
                }
                files["input.json"] = {
                    "profile_id": profile.id,
                    "company_id": "lab-data",
                    "benchmark_mode": "synthetic",
                }
                output = call("/talent-check/evaluate", files["input.json"])
                files["output.json"] = output
                assert output["readiness_score"] == 74.9 and len(output["skillset_gap"]) == 12
                detail = "74.9% from twelve invented level-4 ratings; twelve comparison rows; no CV required"
            else:
                profile = Profile(name="Asha Sample (synthetic)")
                store.save(Identity(user_id), "profile", profile.model_dump(mode="json"))
                quote = "Required: Python"
                sections = [{"page": None, "text": "SYNTHETIC teaching JD\n" + quote}]
                document = persist_document(
                    user=Identity(user_id),
                    filename="practice-jd-SYNTHETIC.txt",
                    content=sections[0]["text"].encode(),
                    sections=sections,
                    origin="pasted_text",
                )
                skill = Skill(
                    skill_name="Python",
                    category_code="COD",
                    evidence=quote,
                    confidence="medium",
                    source_type="document",
                    evidence_type="jd_requirement",
                    source_file="practice-jd-SYNTHETIC.txt",
                    source_document_id=document["id"],
                )
                jd = Extraction(
                    source_type="jd",
                    source_file="practice-jd-SYNTHETIC.txt",
                    company="Synthetic Teaching Co",
                    role="Junior Developer (synthetic)",
                    skills=[skill],
                    requirement_groups=[
                        Requirement(skill_ids=[skill.skill_id], requirement_type="mandatory", evidence=quote)
                    ],
                    sections=sections,
                    document_id=document["id"],
                    input_method="pasted_text",
                    review_status="reviewed",
                    extraction_mode="manual",
                )
                store.save(Identity(user_id), "jd", jd.model_dump(mode="json"))
                files["profile.json"] = profile.model_dump(mode="json")
                files["jd.json"] = jd.model_dump(mode="json")
                files["input.json"] = {"profile_id": profile.id, "jd_id": jd.id}
                files["output.json"] = call("/matching/evaluate", files["input.json"])
                assert files["output.json"]["match_score"] == 0
                files["scenario-request.json"] = {
                    **files["input.json"],
                    "profile_revision": profile.revision,
                    "jd_revision": jd.revision,
                    "skill_overrides": ["Python"],
                    "category_overrides": {},
                }
                scenario = call("/matching/scenarios/preview", files["scenario-request.json"])
                assert scenario["projected_match"]["match_score"] == 100
                assert client.get("/api/handoff/context").json()["profiles"][0] == files["profile.json"]
                files["scenario-expected.json"] = {
                    "provenance": "SYNTHETIC actual checked scenario summary, not the full API response",
                    "baseline_match_score": 0,
                    "projected_match_score": 100,
                    "saved_profile_unchanged": True,
                    "company_readiness": None,
                }
                detail = "no entered Python claim: 0%; hypothetical Python: 100%; saved profile unchanged"
        if write:
            samples.mkdir(exist_ok=True)
            for name, data in files.items():
                (samples / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"PASS {module}: {detail}. Synthetic temporary store; no keys or network.")
        return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", choices=MODULES)
    parser.add_argument("--write-samples", action="store_true")
    arguments = parser.parse_args()
    example(arguments.module, arguments.write_samples)
