"""Descriptive skill families supplement, and never replace, RADIX competency categories."""

SKILL_FAMILIES = {
    "Programming Languages": {"C", "C++", "C#", "Python", "Java", "JavaScript", "TypeScript", "Go", "R"},
    "Web & APIs": {"React", "Node.js", "FastAPI", "Django", "Spring", "REST APIs", "HTML/CSS", "Streamlit"},
    "Data Structures & Design": {
        "Data Structures",
        "Algorithms",
        "Object-Oriented Design",
        "Design Patterns",
    },
    "Machine Learning": {
        "Machine Learning",
        "Artificial Intelligence",
        "Supervised Learning",
        "Unsupervised Learning",
        "Classification",
        "Regression",
        "Ensemble Learning",
        "Predictive Modeling",
        "LightGBM",
        "scikit-learn",
        "Model Training",
    },
    "Deep Learning & GenAI": {
        "Deep Learning",
        "NLP",
        "LLMs",
        "TensorFlow",
        "PyTorch",
        "Hugging Face",
        "Computer Vision",
        "Reinforcement Learning",
        "LoRA",
        "GRPO",
        "librosa",
    },
    "Data Preparation & Analysis": {
        "Pandas",
        "NumPy",
        "Feature Engineering",
        "Data Preprocessing",
        "Data Cleaning",
        "Data Transformation",
        "EDA",
        "RDKit",
    },
    "Statistics & Evaluation": {"Statistics", "Model Evaluation"},
    "Data Visualization & BI": {"Data Visualization", "Plotly", "Tableau", "Power BI", "Excel"},
    "Databases": {"SQL", "PostgreSQL", "MySQL", "Database Design"},
    "Cloud & Deployment": {
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Render",
        "Vercel",
        "Model Deployment",
    },
    "Engineering Practices": {"Git", "Testing", "CI/CD", "Agile"},
    "Systems & Architecture": {"System Design", "Distributed Systems", "Microservices"},
    "Networks & Operating Systems": {
        "Networking",
        "TCP/IP",
        "HTTP",
        "DNS",
        "Linux",
        "Operating Systems",
        "Shell Scripting",
    },
    "Analytical Skills": {"Problem Solving", "Analytical Thinking"},
    "Collaboration & Work Habits": {
        "Communication",
        "Teamwork",
        "Independent Remote Work",
        "Willingness to Learn",
    },
    "Other": set(),
}


_FAMILY_BY_NAME = {name.casefold(): family for family, names in SKILL_FAMILIES.items() for name in names}


def family_for(name: str) -> str:
    return _FAMILY_BY_NAME.get(name.casefold(), "Other")
