"""Create the PDF and Markdown from the same beginner lesson, including complete real examples."""

import hashlib
import json
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from lesson_data import LESSONS
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
NAVY, BLUE, GREY = "#17253B", "#2854B8", "#526075"


def compact(value, depth=0):
    """Valid complete JSON with small flat objects on one line; never drop fields."""
    prefix = "  " * depth
    if isinstance(value, dict):
        if not value:
            return "{}"

        def leaf(v):
            return (
                not isinstance(v, (dict, list))
                or not v
                or (isinstance(v, list) and all(not isinstance(item, (dict, list)) for item in v))
            )

        if all(leaf(v) for v in value.values()) and depth > 0:
            return json.dumps(value, ensure_ascii=True, separators=(", ", ": "))
        return (
            "{\n"
            + ",\n".join(
                prefix + "  " + json.dumps(k) + ": " + compact(v, depth + 1) for k, v in value.items()
            )
            + "\n"
            + prefix
            + "}"
        )
    if isinstance(value, list):
        if not value or all(not isinstance(v, (dict, list)) for v in value):
            return json.dumps(value, ensure_ascii=True)
        return "[\n" + ",\n".join(prefix + "  " + compact(v, depth + 1) for v in value) + "\n" + prefix + "]"
    return json.dumps(value, ensure_ascii=True)


def block(kind, text):
    return {"kind": kind, "text": text}


