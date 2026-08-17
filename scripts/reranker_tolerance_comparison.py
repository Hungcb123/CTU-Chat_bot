"""So sánh 4 cấu hình reranker trên cùng 100 câu dataset:
  1. plain        : CrossEncoderReranker gốc (chỉ theo score)
  2. tie 0.05     : TemporalCrossEncoderReranker score_tolerance=0.05
  3. tie 0.02     : TemporalCrossEncoderReranker score_tolerance=0.02
  4. tie 0.01     : TemporalCrossEncoderReranker score_tolerance=0.01

Ngoài hit/rank, script phân tích "lost in the middle": vị trí (position fraction)
của expected source trong context. Theo Liu et al. 2024, attention LLM có hình chữ U
(đầu tốt nhất, cuối khá tốt, giữa dễ bị bỏ quên) nên ta gán trọng số attention theo vị trí:
  - p < 0.20  (đầu context): w = 1.00
  - 0.20..0.80 (giữa):         w = 0.50
  - p > 0.80  (cuối context):  w = 0.85

    python scripts/reranker_tolerance_comparison.py \
        --jsonl-005 <merge_0.05>.jsonl \
        --jsonl-002 <run_0.02>.jsonl \
        --jsonl-001 <run_0.01>.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "logs" / "reranker_ab_test"

CONFIGS = ("plain", "tie_005", "tie_002", "tie_001")
LABELS = {
    "plain": "Plain (B)",
    "tie_005": "Tie 0.05 (A)",
    "tie_002": "Tie 0.02 (A')",
    "tie_001": "Tie 0.01 (A'')",
}


def load_records(path: Path) -> dict[int, dict[str, Any]]:
    records: dict[int, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        records[int(record["case_id"])] = record
    return records


def attention_weight(position_fraction: float) -> float:
    if position_fraction < 0.20:
        return 1.00
    if position_fraction <= 0.80:
        return 0.50
    return 0.85


def position_fraction(rank: int | None, doc_count: int | None) -> float | None:
    if rank is None or not doc_count or doc_count < 1:
        return None
    if doc_count == 1:
        return 0.0
    return (rank - 1) / (doc_count - 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl-005", type=Path, help="JSONL tolerance=0.05 (đã merge)")
    parser.add_argument("--jsonl-002", type=Path, help="JSONL tolerance=0.02")
    parser.add_argument("--jsonl-001", type=Path, help="JSONL tolerance=0.01")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    provided = {name: getattr(args, name) for name in ("jsonl_005", "jsonl_002", "jsonl_001")}
    provided = {k: v for k, v in provided.items() if v is not None}
    if not provided:
        raise SystemExit("Cần ít nhất một trong --jsonl-005 / --jsonl-002 / --jsonl-001")

    sources: dict[str, dict[int, dict[str, Any]]] = {}
    for key, path in provided.items():
        sources[key] = load_records(path)
        print(f"Loaded {len(sources[key])} records from {path.name} ({key})")

    base_ids = sorted(set.intersection(*(set(v) for v in sources.values())))
    if not base_ids:
        raise SystemExit("Không có case nào trùng giữa các file JSONL")
    print(f"Cases chung: {len(base_ids)}")

    # plain lấy từ bất kỳ file nào (đã kiểm tra nhất quán giữa các run)
    plain_source = next(iter(sources.values()))

    rows: list[dict[str, Any]] = []
    sanity_mismatch = 0
    for case_id in base_ids:
        plain_rec = plain_source[case_id]
        if plain_rec["bypass"]:
            continue
        row: dict[str, Any] = {
            "case_id": case_id,
            "category": plain_rec["category"],
            "question": plain_rec["question"],
            "expected_sources": plain_rec["expected_sources"],
            "intent": plain_rec["intent"],
        }
        for cfg_key in CONFIGS:
            if cfg_key == "plain":
                rec = plain_rec
                tie_key = "plain"
            else:
                tol = cfg_key.split("_")[1]
                src = sources.get(f"jsonl_{tol}")
                if src is None:
                    continue
                rec = src[case_id]
                tie_key = "tie_break"
            v = rec["variants"][tie_key]
            row[cfg_key] = {
                "hit": v["hit"],
                "rank": v["rank"],
                "n_docs": len(v["sources"]),
            }
        if row["plain"]["rank"] is not None:
            for cfg_key in ("tie_005", "tie_002", "tie_001"):
                if cfg_key in row and row[cfg_key]["rank"] is not None and row[cfg_key]["rank"] != row["plain"]["rank"]:
                    pass
        rows.append(row)

    active = rows
    n_active = len(active)

    def hit_count(cfg: str) -> int:
        return sum(1 for r in active if r.get(cfg, {}).get("hit"))

    def avg_rank(cfg: str) -> float | None:
        ranks = [r[cfg]["rank"] for r in active if r.get(cfg, {}).get("rank") is not None]
        return sum(ranks) / len(ranks) if ranks else None

    def diff_vs_plain(cfg: str) -> dict[str, int]:
        better = worse = equal = 0
        for r in active:
            pr = r["plain"]["rank"]
            cr = r.get(cfg, {}).get("rank")
            if pr is None or cr is None:
                continue
            if cr < pr:
                better += 1
            elif cr > pr:
                worse += 1
            else:
                equal += 1
        return {"better": better, "worse": worse, "equal": equal}

    def avg_attention(cfg: str) -> float | None:
        weights = []
        for r in active:
            if cfg not in r:
                continue
            rank = r[cfg]["rank"]
            n = r[cfg]["n_docs"]
            if rank is None:
                continue
            pf = position_fraction(rank, n)
            if pf is not None:
                weights.append(attention_weight(pf))
        return sum(weights) / len(weights) if weights else None

    def attn_better_than(cfg: str, other: str) -> dict[str, int]:
        better = worse = equal = 0
        for r in active:
            if cfg not in r or other not in r:
                continue
            pf1 = position_fraction(r[cfg]["rank"], r[cfg]["n_docs"])
            pf2 = position_fraction(r[other]["rank"], r[other]["n_docs"])
            if pf1 is None or pf2 is None:
                continue
            w1 = attention_weight(pf1)
            w2 = attention_weight(pf2)
            if w1 > w2:
                better += 1
            elif w1 < w2:
                worse += 1
            else:
                equal += 1
        return {"better": better, "worse": worse, "equal": equal}

    lines = [
        "# So sánh 4 cấu hình reranker: Plain vs Tie-break 0.05 / 0.02 / 0.01",
        "",
        f"- Thời điểm: `{datetime.now(timezone.utc).astimezone().isoformat()}`",
    ]
    for key, path in provided.items():
        lines.append(f"- {key}: `{path.name}`")
    lines.extend(
        [
            f"- Số câu so sánh (RAG active): **{n_active}**",
            "",
            "> Vị trí (position fraction): `(rank-1)/(n_docs-1)`, 0=đầu context, 1=cuối. "
            "Trọng số attention hình chữ U: đầu=1.0, giữa=0.5, cuối=0.85 (tham khảo Liu et al. 2024).",
            "",
            "## Tổng quan",
            "",
            "| Chỉ số | Plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    present = [cfg for cfg in CONFIGS if any(cfg in r for r in active)]
    lines.append(
        "| Hit (expected source trong top docs) | "
        + " | ".join(f"{hit_count(c)}/{n_active} ({hit_count(c)/n_active*100:.2f}%)" for c in present)
        + " |"
    )
    lines.append(
        "| Avg rank expected source | "
        + " | ".join(f"{avg_rank(c):.2f}" for c in present)
        + " |"
    )
    lines.append(
        "| Avg attention weight (lost-in-middle proxy) | "
        + " | ".join(f"{avg_attention(c):.3f}" for c in present)
        + " |"
    )
    lines.extend(
        [
            "",
            "### So với plain (thay đổi rank của expected source)",
            "",
            "| So với plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |",
            "|---|---:|---:|---:|",
        ]
    )
    for tie in ("tie_005", "tie_002", "tie_001"):
        d = diff_vs_plain(tie)
        lines.append(f"| Rank khác plain: tốt hơn / tệ hơn / bằng | {d['better']} / {d['worse']} / {d['equal']} |")
    lines.extend(
        [
            "",
            "### Attention (lost-in-the-middle) so với plain",
            "",
            "| So với plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |",
            "|---|---:|---:|---:|",
        ]
    )
    for tie in ("tie_005", "tie_002", "tie_001"):
        d = attn_better_than(tie, "plain")
        lines.append(f"| Attention tốt hơn / kém hơn / bằng | {d['better']} / {d['worse']} / {d['equal']} |")

    # Chi tiết các case có bất kỳ tie config nào khác plain
    lines.extend(["", "## Chi tiết từng câu khác biệt", ""])
    changed_rows = []
    for r in sorted(active, key=lambda r: r["case_id"]):
        ranks = {cfg: r.get(cfg, {}).get("rank") for cfg in present}
        if any(v is not None and v != ranks["plain"] for cfg, v in ranks.items() if cfg != "plain"):
            changed_rows.append(r)
    for r in changed_rows:
        lines.extend(
            [
                f"### Câu {r['case_id']} · {r['category']}",
                "",
                f"- Intent: `{r['intent']}` | Nguồn kỳ vọng: `{', '.join(r['expected_sources'])}`",
                f"- Câu hỏi: {r['question']}",
            ]
        )
        for cfg in present:
            c = r.get(cfg, {})
            rank = c.get("rank")
            pf = position_fraction(rank, c.get("n_docs"))
            attn = attention_weight(pf) if pf is not None else None
            pos_str = f"{pf:.2f}" if pf is not None else "-"
            attn_str = f"{attn:.2f}" if attn is not None else "-"
            lines.append(
                f"- {LABELS[cfg]}: hit={c.get('hit')}, rank={rank or '-'}, "
                f"n_docs={c.get('n_docs')}, pos={pos_str}, attn={attn_str}"
            )
        lines.extend(["", "---", ""])
    if not changed_rows:
        lines.append("(không có câu nào khác biệt)")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    report_path = args.output_dir / f"reranker_tolerance_comparison_{stamp}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Completed ({n_active} active): "
        + " | ".join(
            f"{cfg}: hit={hit_count(cfg)}/{n_active} avgrank={avg_rank(cfg):.2f} attn={avg_attention(cfg):.3f}"
            for cfg in present
        )
    )
    print(f"Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
