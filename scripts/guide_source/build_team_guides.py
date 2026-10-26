# ruff: noqa: E402
"""Author and verify five human-readable module PDFs without changing application code."""

import hashlib
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "team_guides"
TMP = ROOT / "verification/local/pdf-review"
os.environ.update(
    RADIX_ENV="development",
    RADIX_AUTH_MODE="local",
    RADIX_STORAGE_MODE="local",
    RADIX_DOCUMENT_STORAGE_MODE="local",
    RADIX_LLM_MODE="rules",
    RADIX_LLM_API_KEY="",
    GROQ_API_KEY="",
)

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from team_guide_content import MODULES

from jd_analytics.backend.service import extract as extract_jd
from resume_parsing.backend.service import extract as extract_resume
from shared.contracts.models import (
    CATEGORIES,
    Extraction,
    MatchingResult,
    Profile,
    Rating,
    ReadinessResult,
    ScenarioRequest,
    ScenarioResult,
)
from shared.integrations.documents import read_document
from shared.integrations.extraction import validate_evidence
from skill_matching.backend.matcher import evaluate as match
from skill_matching.backend.scenarios import preview
from talent_check.backend.scoring import evaluate as readiness

pdfmetrics.registerFont(TTFont("Guide", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("GuideBold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("GuideItalic", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFont(TTFont("GuideMono", "C:/Windows/Fonts/consola.ttf"))
pdfmetrics.registerFontFamily(
    "Guide", normal="Guide", bold="GuideBold", italic="GuideItalic", boldItalic="GuideBold"
)

NAVY = colors.HexColor("#111C30")
INK = colors.HexColor("#18243B")
MUTED = colors.HexColor("#526079")
BLUE = colors.HexColor("#3459C6")
TEAL = colors.HexColor("#08756B")
PAPER = colors.HexColor("#F4F6FA")
BORDER = colors.HexColor("#DCE2EB")
AMBER = colors.HexColor("#8A5100")
WHITE = colors.white
WIDTH, HEIGHT = A4
CONTENT_W = WIDTH - 88

STYLES = {
    "body": ParagraphStyle(
        "body", fontName="Guide", fontSize=10.8, leading=15.4, textColor=INK, spaceAfter=8
    ),
    "small": ParagraphStyle(
        "small", fontName="Guide", fontSize=9.2, leading=12.8, textColor=MUTED, spaceAfter=6
    ),
    "h1": ParagraphStyle("h1", fontName="GuideBold", fontSize=24, leading=28, textColor=NAVY, spaceAfter=12),
    "h2": ParagraphStyle(
        "h2", fontName="GuideBold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=9, spaceAfter=8
    ),
    "h3": ParagraphStyle(
        "h3", fontName="GuideBold", fontSize=11.2, leading=15, textColor=BLUE, spaceBefore=4, spaceAfter=5
    ),
    "kicker": ParagraphStyle(
        "kicker", fontName="GuideBold", fontSize=9, leading=13, textColor=BLUE, spaceAfter=9
    ),
    "code": ParagraphStyle("code", fontName="GuideMono", fontSize=8.8, leading=11.8, textColor=INK),
    "cell": ParagraphStyle("cell", fontName="Guide", fontSize=9.4, leading=13, textColor=INK),
    "cellsmall": ParagraphStyle("cellsmall", fontName="Guide", fontSize=8.4, leading=11.2, textColor=INK),
    "header": ParagraphStyle("header", fontName="GuideBold", fontSize=9, leading=12, textColor=WHITE),
}


def ascii_text(text):
    return str(text).translate(
        str.maketrans(
            {
                "\u2014": " - ",
                "\u2013": "-",
                "\u2011": "-",
                "\u2192": " -> ",
                "\u00d7": " x ",
                "\u2019": "'",
                "\u2018": "'",
                "\u201c": '"',
                "\u201d": '"',
                "\u2026": "...",
            }
        )
    )


def p(text, style="body"):
    return Paragraph(escape(ascii_text(text)).replace("\n", "<br/>"), STYLES[style])


def rich(text, style="body"):
    return Paragraph(ascii_text(text), STYLES[style])


def heading(section, title, sub=None):
    items = [p(section.upper(), "kicker"), p(title, "h1")]
    if sub:
        items.append(p(sub))
    return items


def note(title, text, tone="blue"):
    color = BLUE if tone == "blue" else TEAL if tone == "teal" else AMBER
    background = (
        colors.HexColor("#EEF2FC")
        if tone == "blue"
        else colors.HexColor("#EAF6F2")
        if tone == "teal"
        else colors.HexColor("#FFF5E3")
    )
    table = Table([[p(title, "h3")], [p(text, "small")]], colWidths=[CONTENT_W - 22])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
            ]
        )
    )
    return [table, Spacer(1, 10)]


