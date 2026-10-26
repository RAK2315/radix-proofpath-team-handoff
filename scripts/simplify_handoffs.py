"""Archive redundant module documents and create two small synthetic teaching inputs."""

import shutil
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
MODULES = ["jd_analytics", "resume_parsing", "profile_builder", "talent_check", "skill_matching"]
KEEP = {"backend", "frontend", "tests", "samples", "run.ps1", "START_HERE.md", "START_HERE.pdf"}


def build():
    for module in MODULES:
        archive = ROOT / "docs/internal/archive" / module
        archive.mkdir(parents=True, exist_ok=True)
        for path in (ROOT / module).iterdir():
            if path.name in KEEP or path.name == "__pycache__":
                continue
            target = archive / path.name
            assert ROOT in path.resolve().parents and ROOT in target.resolve().parents
            if target.exists():
                raise RuntimeError(f"Archive already contains {target.name}; inspect before replacing")
            shutil.move(str(path), str(target))
        # Keep the old launcher as historical information before writing the simpler one.
        launcher = ROOT / module / "run.ps1"
        if launcher.exists() and not (archive / "run.ps1").exists():
            shutil.copy2(launcher, archive / "run.ps1")
        (ROOT / module / "samples").mkdir(exist_ok=True)
    for module, filename, lines in [
        (
            "jd_analytics",
            "practice-jd-SYNTHETIC",
            [
                "SYNTHETIC TEACHING JD - NOT OFFICIAL ORGANIZER DATA",
                "Company: Synthetic Teaching Co",
                "Role: Junior Developer",
                "Required: Python",
            ],
        ),
        (
            "resume_parsing",
            "practice-cv-SYNTHETIC",
            [
                "SYNTHETIC TEACHING CV - NOT A REAL PERSON",
                "Name: Asha Sample (synthetic)",
                "Email: asha@example.test",
                "Technical Skills",
                "Python",
                "Projects",
                "Built a small Python quiz for invented training exercises.",
                "Education",
                "Fictional Computing College - invented course.",
            ],
        ),
    ]:
        directory = ROOT / module / "samples"
        document = Document()
        for line in lines:
            document.add_paragraph(line)
        document.save(directory / (filename + ".docx"))
        pdf = canvas.Canvas(str(directory / (filename + ".pdf")), pagesize=A4)
        pdf.setTitle(filename)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(48, 790, lines[0])
        pdf.setFont("Helvetica", 12)
        for index, line in enumerate(lines[1:]):
            pdf.drawString(48, 754 - index * 26, line)
        pdf.save()


if __name__ == "__main__":
    build()
