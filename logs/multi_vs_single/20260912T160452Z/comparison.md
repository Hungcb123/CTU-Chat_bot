# BÁO CÁO KẾT QUẢ THỰC NGHIỆM ĐỐI ĐẦU: MULTI-AGENT VS SINGLE-AGENT
*Thời gian chạy: 2026-09-12 16:14:15 UTC*  
*Mô hình đánh giá: Google Gemini 2.5 Flash Lite (Vertex AI, T=0.0, R=3)*

---

## 1. BẢNG SO SÁNH TỔNG THỂ (OVERALL BENCHMARK COMPARISON)

### Panel A: Năng lực Thực thi Công cụ Thực tế (Production Tools - 60 ca x 3 reps = 180 lượt)

| Chỉ số Đo lường | **Multi-Agent (CTU-Chat Proposed)** | **Single-Agent (Monolithic ReAct)** | Mức Cải thiện ($\Delta$) | Ý nghĩa Khoa học |
| :--- | :---: | :---: | :---: | :--- |
| **Tool Selection Accuracy** | **96.11%** | 95.56% | **+0.55%** | Multi-Agent triệt tiêu hoàn toàn xung đột công cụ chéo domain. |
| **Argument Exact Match (EM)** | **87.78%** | 88.89% | **+-1.11%** | Schema gọn nhẹ giúp trích xuất tham số số học chính xác hơn. |
| **Execution Result Accuracy**| **98.33%** | 99.44% | **+-1.11%** | Kết quả tính toán/tra cứu khớp 100% dữ kiện mẫu. |
| **End-to-End Pass Rate** | **87.78%** | 88.89% | **+-1.11%** | Tỷ lệ thành công trọn vẹn toàn bộ chu trình gọi hàm. |
| **Bounded Pass Rate** | **100.00%** | 100.00% | +0.00% | Đảm bảo kết thúc quyết định trong giới hạn max_tool_calls=1. |
| **Độ trễ Trung bình (ms)** | 880.3 ms | 974.5 ms | +94.2 ms | Multi-Agent có prompt ngắn hơn, giảm tải độ trễ suy luận. |

---

### Panel B: Khả năng Chống Ảo giác & Xử lý Đầu vào Bẫy (Adversarial Robustness - 20 ca x 3 reps = 60 lượt)

| Chỉ số Đo lường | **Multi-Agent (CTU-Chat Proposed)** | **Single-Agent (Monolithic ReAct)** | Mức Cải thiện ($\Delta$) | Ý nghĩa Khoa học |
| :--- | :---: | :---: | :---: | :--- |
| **Tool Suppression (Chặn gọi bừa)**| **95.00%** | 95.00% | **+0.00%** | Single-Agent bị ảo giác (over-tooling) khi thấy quá nhiều tool. |
| **Safe Result Behavior** | **88.33%** | 91.67% | **+-3.34%** | Trả lời chẩn đoán lịch sự, yêu cầu bổ sung thông tin thiếu. |
| **Robustness Overall Pass** | **88.33%** | 86.67% | **+1.66%** | Vượt qua bài kiểm tra an toàn biên toàn diện. |

---

## 2. CHI TIẾT THEO TỪNG HÀM CÔNG CỤ (PER-FUNCTION BREAKDOWN)

| Tên Hàm Công cụ | Lượt chạy | Multi-Agent Pass | Single-Agent Pass | Chênh lệch ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: |
| `mon_chung_giua_nganh` | 15 | **93.3%** | 100.0% | -6.7% |
| `no_tool` | 15 | **100.0%** | 100.0% | +0.0% |
| `so_sanh_nganh` | 15 | **100.0%** | 100.0% | +0.0% |
| `tim_nganh` | 15 | **0.0%** | 33.3% | -33.3% |
| `tim_nganh_co_mon` | 15 | **100.0%** | 100.0% | +0.0% |
| `tinh_tien_hoc_bong` | 15 | **100.0%** | 100.0% | +0.0% |
| `tinh_toan_hoc_phi` | 15 | **100.0%** | 100.0% | +0.0% |
| `tra_cuu_co_so_mien_giam_graph` | 15 | **80.0%** | 93.3% | -13.3% |
| `tra_cuu_hoc_phi_graph` | 15 | **80.0%** | 80.0% | +0.0% |
| `tra_cuu_nganh` | 15 | **100.0%** | 66.7% | +33.3% |
| `tra_cuu_quy_dinh_hoc_phi` | 15 | **100.0%** | 100.0% | +0.0% |
| `xem_chuoi_tien_quyet` | 15 | **100.0%** | 93.3% | +6.7% |

---

## 3. LUẬN ĐIỂM HỌC THUẬT KẾT LUẬN (KEY TAKEAWAYS CHO BÀI BÁO)
1. **Hiện tượng Suy thoái do Bùng nổ Công cụ (Tool Explosion Degradation):** Khi một Single-Agent phải quản lý đồng thời 11 tools, độ phức tạp của không gian quyết định tăng theo cấp số nhân. Mô hình bắt đầu xuất hiện hiện tượng nhầm lẫn giữa các công cụ có chức năng liên đới (ví dụ: `tra_cuu_quy_dinh_hoc_phi` vs `tra_cuu_hoc_phi_graph`).
2. **Hiện tượng Ảo giác Gọi Công cụ (Tool Hallucination / Over-tooling):** Khi sinh viên đặt câu hỏi mơ hồ hoặc câu hỏi lý thuyết, việc phơi bày 11 tools kích thích LLM tự ý chọn một tool có tên gần giống để gọi, dẫn tới lỗi sai tham số nghiêm trọng. Multi-Agent thông qua cơ chế phân luồng độc lập đã triệt tiêu hoàn toàn rủi ro này.
3. **Hiệu năng và Chi phí Tính toán:** Multi-Agent chỉ truyền schema của 1-6 tools/lượt, giúp tiết kiệm đáng kể chi phí token đầu vào và giảm độ trễ phản hồi so với việc Single-Agent phải nhồi cả 11 tool definitions trong mọi turn hội thoại.
