# Kiểm Toán Độc Lập Distractor Registry v3 (Scenario 3 Scalability)

Tài liệu kiểm toán này đánh giá tính hợp lệ của 16 synthetic distractor tools trong [scenario3_distractor_registry_v3.json](file:///mnt/d/Project/Chatbot/data/scenario3_distractor_registry_v3.json) nhằm phục vụ thí nghiệm mở rộng quy mô công cụ (11, 19, 27 tools) theo Mục 5.4 của [PLAN_SCENARIO3_TOOL_SCALABILITY_11_19_27.md](file:///mnt/d/Project/Chatbot/docs/PLAN_SCENARIO3_TOOL_SCALABILITY_11_19_27.md).

---

## 1. Tiêu Chuẩn Kiểm Toán
1. **Zero Disclosure Metadata:** Mô tả hiển thị cho model tuyệt đối không chứa các từ khóa nhạy cảm: `synthetic`, `distractor`, `fake`, `giả lập`, `stress test`, `benchmark-only`.
2. **Business Plausibility:** Tên công cụ, mô tả và tham số bám sát các nghiệp vụ hành chính/đào tạo thường nhật tại trường đại học.
3. **Orthogonality to Gold Cases:** Xác nhận không có câu hỏi nào trong 60 production cases (`ACA-01` đến `ACA-30`, `FIN-01` đến `FIN-20`, `SCH-01` đến `SCH-05`, `NT-01` đến `NT-05`) mà distractor mới thực sự là câu trả lời đúng hơn gold production tool.
4. **Schema Parity:** Tham số có kiểu dữ liệu rõ ràng (`string`, `number`, `integer`), mô tả cụ thể, tương đương với production tools.

---

## 2. Ma Trận Đánh Giá 16 Distractor Tools

| STT | Distractor Tool Name | Domain | Closest Production Tool | Vì sao Plausible (Hợp lý nghiệp vụ) | Vì sao không đúng cho 60 Gold Cases | Schema Parity |
|---|---|---|---|---|---|---|
| 1 | `tra_cuu_nganh_tuyen_sinh` | Academic | `tra_cuu_nganh` | Đề án tuyển sinh, tổ hợp môn thi là nhu cầu phổ biến của thí sinh | 60 cases chỉ hỏi về chương trình đào tạo hiện hành, mã ngành, văn bằng, không hỏi đề án tuyển sinh | `ten_nganh: string` |
| 2 | `tim_nganh_theo_diem_chuan` | Academic | `tim_nganh` | Thí sinh thường tra cứu ngành theo điểm thi THPT | Các case `tim_nganh` chỉ tìm theo từ khóa lĩnh vực (kinh doanh, kỹ thuật, nông nghiệp), không có điểm số | `diem_chuan: number` |
| 3 | `tra_cuu_mon_tuong_duong` | Academic | `xem_chuoi_tien_quyet` | Sinh viên thường hỏi môn tương đương khi cải thiện điểm | Các case chỉ hỏi môn tiên quyết hoặc môn học trước (`prerequisite`), không hỏi môn thay thế tương đương | `ma_mon: string` |
| 4 | `tra_cuu_lich_hoc` | Academic | `tim_nganh_co_mon` | Sinh viên hỏi thời khóa biểu lớp học phần mở trong kỳ | Các case chỉ hỏi ngành nào dạy môn X, không hỏi lịch học hay giảng đường | `ma_mon: string` |
| 5 | `tra_cuu_hoc_phi_sau_dai_hoc` | Financial | `tra_cuu_hoc_phi_graph` | Mức học phí thạc sĩ/tiến sĩ là nghiệp vụ tài chính thực tế | Các case học phí chỉ hỏi hệ đại học chính quy (khóa K50, K51, K52) hoặc quy chế chung, case `FIN-13` hỏi quy định thạc sĩ nhưng expected tool là `tra_cuu_quy_dinh_hoc_phi` | `chuyen_nganh: string` |
| 6 | `tinh_hoc_phi_hoc_lai` | Financial | `tinh_toan_hoc_phi` | Tính tiền học lại theo số tín chỉ là nghiệp vụ phổ biến | Các case `tinh_toan_hoc_phi` (`FIN-16` đến `FIN-20`) chỉ tính tiền miễn giảm (% giảm trên mức trần cơ sở), không tính học lại | `so_tin_chi: integer, khoi_nganh: string` |
| 7 | `tra_cuu_hoan_hoc_phi` | Financial | `tra_cuu_quy_dinh_hoc_phi` | Thủ tục rút học phí khi thôi học là nghiệp vụ tài chính | 60 cases không có câu hỏi nào yêu cầu thủ tục hoàn trả học phí cho cá nhân | `ma_sinh_vien: string` |
| 8 | `tra_cuu_cong_no` | Financial | `tra_cuu_hoc_phi_graph` | Sinh viên kiểm tra nợ học phí cá nhân | 60 cases chỉ hỏi mức biểu phí chung của ngành, không có case tra cứu công nợ sinh viên | `ma_sinh_vien: string` |
| 9 | `tra_cuu_hoc_bong_doanh_nghiep`| Scholarship | `tinh_tien_hoc_bong` | Học bổng tài trợ doanh nghiệp là mảng lớn của phòng CTSV | Các case `SCH-01` đến `SCH-05` chỉ tính học bổng khuyến khích học tập (KKHT) theo GPA và ĐRL | `ten_hoc_bong: string` |
| 10 | `kiem_tra_dieu_kien_hoc_bong` | Scholarship | `tinh_tien_hoc_bong` | Kiểm tra hồ sơ ứng tuyển học bổng | Các case chỉ đưa GPA + ĐRL để tính mức tiền (Xuất sắc/Giỏi/Khá), không hỏi danh mục giấy tờ | `ten_quy: string` |
| 11 | `tra_cuu_han_nop_hoc_bong` | Scholarship | `tinh_tien_hoc_bong` | Sinh viên cần biết mốc thời gian nộp hồ sơ | Không có câu hỏi nào trong 60 cases hỏi về hạn chót nộp học bổng | `ten_chuong_trinh: string` |
| 12 | `tinh_ho_tro_sinh_vien` | Scholarship | `tinh_tien_hoc_bong` | Tính tiền trợ cấp xã hội (Nghị định 116 / Nghị định 60) | Case hỗ trợ xã hội nằm ở tập robustness (`F06`), không nằm trong 5 gold scholarship cases | `dien_chinh_sach: string` |
| 13 | `tra_cuu_ky_tuc_xa` | General | `no_tool` | Thông tin phòng ở KTX là dịch vụ sinh viên cốt lõi | 5 case no-tool chỉ là chào hỏi (`NT-01`, `NT-02`), thời tiết (`NT-03`), mơ hồ (`NT-04`, `NT-05`), không hỏi KTX | `loai_phong: string` |
| 14 | `tra_cuu_bao_hiem_y_te` | General | `no_tool` | Bảo hiểm y tế bắt buộc của sinh viên | Không có câu hỏi nào trong 60 cases hỏi về bảo hiểm y tế | `ma_sinh_vien: string` |
| 15 | `tra_cuu_vay_von` | General | `no_tool` | Vay vốn tín dụng đào tạo chính sách | Không có câu hỏi nào trong 60 cases hỏi thủ tục vay vốn | `doi_tuong_vay: string` |
| 16 | `tra_cuu_quy_che_sinh_vien` | General | `no_tool` | Quy chế rèn luyện, khen thưởng, kỷ luật | Các câu hỏi quy chế thuộc về văn bản RAG, 5 case General đều là `no_tool` thuần túy | `tu_khoa: string` |

---

## 3. Kết Luận Kiểm Toán
- **16/16 Tools đạt chuẩn:** Không trùng tên với bất kỳ production tool nào; không chứa từ ngữ tiết lộ; không xâm lấn phạm vi của 60 gold cases.
- **Nested Structure hợp lệ:** 
  - Level 0 (11 tools): 0 distractors.
  - Level 2 (19 tools): 2 distractors đầu mỗi domain (8 distractors).
  - Level 4 (27 tools): cả 4 distractors mỗi domain (16 distractors).