def lesson(module, data):
    def p(text):
        return block("p", text)

    def h(text):
        return block("h", text)

    def item(text):
        return block("item", text)

    def code(text):
        return block("code", text)

    def full(path):
        return f"{module}/{path}"

    samples = ROOT / module / "samples"
    request = json.loads((samples / data["request_file"]).read_text())
    response = json.loads((samples / data["response_file"]).read_text())
    sections = []
    sections.append(
        (
            "1. What am I making?",
            [
                p(
                    "RADIX ProofPath helps a candidate understand job readiness. Five teammates own five parts: JD Analytics -> Resume Parsing -> Profile Builder -> Talent Check -> Skill Matching. You own part "
                    + str(data["number"])
                    + "."
                ),
                h(data["tagline"]),
                p(data["purpose"]),
                h("Why your part matters"),
                p(data["why"]),
                h("What the user gives you"),
                p(data["input"]),
                h("What you return"),
                p(data["output"]),
                h("A small example"),
                p(data["example"]),
                h("Start with the working code"),
                p(
                    "This is a working starting point, not an instruction to rebuild an app. Clone the WHOLE repository so shared support is available. Work mainly in "
                    + module
                    + "/. Read this one guide, run it, then improve a problem you can demonstrate."
                ),
                p(
                    "Your folder has this guide as PDF and Markdown, backend/, frontend/, tests/, samples/ and run.ps1. Shared support is stored once at the root. The Markdown contains the same teaching content and full examples as this PDF."
                ),
            ],
        )
    )
    sections.append(
        (
            "2. What exactly must I build?",
            [
                h("Organizer requirements - keep these working"),
                *[item(t) for t in data["requirements"]],
                h("Already implemented"),
                p(data["built"]),
                h("Your development checklist"),
                *[item(f"{i}. {t}") for i, t in enumerate(data["tasks"], 1)],
                h("Currently missing or unverified"),
                p(data["missing"]),
                h("Extra ProofPath features"),
                p(data["innovation"]),
            ],
        )
    )
    sections.append(
        (
            "3. How does it work?",
            [
                block("diagram", "  ->  ".join(step for step, _ in data["flow"])),
                *[item(f"{i}. {title}: {text}") for i, (title, text) in enumerate(data["flow"], 1)],
                h("Words you will see"),
                p(
                    "Backend = Python server code. Frontend = React browser screen. API = an address the screen calls to send/receive data. A contract/schema is the agreed field list, defined in shared/contracts/models.py. An LLM is a language model that interprets text; Groq runs it. Supabase is the cloud database service."
                ),
                h("The shared RADIX categories"),
                p(
                    "COD Coding; DSA Data Structures & Algorithms; OOD Object-Oriented Design; APTI Aptitude; COMM Communication; AI Artificial Intelligence; CLOUD Cloud; SQL SQL; SWE Software Engineering; SYSD System Design; NETW Networking; OS Operating Systems."
                ),
                p(
                    "Each skill has exactly one category, or OTHER. Descriptive skill families are extra UI filters, not new rated categories. Unknown competency is null, never zero. Confidence describes extraction support, not ability. What-if changes never save a real profile."
                ),
            ],
        )
    )
    sections.append(
        (
            "4. Inputs and outputs",
            [
                p(data["receiver"]),
                h(data["endpoint"]),
                p(data["request_intro"]),
                p("Complete input example: " + full("samples/" + data["request_file"])),
                code(compact(request)),
                h("Important fields"),
                *[item(name + ": " + meaning) for name, meaning in data["fields"]],
                p(data["api_notes"]),
                p(
                    "The next page(s) show the COMPLETE captured response from the existing API, including defaults and empty fields. Long lines wrap for reading. Use samples/output.json for exact machine-readable JSON. IDs, receipt IDs, source hashes and times can differ between runs; do not hardcode them. JSON null means unknown/not present; [] means an empty list."
                ),
            ],
        )
    )
    # Keep the complete response as a real code block in Markdown. Split only its visual PDF layout.
    sections.append(
        (
            "Complete output example",
            [p(full("samples/" + data["response_file"])), block("json", compact(response))],
        )
    )
    sections.append(
        (
            "5. How do I work on the code?",
            [
                h("Install and run - Windows PowerShell"),
                p(
                    "Install Python 3.10+, Node.js 24 LTS (includes npm), Git and an editor such as VS Code. Accept the installers' PATH option, reopen PowerShell and clone the full GitHub repository. Open a terminal at the repository root - the folder containing package.json."
                ),
                code(
                    f".\\{module}\\run.ps1 setup\n# Terminal 1:\n.\\{module}\\run.ps1 api\n# A SECOND terminal, same root:\n.\\{module}\\run.ps1 web"
                ),
                p(
                    "Open http://127.0.0.1:5173/. Server API help is at http://127.0.0.1:8000/docs. setup creates .venv and installs locked Python/npm dependencies plus Chromium for browser tests. Run setup once; no key is needed. Keep api and web running; Ctrl+C stops your own server. Only one module uses 8000/5173 at a time."
                ),
                h("Open these files first"),
                *[item(full(name) + " - " + detail) for name, detail in data["sources"]],
                p(data["shared_sources"]),
                h("Make one useful change"),
                p(
                    "Read a failing example, locate the responsible function, change that part and add a test in your tests/ or frontend test file. Do not rename shared fields, duplicate common code or rewrite other modules. Ask the Scrum Master before changing shared contracts, storage or provider code."
                ),
                h("What should I see?"),
                p(data["screen"]),
                p(
                    "Load synthetic inputs supplies pre-reviewed Mira records for independent operation. It is not fresh extraction. The tiny Asha terminal examples and the richer Mira browser examples are intentionally different inputs."
                ),
            ],
        )
    )
    inventory = {
        "input.json": "Complete upload description or JSON request shown in this guide.",
        "output.json": "Complete response captured from that actual API request.",
        "expected.json": "Small expected-result checklist; compare semantics, not generated IDs.",
        "practice-jd-SYNTHETIC.pdf": "Tiny invented Python JD for upload testing.",
        "practice-jd-SYNTHETIC.docx": "The same teaching JD in Word format.",
        "practice-cv-SYNTHETIC.pdf": "Tiny fictional Asha CV for upload testing.",
        "practice-cv-SYNTHETIC.docx": "The same fictional CV in Word format.",
        "cv-upload-SYNTHETIC.pdf": "Fictional Mira CV for checking Profile Builder's direct CV attachment.",
        "reviewed-resume.json": "Reviewed Mira input snapshot for understanding import.",
        "import-request.json": "Full import-preview request with resume ID and profile draft.",
        "import-preview.json": "Actual import result; it remains a draft until explicitly saved.",
        "candidate.json": "Full synthetic candidate with twelve deliberately invented ratings of 4.",
        "company.json": "One labelled invented company and all twelve required levels.",
        "profile.json": "Saved synthetic beginner profile with no entered skill claims.",
        "jd.json": "Manually reviewed teaching JD requiring Python; not a model extraction claim.",
        "scenario-request.json": "Full what-if request adding hypothetical Python.",
        "scenario-expected.json": "Checked summary: 0 -> 100 matching; saved profile unchanged. Not a full API response.",
    }
    sections.append(
        (
            "6. How do I know it works?",
            [
                code(f".\\{module}\\run.ps1 example\n.\\{module}\\run.ps1 test"),
                p(
                    "example runs the small teaching case in a fresh temporary database and checks its result. test runs your real standalone API check, Python tests, React tests, type checking, lint, your production build and your browser test. It stops on failure. Both use synthetic data; tests force rules mode and do not prove live LLM quality."
                ),
                *[item(title + ": " + text) for title, text in data["tests"]],
                h("Use an unfamiliar document too"),
                p(
                    "Use only documents you own or have permission to process. Before running extraction, list expected skills and supporting words yourself. Compare missing and invented skills, sections, groups and quotes. A successful API response or valid JSON is not proof of correct extraction. Do not commit real CVs or send them to Groq without explicit permission."
                ),
                h("If something fails"),
                p(
                    "Read the FIRST error. Missing Python/npm: install and reopen the terminal. Missing packages: rerun setup. Browser cannot reach API: keep api running. Port busy: stop your own earlier server or coordinate a free port; do not kill unknown processes. Wrong extraction: compare the source, review and add a regression case."
                ),
            ],
        )
    )
    resources = [
        h("What you can do now"),
        p(
            "All local teaching inputs are synthetic. No organizer pack, API key or cloud account is needed to run, edit and test your module. The tiny samples teach fields and behavior; the larger reconstructed pack remains under data/synthetic/. Neither is official organizer data."
        ),
        h("Your samples - every file has a purpose"),
        *[
            item(path.name + " - " + inventory[path.name])
            for path in sorted(samples.iterdir())
            if path.is_file()
        ],
    ]
    if module in {"jd_analytics", "resume_parsing"}:
        resources += [
            h("Groq: needed for live LLM verification, not offline practice"),
            p(
                "Use an authorized Groq account/key. If root .env does not exist, copy .env.example to .env; otherwise edit the existing private file carefully. Add these server-side values, restart api, choose hosted consent for ONE synthetic upload and check llm_status=processed plus source correctness. No LangChain wrapper is used; this implementation calls Groq directly."
            ),
            code(
                "RADIX_LLM_MODE=auto\nRADIX_LLM_API_KEY=YOUR_PRIVATE_GROQ_KEY\nRADIX_LLM_MODEL=openai/gpt-oss-20b"
            ),
            p(
                "The placeholder is not a real key. Never put the key in frontend code, VITE_ variables, Git, a screenshot or an AI upload. If unavailable, continue rules-mode development and report live verification pending. If the model/key is unavailable, the configured fallback may return rules with llm_status=unavailable; do not call it model success."
            ),
        ]
    elif module == "talent_check":
        resources += [
            h("When organizer access arrives"),
            p(
                "The Scrum Master needs the authorized Supabase project URL, read permission/credential, actual company/category/level columns and any required company IDs or filters for staging_company_skill_levels. Configure private root .env using RADIX_BENCHMARK_URL, RADIX_BENCHMARK_KEY (or authorized access token) and RADIX_BENCHMARK_MAPPING. An authorized local export can use RADIX_BENCHMARK_EXPORT instead. Do not guess a schema or invent expected levels."
            ),
            p(
                "Verify twelve unique valid values per company and test real mode. Until then show source unavailable and use explicitly selected synthetic mode for practice. Never write the organizer staging table; never publish its keys or private exports."
            ),
        ]
    else:
        resources += [
            h("Other modules and cloud resources"),
            p(
                "The shared folder and locked root dependencies are required; clone the whole repository. The local workspace supplies reviewed upstream snapshots, so you do not wait for a teammate's server. Later, integration uses real saved IDs, versions and owned source links, not the snapshot UUIDs in this guide."
            ),
            p(
                "Supabase accounts, live database rules and real organizer data are configured and verified by the Scrum Master when authorized. Local SQLite storage already works. Module 3 needs no LLM; Module 5's named-JD matching also needs no LLM or company data. Company-readiness previews remain unavailable without a valid chosen benchmark."
            ),
        ]
    sections.append(("7. Missing resources and what to do", resources))
    ai = (
        f"Help me complete module {data['number']}: {data['title']} step by step using this guide. "
        "First run it; request the exact section-5 source files and tests before editing. Preserve working code and shared fields. "
        "Fix a reproduced issue and test it. Keep confidence separate from competency and scenarios separate from saved profiles. "
        "Never invent official data or request pasted keys. Help me submit my own GitHub URL, tested commit, results and honest limitations."
    )
    sections.append(
        (
            "8. Submit and explain your module",
            [
                h("Completion checklist"),
                p(
                    "[ ] I can run/explain it. [ ] Required inputs/outputs work. [ ] Normal/failure cases checked. [ ] Tests passed or failures reported. [ ] Contracts/source links preserved. [ ] No secrets/private CVs committed."
                ),
                h("Push to YOUR own GitHub"),
                p(
                    "Create an EMPTY private repository on your own account. From your full working clone, replace the URL below with YOUR new repository, review/stage only your changes, then run:"
                ),
                code(
                    f'git remote rename origin scrum-master\ngit remote add origin https://github.com/YOU/YOUR-REPO.git\ngit add {module}\n.\\.venv\\Scripts\\python.exe scripts/scan_handoff.py --staged\ngit commit -m "Verify my RADIX module"\ngit push -u origin main'
                ),
                p(
                    "Keep the whole working clone, including your source/tests/samples, guides, launcher and shared support. Never force-push. Grant the Scrum Master access if private."
                ),
                p(
                    "Return URL, git rev-parse HEAD, changed files, actual test commands/results, three normal + three failure cases, synthetic screenshots and limitations. Distinguish implemented, mock-tested, live-verified and pending. The Scrum Master handles integration; you need not solve central merges."
                ),
                h("A 45-second explanation for judges"),
                p(data["judge"]),
                h("Three likely questions"),
                *[item(q + " " + a) for q, a in data["questions"]],
                h("Copy this prompt into your AI assistant"),
                p(ai),
            ],
        )
    )
    return sections


