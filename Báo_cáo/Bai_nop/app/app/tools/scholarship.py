import json
import os
from langchain.tools import tool

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
json_path = os.path.join(PROJECT_ROOT, "data", "hoc_bong.json")

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        HOC_BONG_DATA = json.load(f)
except Exception as e:
    HOC_BONG_DATA = {}

@tool
def tinh_tien_hoc_bong(gpa: float, drl: int, khoi_nganh: str = "") -> str:
    """
    Công cụ này dùng để tính mức học bổng khuyến khích học tập dựa trên Quyết định 3530.
    LUÔN gọi công cụ này khi người dùng cung cấp GPA và ĐRL (Điểm rèn luyện).
    Đầu vào:
    - gpa: Điểm trung bình tích lũy (ví dụ: 3.5, 4.0)
    - drl: Điểm rèn luyện (ví dụ: 79, 90)
    - khoi_nganh: (Tùy chọn) Khối ngành của sinh viên (ví dụ: "Sức khỏe", "CNTT", "Kinh doanh"). Nếu không biết thì để trống "".
    """
    if not HOC_BONG_DATA:
        return "Lỗi: Không tìm thấy hệ thống dữ liệu JSON quy định học bổng."

    dieu_kien = HOC_BONG_DATA.get("dieu_kien", {})
    
    # 1. Xác định loại học bổng (Lấy mức thấp nhất giữa GPA và ĐRL để đồng bộ)
    loai_dat_duoc = None
    if gpa >= dieu_kien["Xuat_sac"]["gpa_min"] and drl >= dieu_kien["Xuat_sac"]["drl_min"]:
        loai_dat_duoc = "Xuat_sac"
    elif gpa >= dieu_kien["Gioi"]["gpa_min"] and drl >= dieu_kien["Gioi"]["drl_min"]:
        loai_dat_duoc = "Gioi"
    elif gpa >= dieu_kien["Kha"]["gpa_min"] and drl >= dieu_kien["Kha"]["drl_min"]:
        loai_dat_duoc = "Kha"
        
    if not loai_dat_duoc:
        return f"Rất tiếc! Với GPA {gpa} và ĐRL {drl}, bạn chưa đủ điều kiện nhận học bổng. (Lưu ý: Để đạt loại Khá cần GPA >= 2.5 và ĐRL >= 65)."

    loai_text = {"Xuat_sac": "Xuất sắc", "Gioi": "Giỏi", "Kha": "Khá"}[loai_dat_duoc]
    
    # 2. Lấy số tiền
    bang_gia = HOC_BONG_DATA.get("bang_gia_tien", {})
    
    result = f"Chúc mừng! Với GPA {gpa} và ĐRL {drl}, bạn đạt học bổng loại **{loai_text}**.\n"
    
    # Nếu user không nói rõ học ngành nào, in ra toàn bộ bảng tiền cho loại đó
    result += f"\nSau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):\n"
    for ma_khoi, thong_tin in bang_gia.items():
        tien = thong_tin[loai_dat_duoc]
        ten_nganh = thong_tin["ten"]
        
        # Nếu user có khai báo khối ngành và khớp, đánh dấu đậm
        prefix = "- "
        if khoi_nganh and khoi_nganh.lower() in ten_nganh.lower():
            prefix = "👉 **(Ngành của bạn) "
            
        result += f"{prefix}Khối {ma_khoi} ({ten_nganh}): {tien} đồng.**\n" if "👉" in prefix else f"{prefix}Khối {ma_khoi} ({ten_nganh}): {tien} đồng.\n"
        
    return result
