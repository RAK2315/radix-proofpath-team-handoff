import pytest

from conftest import pdf_bytes
from resume_parsing.backend.service import extract
from shared.integrations.documents import read_document
from shared.integrations.errors import AppError
from shared.integrations.examples import EXAMPLES, example_docx
from shared.integrations.extraction import hosted_extract


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("format", ["pdf", "docx"])
def test_two_synthetic_resumes(index, format):
    content = pdf_bytes(EXAMPLES["resumes"][index]) if format == "pdf" else example_docx("resumes", index)
    result = extract(read_document(f"synthetic.{format}", content), f"synthetic.{format}")
    assert result.email.endswith("@example.test")
    assert result.education and result.projects and result.experience
    assert result.company is None and result.role is None
    assert all(s.verification_status == "unverified" for s in result.skills)


def test_absent_fields_not_fabricated():
    result = extract(
        [{"page": None, "text": "Synthetic Candidate\nSkills\nSQL and Python"}], "synthetic.docx"
    )
    assert result.education == [] and result.certifications == [] and result.email == ""


def test_no_hosted_provider_without_configuration():
    with pytest.raises(AppError) as error:
        hosted_extract("resume", [{"page": None, "text": "Synthetic resume"}], "synthetic.docx")
    assert error.value.code == "LLM_NOT_CONFIGURED"
