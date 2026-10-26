"""Explicitly synthetic downloadable examples; no candidate or company impersonation."""

import io
from typing import Literal

from docx import Document
from fastapi import APIRouter, Depends, Response

from shared.integrations.auth import Identity, identity
from shared.integrations.errors import AppError

router = APIRouter(prefix="/api/examples", tags=["Synthetic examples"])

EXAMPLES = {
    "jd": [
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Systems Co",
            "Role: Platform Engineer",
            "Key Responsibilities",
            "Required: Python and SQL",
            "Required: Docker and Linux",
            "Preferred: Kubernetes or AWS",
            "Communication and system design",
        ],
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Data Co",
            "Role: Data Analyst",
            "Key Responsibilities",
            "Required: SQL and statistics",
            "Required: Python or R programming",
            "Preferred: Power BI and machine learning",
        ],
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Systems Co",
            "Role: Application Engineer",
            "Required: Java and object-oriented design",
            "Required: Data structures and algorithms",
            "Preferred: Git and unit testing",
        ],
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Data Co",
            "Role: ML Engineer",
            "Required: Python and machine learning",
            "Required: PyTorch and SQL",
            "Preferred: AWS and Docker",
        ],
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Support Co",
            "Role: Support Analyst",
            "Required: SQL and Linux",
            "Required: Communication and networking",
            "Preferred: Shell scripting",
        ],
        [
            "SYNTHETIC TEST DOCUMENT - invented role and company",
            "Company: Synthetic Support Co",
            "Role: Cloud Operations Associate",
            "Required: Linux and TCP/IP",
            "Required: AWS and communication",
            "Preferred: Docker and system design",
        ],
    ],
    "resumes": [
        [
            "Synthetic Candidate Alpha",
            "alpha@example.test",
            "SYNTHETIC TEST RESUME - no real person",
            "Skills",
            "Python, SQL, Git, Linux",
            "Education",
            "Synthetic Institute - computing degree (test fixture)",
            "Projects",
            "Built Python and SQL services with Git and Linux",
            "Experience",
            "Synthetic practice internship - API development",
            "Certifications",
            "Synthetic SQL practice certificate",
        ],
        [
            "Synthetic Candidate Beta",
            "beta@example.test",
            "SYNTHETIC TEST RESUME - no real person",
            "Skills",
            "SQL, Power BI, statistics, machine learning",
            "Education",
            "Synthetic Institute - analytics degree (test fixture)",
            "Projects",
            "SQL and Power BI analysis with statistics",
            "Experience",
            "Synthetic data practice project",
        ],
        [
            "Synthetic Candidate Gamma",
            "gamma@example.test",
            "SYNTHETIC TEST RESUME - no real person",
            "Skills",
            "SQL, Linux, networking, communication, shell scripting",
            "Education",
            "Synthetic Institute - support studies (test fixture)",
            "Projects",
            "SQL troubleshooting on Linux with networking exercises",
            "Experience",
            "Synthetic helpdesk practice",
        ],
        [
            "Synthetic Candidate Delta",
            "delta@example.test",
            "SYNTHETIC TEST RESUME - no real person",
            "Skills",
            "Python, Java, SQL, Linux, Git, Docker, AWS, communication, PyTorch, machine learning, data structures, algorithms, object-oriented design",
            "Education",
            "Synthetic Institute - general computing (test fixture)",
            "Projects",
            "Python and SQL pipeline deployed with Docker and AWS",
            "Experience",
            "Synthetic Java services practice",
            "Certifications",
            "Synthetic networking practice badge",
        ],
    ],
}


def example_docx(kind: str, index: int) -> bytes:
    if kind not in EXAMPLES or not 0 <= index < len(EXAMPLES[kind]):
        raise AppError("EXAMPLE_NOT_FOUND", "Choose a synthetic JD index 0–5 or resume index 0–3", 404)
    document = Document()
    for line in EXAMPLES[kind][index]:
        document.add_paragraph(line)
    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()


@router.get("/{kind}/{index}")
def download(kind: Literal["jd", "resumes"], index: int, user: Identity = Depends(identity)):
    return Response(
        example_docx(kind, index),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="synthetic-{kind}-{index}.docx"'},
    )
