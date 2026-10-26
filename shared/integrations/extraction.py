"""Generic text/skill extraction infrastructure, shared by JD and resume features."""

import re
from typing import cast

from shared.contracts.models import Category, Extraction, Skill
from shared.integrations.errors import AppError

# Each named skill has exactly one RADIX category. Aliases here are extraction vocabulary.
VOCABULARY = {
    "C": ("COD", ["c"]),
    "Python": ("COD", ["python"]),
    "Java": ("COD", ["java"]),
    "JavaScript": ("COD", ["javascript", "js"]),
    "TypeScript": ("COD", ["typescript"]),
    "C++": ("COD", ["c++"]),
    "C#": ("COD", ["c#"]),
    "Go": ("COD", ["golang"]),
    "R": ("COD", ["r programming"]),
    "React": ("SWE", ["react", "reactjs", "react.js"]),
    "Node.js": ("SWE", ["node.js", "nodejs"]),
    "FastAPI": ("SWE", ["fastapi"]),
    "Django": ("SWE", ["django"]),
    "Spring": ("SWE", ["spring", "spring boot"]),
    "Git": ("SWE", ["git"]),
    "Testing": ("SWE", ["unit testing", "software testing", "pytest"]),
    "CI/CD": ("SWE", ["ci/cd", "continuous integration"]),
    "Agile": ("SWE", ["agile"]),
    "REST APIs": ("SWE", ["rest api", "rest apis", "restful"]),
    "Data Structures": ("DSA", ["data structures"]),
    "Algorithms": ("DSA", ["algorithms", "algorithm design"]),
    "Object-Oriented Design": ("OOD", ["object-oriented", "object oriented", "oop", "ood"]),
    "Design Patterns": ("OOD", ["design patterns"]),
    "Problem Solving": (
        "APTI",
        ["problem solving", "problem-solving", "aptitude", "debugging", "troubleshooting", "solve problems"],
    ),
    "Communication": (
        "COMM",
        [
            "communication",
            "presentation skills",
            "presented at",
            "explaining complex",
            "technical presentations",
        ],
    ),
    "Teamwork": ("COMM", ["teamwork", "collaboration", "collaborate with", "team lead", "led teams"]),
    "Machine Learning": ("AI", ["machine learning", "ml"]),
    "Deep Learning": ("AI", ["deep learning"]),
    "NLP": ("AI", ["nlp", "natural language processing"]),
    "LLMs": ("AI", ["llm", "llms", "large language models"]),
    "TensorFlow": ("AI", ["tensorflow"]),
    "PyTorch": ("AI", ["pytorch"]),
    "AWS": ("CLOUD", ["aws", "amazon web services"]),
    "Azure": ("CLOUD", ["azure"]),
    "GCP": ("CLOUD", ["gcp", "google cloud"]),
    "Docker": ("CLOUD", ["docker"]),
    "Kubernetes": ("CLOUD", ["kubernetes", "k8s"]),
    "SQL": ("SQL", ["sql", "structured query language"]),
    "PostgreSQL": ("SQL", ["postgresql", "postgres"]),
    "MySQL": ("SQL", ["mysql"]),
    "Database Design": ("SQL", ["database design", "relational databases"]),
    "System Design": ("SYSD", ["system design", "systems design"]),
    "Distributed Systems": ("SYSD", ["distributed systems"]),
    "Microservices": ("SYSD", ["microservices"]),
    "Networking": ("NETW", ["networking", "computer networks"]),
    "TCP/IP": ("NETW", ["tcp/ip", "tcp"]),
    "HTTP": ("NETW", ["http", "https"]),
    "DNS": ("NETW", ["dns"]),
    "Linux": ("OS", ["linux"]),
    "Operating Systems": ("OS", ["operating systems"]),
    "Shell Scripting": ("OS", ["shell scripting", "bash"]),
    "Excel": ("OTHER", ["excel"]),
    "Power BI": ("OTHER", ["power bi"]),
    "Tableau": ("OTHER", ["tableau"]),
    "Pandas": ("AI", ["pandas"]),
    "Statistics": ("APTI", ["statistics", "statistical analysis"]),
    "HTML/CSS": ("SWE", ["html/css", "html", "css"]),
    "scikit-learn": ("AI", ["scikit-learn", "sklearn"]),
    "NumPy": ("AI", ["numpy"]),
    "LightGBM": ("AI", ["lightgbm"]),
    "Streamlit": ("SWE", ["streamlit"]),
    "Plotly": ("OTHER", ["plotly"]),
    "Hugging Face": ("AI", ["hugging face", "huggingface"]),
    "Feature Engineering": ("AI", ["feature engineering"]),
    "Model Evaluation": ("AI", ["model evaluation", "evaluate model performance"]),
    "Computer Vision": ("AI", ["computer vision"]),
    "Reinforcement Learning": ("AI", ["reinforcement learning", "reinforcement-learning"]),
    "Classification": ("AI", ["classification"]),
    "Regression": ("AI", ["regression"]),
    "Ensemble Learning": ("AI", ["ensemble learning"]),
    "Data Preprocessing": ("AI", ["data preprocessing", "data-processing"]),
    "EDA": ("AI", ["eda", "exploratory data analysis"]),
    "librosa": ("AI", ["librosa"]),
    "RDKit": ("OTHER", ["rdkit"]),
    "Artificial Intelligence": ("AI", ["artificial intelligence"]),
    "Supervised Learning": ("AI", ["supervised learning", "supervised and unsupervised learning"]),
    "Unsupervised Learning": ("AI", ["unsupervised learning"]),
    "Predictive Modeling": (
        "AI",
        [
            "predictive modeling",
            "predictive modelling",
            "predictive analytics",
            "forecasting pipeline",
            "prediction pipeline",
        ],
    ),
    "Data Cleaning": ("AI", ["data cleaning", "clean datasets", "clean, preprocess"]),
    "Data Transformation": ("AI", ["data transformation"]),
    "Data Visualization": ("AI", ["data visualization", "data visualisation"]),
    "Model Deployment": (
        "AI",
        ["model deployment", "deployed the api", "deployed the model", "deployed the environment"],
    ),
    "Model Training": (
        "AI",
        ["model training", "training scripts", "training, and testing machine learning models"],
    ),
    "Analytical Thinking": ("APTI", ["analytical thinking"]),
    "Independent Remote Work": (
        "COMM",
        ["work independently in a remote environment", "remote collaboration"],
    ),
    "Willingness to Learn": ("COMM", ["willingness to learn"]),
    "Render": ("CLOUD", ["on render", "render,", "render.com"]),
    "Vercel": ("CLOUD", ["vercel"]),
    "LoRA": ("AI", ["lora"]),
    "GRPO": ("AI", ["grpo"]),
}

