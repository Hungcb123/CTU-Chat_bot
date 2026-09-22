import json
import math
from pathlib import Path
from collections import defaultdict
from statistics import mean

CKPT_PATH = Path("/mnt/d/Project/Chatbot/logs/scenario12/20260920T153313Z/checkpoint.json")

def audit_ragas():
    if not CKPT_PATH.exists():
        print("Checkpoint not found!")
        return
    
    ckpt = json.loads(CKPT_PATH.read_text(encoding="utf-8"))
    answers = ckpt.get("answers", {})
    ragas = ckpt.get("ragas", {})
    
    total_answers = len(answers)
    total_ragas = len(ragas)
    
    print(f"=== RAGAS EVALUATION AUDIT ===")
    print(f"Answers generated: {total_answers} / 2100")
    print(f"Ragas evaluated:   {total_ragas} / 2100 ({total_ragas/2100*100:.1f}%)")
    
    if not ragas:
        print("Ragas evaluation has not produced any records yet.")
        return

    metrics = ["AR", "CR", "CP", "AC", "Faith"]
    missing_by_metric = defaultdict(list)
    valid_counts = defaultdict(int)
    scores_by_config = defaultdict(lambda: defaultdict(list))
    
    for key, record in ragas.items():
        # key format: r{rep}:{case_id}:{config}
        parts = key.split(":")
        cfg = parts[2] if len(parts) >= 3 else "unknown"
        
        for m in metrics:
            val = record.get(m)
            if val is not None and isinstance(val, (int, float)) and math.isfinite(val):
                valid_counts[m] += 1
                scores_by_config[cfg][m].append(float(val))
            else:
                missing_by_metric[m].append((key, val))
                
    print("\n--- Metric Completeness (Valid / Evaluated) ---")
    for m in metrics:
        v = valid_counts[m]
        miss = len(missing_by_metric[m])
        pct = (v / total_ragas * 100) if total_ragas else 0
        status = "OK (100%)" if miss == 0 else f"WARNING: {miss} missing/None!"
        print(f"  {m:<6}: {v}/{total_ragas} ({pct:.1f}%) -> {status}")
        
    missing_file = CKPT_PATH.parent / "missing_ragas_cells.json"
    if any(len(v) > 0 for v in missing_by_metric.values()):
        print("\n[!] Sample missing/invalid records:")
        payload = {}
        for m in metrics:
            if missing_by_metric[m]:
                sample = missing_by_metric[m][:3]
                print(f"  {m}: {len(missing_by_metric[m])} missing. Examples: {sample}")
                payload[m] = [{"key": k, "val": v} for k, v in missing_by_metric[m]]
        missing_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  -> Đã lưu toàn bộ {sum(len(v) for v in payload.values())} ô lỗi vào: {missing_file.name}")
    else:
        if missing_file.exists():
            missing_file.unlink()
                
    print("\n--- Current Interim Means by Config ---")
    header = f"{'Config':<8} | {'AR':<8} | {'CR':<8} | {'CP':<8} | {'AC':<8} | {'Faith':<8} | {'Count':<6}"
    print(header)
    print("-" * len(header))
    for cfg in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        m_scores = scores_by_config[cfg]
        ar = f"{mean(m_scores['AR']):.4f}" if m_scores['AR'] else "N/A"
        cr = f"{mean(m_scores['CR']):.4f}" if m_scores['CR'] else "N/A"
        cp = f"{mean(m_scores['CP']):.4f}" if m_scores['CP'] else "N/A"
        ac = f"{mean(m_scores['AC']):.4f}" if m_scores['AC'] else "N/A"
        faith = f"{mean(m_scores['Faith']):.4f}" if m_scores['Faith'] else "N/A"
        cnt = len(m_scores['AR'])
        print(f"{cfg:<8} | {ar:<8} | {cr:<8} | {cp:<8} | {ac:<8} | {faith:<8} | {cnt:<6}")

if __name__ == "__main__":
    audit_ragas()
