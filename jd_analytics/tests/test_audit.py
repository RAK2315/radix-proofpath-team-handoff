from jd_analytics.backend.service import extract


def test_repeated_requirement_uses_strongest_importance_and_its_source():
    result = extract([{"page": 1, "text": "Preferred: Python\nRequired: Python"}], "synthetic.pdf")
    assert len(result.requirement_groups) == 1
    assert result.requirement_groups[0].requirement_type == "mandatory"
    assert result.requirement_groups[0].evidence == "Required: Python"


def test_required_heading_applies_to_bullets():
    result = extract(
        [{"page": 1, "text": "Required qualifications\n- Python\n- SQL\nNice to have\n- Docker"}],
        "synthetic.pdf",
    )
    assert [g.requirement_type for g in result.requirement_groups] == ["mandatory", "mandatory", "preferred"]


def test_paste_text_is_saved_with_evidence_and_editable_review(client):
    text = "Company: Synthetic Test Co\nRole: API Engineer\nRequired: Python and SQL\nPreferred: Docker"
    response = client.post("/api/jd/extract-text", json={"text": text, "source_name": "Pasted synthetic JD"})
    assert response.status_code == 200
    value = response.json()
    assert value["document_id"] and value["source_file"].endswith(".txt")
    assert {s["skill_name"] for s in value["skills"]} == {"Python", "SQL", "Docker"}
    source = client.get(f"/api/documents/{value['document_id']}/download")
    assert source.content.decode("utf-8") == text


def test_paste_rejects_blank_and_oversized_inputs(client):
    for text in ["   ", "x" * 120001]:
        assert client.post("/api/jd/extract-text", json={"text": text}).status_code == 422


def test_company_and_role_metadata_are_not_requirements():
    result = extract(
        [{"page": None, "text": "Company: Docker Co\nRole: ML Engineer\nRequired: Python"}], "synthetic.txt"
    )
    assert {s.skill_name for s in result.skills} == {"Python"}


def test_internship_requirements_have_importance_title_and_no_intro_duplicates():
    text = """About the job
Machine Learning Intern
Company: Example Test Employer
About the Internship
We are interested in Machine Learning and Artificial Intelligence.
Responsibilities
- Work with Python and Machine Learning libraries.
- Perform feature engineering and exploratory data analysis.
Requirements
- Basic understanding of Machine Learning concepts and algorithms.
- Familiarity with Python programming.
- Knowledge of Pandas, NumPy, and Scikit-learn is an advantage.
- Basic understanding of statistics and data visualization.
- Familiarity with TensorFlow, PyTorch, or Deep Learning concepts is a plus.
- Knowledge of regression and predictive modeling is beneficial.
- Ability to work independently in a remote environment.
Who Can Apply?
Machine Learning enthusiasts welcome.
"""
    result = extract([{"page": None, "text": text}], "test.txt")
    assert result.role == "Machine Learning Intern"
    names = {s.skill_id: s.skill_name for s in result.skills}
    by_name = {names[sid]: g for g in result.requirement_groups for sid in g.skill_ids}
    assert by_name["Python"].requirement_type == "mandatory"
    assert by_name["Pandas"].requirement_type == "preferred"
    assert by_name["PyTorch"].operator == "OR"
    assert by_name["PyTorch"].requirement_type == "preferred"
    assert by_name["Predictive Modeling"].requirement_type == "preferred"
    assert by_name["Independent Remote Work"].requirement_type == "mandatory"
    assert by_name["Feature Engineering"].requirement_type == "unspecified"
    assert "Algorithms" not in names.values()  # ML algorithms alone are not a DSA claim.
    assert sum("Python" == names[sid] for g in result.requirement_groups for sid in g.skill_ids) == 1
    assert all("enthusiasts" not in g.evidence for g in result.requirement_groups)
