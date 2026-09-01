# So sánh 4 cấu hình reranker: Plain vs Tie-break 0.05 / 0.02 / 0.01

- Thời điểm: `2026-08-16T19:03:16.803875+07:00`
- jsonl_005: `reranker_ab_test_merged_20260816_181356.jsonl`
- jsonl_002: `reranker_ab_20260816_182408.jsonl`
- jsonl_001: `reranker_ab_20260816_183617.jsonl`
- Số câu so sánh (RAG active): **80**

> Vị trí (position fraction): `(rank-1)/(n_docs-1)`, 0=đầu context, 1=cuối. Trọng số attention hình chữ U: đầu=1.0, giữa=0.5, cuối=0.85 (tham khảo Liu et al. 2024).

## Tổng quan

| Chỉ số | Plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |
|---|---:|---:|---:|---:|
| Hit (expected source trong top docs) | 80/80 (100.00%) | 80/80 (100.00%) | 80/80 (100.00%) | 80/80 (100.00%) |
| Avg rank expected source | 1.18 | 1.27 | 1.24 | 1.21 |
| Avg attention weight (lost-in-middle proxy) | 0.938 | 0.927 | 0.936 | 0.948 |

### So với plain (thay đổi rank của expected source)

| So với plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |
|---|---:|---:|---:|
| Rank khác plain: tốt hơn / tệ hơn / bằng | 1 / 6 / 73 |
| Rank khác plain: tốt hơn / tệ hơn / bằng | 2 / 4 / 74 |
| Rank khác plain: tốt hơn / tệ hơn / bằng | 2 / 2 / 76 |

### Attention (lost-in-the-middle) so với plain

| So với plain | Tie 0.05 | Tie 0.02 | Tie 0.01 |
|---|---:|---:|---:|
| Attention tốt hơn / kém hơn / bằng | 3 / 4 / 73 |
| Attention tốt hơn / kém hơn / bằng | 3 / 3 / 74 |
| Attention tốt hơn / kém hơn / bằng | 3 / 1 / 76 |

## Chi tiết từng câu khác biệt

### Câu 16 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `66_2013.md`
- Câu hỏi: Em là sinh viên dân tộc thiểu số thuộc hộ nghèo thì được hỗ trợ chi phí học tập bao nhiêu?
- Plain (B): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.05 (A): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.02 (A'): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.01 (A''): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00

---

### Câu 18 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `66_2013.md`
- Câu hỏi: Sinh viên học văn bằng hai có được nhận hỗ trợ chi phí học tập dành cho sinh viên dân tộc thiểu số thuộc hộ nghèo không?
- Plain (B): hit=True, rank=5, n_docs=6, pos=0.80, attn=0.50
- Tie 0.05 (A): hit=True, rank=6, n_docs=6, pos=1.00, attn=0.85
- Tie 0.02 (A'): hit=True, rank=5, n_docs=6, pos=0.80, attn=0.50
- Tie 0.01 (A''): hit=True, rank=5, n_docs=6, pos=0.80, attn=0.50

---

### Câu 22 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `donz.md`
- Câu hỏi: Sinh viên dân tộc thiểu số thuộc hộ nghèo muốn nộp hồ sơ hỗ trợ chi phí học tập thì nộp trực tiếp ở đâu?
- Plain (B): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.05 (A): hit=True, rank=3, n_docs=6, pos=0.40, attn=0.50
- Tie 0.02 (A'): hit=True, rank=3, n_docs=6, pos=0.40, attn=0.50
- Tie 0.01 (A''): hit=True, rank=3, n_docs=6, pos=0.40, attn=0.50

---

### Câu 25 · Miễn giảm học phí & Hỗ trợ chi phí học tập

- Intent: `social_support` | Nguồn kỳ vọng: `Ho_tro.md`
- Câu hỏi: Sinh viên được hỗ trợ chi phí đào tạo dành cho vùng đồng bào dân tộc thiểu số thì nộp hồ sơ ở đâu?
- Plain (B): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.05 (A): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.02 (A'): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.01 (A''): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00

---

### Câu 26 · Học phí

- Intent: `actual_tuition` | Nguồn kỳ vọng: `MucHocPhi_QuyDinhChung.md`
- Câu hỏi: Mức học phí đại cương chung của ngành CNTT đối với Khóa 49 là bao nhiêu?
- Plain (B): hit=True, rank=3, n_docs=6, pos=0.40, attn=0.50
- Tie 0.05 (A): hit=True, rank=6, n_docs=6, pos=1.00, attn=0.85
- Tie 0.02 (A'): hit=True, rank=6, n_docs=6, pos=1.00, attn=0.85
- Tie 0.01 (A''): hit=True, rank=6, n_docs=6, pos=1.00, attn=0.85

---

### Câu 65 · Vay vốn

- Intent: `student_loan` | Nguồn kỳ vọng: `NDCP_VayVonSVKT.md`
- Câu hỏi: Lãi suất nợ quá hạn của các chương trình vay vốn sinh viên là bao nhiêu?
- Plain (B): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.05 (A): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.02 (A'): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.01 (A''): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00

---

### Câu 94 · Học bổng

- Intent: `scholarship` | Nguồn kỳ vọng: `HB_SCIC_2026.md`
- Câu hỏi: Học bổng SCIC - Nâng bước tài năng trẻ năm 2026 dành cho sinh viên trường nào của Đại học Cần Thơ?
- Plain (B): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.05 (A): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.02 (A'): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.01 (A''): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00

---

### Câu 100 · Học bổng

- Intent: `scholarship` | Nguồn kỳ vọng: `HB_Vallet_Chi_Tiet.md`
- Câu hỏi: Đăng ký hồ sơ dự tuyển học bổng Vallet được thực hiện qua hình thức nào?
- Plain (B): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00
- Tie 0.05 (A): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.02 (A'): hit=True, rank=2, n_docs=6, pos=0.20, attn=0.50
- Tie 0.01 (A''): hit=True, rank=1, n_docs=6, pos=0.00, attn=1.00

---
