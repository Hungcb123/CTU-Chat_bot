import json
import unittest
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

from scripts.run_multi_vs_single_agent_v3_scalability import (
    load_distractor_registry,
    build_distractor_tools,
    DISCLOSURE_TERMS,
    score_case,
)
from scripts.summarize_multi_vs_single_v3 import bootstrap_ci, compute_case_means, summarize_level
from scripts.run_multi_vs_single_agent_experiment import SPECIALIST_TOOLS


def test_distractor_registry_validation():
    registry_path = ROOT / "data" / "scenario3_distractor_registry_v3.json"
    assert registry_path.exists(), "Distractor registry v3 must exist"
    data = load_distractor_registry(registry_path)
    assert len(data) == 16, "Must have exactly 16 distractors"

    domains = [item["domain"] for item in data]
    for d in ("academic", "financial", "scholarship", "general"):
        assert domains.count(d) == 4, f"Domain {d} must have exactly 4 distractors"

    # Verify no disclosure terms
    for item in data:
        desc = item["description"].lower()
        for term in DISCLOSURE_TERMS:
            assert term not in desc, f"Found disclosure term '{term}' in {item['name']}"

    # Verify no name collision with production tools
    all_real_names = set()
    for names in SPECIALIST_TOOLS.values():
        all_real_names.update(names)

    distractor_names = [item["name"] for item in data]
    assert len(distractor_names) == len(set(distractor_names)), "Distractor names must be unique"
    for name in distractor_names:
        assert name not in all_real_names, f"Distractor name '{name}' collides with production tool"


def test_tool_counts_by_level():
    registry_path = ROOT / "data" / "scenario3_distractor_registry_v3.json"
    registry = load_distractor_registry(registry_path)

    # Level 0
    d0 = build_distractor_tools(registry, 0)
    for d in ("academic", "financial", "scholarship", "general"):
        assert len(d0[d]) == 0

    # Level 2
    d2 = build_distractor_tools(registry, 2)
    assert len(d2["academic"]) == 2
    assert len(d2["financial"]) == 2
    assert len(d2["scholarship"]) == 2
    assert len(d2["general"]) == 2
    single_2 = 11 + sum(len(v) for v in d2.values())
    assert single_2 == 19, f"Level 2 single-agent must see 19 tools, got {single_2}"
    assert len(SPECIALIST_TOOLS["academic"]) + len(d2["academic"]) == 8
    assert len(SPECIALIST_TOOLS["financial"]) + len(d2["financial"]) == 6
    assert len(SPECIALIST_TOOLS["scholarship"]) + len(d2["scholarship"]) == 3
    assert len(SPECIALIST_TOOLS["general"]) + len(d2["general"]) == 2

    # Level 4
    d4 = build_distractor_tools(registry, 4)
    assert len(d4["academic"]) == 4
    assert len(d4["financial"]) == 4
    assert len(d4["scholarship"]) == 4
    assert len(d4["general"]) == 4
    single_4 = 11 + sum(len(v) for v in d4.values())
    assert single_4 == 27, f"Level 4 single-agent must see 27 tools, got {single_4}"
    assert len(SPECIALIST_TOOLS["academic"]) + len(d4["academic"]) == 10
    assert len(SPECIALIST_TOOLS["financial"]) + len(d4["financial"]) == 8
    assert len(SPECIALIST_TOOLS["scholarship"]) + len(d4["scholarship"]) == 5
    assert len(SPECIALIST_TOOLS["general"]) + len(d4["general"]) == 4


def test_bootstrap_ci_reproducibility():
    values = [0.1, -0.2, 0.3, 0.4, 0.0, 0.2, -0.1, 0.5]
    ci1 = bootstrap_ci(values, seed=42, draws=1000)
    ci2 = bootstrap_ci(values, seed=42, draws=1000)
    assert ci1 == ci2
    assert ci1[0] <= ci1[1]


def test_validate_only_cli():
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_multi_vs_single_agent_v3_scalability.py"),
        "--validate-only",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert res.returncode == 0
    assert "production cases       = 60" in res.stdout
    assert "robustness cases       = 20" in res.stdout
    assert "expected total records = 1440" in res.stdout
