from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PAPER_DIR = Path(__file__).resolve().parents[1]
OUTPUT = PAPER_DIR / "output" / "pdf" / "evidence-aware-agentic-graphrag-review.pdf"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2F75B5")
CYAN = colors.HexColor("#DDEBF7")
GREEN = colors.HexColor("#548235")
LIGHT_GREEN = colors.HexColor("#E2F0D9")
ORANGE = colors.HexColor("#C65911")
LIGHT_ORANGE = colors.HexColor("#FCE4D6")
RED = colors.HexColor("#A61C2D")
LIGHT_RED = colors.HexColor("#F4CCCC")
INK = colors.HexColor("#202A35")
MUTED = colors.HexColor("#5F6B76")
GRID = colors.HexColor("#B8C2CC")


def _register_font() -> str:
    candidates = (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    )
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("PaperSans", str(path)))
            return "PaperSans"
    return "Helvetica"


FONT = _register_font()


class BoxFlow(Flowable):
    def __init__(self, width: float, height: float, rows: list[list[tuple]]) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.rows = rows

    def draw(self) -> None:
        canvas = self.canv
        for row in self.rows:
            for item in row:
                x, y, width, height, label, fill, stroke = item
                canvas.setFillColor(fill)
                canvas.setStrokeColor(stroke)
                canvas.roundRect(x, y, width, height, 5, fill=1, stroke=1)
                canvas.setFillColor(INK)
                canvas.setFont(FONT, 7.5)
                lines = label.split("\n")
                baseline = y + height / 2 + (len(lines) - 1) * 4
                for index, line in enumerate(lines):
                    canvas.drawCentredString(x + width / 2, baseline - index * 9, line)


class ArchitectureFlow(BoxFlow):
    def __init__(self, width: float) -> None:
        box_width = 88
        rows = [
            [
                (0, 200, 82, 35, "User query", LIGHT_GREEN, GREEN),
                (100, 200, 102, 35, "Context resolver\n+ ambiguity gate", CYAN, BLUE),
                (220, 200, 96, 35, "Orchestrator\n lane routing", CYAN, BLUE),
                (334, 200, 132, 35, "Specialist agent\n tools + memory + workflow", LIGHT_ORANGE, ORANGE),
            ],
            [
                (15, 115, box_width, 42, "BM25\nQdrant", CYAN, BLUE),
                (125, 115, box_width, 42, "Dense BGE-M3\nQdrant", CYAN, BLUE),
                (235, 115, box_width, 42, "Entity/path graph\nNeo4j", CYAN, BLUE),
                (345, 115, 112, 42, "Typed tools\nGPA / grade / tuition", LIGHT_ORANGE, ORANGE),
            ],
            [
                (70, 35, 135, 40, "Union + deduplicate\nRRF + reranker", LIGHT_GREEN, GREEN),
                (230, 35, 135, 40, "PostgreSQL governance\ncoverage + provenance", LIGHT_GREEN, GREEN),
                (390, 35, 76, 40, "Grounded\nanswer", LIGHT_RED, RED),
            ],
        ]
        super().__init__(width, 250, rows)

    def draw(self) -> None:
        super().draw()
        canvas = self.canv
        canvas.setStrokeColor(MUTED)
        canvas.setFillColor(MUTED)
        arrows = [
            (82, 217, 100, 217), (202, 217, 220, 217), (316, 217, 334, 217),
            (400, 200, 400, 165), (400, 165, 59, 157), (400, 165, 169, 157),
            (400, 165, 279, 157), (400, 165, 401, 157),
            (59, 115, 135, 75), (169, 115, 135, 75), (279, 115, 297, 75),
            (135, 35, 230, 55), (365, 55, 390, 55),
        ]
        for x1, y1, x2, y2 in arrows:
            canvas.line(x1, y1, x2, y2)
            angle = 1 if x2 >= x1 else -1
            canvas.line(x2, y2, x2 - 4 * angle, y2 + 2)
            canvas.line(x2, y2, x2 - 4 * angle, y2 - 2)


