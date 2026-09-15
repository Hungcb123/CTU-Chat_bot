#!/usr/bin/env python3
"""Script to generate semantic / student-natural paraphrase benchmark dataset from data/scenario12_heldout.jsonl.

Preserves 100% of ground truth (id, category, reference_answer, raw_evidence,
gold_sources, source_relation, required_facts, query_family, etc.) while
paraphrasing the questions into natural, authentic student phrasing
with vocabulary mismatch to test semantic understanding.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "scenario12_heldout.jsonl"
OUTPUT_PATH = ROOT / "data" / "scenario12_heldout_semantic.jsonl"

# Mapping from case ID to authentic, natural student phrasing
PARAPHRASE_MAP = {
    # Actual tuition (HOUT-TUI-01 to 20)
    "HOUT-TUI-01": "Em muốn theo học ngành Thú y hệ chuẩn K52 thì học phí đóng trọn gói từ đầu tới lúc tốt nghiệp ra trường hết bao nhiêu tiền ạ?",
    "HOUT-TUI-02": "Cho em hỏi học phí nguyên khóa cho ngành Kỹ thuật y sinh hệ chuẩn khóa 52 năm học tới tính tổng cộng là bao nhiêu tiền?",
    "HOUT-TUI-03": "Sinh viên mới trúng tuyển ngành Kỹ thuật xây dựng công trình thủy hệ chuẩn K52 thì học hết khóa ra trường tốn bao nhiêu học phí ạ?",
    "HOUT-TUI-04": "Em học Công nghệ sinh học hệ tiên tiến K52 thì trung bình mỗi năm đóng khoảng bao nhiêu tiền học phí vậy mọi người?",
    "HOUT-TUI-05": "Mấy anh chị khóa trước cho em hỏi Nuôi trồng thủy sản hệ tiên tiến K49 thì đăng ký mỗi tín chỉ tính giá bao nhiêu tiền vậy ạ?",
    "HOUT-TUI-06": "Ngành Quản lý xây dựng hệ chuẩn khóa 52 thì trường thu tiền học phí một tín chỉ là bao nhiêu thế ạ?",
    "HOUT-TUI-07": "Cho em hỏi sinh viên ngành Tự động hóa hệ chuẩn khóa 52 thì mỗi chỉ học phí phải đóng bao nhiêu tiền ạ?",
    "HOUT-TUI-08": "Học Tài chính Ngân hàng lớp chất lượng cao khóa 49 thì một năm học phải nộp bao nhiêu tiền học phí vậy ạ?",
    "HOUT-TUI-09": "Học phí tính trên từng tín chỉ của ngành Kinh doanh quốc tế hệ CLC khóa 49 là bao nhiêu thế mọi người?",
    "HOUT-TUI-10": "Tiền học phí 1 tín chỉ của ngành Hóa học CLC khóa 49 thu bao nhiêu tiền vậy ạ?",
    "HOUT-TUI-11": "Mỗi năm học sinh viên Kinh doanh quốc tế chương trình CLC K50 phải đóng bao nhiêu tiền học phí vậy ạ?",
    "HOUT-TUI-12": "Sinh viên ngành Kỹ thuật điện lớp chuẩn K52 năm học 2026-2027 thì đóng tiền học phí một chỉ là bao nhiêu?",
    "HOUT-TUI-13": "Ngành CNTT chất lượng cao khóa 49 thì tiền học phí nguyên một năm học là bao nhiêu vậy anh chị?",
    "HOUT-TUI-14": "Tiền học phí đóng mỗi năm của sinh viên Quản trị kinh doanh hệ CLC khóa 48 là bao nhiêu tiền vậy ạ?",
    "HOUT-TUI-15": "Sinh viên Công nghệ thông tin hệ CLC khóa 45 đóng học phí một năm học là bao nhiêu?",
    "HOUT-TUI-16": "Một chỉ học phí của ngành Truyền thông đa phương tiện lớp chuẩn K52 là bao nhiêu tiền vậy ạ?",
    "HOUT-TUI-17": "Sinh viên ngành Du lịch và Lữ hành hệ CLC khóa 48 đóng học phí mỗi tín chỉ là bao nhiêu?",
    "HOUT-TUI-18": "Cho em hỏi tiền học phí tính theo từng tín chỉ của ngành Ngôn ngữ Anh CLC K45 là bao nhiêu ạ?",
    "HOUT-TUI-19": "Học phí 1 tín chỉ ngành Kỹ thuật điện lớp chất lượng cao khóa 45 quy định đóng bao nhiêu vậy ạ?",
    "HOUT-TUI-20": "Học phí tính theo từng năm học của ngành Xây dựng hệ CLC khóa 47 là bao nhiêu tiền thế ạ?",

    # Academic rules (HOUT-ACADEMIC-RULES-01 to 06)
    "HOUT-ACADEMIC-RULES-01": "Nếu em đi thi Robocon hoặc thi Olympic cấp quốc gia thì trường mình cho miễn thi và quy đổi điểm tối đa được mấy môn học vậy ạ?",
    "HOUT-ACADEMIC-RULES-02": "Ngành em học bình thường là 4 năm rưỡi thì nhà trường cho phép học kéo dài dây dưa tối đa mấy năm là bị đuổi học vậy ạ?",
    "HOUT-ACADEMIC-RULES-03": "Trong một năm thì trường mình thường tổ chức xét công nhận tốt nghiệp cho sinh viên vào những đợt hay thời gian nào thế ạ?",
    "HOUT-ACADEMIC-RULES-04": "Em từng bị trường kỷ luật đình chỉ học một thời gian, giờ muốn nộp đơn xin đi học lại thì áp dụng trong trường hợp cụ thể ra sao ạ?",
    "HOUT-ACADEMIC-RULES-05": "Em bị ốm nặng phải nằm viện điều trị dài ngày thì cần nộp những giấy tờ bệnh viện gì để làm thủ tục bảo lưu tạm nghỉ học ạ?",
    "HOUT-ACADEMIC-RULES-06": "Em muốn nộp đơn xin chuyển ngành học bằng điểm xét học bạ thì cần chuẩn bị những giấy tờ hồ sơ nào để chứng minh vậy ạ?",

    # Scholarship (HOUT-SCHOLARSHIP-01 to 05)
    "HOUT-SCHOLARSHIP-01": "Sinh viên mới vô học kỳ đầu tiên đạt học bổng khuyến khích học tập thì bình quân được nhận bao nhiêu tiền vậy ạ?",
    "HOUT-SCHOLARSHIP-02": "Tân sinh viên K52 nộp học bổng Thắp sáng Niềm Tin thì một năm nhận được tối đa bao nhiêu tiền và gồm những khoản chi phí nào hỗ trợ?",
    "HOUT-SCHOLARSHIP-03": "Đợt học bổng tài trợ Vallet năm 2026 thì sinh viên trường mình được chia tổng cộng bao nhiêu suất vậy ạ?",
    "HOUT-SCHOLARSHIP-04": "Bên quỹ SCIC trao cho sinh viên khoa CNTT trường mình bao nhiêu suất học bổng năm 2026 và mỗi bạn nhận được bao nhiêu tiền?",
    "HOUT-SCHOLARSHIP-05": "Sinh viên thuộc Khối V đạt xếp loại học tập loại Giỏi thì mỗi kỳ được lãnh học bổng khuyến khích bao nhiêu tiền vậy ạ?",

    # Student loan (HOUT-STUDENT-LOAN-01 to 04)
    "HOUT-STUDENT-LOAN-01": "Sinh viên muốn vay vốn chính sách ngân hàng chính sách xã hội đi học thì theo quy định mới nhất mỗi bạn được vay tối đa bao nhiêu tiền?",
    "HOUT-STUDENT-LOAN-02": "Theo chính sách hỗ trợ chi phí sinh hoạt mới nhất thì hàng tháng sinh viên được nhận tối đa bao nhiêu tiền sinh hoạt phí vậy ạ?",
    "HOUT-STUDENT-LOAN-03": "Gia đình em khó khăn muốn vay vốn ngân hàng chính sách để sắm laptop học tập thì được vay tối đa bao nhiêu tiền thế ạ?",
    "HOUT-STUDENT-LOAN-04": "Làm thế nào để lên trang quản lý sinh viên của trường đăng ký in cái giấy xác nhận vay vốn ngân hàng, các bước làm như thế nào vậy ạ?",

    # Social support (HOUT-SOCIAL-SUPPORT-01 to 04)
    "HOUT-SOCIAL-SUPPORT-01": "Em là sinh viên người dân tộc thiểu số thì phải thuộc những trường hợp hay hoàn cảnh nào mới được nhận tiền hỗ trợ chi phí học tập của trường ạ?",
    "HOUT-SOCIAL-SUPPORT-02": "Năm 2024 em đã từng lãnh tiền hỗ trợ học tập rồi thì sang năm 2025 đợt 3 này cần bổ sung những giấy tờ gì để được nhận tiếp ạ?",
    "HOUT-SOCIAL-SUPPORT-03": "Hoàn cảnh em mồ côi cha mẹ không có ai nuôi dưỡng thì cần nộp những giấy tờ chứng nhận gì để xin tiền trợ cấp xã hội của trường vậy ạ?",
    "HOUT-SOCIAL-SUPPORT-04": "Sinh viên nhà nghèo, mồ côi hoặc bị khuyết tật nặng thì trường hỗ trợ tiền trợ cấp xã hội mỗi tháng bao nhiêu và được hưởng trong mấy tháng ạ?",

    # Other (HOUT-OTHER-01 to 04)
    "HOUT-OTHER-01": "Ở trong phòng ký túc xá của trường thì sinh viên có được phép lập bàn thờ hay để bát hương cúng bái không vậy ạ?",
    "HOUT-OTHER-02": "Nếu em cần nhờ xử lý các vấn đề về tài khoản sinh viên hay hòm thư email của trường thì Trung tâm Chuyển đổi số có nhiệm vụ gì hỗ trợ ạ?",
    "HOUT-OTHER-03": "Em nộp đơn xin cấp bảng điểm tốt nghiệp xong xuôi hết rồi thì thường phải chờ khoảng mấy ngày mới có bảng điểm lấy vậy ạ?",
    "HOUT-OTHER-04": "Xin cấp lại bản sao bằng tốt nghiệp đại học thì nhà trường thu lệ phí bao nhiêu tiền một bản thế ạ?",

    # Academic program (HOUT-ACADEMIC-PROGRAM-01 to 03)
    "HOUT-ACADEMIC-PROGRAM-01": "Ngành Trí tuệ nhân tạo của trường mình từ lúc nhập học tới khi ra trường phải tích lũy đủ tổng cộng bao nhiêu tín chỉ vậy ạ?",
    "HOUT-ACADEMIC-PROGRAM-02": "Học ngành Logistics và Chuỗi cung ứng thì toàn bộ khung chương trình đào tạo có tất cả bao nhiêu tín chỉ thế mọi người?",
    "HOUT-ACADEMIC-PROGRAM-03": "Ngành Đảm bảo chất lượng và An toàn thực phẩm thì trong khung chương trình có bao nhiêu tín chỉ thuộc phần học phần bắt buộc ạ?",

    # Exemption policy & basis (HOUT-EXEMPTION-POLICY-01 to 02, HOUT-EXEMPTION-BASIS-01 to 02)
    "HOUT-EXEMPTION-POLICY-01": "Sinh viên thuộc diện nào mà bản thân và gia đình thuộc hộ nghèo hoặc cận nghèo thì được trường xét miễn toàn bộ 100% học phí vậy ạ?",
    "HOUT-EXEMPTION-POLICY-02": "Làm xong cái đơn xin miễn giảm học phí theo mẫu rồi thì sinh viên phải mang nộp cho phòng ban hay cơ quan nào vậy mọi người?",
    "HOUT-EXEMPTION-BASIS-01": "Trường mình quy định mức học phí cơ sở để tính tiền miễn giảm cho sinh viên thuộc Khối ngành IV năm học 2025-2026 là bao nhiêu vậy ạ?",
    "HOUT-EXEMPTION-BASIS-02": "Môn Giáo dục quốc phòng an ninh thì trường lấy mức học phí cơ sở để tính miễn giảm là bao nhiêu tiền cho 1 tín chỉ thế ạ?",
}


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(cases)} cases from {INPUT_PATH.name}")

    paraphrased_count = 0
    new_cases = []
    for case in cases:
        cid = case["id"]
        if cid in PARAPHRASE_MAP:
            orig_q = case["question"]
            new_q = PARAPHRASE_MAP[cid]
            case_copy = dict(case)
            case_copy["question"] = new_q
            case_copy["original_question"] = orig_q
            case_copy["is_semantic_paraphrase"] = True
            new_cases.append(case_copy)
            paraphrased_count += 1
        else:
            raise ValueError(f"Missing paraphrase for case ID: {cid}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for case in new_cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    print(f"Successfully generated {paraphrased_count} semantic cases in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
