import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.run_multi_vs_single_agent_v4_scalability import (
    ARCHITECTURES,
    counterbalanced_tools,
    expected_position,
    schema_chars,
)
from scripts.summarize_multi_vs_single_v4 import summarize_level

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class DummyTool:
    name: str
    description: str = "A tool"
    args: dict | None = None


def test_counterbalanced_gold_position_and_determinism():
    tools = [DummyTool(name) for name in ("a", "b", "gold", "c", "d")]
    expected_indices = (0, 2, 4)
    for block, expected_index in enumerate(expected_indices, start=1):
        first = counterbalanced_tools(
            tools,
            expected_tool="gold",
            case_key="production:001",
            order_block=block,
            seed=42,
        )
        second = counterbalanced_tools(
            tools,
            expected_tool="gold",
            case_key="production:001",
            order_block=block,
            seed=42,
        )
        assert [tool.name for tool in first] == [tool.name for tool in second]
        assert [tool.name for tool in first].index("gold") == expected_index


def test_nested_registry_preserves_existing_non_gold_order():
    base = [DummyTool(name) for name in ("a", "b", "gold", "c")]
    expanded = base + [DummyTool("x"), DummyTool("y")]
    base_order = counterbalanced_tools(
        base,
        expected_tool="gold",
        case_key="production:002",
        order_block=1,
        seed=7,
    )
    expanded_order = counterbalanced_tools(
        expanded,
        expected_tool="gold",
        case_key="production:002",
        order_block=1,
        seed=7,
    )
    expanded_existing = [tool.name for tool in expanded_order if tool.name in {t.name for t in base}]
    assert expanded_existing == [tool.name for tool in base_order]


def test_position_and_schema_measurement():
    tools = [
        DummyTool("a", "first", {"x": {"type": "string"}}),
        DummyTool("gold", "second", {"y": {"type": "integer"}}),
    ]
    assert expected_position([tool.name for tool in tools], "gold") == (2, 1.0)
    assert expected_position([tool.name for tool in tools], None) == (None, None)
    assert schema_chars(tools) > 0


def test_three_arm_summary_contrasts():
    case_means = {}
    for case_id in ("c1", "c2"):
        case_means[("production_tools", 0, "single_agent", case_id)] = {
            "selection_passed": 0.0,
            "arguments_passed": 0.0,
            "result_passed": 0.0,
            "passed": 0.0,
            "bounded_pass": 1.0,
            "visible_tool_count": 11.0,
            "visible_tool_schema_chars": 1000.0,
            "route_latency_ms": 0.0,
            "gate_latency_ms": 100.0,
            "total_decision_latency_ms": 100.0,
        }
        for architecture in ("oracle_partitioned", "multi_agent"):
            case_means[("production_tools", 0, architecture, case_id)] = {
                "selection_passed": 1.0,
                "arguments_passed": 1.0,
                "result_passed": 1.0,
                "passed": 1.0,
                "bounded_pass": 1.0,
                "visible_tool_count": 4.0,
                "visible_tool_schema_chars": 400.0,
                "route_latency_ms": 50.0 if architecture == "multi_agent" else 0.0,
                "gate_latency_ms": 100.0,
                "total_decision_latency_ms": 150.0 if architecture == "multi_agent" else 100.0,
            }
    summary = summarize_level(
        case_means,
        suite="production_tools",
        level=0,
        case_ids=["c1", "c2"],
        seed=1,
        draws=100,
    )
    assert set(summary["architectures"]) == set(ARCHITECTURES)
    assert summary["paired_contrasts"]["live_vs_single"]["selection_passed"]["mean"] == 1.0
    assert summary["paired_contrasts"]["live_vs_oracle"]["selection_passed"]["mean"] == 0.0


def test_validate_only_cli_reports_locked_record_count():
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_multi_vs_single_agent_v4_scalability.py"),
        "--validate-only",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "expected total records = 2160" in result.stdout
    assert "oracle_partitioned" in result.stdout
