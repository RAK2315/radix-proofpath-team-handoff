from conftest import pdf_bytes
from jd_analytics.backend.service import extract as extract_jd
from resume_parsing.backend.service import extract as extract_resume
from shared.contracts.models import CATEGORIES, Profile, Rating
from shared.integrations.documents import read_document
from shared.integrations.examples import EXAMPLES, example_docx
from skill_matching.backend.matcher import evaluate as match
from talent_check.backend.benchmark_repository import load
from talent_check.backend.scoring import evaluate as readiness


def test_full_synthetic_matrix_with_pdf_docx_parity():
    """Invented fixtures only: 24 JD pairs and 12 company comparisons, no official pack claims."""
    jobs = []
    for index, lines in enumerate(EXAMPLES["jd"]):
        parsed = extract_jd(read_document("synthetic.docx", example_docx("jd", index)), "synthetic.docx")
        pdf = extract_jd(read_document("synthetic.pdf", pdf_bytes(lines)), "synthetic.pdf")
        assert {s.skill_name for s in parsed.skills} == {s.skill_name for s in pdf.skills}
        parsed.review_status = "reviewed"
        jobs.append(parsed)
    candidates = []
    for index, lines in enumerate(EXAMPLES["resumes"]):
        parsed = extract_resume(
            read_document("synthetic.docx", example_docx("resumes", index)), "synthetic.docx"
        )
        pdf = extract_resume(read_document("synthetic.pdf", pdf_bytes(lines)), "synthetic.pdf")
        assert {s.skill_name for s in parsed.skills} == {s.skill_name for s in pdf.skills}
        # Explicit team-authored ratings, unrelated to extraction confidence.
        candidates.append(
            Profile(
                name=parsed.name,
                skills=parsed.skills,
                ratings=[Rating(category_code=c, level=3 + index) for c in CATEGORIES],
            )
        )
    job_matrix = [[match(candidate, job)["match_score"] for job in jobs] for candidate in candidates]
    bundle = load("synthetic")
    company_matrix = [
        [readiness(candidate, company, bundle)["readiness_score"] for company in bundle["companies"]]
        for candidate in candidates
    ]
    assert len(job_matrix) == 4 and all(len(row) == 6 for row in job_matrix)
    assert len(company_matrix) == 4 and all(len(row) == 3 for row in company_matrix)
    assert len({tuple(row) for row in job_matrix}) == 4
    assert len({tuple(row) for row in company_matrix}) == 4
    assert all(0 <= score <= 100 for row in job_matrix + company_matrix for score in row)