class GraphRouterFlow(BoxFlow):
    def __init__(self, width: float) -> None:
        rows = [
            [(170, 185, 140, 34, "Resolved query", LIGHT_GREEN, GREEN)],
            [(170, 130, 140, 34, "Deterministic entity linker", CYAN, BLUE)],
            [
                (5, 55, 130, 46, "0 linked entities\nlexical graph fallback", LIGHT_ORANGE, ORANGE),
                (175, 55, 130, 46, "1 linked entity\nneighbourhood retrieval", CYAN, BLUE),
                (345, 55, 130, 46, "2+ linked entities\npath + evidence subgraph", CYAN, BLUE),
            ],
            [(170, 0, 140, 30, "Governance-checked chunks", LIGHT_RED, RED)],
        ]
        super().__init__(width, 225, rows)

    def draw(self) -> None:
        super().draw()
        canvas = self.canv
        canvas.setStrokeColor(MUTED)
        canvas.line(240, 185, 240, 164)
        canvas.line(240, 130, 240, 116)
        canvas.line(240, 116, 70, 101)
        canvas.line(240, 116, 240, 101)
        canvas.line(240, 116, 410, 101)
        canvas.line(70, 55, 240, 30)
        canvas.line(240, 55, 240, 30)
        canvas.line(410, 55, 240, 30)


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName=FONT, fontSize=23,
            leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName=FONT, fontSize=11,
            leading=15, textColor=MUTED, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName=FONT, fontSize=16,
            leading=19, textColor=NAVY, spaceBefore=8, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName=FONT, fontSize=11.5,
            leading=14, textColor=BLUE, spaceBefore=8, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName=FONT, fontSize=9.2,
            leading=13, textColor=INK, alignment=TA_LEFT, spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName=FONT, fontSize=7.7,
            leading=10, textColor=INK,
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["BodyText"], fontName=FONT, fontSize=7.7,
            leading=10, textColor=MUTED, alignment=TA_CENTER, spaceAfter=8,
        ),
        "note": ParagraphStyle(
            "Note", parent=base["BodyText"], fontName=FONT, fontSize=8.5,
            leading=12, textColor=RED, borderColor=RED, borderWidth=0.8,
            borderPadding=7, backColor=colors.HexColor("#FFF4F4"), spaceAfter=8,
        ),
        "formula": ParagraphStyle(
            "Formula", parent=base["BodyText"], fontName="Courier", fontSize=8,
            leading=12, textColor=NAVY, leftIndent=12, rightIndent=12,
            borderColor=GRID, borderWidth=0.5, borderPadding=6,
            backColor=colors.HexColor("#F7F9FB"), spaceBefore=4, spaceAfter=7,
        ),
        "toc": ParagraphStyle(
            "TOC", parent=base["BodyText"], fontName=FONT, fontSize=9.5,
            leading=15, textColor=INK, leftIndent=12,
        ),
    }


