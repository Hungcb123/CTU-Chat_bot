#!/usr/bin/env python3
"""
Update data/scenario12_heldout.jsonl with:
1. Multi-source canonical equivalents for official regulations (scholarships, loans, tuition exemptions).
2. Clean natural language formulations for robotic tuition template queries.
3. Fix domain conflicts (e.g. administrative fee vs tuition).
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELDOUT_PATH = ROOT / "data" / "scenario12_heldout.jsonl"
BACKUP_PATH = ROOT / "data" / "scenario12_heldout.jsonl.bak"

# 1. Back up original
if not BACKUP_PATH.exists():
    shutil.copyfile(HELDOUT_PATH, BACKUP_PATH)
    print(f"Created backup at {BACKUP_PATH}")

# 2. Define canonical equivalents
GOLD_UPDATES = {
    "HOUT-STUDENT-LOAN-01": [
        "VayVonSinhVien2022.md",
        "NDCP_VayVonSVKT.md",
        "VayVon.md",
    ],
    "HOUT-STUDENT-LOAN-02": [
        "VayVonVoiNhomNganhKThuat.md",
        "NDCP_VayVonSVKT.md",
        "VayVonVoiNhomNganhKThuat - Copy.md",
    ],
    "HOUT-SCHOLARSHIP-01": [
        "HB_K51_2026.md",
        "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md",
    ],
    "HOUT-SOCIAL-SUPPORT-01": [
        "Ho_tro.md",
        "02_246_23-06-2026.md",
    ],
    "HOUT-SOCIAL-SUPPORT-02": [
        "HoTroCp.md",
        "02_246_23-06-2026.md",
        "donz.md",
    ],
    "HOUT-EXEMPTION-POLICY-02": [
        "12_don_de_nghi_mien_giam_hoc_phi_llp.md",
        "mghp.md",
    ],
    "HOUT-EXEMPTION-BASIS-01": [
        "MucHocPhi_2526_MienGiam.md",
        "mghp.md",
    ],
    "HOUT-ACADEMIC-RULES-06": [
        "7_don_de_nghi_chuyen_ctdt_llp.md",
        "02_3924KHTH_23-10-2023_llp.md",
    ],
}

# 3. Naturalized conversational questions
QUESTION_UPDATES = {
    "HOUT-TUI-01": "Ngành Thú y khóa 52 chương trình chuẩn đóng học phí trọn khóa là bao nhiêu tiền?",
    "HOUT-TUI-02": "Học phí toàn khóa của ngành Kỹ thuật y sinh K52 hệ chuẩn năm học 2026-2027 là bao nhiêu?",
    "HOUT-TUI-03": "Học phí trọn khóa ngành Kỹ thuật xây dựng công trình thủy hệ chuẩn K52 là bao nhiêu?",
    "HOUT-TUI-04": "Sinh viên ngành Công nghệ sinh học chương trình tiên tiến khóa 52 mỗi năm học đóng bao nhiêu học phí?",
    "HOUT-TUI-05": "Cho mình hỏi học phí mỗi tín chỉ của ngành Nuôi trồng thủy sản hệ tiên tiến khóa 49 là bao nhiêu?",
    "HOUT-TUI-06": "Một tín chỉ ngành Quản lý xây dựng chương trình chuẩn khóa 52 có mức thu học phí là bao nhiêu?",
    "HOUT-TUI-07": "Học phí một tín chỉ của ngành Kỹ thuật điều khiển và tự động hóa hệ chuẩn khóa 52 là bao nhiêu?",
    "HOUT-TUI-08": "Sinh viên ngành Tài chính – Ngân hàng chất lượng cao khóa 49 đóng học phí bao nhiêu mỗi năm học?",
    "HOUT-TUI-09": "Học phí tính theo tín chỉ của ngành Kinh doanh quốc tế chương trình CLC khóa 49 là bao nhiêu?",
    "HOUT-TUI-10": "Một tín chỉ ngành Công nghệ kỹ thuật hóa học chất lượng cao khóa 49 mức thu là bao nhiêu?",
    "HOUT-TUI-11": "Ngành Kinh doanh quốc tế chất lượng cao khóa 50 có mức học phí mỗi năm là bao nhiêu?",
    "HOUT-TUI-12": "Cho em hỏi học phí 1 tín chỉ ngành Kỹ thuật điện hệ chuẩn khóa 52 năm học 2026-2027 là bao nhiêu?",
    "HOUT-TUI-13": "Sinh viên ngành Công nghệ thông tin chương trình CLC khóa 49 mỗi năm học phải nộp bao nhiêu học phí?",
    "HOUT-TUI-14": "Mức thu học phí hàng năm của ngành Quản trị kinh doanh chất lượng cao khóa 48 là bao nhiêu?",
    "HOUT-TUI-15": "Học phí một năm của ngành Công nghệ thông tin hệ chất lượng cao khóa 45 là bao nhiêu tiền?",
    "HOUT-TUI-16": "Học phí mỗi tín chỉ ngành Truyền thông đa phương tiện hệ chuẩn khóa 52 là bao nhiêu?",
    "HOUT-TUI-17": "Mức thu học phí một tín chỉ ngành Quản trị Dịch vụ Du lịch và Lữ hành CLC khóa 48 là bao nhiêu?",
    "HOUT-TUI-18": "Học phí mỗi tín chỉ của sinh viên ngành Ngôn ngữ Anh chất lượng cao khóa 45 là bao nhiêu?",
    "HOUT-TUI-19": "Một tín chỉ ngành Kỹ thuật điện chất lượng cao khóa 45 đóng bao nhiêu tiền học phí?",
    "HOUT-TUI-20": "Mức học phí mỗi năm của ngành Kỹ thuật xây dựng chất lượng cao khóa 47 là bao nhiêu?",
    "HOUT-OTHER-04": "Lệ phí để xin cấp một bản sao văn bằng tốt nghiệp đại học là bao nhiêu?",
    "HOUT-SCHOLARSHIP-03": "Theo thông báo xét cấp học bổng tài trợ, sinh viên Đại học Cần Thơ (CTU) được phân bổ bao nhiêu suất học bổng Vallet năm 2026?",
}

def main():
    rows = []
    updated_gold_count = 0
    updated_q_count = 0

    with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            cid = row["id"]

            if cid in GOLD_UPDATES:
                old_gold = row.get("gold_sources", [])
                new_gold = list(dict.fromkeys(GOLD_UPDATES[cid]))
                row["gold_sources"] = new_gold
                updated_gold_count += 1
                print(f"[{cid}] Updated gold: {old_gold} -> {new_gold}")

            if cid in QUESTION_UPDATES:
                old_q = row["question"]
                new_q = QUESTION_UPDATES[cid]
                row["question"] = new_q
                updated_q_count += 1
                print(f"[{cid}] Updated Q: '{old_q}' -> '{new_q}'")

            rows.append(row)

    with open(HELDOUT_PATH, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nDone: Successfully updated {updated_gold_count} gold lists and {updated_q_count} questions in {HELDOUT_PATH}")

if __name__ == "__main__":
    main()
