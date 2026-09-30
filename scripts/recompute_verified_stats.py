#!/usr/bin/env python3
"""
Recomputes Table 1, Table 2 (ablation), Table 3 (family breakdown),
and all statistical claims for PAPER_V14 based on the verified benchmark
data/scenario12_heldout_100.jsonl (all review_status=verified).
"""

import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILE = ROOT / "logs" / "v13_architecture" / "run_20260923_155602" / "results.jsonl"
HELDOUT_FILE = ROOT / "data" / "scenario12_heldout_100.jsonl"

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def normalize_vietnamese(value: str) -> str:
    value = unicodedata.normalize("NFD", value.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def compute_fact_coverage(response: str, required_facts: list[str]) -> float:
    if not required_facts:
        return 0.0
    norm_resp = normalize_text(response)
    matched = sum(1 for f in required_facts if normalize_text(f) in norm_resp)
    return matched / len(required_facts)

def bootstrap_ci(arr_a, arr_b=None, n_boot=10000, ci=0.95, seed=42):
    rng = np.random.default_rng(seed)
    n = len(arr_a)
    if arr_b is not None:
        diffs = np.array(arr_a) - np.array(arr_b)
    else:
        diffs = np.array(arr_a)
    boot = [np.mean(rng.choice(diffs, size=n, replace=True)) for _ in range(n_boot)]
    alpha = (1 - ci) / 2
    return {
        "mean": float(np.mean(diffs)),
        "lower": float(np.percentile(boot, 100 * alpha)),
        "upper": float(np.percentile(boot, 100 * (1 - alpha))),
    }

def exact_mcnemar(passed_a, passed_b):
    b = sum(1 for a, b in zip(passed_a, passed_b) if a and not b)
    c = sum(1 for a, b in zip(passed_a, passed_b) if not a and b)
    n = b + c
    if n == 0:
        p = 1.0
    else:
        k = min(b, c)
        p = 2 * sum(math.comb(n, i) * (0.5**n) for i in range(k + 1))
        p = min(1.0, p)
    return {"b": b, "c": c, "n": n, "p_value": p}

def main():
    with open(HELDOUT_FILE, "r", encoding="utf-8") as f:
        cases = {json.loads(line)["id"]: json.loads(line) for line in f if line.strip()}
    
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    by_cfg = defaultdict(dict)
    for r in records:
        cfg = r.get("configuration") or r.get("config_id")
        qid = r["query_id"]
        by_cfg[cfg][qid] = r

    qids = sorted(cases.keys())
    print(f"Loaded {len(cases)} benchmark queries, {len(by_cfg)} configs.")
    for cfg in sorted(by_cfg.keys()):
        print(f"  {cfg}: {len(by_cfg[cfg])} queries")

    # Group queries into families:
    # Graph (19), Struct-fin (28), Narr-reg (33), Cross (20)
    family_map = {}
    for qid, c in cases.items():
        dom = c.get("domain", "")
        if "+" in dom:
            family_map[qid] = "Cross"
        elif dom == "academic":
            family_map[qid] = "Graph"
        elif dom == "financial":
            family_map[qid] = "Struct-fin"
        elif dom in ("scholarship", "general", "regulation"):
            family_map[qid] = "Narr-reg"
        else:
            family_map[qid] = "Other"

    counts = defaultdict(int)
    for q, fam in family_map.items():
        counts[fam] += 1
    print("Family counts:", dict(counts))

    # Metric evaluation per config
    metrics = {}
    for cfg, qmap in by_cfg.items():
        e2e_list = []
        fact_list = []
        src_r_list = []
        src_ap_list = []
        tools_list = []
        in_tok_list = []
        out_tok_list = []
        lat_list = []
        
        # Family e2e
        fam_e2e = defaultdict(list)

        for qid in qids:
            r = qmap.get(qid, {})
            facts = cases[qid]["required_facts"]
            resp = r.get("response", "")
            fc = compute_fact_coverage(resp, facts)
            e2e = float(fc >= 0.50)
            
            fact_list.append(fc)
            e2e_list.append(e2e)
            src_r_list.append(r.get("source_recall", 0.0))
            src_ap_list.append(r.get("source_ap", 0.0))
            tc = r.get("tool_calls", 0)
            tools_list.append(len(tc) if isinstance(tc, list) else int(tc or 0))
            in_tok_list.append(r.get("input_tokens", 0))
            out_tok_list.append(r.get("output_tokens", 0))
            lat_list.append(r.get("latency_ms", 0))

            fam = family_map[qid]
            fam_e2e[fam].append(e2e)

        metrics[cfg] = {
            "e2e": e2e_list,
            "fact": fact_list,
            "src_r": src_r_list,
            "src_ap": src_ap_list,
            "tools": tools_list,
            "in_tok": in_tok_list,
            "out_tok": out_tok_list,
            "lat": lat_list,
            "fam_e2e": fam_e2e,
        }

    print("\n" + "="*60)
    print("TABLE 1: Scenario 1 Architecture Comparison (N=100)")
    print("="*60)
    for cfg in ["S1-A", "S1-B", "S1-C"]:
        m = metrics[cfg]
        e2e_pct = np.mean(m["e2e"]) * 100
        fact_pct = np.mean(m["fact"]) * 100
        src_r = np.mean(m["src_r"]) * 100
        src_ap = np.mean(m["src_ap"]) * 100
        tools = np.mean(m["tools"])
        in_tok = np.mean(m["in_tok"])
        out_tok = np.mean(m["out_tok"])
        lat = np.mean(m["lat"])
        med_lat = np.median(m["lat"])
        print(f"{cfg:6s} | E2E: {e2e_pct:5.1f}% | Fact: {fact_pct:5.1f}% | Src.R: {src_r:5.1f}% | Src.AP: {src_ap:5.1f}% | Tools/Q: {tools:4.2f} | InTok: {in_tok:6.0f} | OutTok: {out_tok:6.0f} | Lat(mean): {lat:6.0f}ms | Lat(med): {med_lat:6.0f}ms")

    # Statistical comparisons: CTU (S1-C) vs Single (S1-A)
    ctu = metrics["S1-C"]
    s1a = metrics["S1-A"]
    s1b = metrics["S1-B"]

    print("\n--- CTU-Chat vs Single Agent ---")
    ci_e2e = bootstrap_ci(np.array(ctu["e2e"])*100, np.array(s1a["e2e"])*100)
    mcn = exact_mcnemar([x >= 0.50 for x in ctu["e2e"]], [x >= 0.50 for x in s1a["e2e"]])
    ci_fact = bootstrap_ci(np.array(ctu["fact"])*100, np.array(s1a["fact"])*100)
    diff_intok = bootstrap_ci(ctu["in_tok"], s1a["in_tok"])
    
    # Exclude the 3 extreme looping outliers for token CI as in the paper
    outlier_ids = {"HOUT-MHOP-FIN-01", "HOUT-MHOP-FIN-03", "HOUT-TEMP-05"}
    clean_indices = [i for i, q in enumerate(qids) if q not in outlier_ids]
    ctu_tot = np.array(ctu["in_tok"]) + np.array(ctu["out_tok"])
    s1a_tot = np.array(s1a["in_tok"]) + np.array(s1a["out_tok"])
    diff_tot_clean = bootstrap_ci(ctu_tot[clean_indices], s1a_tot[clean_indices])
    
    print(f"E2E: Diff = {ci_e2e['mean']:+.1f} pp, 95% CI = [{ci_e2e['lower']:+.1f}, {ci_e2e['upper']:+.1f}] pp")
    print(f"McNemar: b={mcn['b']}, c={mcn['c']}, n={mcn['n']}, p={mcn['p_value']:.4f}")
    print(f"Fact: Diff = {ci_fact['mean']:+.2f} pp, 95% CI = [{ci_fact['lower']:+.2f}, {ci_fact['upper']:+.2f}] pp")
    print(f"InTok: Diff = {diff_intok['mean']:.0f} tokens, 95% CI = [{diff_intok['lower']:.0f}, {diff_intok['upper']:.0f}] tokens")
    print(f"TotalTok (clean): Diff = {diff_tot_clean['mean']:.0f} tokens, 95% CI = [{diff_tot_clean['lower']:.0f}, {diff_tot_clean['upper']:.0f}] tokens")

    print("\n--- CTU-Chat vs Routed Generic ---")
    ci_fact_cb = bootstrap_ci(np.array(ctu["fact"])*100, np.array(s1b["fact"])*100)
    ci_e2e_cb = bootstrap_ci(np.array(ctu["e2e"])*100, np.array(s1b["e2e"])*100)
    print(f"Fact: Diff = {ci_fact_cb['mean']:+.2f} pp, 95% CI = [{ci_fact_cb['lower']:+.2f}, {ci_fact_cb['upper']:+.2f}] pp")
    print(f"E2E: Diff = {ci_e2e_cb['mean']:+.1f} pp, 95% CI = [{ci_e2e_cb['lower']:+.1f}, {ci_e2e_cb['upper']:+.1f}] pp")

    print("\n--- Routed Generic vs Single Agent ---")
    ci_fact_ba = bootstrap_ci(np.array(s1b["fact"])*100, np.array(s1a["fact"])*100)
    diff_intok_ba = bootstrap_ci(s1b["in_tok"], s1a["in_tok"])
    print(f"Fact: Diff = {ci_fact_ba['mean']:+.2f} pp, 95% CI = [{ci_fact_ba['lower']:+.2f}, {ci_fact_ba['upper']:+.2f}] pp")
    print(f"InTok: Diff = {diff_intok_ba['mean']:.0f} tokens, 95% CI = [{diff_intok_ba['lower']:.0f}, {diff_intok_ba['upper']:.0f}] tokens")

    print("\n--- Cross-domain (N=20) ---")
    print(f"CTU-Chat: {np.mean(ctu['fam_e2e']['Cross'])*100:.1f}% ({sum(ctu['fam_e2e']['Cross'])}/20)")
    print(f"Single:   {np.mean(s1a['fam_e2e']['Cross'])*100:.1f}% ({sum(s1a['fam_e2e']['Cross'])}/20)")
    print(f"Generic:  {np.mean(s1b['fam_e2e']['Cross'])*100:.1f}% ({sum(s1b['fam_e2e']['Cross'])}/20)")

    print("\n" + "="*60)
    print("TABLE 2: Scenario 2 Architectural Ablation (Deltas rel. to Full CTU-Chat)")
    print("="*60)
    ctu_tot_all = np.array(ctu["in_tok"]) + np.array(ctu["out_tok"])
    
    # Ablations map to config IDs:
    # S1-B: No Spec Policy
    # S2-A2: Full Tool Vis
    # S2-A3: Uniform Text-RAG
    # S2-A4: No Determ Calc
    # S2-A5: No Route Rep
    ablation_cfgs = [
        ("No Spec.~Policy", "S1-B"),
        ("Full Tool Vis.", "S2-A2"),
        ("Uniform Text-RAG", "S2-A3"),
        ("No Route Rep.", "S2-A5"),
        ("No Determ.~Calc.$^\\dagger$", "S2-A4"),
    ]

    for label, acfg in ablation_cfgs:
        am = metrics[acfg]
        delta_e2e = bootstrap_ci(np.array(am["e2e"])*100, np.array(ctu["e2e"])*100)
        delta_fact = bootstrap_ci(np.array(am["fact"])*100, np.array(ctu["fact"])*100)
        delta_src_r = bootstrap_ci(np.array(am["src_r"])*100, np.array(ctu["src_r"])*100)
        
        # tokens: input tokens delta or total tokens delta?
        # In Table 2: DeltaTok is input token or total token? Let's check:
        delta_intok = np.mean(am["in_tok"]) - np.mean(ctu["in_tok"])
        am_tot = np.array(am["in_tok"]) + np.array(am["out_tok"])
        delta_tot = np.mean(am_tot) - np.mean(ctu_tot_all)
        delta_lat = np.mean(am["lat"]) - np.mean(ctu["lat"])
        print(f"{label:25s} | dE2E: {delta_e2e['mean']:+5.1f} (CI [{delta_e2e['lower']:+5.1f}, {delta_e2e['upper']:+5.1f}]) | dFact: {delta_fact['mean']:+5.2f} (CI [{delta_fact['lower']:+5.2f}, {delta_fact['upper']:+5.2f}]) | dSrc.R: {delta_src_r['mean']:+5.1f} | dInTok: {delta_intok:+6.0f} | dTotTok: {delta_tot:+6.0f} | dLat: {delta_lat:+6.0f}ms")

    print("\n" + "="*60)
    print("TABLE 3: Scenario 2 E2E Success by query family across ablations")
    print("="*60)
    print(f"{'Config.':22s} | {'Graph (n=19)':12s} | {'Struct-fin (n=28)':17s} | {'Narr-reg (n=33)':15s} | {'Cross (n=20)':12s}")
    breakdown_cfgs = [
        ("Full CTU-Chat", "S1-C"),
        ("No Spec.~Policy", "S1-B"),
        ("Full Tool Vis.", "S2-A2"),
        ("Uniform Text-RAG", "S2-A3"),
        ("No Route Rep.", "S2-A5"),
    ]
    for label, cfg in breakdown_cfgs:
        fam_m = metrics[cfg]["fam_e2e"]
        g_pct = np.mean(fam_m["Graph"]) * 100
        f_pct = np.mean(fam_m["Struct-fin"]) * 100
        r_pct = np.mean(fam_m["Narr-reg"]) * 100
        c_pct = np.mean(fam_m["Cross"]) * 100
        print(f"{label:22s} | {g_pct:12.1f} | {f_pct:17.1f} | {r_pct:15.1f} | {c_pct:12.1f}")

    # Arithmetic tuition subset (N=9) check for S2-A4
    tuition_arith_qids = [
        q for q in qids if any(
            kw in normalize_vietnamese(cases[q]["question"]) for kw in ("tinh tien", "bao nhieu tien", "tinh hoc phi", "mien giam")
        )
    ]
    print(f"\nTuition arithmetic subset queries: {len(tuition_arith_qids)}")
    for q in tuition_arith_qids:
        print(f"  {q}: {cases[q]['question']}")
    ctu_arith_pass = [compute_fact_coverage(by_cfg["S1-C"][q]["response"], cases[q]["required_facts"]) >= 0.50 for q in tuition_arith_qids]
    s2a4_arith_pass = [compute_fact_coverage(by_cfg["S2-A4"][q]["response"], cases[q]["required_facts"]) >= 0.50 for q in tuition_arith_qids]
    print(f"S1-C arith pass (E2E >=0.50): {sum(ctu_arith_pass)}/{len(tuition_arith_qids)}, S2-A4 arith pass (E2E >=0.50): {sum(s2a4_arith_pass)}/{len(tuition_arith_qids)}")

if __name__ == "__main__":
    main()
