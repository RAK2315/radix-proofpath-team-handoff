"""Measure finite-set extraction coverage on explicitly invented, inspectable cases.

This is a development regression set, not a statistical estimate of real-world accuracy.
"""

import argparse
import json
from pathlib import Path

from jd_analytics.backend.service import extract as extract_jd
from resume_parsing.backend.service import extract as extract_resume
from scripts.evaluation_documents import ROOT, cases, render
from shared.integrations.documents import read_document
from shared.integrations.extraction import validate_evidence


def evaluate() -> dict:
    records = []
    for case in cases():
        for extension in case["formats"]:
            filename = f"{case['id']}.{extension}"
            sections = read_document(filename, render(case, extension))
            result = (extract_jd if case["kind"] == "jd" else extract_resume)(sections, filename)
            validate_evidence(result, sections)
            actual = {s.skill_name for s in result.skills}
            expected = set(case["expected_skills"])
            ids = {s.skill_id: s.skill_name for s in result.skills}
            groups = sorted(
                [
                    {
                        "skills": sorted(ids[sid] for sid in g.skill_ids),
                        "importance": g.requirement_type,
                        "operator": g.operator,
                        "review": g.requires_review,
                    }
                    for g in result.requirement_groups
                ],
                key=lambda g: ",".join(g["skills"]),
            )
            expected_groups = sorted(
                [{**g, "skills": sorted(g["skills"])} for g in case.get("expected_groups", [])],
                key=lambda g: ",".join(g["skills"]),
            )
            fields = {
                field: any(quote in line for line in getattr(result, field))
                for field, quote in case.get("expected_sections", {}).items()
            }
            records.append(
                {
                    "id": case["id"],
                    "kind": case["kind"],
                    "format": extension,
                    "true_positives": sorted(actual & expected),
                    "false_positives": sorted(actual - expected),
                    "false_negatives": sorted(expected - actual),
                    "review_actual": sorted(
                        s.skill_name for s in result.skills if s.claim_status == "needs_review"
                    ),
                    "review_expected": sorted(case.get("expected_review", [])),
                    "name_correct": result.name == case["expected_name"] if "expected_name" in case else None,
                    "sections_correct": fields,
                    "groups_correct": groups == expected_groups if "expected_groups" in case else None,
                    "groups_actual": groups,
                    "warnings": result.warnings,
                    "source_quotes_valid": True,
                    "verification": sorted({s.verification_status for s in result.skills}),
                }
            )
    tp = sum(len(r["true_positives"]) for r in records)
    fp = sum(len(r["false_positives"]) for r in records)
    fn = sum(len(r["false_negatives"]) for r in records)
    return {
        "scope": "Synthetic development evaluation: 12 invented documents rendered in PDF and DOCX; not held out, independent or official. Metrics count distinct named skills per document/format. Negated mentions are expected extractions marked for review, not positive competency claims.",
        "documents": len(records),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(tp / (tp + fp), 4) if tp + fp else None,
        "recall": round(tp / (tp + fn), 4) if tp + fn else None,
        "records": records,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evaluation/final.json")
    args = parser.parse_args()
    report = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "records"}, indent=2))
    for record in report["records"]:
        print(
            f"{record['id']} ({record['format']}): FP={record['false_positives']}, FN={record['false_negatives']}, name={record['name_correct']}, fields={record['sections_correct']}, groups={record['groups_correct']}, review={record['review_actual']}"
        )
