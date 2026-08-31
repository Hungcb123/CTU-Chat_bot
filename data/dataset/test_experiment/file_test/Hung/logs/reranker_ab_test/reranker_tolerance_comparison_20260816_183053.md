# So sánh 3 cấu hình reranker: Plain vs Tie-break 0.05 vs Tie-break 0.02

- Thời điểm: `2026-08-16T18:30:53.309524+07:00`
- JSONL 0.05: `reranker_ab_test_merged_20260816_181356.jsonl`
- JSONL 0.02: `reranker_ab_20260816_182408.jsonl`
- Số câu so sánh: **100** (RAG active: 80, bypass catalog: 20)
- Kiểm tra nhất quán plain giữa 2 run: 0 mismatch

## Tổng quan

| Chỉ số | Plain (B) | Tie-break 0.05 (A) | Tie-break 0.02 (A') |
|---|---:|---:|---:|
| Hit (expected source trong top docs) | 80/80 (100.00%) | 80/80 (100.00%) | 80/80 (100.00%) |
| Avg rank expected source | 1.18 | 1.27 | 1.24 |

### So với plain (thay đổi rank của expected source)

| So với plain | Tie-break 0.05 | Tie-break 0.02 |
|---|---:|---:|
| Có rank khác plain | 7 | 6 |
| Rank tốt hơn | 1 | 2 |
| Rank tệ hơn | 6 | 4 |
| Rank bằng | 73 | 74 |

### Chuyển đổi từ 0.05 -> 0.02

| Trạng thái | Số câu |
|---|---:|
| 0.05 đổi rank nhưng 0.02 đã khôi phục = plain (tốt) | 2 |
| 0.05 và 0.02 đều còn khác plain (0.02 chưa khử hết) | 5 |
| 0.05 bằng plain nhưng 0.02 mới tạo khác biệt (xấu) | 1 |

## Chi tiết từng câu khác biệt

### Câu 16 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `66_2013.md`
- Câu hỏi: Em là sinh viên dân tộc thiểu số thuộc hộ nghèo thì được hỗ trợ chi phí học tập bao nhiêu?
- Plain: Plain (hit=True, rank=1)
- Tie 0.05: Tie 0.05 (hit=True, rank=2)
- Tie 0.02: Tie 0.02 (hit=True, rank=1)

---

### Câu 18 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `66_2013.md`
- Câu hỏi: Sinh viên học văn bằng hai có được nhận hỗ trợ chi phí học tập dành cho sinh viên dân tộc thiểu số thuộc hộ nghèo không?
- Plain: Plain (hit=True, rank=5)
- Tie 0.05: Tie 0.05 (hit=True, rank=6)
- Tie 0.02: Tie 0.02 (hit=True, rank=5)

---

### Câu 22 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `donz.md`
- Câu hỏi: Sinh viên dân tộc thiểu số thuộc hộ nghèo muốn nộp hồ sơ hỗ trợ chi phí học tập thì nộp trực tiếp ở đâu?
- Plain: Plain (hit=True, rank=1)
- Tie 0.05: Tie 0.05 (hit=True, rank=3)
- Tie 0.02: Tie 0.02 (hit=True, rank=3)

---

### Câu 25 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `Ho_tro.md`
- Câu hỏi: Sinh viên được hỗ trợ chi phí đào tạo dành cho vùng đồng bào dân tộc thiểu số thì nộp hồ sơ ở đâu?
- Plain: Plain (hit=True, rank=2)
- Tie 0.05: Tie 0.05 (hit=True, rank=2)
- Tie 0.02: Tie 0.02 (hit=True, rank=1)

---

### Câu 26 · Học phí

- Intent: `actual_tuition` | Nguồn kỳ vọng: `MucHocPhi_QuyDinhChung.md`
- Câu hỏi: Mức học phí đại cương chung của ngành CNTT đối với Khóa 49 là bao nhiêu?
- Plain: Plain (hit=True, rank=3)
- Tie 0.05: Tie 0.05 (hit=True, rank=6)
- Tie 0.02: Tie 0.02 (hit=True, rank=6)

---

### Câu 65 · Vay vốn

- Intent: `student_loan` | Nguồn kỳ vọng: `NDCP_VayVonSVKT.md`
- Câu hỏi: Lãi suất nợ quá hạn của các chương trình vay vốn sinh viên là bao nhiêu?
- Plain: Plain (hit=True, rank=2)
- Tie 0.05: Tie 0.05 (hit=True, rank=1)
- Tie 0.02: Tie 0.02 (hit=True, rank=1)

---

### Câu 94 · Học bổng

- Intent: `scholarship` | Nguồn kỳ vọng: `HB_SCIC_2026.md`
- Câu hỏi: Học bổng SCIC - Nâng bước tài năng trẻ năm 2026 dành cho sinh viên trường nào của Đại học Cần Thơ?
- Plain: Plain (hit=True, rank=1)
- Tie 0.05: Tie 0.05 (hit=True, rank=2)
- Tie 0.02: Tie 0.02 (hit=True, rank=2)

---

### Câu 100 · Học bổng

- Intent: `scholarship` | Nguồn kỳ vọng: `HB_Vallet_Chi_Tiet.md`
- Câu hỏi: Đăng ký hồ sơ dự tuyển học bổng Vallet được thực hiện qua hình thức nào?
- Plain: Plain (hit=True, rank=1)
- Tie 0.05: Tie 0.05 (hit=True, rank=2)
- Tie 0.02: Tie 0.02 (hit=True, rank=2)

---
