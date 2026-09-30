from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
)

from build_review_pdf import (
    ArchitectureFlow,
    FONT,
    GraphRouterFlow,
    GRID,
    INK,
    MUTED,
    NAVY,
    STYLES,
    build_story,
)


PAPER_DIR = Path(__file__).resolve().parents[1]
OUTPUT = PAPER_DIR / "output" / "pdf" / "evidence-aware-agentic-graphrag-paper-preview.pdf"

# Springer computer-science proceedings use a compact, single-column trim size.
PAGE_SIZE = portrait((155 * mm, 235 * mm))
TEXT_WIDTH = 122 * mm


class ScaledFlowable(Flowable):
    def __init__(self, child: Flowable, scale: float) -> None:
        super().__init__()
        self.child = child
        self.scale = scale
        self.width = child.width * scale
        self.height = child.height * scale

    def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
        return self.width, self.height

    def draw(self) -> None:
        self.canv.saveState()
        self.canv.scale(self.scale, self.scale)
        self.child.canv = self.canv
        self.child.draw()
        self.canv.restoreState()


def configure_styles() -> None:
    STYLES["h1"].fontSize = 11.2
    STYLES["h1"].leading = 13.2
    STYLES["h1"].spaceBefore = 8
    STYLES["h1"].spaceAfter = 3
    STYLES["h2"].fontSize = 9.4
    STYLES["h2"].leading = 11
    STYLES["h2"].spaceBefore = 6
    STYLES["h2"].spaceAfter = 2
    STYLES["body"].fontSize = 9
    STYLES["body"].leading = 11.2
    STYLES["body"].alignment = TA_JUSTIFY
    STYLES["body"].spaceAfter = 4
    STYLES["small"].fontSize = 7.5
    STYLES["small"].leading = 9
    STYLES["caption"].fontSize = 7.4
    STYLES["caption"].leading = 9
    STYLES["note"].fontSize = 8
    STYLES["note"].leading = 10
    STYLES["formula"].fontSize = 7.7
    STYLES["formula"].leading = 10


TITLE = ParagraphStyle(
    "ProceedingsTitle",
    fontName=FONT,
    fontSize=16,
    leading=19,
    alignment=TA_CENTER,
    textColor=colors.black,
    spaceAfter=8,
)
AUTHOR = ParagraphStyle(
    "ProceedingsAuthor",
    fontName=FONT,
    fontSize=9.2,
    leading=11,
    alignment=TA_CENTER,
    textColor=INK,
    spaceAfter=3,
)
ABSTRACT = ParagraphStyle(
    "ProceedingsAbstract",
    fontName=FONT,
    fontSize=8.5,
    leading=10.5,
    alignment=TA_JUSTIFY,
    leftIndent=8 * mm,
    rightIndent=8 * mm,
    spaceAfter=5,
)


def scale_table(item: Table) -> Table:
    widths = list(item._argW)
    total = sum(float(width or 0) for width in widths)
    if total <= TEXT_WIDTH:
        return item
    factor = TEXT_WIDTH / total
    scaled = [float(width or 0) * factor for width in widths]
    item._argW = scaled
    item._colWidths = scaled
    return item


def manuscript_body() -> list:
    source = build_story()
    page_breaks = [i for i, item in enumerate(source) if isinstance(item, PageBreak)]
    # Drop the review cover/contents and the review-only appendix.
    body = source[page_breaks[1] + 1 : page_breaks[-1]]
    output: list = []
    for item in body:
        if isinstance(item, PageBreak):
            continue
        if isinstance(item, (ArchitectureFlow, GraphRouterFlow)):
            output.append(ScaledFlowable(item, TEXT_WIDTH / item.width))
        elif isinstance(item, (Table, LongTable)):
            output.append(scale_table(item))
        else:
            output.append(item)
    return output


def paper_story() -> list:
    abstract = (
        "<b>Abstract.</b> University administrative question answering requires more than semantic similarity: "
        "answers must respect document validity, organizational authority, temporal scope, and exact procedural "
        "or numerical rules. We present <b>Evidence-Aware Agentic GraphRAG</b>, a bilingual Vietnamese-English "
        "framework combining governed BM25 and dense retrieval, entity-centric and bounded-path graph retrieval, "
        "deterministic evidence reranking, and specialist agents with typed tools and bounded memory. PostgreSQL "
        "is the authority while Qdrant and Neo4j are rebuildable projections. An ambiguity gate asks for "
        "clarification before retrieval when scope is insufficient. A reproduced REBot/CatRAG-style system is the "
        "direct predecessor baseline. Final claims remain conditional on a frozen, "
        "human-verified bilingual benchmark."
    )
    story: list = [
        Spacer(1, 4 * mm),
        Paragraph(
            "Evidence-Aware Agentic GraphRAG for Bilingual University Administrative Question Answering",
            TITLE,
        ),
        Paragraph("Anonymous Authors", AUTHOR),
        Paragraph("Anonymous Institution", AUTHOR),
        Spacer(1, 4 * mm),
        Paragraph(abstract, ABSTRACT),
        Paragraph(
            "<b>Keywords:</b> retrieval-augmented generation, GraphRAG, agentic AI, evidence provenance, bilingual question answering",
            ABSTRACT,
        ),
        Spacer(1, 2 * mm),
    ]
    story.extend(manuscript_body())
    return story


def header_footer(canvas, document) -> None:
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(GRID)
        canvas.line(16.5 * mm, PAGE_SIZE[1] - 13 * mm, PAGE_SIZE[0] - 16.5 * mm, PAGE_SIZE[1] - 13 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont(FONT, 6.8)
        canvas.drawString(16.5 * mm, PAGE_SIZE[1] - 10 * mm, "Evidence-Aware Agentic GraphRAG")
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT, 7)
    canvas.drawCentredString(PAGE_SIZE[0] / 2, 9 * mm, str(page))
    canvas.restoreState()


def main() -> None:
    configure_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=PAGE_SIZE,
        leftMargin=16.5 * mm,
        rightMargin=16.5 * mm,
        topMargin=17 * mm,
        bottomMargin=15 * mm,
        title="Evidence-Aware Agentic GraphRAG",
        author="Anonymous Authors",
        subject="AICON 2026 Springer LNICST submission-format preview",
    )
    document.build(paper_story(), onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
