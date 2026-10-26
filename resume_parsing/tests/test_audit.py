import io

from reportlab.pdfgen import canvas

from resume_parsing.backend.service import extract
from shared.integrations.documents import read_document
from shared.integrations.extraction import validate_evidence


def test_detailed_families_context_and_action_evidence_remain_unverified():
    sections = [
        {
            "page": 1,
            "text": "Synthetic Candidate\nPROJECTS\nBuilt an audio pipeline for voice\nclassification.\nCreated a forecasting pipeline and deployed the API on Render.\nExplaining complex results and debugging model errors.\nSKILLS\nPython, Pandas, NumPy, PyTorch\n",
        }
    ]
    result = extract(sections, "synthetic.pdf")
    skills = {s.skill_name: s for s in result.skills}
    assert skills["Classification"].evidence.startswith("Built an audio pipeline")
    assert skills["Classification"].evidence_type == "project_mention"
    assert skills["Pandas"].skill_family == "Data Preparation & Analysis"
    assert skills["PyTorch"].skill_family == "Deep Learning & GenAI"
    assert {"Predictive Modeling", "Model Deployment", "Communication", "Problem Solving"} <= skills.keys()
    assert (
        not {"Statistics", "Supervised Learning", "Unsupervised Learning", "Data Visualization"}
        & skills.keys()
    )
    assert all(s.verification_status == "unverified" for s in result.skills)
    validate_evidence(result, sections)


def test_visual_pdf_order_beats_content_stream_order():
    stream = io.BytesIO()
    pdf = canvas.Canvas(stream)
    # A common template writes body objects before section headings.
    for y, line in [
        (780, "Synthetic Person"),
        (700, "Built a FastAPI service"),
        (720, "Voice classification project"),
        (600, "B.Tech Computing, Synthetic Institute"),
        (510, "Python, SQL"),
    ]:
        pdf.drawString(40, y, line)
    for y, line in [(740, "PROJECTS"), (620, "EDUCATION"), (530, "SKILLS")]:
        pdf.drawString(40, y, line)
    pdf.save()
    result = extract(read_document("synthetic-layout.pdf", stream.getvalue()), "synthetic-layout.pdf")
    assert any("Voice classification" in line for line in result.projects)
    assert any("B.Tech" in line for line in result.education)
    assert not any("Python, SQL" in line for line in result.education)


def test_unknown_sections_do_not_pollute_experience():
    result = extract(
        [
            {
                "page": None,
                "text": "Synthetic Person\nExperience\nBuilt Python services\nAwards & Achievements\nWon a synthetic hackathon\nSkills\nSQL",
            }
        ],
        "synthetic.docx",
    )
    assert result.experience == ["Built Python services"]


def test_conflicting_skill_mentions_require_review():
    result = extract(
        [{"page": None, "text": "Synthetic Person\nSkills\nPython and Java\nNo experience with Java"}],
        "synthetic.docx",
    )
    java = next(s for s in result.skills if s.skill_name == "Java")
    assert java.claim_status == "needs_review"


def test_negation_does_not_cross_an_explicit_contrast():
    result = extract(
        [{"page": None, "text": "Synthetic Profile\nSkills\nNo Java experience, but Python used daily."}],
        "synthetic.txt",
    )
    by_name = {s.skill_name: s for s in result.skills}
    assert by_name["Java"].claim_status == "needs_review"
    assert by_name["Python"].claim_status == "claimed"