def grid(headers, rows, widths=None, small=False):
    widths = widths or [0.31, 0.69]
    cellstyle = "cellsmall" if small else "cell"
    data = [[p(h, "header") for h in headers]] + [[p(v, cellstyle) for v in row] for row in rows]
    table = Table(data, colWidths=[CONTENT_W * w for w in widths], hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, NAVY),
                ("LINEBELOW", (0, 1), (-1, -1), 0.35, BORDER),
            ]
        )
    )
    return table


def code(text):
    text = ascii_text(text)
    # JSON lines remain legible; reject rather than silently shrink code that is too wide.
    for line in text.splitlines():
        if pdfmetrics.stringWidth(line, "GuideMono", 8.8) > CONTENT_W - 24:
            raise ValueError("Code line too wide: " + line)
    block = Preformatted(text, STYLES["code"])
    box = Table([[block]], colWidths=[CONTENT_W])
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return [box, Spacer(1, 9)]


class Journey(Flowable):
    def __init__(self, active):
        super().__init__()
        self.width = CONTENT_W
        self.height = 58
        self.active = active

    def draw(self):
        c = self.canv
        labels = ["JD", "Resume", "Profile", "Talent Check", "Match + GPS"]
        gap = 7
        w = (self.width - gap * 4) / 5
        for i, label in enumerate(labels):
            x = i * (w + gap)
            c.setFillColor(BLUE if i + 1 == self.active else PAPER)
            c.setStrokeColor(BLUE if i + 1 == self.active else BORDER)
            c.roundRect(x, 15, w, 34, 5, fill=1, stroke=1)
            c.setFillColor(WHITE if i + 1 == self.active else MUTED)
            c.setFont("GuideBold", 8.1)
            c.drawCentredString(x + w / 2, 28, label)
        c.setFont("Guide", 8)
        c.setFillColor(MUTED)
        c.drawString(0, 2, "The shared journey; each module also runs independently.")


