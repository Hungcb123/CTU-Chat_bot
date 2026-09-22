import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from scripts.run_multi_vs_single_agent_v5_scalability import (
    DEFAULT_BASE_DISTRACTORS,
    DEFAULT_EXTENSION_DISTRACTORS,
    bm25_shortlist,
    build_distractor_tools,
    load_registry,
    parse_levels,
    validate_args,
)

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class DummyTool:
    name: str
    description: str
    args_schema: object | None = None


def test_v5_registry_is_nested_and_balanced():
    registry = load_registry(DEFAULT_BASE_DISTRACTORS, DEFAULT_EXTENSION_DISTRACTORS)
    assert len(registry) == 40
    assert all(len(build_distractor_tools(registry, 10)[domain]) == 10 for domain in ("academic", "financial", "scholarship", "general"))
    assert all(len(build_distractor_tools(registry, 4)[domain]) == 4 for domain in ("academic", "financial", "scholarship", "general"))
    assert all(len(build_distractor_tools(registry, 0)[domain]) == 0 for domain in ("academic", "financial", "scholarship", "general"))


def test_v5_levels_map_to_11_27_51_tools():
    levels = parse_levels("0,4,10")
    assert [11 + 4 * level for level in levels] == [11, 27, 51]


def test_bm25_shortlist_prefers_semantically_matching_tool():
    tools = [
        DummyTool("tra_cuu_nganh", "Tra cứu thông tin ngành và tổng số tín chỉ."),
        DummyTool("xem_chuoi_tien_quyet", "Xem chuỗi môn học tiên quyết cần học trước."),
        DummyTool("tra_cuu_lich_hoc", "Tra cứu thời khóa biểu và lịch học."),
    ]
    selected, scores = bm25_shortlist("Môn nào là tiên quyết cần học trước?", tools, 1)
    assert selected[0].name == "xem_chuoi_tien_quyet"
    assert scores["xem_chuoi_tien_quyet"] > scores["tra_cuu_lich_hoc"]


def test_schema_guard_rejects_missing_required_argument():
    class Args(BaseModel):
        value: int

    tool = DummyTool("calculator", "Calculate", Args)
    assert validate_args(tool, {"value": 1})[0] is True
    valid, error = validate_args(tool, {})
    assert valid is False
    assert "ValidationError" in error


def test_validate_only_cli():
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_multi_vs_single_agent_v5_scalability.py"),
        "--validate-only",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "registry_sizes=[11, 27, 51]" in result.stdout
    assert "expected_records=2160" in result.stdout
