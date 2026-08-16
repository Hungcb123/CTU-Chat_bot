from langchain.tools import tool

@tool
def tinh_toan_hoc_phi(gia_hoc_phi_thuc_te: float, muc_tran_mien_giam: float, phan_tram_giam: float) -> str:
    """
    Công cụ tính số tiền còn lại sau khi áp dụng phần trăm giảm giá (Dùng để tính số tiền miễn giảm học phí).
    Đầu vào:
    - gia_hoc_phi_thuc_te: Giá tiền gốc thực tế phải đóng của 1 tín chỉ (Ví dụ: 832000, 695000). Đọc từ tài liệu về Mức học phí.
    - muc_tran_mien_giam: Mức học phí làm cơ sở để tính miễn giảm của Khối ngành đó (Ví dụ: 538000, 451000). Đọc từ tài liệu "cơ sở tính miễn giảm".
    - phan_tram_giam: Phần trăm được giảm dựa vào diện đối tượng (Ví dụ: 70, 100). Đừng để dấu %, chỉ điền số.
    """
    try:
        gia_hoc_phi_thuc_te = float(gia_hoc_phi_thuc_te)
        muc_tran_mien_giam = float(muc_tran_mien_giam)
        phan_tram_giam = float(phan_tram_giam)
        
        if phan_tram_giam < 0 or phan_tram_giam > 100:
            return "Lỗi: Phần trăm giảm phải nằm trong khoảng từ 0 đến 100."
            
        tien_duoc_giam = muc_tran_mien_giam * (phan_tram_giam / 100)
        tien_phai_dong = gia_hoc_phi_thuc_te - tien_duoc_giam
        
        if tien_phai_dong < 0:
            tien_phai_dong = 0
            
        return f"Học phí thực tế: {int(gia_hoc_phi_thuc_te):,}đ/tín chỉ.\nMức trần (cơ sở miễn giảm): {int(muc_tran_mien_giam):,}đ/tín chỉ.\nSố tiền được Nhà nước miễn giảm ({phan_tram_giam}% x {int(muc_tran_mien_giam):,}): {int(tien_duoc_giam):,}đ/tín chỉ.\n=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: {int(tien_phai_dong):,}đ/tín chỉ.".replace(",", ".")
    except Exception as e:
        return f"Lỗi tính toán: {str(e)}"