class Screen(Flowable):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.width = CONTENT_W
        self.height = 355

    def draw(self):
        c = self.canv
        w = self.width
        h = self.height
        c.setFillColor(PAPER)
        c.setStrokeColor(BORDER)
        c.roundRect(0, 0, w, h, 7, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.roundRect(0, 0, 77, h, 7, fill=1, stroke=0)
        c.setFont("GuideBold", 9)
        c.setFillColor(WHITE)
        c.drawString(11, h - 25, "RADIX")
        labels = ["JD Analytics", "Resume", "Profile", "Talent Check", "Matching"]
        for i, label in enumerate(labels):
            y = h - 67 - i * 37
            if i + 1 == self.module["n"]:
                c.setFillColor(BLUE)
                c.roundRect(7, y - 10, 63, 26, 4, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Guide", 7.4)
            c.drawString(11, y, label)
        x = 91
        inner = w - x - 13
        c.setFillColor(MUTED)
        c.setFont("Guide", 8)
        c.drawString(x, h - 23, "Candidate  |  Job  |  Clear source mode")
        c.setFillColor(NAVY)
        c.setFont("GuideBold", 16)
        c.drawString(x, h - 52, self.module["ui_title"])
        y = h - 71
        for label, title, _detail in self.module["ui_blocks"]:
            c.setFillColor(WHITE)
            c.setStrokeColor(BORDER)
            c.roundRect(x, y - 45, inner, 43, 4, fill=1, stroke=1)
            c.setFillColor(BLUE)
            c.setFont("GuideBold", 7.3)
            c.drawString(x + 9, y - 15, label)
            c.setFillColor(INK)
            c.setFont("Guide", 9.2)
            # Split human labels to avoid a dense illegible miniature UI.
            shown = ascii_text(title)
            if pdfmetrics.stringWidth(shown, "Guide", 9.2) > inner - 18:
                c.setFont("Guide", 8.5)
            c.drawString(x + 9, y - 32, shown)
            y -= 51
        c.setFillColor(MUTED)
        c.setFont("GuideItalic", 8)
        c.drawString(x, 14, "Illustrative layout guide, not a live application screenshot.")


def model_examples():
    examples = {}
    for kind, name, extractor in [
        ("jd", "junior-data-engineer-jd-SYNTHETIC.docx", extract_jd),
        ("resume", "mira-cv-SYNTHETIC.pdf", extract_resume),
    ]:
        sections = read_document(name, (ROOT / "demo/final" / name).read_bytes())
        value = extractor(sections, name, False)
        value.id = str(uuid5(NAMESPACE_URL, "team-guide:" + kind))
        value.document_id = str(uuid5(NAMESPACE_URL, "team-guide:document:" + kind))
        value.review_status = "reviewed"
        value.revision = 2
        for skill in value.skills:
            skill.source_document_id = value.document_id
        validate_evidence(value, sections)
        examples[kind] = value
    resume = examples["resume"]
    candidate = Profile(
        id=str(uuid5(NAMESPACE_URL, "team-guide:profile")),
        revision=1,
        name=resume.name,
        email=resume.email,
        education=resume.education,
        projects=resume.projects,
        experience=resume.experience,
        internships=resume.internships,
        certifications=resume.certifications,
        skills=deepcopy(resume.skills),
        cv_file=resume.document_id,
        preferred_roles=["Junior Data Engineer"],
        ratings=[Rating(category_code=category, level=4) for category in CATEGORIES],
    )
    bundle = json.loads((ROOT / "data/synthetic/benchmarks.json").read_text())
    from talent_check.backend.benchmark_repository import digest

    bundle["content_hash"] = digest(bundle["companies"])
    company = next(c for c in bundle["companies"] if c["id"] == "lab-data")
    ready = ReadinessResult.model_validate(readiness(candidate, company, bundle))
    matched = MatchingResult.model_validate(match(candidate, examples["jd"]))
    scenario = ScenarioRequest(
        profile_id=candidate.id,
        jd_id=examples["jd"].id,
        profile_revision=candidate.revision,
        jd_revision=examples["jd"].revision,
        company_id="lab-data",
        benchmark_mode="synthetic",
        benchmark_hash=bundle["content_hash"],
        skill_overrides=["Docker"],
        category_overrides={"SQL": 9},
    )
    projected = ScenarioResult.model_validate(preview(candidate, examples["jd"], scenario, bundle))
    assert ready.readiness_score == 74.9 and matched.match_score == 75
    assert (
        projected.projected_match.match_score == 87.5
        and projected.projected_readiness.readiness_score == 79.5
    )
    examples.update(
        profile=candidate, readiness=ready, matching=matched, scenario=projected, scenario_request=scenario
    )
    directory = OUT / "contracts"
    directory.mkdir(parents=True, exist_ok=True)
    for name, value in examples.items():
        (directory / (name + "-SYNTHETIC.json")).write_text(
            value.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    (directory / "README.txt").write_text(
        "All people, employers, values and IDs are synthetic teaching snapshots. IDs do not exist in a live workspace.\n"
        "Files are validated against the current Python contracts; numeric demo uses rules extraction and invented ratings.\n"
        "Never use snapshot IDs for live requests. Upload/save real current inputs and use their returned IDs/revisions.\n",
        encoding="utf-8",
    )
    return examples


def page1(m):
    a = heading(f"MODULE {m['n']:02d} / TEAMMATE FIELD GUIDE", m["name"], m["mission"])
    a += [
        Journey(m["n"]),
        Spacer(1, 12),
        grid(["You receive", "You return"], [(m["input"], m["output"])], [0.5, 0.5]),
        Spacer(1, 8),
    ]
    a += [
        p("Your responsibility", "h2"),
        p(m["required"]),
        p("A successful handoff looks like this", "h2"),
        p(m["win"]),
    ]
    a += note(
        "Start from the working baseline",
        "Assume YOU own this module. Run and understand the supplied working source, finish or improve your part, and test it. Push the verified working copy to YOUR OWN GitHub repository. Return its URL, commit SHA, actual test results and known limitations to the Scrum Master. No central merge or PR is required from you.",
    )
    a += [grid(["Before your module", "After your module"], [(m["receives"], m["hands"])], [0.5, 0.5])]
    a += [
        Spacer(1, 10),
        p(
            "Read in order: 2 build plan | 3 screen layout | 4 API | 5 logic | 6 integration | 7 tests | 8 presentation | 9 exact field reference",
            "small",
        ),
    ]
    return a


def page2(m):
    a = heading(
        "02 / IMPLEMENTATION PLAN",
        "What to do, in order.",
        "Keep changes inside your feature folder. Each step has an observable result; do not begin by replacing the whole app.",
    )
    for i, (title, text) in enumerate(m["steps"], 1):
        a.append(KeepTogether([p(f"{i:02d}  {title}", "h3"), p(text)]))
    a += [
        p("Files to open first", "h2"),
        p("All paths below are relative to " + m["folder"] + "/.", "small"),
        grid(["File", "What it owns"], m["files"], [0.43, 0.57], True),
    ]
    return a


def page3(m):
    a = heading(
        "03 / SCREEN AND USER EXPERIENCE",
        "What it should look like.",
        "Keep the current app shell, navigation, typography and shared controls. The drawing shows information order, not a redesign request.",
    )
    a += [Screen(m), Spacer(1, 10)]
    a += [
        grid(["Screen state", "Expected visible behavior"], m["ui_states"], [0.29, 0.71], True),
        Spacer(1, 9),
    ]
    a += [
        p(
            "Visual rules: 16 px body/form text, 14 px minimum supporting labels; clear headings; 44 px touch targets. Navy #111C30, blue #3459C6, white cards and #F4F6FA canvas. Use the existing Inter web font. On mobile, stack panels and keep actions readable. Do not rely on color alone for status.",
            "small",
        )
    ]
    return a


def snapshot_summary(m, e):
    key = {1: "jd", 2: "resume", 3: "profile", 4: "readiness", 5: "matching"}[m["n"]]
    raw = e[key].model_dump(mode="json")
    selected = {k: raw[k] for k in m["response_keys"]}
    # Complete JSON, deliberately a view of the full payload, not a copy-paste replacement.
    return json.dumps(selected, indent=2, ensure_ascii=True)


def page4(m, e):
    a = heading(
        "04 / EXACT API BOUNDARY",
        "Input, output and format.",
        "Use the current Pydantic/OpenAPI contract. A UI label can change; an agreed JSON field cannot be renamed independently.",
    )
    a += [
        grid(["Endpoint", "Body or result"], m["endpoints"], [0.46, 0.54], True),
        Spacer(1, 8),
        p(m["request_label"], "h3"),
    ]
    if m.get("request_code"):
        a += code(m["request_code"])
    else:
        request = deepcopy(m["request"])
        if m["n"] == 1:
            # Show literal newlines as JSON escapes, with line width kept readable.
            a += code("""{
  "text": "Required: Python and SQL",
  "source_name": "Synthetic JD",
  "hosted_consent": false
}""")
        else:
            a += code(json.dumps(request, indent=2))
    a += [
        p("Current synthetic response excerpt", "h3"),
        p(
            "Only selected fields are shown below. Page 9 describes the complete shape. Snapshot UUIDs are teaching examples, not IDs to reuse in a running app.",
            "small",
        ),
    ]
    a += code(snapshot_summary(m, e))
    a += [
        p(
            "Every mutation needs X-ProofPath-Client: web (or cli). Cloud requests also need the current user's Bearer JWT. The shared web helper supplies these headers. File upload uses multipart; never manually set its boundary. JSON fields use snake_case.",
            "small",
        )
    ]
    return a


def page5(m, e):
    a = heading("05 / REASONING AND BUSINESS RULES", m["logic_title"], m["logic_intro"])
    if m.get("formula"):
        a += code(m["formula"])
    a += [grid(["Situation", "Exact expected reasoning"], m["logic_rows"]), Spacer(1, 10)]
    a += note("Important edge case", m["special"])
    if m["n"] in (1, 2):
        a += [
            p("The LLM path", "h2"),
            p(
                "Document reader -> rules as hints -> consented Groq strict JSON -> schema/quote checks -> server-owned IDs -> editable proposals -> reviewed save. Model claims start needs_review; verification stays unverified. One bounded regeneration is allowed for invalid output. Provider errors produce an honest fallback by default."
            ),
        ]
    elif m["n"] == 3:
        a += code("""POST /api/profiles/import-resume
{
  "resume_id": "CURRENT_REVIEWED_RESUME_ID",
  "profile": {"name": "Synthetic Candidate"},
  "replace_existing": false
}
// Response is a merged draft: save it explicitly.""")
    elif m["n"] == 5:
        a += [
            p("GPS must compare one frozen baseline", "h2"),
            p(
                "Request current profile_revision + jd_revision, optional benchmark_hash, skill_overrides=['Docker'] and category_overrides={'SQL':9}. Reject overrides outside the selected JD and stale versions. Baseline/projected results come from the same engines; no profile write occurs."
            ),
        ]
    a += note("Never cross this boundary", m["guard"], "amber")
    return a


def page6(m):
    a = heading(
        "06 / INTEGRATION AGREEMENT",
        "Own it. Test it. Publish your part.",
        "Your task is a working module on your own GitHub. Keep the supplied shared contracts and exact output formats so the Scrum Master can integrate the returned code.",
    )
    entry = {
        1: "backend/service.py: extract(sections, filename, hosted=False) -> Extraction. Input sections are page/text dictionaries; the route supplies document ownership and persistence.",
        2: "backend/service.py: extract(sections, filename, hosted=False) -> Extraction. Keep resume source_type and the reviewed Profile Builder handoff.",
        3: "backend/service.py: import_resume(request, resume) -> Profile preview; validate_sources(profile, user) before save. The router owns HTTP/storage calls.",
        4: "backend/scoring.py: evaluate(profile, company, bundle) -> result dictionary. The router validates ReadinessResult and records the receipt; GPS reuses evaluate.",
        5: "matcher.evaluate(profile, jd) -> result dictionary; scenarios.preview(profile, jd, request, bundle) -> preview dictionary. HTTP routes validate the shared result models.",
    }[m["n"]]
    a += [
        grid(
            ["Team rule", "What you do"],
            [
                ("Service boundary", entry),
                (
                    "One feature owner",
                    f"Own {m['folder']}/backend, frontend, tests and docs. Keep the common support area in your clone. Run your module independently before claiming it works.",
                ),
                (
                    "One contract source",
                    "Read shared/contracts/models.py. OpenAPI and generated TypeScript follow it. Do not maintain a second handwritten schema or change categories alone.",
                ),
                (
                    "One storage/auth path",
                    "Use shared store/document/auth helpers. Do not add a second database, anonymous cloud owner, public CV URL or frontend API secret.",
                ),
                (
                    "One current record",
                    "Use actual returned IDs/revisions, owned by the signed-in user. Pass saved IDs to consumers; never hardcode teaching snapshot IDs.",
                ),
                (
                    "Your GitHub",
                    "Create a private repository on YOUR account. Rename the old origin to scrum-master, set your new origin, review staged files and scan for secrets, then commit and push. See SUBMIT_YOUR_REPOSITORY.md.",
                ),
                (
                    "Return working evidence",
                    "Fill DELIVERY.md with your URL, commit SHA, actual commands/results, three normal and three failure cases, synthetic screenshots and known bugs. If a check fails, fix it or report it honestly; do not copy passing counts.",
                ),
            ],
            [0.27, 0.73],
            True,
        ),
        Spacer(1, 8),
    ]
    a += [
        p("The official category vocabulary", "h2"),
        p(
            "Every extracted skill has exactly one official code or OTHER. The extra descriptive skill families are filters, not replacement categories. Only the twelve official codes can have numeric ratings or company expectations.",
            "small",
        ),
    ]
    pairs = list(CATEGORIES.items())
    rows = [(pairs[i][0] + " - " + pairs[i][1], pairs[i + 6][0] + " - " + pairs[i + 6][1]) for i in range(6)]
    a += [grid(["Category", "Category"], rows, [0.5, 0.5], True), Spacer(1, 8)]
    a += note(
        "Keep these meanings separate",
        "Confidence = how clearly the document supports an extraction. Competency = explicit self-rating, null or 1-10. Review = a human checked the output. Verified = independently established; this app's claims remain unverified. Hypothetical = GPS preview only.",
        "teal",
    )
    return a


def page7(m):
    a = heading(
        "07 / RUN AND VERIFY",
        "Your definition of done.",
        "A module must run independently as well as inside the shared app. Record actual commands and failures; a screenshot or a copied passing count is not test evidence.",
    )
    a += [
        p("Use the existing project, not a second app", "h3"),
        p(
            "From the repository root, install the existing requirements/lockfiles if needed. Open two terminals. If the ports are already running, use them; do not kill unknown processes. Never overwrite an existing .env.",
            "small",
        ),
    ]
    a += code(
        f".\\{m['folder']}\\run.ps1 api\n# Separate terminal:\n.\\{m['folder']}\\run.ps1 web\n# Real standalone API check:\n.\\{m['folder']}\\run.ps1 check"
    )
    a += [
        p(
            "Clone the full repo and install root dependencies (README). Run these from its root. Open http://127.0.0.1:5173/; Load synthetic inputs supplies upstream fixtures. No key is needed for rules. A Groq key belongs only in the private root .env; restart Python after editing it.",
            "small",
        )
    ]
    a += [grid(["Test", "Pass means"], m["tests"]), Spacer(1, 8)]
    a += [p("Your focused commands", "h3")]
    a += code(m["unitcmd"] + "\n" + m["frontcmd"])
    a += [
        p(
            "Before returning: run typecheck, lint, build and the standalone browser check. Use the project virtualenv for Python. Keep assertions meaningful and record actual results.",
            "small",
        )
    ]
    a += note(
        "Error behavior to demonstrate",
        "422 = invalid/unreadable input; 413 = size limit; 415 = unsupported file; 404 = missing/unowned record; 409 = stale revision; 503 = unavailable storage/benchmark. Groq may fall back and return a successful Extraction with llm_status=unavailable instead of an HTTP error. Show the status, not just HTTP 200.",
    )
    return a


def page8(m):
    a = heading(
        "08 / LIVE DEMO AND PRESENTATION",
        "Show it. Explain it. Hand it over.",
        "Suggested speaking time: four minutes per module. Five modules use about 20 minutes, leaving 10 for the problem, architecture, challenge and close within the 30-minute presentation. Q&A is separate (15 minutes).",
    )
    a += [p("Reproducible synthetic demo", "h2")]
    for i, step in enumerate(m["demo"], 1):
        a.append(rich(f"<b>{i}.</b> " + escape(ascii_text(step))))
    a += [
        p("What to say and show", "h2"),
        grid(["Time", "Speaking cue"], m["talk"], [0.19, 0.81], True),
        Spacer(1, 8),
    ]
    a += note("Transition to the next speaker", m["transition"], "teal")
    a += [
        p("Use this language honestly", "h3"),
        p(
            "Say which parts you implemented, adapted, tested or learned. If showing the working team baseline, call it the integrated team implementation. Do not claim a live model, official benchmark or feature history that has not actually been demonstrated.",
            "small",
        ),
    ]
    return a


def schema_fields(model):
    schema = model.model_json_schema()
    props = schema["properties"]
    return props


def page9(m):
    a = heading(
        "09 / FIELD REFERENCE AND QUESTIONS",
        "Keep this beside your editor.",
        "These are exact field names from the current Python contracts. Defaults fill omitted optional fields; partial excerpts are not safe replacements for full PATCH payloads.",
    )
    if m["n"] in (1, 2):
        rows = [
            (
                "Identity / version",
                "schema_version, id, revision, source_type, source_file, document_id, input_method",
            ),
            ("Document context", "company, role, name, email, sections"),
            (
                "Content arrays",
                "skills, requirement_groups, education, projects, experience, certifications, internships, hackathons, achievements",
            ),
            (
                "Lifecycle / processing",
                "review_status, extraction_mode, parser_version, model_version, prompt_version, llm_status, llm_metadata, warnings",
            ),
            ("Each skill: identity", "skill_id, skill_name, normalized_name, category_code, skill_family"),
            (
                "Each skill: evidence",
                "evidence, confidence, source_page, source_start, source_end, source_file, source_document_id, source_type, evidence_type",
            ),
            (
                "Each skill: state",
                "verification_status=unverified; claim_status=claimed|needs_review; claim_basis=explicit|inferred",
            ),
            (
                "Each requirement group",
                "requirement_id, skill_ids, operator=AND|OR, requirement_type=mandatory|preferred|unspecified, requires_review, evidence, source_page",
            ),
        ]
    elif m["n"] == 3:
        rows = [
            ("Profile scalar fields", "schema_version, id, revision, name, email, cv_file"),
            (
                "Background string arrays",
                "education, hackathons, internships, certifications, preferred_roles, projects, experience, achievements",
            ),
            (
                "Skills array",
                "Skill objects: identity/category/family, exact source evidence/provenance, confidence, claim basis and review state. Keep all fields from the shared model.",
            ),
            (
                "Ratings array",
                "Exactly twelve entries: category_code, level=null|1-10, origin=self_reported. OTHER cannot be rated.",
            ),
            (
                "Import request",
                "resume_id, profile (the full current draft), replace_existing=false. Returns a Profile preview without saving.",
            ),
            ("CV reference", "cv_file is an owned document ID, not a filename or public download URL."),
        ]
    elif m["n"] == 4:
        rows = [
            ("Result identity", "company, company_id, profile_id, profile_revision"),
            (
                "Score / completeness",
                "readiness_score, status=complete|incomplete, rating_completeness, evidence_coverage",
            ),
            (
                "Source / explanation",
                "skillset_gap, rules_version, benchmark_source, benchmark_hash, methodology, receipt_id",
            ),
            (
                "Each category row",
                "category_code, category_name, required_level, candidate_level, gap, shortfall, status, attainment, contribution, evidence, rating_origin, recommended_action",
            ),
            (
                "Row states",
                "unknown, below_expected, meets_expected, above_expected. Unknown candidate_level/gap/attainment/contribution are null.",
            ),
            (
                "Benchmark source",
                "source_mode, source_table, fetched_at, content_hash, notice. Keep synthetic provenance explicit; exported real data needs validated origin.",
            ),
        ]
    else:
        rows = [
            ("Matching identity", "jd_source_file, jd_id, jd_revision, profile_id, profile_revision"),
            (
                "Matching explanation",
                "match_score, matched_skills, missing_skills, ambiguous_matches, contributions, rules_version, status, methodology, receipt_id",
            ),
            (
                "Decision record",
                "requirement_id, skill_name, category_code, matched, requirement_type, jd_evidence, candidate_evidence, decision_type, reason, suggested_review, recommended_action, score_contribution",
            ),
            (
                "Contribution group",
                "requirement_id, operator, requirement_type, skills, weight, coverage, weighted_contribution, requires_review, member_count, matched_count, score_contribution",
            ),
            (
                "Scenario request",
                "profile_id, jd_id, profile_revision, jd_revision, optional company_id/benchmark_mode/benchmark_hash; skill_overrides; category_overrides",
            ),
            (
                "Scenario result",
                "hypothetical=true, baseline_match, projected_match, baseline_readiness, projected_readiness, match_delta, readiness_delta, recommendations, profile_revision, notice",
            ),
        ]
    a += [grid(["Group", "Exact fields / meaning"], rows, [0.27, 0.73], True), Spacer(1, 7)]
    a += [p("Questions you should answer without memorizing code", "h2")]
    for q, answer in m["qa"]:
        a.append(rich("<b>" + escape(q) + "</b> " + escape(answer), "small"))
    a += [
        p("Source of truth and current limits", "h3"),
        p(
            "Read your module's README.md, PLAN.md, CONTRACT.md and USAGE.md; shared/contracts/models.py; docs/BUILD_PLAN.md; docs/DEPLOYMENT_SETUP.md; docs/LLM_EXTRACTION_IMPLEMENTATION.md; verification/RESULTS.md; and docs/TEAM_PRESENTATION_CHECKLIST.md. Full current validated synthetic JSON snapshots are under data/synthetic/handoff/. Snapshot IDs are not live IDs.",
            "small",
        ),
    ]
    a += [
        p(
            "Original Participant Brief: pp.7-10 (roles/contracts), p.11 (official test pack), p.13 (stack/done). Event Plan p.4: 30 minutes presentation + 15 Q&A. Original baseline suite (see new checkout results in verification/RESULTS.md): 134 backend, 17 frontend and 14 browser tests. Live Groq quality, cloud RLS/deployment and official organizer-pack/benchmark acceptance remain pending. All guide examples are synthetic.",
            "small",
        )
    ]
    return a


def footer(canvas, doc, m):
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, HEIGHT - 7, WIDTH, 7, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Guide", 8)
    canvas.drawString(44, HEIGHT - 28, f"RADIX PROOFPATH  /  MODULE {m['n']:02d}")
    canvas.drawRightString(WIDTH - 44, HEIGHT - 28, "TEAM HANDOFF  |  26 OCT 2026")
    canvas.setStrokeColor(BORDER)
    canvas.line(44, 38, WIDTH - 44, 38)
    canvas.setFont("Guide", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(44, 25, ascii_text(m["name"]))
    canvas.drawRightString(WIDTH - 44, 25, f"{doc.page} / 9")
    canvas.restoreState()


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    examples = {
        name: model.model_validate_json(
            (ROOT / "data/synthetic/handoff" / (name + "-SYNTHETIC.json")).read_text()
        )
        for name, model in {
            "jd": Extraction,
            "resume": Extraction,
            "profile": Profile,
            "readiness": ReadinessResult,
            "matching": MatchingResult,
            "scenario": ScenarioResult,
            "scenario_request": ScenarioRequest,
        }.items()
    }
    manifest = {
        "date": "2026-10-26",
        "scope": "Five module teammate teaching guides. No application edits or external calls.",
        "files": [],
    }
    for m in MODULES:
        name = f"RADIX_{m['n']:02d}_{m['folder'].title()}_Teammate_Guide.pdf"
        target = ROOT / m["folder"] / "GUIDE.pdf"
        doc = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            leftMargin=44,
            rightMargin=44,
            topMargin=50,
            bottomMargin=52,
            title=f"RADIX ProofPath - Module {m['n']}: {m['name']} - Teammate Guide",
            author="RADIX ProofPath team",
            subject="Module ownership, implementation, contracts, integration and presentation",
        )
        story = []
        for i, func in enumerate([page1, page2, page3, page4, page5, page6, page7, page8, page9]):
            if i:
                story.append(PageBreak())
            story += func(m, examples) if func in (page4, page5) else func(m)
        doc.build(
            story,
            onFirstPage=lambda c, d, mod=m: footer(c, d, mod),
            onLaterPages=lambda c, d, mod=m: footer(c, d, mod),
        )
        reader = PdfReader(target)
        assert len(reader.pages) == 9, (name, len(reader.pages))
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            assert len(text) > 300, (name, i)
            assert f"{i} / 9" in text, (name, i)
            assert "\ufffd" not in text, (name, i)
        manifest["files"].append(
            {
                "name": name,
                "pages": len(reader.pages),
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        )
        print(name, len(reader.pages), "pages")
    (TMP / "verification.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