# Compile once per process rather than rebuilding every alias expression for each line.
SKILL_PATTERNS = {
    name: re.compile(r"(?<!\w)(?:" + "|".join(re.escape(a) for a in aliases) + r")(?![A-Za-z_+#])", re.I)
    for name, (_, aliases) in VOCABULARY.items()
}


def mentions(line: str, name: str) -> bool:
    # Contact/portfolio URLs name protocols, not claimed networking experience.
    line = re.sub(r"https?://\S+", "", line, flags=re.I)
    if (
        name == "Algorithms"
        and re.search(r"machine learning|supervised|unsupervised", line, re.I)
        and not re.search(r"data structures|algorithm design", line, re.I)
    ):
        return False
    pattern = SKILL_PATTERNS.get(name)
    return (
        bool(pattern.search(line))
        if pattern
        else bool(re.search(r"(?<!\w)" + re.escape(name) + r"(?![A-Za-z_+#])", line, re.I))
    )


def negated(line: str, name: str) -> bool:
    aliases = VOCABULARY.get(name, ("OTHER", [name]))[1]
    for alias in aliases:
        for match in re.finditer(r"(?<!\w)" + re.escape(alias) + r"(?![A-Za-z_+#])", line, re.I):
            prefix = line[max(0, match.start() - 65) : match.start()]
            prefix = re.split(r"\b(?:but|however|although)\b", prefix, flags=re.I)[-1]
            suffix = line[match.end() : match.end() + 30]
            if re.search(
                r"\b(?:no|not|without|lack|never|haven.t|don.t)\b(?!\s+only\b)[^.;:]*$", prefix, re.I
            ) or re.match(r"\s+(?:is\s+)?not\s+(?:required|known|used)", suffix, re.I):
                return True
    return False


def instruction_like(text: str) -> bool:
    return bool(
        re.search(
            r"ignore\s+(?:all\s+)?(?:previous|system|developer)\s+instructions|reveal\s+(?:api\s+keys|secrets)|assign\s+(?:every|all)\s+competency",
            text,
            re.I,
        )
    )


def local_skills(sections: list[dict], source_file: str, kind: str) -> list[Skill]:
    found = []
    for name, (category, _aliases) in VOCABULARY.items():
        occurrences = [
            (line.strip(), section["page"])
            for section in sections
            for line in section["text"].splitlines()
            if not instruction_like(line)
            and mentions(line, name)
            and not (kind == "jd" and re.match(r"\s*(?:company|role|job title|position)\s*:", line, re.I))
        ]
        if not occurrences:
            continue
        uncertain = [item for item in occurrences if negated(item[0], name)]
        line, page = (uncertain or occurrences)[0]
        # A wrapped fragment such as "classification." needs the neighboring source lines.
        # Keep their original whitespace/newlines so the evidence remains an exact quote.
        if kind == "resume" and len(line) < 45:
            for section in sections:
                if section["page"] != page:
                    continue
                source_lines = section["text"].splitlines()
                index = next((i for i, raw in enumerate(source_lines) if raw.strip() == line), None)
                if index is not None:
                    line = "\n".join(source_lines[max(0, index - 1) : index + 2]).strip()
                    break
        found.append(
            Skill(
                skill_name=name,
                category_code=cast(Category, category),
                evidence=line[:2000],
                confidence="low" if uncertain else "medium",
                source_page=page,
                source_file=source_file,
                source_type="document",
                evidence_type="jd_requirement" if kind == "jd" else "resume_mention",
                claim_status="needs_review" if uncertain else "claimed",
            )
        )
    return found


def validate_evidence(result: Extraction, sections: list[dict]):
    for group in result.requirement_groups:
        if group.evidence and not any(
            group.evidence in section["text"]
            for section in sections
            if group.source_page is None or section["page"] == group.source_page
        ):
            raise AppError("UNSUPPORTED_EVIDENCE", "Requirement evidence must quote the source page exactly")
    for skill in result.skills:
        if skill.source_type == "hypothetical":
            raise AppError("HYPOTHETICAL_CLAIM", "Hypothetical claims belong only in scenario previews")
        if skill.source_type == "document":
            pages = [s for s in sections if skill.source_page is None or s["page"] == skill.source_page]
            if not skill.evidence.strip() or not any(skill.evidence in s["text"] for s in pages):
                raise AppError(
                    "UNSUPPORTED_EVIDENCE",
                    f"Evidence for {skill.skill_name} must quote its source page exactly",
                )


def hosted_extract(kind: str, sections: list[dict], filename: str, instructions: str = "") -> Extraction:
    from shared.integrations.llm import extract_proposals

    return extract_proposals(kind, sections, filename, instructions)