STYLES = build_styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def table(data: list[list], widths: list[float], repeat_rows: int = 1) -> LongTable:
    result = LongTable(data, colWidths=widths, repeatRows=repeat_rows, hAlign="LEFT")
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), FONT),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("FONTSIZE", (0, 1), (-1, -1), 7.2),
                ("LEADING", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return result


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(GRID)
        canvas.line(18 * mm, A4[1] - 16 * mm, A4[0] - 18 * mm, A4[1] - 16 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont(FONT, 7.2)
        canvas.drawString(18 * mm, A4[1] - 12 * mm, "Evidence-Aware Agentic GraphRAG - Review Draft")
        canvas.drawRightString(A4[0] - 18 * mm, 11 * mm, f"Page {page}")
    canvas.restoreState()


def section_title(number: str, title: str) -> list:
    return [p(f"{number}  {title}", "h1"), HRFlowable(width="100%", thickness=0.8, color=BLUE), Spacer(1, 4)]


def build_story() -> list:
    story: list = []
    story.extend(
        [
            Spacer(1, 27 * mm),
            p("Evidence-Aware Agentic GraphRAG", "title"),
            p("for Bilingual University Administrative Question Answering", "subtitle"),
            Spacer(1, 14 * mm),
            HRFlowable(width="78%", thickness=1.2, color=BLUE),
            Spacer(1, 10 * mm),
            p("Manuscript Review Draft", "h1"),
            p("Target format: AICON 2026 / Springer LNICST full paper", "subtitle"),
            Spacer(1, 17 * mm),
            p(
                "This review PDF reflects the implemented architecture as of 22 August 2026. "
                "Final benchmark values are intentionally marked as not yet measured. Development smoke-test "
                "numbers are isolated and must not be used as submission claims.",
                "note",
            ),
            Spacer(1, 10 * mm),
            p("Authors: to be confirmed", "subtitle"),
            p("Affiliation: Can Tho University, Vietnam", "subtitle"),
            Spacer(1, 30 * mm),
            p("Review focus", "h2"),
            p(
                "Architecture correctness; graph-retrieval novelty; ambiguity handling; evidence governance; "
                "experimental validity; and replacement of all pending-result statements before submission.",
                "body",
            ),
            PageBreak(),
        ]
    )

    story.extend(section_title("Abstract", ""))
    story.append(
        p(
            "University administrative question answering requires more than semantic similarity: answers must "
            "respect document validity, organizational authority, temporal scope, and exact procedural or "
            "numerical rules. We present <b>Evidence-Aware Agentic GraphRAG</b>, a bilingual Vietnamese-English "
            "framework combining filtered BM25 and dense retrieval, entity-centric and bounded path retrieval, "
            "provenance-preserving graph expansion, deterministic evidence reranking, and specialist agents with "
            "typed tools and bounded memory. PostgreSQL is the authoritative store; Qdrant and Neo4j are "
            "rebuildable projections. An ambiguity gate asks for clarification before retrieval when the request "
            "lacks a concrete domain object or scope. Every candidate is revalidated against approval, publication, "
            "category, audience, version, and effective-date constraints. The final study will evaluate five "
            "cumulative variants and a reproduced CatRAG-style predecessor baseline on a human-verified bilingual "
            "benchmark. Final sample "
            "size, effect estimates, citation correctness, and latency remain not yet measured.",
            "body",
        )
    )
    story.append(p("Keywords: retrieval-augmented generation; GraphRAG; agentic AI; evidence provenance; bilingual QA", "small"))
    story.append(Spacer(1, 12))
    story.append(p("Contents", "h2"))
    for line in (
        "1 Introduction", "2 Related Work", "3 Problem Formulation", "4 System Architecture",
        "5 Retrieval and Agent Method", "6 Experimental Setup", "7 Results Plan",
        "8 Discussion and Responsible Use", "9 Conclusion", "References", "Appendix: Review Checklist",
    ):
        story.append(p(line, "toc"))
    story.append(PageBreak())

    story.extend(section_title("1", "Introduction"))
    story.append(p(
        "University policies and procedures are distributed across regulations, notices, forms, organizational "
        "websites, and document versions. Vietnamese student questions frequently mix abbreviations, policy "
        "terminology, course codes, cohort references, and English paraphrases. A plausible but obsolete or "
        "weakly sourced answer may cause academic or financial harm.",
    ))
    story.append(p(
        "Dense retrieval supports semantic matching but may miss identifiers. BM25 captures exact policy terms "
        "but is weaker for paraphrases. Knowledge graphs expose organizational, provenance, and validated-fact "
        "relations, while agent workflows can select deterministic tools and retry when evidence is incomplete. "
        "These additions also create routing, latency, noise-amplification, and reproducibility risks.",
    ))
    story.append(p("Research gap", "h2"))
    story.append(p(
        "Existing RAG systems often optimize relevance without jointly enforcing authority, temporal validity, "
        "evidence coverage, and deterministic computation. GraphRAG evaluation may also conflate lexical seed "
        "quality with genuine graph-traversal gain. Evidence from multiple stores is frequently collapsed without "
        "preserving source-specific provenance.",
    ))
    story.append(p(
        "The closest institutional predecessor is REBot/CatRAG [7], which combines dense retrieval with a graph "
        "partitioned by predicted regulation category. This paper treats that design as a direct baseline and "
        "tests the added value of BM25, version governance, reviewed facts, entity/path retrieval, citations, and "
        "specialist-agent control under one frozen evaluation protocol.",
    ))
    story.append(p("Research questions", "h2"))
    rq_data = [[p("RQ", "small"), p("Question", "small")]] + [
        ["RQ1", p("Does BM25-dense fusion outperform either retriever alone for Vietnamese and English questions?", "small")],
        ["RQ2", p("When does entity/path graph retrieval improve recall and multi-hop performance?", "small")],
        ["RQ3", p("Do reranking and evidence-quality scoring improve top-ranked support and citations?", "small")],
        ["RQ4", p("Does specialist routing with clarification and coverage-aware retry improve reliability?", "small")],
        ["RQ5", p("What latency and token-cost overhead does each cumulative component introduce?", "small")],
    ]
    story.append(table(rq_data, [28 * mm, 135 * mm]))
    story.append(PageBreak())

    story.extend(section_title("2", "Related Work"))
    for heading, text in (
        ("Retrieval-augmented generation", "RAG conditions generation on retrieved evidence and supports access to non-parametric knowledge [1]. This study focuses on obsolete, incomplete, or weakly governed evidence rather than treating retrieval as an unrestricted context provider."),
        ("Lexical, dense, and hybrid retrieval", "BM25 remains a strong lexical baseline for identifiers and policy terminology [2]. BGE-M3 supports multilingual dense representations [4]. Reciprocal Rank Fusion combines rankings without assuming calibrated source-score scales [3]."),
        ("Knowledge graphs and GraphRAG", "GraphRAG uses explicit relations for connected evidence and multi-hop reasoning [5]. This work separates internal lexical seed quality from entity neighbourhood, bounded path, and evidence-subgraph contribution."),
        ("Agentic RAG and tool use", "Reasoning-and-acting systems interleave model decisions with external actions [6]. The proposed harness constrains this pattern with specialist allow-lists, typed tools, bounded memory, deterministic clarification, and auditable traces."),
    ):
        story.append(p(heading, "h2"))
        story.append(p(text))
    related = [
        ["System", "VI/EN", "BM25", "Dense", "Graph", "Governance", "Agents/tools", "Citation eval"],
        ["Dense RAG", "Yes", "No", "Yes", "No", "No", "No", "No"],
        ["REBot/CatRAG [7]", "No", "No", "Yes", "Yes", "No", "No", "No"],
        ["EA-GraphRAG", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes"],
    ]
    story.append(Spacer(1, 5))
    story.append(table(related, [28 * mm, 14 * mm, 14 * mm, 14 * mm, 14 * mm, 23 * mm, 24 * mm, 22 * mm]))
    story.append(p("Table 1. Capability comparison. Checks describe components, not empirical superiority.", "caption"))
    story.append(PageBreak())

    story.extend(section_title("3", "Problem Formulation"))
    story.append(p(
        "Let q = (x, language, C, A, t), where x is the question text, C is the category set, A is an optional "
        "audience constraint, and t is the answer date. The corpus contains versioned documents D, chunks E, "
        "organizations O, categories C, entities V, and reviewed facts F.",
    ))
    story.append(p("Governance predicate", "h2"))
    story.append(p(
        "G(e,q) = I<sub>approved</sub> I<sub>published</sub> I<sub>latest</sub> I<sub>valid</sub> "
        "I<sub>category</sub>(e,C) I<sub>audience</sub>(e,A) I<sub>effective</sub>(e,t)",
        "formula",
    ))
    story.append(p(
        "Only evidence with G(e,q) = 1 may reach answer generation. Claims must be supported by admissible "
        "chunks or by deterministic tool outputs whose evidence identifiers are validated against the current "
        "evidence window.",
    ))
    story.append(p("Clarification contract", "h2"))
    story.append(p(
        "If a standalone request names only a broad domain, such as 'tuition' or 'course', and bounded context "
        "does not supply a concrete program, cohort, course, procedure, audience, or required output, the system "
        "returns a domain-specific clarification question. This branch performs no retrieval and emits no citation.",
    ))
    clarification = [
        ["Input", "Required clarification"],
        ["Tuition", "Program/major, cohort, training mode, per-credit or total fee"],
        ["Course", "Course code or course name"],
        ["Program", "Program/major and applicable cohort"],
        ["Procedure/regulation", "Concrete procedure, audience, or responsible unit"],
    ]
    story.append(table(clarification, [45 * mm, 118 * mm]))
    story.append(PageBreak())

    story.extend(section_title("4", "System Architecture"))
    story.append(ArchitectureFlow(470))
    story.append(p("Figure 1. End-to-end governed agentic retrieval architecture.", "caption"))
    story.append(p("Data authority boundary", "h2"))
    story.append(p(
        "The framework preserves CatRAG's separation between routing and hybrid retrieval while replacing a "
        "category-only graph decision with governed triple retrieval. Each projected candidate is revalidated "
        "against PostgreSQL before an agent or tool can consume it.",
    ))
    stores = [
        ["Layer", "Technology", "Role", "Authority"],
        ["Source objects", "Cloudflare R2", "Original/canonical objects and attachments", "Preservation"],
        ["Authoritative records", "PostgreSQL", "Versions, governance, chunks, facts, audit", "System of record"],
        ["Lexical/vector projection", "Qdrant", "BM25 sparse and BGE-M3 dense retrieval", "Rebuildable"],
        ["Graph projection", "Neo4j", "Structure and validated facts", "Rebuildable"],
        ["Language model", "OpenRouter/Qwen", "Routing, coverage, grounded generation", "Not policy authority"],
    ]
    story.append(table(stores, [33 * mm, 31 * mm, 75 * mm, 27 * mm]))
    story.append(p(
        "Every Qdrant or Neo4j candidate is hydrated from PostgreSQL and rechecked for approval, publication, "
        "latest-version status, category, audience, and effective dates.",
    ))
    story.append(PageBreak())

    story.extend(section_title("5", "Retrieval and Agent Method"))
    story.append(p("Triple retrieval", "h2"))
    story.append(p(
        "BM25, dense BGE-M3, and graph retrieval execute concurrently. Candidates are normalized, unioned, and "
        "deduplicated by chunk ID. Raw scores remain traceable but are not added because their scales differ.",
    ))
    story.append(p(
        "RRF(e) = sum over r in {BM25,dense,graph} of 1 / (60 + rank<sub>r</sub>(e))",
        "formula",
    ))
    story.append(p(
        "The deterministic second-stage score is 0.55 content recall + 0.25 heading recall + 0.10 exact-term "
        "coverage + 0.10 source consensus. Ties use source agreement, best source rank, heading overlap, document "
        "key, and chunk UUID.",
    ))
    story.append(p("Entity-aware graph router", "h2"))
    story.append(GraphRouterFlow(470))
    story.append(p("Figure 2. Query-aware graph routing with bounded lexical fallback.", "caption"))
    story.append(PageBreak())

    story.extend(section_title("5.1", "Entity Linking, Neighbourhoods, and Paths"))
    story.append(p(
        "The deterministic linker accent-folds and normalizes text, detects exact alphanumeric identifiers, and "
        "matches entity labels and aliases. Confidence is 1.00 for an exact identifier, 0.95 for a normalized label "
        "substring, and 0.85 for an alias. No entity is invented when these checks fail.",
    ))
    story.append(p("Entity-neighbourhood score", "h2"))
    story.append(p("S<sub>N</sub>(e) = c(v) c(f) w<sub>predicate</sub>", "formula"))
    story.append(p("Bounded path score", "h2"))
    story.append(p(
        "S<sub>P</sub>(p) = c(v<sub>s</sub>) c(v<sub>t</sub>) min(c(f) for f in p) "
        "w<sub>predicate</sub> w<sub>hop</sub>, where w<sub>hop</sub> is 0.95 for one fact and 0.75 for two facts.",
        "formula",
    ))
    graph_rows = [
        ["Method", "Trigger", "Returned evidence", "Reason trace"],
        ["Entity neighbourhood", "One linked entity", "Chunks supporting adjacent validated facts", "linked_entity_neighborhood"],
        ["One-fact path", "Two linked endpoints", "Chunk supporting their direct fact", "linked_entity_path_1_fact"],
        ["Two-fact subgraph", "Two endpoints plus intermediate entity", "Both supporting chunks", "linked_entity_path_2_facts"],
        ["Lexical fallback", "No linked graph evidence", "Only expanded nodes; seed excluded", "adjacent/shared relation"],
    ]
    story.append(table(graph_rows, [35 * mm, 35 * mm, 62 * mm, 35 * mm]))
    story.append(p(
        "Traversal is limited to validated facts and at most two fact edges. The runtime does not execute "
        "LLM-generated Cypher and does not perform unbounded variable-length traversal.",
        "note",
    ))
    story.append(p("Construction and query algorithms", "h2"))
    construction = [
        ["Step", "Governed construction procedure"],
        ["1", "Store source object and create a versioned PostgreSQL record"],
        ["2", "Chunk and attach category, organization, audience, and effective dates"],
        ["3", "Build BM25 sparse and BGE-M3 dense Qdrant projections"],
        ["4", "Extract entity/fact candidates with source-chunk provenance"],
        ["5", "Project only human-validated facts to Neo4j and reconcile superseded nodes"],
    ]
    story.append(table(construction, [15 * mm, 152 * mm]))
    query_steps = [
        ["Step", "Evidence-aware agent query procedure"],
        ["1", "Resolve bounded context; clarify if the request remains ambiguous"],
        ["2", "Select a specialist lane and enforce its tool allow-list"],
        ["3", "Run BM25, dense, and query-aware graph retrieval concurrently"],
        ["4", "Govern, deduplicate, fuse, rerank, and quality-score evidence"],
        ["5", "Retry on insufficient coverage or abstain; validate tool evidence and citations"],
    ]
    story.append(table(query_steps, [15 * mm, 152 * mm]))
    story.append(p(
        "For N chunks of dimension d, vector storage is O(Nd) and graph storage is O(|V|+|E|). "
        "Query latency is governed by the slowest concurrent retrieval lane plus O(K log K) fusion/reranking "
        "for bounded K. Graph paths contain at most two reviewed fact edges.",
    ))
    story.append(PageBreak())

    story.extend(section_title("5.2", "Agents, Memory, Tools, and Evidence Control"))
    agent_rows = [
        ["Agent", "Primary scope", "Examples of allowed tools"],
        ["Academic Affairs and Regulations", "Rules, applicability, dates, exceptions", "Triple/graph retrieval; policy comparison"],
        ["Training Programs", "Programs, curricula, cohorts, responsible units", "Triple retrieval; procedure context"],
        ["Courses and Subjects", "Codes, prerequisites, assessment rules", "Course-grade and GPA tools"],
        ["Guides and Procedures", "Steps, offices, forms, deadlines, fees", "Tuition; procedure context; official web"],
    ]
    story.append(table(agent_rows, [43 * mm, 65 * mm, 60 * mm]))
    story.append(p("Workflow", "h2"))
    story.append(p(
        "resolve context -> clarify or classify -> select agent -> load namespaced memory -> retrieve -> assess "
        "quality and coverage -> invoke allow-listed tools -> bounded retry -> generate -> validate citations",
        "formula",
    ))
    story.append(p(
        "Conversation context is bounded to recent messages and characters. Lane working memory is namespaced by "
        "thread and agent. Each run stores immutable workflow and tool traces. Calculation tools require at least "
        "one evidence ID and reject IDs outside the current evidence window.",
    ))
    story.append(p("Evidence quality", "h2"))
    story.append(p(
        "Q(e) = 0.35 relevance + 0.20 authority + 0.15 freshness + 0.20 provenance + 0.10 consistency",
        "formula",
    ))
    story.append(p("Coverage(q) = |required facts intersect supported facts| / |required facts|", "formula"))
    story.append(PageBreak())

    story.extend(section_title("6", "Experimental Setup"))
    story.append(p(
        "The final benchmark must contain human-verified Vietnamese and English questions linked to source "
        "documents, required facts, categories, temporal scope, expected lane, and expected tools. Draft questions "
        "remain development data and are excluded from paper claims.",
    ))
    variants = [
        ["Variant", "Components", "Purpose"],
        ["P0", "CatRAG-style dense + category graph", "Direct predecessor baseline"],
        ["M0", "Filtered BM25 + dense BGE-M3 + RRF", "Strong non-graph baseline"],
        ["M1", "M0 + entity/path Neo4j retrieval", "Graph contribution"],
        ["M2", "M1 + orchestrator and specialist agents", "Routing/workflow"],
        ["M3", "M2 + evidence-quality and coverage assessment", "Evidence awareness"],
        ["M4", "M3 + coverage-aware retry and triple retrieval", "Full system"],
    ]
    story.append(table(variants, [20 * mm, 95 * mm, 52 * mm]))
    story.append(p("Required ablations", "h2"))
    ablations = [
        ["Ablation", "Question answered"],
        ["BM25 only / dense only / hybrid", "Does fusion beat strong individual retrievers?"],
        ["No graph", "Does graph add relevant evidence?"],
        ["Entity only / path only / lexical graph fallback", "Which graph mechanism contributes?"],
        ["No reranker / no tie-break", "Does second-stage ranking help?"],
        ["No quality score / no coverage retry", "Does evidence-aware control help?"],
        ["No ambiguity gate", "Does clarification prevent misrouted retrieval and unsupported answers?"],
    ]
    story.append(table(ablations, [55 * mm, 112 * mm]))
    story.append(PageBreak())

    story.extend(section_title("6.1", "Metrics and Reproducibility"))
    metrics = [
        ["Layer", "Metrics"],
        ["Retrieval", "Hits@k, Recall@k, MRR, nDCG@k"],
        ["Graph", "Entity-link accuracy, seed precision, path precision, entity-path hit rate, noise amplification"],
        ["Agent", "Routing/category accuracy, clarification precision/recall, coverage, answer token F1"],
        ["Citations", "Citation precision/recall, unsupported-claim rate, abstention correctness"],
        ["Tools", "Tool precision/recall, unauthorized-tool rate, formula/input correctness"],
        ["Efficiency", "Median and p95 latency, LLM calls, tokens, external-service failures"],
    ]
    story.append(table(metrics, [35 * mm, 132 * mm]))
    story.append(p("Reproducibility record", "h2"))
    story.append(p(
        "Freeze model identifiers, prompts, embedding dimension, index configuration, candidate budgets, RRF "
        "depth, reranker weights, graph path weights, random seeds, hardware, and software versions. Preserve "
        "per-query source ranks, raw scores, graph reasons, linked entities, graph paths, trace IDs, failures, and "
        "ablation identifiers. Gold categories and dates must not be injected into agent inputs.",
    ))
    dataset = [
        ["Final dataset item", "Value"],
        ["Approved documents", "Not yet frozen"],
        ["Chunks", "Not yet frozen"],
        ["Validated graph facts", "Pending human validation"],
        ["Vietnamese questions", "Not yet frozen"],
        ["English questions", "Not yet frozen"],
        ["Multi-hop questions", "Not yet frozen"],
    ]
    story.append(table(dataset, [80 * mm, 87 * mm]))
    story.append(PageBreak())

    story.extend(section_title("7", "Results Plan"))
    results = [
        ["System", "Hits@1", "Recall@3", "MRR", "Answer F1", "Citation P", "Coverage", "Latency"],
        ["BM25 only", "-", "-", "-", "-", "-", "-", "-"],
        ["Dense only", "-", "-", "-", "-", "-", "-", "-"],
        ["CatRAG-style", "-", "-", "-", "-", "-", "-", "-"],
        ["M0 Hybrid", "-", "-", "-", "-", "-", "-", "-"],
        ["M1 GraphRAG", "-", "-", "-", "-", "-", "-", "-"],
        ["M2 Agents", "-", "-", "-", "-", "-", "-", "-"],
        ["M3 Evidence-aware", "-", "-", "-", "-", "-", "-", "-"],
        ["M4 Full", "-", "-", "-", "-", "-", "-", "-"],
    ]
    story.append(table(results, [25 * mm, 18 * mm, 21 * mm, 16 * mm, 22 * mm, 22 * mm, 20 * mm, 20 * mm]))
    story.append(p("Table 6. Main verified-test results. Dashes indicate measurements not yet produced.", "caption"))
    story.append(p("Development-only diagnostic", "h2"))
    story.append(p(
        "A seven-question draft smoke test over 23 documents and 350 chunks obtained document Recall@3 = 1.0 "
        "for BM25, dense, and hybrid retrieval. Hits@1 was 0.714 for BM25, 0.714 for dense, and 0.571 for "
        "equal-weight hybrid RRF. The sample is draft, small, and not submission-grade. It warns that equal-weight "
        "fusion is not automatically superior.",
        "note",
    ))
    story.append(p("Result-writing discipline", "h2"))
    story.append(p(
        "For every method introduced, report a corresponding result. Separate retrieval effectiveness, graph "
        "contribution, evidence/citation quality, agent/tool behavior, clarification behavior, and reliability-cost "
        "trade-offs. Avoid interpreting results inside the Results section; reserve mechanisms and implications for "
        "Discussion.",
    ))
    story.append(PageBreak())

    story.extend(section_title("8", "Discussion, Limitations, and Responsible Use"))
    story.append(p(
        "The discussion must distinguish graph traversal gain from lexical seed quality and identify cases where "
        "BM25 remains preferable. Error analysis should cover ambiguous scope, wrong entity links, missing validated "
        "facts, obsolete versions, noisy graph paths, incomplete procedures, wrong calculation inputs, and unsupported "
        "citations.",
    ))
    limitations = [
        ["Threat", "Current mitigation", "Remaining limitation"],
        ["Ambiguous questions", "Deterministic clarification gate", "Heuristic ambiguity coverage must be measured"],
        ["Graph hallucination", "Only validated facts are projected", "Human review cost and incomplete graph"],
        ["Temporal error", "PostgreSQL as-of revalidation", "Missing metadata may cause abstention"],
        ["Citation error", "Known-ID and lexical support guard", "Not full claim-level entailment"],
        ["Web drift", "URL, fetch time, publication time, hash", "Live pages may change or disappear"],
        ["Generalizability", "Bilingual/category reporting", "Single-institution study"],
    ]
    story.append(table(limitations, [38 * mm, 63 * mm, 66 * mm]))
    story.append(p("Responsible deployment", "h2"))
    story.append(p(
        "The assistant is decision support, not a policy authority. High-impact answers should expose source, "
        "effective date, responsible unit, and uncertainty. No student-specific profile should be retained without "
        "explicit consent, retention limits, and institutional approval.",
    ))
    story.append(PageBreak())

    story.extend(section_title("9", "Conclusion"))
    story.append(p(
        "This manuscript defines Evidence-Aware Agentic GraphRAG, a governed bilingual framework combining lexical, "
        "dense, entity-centric, and bounded path retrieval with provenance-aware evidence assessment, typed tools, "
        "bounded memory, clarification, and specialist-agent workflows. The implementation separates authoritative "
        "records from rebuildable projections and excludes lexical seeds from measured graph evidence. Final claims "
        "extend category-guided CatRAG with version governance, BM25, query-aware graph retrieval, citation control, "
        "and typed agent tools. Comparative claims remain contingent on a frozen human-verified benchmark. Future "
        "work should evaluate entity-first retrieval "
        "across institutions and strengthen claim-level citation entailment.",
    ))
    story.append(p("Claims that must remain conditional", "h2"))
    story.append(p(
        "Do not claim that graph retrieval, hybrid fusion, agent routing, or coverage-aware retry improves quality "
        "until verified ablations support the claim. Negative or mixed results remain publishable when the paper "
        "explains when added graph or agent complexity is not beneficial.",
        "note",
    ))
    story.append(PageBreak())

    story.extend(section_title("References", ""))
    references = (
        "[1] Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS (2020).",
        "[2] Robertson, S., Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond. FnTIR (2009).",
        "[3] Cormack, G.V., Clarke, C.L.A., Buettcher, S. Reciprocal Rank Fusion. SIGIR (2009).",
        "[4] Chen, J. et al. BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity. arXiv:2402.03216 (2024).",
        "[5] Edge, D. et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130 (2024).",
        "[6] Yao, S. et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR (2023).",
        "[7] Ma, T. et al. REBot: From RAG to CatRAG with Semantic Enrichment and Graph Routing. arXiv:2510.01800 (2025).",
    )
    for reference in references:
        story.append(p(reference, "small"))
        story.append(Spacer(1, 4))
    story.append(p(
        "The final manuscript must expand and verify the related-work bibliography using primary papers and "
        "official technical documentation.",
        "note",
    ))
    story.append(PageBreak())

    story.extend(section_title("Appendix", "Review Checklist"))
    checklist = [
        ["Status", "Item"],
        ["Done", "Architecture distinguishes PostgreSQL authority from Qdrant/Neo4j projections"],
        ["Done", "BM25, dense, graph, RRF, reranker, quality, and coverage formulas included"],
        ["Done", "Entity linking, neighbourhood, bounded path/subgraph, and lexical fallback specified"],
        ["Done", "Ambiguous requests ask for clarification without retrieval"],
        ["Pending", "Synchronize PostgreSQL runtime credential and rebuild Neo4j"],
        ["Pending", "Human-validate graph facts and project Entity/Fact paths"],
        ["Pending", "Freeze verified bilingual retrieval and agent benchmarks"],
        ["Pending", "Run M0-M4, graph-component, ambiguity, citation, and tool ablations"],
        ["Pending", "Replace result dashes and conditional abstract/conclusion language"],
        ["Pending", "Install official Springer LNICST template and perform final page-limit check"],
    ]
    story.append(table(checklist, [24 * mm, 143 * mm]))
    story.append(Spacer(1, 10))
    story.append(p(
        "Reviewer notes: mark architectural corrections directly against this draft, then update the LaTeX source "
        "under Paper/latex before producing the submission-formatted PDF.",
        "body",
    ))
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=17 * mm,
        title="Evidence-Aware Agentic GraphRAG - Review Draft",
        author="Can Tho University",
        subject="Manuscript review draft",
    )
    document.build(build_story(), onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