class FlowDiagram(Flowable):
    def __init__(self, text):
        super().__init__()
        self.steps = text.split("  ->  ")
        self.width, self.height = 499, 66

    def draw(self):
        c = self.canv
        for i, step in enumerate(self.steps):
            col, row = i % 3, i // 3
            x, y = col * 170, 36 - row * 34
            c.setFillColor(colors.HexColor("#EAF0FA"))
            c.roundRect(x, y, 158, 27, 5, fill=1, stroke=0)
            c.setFillColor(colors.HexColor(NAVY))
            c.setFont("GuideBold", 10)
            c.drawString(x + 9, y + 9, f"{i + 1}. {step}")


def build():
    for name, path in [("Guide", "arial.ttf"), ("GuideBold", "arialbd.ttf"), ("GuideMono", "consola.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / path)))
    styles = {
        "p": ParagraphStyle(
            "Body", fontName="Guide", fontSize=11.2, leading=15, textColor=colors.HexColor(NAVY), spaceAfter=7
        ),
        "h": ParagraphStyle(
            "Subheading",
            fontName="GuideBold",
            fontSize=12.3,
            leading=16,
            textColor=colors.HexColor(BLUE),
            spaceBefore=5,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "title": ParagraphStyle(
            "Title",
            fontName="GuideBold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor(NAVY),
            spaceAfter=17,
        ),
        "item": ParagraphStyle(
            "List",
            fontName="Guide",
            fontSize=11.0,
            leading=14.7,
            textColor=colors.HexColor(NAVY),
            leftIndent=11,
            firstLineIndent=-9,
            spaceAfter=7,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="GuideMono",
            fontSize=9.7,
            leading=12.4,
            textColor=colors.HexColor(NAVY),
            backColor=colors.HexColor("#F1F4F8"),
            borderPadding=7,
            spaceBefore=6,
            spaceAfter=10,
        ),
    }
    manifest = []
    for module, data in LESSONS.items():
        sections = lesson(module, data)
        markdown = [f"# Module {data['number']}: {data['title']} - START HERE\n"]
        story = []
        for index, (title, blocks) in enumerate(sections):
            if index:
                story.append(PageBreak())
            story.append(Paragraph(escape(title), styles["title"]))
            markdown.append("## " + title + "\n")
            for entry in blocks:
                kind, text = entry["kind"], entry["text"]
                if kind in {"code", "json"}:
                    markdown.append("```" + ("json" if kind == "json" else "text") + "\n" + text + "\n```\n")
                    lines = []
                    bundles = []
                    for line in text.splitlines():
                        wrapped = textwrap.wrap(
                            line,
                            width=89,
                            subsequent_indent="  ",
                            replace_whitespace=False,
                            drop_whitespace=False,
                        ) or [""]
                        bundles.append(wrapped)
                        lines.extend(wrapped)
                    if kind == "json":
                        # Each part contains consecutive lines of the same full JSON object.
                        chunks = [[]]
                        for bundle in bundles:
                            if chunks[-1] and len(chunks[-1]) + len(bundle) > 51:
                                chunks.append([])
                            chunks[-1].extend(bundle)
                        for number, chunk in enumerate(chunks):
                            if number:
                                story.append(PageBreak())
                                story.append(Paragraph("Complete output - continued", styles["title"]))
                            story.append(Preformatted("\n".join(chunk), styles["code"]))
                    else:
                        story.append(Preformatted("\n".join(lines), styles["code"]))
                elif kind == "diagram":
                    markdown.append(text + "\n")
                    story.append(FlowDiagram(text))
                    story.append(Spacer(1, 10))
                else:
                    markdown.append(("### " if kind == "h" else "- " if kind == "item" else "") + text + "\n")
                    story.append(Paragraph(("- " if kind == "item" else "") + escape(text), styles[kind]))
        (ROOT / module / "START_HERE.md").write_text("\n".join(markdown), encoding="utf-8")
        target = ROOT / module / "START_HERE.pdf"

        def footer(canvas, doc, label=data["title"], n=data["number"]):
            canvas.setFillColor(colors.HexColor(BLUE))
            canvas.rect(0, A4[1] - 6, A4[0], 6, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor(GREY))
            canvas.setFont("Guide", 8.2)
            canvas.drawString(48, A4[1] - 32, f"RADIX PROOFPATH  /  MODULE {n:02d}")
            canvas.drawRightString(A4[0] - 48, A4[1] - 32, "START HERE  /  26 OCT 2026")
            canvas.setStrokeColor(colors.HexColor("#DDE3EC"))
            canvas.line(48, 38, A4[0] - 48, 38)
            canvas.drawString(48, 24, label)
            canvas.drawRightString(A4[0] - 48, 24, str(doc.page))

        document = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            leftMargin=48,
            rightMargin=48,
            topMargin=57,
            bottomMargin=53,
            title=f"RADIX ProofPath - {data['title']} - Start Here",
            author="RADIX ProofPath team",
        )
        document.build(story, onFirstPage=footer, onLaterPages=footer)
        reader = PdfReader(target)
        manifest.append(
            {
                "path": target.relative_to(ROOT).as_posix(),
                "pages": len(reader.pages),
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        )
        print(module, len(reader.pages), "pages")
        assert 8 <= len(reader.pages) <= 10, (module, len(reader.pages))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        assert "Copy this prompt" in text and "Complete output" in text and "\ufffd" not in text
        for page in reader.pages:
            assert len(page.extract_text() or "") > 150
        # The Markdown embeds exactly the captured complete response; no ellipses or omitted fields.
        assert json.loads(
            compact(json.loads((ROOT / module / "samples/output.json").read_text()))
        ) == json.loads((ROOT / module / "samples/output.json").read_text())
    (ROOT / "verification/pdf-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    build()
