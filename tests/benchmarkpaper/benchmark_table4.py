"""Run the E1--E5 retrieval ablation used by Table 4.

The benchmark reads ``tests/data/dataset.xlsx`` and reports document-level
P@5, Recall@5, and MRR.  It uses the same query set for every variant:

    E1 BM25
    E2 Dense
    E3 BM25 + Dense + RRF
    E4 BM25 + Dense + RRF + Graph
    E5 BM25 + Dense + RRF + Graph + Agent

Only rows with a local Markdown gold source are evaluated.  The ``Retrieval``
rows in the workbook use source/version IDs from another deployment and are
reported as skipped unless a local source mapping is added.

Examples::

    python tests/benchmarkpaper/benchmark_table4.py --dry-run
    python tests/benchmarkpaper/benchmark_table4.py

Services required for a real run: PostgreSQL, Qdrant, and Neo4j.  Results are
written to ``tests/outputpaper/table4_results.json`` and the chart to
``tests/outputpaper/table4_results.svg``.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "tests" / "data" / "dataset.xlsx"
DEFAULT_OUTPUT = PROJECT_ROOT / "tests" / "outputpaper" / "table4_results.json"
DEFAULT_CHART = PROJECT_ROOT / "tests" / "outputpaper" / "table4_results.svg"
GRAPH_DATA_DIR = PROJECT_ROOT / "data" / "markdown_graph"
TOP_K = 5
RRF_K = 60

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True)
class Case:
    case_id: str
    group: str
    question: str
    gold_sources: tuple[str, ...]


def _column_number(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref.upper())
    if not letters:
        return 0
    value = 0
    for char in letters.group(0):
        value = value * 26 + ord(char) - ord("A") + 1
    return value - 1


def _shared_strings(book: ZipFile) -> list[str]:
    try:
        root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    values = []
    for item in root.findall(f"{{{NS_MAIN}}}si"):
        values.append("".join(item.itertext()))
    return values


def _sheet_path(book: ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    relation_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{NS_PKG_REL}}}Relationship")
    }
    for sheet in workbook.findall(f"{{{NS_MAIN}}}sheets/{{{NS_MAIN}}}sheet"):
        if sheet.attrib.get("name") != sheet_name:
            continue
        rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
        target = relation_targets[rel_id].lstrip("/")
        return target if target.startswith("xl/") else f"xl/{target}"
    raise KeyError(f"worksheet not found: {sheet_name}")


def read_xlsx_rows(path: Path, sheet_name: str = "Master Dataset") -> list[dict[str, Any]]:
    """Read one XLSX sheet with stdlib only; avoids a benchmark dependency."""
    with ZipFile(path) as book:
        strings = _shared_strings(book)
        root = ET.fromstring(book.read(_sheet_path(book, sheet_name)))
        raw_rows: list[list[Any]] = []
        for row in root.findall(f".//{{{NS_MAIN}}}row"):
            cells: list[Any] = []
            for cell in row.findall(f"{{{NS_MAIN}}}c"):
                index = _column_number(cell.attrib.get("r", ""))
                while len(cells) <= index:
                    cells.append(None)
                kind = cell.attrib.get("t")
                value_node = cell.find(f"{{{NS_MAIN}}}v")
                inline_node = cell.find(f"{{{NS_MAIN}}}is")
                if kind == "inlineStr" and inline_node is not None:
                    value: Any = "".join(inline_node.itertext())
                elif value_node is None:
                    value = None
                else:
                    raw = value_node.text or ""
                    if kind == "s":
                        value = strings[int(raw)]
                    elif kind == "b":
                        value = raw == "1"
                    else:
                        try:
                            value = int(raw) if raw.isdigit() else float(raw)
                        except ValueError:
                            value = raw
                cells[index] = value
            raw_rows.append(cells)

    if not raw_rows:
        return []
    headers = [str(value).strip() if value is not None else "" for value in raw_rows[0]]
    return [
        {header: row[index] if index < len(row) else None for index, header in enumerate(headers) if header}
        for row in raw_rows[1:]
    ]


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _parse_source_list(value: Any) -> list[str]:
    raw = _text(value)
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, list):
            return [_text(item) for item in parsed if _text(item)]
    return [item.strip().strip("\"'") for item in re.split(r"[,;]", raw) if item.strip()]


def _gold_sources(row: dict[str, Any], group: str) -> list[str]:
    if group == "RAGAS":
        source = _text(row.get("Source"))
        match = re.search(r"\(([^()]+\.md)\)\s*$", source)
        if match:
            return [match.group(1)]
        return [source] if source.casefold().endswith(".md") else []
    if group == "E2E":
        return _parse_source_list(row.get("expected_sources"))
    return []


def load_cases(path: Path, groups: Sequence[str], limit: int | None = None) -> tuple[list[Case], dict[str, int]]:
    rows = read_xlsx_rows(path)
    selected: list[Case] = []
    skipped = Counter()
    for row in rows:
        group = _text(row.get("Dataset Group"))
        if group not in groups:
            continue
        question = _text(row.get("Master Question")) or _text(row.get("Question"))
        gold = tuple(dict.fromkeys(_gold_sources(row, group)))
        if not question:
            skipped["missing_question"] += 1
            continue
        if not gold:
            skipped["unmapped_gold_source"] += 1
            continue
        selected.append(
            Case(
                case_id=_text(row.get("Master ID")) or _text(row.get("Original ID")),
                group=group,
                question=question,
                gold_sources=gold,
            )
        )
        if limit is not None and len(selected) >= limit:
            break
    return selected, dict(skipped)


def _source_from_document(document: Any) -> str:
    metadata = getattr(document, "metadata", {}) or {}
    return _text(metadata.get("source") or metadata.get("document_key"))


def _unique_sources(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _rrf(lanes: Sequence[Sequence[str]], limit: int = TOP_K) -> list[str]:
    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    for lane in lanes:
        for rank, source in enumerate(_unique_sources(lane)):
            scores[source] = scores.get(source, 0.0) + 1.0 / (RRF_K + rank + 1)
            first_seen.setdefault(source, rank)
    ranked = sorted(scores, key=lambda source: (-scores[source], first_seen[source], source))
    return ranked[:limit]


def _metrics(retrieved: Sequence[str], gold: Sequence[str]) -> dict[str, float | int | None]:
    top = _unique_sources(retrieved)[:TOP_K]
    gold_set = set(gold)
    hits = [index + 1 for index, source in enumerate(top) if source in gold_set]
    assert TOP_K == 5  # Table 4's fixed cutoff.
    return {
        "precision_at_5": len(hits) / TOP_K,
        "recall_at_5": len(hits) / len(gold_set),
        "mrr": 1.0 / hits[0] if hits else 0.0,
        "first_relevant_rank": hits[0] if hits else None,
        "retrieved": top,
    }


def _academic_route(question: str) -> bool:
    # ponytail: deterministic route gate; replace with supervisor traces when
    # measuring LLM routing itself.
    markers = (
        "ngành",
        "chương trình",
        "học phần",
        "môn",
        "plo",
        "peo",
        "tiên quyết",
        "chuẩn đầu ra",
        "vị trí việc làm",
        "tín chỉ",
    )
    folded = question.casefold()
    return any(marker in folded for marker in markers)


def _graph_sources(graph_service: Any, question: str, file_by_code: dict[str, str]) -> list[str]:
    if graph_service is None:
        return []
    results: list[dict[str, Any]] = []
    try:
        direct = graph_service.lookup_program(question)
        if direct and direct.get("program"):
            results.append(direct["program"])
    except Exception:
        pass
    try:
        results.extend(graph_service.search_programs(question) or [])
    except Exception:
        pass
    sources = []
    for result in results:
        code = _text(result.get("code"))
        if code in file_by_code:
            sources.append(file_by_code[code])
    return _unique_sources(sources)


def _graph_file_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in GRAPH_DATA_DIR.glob("*.md"):
        match = re.search(r"_(\d{7}C?)_", path.name)
        if match:
            mapping[match.group(1)] = path.name
    return mapping


def _retrieve_lanes(engine: Any, query: str) -> dict[str, list[str]]:
    dense_docs = engine.retrieve(
        query,
        top_n=TOP_K,
        hybrid_search=False,
        use_reranker=False,
        metadata_filter_enabled=False,
    )
    dense = _unique_sources(_source_from_document(doc) for doc in dense_docs)

    sparse: list[str] = []
    if engine.bm25_index is not None and engine.bm25_index.is_indexed():
        matches = engine.bm25_index.search(query=query, top_k=TOP_K)
        parents = engine.doc_store.mget([parent_id for parent_id, _ in matches])
        sparse = _unique_sources(_source_from_document(doc) for doc in parents if doc is not None)

    hybrid_docs = engine.retrieve(
        query,
        top_n=TOP_K,
        hybrid_search=True,
        use_reranker=False,
        metadata_filter_enabled=False,
    )
    hybrid = _unique_sources(_source_from_document(doc) for doc in hybrid_docs)
    return {"bm25": sparse, "dense": dense, "hybrid": hybrid}


def _variant_sources(lanes: dict[str, list[str]], graph: list[str], question: str) -> dict[str, tuple[list[str], str | None]]:
    e1 = lanes["bm25"]
    e2 = lanes["dense"]
    e3 = lanes["hybrid"] or _rrf((e1, e2))
    e4 = _rrf((e3, graph))
    if _academic_route(question):
        # Agent proxy: route relational questions graph-first; retain hybrid
        # fallback when graph linking returns no candidate.
        e5 = _rrf((graph, e3)) if graph else e3
        route = "academic_graph"
    else:
        e5 = e3
        route = "hybrid_only"
    return {
        "E1": (e1, None),
        "E2": (e2, None),
        "E3": (e3, None),
        "E4": (e4, None),
        "E5": (e5, route),
    }


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return sum(values) / len(values) if values else 0.0


def write_chart(summary: dict[str, dict[str, Any]], output_path: Path) -> None:
    """Write a dependency-free SVG chart for Table 4 metrics."""
    variants = ["E1", "E2", "E3", "E4", "E5"]
    metric_names = ("precision_at_5", "recall_at_5", "mrr")
    metric_labels = ("P@5", "Recall@5", "MRR")
    colors = ("#2563eb", "#16a34a", "#f59e0b")
    width, height = 1000, 600
    left, right, top, bottom = 90, 35, 55, 95
    plot_width, plot_height = width - left - right, height - top - bottom
    group_width = plot_width / len(variants)
    bar_width = min(34, group_width / 5)

    def y(value: float) -> float:
        return top + (1.0 - max(0.0, min(1.0, value))) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Table 4 E1-E5 retrieval comparison</title>',
        '<desc id="desc">Grouped bar chart for P at 5, Recall at 5, and MRR.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="90" y="30" font-family="Arial, sans-serif" font-size="22" font-weight="700">Table 4: E1-E5 Retrieval Comparison</text>',
    ]
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = y(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#d1d5db"/>')
        parts.append(f'<text x="{left-12}" y="{yy+5:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" fill="#374151">{tick:.2f}</text>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#111827"/>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#111827"/>')
    parts.append(f'<text x="22" y="{top + plot_height/2:.1f}" transform="rotate(-90 22 {top + plot_height/2:.1f})" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Score</text>')

    for index, variant in enumerate(variants):
        center = left + group_width * (index + 0.5)
        parts.append(f'<text x="{center:.1f}" y="{height-bottom+28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" font-weight="700">{variant}</text>')
        values = summary.get(variant, {})
        for metric_index, (metric, color) in enumerate(zip(metric_names, colors)):
            value = float(values.get(metric, 0.0) or 0.0)
            x = center + (metric_index - 1) * (bar_width + 5) - bar_width / 2
            yy = y(value)
            parts.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bar_width:.1f}" height="{height-bottom-yy:.1f}" fill="{color}" rx="2"/>')
            parts.append(f'<text x="{x + bar_width/2:.1f}" y="{max(top+15, yy-6):.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#111827">{value:.3f}</text>')

    legend_x = width - 270
    for index, (label, color) in enumerate(zip(metric_labels, colors)):
        x = legend_x + index * 82
        parts.append(f'<rect x="{x}" y="{top-22}" width="12" height="12" fill="{color}"/>')
        parts.append(f'<text x="{x+16}" y="{top-11}" font-family="Arial, sans-serif" font-size="12">{html.escape(label)}</text>')
    parts.append('<text x="90" y="585" font-family="Arial, sans-serif" font-size="12" fill="#4b5563">Values are macro averages at document/source level; pending values render as 0 until a run completes.</text>')
    parts.append('</svg>')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def run_benchmark(
    dataset_path: Path,
    output_path: Path,
    chart_path: Path,
    groups: Sequence[str],
    limit: int | None = None,
    dry_run: bool = False,
) -> int:
    cases, skipped = load_cases(dataset_path, groups, limit)
    if dry_run:
        payload = {
            "status": "dry_run",
            "dataset": str(dataset_path),
            "groups": list(groups),
            "cases": len(cases),
            "skipped": skipped,
            "gold_groups": dict(Counter(case.group for case in cases)),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if not cases:
        print(json.dumps({"status": "error", "error": "no evaluable cases", "skipped": skipped}, ensure_ascii=False, indent=2))
        return 2

    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from app.services.rag_engine import AdvancedChunkingEngine

        engine = AdvancedChunkingEngine(
            persist_dir=str(PROJECT_ROOT / "parent_doc_storage"),
            load_reranker=False,
            metadata_filter_enabled=False,
        )
    except Exception as exc:
        payload = {"status": "blocked", "stage": "rag_engine", "error": f"{type(exc).__name__}: {exc}", "cases": len(cases)}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    graph_service = None
    graph_error = None
    try:
        from app.services.graph_service import AcademicGraphService

        graph_service = AcademicGraphService(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )
        if not graph_service.ensure_data_loaded():
            graph_error = "Neo4j graph data could not be loaded"
    except Exception as exc:
        graph_error = f"{type(exc).__name__}: {exc}"

    file_by_code = _graph_file_map()
    per_variant: dict[str, list[dict[str, Any]]] = {f"E{index}": [] for index in range(1, 6)}
    errors: list[dict[str, str]] = []
    for case in cases:
        try:
            lanes = _retrieve_lanes(engine, case.question)
            graph = _graph_sources(graph_service, case.question, file_by_code)
            for variant, (retrieved, route) in _variant_sources(lanes, graph, case.question).items():
                metric = _metrics(retrieved, case.gold_sources)
                per_variant[variant].append(
                    {
                        "case_id": case.case_id,
                        "group": case.group,
                        "question": case.question,
                        "gold_sources": list(case.gold_sources),
                        "graph_sources": graph,
                        "agent_route": route,
                        **metric,
                    }
                )
        except Exception as exc:
            errors.append({"case_id": case.case_id, "error": f"{type(exc).__name__}: {exc}"})

    summary: dict[str, Any] = {}
    labels = {
        "E1": ("BM25", "Baseline lexical"),
        "E2": ("Dense", "Baseline semantic"),
        "E3": ("BM25 + Dense + RRF", "Hybrid baseline"),
        "E4": ("BM25 + Dense + RRF + Graph", "Graph contribution"),
        "E5": ("BM25 + Dense + RRF + Graph + Agent", "Proposed system"),
    }
    for variant, rows in per_variant.items():
        config, purpose = labels[variant]
        summary[variant] = {
            "configuration": config,
            "purpose": purpose,
            "cases": len(rows),
            "precision_at_5": _mean(rows, "precision_at_5"),
            "recall_at_5": _mean(rows, "recall_at_5"),
            "mrr": _mean(rows, "mrr"),
            "details": rows,
        }

    payload = {
        "status": "completed" if not errors else "completed_with_errors",
        "benchmark": "Table 4 E1-E5",
        "dataset": str(dataset_path),
        "groups": list(groups),
        "top_k": TOP_K,
        "rrf_k": RRF_K,
        "cases_loaded": len(cases),
        "skipped": skipped,
        "errors": errors,
        "graph": {"available": graph_service is not None and graph_error is None, "error": graph_error},
        "chart": str(chart_path),
        "variants": summary,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_chart(summary, chart_path)
    print(json.dumps({key: value for key, value in payload.items() if key != "variants"}, ensure_ascii=False, indent=2))
    for variant, result in summary.items():
        print(
            f"{variant}: P@5={result['precision_at_5']:.4f} "
            f"Recall@5={result['recall_at_5']:.4f} MRR={result['mrr']:.4f} "
            f"n={result['cases']}"
        )
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--chart", type=Path, default=DEFAULT_CHART)
    parser.add_argument("--groups", nargs="+", default=["RAGAS", "E2E"], choices=["RAGAS", "E2E", "Retrieval"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return run_benchmark(args.dataset, args.output, args.chart, args.groups, args.limit, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
