import json

from scripts.run_multi_vs_single_agent_v6_ambiguity import (
    ARCHITECTURES,
    DEFAULT_DATASET,
    DEFAULT_REGISTRY,
    LEVELS,
    build_neighbor_tools,
    coverage_cases,
    load_registry,
    specialist_prompt,
)


def test_registry_is_balanced_by_target_family():
    registry = load_registry(DEFAULT_REGISTRY)
    assert len(registry) == 40
    families = {item["target_family"] for item in registry}
    assert len(families) == 10
    assert all(sum(item["target_family"] == family for item in registry) == 4 for family in families)


def test_levels_produce_locked_registry_sizes():
    registry = load_registry(DEFAULT_REGISTRY)
    assert LEVELS == (0, 2, 4)
    assert [11 + sum(len(items) for items in build_neighbor_tools(registry, level).values()) for level in LEVELS] == [11, 31, 51]


def test_coverage_makes_every_neighbor_a_gold_tool():
    registry = load_registry(DEFAULT_REGISTRY)
    cases = coverage_cases(registry)
    assert len(cases) == 40
    assert {case["expected_tool"] for case in cases} == {item["name"] for item in registry}
    assert len({case["id"] for case in cases}) == 40


def test_primary_design_has_50_fixed_cases_and_1960_records():
    production = json.loads(DEFAULT_DATASET.read_text(encoding="utf-8"))
    primary = [case for case in production if case.get("agent") in {"academic", "financial"}]
    expected = len(primary) * len(LEVELS) * len(ARCHITECTURES) * 3 + 40 * len(ARCHITECTURES)
    assert len(primary) == 50
    assert expected == 1960


def test_specialist_prompt_does_not_disclose_evaluation_role():
    registry = load_registry(DEFAULT_REGISTRY)
    tools = build_neighbor_tools(registry, 4)["academic"][:3]
    policies = {item["name"]: (item["use_when"], item["avoid_when"]) for item in registry}
    prompt = specialist_prompt(tools, policies).casefold()
    for forbidden in ("synthetic", "distractor", "benchmark", "giả lập"):
        assert forbidden not in prompt
